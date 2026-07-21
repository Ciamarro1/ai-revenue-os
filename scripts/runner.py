import sys
import argparse
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.revenue_os.analytics.database import ExperimentDatabase

def manage_unpause(force: bool):
    db = ExperimentDatabase("prod_db.sqlite3")
    state = db.get_system_state("AUTOPAUSE")
    
    if not state or not state.get("active"):
        print("✅ O sistema NÃO está em AUTOPAUSE. Nenhuma ação necessária.")
        return
        
    print(f"🛑 ESTADO ATUAL: AUTOPAUSE = ATIVO")
    print(f"Motivo: {state.get('reason')} - {state.get('subreason')}")
    
    if not force:
        print("\n⚠️ AVISO: O sistema foi paralisado por medidas de segurança da SafetyPolicy.")
        print("Despausar o sistema sem resolver a causa raiz pode gerar danos financeiros ou corromper a operação.")
        ans = input("Tem certeza que deseja liberar a operação? Digite 'CONFIRMAR': ")
        if ans.strip() != "CONFIRMAR":
            print("Operação cancelada.")
            return
            
    # Registrar auditoria
    db.log_event("GLOBAL", "SYSTEM_UNPAUSED", {"previous_reason": state.get("reason"), "forced": force})
    
    # Limpar o estado
    db.set_system_state("AUTOPAUSE", {"active": False})
    print("✅ Sistema despausado com sucesso. O ExperimentRunner voltará a operar.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Revenue OS - Runner CLI")
    parser.add_argument("--unpause", action="store_true", help="Remove o estado global de AUTOPAUSE")
    parser.add_argument("--force", action="store_true", help="Pula a confirmação manual ao despausar")
    args = parser.parse_args()
    
    if args.unpause:
        manage_unpause(args.force)
    else:
        print("Para rodar o worker, utilize os scripts específicos ou passe a flag --unpause.")
