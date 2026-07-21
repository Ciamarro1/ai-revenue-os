import sys
import os
import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(str(Path(__file__).parent.parent))

from src.revenue_os.analytics.database import ExperimentDatabase
from src.revenue_os.analytics.hypothesis_registry import HypothesisRegistry
from src.revenue_os.analytics.research_registry import ResearchLedger
from src.reality.base import CapabilityRegistry, Publisher, MetricsProvider, PublishedContent, CanonicalMetrics
from src.factory.base import FactoryRegistry, VideoGenerator, ImageGenerator
from src.factory.schemas import GeneratedAsset
from src.services.experiment_runner import ExperimentRunner, ExperimentState
from src.revenue_os.analytics.genome_library import GenomeLibrary
from src.factory.quality.video_gate import VideoQualityGate

def run_e2e_evidence():
    print("==============================================================")
    print(" [AI Revenue OS] RUNNING END-TO-END PIPELINE WITH EVIDENCE ")
    print("==============================================================")
    
    db_path = "prod_db.sqlite3"
    db = ExperimentDatabase(db_path)
    hypo = HypothesisRegistry(db)
    ledger = ResearchLedger(db)
    genome_lib = GenomeLibrary(db_path="prod_genome.jsonl")
    
    # 1. Factory Registry with Mocks so we don't depend on external APIs/local files
    factory = FactoryRegistry()
    
    mock_video_generator = MagicMock(spec=VideoGenerator)
    mock_video_generator.provider_name = "mock_video_factory"
    mock_video_generator.confidence_score = 1.0
    mock_video_generator.generate.return_value = GeneratedAsset(
        path="mock_video.mp4",
        duration=30,
        resolution="1080x1920",
        provider="mock_video_factory",
        confidence=0.95
    )
    
    mock_image_generator = MagicMock(spec=ImageGenerator)
    mock_image_generator.provider_name = "mock_image_factory"
    mock_image_generator.confidence_score = 1.0
    mock_image_generator.generate.return_value = GeneratedAsset(
        path="mock_image.jpg",
        duration=0,
        resolution="1024x1024",
        provider="mock_image_factory",
        confidence=0.98
    )
    
    factory.register_video_generator(mock_video_generator)
    factory.register_image_generator(mock_image_generator)
    
    # 2. Reality Registry with Mocks and Stochastic providers
    reality = CapabilityRegistry()
    
    # We can use the actual StochasticResearchProvider
    from src.reality.research.stochastic_provider import StochasticResearchProvider
    researcher = StochasticResearchProvider(genome_lib)
    reality.register_research_provider(researcher)
    
    # Mock Publisher
    mock_publisher = MagicMock(spec=Publisher)
    mock_publisher.provider_name = "mock_pinterest_publisher"
    mock_publisher.confidence_score = 1.0
    mock_publisher.publish_image.return_value = PublishedContent(
        content_id="pin_e2e_evidence_123",
        platform="pinterest",
        status="published",
        url="https://pinterest.com/pin/pin_e2e_evidence_123"
    )
    mock_publisher.publish_video.return_value = PublishedContent(
        content_id="pin_e2e_evidence_123",
        platform="pinterest",
        status="published",
        url="https://pinterest.com/pin/pin_e2e_evidence_123"
    )
    reality.register_publisher(mock_publisher)
    
    # Mock MetricsProvider
    mock_metrics_provider = MagicMock(spec=MetricsProvider)
    mock_metrics_provider.provider_name = "mock_pinterest_metrics"
    mock_metrics_provider.confidence_score = 1.0
    mock_metrics_provider.get_metrics.return_value = CanonicalMetrics(
        impressions=1250,
        outbound_clicks=75,
        saves=30
    )
    reality.register_metrics_provider(mock_metrics_provider)
    
    # Run the cycle complete up to CALIBRATED
    print("\n[STAGES START] Starting Experiment Runner...")
    
    # We patch quality check gates to return True
    with patch('src.factory.quality.video_gate.VideoQualityGate.check_quality', return_value=True), \
         patch('src.factory.quality.image_gate.ImageQualityGate.check_quality', return_value=True):
        
        runner = ExperimentRunner(
            db=db,
            registry=hypo,
            reality_registry=reality,
            factory_registry=factory,
            research_ledger=ledger,
            require_human_approval=False  # No pause, go straight through
        )
        runner.is_synthetic = True
        
        # Run entire cycle
        result = runner.run_cycle()
        
    print("\n==============================================================")
    print(" [RUN STATUS] Pipeline finished.")
    print("==============================================================")
    print(f"Status: {result.get('status')}")
    print(f"Final State: {result.get('final_state')}")
    print(f"Experiment ID: {result.get('experiment_id')}")
    print(f"Error (if any): {result.get('error')}")
    print("==============================================================")
    
    if result.get("status") == "success":
        exp_id = result["experiment_id"]
        
        # Verify Manifest Sealing
        exp_dir = Path("experiments") / exp_id
        manifest_path = exp_dir / "manifest.json"
        print(f"\n📁 [EVIDENCE 1: Disk Bundle]")
        print(f"Experiment Directory exists: {exp_dir.exists()}")
        print(f"manifest.json exists (Sealed): {manifest_path.exists()}")
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                manifest_content = json.load(f)
            print(f"Sealed At: {manifest_content.get('sealed_at')}")
            print(f"Bundle Hash: {manifest_content.get('bundle_hash')}")
            print("Files listed in bundle:")
            for fname, details in manifest_content.get("files", {}).items():
                print(f"  - {fname} (SHA256: {details['sha256'][:10]}...)")
                
        # Verify SQLite Database Rows
        print(f"\n🗄️ [EVIDENCE 2: SQLite Database Rows]")
        with db._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch from experiments table
            cursor.execute("SELECT * FROM experiments WHERE experiment_id = ?", (exp_id,))
            exp_row = cursor.fetchone()
            if exp_row:
                print("Table 'experiments' row:")
                for col in exp_row.keys():
                    print(f"  {col}: {exp_row[col]}")
            else:
                print("❌ No row found in 'experiments' table.")
                
            # Fetch from metrics table
            cursor.execute("SELECT * FROM metrics WHERE experiment_id = ?", (exp_id,))
            metrics_row = cursor.fetchone()
            if metrics_row:
                print("\nTable 'metrics' row:")
                for col in metrics_row.keys():
                    print(f"  {col}: {metrics_row[col]}")
            else:
                print("\n❌ No row found in 'metrics' table.")
                
            # Fetch from decisions table
            cursor.execute("SELECT * FROM experiment_decisions WHERE experiment_id = ?", (exp_id,))
            decision_rows = cursor.fetchall()
            print(f"\nTable 'experiment_decisions' rows (Count: {len(decision_rows)}):")
            for row in decision_rows:
                print(f"  - Decision Point: {row['decision_point']} | Chosen Value: {row['chosen_value']} | Reason: {row['reason']}")
                
            # Fetch from events table
            cursor.execute("SELECT * FROM experiment_events WHERE experiment_id = ?", (exp_id,))
            event_rows = cursor.fetchall()
            print(f"\nTable 'experiment_events' rows (Count: {len(event_rows)}):")
            for row in event_rows:
                print(f"  - Event: {row['event_type']} | Payload: {row['payload_json']}")
                
if __name__ == "__main__":
    run_e2e_evidence()
