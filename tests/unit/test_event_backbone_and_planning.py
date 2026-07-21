import pytest
from src.revenue_os.events.domain_events import (
    DomainEvent, ResearchTopicCreated, OpportunitySelected, OfferGenerated
)
from src.revenue_os.events.event_backbone import EventBackbone
from src.revenue_os.planning.planning_engine import PlanningEngine
from src.revenue_os.analytics.economic_brain import EconomicBrain

def test_domain_events_and_backbone():
    backbone = EventBackbone()
    received_events = []

    def on_opportunity(event: DomainEvent):
        received_events.append(event)

    backbone.subscribe("opportunity.selected", on_opportunity)

    evt = OpportunitySelected(payload={"product": "Notion Course", "marketplace": "Hotmart"})
    notified = backbone.publish(evt)

    assert notified == 1
    assert len(received_events) == 1
    assert received_events[0].payload["product"] == "Notion Course"
    assert len(backbone.get_history()) == 1

def test_planning_engine_dag():
    planner = PlanningEngine()
    plan = planner.create_execution_plan(target_daily_revenue_usd=100.0, niche="productivity")

    assert plan["plan_id"] == "PLAN-PRODUCTIVITY-100USD"
    assert plan["total_steps"] == 6
    assert plan["execution_dag_steps"][0]["phase"] == "RESEARCH"
    assert plan["execution_dag_steps"][3]["phase"] == "LANDING_BUILD"

def test_economic_brain_objective_function():
    brain = EconomicBrain()

    # 1. Experimento financeiramente lucrativo
    res_prof = brain.calculate_utility(
        expected_revenue=50.0,
        infra_cost=5.0,
        risk_factor=0.10,
        observations_count=10,
        confidence_delta=0.20
    )
    assert res_prof["total_utility_score"] > 35.0
    assert res_prof["is_approved_for_execution"] is True

    # 2. Experimento financeiramente neutro mas aprovado pelo ganho de conhecimento
    res_learn = brain.calculate_utility(
        expected_revenue=2.0,
        infra_cost=4.0,
        risk_factor=0.05,
        observations_count=100,
        confidence_delta=0.30
    )
    assert res_learn["knowledge_gain_value"] > 3.0
    assert res_learn["is_approved_for_execution"] is True
    assert "Aprovado" in res_learn["approval_reason"]
