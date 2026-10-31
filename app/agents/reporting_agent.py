from typing import List, Dict, Any
from pydantic import BaseModel
from app.agents.base_agent import BaseAgent
from app.protocols.message_schema import (
    AgentRole,
    MessageType,
    AgentMessage,
    NormalizedTelemetry,
)
from app.services.gemini_service import gemini_service

class DiagnosticReportSchema(BaseModel):
    incident_id: str
    status: str
    suspected_root_cause: str
    confidence: float
    affected_devices: List[str]
    supporting_evidence: List[Dict[str, Any]]
    alternative_causes: List[str]
    recommended_actions: List[str]
    evidence_sources: List[str]
    limitations: List[str]
    executive_summary: str

class ReportingAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentRole.REPORTING)
        self.system_instruction = (
            "You are the Recommendation and Reporting AI Agent for NetCoop AI. "
            "Use the validated correlated diagnosis to produce a concise, authoritative engineering report. "
            "Recommend safe, actionable remediation steps for campus network engineers. "
            "Acknowledge diagnostic limitations where measurements were sparse. Return structured JSON."
        )

    async def generate_report(
        self,
        correlation_msg: AgentMessage,
        incident_id: str,
        correlation_id: str
    ) -> AgentMessage:
        c_data = correlation_msg.payload

        prompt = (
            f"Generate a final incident report based on correlated diagnosis:\n"
            f"Root Cause: {c_data.get('suspected_root_cause')}\n"
            f"Confidence: {c_data.get('confidence')} ({c_data.get('confidence_category')})\n"
            f"Affected Devices: {c_data.get('affected_devices')}\n"
            f"Supporting Evidence: {c_data.get('supporting_evidence')}\n"
            f"Alternative Causes: {c_data.get('alternative_causes')}\n"
            "Include practical, non-destructive network troubleshooting recommendations. Output strict JSON."
        )

        gemini_result, mode = await gemini_service.generate_structured(
            system_instruction=self.system_instruction,
            user_prompt=prompt,
            response_schema=DiagnosticReportSchema
        )

        if gemini_result:
            final_report = gemini_result
            final_report["reasoning_mode"] = mode
        else:
            actions = [
                "Verify interface port status and queue discards via CLI (e.g., 'show interface ...')",
                "Cross-check NetFlow/IPFIX telemetry on uplink switches to isolate top talkers",
                "Perform scheduled bandwidth shape review and queue policy adjustments"
            ]
            if "DNS" in str(c_data.get("suspected_root_cause")):
                actions = [
                    "Inspect core recursive DNS forwarders and upstream resolving delays",
                    "Verify DNS service port 53 UDP/TCP reachability across access VLANs"
                ]

            final_report = {
                "incident_id": incident_id,
                "status": c_data.get("status", "diagnosed"),
                "suspected_root_cause": c_data.get("suspected_root_cause", "Undetermined"),
                "confidence": c_data.get("confidence", 0.0),
                "confidence_category": c_data.get("confidence_category", "Unknown"),
                "confidence_explanation": c_data.get("confidence_explanation", ""),
                "affected_devices": c_data.get("affected_devices", []),
                "supporting_evidence": c_data.get("supporting_evidence", []),
                "alternative_causes": c_data.get("alternative_causes", []),
                "recommended_actions": actions,
                "evidence_sources": c_data.get("evidence_sources", []),
                "limitations": [
                    "Root-cause diagnosis requires physical port cross-check before maintenance.",
                    "Single-snapshot capture; long-term NetFlow aggregation recommended for intermittent jitter."
                ],
                "executive_summary": (
                    f"Incident {incident_id} [{c_data.get('status', '').upper()}]: {c_data.get('suspected_root_cause')} "
                    f"with {c_data.get('confidence_category', '')} ({(c_data.get('confidence', 0)*100):.0f}%)."
                ),
                "conflict_detected": c_data.get("conflict_detected", False),
                "conflict_explanation": c_data.get("conflict_explanation", ""),
                "reasoning_mode": mode
            }

        return self.create_message(
            receiver=AgentRole.USER,
            incident_id=incident_id,
            correlation_id=correlation_id,
            message_type=MessageType.FINAL_REPORT,
            payload=final_report
        )

    async def process(self, telemetry: NormalizedTelemetry, incident_id: str, correlation_id: str) -> AgentMessage:
        raise NotImplementedError("Use generate_report() directly.")