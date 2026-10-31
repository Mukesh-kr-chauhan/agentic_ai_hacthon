from typing import Any, Dict, Tuple
from app.protocols.message_schema import NormalizedTelemetry

class TelemetryNormalizer:
    @staticmethod
    def normalize(raw: Dict[str, Any]) -> Tuple[NormalizedTelemetry, list[str]]:
        warnings: list[str] = []
        data = dict(raw)
        
        # 1. Normalize Latency: seconds -> ms
        if "latency" in data and "latency_ms" not in data:
            val = float(data.pop("latency"))
            if val < 5.0: # Explicitly declared seconds
                data["latency_ms"] = round(val * 1000.0, 2)
                warnings.append(f"Normalized 'latency' ({val}s) to 'latency_ms' ({data['latency_ms']})")
            else:
                data["latency_ms"] = val

        # 2. Normalize Link Utilization: fraction -> pct
        if "utilization" in data and "link_utilization_pct" not in data:
            val = float(data.pop("utilization"))
            if 0.0 <= val <= 1.0:
                data["link_utilization_pct"] = round(val * 100.0, 2)
                warnings.append(f"Normalized 'utilization' ({val}) fraction to percentage ({data['link_utilization_pct']}%)")
            else:
                data["link_utilization_pct"] = val

        # 3. Normalize Packet Loss: fraction -> pct
        if "packet_loss" in data and "packet_loss_pct" not in data:
            val = float(data.pop("packet_loss"))
            if 0.0 <= val <= 1.0:
                data["packet_loss_pct"] = round(val * 100.0, 2)
                warnings.append(f"Normalized 'packet_loss' ({val}) fraction to percentage ({data['packet_loss_pct']}%)")
            else:
                data["packet_loss_pct"] = val

        # 4. Device ID fallback
        if "device_id" not in data or not str(data["device_id"]).strip():
            data["device_id"] = "UNKNOWN_NODE"
            warnings.append("Missing device_id; assigned UNKNOWN_NODE")

        # 5. Type Conversions
        for int_field in ["queue_drops", "interface_errors"]:
            if int_field in data and data[int_field] is not None:
                try:
                    data[int_field] = int(data[int_field])
                except (ValueError, TypeError):
                    warnings.append(f"Invalid integer value for {int_field}: {data[int_field]}")
                    data[int_field] = None

        fields = NormalizedTelemetry.model_fields.keys()
        recognized = {k: v for k, v in data.items() if k in fields}
        unrecognized = {k: v for k, v in data.items() if k not in fields}
        recognized["raw_unrecognized"] = unrecognized

        return NormalizedTelemetry(**recognized), warnings