import pytest
from src.revenue_os.analytics.genome_library import Genome, GenomeLibrary

def test_genome_schema_and_score():
    genome = Genome(
        hook="Negative Curiosity",
        emotion="Urgency",
        visual_style="Minimalist Dark",
        colors=["#000000", "#FF0000"],
        cta="Click link in bio",
        length=15,
        music="Lo-Fi Beats",
        narration="Whisper Voice",
        platform="pinterest",
        audience="young_adults",
        topic="finance",
        offer="Budget Planner Notion",
        keywords=["budget", "money", "savings"],
        thumbnail="thumb_001.png",
        posting_time="19:00",
        format="pin_video",
        ctr=0.08,
        save_rate=0.12,
        conversion_rate=0.04,
        revenue=45.0,
        observations_count=15
    )

    assert genome.hook == "Negative Curiosity"
    assert genome.score > 0

def test_genome_library_catalog_and_ranking(tmp_path):
    jsonl_file = tmp_path / "test_genomes.jsonl"
    lib = GenomeLibrary(db_path=str(jsonl_file))

    attrs_a = {"hook": {"type": "Curiosity"}, "emotion": "Urgency", "niche": "finance"}
    attrs_b = {"hook": {"type": "Question"}, "emotion": "Calm", "niche": "finance"}

    lib.extract_and_catalog("genome_a", attrs_a, reward=0.85, is_real_world=True)
    lib.extract_and_catalog("genome_b", attrs_b, reward=0.30, is_real_world=True)

    best = lib.get_best_genomes(top_n=2)
    assert len(best) >= 1
    assert best[0]["genome_id"] == "genome_a"
