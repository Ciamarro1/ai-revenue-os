import os
import subprocess
from pathlib import Path

def main():
    project_root = Path(__file__).parent.parent
    db_full_path = project_root / "knowledge" / "mlflow.db"
    
    # Ensure the knowledge directory exists
    db_full_path.parent.mkdir(parents=True, exist_ok=True)
    
    tracking_uri = f"sqlite:///{db_full_path}"
    
    print(f"🚀 Iniciando servidor MLflow em http://localhost:5000")
    print(f"📊 Tracking URI: {tracking_uri}")
    print(f"Pressione Ctrl+C para encerrar.\n")
    
    try:
        subprocess.run([
            "mlflow", "ui", 
            "--backend-store-uri", tracking_uri,
            "--port", "5000"
        ], cwd=project_root)
    except KeyboardInterrupt:
        print("\nServidor MLflow encerrado.")
    except Exception as e:
        print(f"Erro ao iniciar servidor MLflow: {e}")

if __name__ == "__main__":
    main()
