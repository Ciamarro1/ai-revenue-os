import sys, time
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.factory.base import FactoryRegistry
from src.factory.video.moneyprinterturbo.adapter import MoneyPrinterTurboProvider
from src.factory.schemas import CreativeBrief
import numpy as np
import psutil
import shutil

def stress_test():
    mpt_dir = Path(r"C:\Users\WDAGUtilityAccount\Downloads\ai rev\MoneyPrinterTurbo")
    provider = MoneyPrinterTurboProvider(mpt_dir)
    
    times = []
    rams = []
    failures = 0
    
    print("Iniciando Factory Stress Test (10 Renders)...")
    for i in range(10):
        t0 = time.time()
        try:
            brief = CreativeBrief(
                hypothesis_id="stress", audience="testers", emotion="neutral", 
                hook=f"Stress Test {i}", format="short_video", duration=10, 
                platform="youtube", search_terms=["stress", "test"], subject="stress"
            )
            asset = provider.generate(brief)
            dur = time.time() - t0
            times.append(dur)
            rams.append(psutil.virtual_memory().percent)
            print(f"[{i+1}/10] Render OK em {dur:.1f}s")
        except Exception as e:
            failures += 1
            print(f"[{i+1}/10] FAILED: {e}")
            
    if times:
        p50 = np.percentile(times, 50)
        p90 = np.percentile(times, 90)
        p99 = np.percentile(times, 99)
        avg = np.mean(times)
        
        print("\n=== STRESS TEST RESULTS ===")
        print(f"P50: {p50:.1f}s")
        print(f"P90: {p90:.1f}s")
        print(f"P99: {p99:.1f}s")
        print(f"AVG: {avg:.1f}s")
        print(f"Avg RAM Usage: {np.mean(rams):.1f}%")
        print(f"Failures: {failures}/10")
        
        disk = shutil.disk_usage("/")
        print(f"Free Disk: {disk.free / (1024**3):.1f} GB")

if __name__ == "__main__":
    stress_test()
