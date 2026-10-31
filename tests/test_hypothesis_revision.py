import pytest
from app.diagnosis.hypothesis_tracker import HypothesisTracker
from app.diagnosis.evidence_critic import EvidenceCritic


def test_evidence_critic_penalizes_incompatible_hypothesis():
    tracker = HypothesisTracker()
    h_wifi = tracker.register_hypothesis("Wi-Fi Signal Degradation", "connectivity_agent", 0.6)
    h_congestion = tracker.register_hypothesis("Upstream Congestion", "telemetry_agent", 0.5)

    critic = EvidenceCritic()
    snapshot = {
        "rssi": -48,            # Great Wi-Fi -> penalize Wi-Fi hypothesis
        "jitter": 35,           # High jitter -> supports congestion
        "port_drops": 250,      # Packet drops -> supports congestion
        "cpu_utilization": 15,
        "crc_errors": 0
    }

    critic.critique_hypotheses(tracker, snapshot)

    assert tracker.hypotheses[h_wifi.id].confidence < 0.6
    assert len(tracker.hypotheses[h_wifi.id].counter_evidence) >= 1

    assert tracker.hypotheses[h_congestion.id].confidence > 0.5
    assert len(tracker.hypotheses[h_congestion.id].supporting_evidence) >= 1