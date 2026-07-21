from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

class DomainEvent(BaseModel):
    """
    Classe Base para todos os Eventos de Domínio do AI Revenue OS (Sprint 9.8).
    """
    event_id: str = Field(default_factory=lambda: f"EVT-{uuid.uuid4().hex[:8].upper()}")
    event_type: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")
    payload: Dict[str, Any] = Field(default_factory=dict)

class ResearchTopicCreated(DomainEvent):
    event_type: str = "research.topic.created"

class OpportunitySelected(DomainEvent):
    event_type: str = "opportunity.selected"

class OfferGenerated(DomainEvent):
    event_type: str = "offer.generated"

class LandingPublished(DomainEvent):
    event_type: str = "landing.published"

class TrafficObserved(DomainEvent):
    event_type: str = "traffic.received"

class ConversionRecorded(DomainEvent):
    event_type: str = "conversion.recorded"

class GenomeUpdated(DomainEvent):
    event_type: str = "genome.updated"

class KnowledgeLearned(DomainEvent):
    event_type: str = "knowledge.learned"
