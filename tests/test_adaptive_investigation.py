import pytest
from app.orchestration.investigation_state import InvestigationState
from app.orchestration.agent_planner import AgentPlanner


def test_planner_dispatch_rounds():
    state = InvestigationState(incident_id="INC-901")
    planner = AgentPlanner(max_rounds=3)

    queries_r1 = planner.plan_next_actions(state)
    assert len(queries_r1) >= 1
    assert queries_r1[0].target_agent == "telemetry_agent"

    state.add_evidence("latency", 120)
    state.advance_round()

    queries_r2 = planner.plan_next_actions(state)
    target_agents = [q.target_agent for q in queries_r2]
    assert "infrastructure_agent" in target_agents
    assert state.current_round == 2