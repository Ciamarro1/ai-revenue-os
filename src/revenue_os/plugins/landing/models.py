from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

class BuildResult(BaseModel):
    """
    Resultado de compilação estática (Build) de uma Landing Page.
    """
    build_id: str
    framework: str  # astro, nextjs
    manifest_id: str
    build_fingerprint: str  # Hash SHA-256 dos artefatos compilação
    assets_count: int = 1
    build_time_sec: float = 0.50
    output_dir: str = ""
    built_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")

class DeploymentRecord(BaseModel):
    """
    Registro formal de Deploy em uma CDN / Cloud Provider.
    """
    deployment_id: str
    version: str  # SemVer + Timestamp
    framework: str
    cdn_provider: str  # cloudflare_pages, vercel, netlify
    public_url: str
    status: str = "ACTIVE"  # ACTIVE, ROLLED_BACK, FAILED
    build_fingerprint: str
    deployed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")
    is_active: bool = True
    classification_status: str = "LOCAL_TEST"  # REAL_PRODUCTION, SIMULATED_BENCHMARK, LOCAL_TEST, WAITING_EXTERNAL_DEPENDENCY

class RollbackRecord(BaseModel):
    """
    Registro de operação de Rollback instantâneo.
    """
    rollback_id: str
    previous_deployment_id: str
    restored_deployment_id: str
    restored_version: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat() + "Z")
    status: str = "SUCCESS"

class LandingDeploymentConfig(BaseModel):
    """
    Configuração Pydantic v2 para a Landing Deployment Engine.
    """
    default_framework: str = "astro"
    default_cdn_provider: str = "cloudflare_pages"
    enable_cloudflare: bool = True
    enable_vercel: bool = True
    enable_netlify: bool = True
    request_timeout_seconds: float = 10.0
