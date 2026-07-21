import pytest
import sqlite3
import json
import time
from typing import Dict
from src.core.kernel import CognitiveKernel
from src.core.cognition.models import Skill, SkillStep, Provider, Tool, Capability, Action, PlanStep, Plan
from src.revenue_os.analytics.database import ExperimentDatabase
from src.core.events.event_bus import Event

@pytest.fixture
def in_memory_db():
    db = ExperimentDatabase(":memory:")
    # Aplica migrações
    from pathlib import Path
    mig_dir = Path(__file__).parent.parent.parent / "migrations"
    if mig_dir.exists():
        sql_files = sorted([f for f in mig_dir.iterdir() if f.suffix == ".sql"])
        with db._get_conn() as conn:
            c = conn.cursor()
            for sql_file in sql_files:
                with open(sql_file, "r", encoding="utf-8") as f:
                    script = f.read()
                try:
                    c.executescript(script)
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower() and "already exists" not in str(e).lower():
                        raise e
            conn.commit()
    return db

def test_skill_bootstrap_discovery_and_registration(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    # 1. Verificar habilidades semeadas por padrão
    discovered = kernel.skills.discover("niche_opportunity")
    assert len(discovered) == 1
    assert discovered[0].name == "market_research_skill"

    # Verificar que as 5 skills reais estão semeadas
    all_skills = kernel.skills.repository.get_skills()
    assert len(all_skills) >= 5
    names = [s.name for s in all_skills]
    assert "market_research_skill" in names
    assert "generate_creative_assets_skill" in names
    assert "quality_validation_skill" in names
    assert "publish_distribution_skill" in names
    assert "experiment_analysis_skill" in names

    # 2. Registrar nova custom Skill
    custom_skill = Skill(
        name="custom_campaign_skill",
        description="Launch a custom marketing campaign",
        objective="marketing_boost",
        steps=[
            SkillStep(step_order=1, capability_required="Search", input_mapping='{"query": "$.niche"}', output_mapping='{"results": "$.result"}')
        ]
    )
    saved_skill = kernel.skills.register(custom_skill)
    assert saved_skill.id is not None
    
    discovered_custom = kernel.skills.discover("marketing_boost")
    assert len(discovered_custom) == 1
    assert discovered_custom[0].name == "custom_campaign_skill"


def test_skill_execution_telemetry_and_events(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    # Rastrear eventos cognitivos emitidos
    emitted_events = []
    def log_event(event: Event):
        emitted_events.append(event)
    kernel.event_bus.subscribe_global(log_event)

    # Preparar Action vinculada
    obj = kernel.planning.create_objective(description="Marketing", target_metric="CTR")
    plan = kernel.planning.repository.save_plan(Plan(objective_id=obj.id, statement="Test plan"))
    step = kernel.planning.repository.save_plan_step(PlanStep(plan_id=plan.id, step_number=1, action_description="Step"))
    action = kernel.executive.create_action(step.id)

    # Executar a skill market_research_skill
    outputs = kernel.skills.execute(
        skill_name="market_research_skill",
        input_data={"niche": "Notion Organizer Template"},
        action_id=action.id
    )

    assert outputs is not None
    assert "opportunity_id" in outputs
    assert outputs["opportunity_id"] == 100 # Conforme mock handler padrão

    # Verificar banco de execuções
    all_execs = kernel.skills.repository.get_skill_step_executions(1)
    assert len(all_execs) == 4 # 4 passos no market_research_skill
    assert all_execs[0].status == "Completed"
    assert all_execs[3].status == "Completed"
    
    # Verificar eventos do EventBus
    event_types = [e.event_type for e in emitted_events]
    assert "SkillStarted" in event_types
    assert "SkillStepCompleted" in event_types
    assert "SkillCompleted" in event_types


def test_skill_execution_retry_policy_recovery(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)

    # Registrar capacidade customizada e handler instável
    run_attempts = 0
    def unstable_handler(inputs: Dict) -> Dict:
        nonlocal run_attempts
        run_attempts += 1
        if run_attempts < 3:
            raise RuntimeError("API timeout connection error")
        return {"result": "Recovered Output"}

    kernel.skills.register_handler("UnstableCap", unstable_handler)

    # Registrar Skill customizada com política de retentativas
    unstable_skill = Skill(
        name="unstable_test_skill",
        description="Tests retry logic recovery",
        objective="recovery_test",
        steps=[
            SkillStep(
                step_order=1,
                capability_required="UnstableCap",
                input_mapping="{}",
                output_mapping='{"final_value": "$.result"}',
                retry_policy='{"max_attempts": 4, "delay": 0.1}'
            )
        ]
    )
    kernel.skills.register(unstable_skill)

    res = kernel.skills.execute("unstable_test_skill", {})
    assert res["final_value"] == "Recovered Output"
    assert run_attempts == 3 # Recuperou-se na 3ª tentativa!


def test_skill_execution_failure_propagation(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)
    
    emitted_events = []
    def log_event(event: Event):
        emitted_events.append(event)
    kernel.event_bus.subscribe_global(log_event)

    # Registrar handler que sempre quebra
    def failing_handler(inputs: Dict) -> Dict:
        raise ValueError("Fatal authorization error")

    kernel.skills.register_handler("FailingCap", failing_handler)

    failing_skill = Skill(
        name="failing_test_skill",
        description="Fails permanently",
        objective="fail_test",
        steps=[
            SkillStep(step_order=1, capability_required="FailingCap", input_mapping="{}")
        ]
    )
    kernel.skills.register(failing_skill)

    with pytest.raises(RuntimeError) as exc_info:
        kernel.skills.execute("failing_test_skill", {})
    
    assert "Fatal authorization error" in str(exc_info.value)

    # Verificar que evento SkillFailed foi emitido
    event_types = [e.event_type for e in emitted_events]
    assert "SkillFailed" in event_types


def test_quality_validation_skill_execution(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)

    # Executar a skill quality_validation_skill
    outputs = kernel.skills.execute(
        skill_name="quality_validation_skill",
        input_data={"media_path": "creative_sample.png", "approved_title": "Validation Title"}
    )

    assert outputs is not None
    assert "approved" in outputs
    assert "quality_score" in outputs


def test_nested_result_output_parsing(in_memory_db):
    kernel = CognitiveKernel(in_memory_db)

    # Executar a skill generate_creative_assets_skill
    outputs = kernel.skills.execute(
        skill_name="generate_creative_assets_skill",
        input_data={"creative_prompt": "Minimalist Home Office Decor"}
    )

    assert outputs is not None
    assert "media_path" in outputs
    assert outputs["media_path"] == "temp_val_creative.png"
    assert outputs["approved_title"] == "Asset Title"
    assert outputs["approved_description"] == "Asset Description"
