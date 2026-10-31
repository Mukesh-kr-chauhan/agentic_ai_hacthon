import pytest
from app.protocols.evidence_request import EvidenceQuery, EvidenceRequestEnvelope, EvidenceItem, EvidenceResponseEnvelope


def test_evidence_request_envelope_contract():
    query = EvidenceQuery(
        target_agent="telemetry_agent",
        requested_metrics=["jitter", "loss"],
        rationale="Corroborate bufferbloat"
    )
    req = EvidenceRequestEnvelope(
        incident_id="INC-100",
        sender="agent_planner",
        query=query
    )
    assert req.version == "1.0"
    assert req.query.target_agent == "telemetry_agent"

    item = EvidenceItem(metric="jitter", value=42.5, unit="ms", is_anomalous=True)
    res = EvidenceResponseEnvelope(
        incident_id="INC-100",
        request_id=req.request_id,
        responder="telemetry_agent",
        payload=[item]
    )
    assert res.status == "SUCCESS"
    assert res.payload[0].value == 42.5