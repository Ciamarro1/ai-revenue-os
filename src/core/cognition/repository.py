import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.core.cognition.models import Belief, Evidence, Learning, Observation, GraphNode, GraphEdge

class CognitiveRepository:
    """
    Repositório de persistência cognitiva (Sprint 2).
    Fornece leitura/gravação das entidades cognitivas (Beliefs, Evidence, Learnings) no SQLite
    e atualiza de forma síncrona e simples os respectivos Markdowns.
    """
    def __init__(self, db: Any, docs_dir: str = "docs"):
        self.db = db
        self.project_root = Path(__file__).parent.parent.parent
        self.docs_path = self.project_root / docs_dir

    def _get_conn(self):
        return self.db._get_conn()

    # ==========================================
    # Operações de Crenças (Beliefs)
    # ==========================================
    def get_beliefs(self) -> List[Belief]:
        """Recupera todas as crenças persistidas."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, statement, confidence_score, updated_at FROM beliefs ORDER BY confidence_score DESC")
            rows = c.fetchall()
            return [
                Belief(id=r[0], statement=r[1], confidence_score=r[2], updated_at=r[3])
                for r in rows
            ]

    def save_belief(self, belief: Belief) -> Belief:
        """Insere ou atualiza uma crença no banco de dados."""
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO beliefs (statement, confidence_score, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(statement) DO UPDATE SET
                    confidence_score=excluded.confidence_score,
                    updated_at=excluded.updated_at
            """, (belief.statement, belief.confidence_score, ts))
            
            if belief.id is None:
                c.execute("SELECT id FROM beliefs WHERE statement = ?", (belief.statement,))
                row = c.fetchone()
                if row:
                    belief.id = row[0]
                    
            belief.updated_at = ts
            conn.commit()
            
        self.sync_beliefs_markdown()
        return belief

    def get_belief_history(self, belief_id: int) -> List[Dict[str, Any]]:
        """Recupera a trajetória histórica de confiança de uma crença."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT old_confidence, new_confidence, change_reason, timestamp
                FROM belief_history
                WHERE belief_id = ?
                ORDER BY id ASC
            """, (belief_id,))
            rows = c.fetchall()
            return [
                {
                    "old_confidence": r[0],
                    "new_confidence": r[1],
                    "change_reason": r[2],
                    "timestamp": r[3]
                }
                for r in rows
            ]

    # ==========================================
    # Operações de Evidências (Evidence)
    # ==========================================
    def get_evidence(self) -> List[Evidence]:
        """Recupera todas as evidências registradas."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, hypothesis_id, experiment_id, claim, confidence_score, impact, timestamp, narrative FROM evidence ORDER BY id DESC")
            rows = c.fetchall()
            return [
                Evidence(id=r[0], hypothesis_id=r[1], experiment_id=r[2], claim=r[3], confidence_score=r[4], impact=r[5], timestamp=r[6], narrative=r[7])
                for r in rows
            ]

    def register_evidence(self, evidence: Evidence) -> Evidence:
        """Registra uma nova evidência empírica."""
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO evidence (hypothesis_id, experiment_id, claim, confidence_score, impact, timestamp, narrative)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (evidence.hypothesis_id, evidence.experiment_id, evidence.claim, evidence.confidence_score, evidence.impact, ts, evidence.narrative))
            evidence.id = c.lastrowid
            evidence.timestamp = ts
            conn.commit()
            
        self.sync_evidence_markdown()
        return evidence

    def get_evidence_by_experiment(self, experiment_id: str) -> List[Evidence]:
        """Recupera todas as evidências associadas a um experimento."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, hypothesis_id, experiment_id, claim, confidence_score, impact, timestamp, narrative FROM evidence WHERE experiment_id = ? ORDER BY id DESC", (experiment_id,))
            rows = c.fetchall()
            return [
                Evidence(id=r[0], hypothesis_id=r[1], experiment_id=r[2], claim=r[3], confidence_score=r[4], impact=r[5], timestamp=r[6], narrative=r[7])
                for r in rows
            ]

    def get_evidence_quality(self, evidence_id: int) -> Optional[Dict[str, Any]]:
        """Recupera as métricas de qualidade de uma evidência."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                SELECT sample_size, confidence, reliability, recency, quality_score
                FROM evidence_quality
                WHERE evidence_id = ?
            """, (evidence_id,))
            row = c.fetchone()
            if row:
                return {
                    "sample_size": row[0],
                    "confidence": row[1],
                    "reliability": row[2],
                    "recency": row[3],
                    "quality_score": row[4]
                }
        return None

    # ==========================================
    # Operações de Aprendizados (Learnings)
    # ==========================================
    def get_learnings(self) -> List[Learning]:
        """Recupera todos os aprendizados operacionais."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, experiment_id, pattern, severity, description, created_at FROM learnings ORDER BY id DESC")
            rows = c.fetchall()
            return [
                Learning(id=r[0], experiment_id=r[1], pattern=r[2], severity=r[3], description=r[4], created_at=r[5])
                for r in rows
            ]

    def log_learning(self, learning: Learning) -> Learning:
        """Registra um novo aprendizado operacional no repositório."""
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO learnings (experiment_id, pattern, severity, description, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (learning.experiment_id, learning.pattern, learning.severity, learning.description, ts))
            learning.id = c.lastrowid
            learning.created_at = ts
            conn.commit()
            
        self.sync_learnings_markdown()
        return learning

    # ==========================================
    # Operações de Observações (Observations)
    # ==========================================
    def get_observations(self) -> List[Observation]:
        """Recupera todas as observações registradas."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, source, metric_name, value, timestamp, raw_data FROM observations ORDER BY id DESC")
            rows = c.fetchall()
            return [
                Observation(id=r[0], source=r[1], metric_name=r[2], value=r[3], timestamp=r[4], raw_data=r[5])
                for r in rows
            ]

    def save_observation(self, observation: Observation) -> Observation:
        """Salva uma nova observação empírica."""
        ts = datetime.now(timezone.utc).isoformat() + "Z"
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO observations (source, metric_name, value, timestamp, raw_data)
                VALUES (?, ?, ?, ?, ?)
            """, (observation.source, observation.metric_name, observation.value, ts, observation.raw_data))
            observation.id = c.lastrowid
            observation.timestamp = ts
            conn.commit()
        return observation

    # ==========================================
    # Operações de Grafo Cognitivo (Evidence Graph)
    # ==========================================
    def save_node(self, node: GraphNode) -> GraphNode:
        """Salva ou atualiza um nó no grafo cognitivo."""
        import json
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO cognitive_graph_nodes (id, type, label, properties_json)
                VALUES (?, ?, ?, ?)
            """, (node.id, node.type, node.label, json.dumps(node.properties)))
            conn.commit()
        return node

    def save_edge(self, edge: GraphEdge) -> GraphEdge:
        """Salva ou atualiza uma aresta no grafo cognitivo."""
        import json
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("""
                INSERT OR REPLACE INTO cognitive_graph_edges (source, target, relation_type, weight, properties_json)
                VALUES (?, ?, ?, ?, ?)
            """, (edge.source, edge.target, edge.relation_type, edge.weight, json.dumps(edge.properties)))
            conn.commit()
        return edge

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Recupera um nó específico do grafo cognitivo."""
        import json
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT id, type, label, properties_json FROM cognitive_graph_nodes WHERE id = ?", (node_id,))
            row = c.fetchone()
            if row:
                return GraphNode(
                    id=row[0],
                    type=row[1],
                    label=row[2],
                    properties=json.loads(row[3])
                )
            return None

    def get_edges_to(self, target_id: str) -> List[GraphEdge]:
        """Recupera todas as arestas que apontam para um nó de destino."""
        import json
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT source, target, relation_type, weight, properties_json FROM cognitive_graph_edges WHERE target = ?", (target_id,))
            rows = c.fetchall()
            return [
                GraphEdge(source=r[0], target=r[1], relation_type=r[2], weight=r[3], properties=json.loads(r[4]))
                for r in rows
            ]

    def get_edges_from(self, source_id: str) -> List[GraphEdge]:
        """Recupera todas as arestas que partem de um nó de origem."""
        import json
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT source, target, relation_type, weight, properties_json FROM cognitive_graph_edges WHERE source = ?", (source_id,))
            rows = c.fetchall()
            return [
                GraphEdge(source=r[0], target=r[1], relation_type=r[2], weight=r[3], properties=json.loads(r[4]))
                for r in rows
            ]

    def trace_observations_for_belief(self, belief_id: int) -> List[Observation]:
        """Retorna todas as observações que originaram uma crença diretamente ou transitivamente."""
        visited = set()
        self._dfs_backwards(f"belief:{belief_id}", visited)
        
        obs_ids = []
        for node_id in visited:
            if node_id.startswith("observation:"):
                try:
                    obs_ids.append(int(node_id.split(":")[1]))
                except ValueError:
                    pass
                    
        if not obs_ids:
            return []
            
        placeholders = ",".join(["?"] * len(obs_ids))
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute(f"SELECT id, source, metric_name, value, timestamp, raw_data FROM observations WHERE id IN ({placeholders})", obs_ids)
            rows = c.fetchall()
            return [
                Observation(id=r[0], source=r[1], metric_name=r[2], value=r[3], timestamp=r[4], raw_data=r[5])
                for r in rows
            ]

    def trace_evidence_for_decision(self, decision_id: int) -> List[Evidence]:
        """Retorna todas as evidências que sustentam uma decisão diretamente ou transitivamente."""
        visited = set()
        self._dfs_backwards(f"decision:{decision_id}", visited)
        
        ev_ids = []
        for node_id in visited:
            if node_id.startswith("evidence:"):
                try:
                    ev_ids.append(int(node_id.split(":")[1]))
                except ValueError:
                    pass
                    
        if not ev_ids:
            return []
            
        placeholders = ",".join(["?"] * len(ev_ids))
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute(f"SELECT id, hypothesis_id, experiment_id, claim, confidence_score, impact, timestamp, narrative FROM evidence WHERE id IN ({placeholders})", ev_ids)
            rows = c.fetchall()
            return [
                Evidence(id=r[0], hypothesis_id=r[1], experiment_id=r[2], claim=r[3], confidence_score=r[4], impact=r[5], timestamp=r[6], narrative=r[7])
                for r in rows
            ]

    def trace_experiments_for_belief(self, belief_id: int) -> List[str]:
        """Retorna todos os IDs de experimentos que modificaram uma crença diretamente ou transitivamente."""
        visited = set()
        self._dfs_backwards(f"belief:{belief_id}", visited)
        
        exp_ids = []
        for node_id in visited:
            if node_id.startswith("experiment:"):
                exp_ids.append(node_id.split(":")[1])
        return exp_ids

    def _dfs_backwards(self, target_id: str, visited: set) -> None:
        if target_id in visited:
            return
        visited.add(target_id)
        edges = self.get_edges_to(target_id)
        for edge in edges:
            self._dfs_backwards(edge.source, visited)

    # ==========================================
    # Sincronização Síncrona simples com Markdowns
    # ==========================================
    def sync_beliefs_markdown(self):
        """Regera docs/cognition/beliefs.md baseado nos dados do banco."""
        file_path = self.docs_path / "cognition" / "beliefs.md"
        beliefs = self.get_beliefs()
        
        lines = []
        for b in beliefs:
            lines.append(f"- **{b.statement}** (Confiança Atual: {int(b.confidence_score * 100)}%)")
            history = self.get_belief_history(b.id)
            if history:
                lines.append("  * *Trajetória de Evolução*:")
                for h in history:
                    lines.append(f"    - {int(h['old_confidence'] * 100)}% ➔ {int(h['new_confidence'] * 100)}% ({h['change_reason']}) em {h['timestamp']}")
            
        list_content = "\n".join(lines)
        if not list_content:
            list_content = "Nenhuma crença cadastrada no banco."
            
        content = f"""# SYSTEM BELIEFS (CRENÇAS DO SISTEMA)

Lista de premissas estratégicas acumuladas pela inteligência coletiva do AI Revenue OS. A confiança de cada crença flutua à medida que novas evidências estatísticas são colhidas pelo sistema.

{list_content}
"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def sync_evidence_markdown(self):
        """Regera docs/cognition/evidence.md baseado nos dados do banco."""
        file_path = self.docs_path / "cognition" / "evidence.md"
        evidence_list = self.get_evidence()
        
        blocks = []
        for e in evidence_list:
            narrative_text = e.narrative if e.narrative else "Nenhuma narrativa descritiva adicionada pelo agente."
            quality_info = self.get_evidence_quality(e.id)
            if quality_info:
                quality_str = f"""
* **Qualidade da Evidência**:
  - Escore Geral: {int(quality_info['quality_score'] * 100)}%
  - Tamanho da Amostra: {quality_info['sample_size']} posts/imp
  - Confiabilidade da Fonte: {int(quality_info['reliability'] * 100)}%
  - Recência: {int(quality_info['recency'] * 100)}%"""
            else:
                quality_str = "\n* **Qualidade da Evidência**: Nenhuma avaliação realizada."
                
            blocks.append(f"""## Evidência E-{e.id}: {e.claim}
* **Data**: {e.timestamp}
* **Experimento**: {e.experiment_id}
* **Impacto**: {e.impact}
* **Confiança**: {int(e.confidence_score * 100)}%{quality_str}
* **Narrativa**: {narrative_text}""")
            
        list_content = "\n\n".join(blocks)
        if not list_content:
            list_content = "Nenhuma evidência registrada no banco."
            
        content = f"""# EMPIRICAL EVIDENCE LEDGER (LIVRO DE EVIDÊNCIAS EMPÍRICAS)

Evidências científicas e estatísticas coletadas no mundo real que corroboram ou invalidam as hipóteses e crenças do sistema.

{list_content}
"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def sync_learnings_markdown(self):
        """Regera docs/knowledge/repository_learning.md mantendo os aprendizados core estáticos e adicionando os do banco."""
        file_path = self.docs_path / "knowledge" / "repository_learning.md"
        learnings = self.get_learnings()
        
        dynamic_lines = []
        for l in learnings:
            dynamic_lines.append(f"- **{l.pattern}** ({l.severity}): {l.description} (Experimento: {l.experiment_id}, Data: {l.created_at})")
            
        dynamic_content = "\n".join(dynamic_lines)
        if not dynamic_content:
            dynamic_content = "*Nenhum aprendizado operacional registrado de loops automáticos.*"
            
        content = f"""# APRENDIZADOS DO REPOSITÓRIO (REPOSITORY LEARNINGS)

Este arquivo consolida aprendizados operacionais práticos e comportamentos empíricos descobertos durante as execuções, testes e simulações do AI Revenue OS.

---

## 1. Testabilidade e Isolamento de Estado
* **Comportamento**: O banco de dados de produção `prod_db.sqlite3` contém o histórico real das campanhas orgânicas. Modificá-lo diretamente durante os testes unitários corrompe dados analíticos históricos.
* **Lição**: Os testes unitários do `pytest` utilizam bancos de dados em memória (`sqlite:///:memory:`). Sempre que desenvolver um novo serviço que interaja com o banco de dados, garanta que a fábrica de conexões ou o engine de banco suporte a passagem de um path mockado ou conexão em memória, protegendo o banco real.

## 2. Consistência Visual do Playwright
* **Comportamento**: Bounding boxes e coordenadas de clique inferidas pelo modelo de Visão LLM (Gemini 2.5 Flash) quebram ou erram o alvo caso o navegador seja redimensionado aleatoriamente.
* **Lição**: O Playwright deve sempre rodar com uma **Viewport fixa de 1280x800**. O script `pinterest_playwright.py` e qualquer conector futuro que implemente `Vision Fallback` deve forçar essa resolução nas propriedades do navegador no momento da inicialização para garantir consistência matemática dos pixels.

## 3. Gestão de Cookies e Sessões Persistentes
* **Comportamento**: Fazer login programático direto no Pinterest via Playwright Headless em cada execução de postagem ativa rapidamente proteções automatizadas contra bots (captchas e bloqueio de IP).
* **Lição**: Use o utilitário `scripts/setup_session.py` no modo headful (navegador visível) uma única vez para realizar o login manual. O estado da sessão (cookies, localStorage) é persistido no diretório `config/sessions/`. As postagens automatizadas subsequentes carregam esse contexto de sessão pré-autenticado rodando headless, minimizando consideravelmente as taxas de verificação de login e captchas.

## 4. Degradação de Trust Score e Cooldowns
* **Comportamento**: Postar sem resfriamento e ignorar pequenos erros de rede ou de interface de rede degrada a reputação do robô na API do Pinterest.
* **Lição**: O `PinterestSafetyCoordinator` monitora erros operacionais e desconta pontos do Trust Score da conta:
  - Timeouts de publicação: -5 pontos.
  - Captcha detectado: -20 pontos.
  - Redirecionamento forçado para a página de login (sessão expirada): -30 pontos.
  Se o score cair abaixo de 50 ou houver 3 erros críticos consecutivos, o sistema entra em `COOLDOWN` (resfriamento de 12 a 24 horas) e o circuito de proteção global `AUTOPAUSE` é ativada no SQLite para proteger a conta.

## 5. Filtragem de Spam Perceptual (Deduplication)
* **Comportamento**: A geração estocástica de imagens via NVIDIA API sob prompts de nicho idênticos cria criativos com padrões visuais idênticos, o que ativa o lixo spam das plataformas e reduz o alcance orgânico.
* **Lição**: O `ImageDeduplicator` calcula os hashes perceptuais (pHash, aHash, dHash) das mídias. Uma distância de Hamming menor ou igual a 10 em relação ao histórico recente de postagens bloqueia a postagem preventiva do criativo, exigindo a regeneração do ativo criativo com um prompt modificado.

---

## 🧠 Aprendizados Coletados de Loops Automáticos
{dynamic_content}
"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

