from src.revenue_os.plugins.creatives.models import (
    CreativeJob,
    GeneratedCreativeAsset,
    BenchmarkResult,
    CreativeConfig
)

def test_creative_job_schema():
    job = CreativeJob(job_id="JOB-1", job_type="image", provider_name="flux", prompt="A cat", priority="HIGH")
    assert job.job_id == "JOB-1"
    assert job.priority == "HIGH"
    assert job.status == "QUEUED"

def test_generated_creative_asset_schema():
    asset = GeneratedCreativeAsset(
        asset_id="AST-1",
        asset_type="video",
        provider_name="mpt",
        file_path="storage/creatives/videos/render.mp4",
        content_hash="hash123",
        version="v1.0.0"
    )
    assert asset.asset_id == "AST-1"
    assert asset.asset_type == "video"
    assert asset.content_hash == "hash123"

def test_benchmark_result_schema():
    b = BenchmarkResult(
        total_jobs=10,
        successful_jobs=10,
        failed_jobs=0,
        total_time_sec=1.5,
        average_latency_sec=0.15,
        throughput_jobs_per_sec=6.67,
        success_rate_pct=100.0
    )
    assert b.successful_jobs == 10
    assert b.success_rate_pct == 100.0
