from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentRole(str, Enum):
    TELEMETRY = "telemetry_agent"
    INFRASTRUCTURE = "infrastructure_agent"
    CONNECTIVITY = "connectivity_agent"
    CORRELATION = "correlation_agent"
    REPORTING = "reporting_agent"
    ORCHESTRATOR = "orchestrator"
    USER = "user"

class MessageType(str, Enum):
    TELEMETRY_FINDING = "TELEMETRY_FINDING"
    INFRASTRUCTURE_FINDING = "INFRASTRUCTURE_FINDING"
    CONNECTIVITY_FINDING = "CONNECTIVITY_FINDING"
    CORRELATED_DIAGNOSIS = "CORRELATED_DIAGNOSIS"
    FINAL_REPORT = "FINAL_REPORT"
    ERROR_ALERT = "ERROR_ALERT"

class EvidenceItem(BaseModel):
    metric: str
    value: Any
    unit: str
    interpretation: Optional[str] = None

class AgentFindingPayload(BaseModel):
    hypothesis: str
    severity: str = Field(description="low, medium, high, critical, or normal")
    evidence: List[EvidenceItem]
    confidence_contribution: float = Field(ge=0.0, le=1.0)
    anomalies_detected: List[str] = Field(default_factory=list)
    affected_targets: List[str] = Field(default_factory=list)
    reasoning_summary: str

class AgentMessage(BaseModel):
    protocol_version: str = "1.0"
    schema_version: str = "1.0"
    message_id: str
    incident_id: str
    correlation_id: str
    sender: AgentRole
    receiver: AgentRole
    message_type: MessageType
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "success"
    payload: Dict[str, Any]
    validation_errors: Optional[List[str]] = None

class NormalizedTelemetry(BaseModel):
    device_id: str
    device_type: Optional[str] = "switch"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    latency_ms: Optional[float] = None
    jitter_ms: Optional[float] = None
    packet_loss_pct: Optional[float] = None
    throughput_mbps: Optional[float] = None
    link_utilization_pct: Optional[float] = None
    bandwidth_mbps: Optional[float] = None
    cpu_usage_pct: Optional[float] = None
    memory_usage_pct: Optional[float] = None
    queue_drops: Optional[int] = None
    interface_errors: Optional[int] = None
    device_status: Optional[str] = "online"
    wifi_rssi_dbm: Optional[float] = None
    retransmission_rate_pct: Optional[float] = None
    dns_resolution_time_ms: Optional[float] = None
    dns_failure: Optional[bool] = None
    dhcp_lease_success: Optional[bool] = None
    connected_neighbors: List[str] = Field(default_factory=list)
    upstream_uplink: Optional[str] = None
    raw_unrecognized: Dict[str, Any] = Field(default_factory=dict)