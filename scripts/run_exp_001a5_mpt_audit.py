import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.reality.base import CapabilityRegistry
from src.factory.base import FactoryRegistry
from src.reality.research.openmanus_provider import OpenManusProvider
from src.factory.video.moneyprinterturbo.adapter import MoneyPrinterTurboProvider
from src.services.experiment_runner import ExperimentRunner, ExperimentState

def run_audit():
    print("[EXP-001A.5] Iniciando Auditoria Rigorosa de Geração MPT (Sem Publisher)")
    
    db = ExperimentDatabase()
    hypo_registry = HypothesisRegistry(db)
    
    reality_registry = CapabilityRegistry()
    reality_registry.register_research_provider(OpenManusProvider())
    
    factory_registry = FactoryRegistry()
    mpt_dir = Path(r"C:\Users\WDAGUtilityAccount\Downloads\ai rev\MoneyPrinterTurbo")
    mpt_provider = MoneyPrinterTurboProvider(mpt_dir)
    
    if not mpt_provider.python_exe.exists():
        print("❌ ERRO FATAL: Instalação do MPT não encontrada. Auditoria falhou antes de iniciar.")
        sys.exit(1)
        
    factory_registry.register_video_generator(mpt_provider)
    
    runner = ExperimentRunner(
        db=db,
        registry=hypo_registry,
        reality_registry=reality_registry,
        factory_registry=factory_registry,
        require_human_approval=True
    )
    
    print("Executando pipeline ate HUMAN_APPROVED...")
    try:
        res = runner.run_cycle(stop_at_state=ExperimentState.HUMAN_APPROVED)
    except Exception as e:
        res = {"status": "failed", "error": str(e), "step": getattr(runner.ctx.get("state"), "value", str(runner.ctx.get("state")))}
        
    print("\n=======================================================")
    if res["status"] == "success" or res.get("error") == "Awaiting human approval before publishing.":
        print(f"✅ SUCESSO AUDITORIA MPT!")
        print(f"Experimento: {res.get('experiment_id', runner.ctx.get('experiment_id'))}")
        print(f"O Video foi gerado FISICAMENTE no MPT, foi validado, e o Bundle de Artefatos foi criado em 'experiments/{runner.ctx.get('experiment_id')}'.")
    else:
        print(f"❌ FALHA NO CICLO: {res.get('error')}")
        print(f"Estado que falhou: {res.get('step')}")
    print("=======================================================")

if __name__ == "__main__":
    run_audit()
