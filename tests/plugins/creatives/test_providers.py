import os
from src.revenue_os.plugins.creatives.providers import (
    FluxImageProvider,
    ComfyUIImageProvider,
    MoneyPrinterTurboVideoProvider,
    RemotionVideoProvider
)
from src.revenue_os.plugins.creatives.storage_manager import CreativeStorageManager

def test_flux_image_provider(tmp_path):
    storage = CreativeStorageManager(base_dir=str(tmp_path))
    flux = FluxImageProvider(storage_manager=storage)
    
    asset = flux.generate_image("Test Prompt", "flux_test.png")
    assert asset.provider_name == "flux"
    assert asset.asset_type == "image"
    assert os.path.exists(asset.file_path)

def test_comfyui_image_provider(tmp_path):
    storage = CreativeStorageManager(base_dir=str(tmp_path))
    comfyui = ComfyUIImageProvider(storage_manager=storage)
    
    asset = comfyui.generate_image("Test Prompt", "comfy_test.png")
    assert asset.provider_name == "comfyui"
    assert os.path.exists(asset.file_path)

def test_mpt_video_provider(tmp_path):
    storage = CreativeStorageManager(base_dir=str(tmp_path))
    mpt = MoneyPrinterTurboVideoProvider(storage_manager=storage)
    
    asset = mpt.generate_video("Test Script", "mpt_test.mp4")
    assert asset.provider_name == "money_printer_turbo"
    assert asset.asset_type == "video"
    assert os.path.exists(asset.file_path)

def test_remotion_video_provider(tmp_path):
    storage = CreativeStorageManager(base_dir=str(tmp_path))
    remotion = RemotionVideoProvider(storage_manager=storage)
    
    asset = remotion.generate_video("Test Script", "remotion_test.mp4")
    assert asset.provider_name == "remotion"
    assert os.path.exists(asset.file_path)
