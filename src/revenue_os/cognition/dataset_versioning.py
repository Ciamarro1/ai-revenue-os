import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class DatasetVersionManager:
    """
    Dataset & Knowledge Version Manager (Fase III Live Operations).
    Garante a linhagem causal rastreável:
    Dataset Version ➔ Knowledge Version ➔ Genome Version ➔ Decision.
    Permite rollback de modelos ou regras caso haja degradação preditiva.
    """

    def __init__(self, version_log_path: Optional[Path] = None):
        if version_log_path is None:
            self.version_log_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "dataset_versions.json"
        else:
            self.version_log_path = Path(version_log_path)
        self.version_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.versions = self._load()

    def _load(self) -> List[Dict[str, Any]]:
        if self.version_log_path.exists():
            try:
                with open(self.version_log_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def create_dataset_version(self, dataset_name: str, records_count: int, knowledge_version: str = "KV-1.0") -> Dict[str, Any]:
        version_id = f"DSV-{len(self.versions)+1:03d}"
        record = {
            "dataset_version_id": version_id,
            "dataset_name": dataset_name,
            "records_count": records_count,
            "knowledge_version": knowledge_version,
            "genome_version": f"GV-{version_id}",
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "status": "ACTIVE"
        }

        self.versions.append(record)
        with open(self.version_log_path, "w", encoding="utf-8") as f:
            json.dump(self.versions, f, indent=2, ensure_ascii=False)

        return record

    def get_latest_version(self) -> Optional[Dict[str, Any]]:
        return self.versions[-1] if self.versions else None
