from app.agents.base_agent import BaseAgent
from app.protocols.message_schema import AgentRole, MessageType, AgentMessage, NormalizedTelemetry, AgentFindingPayload
from app.diagnosis.rule_engine import RuleEngine
from app.services.gemini_service import gemini_service

class ConnectivityAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.CONNECTIVITY)
        self.system_instruction = (
            "You are a Network Connectivity and Topology Analysis AI Agent. "
            "Analyze network topology and connectivity evidence. Identify which devices and network segments are affected. "
            "Evaluate possible link, Wi-Fi, DNS, DHCP, and routing-related explanations. "
            "Never invent topology connections. Return structured findings with explicit evidence."
        )

    async def process(self, telemetry: NormalizedTelemetry, incident_id: str, correlation_id: str) -> AgentMessage:
        rule_evidence = RuleEngine.evaluate_connectivity(telemetry)
        anomalies = [e.interpretation for e in rule_evidence if e.interpretation]

        prompt = (
            f"Analyze connectivity for '{telemetry.device_id}':\n"
            f"- Wi-Fi RSSI: {telemetry.wifi_rssi_dbm} dBm\n"
            f"- DNS Resolution Failure: {telemetry.dns_failure}\n"
            f"- DHCP Success: {telemetry.dhcp_lease_success}\n"
            f"- Connected Neighbors: {telemetry.connected_neighbors}\n"
            f"- Upstream Uplink: {telemetry.upstream_uplink}\n"
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
            hypothesis = "Layer 1 to Layer 3 access and upstream links active"
            if telemetry.dns_failure:
                severity = "critical"
                hypothesis = "DNS resolver unreachable or recurring query timeout"
            elif telemetry.dhcp_lease_success is False:
                severity = "critical"
                hypothesis = "DHCP scope exhausted or relay agent unresponsive"
            elif telemetry.wifi_rssi_dbm and telemetry.wifi_rssi_dbm < -75:
                severity = "medium"
                hypothesis = "Poor RF propagation or client distance causing weak Wi-Fi signal"

            affected = [telemetry.device_id]
            if telemetry.upstream_uplink:
                affected.append(telemetry.upstream_uplink)

            payload = {
                "hypothesis": hypothesis,
                "severity": severity,
                "evidence": [e.model_dump() for e in rule_evidence],
                "confidence_contribution": 0.8 if rule_evidence else 0.4,
                "anomalies_detected": anomalies,
                "affected_targets": affected,
                "reasoning_summary": "Evaluated radio signal, service probes (DNS/DHCP), and link topologies.",
                "reasoning_mode": mode
            }

        return self.create_message(
            receiver=AgentRole.CORRELATION,
            incident_id=incident_id,
            correlation_id=correlation_id,
            message_type=MessageType.CONNECTIVITY_FINDING,
            payload=payload
        )