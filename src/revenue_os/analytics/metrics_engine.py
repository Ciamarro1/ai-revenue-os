from typing import List, Dict, Any, Tuple
import numpy as np
from scipy import stats

from src.revenue_os.analytics.schemas import ExperimentContract

class MetricsEngine:
    """
    O cérebro estatístico da plataforma.
    Calcula T-Tests entre variantes para extrair Confiança e Effect Size.
    Remove a matemática das costas do LLM (evita alucinação).
    """
    
    @staticmethod
    def analyze_ab_test(experiments: List[ExperimentContract]) -> Dict[str, Any]:
        if not experiments:
            return {"error": "No data"}
            
        hypothesis = experiments[0].hypothesis
        metric_target = hypothesis.metric_target
        
        # Agrupar variantes
        variants_data: Dict[str, List[float]] = {}
        for exp in experiments:
            var_id = exp.variant.id
            if var_id not in variants_data:
                variants_data[var_id] = []
                
            m = exp.real_world_metrics
            if metric_target == "retention_3s":
                val = m.retention_3s_percent
            elif metric_target == "ctr":
                val = m.ctr_percent
            elif metric_target == "completion":
                val = m.completion_rate_percent
            else:
                val = exp.reward_score
                
            variants_data[var_id].append(val)
            
        variant_keys = list(variants_data.keys())
        if len(variant_keys) < 2:
            return {"error": "Need at least 2 variants"}
            
        group_a = variants_data[variant_keys[0]]
        group_b = variants_data[variant_keys[1]]
        
        n_a, n_b = len(group_a), len(group_b)
        mean_a, mean_b = np.mean(group_a), np.mean(group_b)
        
        # Teste T independente
        t_stat, p_value = stats.ttest_ind(group_a, group_b, equal_var=False)
        
        # Cohen's d (Effect Size)
        var_a, var_b = np.var(group_a, ddof=1), np.var(group_b, ddof=1)
        s = np.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
        effect_size = (mean_a - mean_b) / s if s > 0 else 0
        
        # Confiança (1 - p_value)
        confidence = 1.0 - (p_value if not np.isnan(p_value) else 1.0)
        
        # Winner
        winner = None
        if confidence >= 0.95:
            winner = variant_keys[0] if mean_a > mean_b else variant_keys[1]
            
        # Avaliar Trade-offs de outras métricas
        trade_off_detected = False
        if winner:
            loser = variant_keys[1] if winner == variant_keys[0] else variant_keys[0]
            # Extrair a segunda métrica para checar conflitos
            alt_a = [e.real_world_metrics.ctr_percent if metric_target == "retention_3s" else e.real_world_metrics.retention_3s_percent for e in experiments if e.variant.id == variant_keys[0]]
            alt_b = [e.real_world_metrics.ctr_percent if metric_target == "retention_3s" else e.real_world_metrics.retention_3s_percent for e in experiments if e.variant.id == variant_keys[1]]
            mean_alt_a, mean_alt_b = np.mean(alt_a), np.mean(alt_b)
            
            # Se a variante vencedora teve performance >10% PIOR na outra métrica, é um trade-off
            winner_alt_mean = mean_alt_a if winner == variant_keys[0] else mean_alt_b
            loser_alt_mean = mean_alt_b if winner == variant_keys[0] else mean_alt_a
            
            if loser_alt_mean > winner_alt_mean * 1.1:
                trade_off_detected = True

        return {
            "hypothesis": hypothesis.statement,
            "metric_target": metric_target,
            "sample_size_total": n_a + n_b,
            "variants": {
                variant_keys[0]: {"n": n_a, "mean": round(mean_a, 2)},
                variant_keys[1]: {"n": n_b, "mean": round(mean_b, 2)}
            },
            "p_value": round(p_value, 4) if not np.isnan(p_value) else 1.0,
            "confidence": round(confidence, 3),
            "effect_size": round(abs(effect_size), 2),
            "winner": winner,
            "trade_off_detected": trade_off_detected,
            "is_significant": confidence >= 0.95
        }
