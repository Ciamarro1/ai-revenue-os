import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.genome_library import GenomeLibrary
from src.services.calibration.calibration_service import CalibrationService

def run_sync():
    print("===========================================")
    print(" [AI Revenue OS] METRICS SYNC WORKER       ")
    print("===========================================")
    
    db_path = "prod_db.sqlite3" # O mesmo DB do Canary
    db = ExperimentDatabase(db_path)
    genome_lib = GenomeLibrary(db_path="prod_genome.jsonl")
    
    service = CalibrationService(db=db, genome_library=genome_lib)
    
    if service.has_urgent_pending():
        print("Sincronizando com as APIs sociais (ex: Pinterest)...")
        service.process_pending_experiments()
        print("-------------------------------------------")
        print("✅ Genomas autônomos atualizados com dados orgânicos.")
    else:
        print("Nenhum experimento publicado aguardando calibração.")

if __name__ == "__main__":
    run_sync()
