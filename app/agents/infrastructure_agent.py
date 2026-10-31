from app.agents.base_agent import BaseAgent
from app.protocols.message_schema import AgentRole, MessageType, AgentMessage, NormalizedTelemetry, AgentFindingPayload
from app.diagnosis.rule_engine import RuleEngine
from app.services.gemini_service import gemini_service

class InfrastructureAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.INFRASTRUCTURE)
        self.system_instruction = (
            "You are a specialized Network Infrastructure Health Analysis AI Agent. "
            "Analyze validated infrastructure telemetry to detect abnormal device behavior. "
            "Identify hardware, interface, queue, and resource problems. Use measured evidence. "
            "Distinguish symptoms from causes. Return structured JSON."
        )

    async def process(self, telemetry: NormalizedTelemetry, incident_id: str, correlation_id: str) -> AgentMessage:
        rule_evidence = RuleEngine.evaluate_infrastructure(telemetry)
        anomalies = [e.interpretation for e in rule_evidence if e.interpretation]

        prompt = (
            f"Analyze infrastructure state for device '{telemetry.device_id}':\n"
            f"- CPU Usage: {telemetry.cpu_usage_pct} %\n"
            f"- Memory Usage: {telemetry.memory_usage_pct} %\n"
            f"- Queue Drops: {telemetry.queue_drops}\n"
            f"- Interface Errors: {telemetry.interface_errors}\n"
            f"- Device Status: {telemetry.device_status}\n"
            f"Rule anomalies: {anomalies}\n"
            "Return JSON matching AgentFindingPayload."
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
            severity = "normal"
            hypothesis = "Device hardware and forwarding plane resources operating normally"
            if telemetry.queue_drops and telemetry.queue_drops > 50:
                severity = "high"
                hypothesis = "Egress buffer exhaustion leading to continuous queue drops"
            elif telemetry.cpu_usage_pct and telemetry.cpu_usage_pct > 85:
                severity = "high"
                hypothesis = "Control plane CPU exhaustion affecting control packet processing"
            elif telemetry.interface_errors and telemetry.interface_errors > 10:
                severity = "high"
                hypothesis = "Physical or data-link layer degradation causing interface CRC errors"

            payload = {
                "hypothesis": hypothesis,
                "severity": severity,
                "evidence": [e.model_dump() for e in rule_evidence],
                "confidence_contribution": 0.85 if rule_evidence else 0.5,
                "anomalies_detected": anomalies,
                "affected_targets": [telemetry.device_id],
                "reasoning_summary": f"Analyzed device queues, interfaces, and CPU/memory allocations.",
                "reasoning_mode": mode
            }

        return self.create_message(
            receiver=AgentRole.CORRELATION,
            incident_id=incident_id,
            correlation_id=correlation_id,
            message_type=MessageType.INFRASTRUCTURE_FINDING,
            payload=payload
        )