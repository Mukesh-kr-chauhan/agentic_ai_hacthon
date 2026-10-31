import asyncio
import uuid

from typing import Any, Dict, Tuple, List
from app.protocols.normalizer import TelemetryNormalizer
from app.protocols.validator import ProtocolValidator
from app.protocols.message_schema import AgentRole, MessageType, AgentMessage
from app.agents.telemetry_agent import TelemetryAgent
from app.agents.infrastructure_agent import InfrastructureAgent
from app.agents.connectivity_agent import ConnectivityAgent
from app.agents.correlation_agent import CorrelationAgent
from app.agents.reporting_agent import ReportingAgent
from app.orchestration.event_bus import event_bus
from app.storage.database import db

class NetworkOrchestrator:
    def __init__(self):
        self.telemetry_agent = TelemetryAgent()
        self.infra_agent = InfrastructureAgent()
        self.conn_agent = ConnectivityAgent()
        self.correlation_agent = CorrelationAgent()
        self.reporting_agent = ReportingAgent()

    async def run_diagnosis(self, raw_telemetry: Dict[str, Any], incident_id: str = None) -> Tuple[str, Dict[str, Any]]:
        incident_id = incident_id or f"INC-{uuid.uuid4().hex[:6].upper()}"
        correlation_id = f"CORR-{uuid.uuid4().hex[:6].upper()}"

        # 1. Normalization & Validation
        normalized, warnings = TelemetryNormalizer.normalize(raw_telemetry)
        
        # Save record
        await db.create_incident(incident_id, raw_telemetry)

        # Notify Start
        start_msg = AgentMessage(
            message_id=f"MSG-{uuid.uuid4().hex[:8].upper()}",
            incident_id=incident_id,
            correlation_id=correlation_id,
            sender=AgentRole.ORCHESTRATOR,
            receiver=AgentRole.USER,
            message_type=MessageType.ERROR_ALERT if warnings else MessageType.TELEMETRY_FINDING,
            payload={"status": "processing_started", "normalization_warnings": warnings}
        )
        await event_bus.publish(incident_id, start_msg)
        await db.save_message(start_msg)

        # 2. Parallel Specialized Agent Execution
        tasks = [
            self.telemetry_agent.process(normalized, incident_id, correlation_id),
            self.infra_agent.process(normalized, incident_id, correlation_id),
            self.conn_agent.process(normalized, incident_id, correlation_id)
        ]
        
        # Execute concurrently with resilience
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid_findings: list[AgentMessage] = []

        for r in results:
            if isinstance(r, AgentMessage):
                is_valid, errs = ProtocolValidator.validate_message(r)
                if is_valid:
                    valid_findings.append(r)
                    await event_bus.publish(incident_id, r)
                    await db.save_message(r)
            else:
                # Agent failed
                err_msg = AgentMessage(
                    message_id=f"MSG-{uuid.uuid4().hex[:8].upper()}",
                    incident_id=incident_id,
                    correlation_id=correlation_id,
                    sender=AgentRole.ORCHESTRATOR,
                    receiver=AgentRole.CORRELATION,
                    message_type=MessageType.ERROR_ALERT,
                    payload={"error": str(r)}
                )
                await event_bus.publish(incident_id, err_msg)
                await db.save_message(err_msg)

        # 3. Fault Correlation
        correlation_msg = await self.correlation_agent.correlate(
            valid_findings, normalized, incident_id, correlation_id
        )
        await event_bus.publish(incident_id, correlation_msg)
        await db.save_message(correlation_msg)

        # 4. Final Recommendation & Report
        report_msg = await self.reporting_agent.generate_report(correlation_msg, incident_id, correlation_id)
        await event_bus.publish(incident_id, report_msg)
        await db.save_message(report_msg)

        final_report = report_msg.payload
        await db.update_incident_report(incident_id, final_report)

        return incident_id, final_report

orchestrator = NetworkOrchestrator()