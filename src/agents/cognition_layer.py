import os
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

try:
    from src.revenue_os.analytics.database import ExperimentDatabase
except ImportError:
    ExperimentDatabase = None

class RuntimeCognitiveLayer:
    """
    Runtime Cognitive Layer (Sprint 1).
    Fornece aos agentes uma interface operacional em Python para interagir com o estado do sistema,
    ler/escrever crenças, gerenciar bloqueadores e sincronizar dados do banco SQLite
    diretamente nas documentações markdown.
    """
    def __init__(self, db: Optional[Any] = None, docs_dir: str = "docs"):
        self.project_root = Path(__file__).parent.parent.parent
        self.docs_path = self.project_root / docs_dir
        
        # Conexão de banco opcional
        self.db = db
        if self.db is None and ExperimentDatabase is not None:
            try:
                self.db = ExperimentDatabase()
            except Exception:
                self.db = None

    # ==========================================
    # Operações de Bloqueadores (Blockers)
    # ==========================================
    def load_blockers(self) -> List[Dict[str, Any]]:
        """Lê os bloqueadores ativos do arquivo docs/runtime/current_blockers.md."""
        file_path = self.docs_path / "runtime" / "current_blockers.md"
        if not file_path.exists():
            return []
            
        blockers = []
        pattern = re.compile(r"-\s+\[( |x)\]\s+\[(HIGH|MEDIUM|LOW)\]\s+([^:]+):\s+(.+)")
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    resolved = match.group(1).lower() == "x"
                    severity = match.group(2)
                    title = match.group(3).strip()
                    description = match.group(4).strip()
                    blockers.append({
                        "resolved": resolved,
                        "severity": severity,
                        "title": title,
                        "description": description
                    })
        return blockers

    def add_blocker(self, title: str, description: str, severity: str = "MEDIUM"):
        """Adiciona um novo bloqueador em docs/runtime/current_blockers.md."""
        file_path = self.docs_path / "runtime" / "current_blockers.md"
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# CURRENT BLOCKERS (BLOQUEADORES OPERACIONAIS)\n\n")
                
        # Verifica se já existe um bloqueador com esse título
        blockers = self.load_blockers()
        if any(b["title"].lower() == title.lower() for b in blockers):
            print(f"⚠️ [CognitiveLayer] Bloqueador '{title}' já existe. Ignorando adição.")
            return

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"- [ ] [{severity.upper()}] {title}: {description}\n")
        print(f"🧠 [CognitiveLayer] Novo bloqueador adicionado: {title} ({severity})")

    def resolve_blocker(self, title: str):
        """Marca um bloqueador como resolvido em docs/runtime/current_blockers.md."""
        file_path = self.docs_path / "runtime" / "current_blockers.md"
        if not file_path.exists():
            return
            
        lines = []
        resolved_any = False
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # Se encontrar o título, substitui [ ] por [x]
                if f" {title}:" in line and "[ ]" in line:
                    line = line.replace("[ ]", "[x]")
                    resolved_any = True
                lines.append(line)
                
        if resolved_any:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            print(f"🧠 [CognitiveLayer] Bloqueador resolvido: {title}")
        else:
            print(f"⚠️ [CognitiveLayer] Bloqueador '{title}' não encontrado ou já resolvido.")

    # ==========================================
    # Operações de Crenças (Beliefs)
    # ==========================================
    def load_beliefs(self) -> List[Dict[str, Any]]:
        """Lê as crenças do sistema em docs/cognition/beliefs.md."""
        file_path = self.docs_path / "cognition" / "beliefs.md"
        if not file_path.exists():
            return []
            
        beliefs = []
        pattern = re.compile(r"-\s+([^(]+)\(Confiança:\s+(\d+)%\)")
        
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                match = pattern.match(line.strip())
                if match:
                    statement = match.group(1).strip()
                    confidence = float(match.group(2))
                    beliefs.append({
                        "statement": statement,
                        "confidence_percent": confidence
                    })
        return beliefs

    def add_belief(self, statement: str, confidence_percent: float):
        """Adiciona ou atualiza uma crença em docs/cognition/beliefs.md."""
        file_path = self.docs_path / "cognition" / "beliefs.md"
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("# SYSTEM BELIEFS (CRENÇAS DO SISTEMA)\n\n")
                
        beliefs = self.load_beliefs()
        updated = False
        
        # Se a crença já existir, atualiza a confiança
        for b in beliefs:
            if b["statement"].lower() == statement.lower():
                b["confidence_percent"] = confidence_percent
                updated = True
                break
                
        if not updated:
            beliefs.append({
                "statement": statement,
                "confidence_percent": confidence_percent
            })
            
        # Reescreve o arquivo de crenças
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# SYSTEM BELIEFS (CRENÇAS DO SISTEMA)\n\n")
            f.write("Lista de premissas estratégicas acumuladas pela inteligência coletiva do AI Revenue OS. A confiança de cada crença flutua à medida que novas evidências estatísticas são colhidas pelo sistema.\n\n")
            for b in beliefs:
                f.write(f"- {b['statement']} (Confiança: {int(b['confidence_percent'])}%)\n")
        print(f"🧠 [CognitiveLayer] Crença atualizada/adicionada: '{statement}' ({int(confidence_percent)}%)")

    # ==========================================
    # Sincronização de Banco de Dados -> Markdown
    # ==========================================
    def sync_database_state(self):
        """Consulta as tabelas do SQLite e atualiza current_state.md e hypotheses.md."""
        if not self.db:
            print("⚠️ [CognitiveLayer] Conexão com o banco indisponível. Sincronização ignorada.")
            return
            
        try:
            conn = self.db._get_conn()
            c = conn.cursor()
            
            # 1. Obter Estatísticas Gerais do Sistema
            c.execute("SELECT count(*) FROM hypotheses")
            total_hypotheses = c.fetchone()[0]
            
            c.execute("SELECT count(*) FROM experiments")
            total_experiments = c.fetchone()[0]
            
            c.execute("SELECT count(*) FROM hypotheses WHERE status = 'validated'")
            validated_hypotheses = c.fetchone()[0]
            
            c.execute("SELECT count(*) FROM hypotheses WHERE status = 'rejected'")
            rejected_hypotheses = c.fetchone()[0]
            
            c.execute("SELECT avg(ctr_percent) FROM metrics")
            avg_ctr = c.fetchone()[0] or 0.0
            
            c.execute("SELECT sum(revenue_usd) FROM experiments")
            total_revenue = c.fetchone()[0] or 0.0
            
            c.execute("SELECT sum(generation_cost_usd) FROM experiments")
            total_cost = c.fetchone()[0] or 0.0
            
            margin = 0.0
            if total_cost > 0:
                margin = ((total_revenue - total_cost) / total_cost) * 100.0
                
            # 2. Atualizar docs/runtime/current_state.md
            current_state_path = self.docs_path / "runtime" / "current_state.md"
            self._write_current_state(
                path=current_state_path,
                total_experiments=total_experiments,
                total_hypotheses=total_hypotheses,
                validated_hypotheses=validated_hypotheses,
                rejected_hypotheses=rejected_hypotheses,
                avg_ctr=avg_ctr,
                total_revenue=total_revenue,
                total_cost=total_cost,
                margin=margin
            )
            
            # 3. Obter Detalhes de Hipóteses para docs/cognition/hypotheses.md
            c.execute("SELECT id, statement, category, confidence_score, experiments_count, status FROM hypotheses")
            hyp_rows = c.fetchall()
            
            hypotheses_path = self.docs_path / "cognition" / "hypotheses.md"
            self._write_hypotheses(hypotheses_path, hyp_rows)
            
            print("✅ [CognitiveLayer] Sincronização de documentações executada com sucesso!")
            
        except Exception as e:
            print(f"❌ [CognitiveLayer] Falha durante a sincronização de dados: {e}")

    def _write_current_state(
        self,
        path: Path,
        total_experiments: int,
        total_hypotheses: int,
        validated_hypotheses: int,
        rejected_hypotheses: int,
        avg_ctr: float,
        total_revenue: float,
        total_cost: float,
        margin: float
    ):
        """Escreve a documentação de estado atual atualizada com dados do banco."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        content = f"""# CURRENT STATE (ESTADO OPERACIONAL ATUAL)

Este documento reflete o estado atual dos componentes de software e as métricas do sistema obtidas a partir do banco de dados relacional.

## Componentes do Sistema

- **Pinterest Automation**: `70%` (Playwright headless funcional, Vision Fallback integrado)
- **Content Generator**: `40%` (MPT para vídeos local, Nvidia FLUX para imagens)
- **Analytics & Decision Engine**: `60%` (Atribuição, Bandit, e T-Test estatístico funcionais)
- **Monetization Engine**: `10%` (Funnels e tracking de links afiliados iniciais)

---

## Métricas Consolidadas do Sistema

> [!NOTE]
> As estatísticas abaixo são atualizadas automaticamente pelo módulo `RuntimeCognitiveLayer` sincronizando com a base de dados SQLite `prod_db.sqlite3`.

| Métrica | Valor |
| --- | --- |
| Total de Experimentos Executados | {total_experiments} |
| Total de Hipóteses Cadastradas | {total_hypotheses} |
| Hipóteses Validadas | {validated_hypotheses} |
| Hipóteses Rejeitadas | {rejected_hypotheses} |
| CTR Médio Geral | {avg_ctr:.2f}% |
| Faturamento Total Acumulado (USD) | ${total_revenue:.2f} |
| Custo de Geração Acumulado (USD) | ${total_cost:.2f} |
| Margem Geral / ROI | {margin:.2f}% |

Última sincronização: `{now_str}`
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _write_hypotheses(self, path: Path, rows: List[tuple]):
        """Escreve a documentação de hipóteses ativas atualizada com dados do banco."""
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        table_lines = []
        for r in rows:
            hyp_id, statement, category, conf, count, status = r
            table_lines.append(f"| {hyp_id} | {statement} | {category} | {conf*100:.1f}% | {count} | {status} |")
            
        table_content = "\n".join(table_lines)
        if not table_content:
            table_content = "| - | Nenhuma hipótese cadastrada | - | - | - | - |"
            
        content = f"""# ACTIVE HYPOTHESES (HIPÓTESES ATIVAS)

Este documento registra as suposições estatísticas cadastradas no motor relacional SQLite e seu status estatístico corrente.

> [!NOTE]
> Esta lista é gerada e atualizada de forma programática pelo módulo `RuntimeCognitiveLayer` sincronizando com a tabela `hypotheses`.

| ID | Suposição (Statement) | Nicho | Confiança | Experimentos | Status |
| --- | --- | --- | --- | --- | --- |
{table_content}

Última sincronização: `{now_str}`
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
