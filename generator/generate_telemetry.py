import json
import os
import random

SCENARIOS = {
    "normal.json": {
        "device_id": "HOSTEL_CORE_SW_01",
        "latency_ms": 14.2,
        "jitter_ms": 2.1,
        "packet_loss_pct": 0.0,
        "link_utilization_pct": 34.0,
        "cpu_usage_pct": 28.0,
        "memory_usage_pct": 42.0,
        "queue_drops": 0,
        "interface_errors": 0,
        "wifi_rssi_dbm": -52.0,
        "dns_failure": False,
        "dhcp_lease_success": True
    },
    "link_congestion.json": {
        "device_id": "HOSTEL_CORE_SW_01",
        "latency_ms": 280.0,
        "jitter_ms": 48.0,
        "packet_loss_pct": 8.5,
        "link_utilization_pct": 96.5,
        "cpu_usage_pct": 91.0,
        "memory_usage_pct": 82.0,
        "queue_drops": 195,
        "interface_errors": 2,
        "upstream_uplink": "CAMPUS_CORE_RTR_01",
        "connected_neighbors": ["AP_HOSTEL_BLOCK_A", "AP_HOSTEL_BLOCK_B"]
    },
    "weak_wifi.json": {
        "device_id": "AP_HOSTEL_BLOCK_A",
        "latency_ms": 85.0,
        "jitter_ms": 32.0,
        "packet_loss_pct": 4.5,
        "wifi_rssi_dbm": -84.0,
        "link_utilization_pct": 22.0,
        "cpu_usage_pct": 35.0,
        "queue_drops": 0
    },
    "interface_failure.json": {
        "device_id": "DEPT_CSE_SW_01",
        "latency_ms": 45.0,
        "packet_loss_pct": 12.0,
        "interface_errors": 184,
        "link_utilization_pct": 28.0,
        "queue_drops": 0
    },
    "dns_failure.json": {
        "device_id": "CAMPUS_CORE_RTR_01",
        "dns_failure": True,
        "latency_ms": 18.0,
        "packet_loss_pct": 0.0,
        "link_utilization_pct": 15.0
    },
    "conflicting_evidence.json": {
        "device_id": "HOSTEL_CORE_SW_01",
        "latency_ms": 290.0,
        "packet_loss_pct": 9.0,
        "link_utilization_pct": 12.0,
        "cpu_usage_pct": 18.0,
        "queue_drops": 0,
        "interface_errors": 0
    },
    "malformed_units.json": {
        "device_id": "HOSTEL_CORE_SW_01",
        "latency": 0.28, # In seconds instead of ms
        "utilization": 0.94, # Fraction instead of percentage
        "packet_loss": 0.08, # Fraction instead of percentage
        "queue_drops": "160" # String representation of int
    }
}

def generate_all():
    target_dir = os.path.join(os.path.dirname(__file__), "..", "scenarios")
    os.makedirs(target_dir, exist_ok=True)
    for filename, data in SCENARIOS.items():
        with open(os.path.join(target_dir, filename), "w") as f:
            json.dump(data, f, indent=2)
    print(f"Generated {len(SCENARIOS)} benchmark scenarios in '{target_dir}'.")

if __name__ == "__main__":
    generate_all()