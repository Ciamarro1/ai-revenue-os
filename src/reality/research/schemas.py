from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ResearchReport(BaseModel):
    """
    Contrato estrito para as evidências coletadas do mundo real pela Reality Layer.
    """
    query: str
    provider: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sources: List[str] = Field(default_factory=list)
    trends: List[dict] = Field(default_factory=list)
    competitors: List[dict] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    confidence: float = 1.0
    source_quality: float = 0.8
    sample_size: int = 10


class TopicCandidate(BaseModel):
    """
    Representa um candidato a tópico/nicho identificado e pontuado pelo Autonomous Research Engine.
    Persistido em `knowledge/topic_candidates/`.
    """
    topic: str
    niche: str
    intent: str = "informational"  # informational, commercial, transactional
    competition: str = "medium"    # low, medium, high
    estimated_ctr: float = 0.025
    estimated_rpm: float = 12.50
    estimated_conversion: float = 0.035
    seasonality: str = "evergreen" # evergreen, seasonal, trending
    confidence: float = 0.85
    sources: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @property
    def score(self) -> float:
        """
        Cálculo de pontuação heurística do candidato.
        """
        mult = {"low": 1.2, "medium": 1.0, "high": 0.7}.get(self.competition.lower(), 1.0)
        return round((self.estimated_ctr * 100) * self.estimated_rpm * (self.estimated_conversion * 100) * self.confidence * mult, 2)

