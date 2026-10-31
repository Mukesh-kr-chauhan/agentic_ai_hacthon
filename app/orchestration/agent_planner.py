"""
Dynamic step planner scheduling agent tasks and evidence collection rounds.
"""
from typing import List, Dict, Any
from app.orchestration.investigation_state import InvestigationState
from app.protocols.evidence_request import EvidenceQuery


class AgentPlanner:
    def __init__(self, max_rounds: int = 3):
        self.max_rounds = max_rounds

    def plan_next_actions(self, state: InvestigationState) -> List[EvidenceQuery]:
        """
        Examines unresolved hypotheses and generates targeted queries for agents.
        """
        planned_queries: List[EvidenceQuery] = []

        # If hypotheses are missing physical infrastructure metrics
        infra_checked = any("cpu" in k or "drops" in k for k in state.collected_evidence.keys())
        telemetry_checked = any("latency" in k or "jitter" in k for k in state.collected_evidence.keys())
        wifi_checked = any("rssi" in k or "dns" in k for k in state.collected_evidence.keys())

        if not telemetry_checked:
            planned_queries.append(
                EvidenceQuery(
                    target_agent="telemetry_agent",
                    requested_metrics=["latency", "jitter", "packet_loss"],
                    scope={"stage": "ingress_egress"},
                    rationale="Initial baseline telemetry required to isolate latency vs packet loss."
                )
            )

        if not infra_checked and state.current_round >= 1:
            planned_queries.append(
                EvidenceQuery(
                    target_agent="infrastructure_agent",
                    requested_metrics=["cpu_utilization", "crc_errors", "port_drops"],
                    scope={"stage": "switches_and_gateways"},
                    rationale="Investigate hardware saturation or interface corruptions."
                )
            )

        if not wifi_checked and state.current_round >= 2:
            planned_queries.append(
                EvidenceQuery(
                    target_agent="connectivity_agent",
                    requested_metrics=["wifi_rssi", "dns_latency", "dhcp_ack"],
                    scope={"stage": "last_hop"},
                    rationale="Check last-mile access link and core service discovery."
                )
            )

        state.log_turn(
            agent="agent_planner",
            action="PLAN",
            inputs={"current_round": state.current_round},
            output_state={"queries_planned": [q.model_dump() for q in planned_queries]},
            rationale=f"Round {state.current_round} investigation task dispatch."
        )

        return planned_queries