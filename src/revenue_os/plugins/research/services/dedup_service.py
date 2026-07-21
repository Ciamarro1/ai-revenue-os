import hashlib
import re
from typing import List, Tuple
from src.revenue_os.plugins.research.models import ResearchOpportunity

class DeduplicationService:
    """
    Serviço de Deduplicação determinística baseada em Hash SHA-256 de título/URL normalizados.
    """

    @staticmethod
    def generate_hash(opp: ResearchOpportunity) -> str:
        raw_string = f"{opp.product_name.lower().strip()}|{opp.affiliate_url.lower().strip()}"
        cleaned = re.sub(r'\s+', ' ', raw_string)
        return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:16]

    def deduplicate(self, opportunities: List[ResearchOpportunity]) -> Tuple[List[ResearchOpportunity], int]:
        seen_hashes = set()
        deduped: List[ResearchOpportunity] = []
        removed_count = 0

        for opp in opportunities:
            h = self.generate_hash(opp)
            opp.dedup_hash = h

            if h not in seen_hashes:
                seen_hashes.add(h)
                deduped.append(opp)
            else:
                removed_count += 1

        return deduped, removed_count
