from typing import Optional
from src.revenue_os.plugins.creatives.models import CreativeConfig
from src.revenue_os.plugins.creatives.storage_manager import CreativeStorageManager
from src.revenue_os.plugins.creatives.image_plugin import ImageGenerationPlugin
from src.revenue_os.plugins.creatives.video_plugin import VideoGenerationPlugin
from src.revenue_os.plugins.creatives.benchmark_engine import CreativeBenchmarkEngine

class CreativePluginFactory:
    """
    Factory Pattern para instanciação unificada dos plugins de criação de mídia.
    """

    @staticmethod
    def create_storage_manager(config: Optional[CreativeConfig] = None) -> CreativeStorageManager:
        config = config or CreativeConfig()
        return CreativeStorageManager(base_dir=config.storage_base_dir)

    @staticmethod
    def create_image_plugin(config: Optional[CreativeConfig] = None) -> ImageGenerationPlugin:
        storage = CreativePluginFactory.create_storage_manager(config)
        from src.revenue_os.plugins.creatives.providers import FluxImageProvider, ComfyUIImageProvider
        flux = FluxImageProvider(storage_manager=storage, enabled=config.enable_flux if config else True)
        comfyui = ComfyUIImageProvider(storage_manager=storage, enabled=config.enable_comfyui if config else True)
        return ImageGenerationPlugin(flux_provider=flux, comfyui_provider=comfyui)

    @staticmethod
    def create_video_plugin(config: Optional[CreativeConfig] = None) -> VideoGenerationPlugin:
        storage = CreativePluginFactory.create_storage_manager(config)
        from src.revenue_os.plugins.creatives.providers import MoneyPrinterTurboVideoProvider, RemotionVideoProvider
        mpt = MoneyPrinterTurboVideoProvider(storage_manager=storage, enabled=config.enable_mpt if config else True)
        remotion = RemotionVideoProvider(storage_manager=storage, enabled=config.enable_remotion if config else True)
        return VideoGenerationPlugin(mpt_provider=mpt, remotion_provider=remotion)

    @staticmethod
    def create_benchmark_engine() -> CreativeBenchmarkEngine:
        return CreativeBenchmarkEngine()
