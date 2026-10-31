"""
Evidence Critic: Challenges hypotheses using adversarial heuristics and rule constraints.
"""
from typing import Dict, Any, List, Tuple
from app.diagnosis.hypothesis_tracker import HypothesisTracker, Hypothesis


class EvidenceCritic:
    def __init__(self, conflict_threshold: float = 0.3):
        self.conflict_threshold = conflict_threshold

    def critique_hypotheses(
        self, tracker: HypothesisTracker, telemetry_snapshot: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        critique_results = []

        for h in list(tracker.hypotheses.values()):
            if h.status in ["REJECTED", "CONFIRMED"]:
                continue

            adjustments: List[Tuple[float, str, bool]] = []

            # Rule 1: High latency attributed to Wi-Fi RSSI when Ethernet is flawless
            if "wifi" in h.root_cause.lower():
                rssi = telemetry_snapshot.get("rssi", -50)
                if rssi >= -65:
                    adjustments.append((-0.35, f"Critic penalty: RSSI is healthy ({rssi} dBm), Wi-Fi unlikely root cause.", True))

            # Rule 2: Hardware failure claimed with zero CRC errors and normal CPU
            if "switch" in h.root_cause.lower() or "hardware" in h.root_cause.lower():
                cpu = telemetry_snapshot.get("cpu_utilization", 20)
                crc = telemetry_snapshot.get("crc_errors", 0)
                if cpu < 50 and crc == 0:
                    adjustments.append((-0.4, f"Critic penalty: Switch CPU={cpu}% and CRC={crc}. No physical layer distress.", True))

            # Rule 3: Bufferbloat hypothesis corroborated by jitter + bursty drops
            if "congestion" in h.root_cause.lower() or "bufferbloat" in h.root_cause.lower():
                jitter = telemetry_snapshot.get("jitter", 0)
                drops = telemetry_snapshot.get("port_drops", 0)
                if jitter > 25 and drops > 100:
                    adjustments.append((0.25, f"Critic validation: Elevated jitter ({jitter}ms) with drops ({drops}) strongly supports bufferbloat.", False))

            for delta, reason, is_counter in adjustments:
                tracker.update_hypothesis(h.id, delta, new_evidence=reason, is_counter=is_counter)
                critique_results.append({
                    "hypothesis_id": h.id,
                    "root_cause": h.root_cause,
                    "delta": delta,
                    "reason": reason,
                    "is_counter": is_counter,
                    "resulting_confidence": tracker.hypotheses[h.id].confidence
                })

        return critique_results