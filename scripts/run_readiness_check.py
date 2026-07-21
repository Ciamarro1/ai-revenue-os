import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.revenue_os.analytics.readiness import AutonomousReadinessGate

def run_check():
    print("===========================================")
    print(" [AI Revenue OS] AUTONOMOUS READINESS GATE ")
    print("===========================================")
    
    # Mockando valores que viriam do DB após as rodadas de testes (EXP-001A.7 e A.8)
    gls = 0.85
    safety = 0.95
    frs = 0.80 # Supondo que o stress test real não rodou ainda com boa margem
    audit = 1.0
    
    gate = AutonomousReadinessGate()
    result = gate.evaluate(gls, safety, frs, audit)
    
    print(f"\nGenome Learning Score: {gls:.2f} (Min: 0.76)")
    print(f"Safety Score         : {safety:.2f} (Min: 0.91)")
    print(f"Factory Reliability  : {frs:.2f} (Min: 0.91 para Produção)")
    print(f"Audit Completeness   : {audit*100:.0f}% (Min: 100% para Produção)")
    
    print("\n-------------------------------------------")
    print(" [ STATUS SINTÉTICO (LABORATÓRIO / CANARY) ]")
    if result["synthetic_authorized"]:
        print("✅ AUTORIZADO")
        print("Você pode executar simulações ou o Canary Release (EXP-001B.0).")
    else:
        print("❌ BLOQUEADO")
        for b in result["synthetic_blockers"]: print(f"- {b}")
        
    print("\n-------------------------------------------")
    print(" [ STATUS DE PRODUÇÃO (LIVE AUTÔNOMO) ]")
    if result["production_authorized"]:
        print("✅ AUTORIZADO")
        print("A arquitetura provou integridade mecânica. Pode rodar totalmente autônomo (EXP-001B).")
    else:
        print("❌ BLOQUEADO")
        for b in result["production_blockers"]: print(f"- {b}")
    print("-------------------------------------------")

if __name__ == "__main__":
    run_check()
