import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class OSSEntry(BaseModel):
    """
    Entrada rica do Catálogo de Ferramentas Open Source (Open Source First V2).
    """
    name: str
    category: str  # marketplaces, landing, automation, analytics, rag, agents, video, storage, search
    license: str   # MIT, Apache-2.0, AGPL-3.0
    maturity: str  # High, Production-Ready, Emerging
    language: str  # Python, TypeScript, Go, Rust
    integration_ease: str # Seamless, Medium, Complex
    use_case: str
    official_url: str
    github_url: str = "https://github.com"
    stars: int = 15000
    last_commit_days_ago: int = 2
    maintenance_score: float = 0.95
    docker_ready: bool = True
    api_available: bool = True
    alternatives: List[str] = Field(default_factory=list)
    integration_status: str = "Active"

class OSSCatalogService:
    """
    Catálogo Vivo de Projetos Open Source (Princípio Open Source First).
    Analisa a manutenção, saúde e adequação de soluções prontas antes de qualquer desenvolvimento.
    """

    def __init__(self, catalog_path: Optional[Path] = None):
        if catalog_path is None:
            self.catalog_path = Path(__file__).parent.parent.parent.parent / "knowledge" / "oss_catalog.json"
        else:
            self.catalog_path = Path(catalog_path)
        self.catalog_path.parent.mkdir(parents=True, exist_ok=True)
        self.entries = self._load_or_create_default()

    def _load_or_create_default(self) -> List[OSSEntry]:
        if self.catalog_path.exists():
            try:
                with open(self.catalog_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [OSSEntry(**item) for item in data]
            except Exception:
                pass

        defaults = [
            OSSEntry(name="Astro / Next.js", category="landing", license="MIT", maturity="High", language="TypeScript", integration_ease="Seamless", use_case="Geração de Landing Pages estáticas de alta velocidade com SSG/SEO", official_url="https://astro.build", github_url="https://github.com/withastro/astro", stars=45000, alternatives=["Hugo", "Gatsby"]),
            OSSEntry(name="Playwright", category="automation", license="Apache-2.0", maturity="High", language="Python/TS", integration_ease="Seamless", use_case="Automação headless de navegadores para redes sociais e scraping", official_url="https://playwright.dev", github_url="https://github.com/microsoft/playwright", stars=62000, alternatives=["Puppeteer", "Selenium"]),
            OSSEntry(name="n8n", category="automation", license="Fair-Code", maturity="High", language="TypeScript", integration_ease="Medium", use_case="Automação de workflows secundários e webhooks sem código", official_url="https://n8n.io", github_url="https://github.com/n8n-io/n8n", stars=48000, alternatives=["Activepieces", "Windmill"]),
            OSSEntry(name="Qdrant / Chroma", category="rag", license="Apache-2.0", maturity="High", language="Python/Rust", integration_ease="Seamless", use_case="Banco vetorial para busca semântica de conhecimentos e genomas", official_url="https://qdrant.tech", github_url="https://github.com/qdrant/qdrant", stars=21000, alternatives=["Milvus", "Weaviate"]),
            OSSEntry(name="Grafana / Metabase", category="analytics", license="AGPL-3.0", maturity="High", language="Go/Java", integration_ease="Seamless", use_case="Visualização de métricas de receita, CTR e ROI", official_url="https://grafana.com", github_url="https://github.com/grafana/grafana", stars=61000, alternatives=["Apache Superset"]),
            OSSEntry(name="PydanticAI", category="agents", license="MIT", maturity="Production-Ready", language="Python", integration_ease="Seamless", use_case="Agentes cognitivos com tipagem estrita e validação de schema", official_url="https://pydantic.dev", github_url="https://github.com/pydantic/pydantic-ai", stars=9500, alternatives=["LangGraph", "CrewAI"]),
            OSSEntry(name="MoneyPrinterTurbo", category="video", license="MIT", maturity="Production-Ready", language="Python", integration_ease="Seamless", use_case="Geração automatizada de vídeos curtos verticais (9:16)", official_url="https://github.com/FujiwaraChoki/MoneyPrinter", github_url="https://github.com/FujiwaraChoki/MoneyPrinter", stars=18000, alternatives=["MoviePy", "FFmpeg"]),
            OSSEntry(name="MinIO", category="storage", license="AGPL-3.0", maturity="High", language="Go", integration_ease="Seamless", use_case="Armazenamento de mídia e assets em conformidade S3", official_url="https://min.io", github_url="https://github.com/minio/minio", stars=46000, alternatives=["LocalStack", "SeaweedFS"]),
            OSSEntry(name="Meilisearch", category="search", license="MIT", maturity="High", language="Rust", integration_ease="Seamless", use_case="Busca instantânea de produtos e tópicos de pesquisa", official_url="https://meilisearch.com", github_url="https://github.com/meilisearch/meilisearch", stars=43000, alternatives=["Typesense", "OpenSearch"])
        ]
        self._save(defaults)
        return defaults

    def _save(self, entries: List[OSSEntry]) -> None:
        with open(self.catalog_path, "w", encoding="utf-8") as f:
            json.dump([e.model_dump() for e in entries], f, indent=2, ensure_ascii=False)

    def search_solution(self, category: str, problem_description: Optional[str] = None) -> List[OSSEntry]:
        matches = [e for e in self.entries if e.category.lower() == category.lower()]
        if not matches and problem_description:
            prob_lower = problem_description.lower()
            matches = [e for e in self.entries if any(w in e.use_case.lower() for w in prob_lower.split())]
        return matches

    def evaluate_oss_health(self, entry_name: str) -> Dict[str, Any]:
        """
        Avalia o status de manutenção e saúde de uma biblioteca Open Source.
        """
        for entry in self.entries:
            if entry.name.lower() == entry_name.lower() or entry_name.lower() in entry.name.lower():
                is_healthy = entry.maintenance_score >= 0.80 and entry.last_commit_days_ago <= 30
                return {
                    "name": entry.name,
                    "status": "HEALTHY" if is_healthy else "WARNING",
                    "maintenance_score": entry.maintenance_score,
                    "stars": entry.stars,
                    "last_commit_days_ago": entry.last_commit_days_ago,
                    "recommended_action": "RETAIN" if is_healthy else f"EVALUATE_ALTERNATIVES: {', '.join(entry.alternatives)}"
                }
        return {"name": entry_name, "status": "UNKNOWN", "recommended_action": "SEARCH_CATALOG"}
