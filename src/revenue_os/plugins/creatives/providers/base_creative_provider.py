from abc import ABC, abstractmethod
from src.revenue_os.plugins.creatives.models import GeneratedCreativeAsset

class BaseImageProvider(ABC):
    """
    Interface Abstrata para Provedores Gerativos de Imagem.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    def is_enabled(self) -> bool:
        return True

    @abstractmethod
    def generate_image(self, prompt: str, filename: str) -> GeneratedCreativeAsset:
        pass


class BaseVideoProvider(ABC):
    """
    Interface Abstrata para Provedores Gerativos de Vídeo.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    def is_enabled(self) -> bool:
        return True

    @abstractmethod
    def generate_video(self, prompt: str, filename: str) -> GeneratedCreativeAsset:
        pass
