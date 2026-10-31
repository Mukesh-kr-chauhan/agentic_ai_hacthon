import pytest
from app.protocols.message_schema import NormalizedTelemetry, AgentRole, MessageType, AgentMessage
from app.protocols.normalizer import TelemetryNormalizer
from app.protocols.validator import ProtocolValidator
from app.diagnosis.confidence_engine import ConfidenceEngine
from app.orchestration.orchestrator import orchestrator

@pytest.mark.asyncio
async def test_normal_network_scenario():
    normal_telemetry = {
        "device_id": "HOSTEL_CORE_SW_01",
        "latency_ms": 12.0,
        "packet_loss_pct": 0.0,
        "link_utilization_pct": 30.0,
        "cpu_usage_pct": 20.0
    }
    incident_id, rep = await orchestrator.run_diagnosis(normal_telemetry)
    assert rep["status"] == "healthy"
    assert rep["confidence"] > 0.80

@pytest.mark.asyncio
async def test_missing_telemetry_uncertainty():
    sparse_telemetry = {
        "device_id": "UNKNOWN_NODE",
        "latency_ms": 60.0
    }
    incident_id, rep = await orchestrator.run_diagnosis(sparse_telemetry)
    assert rep["status"] == "insufficient_evidence"
    assert rep["confidence"] < 0.40

@pytest.mark.asyncio
async def test_unit_normalization():
    raw = {"latency": 0.28, "utilization": 0.94, "packet_loss": 0.08}
    norm, warnings = TelemetryNormalizer.normalize(raw)
    assert norm.latency_ms == 280.0
    assert norm.link_utilization_pct == 94.0
    assert norm.packet_loss_pct == 8.0
    assert len(warnings) == 3