from abc import ABC, abstractmethod
import uuid
from app.protocols.message_schema import (
    AgentRole, AgentMessage, MessageType, NormalizedTelemetry
)

class BaseAgent(ABC):
    def __init__(self, role: AgentRole):
        self.role = role

    def create_message(
        self,
        receiver: AgentRole,
        incident_id: str,
        correlation_id: str,
        message_type: MessageType,
        payload: dict
    ) -> AgentMessage:
        return AgentMessage(
            message_id=f"MSG-{uuid.uuid4().hex[:8].upper()}",
            incident_id=incident_id,
            correlation_id=correlation_id,
            sender=self.role,
            receiver=receiver,
            message_type=message_type,
            payload=payload
        )

    @abstractmethod
    async def process(self, telemetry: NormalizedTelemetry, incident_id: str, correlation_id: str) -> AgentMessage:
        pass