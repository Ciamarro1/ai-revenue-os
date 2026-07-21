import json
from datetime import datetime, timezone
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.schemas import CreativeGenome

class AssetRegistry:
    """
    Registra os ativos de mídia gerados pela Factory Layer (MP4, PNG), 
    associando a sua estrutura abstrata (CreativeGenome) aos metadados físicos.
    """
    def __init__(self, db: ExperimentDatabase):
        self.db = db
        
    def register_asset(self, asset_id: str, experiment_id: str, factory: str, prompt_hash: str,
                       genome: CreativeGenome, status: str, file_path: str, file_hash: str, 
                       mime_type: str, duration: int, resolution: str, size: int, quality_score: float):
        query = '''
            INSERT INTO assets (
                asset_id, experiment_id, factory, prompt_hash, creative_genome, status, 
                file_path, file_hash, mime_type, duration_seconds, resolution, size_bytes, 
                quality_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        with self.db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                asset_id, experiment_id, factory, prompt_hash, json.dumps(genome.model_dump()), 
                status, file_path, file_hash, mime_type, duration, resolution, size, 
                quality_score, datetime.now(timezone.utc).isoformat() + "Z"
            ))
            conn.commit()
            return asset_id
