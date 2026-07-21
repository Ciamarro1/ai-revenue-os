import pytest
import json
from pathlib import Path
from src.reality.research.schemas import TopicCandidate
from src.reality.research.autonomous_engine import AutonomousResearchEngine

def test_topic_candidate_schema_and_score():
    cand = TopicCandidate(
        topic="Best Notion Templates 2026",
        niche="productivity",
        intent="commercial",
        competition="low",
        estimated_ctr=0.045,
        estimated_rpm=20.00,
        estimated_conversion=0.05,
        confidence=0.90,
        sources=["google_trends", "pinterest_trends"]
    )
    assert cand.topic == "Best Notion Templates 2026"
    assert cand.niche == "productivity"
    # Score = (0.045 * 100) * 20.00 * (0.05 * 100) * 0.90 * 1.2 = 4.5 * 20 * 5 * 0.9 * 1.2 = 486.0
    assert cand.score > 0

def test_autonomous_research_engine_discovery(tmp_path):
    engine = AutonomousResearchEngine(output_dir=tmp_path)
    candidates = engine.discover_topic_candidates("Home Office Decor")

    assert len(candidates) >= 3
    assert all(isinstance(c, TopicCandidate) for c in candidates)

    saved_candidates = engine.get_saved_candidates("Home Office Decor")
    assert len(saved_candidates) >= 3
    assert saved_candidates[0].niche == "home office decor"

def test_autonomous_research_engine_persistence(tmp_path):
    engine = AutonomousResearchEngine(output_dir=tmp_path)
    cand = TopicCandidate(
        topic="Minimalist Desk Setup",
        niche="lifestyle",
        competition="medium"
    )
    paths = engine.save_candidates([cand])
    assert len(paths) == 1
    assert paths[0].exists()

    with open(paths[0], "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["topic"] == "Minimalist Desk Setup"
    assert data["niche"] == "lifestyle"
