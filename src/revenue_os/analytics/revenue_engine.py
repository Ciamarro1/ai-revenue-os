import logging
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import urllib.parse
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.schemas import ExperimentContract

logger = logging.getLogger("revenue_os.revenue_engine")


class RevenueEngine:
    """
    Motor Financeiro (Revenue Engine).
    Responsável por gerenciar UTMs de links de afiliados, rastrear conversões (payouts/comissões)
    e calcular métricas agregadas de retorno financeiro (EPC, RPC, ROI, CPA, LTV).
    """
    def __init__(self, db: ExperimentDatabase):
        self.db = db

    def generate_affiliate_link(self, raw_url: str, experiment_id: str, variant_id: str, platform: str) -> str:
        """
        Retorna o link com os parâmetros UTM dinâmicos de rastreamento de comissões.
        """
        parsed = urllib.parse.urlparse(raw_url)
        params = urllib.parse.parse_qs(parsed.query)
        
        params['utm_source'] = [platform]
        params['utm_medium'] = ['organic_acquisition']
        params['utm_campaign'] = [experiment_id]
        params['utm_term'] = [variant_id]
        
        new_query = urllib.parse.urlencode(params, doseq=True)
        utm_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
        
        # Persiste o link no banco
        link_id = f"LNK-{experiment_id}-{variant_id}"
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO affiliate_links (link_id, experiment_id, raw_url, utm_url, short_url, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(link_id) DO UPDATE SET utm_url=excluded.utm_url, created_at=excluded.created_at
                ''', (link_id, experiment_id, raw_url, utm_url, utm_url, now))
                conn.commit()
        except Exception as e:
            logger.error(f"Error persisting affiliate link: {e}")
            
        return utm_url

    def register_conversion(self, conversion_id: str, experiment_id: str, click_id: str, 
                            payout_usd: float, commission_usd: float, status: str = "approved") -> Dict[str, Any]:
        """
        Registra uma conversão de compra / comissão de afiliado no banco de dados.
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO affiliate_conversions (id, experiment_id, click_id, payout_usd, commission_usd, converted_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET status=excluded.status, commission_usd=excluded.commission_usd, payout_usd=excluded.payout_usd
                ''', (conversion_id, experiment_id, click_id, payout_usd, commission_usd, now, status))
                conn.commit()
            logger.info(f"Conversion registered: {conversion_id} -> Experiment: {experiment_id} (Commission: {commission_usd})")
        except Exception as e:
            logger.error(f"Error registering conversion: {e}")
            
        return {
            "conversion_id": conversion_id,
            "experiment_id": experiment_id,
            "commission_usd": commission_usd,
            "status": status
        }

    def compute_experiment_roi(self, experiment_id: str, outbound_clicks: int = 0) -> Dict[str, float]:
        """
        Calcula as métricas financeiras (EPC, RPC, ROI, CPA, LTV) para um experimento específico.
        Atualiza os campos no SQLite e retorna os valores.
        """
        total_commission = 0.0
        total_payout = 0.0
        conversions_count = 0
        
        try:
            with self.db._get_conn() as conn:
                conn.row_factory = sqlite3.Row if hasattr(sqlite3, 'Row') else None
                c = conn.cursor()
                # Buscar todas as conversões aprovadas do experimento
                c.execute('''
                    SELECT commission_usd, payout_usd FROM affiliate_conversions
                    WHERE experiment_id = ? AND status = 'approved'
                ''', (experiment_id,))
                rows = c.fetchall()
                for r in rows:
                    total_commission += r[0] if isinstance(r, tuple) else r["commission_usd"]
                    total_payout += r[1] if isinstance(r, tuple) else r["payout_usd"]
                    conversions_count += 1
                    
                # Buscar o custo de geração do experimento
                c.execute('SELECT generation_cost_usd, published_at FROM experiments WHERE experiment_id = ?', (experiment_id,))
                exp_row = c.fetchone()
                generation_cost = exp_row[0] if exp_row else 0.05
        except Exception as e:
            logger.error(f"Error calculating stats for {experiment_id}: {e}")
            generation_cost = 0.05
            
        # ROI = (Receita - Custo) / Custo
        roi = (total_commission - generation_cost) / max(0.01, generation_cost)
        
        # EPC (Earnings Per Click) = Receita / Cliques de saída
        epc = total_commission / max(1, outbound_clicks)
        
        # RPC (Revenue Per Click) = Receita / Conversões
        rpc = total_commission / max(1, conversions_count)
        
        # CPA (Cost Per Acquisition) = Custo de Geração / Conversões
        cpa = generation_cost / max(1, conversions_count)
        
        # LTV = Payout médio da comissão (proxy simples local de longo prazo)
        ltv = total_payout / max(1, conversions_count)
        
        metrics = {
            "revenue": round(total_commission, 3),
            "epc": round(epc, 3),
            "rpc": round(rpc, 3),
            "roi": round(roi, 3),
            "ltv": round(ltv, 3),
            "cpa": round(cpa, 3)
        }
        
        # Persiste de volta nas colunas da tabela experiments e atualiza a receita total
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE experiments 
                    SET revenue_usd = ?, epc = ?, rpc = ?, roi = ?, ltv = ?, cpa = ?
                    WHERE experiment_id = ?
                ''', (total_commission, epc, rpc, roi, ltv, cpa, experiment_id))
                
                # Também atualiza a tabela metrics com conversion_count
                c.execute('''
                    UPDATE metrics
                    SET conversion_count = ?
                    WHERE experiment_id = ?
                ''', (conversions_count, experiment_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating metrics in DB: {e}")
            
        return metrics
