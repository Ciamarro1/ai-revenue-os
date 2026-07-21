import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.factory.video.moneyprinterturbo.adapter import MoneyPrinterTurboProvider
from src.factory.schemas import CreativeBrief

def run_test():
    mpt_dir = Path(__file__).parent.parent / "MoneyPrinterTurbo"
    adapter = MoneyPrinterTurboProvider(mpt_dir)
    
    print("🚀 Iniciando teste do MoneyPrinterTurboProvider (Renderizador Puro)...")
    
    brief = CreativeBrief(
        hypothesis_id="TEST-001",
        audience="general",
        emotion="neutral",
        hook="Real wealth isn't about how much money you make, it is about how much you keep.",
        format="short_video",
        duration=45,
        platform="pinterest",
        search_terms=["artificial intelligence", "wealth", "automation", "server room", "luxury"],
        subject="AI Wealth"
    )
    
    try:
        result = adapter.generate(brief)
        print("\n================ TEST RESULTS ================")
        print(f"✅ Success: True")
        print(f"📁 Task Directory: {result.task_dir}")
        print(f"🎞️ Video Path: {result.path}")
        print(f"💬 Subtitles Path: {result.subtitles_path}")
        print(f"🔊 Audio Path: {result.audio_path}")
        print("\n🎉 Vídeo renderizado e salvo perfeitamente!")
    except Exception as e:
        print(f"\n❌ ERRO DETECTADO: {e}")

if __name__ == "__main__":
    run_test()
