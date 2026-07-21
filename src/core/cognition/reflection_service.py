import sqlite3
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from src.core.cognition.models import Reflection, Lesson, GraphNode, GraphEdge
from src.core.cognition.reflection_repository import ReflectionRepository
from src.core.cognition.repository import CognitiveRepository

class RootCauseAnalyzer:
    """
    RootCauseAnalyzer (Sprint 6.4).
    Analisa métricas reais e evidências para diagnosticar causas de sucesso ou fracasso.
    """
    def analyze(self, metrics: Dict[str, Any]) -> str:
        impressions = metrics.get("impressions", 0)
        ctr = metrics.get("ctr_percent", 0.0) or (metrics.get("outbound_clicks", 0) / max(1, impressions)) * 100
        saves = metrics.get("saves", 0)

        if impressions < 500:
            return "Baixo alcance algorítmico (Impressions < 500). Verifique qualidade visual ou termos de busca do Pin."
        elif ctr < 1.5:
            return "Gancho visual ineficaz (CTR < 1.5%). O design criativo ou copy inicial falhou em atrair cliques."
        elif saves < 5:
            return "Fraca proposta de valor (Saves < 5). O conteúdo não reteve ou engajou o usuário."
        else:
            return "Excelente performance orgânica. Padrão criativo validado."

class FailurePatternDetector:
    """
    FailurePatternDetector (Sprint 6.4).
    Detecta falhas ou sucessos repetitivos com base no histórico de experimentos.
    """
    def __init__(self, db: Any):
        self.db = db

    def detect_patterns(self, market_segment: str) -> List[str]:
        patterns = []
        with self.db._get_conn() as conn:
            c = conn.cursor()
            # Busca últimos experimentos do mesmo segmento
            c.execute("""
                SELECT status, variant_id, epc, roi 
                FROM experiments 
                WHERE market_segment = ? 
                ORDER BY published_at DESC LIMIT 5
            """, (market_segment,))
            rows = c.fetchall()

        if len(rows) >= 3:
            failures = [r for r in rows if r[0] == "Failed" or (r[3] is not None and r[3] < 0.0)]
            if len(failures) >= 2:
                patterns.append(f"Padrão de baixo ROI recorrente no segmento '{market_segment}'.")
            
            variants = [r[1] for r in rows]
            if len(set(variants)) == 1:
                patterns.append(f"Falta de diversificação de variante (apenas Variante {variants[0]} testada recentemente).")
                
        return patterns

class LessonExtractor:
    """
    LessonExtractor (Sprint 6.4).
    Extrai lições acionáveis a partir das análises causais e padrões detectados.
    """
    def extract(self, probable_cause: str, patterns: List[str]) -> List[Dict[str, Any]]:
        lessons = []
        
        # 1. Lição baseada na causa provável
        if "Baixo alcance" in probable_cause:
            lessons.append({
                "pattern_detected": "Exposição algorítmica restrita",
                "actionable_insight": "Otimizar metadados de busca e tags alternativas para melhor indexação de imagem.",
                "severity": "high"
            })
        elif "Gancho visual" in probable_cause:
            lessons.append({
                "pattern_detected": "Falha na retenção de cliques (CTR)",
                "actionable_insight": "Aumentar contraste do texto sobreposto e refinar o gancho textual nos primeiros 3 segundos.",
                "severity": "high"
            })
        elif "proposta de valor" in probable_cause:
            lessons.append({
                "pattern_detected": "Baixo engajamento pós-clique",
                "actionable_insight": "Refinar a relevância do link de destino e alinhar expectativas do criativo com a landing page.",
                "severity": "medium"
            })
        else:
            lessons.append({
                "pattern_detected": "Alta performance criativa",
                "actionable_insight": "Escalar a distribuição desta variante e replicar o genoma criativo nos próximos lotes.",
                "severity": "low"
            })

        # 2. Lição baseada em padrões históricos
        for pattern in patterns:
            if "baixo ROI" in pattern.lower():
                lessons.append({
                    "pattern_detected": "Saturação de ROI no segmento",
                    "actionable_insight": "Reavaliar o CPC ou explorar novas verticais de monetização adjacentes.",
                    "severity": "high"
                })
                
        return lessons

class ReflectionService:
    """
    ReflectionService (Sprint 6.4).
    Orquestra a análise causal, detecta padrões, extrai lições
    e registra tudo no Grafo de Evidências.
    """
    def __init__(
        self,
        reflection_repo: ReflectionRepository,
        cognitive_repo: CognitiveRepository,
        db: Any
    ):
        self.reflection_repo = reflection_repo
        self.cognitive_repo = cognitive_repo
        self.db = db
        self.analyzer = RootCauseAnalyzer()
        self.detector = FailurePatternDetector(db)
        self.extractor = LessonExtractor()

    def generate_reflection(self, experiment_id: str, related_belief_id: int) -> Reflection:
        # 1. Buscar metadados do experimento
        with self.db._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM experiments WHERE experiment_id = ?", (experiment_id,))
            exp_row = c.fetchone()
            if not exp_row:
                raise ValueError(f"Experimento {experiment_id} não encontrado.")
            exp = dict(exp_row)
            
            # Buscar métricas reais do experimento
            c.execute("SELECT * FROM metrics WHERE experiment_id = ?", (experiment_id,))
            metrics_row = c.fetchone()
            metrics = dict(metrics_row) if metrics_row else {}

        # 2. Analisar causa provável
        probable_cause = self.analyzer.analyze(metrics)
        
        # 3. Detectar padrões repetitivos
        segment = exp.get("market_segment", "Geral")
        patterns = self.detector.detect_patterns(segment)
        
        # 4. Calcular delta de confiança da hipótese
        hyp_id = exp.get("hypothesis_id")
        prior_conf = 0.50
        current_conf = 0.50
        if hyp_id:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute("SELECT confidence_score FROM hypotheses WHERE id = ?", (hyp_id,))
                row = c.fetchone()
                if row:
                    current_conf = row[0]
                    
        confidence_delta = current_conf - prior_conf

        # 5. Adicionar metadados da explicação Bayesiana
        bayesian_explanation = {
            "prior": prior_conf,
            "likelihood": 0.85 if probable_cause.startswith("Excelente") else 0.20,
            "posterior": current_conf,
            "explanation": f"Confiança recalibrada Bayesiana-like de {prior_conf} para {current_conf} baseada no impacto empírico do teste."
        }

        # 6. Criar e persistir reflexão
        analysis_text = f"Análise automatizada do experimento {experiment_id}. Causa: {probable_cause}."
        if patterns:
            analysis_text += " Padrões históricos identificados: " + " | ".join(patterns)
            
        reflection = Reflection(
            experiment_id=experiment_id,
            analysis=analysis_text,
            probable_cause=probable_cause,
            confidence_delta=confidence_delta,
            bayesian_explanation=bayesian_explanation
        )
        saved_reflection = self.reflection_repo.save_reflection(reflection)

        # 7. Registrar nó da reflexão no grafo
        ref_node_id = f"reflection:{saved_reflection.id}"
        self.cognitive_repo.save_node(GraphNode(
            id=ref_node_id,
            type="reflection",
            label=f"Ref {saved_reflection.id}: {saved_reflection.probable_cause[:40]}"
        ))

        # Aresta: Experimento -> Reflexão ("explains")
        self.cognitive_repo.save_edge(GraphEdge(
            source=f"experiment:{experiment_id}",
            target=ref_node_id,
            relation_type="explains",
            weight=1.0
        ))

        # Aresta: Reflexão -> Hipótese ("analyzes")
        if hyp_id:
            self.cognitive_repo.save_edge(GraphEdge(
                source=ref_node_id,
                target=f"hypothesis:{hyp_id}",
                relation_type="analyzes",
                weight=1.0
            ))

        # 8. Extrair lições e salvar
        lessons_data = self.extractor.extract(probable_cause, patterns)
        for data in lessons_data:
            lesson = Lesson(
                reflection_id=saved_reflection.id,
                pattern_detected=data["pattern_detected"],
                actionable_insight=data["actionable_insight"],
                severity=data["severity"]
            )
            saved_lesson = self.reflection_repo.save_lesson(lesson)
            
            # Registrar nó da lição no grafo
            lesson_node_id = f"lesson:{saved_lesson.id}"
            self.cognitive_repo.save_node(GraphNode(
                id=lesson_node_id,
                type="lesson",
                label=f"Lesson {saved_lesson.id}: {saved_lesson.pattern_detected[:40]}"
            ))
            
            # Aresta: Reflexão -> Lição ("produces")
            self.cognitive_repo.save_edge(GraphEdge(
                source=ref_node_id,
                target=lesson_node_id,
                relation_type="produces",
                weight=1.0
            ))
            
            # Aresta: Lição -> Crença ("refines")
            self.cognitive_repo.save_edge(GraphEdge(
                source=lesson_node_id,
                target=f"belief:{related_belief_id}",
                relation_type="refines",
                weight=1.0
            ))

        return saved_reflection
