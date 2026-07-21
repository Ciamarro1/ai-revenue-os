import pytest
from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.knowledge_graph import KnowledgeGraph


@pytest.fixture
def temp_db():
    return ExperimentDatabase(":memory:")


@pytest.fixture
def graph(temp_db):
    return KnowledgeGraph(db=temp_db)


def test_add_relation(graph, temp_db):
    graph.add_relation("home office", "notebook", 1.5)
    related = graph.get_related_concepts("home office")
    assert len(related) == 1
    assert related[0][0] == "notebook"
    assert related[0][1] == 1.5


def test_add_relation_conflict(graph):
    graph.add_relation("home office", "notebook", 1.0)
    graph.add_relation("home office", "notebook", 0.5)
    related = graph.get_related_concepts("home office")
    assert related[0][1] == 1.5


def test_get_related_concepts_filter(graph):
    graph.add_relation("home office", "notebook", 1.0)
    graph.add_relation("home office", "chatgpt", 0.3)
    related = graph.get_related_concepts("home office", min_weight=0.5)
    assert len(related) == 1
    assert related[0][0] == "notebook"


def test_traverse_graph(graph):
    graph.add_relation("home office", "notebook", 1.0)
    graph.add_relation("notebook", "chatgpt", 1.0)
    graph.add_relation("chatgpt", "openai", 1.0)
    
    reached = graph.traverse_graph("home office", max_depth=2)
    assert "notebook" in reached
    assert "chatgpt" in reached
    assert "openai" not in reached  # Depth is 3, limit is 2
