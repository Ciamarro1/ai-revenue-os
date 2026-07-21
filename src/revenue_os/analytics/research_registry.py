import json
from contextlib import contextmanager
from typing import List, Optional
from src.reality.research.schemas import ResearchReport
from src.revenue_os.analytics.database import ExperimentDatabase

class ResearchLedger:
    """
    Mantém o histórico de evidências coletadas na camada de Realidade (OpenManus, Crawl4AI, etc).
    Isso é vital para auditar qual evidência gerou qual hipótese.
    """
    def __init__(self, db: ExperimentDatabase):
        self.db = db

    def save_report(self, report: ResearchReport) -> int:
        query = '''
            INSERT INTO research_reports (
                query, provider, timestamp, sources, trends, competitors, keywords, confidence, source_quality, sample_size
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        with self.db._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                report.query,
                report.provider,
                report.timestamp.isoformat() + "Z",
                json.dumps(report.sources),
                json.dumps(report.trends),
                json.dumps(report.competitors),
                json.dumps(report.keywords),
                report.confidence,
                report.source_quality,
                report.sample_size
            ))
            conn.commit()
            return cursor.lastrowid

    def get_report(self, report_id: int) -> Optional[ResearchReport]:
        query = 'SELECT * FROM research_reports WHERE id = ?'
        with self.db._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (report_id,))
            row = cursor.fetchone()
            
        if not row:
            return None
            
        return ResearchReport(
            query=row["query"],
            provider=row["provider"],
            sources=json.loads(row["sources"]),
            trends=json.loads(row["trends"]),
            competitors=json.loads(row["competitors"]),
            keywords=json.loads(row["keywords"]),
            confidence=row["confidence"],
            source_quality=row["source_quality"] if "source_quality" in row.keys() else 0.8,
            sample_size=row["sample_size"] if "sample_size" in row.keys() else 10
        )
