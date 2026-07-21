from pydantic import BaseModel, Field
from typing import List, Optional

class CreativeBrief(BaseModel):
    """
    Especificação formal para a Factory Layer gerar um ativo.
    Traduz uma hipótese abstrata em um briefing de produção concreto.
    """
    hypothesis_id: str
    audience: str
    emotion: str
    hook: str
    script: Optional[str] = None  # Roteiro/descrição aprovado pelo Copywriter + Critic
    format: str = "short_video"
    duration: int = 45
    platform: str
    search_terms: List[str] = Field(default_factory=list)
    subject: str = ""
    inputs_hash: Optional[str] = None  # Hash determinístico dos inputs para cache

class GeneratedAsset(BaseModel):
    """
    O produto físico (arquivo) gerado pela Factory Layer.
    Carrega métricas de qualidade (confidence) e metadados técnicos.
    Também carrega o conteúdo aprovado pelo Copywriter/Critic para ser passado
    diretamente ao Publisher sem reformulação.
    """
    path: str
    duration: float = 45.0
    resolution: str = "1080x1920"
    provider: str = "factory"
    confidence: float = 1.0
    task_dir: Optional[str] = None
    subtitles_path: Optional[str] = None
    audio_path: Optional[str] = None
    # Conteúdo aprovado pelo Core (Copywriter + Critic)
    approved_title: Optional[str] = None
    approved_description: Optional[str] = None
    approved_cta: Optional[str] = None
    destination_link: Optional[str] = None
