"""
Protocol v1.0 Extension: Inter-Agent Evidence Request & Response Schemas.
Backwards compatible with app.protocols.message_schema.
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid


class EvidenceQuery(BaseModel):
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_agent: str = Field(..., description="Target agent, e.g. telemetry_agent")
    requested_metrics: List[str] = Field(..., description="e.g. ['jitter', 'rssi', 'crc_errors']")
    scope: Dict[str, Any] = Field(default_factory=dict, description="e.g. {'device_id': 'sw-core-01'}")
    rationale: str = Field(..., description="Why this evidence is needed by the planner/critic")


class EvidenceRequestEnvelope(BaseModel):
    version: str = "1.0"
    message_type: str = "EVIDENCE_REQUEST"
    incident_id: str
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    query: EvidenceQuery


class EvidenceItem(BaseModel):
    metric: str
    value: Any
    unit: str
    is_anomalous: bool = False
    confidence: float = 1.0
    source_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EvidenceResponseEnvelope(BaseModel):
    version: str = "1.0"
    message_type: str = "EVIDENCE_RESPONSE"
    incident_id: str
    request_id: str
    responder: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: List[EvidenceItem] = Field(default_factory=list)
    status: str = Field(default="SUCCESS", description="SUCCESS, PARTIAL, or NOT_FOUND")