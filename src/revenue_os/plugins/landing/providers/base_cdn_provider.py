from abc import ABC, abstractmethod
from src.revenue_os.plugins.landing.models import BuildResult, DeploymentRecord, RollbackRecord

class BaseCDNProvider(ABC):
    """
    Interface Abstrata para Provedores de Deploy em Nuvem / CDN (Cloudflare Pages, Vercel, Netlify).
    """

    @property
    @abstractmethod
    def cdn_name(self) -> str:
        pass

    @property
    def is_enabled(self) -> bool:
        return True

    @abstractmethod
    def deploy_build(self, build_result: BuildResult, version: str) -> DeploymentRecord:
        """
        Publica os artefatos compilação na CDN e retorna o DeploymentRecord.
        """
        pass

    @abstractmethod
    def rollback_deployment(self, current_deployment: DeploymentRecord, target_deployment: DeploymentRecord) -> RollbackRecord:
        """
        Executa o rollback instantâneo na CDN para a versão selecionada.
        """
        pass
