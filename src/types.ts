export interface AgentMessage {
  protocol_version: string;
  schema_version: string;
  message_id: string;
  incident_id: string;
  correlation_id: string;
  sender: string;
  receiver: string;
  message_type: string;
  timestamp: string;
  payload: any;
}

export interface DiagnosticReport {
  incident_id: string;
  status: string;
  suspected_root_cause: string;
  confidence: number;
  confidence_category?: string;
  confidence_explanation?: string;
  affected_devices: string[];
  supporting_evidence: Array<{
    metric: string;
    value: any;
    unit?: string;
    interpretation?: string;
  }>;
  alternative_causes: string[];
  recommended_actions: string[];
  evidence_sources: string[];
  reasoning_mode?: string;
  limitations?: string[];
  conflict_detected?: boolean;
}

export interface TelemetryPoint {
  timestamp: string;
  latency_ms: number | null;
  jitter_ms: number | null;
  packet_loss_pct: number | null;
  link_utilization_pct: number | null;
  cpu_usage_pct: number | null;
  memory_usage_pct: number | null;
  queue_drops: number | null;
  interface_errors: number | null;
  wifi_rssi_dbm: number | null;
  dns_failure: boolean | null;
  dhcp_lease_success: boolean | null;
  device_id: string;
}

export interface HypothesisRank {
  hypothesis: string;
  confidence: number;
  type: string;
}

export interface TimelineEvent {
  stage: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  agent: string;
  timestamp: string | null;
  message_id?: string;
}
