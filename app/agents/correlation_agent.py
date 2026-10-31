import json
from typing import List, Dict, Any
from pydantic import BaseModel
from app.agents.base_agent import BaseAgent
from app.protocols.message_schema import (
    AgentRole,
    MessageType,
    AgentMessage,
    EvidenceItem,
    NormalizedTelemetry,
)
from app.diagnosis.confidence_engine import ConfidenceEngine
from app.services.gemini_service import gemini_service

class CorrelatedDiagnosisModel(BaseModel):
    suspected_root_cause: str
    affected_devices: List[str]
    supporting_evidence: List[EvidenceItem]
    alternative_causes: List[str]
    conflict_detected: bool
    conflict_explanation: str
    evidence_sources: List[str]

class CorrelationAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.CORRELATION)
        self.system_instruction = (
            "You are the central Fault Correlation AI Agent in NetCoop AI. "
            "You receive structured findings from specialized agents. Compare hypotheses, correlate evidence, "
            "and identify contradictions. If telemetry is sparse, report insufficient evidence. "
            "Return structured JSON matching the schema."
        )

    async def correlate(
        self,
        messages: List[AgentMessage],
        normalized: NormalizedTelemetry,
        incident_id: str,
        correlation_id: str
    ) -> AgentMessage:
        aggregated_evidence: List[EvidenceItem] = []
        contributing_agents: List[str] = []
        hypotheses: List[Dict[str, Any]] = []
        all_affected: set = set()

        for msg in messages:
            payload = msg.payload
            contributing_agents.append(msg.sender.value)
            hypotheses.append({
                "agent": msg.sender.value,
                "hypothesis": payload.get("hypothesis"),
                "severity": payload.get("severity")
            })
            for ev in payload.get("evidence", []):
                aggregated_evidence.append(EvidenceItem(**ev))
            for tgt in payload.get("affected_targets", []):
                all_affected.add(tgt)

        prompt = (
            f"Correlate the following findings for Incident {incident_id}:\n"
            f"Findings: {json.dumps(hypotheses, indent=2)}\n"
            f"Evidence: {json.dumps([e.model_dump() for e in aggregated_evidence], indent=2)}\n"
            "Identify the corroborated root cause, evaluate contradictions, and return strict JSON."
        )

        gemini_result, mode = await gemini_service.generate_structured(
            system_instruction=self.system_instruction,
            user_prompt=prompt,
            response_schema=CorrelatedDiagnosisModel
        )

        contradictions = False
        if gemini_result:
            payload = gemini_result
            contradictions = gemini_result.get("conflict_detected", False)
        else:
            severities = [h.get("severity") for h in hypotheses]
            has_high = any(s in ("high", "critical") for s in severities)
            has_normal = any(s == "normal" for s in severities)
            contradictions = has_high and has_normal and len(severities) > 1

            active_hypotheses = [h["hypothesis"] for h in hypotheses if h.get("severity") in ("high", "critical")]
            if active_hypotheses:
                root_cause = active_hypotheses[0]
                alt = active_hypotheses[1:] if len(active_hypotheses) > 1 else ["Upstream aggregation buffer drop"]
            elif len(aggregated_evidence) == 0:
                root_cause = "Normal network operation: all metrics within baseline parameters"
                alt = []
            else:
                root_cause = "Performance variance detected without clear fault pattern"
                alt = []

            payload = {
                "suspected_root_cause": root_cause,
                "affected_devices": list(all_affected) if all_affected else [normalized.device_id],
                "supporting_evidence": [e.model_dump() for e in aggregated_evidence],
                "alternative_causes": alt,
                "conflict_detected": contradictions,
                "conflict_explanation": "Contradictory telemetry signals detected between agents." if contradictions else "Findings corroborate across agents.",
                "evidence_sources": contributing_agents
            }

        # Calculate metrics presence count
        metrics_present = sum(1 for v in [
            normalized.latency_ms, normalized.packet_loss_pct, normalized.link_utilization_pct,
            normalized.cpu_usage_pct, normalized.queue_drops, normalized.wifi_rssi_dbm
        ] if v is not None)

        score, cat, explanation, status = ConfidenceEngine.calculate_confidence(
            supporting_evidence=aggregated_evidence,
            contributing_agents=contributing_agents,
            contradictions_present=contradictions,
            is_missing_telemetry=(normalized.device_id == "UNKNOWN_NODE" or metrics_present < 2),
            metrics_count=metrics_present
        )

        payload["confidence"] = score
        payload["confidence_category"] = cat
        payload["confidence_explanation"] = explanation
        payload["status"] = status
        payload["reasoning_mode"] = mode

        return self.create_message(
            receiver=AgentRole.REPORTING,
            incident_id=incident_id,
            correlation_id=correlation_id,
            message_type=MessageType.CORRELATED_DIAGNOSIS,
            payload=payload
        )

    async def process(self, telemetry: NormalizedTelemetry, incident_id: str, correlation_id: str) -> AgentMessage:
        raise NotImplementedError("Use correlate() directly.")