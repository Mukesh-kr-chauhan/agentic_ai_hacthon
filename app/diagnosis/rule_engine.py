from typing import List
from app.protocols.message_schema import NormalizedTelemetry, EvidenceItem

class RuleEngine:
    THRESHOLDS = {
        "latency_ms": 100.0,
        "packet_loss_pct": 2.0,
        "link_utilization_pct": 85.0,
        "cpu_usage_pct": 85.0,
        "memory_usage_pct": 90.0,
        "wifi_rssi_dbm": -75.0, # Below is weak
        "queue_drops": 50,
        "interface_errors": 10
    }

    @classmethod
    def evaluate_telemetry(cls, t: NormalizedTelemetry) -> List[EvidenceItem]:
        evidence = []
        if t.latency_ms is not None and t.latency_ms > cls.THRESHOLDS["latency_ms"]:
            evidence.append(EvidenceItem(
                metric="latency_ms", value=t.latency_ms, unit="ms",
                interpretation=f"Elevated latency (>{cls.THRESHOLDS['latency_ms']}ms)"
            ))
        if t.packet_loss_pct is not None and t.packet_loss_pct > cls.THRESHOLDS["packet_loss_pct"]:
            evidence.append(EvidenceItem(
                metric="packet_loss_pct", value=t.packet_loss_pct, unit="%",
                interpretation=f"High packet loss (>{cls.THRESHOLDS['packet_loss_pct']}%)"
            ))
        if t.link_utilization_pct is not None and t.link_utilization_pct > cls.THRESHOLDS["link_utilization_pct"]:
            evidence.append(EvidenceItem(
                metric="link_utilization_pct", value=t.link_utilization_pct, unit="%",
                interpretation=f"Saturated link utilization (>{cls.THRESHOLDS['link_utilization_pct']}%)"
            ))
        return evidence

    @classmethod
    def evaluate_infrastructure(cls, t: NormalizedTelemetry) -> List[EvidenceItem]:
        evidence = []
        if t.cpu_usage_pct is not None and t.cpu_usage_pct > cls.THRESHOLDS["cpu_usage_pct"]:
            evidence.append(EvidenceItem(
                metric="cpu_usage_pct", value=t.cpu_usage_pct, unit="%",
                interpretation=f"CPU overload (>{cls.THRESHOLDS['cpu_usage_pct']}%)"
            ))
        if t.memory_usage_pct is not None and t.memory_usage_pct > cls.THRESHOLDS["memory_usage_pct"]:
            evidence.append(EvidenceItem(
                metric="memory_usage_pct", value=t.memory_usage_pct, unit="%",
                interpretation=f"Critical memory exhaustion (>{cls.THRESHOLDS['memory_usage_pct']}%)"
            ))
        if t.queue_drops is not None and t.queue_drops > cls.THRESHOLDS["queue_drops"]:
            evidence.append(EvidenceItem(
                metric="queue_drops", value=t.queue_drops, unit="packets",
                interpretation=f"Egress queue drops detected (>{cls.THRESHOLDS['queue_drops']})"
            ))
        if t.interface_errors is not None and t.interface_errors > cls.THRESHOLDS["interface_errors"]:
            evidence.append(EvidenceItem(
                metric="interface_errors", value=t.interface_errors, unit="errors",
                interpretation=f"Interface CRC/frame errors detected (>{cls.THRESHOLDS['interface_errors']})"
            ))
        return evidence

    @classmethod
    def evaluate_connectivity(cls, t: NormalizedTelemetry) -> List[EvidenceItem]:
        evidence = []
        if t.wifi_rssi_dbm is not None and t.wifi_rssi_dbm < cls.THRESHOLDS["wifi_rssi_dbm"]:
            evidence.append(EvidenceItem(
                metric="wifi_rssi_dbm", value=t.wifi_rssi_dbm, unit="dBm",
                interpretation=f"Severely degraded Wi-Fi RSSI (<{cls.THRESHOLDS['wifi_rssi_dbm']}dBm)"
            ))
        if t.dns_failure is True:
            evidence.append(EvidenceItem(
                metric="dns_failure", value=True, unit="bool",
                interpretation="Host resolution failure detected on primary DNS servers"
            ))
        if t.dhcp_lease_success is False:
            evidence.append(EvidenceItem(
                metric="dhcp_lease_success", value=False, unit="bool",
                interpretation="DHCP lease request timed out or was refused"
            ))
        return evidence