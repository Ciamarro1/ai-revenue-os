import hashlib
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from src.revenue_os.plugins.landing.models import (
    BuildResult,
    DeploymentRecord,
    RollbackRecord,
    LandingDeploymentConfig
)
from src.revenue_os.plugins.landing.providers import (
    BaseCDNProvider,
    CloudflarePagesProvider,
    VercelProvider,
    NetlifyProvider
)

class LandingDeploymentEngine:
    """
    Orquestrador Central da Landing Deployment Engine (Sprint O4).
    Gerencia compilação estática, selagem de fingerprints SHA-256,
    deploys em CDNs, histórico de versões e rollback instantâneo.
    """

    def __init__(self, config: Optional[LandingDeploymentConfig] = None):
        self.config = config or LandingDeploymentConfig()
        self._cdn_providers: Dict[str, BaseCDNProvider] = {}
        self._history: List[DeploymentRecord] = []
        self._setup_default_providers()

    def _setup_default_providers(self):
        if self.config.enable_cloudflare:
            self.register_cdn_provider(CloudflarePagesProvider())
        if self.config.enable_vercel:
            self.register_cdn_provider(VercelProvider())
        if self.config.enable_netlify:
            self.register_cdn_provider(NetlifyProvider())

    def register_cdn_provider(self, provider: BaseCDNProvider) -> None:
        self._cdn_providers[provider.cdn_name.lower()] = provider

    def get_cdn_provider(self, name: str) -> Optional[BaseCDNProvider]:
        return self._cdn_providers.get(name.lower())

    def build_landing(self, manifest_payload: Dict[str, Any], framework: str = "astro") -> BuildResult:
        """
        Compila a Landing Page e gera o fingerprint SHA-256 dos artefatos.
        """
        start_time = time.time()
        manifest_id = manifest_payload.get("id", "OFFER-DEFAULT")
        title = manifest_payload.get("title", "Landing Page")
        headline = manifest_payload.get("headline", "")

        # Cálculo do SHA-256 Fingerprint dos artefatos estáticos
        raw_bytes = f"{manifest_id}|{framework}|{title}|{headline}".encode("utf-8")
        build_fingerprint = hashlib.sha256(raw_bytes).hexdigest()
        build_id = f"BUILD-{framework.upper()}-{build_fingerprint[:8]}"
        build_time = round(time.time() - start_time, 3)

        return BuildResult(
            build_id=build_id,
            framework=framework,
            manifest_id=manifest_id,
            build_fingerprint=build_fingerprint,
            assets_count=5,
            build_time_sec=build_time,
            output_dir=f"dist/{framework}/{manifest_id}"
        )

    def deploy_landing(self, build_result: BuildResult, cdn_name: Optional[str] = None) -> DeploymentRecord:
        """
        Publica os artefatos compilação na CDN selecionada com versionamento.
        """
        cdn = cdn_name or self.config.default_cdn_provider
        provider = self.get_cdn_provider(cdn)
        if not provider:
            raise ValueError(f"Provedor CDN '{cdn}' não está registrado ou ativado.")

        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        version = f"v1.0.0-{build_result.framework}-{timestamp_str}"

        record = provider.deploy_build(build_result, version)
        self._history.append(record)
        return record

    def rollback(self, deployment_id: str) -> RollbackRecord:
        """
        Executa rollback instantâneo restaurando o deploy com deployment_id especificado.
        """
        current_active = next((d for d in reversed(self._history) if d.is_active), None)
        target = next((d for d in self._history if d.deployment_id == deployment_id), None)

        if not target:
            raise ValueError(f"Deploy com ID '{deployment_id}' não encontrado no histórico.")

        if current_active and current_active.deployment_id == deployment_id:
            raise ValueError(f"O deploy '{deployment_id}' já é a versão ativa atual.")

        provider = self.get_cdn_provider(target.cdn_provider)
        if not provider:
            raise ValueError(f"Provedor CDN '{target.cdn_provider}' não disponível para rollback.")

        if current_active:
            rollback_record = provider.rollback_deployment(current_active, target)
        else:
            target.is_active = True
            target.status = "ACTIVE"
            rollback_record = RollbackRecord(
                rollback_id=f"RB-{deployment_id[:8]}",
                previous_deployment_id="NONE",
                restored_deployment_id=target.deployment_id,
                restored_version=target.version,
                status="SUCCESS"
            )

        return rollback_record

    def get_history(self) -> List[DeploymentRecord]:
        return self._history
