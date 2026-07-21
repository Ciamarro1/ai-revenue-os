"""
Testes unitários para a Memory & Retrieval Layer (Sprint 5 + 5.5).

Todos os testes rodam contra SQLite :memory:, sem dependência de Docker/Qdrant.
"""
import pytest

from src.core.memory.sqlite_memory import SQLiteMemoryProvider
from src.core.memory.vector_memory import VectorMemoryProvider
from src.core.memory.retrieval import MemoryRetriever
from src.adapters.qdrant.embedding import EmbeddingPipeline
from src.adapters.qdrant.client import QdrantConnector, is_qdrant_available
from src.adapters.llamaindex.adapter import LlamaIndexAdapter
from src.revenue_os.analytics.database import ExperimentDatabase


@pytest.fixture
def in_memory_db():
    """Inicializa um banco relacional em memória para testes."""
    return ExperimentDatabase(":memory:")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SQLite Memory Provider
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_sqlite_memory_provider_store_and_search(in_memory_db):
    provider = SQLiteMemoryProvider(in_memory_db)

    id1 = provider.store(
        content="Finance campaign minimal design pins got 4.8 percent CTR",
        memory_type="episodic",
        metadata={"niche": "finance", "variant": "minimal"},
    )
    id2 = provider.store(
        content="Lifestyle campaign cozy recipe videos got 1.2 percent CTR",
        memory_type="episodic",
        metadata={"niche": "lifestyle", "variant": "cozy"},
    )

    assert id1 == "1"
    assert id2 == "2"

    results = provider.search("finance CTR", limit=2)
    assert len(results) >= 1
    assert results[0]["id"] == "1"
    assert "Finance campaign minimal design" in results[0]["content"]
    assert results[0]["score"] > 0.0


def test_sqlite_memory_jaccard_ranking(in_memory_db):
    provider = SQLiteMemoryProvider(in_memory_db)

    provider.store(
        content="high conversion hooks for finance topics on passive income",
        memory_type="declarative",
        metadata={"niche": "finance"},
    )
    provider.store(
        content="recipes and home cooking ideas for young lifestyle segments",
        memory_type="declarative",
        metadata={"niche": "lifestyle"},
    )

    results = provider.search("finance passive income hooks", limit=2)
    assert len(results) == 1
    assert "high conversion hooks" in results[0]["content"]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Vector Memory Provider (Fallback)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_vector_memory_provider_fallback(in_memory_db):
    """VectorMemoryProvider deve funcionar perfeitamente via fallback SQLite."""
    provider = VectorMemoryProvider(in_memory_db)

    # Qdrant deve estar offline em ambiente de teste
    assert provider.qdrant_client is None
    assert provider.qdrant_ready is False

    mem_id = provider.store(
        content="Cozy recipe pins degrade rapidly on week days",
        memory_type="pattern",
        metadata={"niche": "lifestyle"},
    )

    assert mem_id is not None

    results = provider.search("Cozy recipe", limit=1)
    assert len(results) == 1
    assert "Cozy recipe pins" in results[0]["content"]


def test_vector_memory_retrieve_context_fallback(in_memory_db):
    """retrieve_context deve formatar memórias mesmo no fallback SQLite."""
    provider = VectorMemoryProvider(in_memory_db)

    provider.store(
        content="Video pins outperform static images in fitness niche",
        memory_type="episodic",
        metadata={"niche": "fitness", "platform": "pinterest"},
    )

    ctx = provider.retrieve_context("fitness video pins", limit=1)
    assert "Video pins outperform" in ctx
    assert "Tipo: episodic" in ctx


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Memory Retriever
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_memory_retriever_context_building(in_memory_db):
    provider = SQLiteMemoryProvider(in_memory_db)
    retriever = MemoryRetriever(provider)

    provider.store(
        content="Finance minimal clips got high click saves",
        memory_type="episodic",
        metadata={"niche": "finance"},
    )

    context = retriever.get_agent_context(current_niche="finance", query="minimal clips")

    assert "MEMÓRIAS OPERACIONAIS E APRENDIZADOS ANTERIORES" in context
    assert "Finance minimal clips" in context
    assert "Tipo: episodic" in context


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Embedding Pipeline (Sprint 5.5)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_embedding_pipeline_hash_fallback():
    """O hash-fallback deve gerar vetores de dimensão correta e normalizados."""
    pipeline = EmbeddingPipeline(vector_size=384)

    vec = pipeline.embed("Pinterest organic traffic has high conversion potential")

    assert len(vec) == 384
    # Verifica normalização L2 (magnitude ≈ 1.0)
    magnitude = sum(v * v for v in vec) ** 0.5
    assert abs(magnitude - 1.0) < 0.01


def test_embedding_pipeline_deterministic():
    """O mesmo texto deve produzir sempre o mesmo vetor (determinístico)."""
    pipeline = EmbeddingPipeline(vector_size=384)

    vec_a = pipeline.embed("test consistency")
    vec_b = pipeline.embed("test consistency")

    assert vec_a == vec_b


def test_embedding_pipeline_different_texts():
    """Textos diferentes devem produzir vetores distintos."""
    pipeline = EmbeddingPipeline(vector_size=384)

    vec_a = pipeline.embed("finance passive income")
    vec_b = pipeline.embed("cooking recipe blog")

    assert vec_a != vec_b


def test_embedding_pipeline_batch():
    """embed_batch deve retornar uma lista de vetores com dimensões corretas."""
    pipeline = EmbeddingPipeline(vector_size=384)

    texts = ["alpha text", "beta text", "gamma text"]
    vecs = pipeline.embed_batch(texts)

    assert len(vecs) == 3
    for v in vecs:
        assert len(v) == 384


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Qdrant Connector (Sprint 5.5)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_qdrant_connector_offline():
    """QdrantConnector.connect() deve retornar False quando Qdrant está offline."""
    connector = QdrantConnector(host="localhost", port=6333, timeout=0.1)
    result = connector.connect()

    # Em ambiente de teste, Qdrant não está rodando
    assert result is False
    assert connector.is_connected is False


def test_qdrant_availability_flag():
    """is_qdrant_available() reflete se qdrant-client está instalado."""
    # Não testa o valor exato, apenas que retorna bool
    assert isinstance(is_qdrant_available(), bool)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LlamaIndex Adapter (Sprint 5.5)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_llamaindex_adapter_create_document():
    """Adapter deve criar documentos estruturados mesmo sem LlamaIndex instalado."""
    adapter = LlamaIndexAdapter()

    doc = adapter.create_document(
        text_content="Vídeos curtos convertem mais no Pinterest",
        metadata={"niche": "finance", "confidence": 0.82},
    )

    assert doc["content"] == "Vídeos curtos convertem mais no Pinterest"
    assert doc["metadata"]["niche"] == "finance"
    assert doc["metadata"]["confidence"] == 0.82


def test_llamaindex_adapter_parse_batch():
    """parse_documents deve converter múltiplos textos em dicts estruturados."""
    adapter = LlamaIndexAdapter()

    texts = ["texto A", "texto B"]
    metas = [{"tag": "a"}, {"tag": "b"}]
    docs = adapter.parse_documents(texts, metas)

    assert len(docs) == 2
    assert docs[0]["content"] == "texto A"
    assert docs[1]["metadata"]["tag"] == "b"



