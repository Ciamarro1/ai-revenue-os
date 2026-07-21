from abc import ABC, abstractmethod
from typing import Optional, List
from src.factory.schemas import CreativeBrief, GeneratedAsset

class FactoryProvider(ABC):
    """Contrato base para todos os provedores gerativos da Factory Layer."""
    provider_name: str
    confidence_score: float

class VideoGenerator(FactoryProvider):
    """Contrato abstrato para geração de vídeo (ex: MoneyPrinterTurbo, Runway, Kling)."""
    
    @abstractmethod
    def generate(self, brief: CreativeBrief) -> GeneratedAsset:
        """
        Transforma um briefing científico em um arquivo de mídia físico (MP4).
        """
        pass

class ImageGenerator(FactoryProvider):
    """Contrato abstrato para geração de imagem (ex: NVIDIA FLUX, DALL-E, Stable Diffusion)."""
    
    @abstractmethod
    def generate(self, brief: CreativeBrief) -> GeneratedAsset:
        """
        Transforma um briefing científico em um arquivo de imagem físico (JPG/PNG).
        """
        pass

class FactoryRegistry:
    """Registro Universal de Conectores da Fábrica."""
    
    def __init__(self):
        self.video_generators: List[VideoGenerator] = []
        self.image_generators: List[ImageGenerator] = []
        
    def register_video_generator(self, generator: VideoGenerator):
        self.video_generators.append(generator)
        self.video_generators.sort(key=lambda p: getattr(p, "confidence_score", 0.0), reverse=True)

    def register_image_generator(self, generator: ImageGenerator):
        self.image_generators.append(generator)
        self.image_generators.sort(key=lambda p: getattr(p, "confidence_score", 0.0), reverse=True)
        
    def get_best_video_generator(self) -> Optional[VideoGenerator]:
        return self.video_generators[0] if self.video_generators else None

    def get_best_image_generator(self) -> Optional[ImageGenerator]:
        return self.image_generators[0] if self.image_generators else None
