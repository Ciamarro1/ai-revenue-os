from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class CreativeJob(BaseModel):
    """
    Modelo de Job de Produção de Mídia na Fila Assíncrona.
    """
    job_id: str
    job_type: str  # image, video
    provider_name: str
    prompt: str
    priority: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    status: str = "QUEUED"  # QUEUED, PROCESSING, COMPLETED, FAILED, CANCELLED
    error_message: Optional[str] = None
    retry_count: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")
    completed_at: Optional[str] = None

class GeneratedCreativeAsset(BaseModel):
    """
    Ativo de Mídia (Imagem ou Vídeo) Físico Gerado e Auditável.
    """
    asset_id: str
    asset_type: str  # image, video
    provider_name: str
    file_path: str
    content_hash: str  # SHA-256 hash de conteúdo
    version: str  # SemVer + Timestamp
    width: int = 1080
    height: int = 1920
    duration_sec: float = 0.0
    mime_type: str = "image/png"
    classification_status: str = "LOCAL_TEST"  # REAL_PRODUCTION, SIMULATED_BENCHMARK, LOCAL_TEST, WAITING_EXTERNAL_DEPENDENCY
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class BenchmarkResult(BaseModel):
    """
    Resultado de Benchmark de Latência e Throughput da Fábrica Criativa.
    """
    total_jobs: int
    successful_jobs: int
    failed_jobs: int
    total_time_sec: float
    average_latency_sec: float
    throughput_jobs_per_sec: float
    success_rate_pct: float
    evaluated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class CreativeConfig(BaseModel):
    """
    Configuração Pydantic v2 da Creative Generation Engine.
    """
    storage_base_dir: str = "storage/creatives"
    max_worker_threads: int = 4
    max_retries: int = 3
    request_timeout_sec: float = 15.0
    enable_flux: bool = True
    enable_comfyui: bool = True
    enable_mpt: bool = True
    enable_remotion: bool = True
