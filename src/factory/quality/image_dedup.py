import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.revenue_os.analytics.database import ExperimentDatabase

logger = logging.getLogger("revenue_os.image_dedup")

# Tenta importar imagehash; fallback gracioso se não instalado
try:
    import imagehash
    from PIL import Image
    HAS_IMAGEHASH = True
except ImportError:
    HAS_IMAGEHASH = False
    logger.warning("imagehash não instalado. Anti-duplicação de imagem desativada. Instale com: pip install imagehash")


class ImageDeduplicator:
    """
    Usa hashes perceptuais (pHash, aHash, dHash) para detectar
    imagens visualmente similares, mesmo com texto diferente.
    
    O Pinterest é altamente visual — thumbs parecidas mesmo com textos
    diferentes podem ser flaggadas como spam.
    """
    
    def __init__(self, db: ExperimentDatabase, hamming_threshold: int = 10):
        self.db = db
        self.threshold = hamming_threshold
        self._ensure_table()
    
    def _ensure_table(self):
        """Garante que a tabela image_hashes existe."""
        try:
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS image_hashes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        experiment_id TEXT,
                        file_path TEXT,
                        phash TEXT,
                        ahash TEXT,
                        dhash TEXT,
                        created_at TEXT
                    )
                ''')
                conn.commit()
        except Exception as e:
            logger.error(f"Erro ao criar tabela image_hashes: {e}")
    
    def compute_hashes(self, image_path: str) -> Optional[Dict[str, str]]:
        """
        Calcula pHash, aHash e dHash para uma imagem.
        Retorna None se imagehash não estiver instalado ou imagem inválida.
        """
        if not HAS_IMAGEHASH:
            return None
        
        try:
            img = Image.open(image_path)
            return {
                "phash": str(imagehash.phash(img)),
                "ahash": str(imagehash.average_hash(img)),
                "dhash": str(imagehash.dhash(img)),
            }
        except Exception as e:
            logger.error(f"Erro ao calcular hashes para {image_path}: {e}")
            return None
    
    def is_duplicate(self, image_path: str) -> Dict[str, Any]:
        """
        Compara os hashes perceptuais da imagem contra o histórico no DB.
        Hamming distance <= threshold = duplicata.
        
        Retorna: {"duplicate": bool, "similar_to": str|None, "distance": int|None}
        """
        if not HAS_IMAGEHASH:
            return {"duplicate": False, "reason": "imagehash_not_installed"}
        
        hashes = self.compute_hashes(image_path)
        if not hashes:
            return {"duplicate": False, "reason": "hash_computation_failed"}
        
        try:
            current_phash = imagehash.hex_to_hash(hashes["phash"])
            
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute("SELECT experiment_id, file_path, phash FROM image_hashes ORDER BY created_at DESC LIMIT 50")
                rows = c.fetchall()
                
                for row in rows:
                    stored_exp_id, stored_path, stored_phash_str = row
                    if not stored_phash_str:
                        continue
                    try:
                        stored_phash = imagehash.hex_to_hash(stored_phash_str)
                        distance = current_phash - stored_phash
                        if distance <= self.threshold:
                            return {
                                "duplicate": True,
                                "similar_to": stored_exp_id,
                                "similar_path": stored_path,
                                "distance": distance,
                                "threshold": self.threshold
                            }
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.error(f"Erro ao verificar duplicatas: {e}")
        
        return {"duplicate": False, "distance": None}
    
    def register_hash(self, image_path: str, experiment_id: str):
        """Calcula e salva os hashes no DB para futuras comparações."""
        hashes = self.compute_hashes(image_path)
        if not hashes:
            logger.warning(f"Não foi possível registrar hash para {image_path}")
            return
        
        try:
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            with self.db._get_conn() as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO image_hashes (experiment_id, file_path, phash, ahash, dhash, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (experiment_id, image_path, hashes["phash"], hashes["ahash"], hashes["dhash"], now))
                conn.commit()
            logger.info(f"Hash registrado para {experiment_id}: pHash={hashes['phash']}")
        except Exception as e:
            logger.error(f"Erro ao registrar hash: {e}")
