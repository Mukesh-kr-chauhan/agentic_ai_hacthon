import json
from app.agents.base_agent import BaseAgent
from app.protocols.message_schema import AgentRole, MessageType, AgentMessage, NormalizedTelemetry, AgentFindingPayload
from app.diagnosis.rule_engine import RuleEngine
from app.services.gemini_service import gemini_service

class TelemetryAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.TELEMETRY)
        self.system_instruction = (
            "You are a specialized Network Telemetry and Performance Analysis AI Agent. "
            "Your responsibility is to analyze validated network performance measurements and identify potential abnormalities. "
            "Use only the telemetry provided to you. Identify measurable performance problems, describe the supporting metrics, "
            "and suggest plausible fault hypotheses. Do not fabricate measurements. Return findings as structured JSON."
        )

    async def process(self, telemetry: NormalizedTelemetry, incident_id: str, correlation_id: str) -> AgentMessage:
        rule_evidence = RuleEngine.evaluate_telemetry(telemetry)
        anomalies = [e.interpretation for e in rule_evidence if e.interpretation]

        prompt = (
            f"Analyze this telemetry for device '{telemetry.device_id}':\n"
            f"- Latency: {telemetry.latency_ms} ms\n"
            f"- Jitter: {telemetry.jitter_ms} ms\n"
            f"- Packet Loss: {telemetry.packet_loss_pct} %\n"
            f"- Link Utilization: {telemetry.link_utilization_pct} %\n"
            f"- Throughput: {telemetry.throughput_mbps} Mbps\n"
            f"Known rule-based anomalies: {anomalies}\n"
            "Respond strictly in JSON matching the schema."
        )

        gemini_result, mode = await gemini_service.generate_structured(
            system_instruction=self.system_instruction,
            user_prompt=prompt,
            response_schema=AgentFindingPayload
        )

        if gemini_result:
            payload = gemini_result
            payload["reasoning_mode"] = mode
        else:
            # Deterministic Fallback
            severity = "normal"
            hypothesis = "Performance metrics within expected campus operational baselines"
            if telemetry.link_utilization_pct and telemetry.link_utilization_pct > 85:
                severity = "high"
                hypothesis = "Likely link congestion causing queueing delays and packet loss"
            elif telemetry.latency_ms and telemetry.latency_ms > 100:
                severity = "medium"
                hypothesis = "Excessive latency degradation along the path"

            payload = {
                "hypothesis": hypothesis,
                "severity": severity,
                "evidence": [e.model_dump() for e in rule_evidence],
                "confidence_contribution": 0.85 if rule_evidence else 0.5,
                "anomalies_detected": anomalies,
                "affected_targets": [telemetry.device_id],
                "reasoning_summary": f"Deterministic analysis observed {len(rule_evidence)} metric thresholds crossed.",
                "reasoning_mode": mode
            }

        return self.create_message(
            receiver=AgentRole.CORRELATION,
            incident_id=incident_id,
            correlation_id=correlation_id,
            message_type=MessageType.TELEMETRY_FINDING,
            payload=payload
        )