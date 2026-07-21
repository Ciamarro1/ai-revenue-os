import sys, os, time, json
import zipfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

def run_storage_maintenance():
    print("===========================================")
    print(" [AI Revenue OS] STORAGE MAINTENANCE WORKER")
    print("===========================================")
    
    exp_dir = Path("experiments")
    if not exp_dir.exists():
        print("Diretório experiments/ não existe. Pulando.")
        return
        
    now = time.time()
    day_in_sec = 24 * 3600
    
    compressed_count = 0
    removed_count = 0
    freed_space = 0
    errors = []
    
    for d in exp_dir.iterdir():
        if not d.is_dir():
            continue
            
        try:
            mtime = d.stat().st_mtime
            age_days = (now - mtime) / day_in_sec
            
            if age_days > 365:
                size = sum(f.stat().st_size for f in d.rglob('*') if f.is_file())
                shutil.rmtree(d)
                freed_space += size
                removed_count += 1
                
            elif age_days > 30:
                zip_path = d.with_suffix('.zip')
                if not zip_path.exists():
                    original_size = sum(f.stat().st_size for f in d.rglob('*') if f.is_file())
                    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, _, files in os.walk(d):
                            for file in files:
                                zipf.write(os.path.join(root, file), 
                                           os.path.relpath(os.path.join(root, file), d))
                    shutil.rmtree(d)
                    new_size = zip_path.stat().st_size
                    freed_space += (original_size - new_size)
                    compressed_count += 1
                    
        except Exception as e:
            errors.append(f"{d.name}: {str(e)}")

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "compressed_directories": compressed_count,
        "removed_directories": removed_count,
        "freed_space_mb": round(freed_space / (1024 * 1024), 2),
        "errors": errors
    }
    
    with open("storage_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print(json.dumps(report, indent=2))
    print("✅ Maintenance Complete.")

if __name__ == "__main__":
    run_storage_maintenance()
