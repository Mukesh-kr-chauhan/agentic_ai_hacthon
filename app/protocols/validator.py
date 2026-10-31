from typing import List, Tuple
from app.protocols.message_schema import AgentMessage

class ProtocolValidator:
    SUPPORTED_VERSIONS = {"1.0"}

    @classmethod
    def validate_message(cls, message: AgentMessage) -> Tuple[bool, List[str]]:
        errors = []
        if message.protocol_version not in cls.SUPPORTED_VERSIONS:
            errors.append(f"Unsupported protocol_version: {message.protocol_version}")
        if message.schema_version not in cls.SUPPORTED_VERSIONS:
            errors.append(f"Unsupported schema_version: {message.schema_version}")
        if not message.incident_id:
            errors.append("Missing incident_id")
        if not message.message_id:
            errors.append("Missing message_id")
        if not message.payload:
            errors.append("Payload cannot be empty")
        return (len(errors) == 0, errors)