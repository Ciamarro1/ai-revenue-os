from src.revenue_os.plugins.creatives.job_queue import CreativeJobQueue
from src.revenue_os.plugins.creatives.worker_pool import CreativeWorkerPool
from src.revenue_os.plugins.creatives.models import CreativeJob, GeneratedCreativeAsset

def test_job_queue_priority_order():
    q = CreativeJobQueue()
    
    j_low = CreativeJob(job_id="J1", job_type="image", provider_name="p", prompt="Low", priority="LOW")
    j_high = CreativeJob(job_id="J2", job_type="image", provider_name="p", prompt="High", priority="HIGH")
    
    q.enqueue(j_low)
    q.enqueue(j_high)
    
    # O job HIGH deve ser retirado primeiro
    first = q.dequeue()
    assert first.job_id == "J2"
    
    second = q.dequeue()
    assert second.job_id == "J1"

def test_worker_pool_processing():
    q = CreativeJobQueue()
    pool = CreativeWorkerPool(q)
    
    job = CreativeJob(job_id="J1", job_type="image", provider_name="flux", prompt="Prompt")
    q.enqueue(job)
    
    def mock_handler(j):
        return GeneratedCreativeAsset(
            asset_id="A1", asset_type="image", provider_name=j.provider_name,
            file_path="f.png", content_hash="h", version="v1"
        )
        
    asset = pool.process_next_job(mock_handler)
    assert asset is not None
    assert asset.asset_id == "A1"
    assert job.status == "COMPLETED"
