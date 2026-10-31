import React, { useState, useEffect } from 'react';
import {
  Activity,
  ShieldCheck,
  Cpu,
  Terminal,
  Radio,
  AlertTriangle,
  Play,
  RefreshCw,
  Layers,
  FileDown,
  Server,
  Network,
  Ban,
  HelpCircle,
} from 'lucide-react';
import {
  AgentMessage,
  DiagnosticReport,
  TelemetryPoint,
  HypothesisRank,
  TimelineEvent,
} from './types';
import { TelemetryCharts } from './components/TelemetryCharts';
import { EvidenceComparison } from './components/EvidenceComparison';
import { NetworkTopology } from './components/NetworkTopology';
import { AgentWorkflowGraph } from './components/AgentWorkflowGraph';
import { IncidentTimeline } from './components/IncidentTimeline';

const SCENARIOS = [
  {
    id: 'normal',
    label: '1. Normal Network Operation',
    icon: ShieldCheck,
    badge: 'Baseline',
  },
  {
    id: 'link_congestion',
    label: '2. Link Congestion & Buffer Drops',
    icon: AlertTriangle,
    badge: 'Critical',
  },
  {
    id: 'weak_wifi',
    label: '3. Weak Wi-Fi Signal (-84 dBm)',
    icon: Radio,
    badge: 'Warning',
  },
  {
    id: 'interface_failure',
    label: '4. Interface Frame/CRC Errors',
    icon: Cpu,
    badge: 'Critical',
  },
  {
    id: 'dns_failure',
    label: '5. Campus DNS Server Failure',
    icon: Layers,
    badge: 'Critical',
  },
  {
    id: 'dhcp_failure',
    label: '6. DHCP Lease Scope Exhaustion',
    icon: Network,
    badge: 'Critical',
  },
  {
    id: 'conflicting_evidence',
    label: '7. Contradictory Telemetry',
    icon: AlertTriangle,
    badge: 'Conflict',
  },
  {
    id: 'malformed_units',
    label: '8. Incompatible Units (s & frac)',
    icon: RefreshCw,
    badge: 'Normalize',
  },
  {
    id: 'missing_telemetry',
    label: '9. Missing Telemetry (Uncertainty)',
    icon: HelpCircle,
    badge: 'Uncertain',
  },
  {
    id: 'invalid_schema',
    label: '10. Incompatible Schema (v99.0)',
    icon: Ban,
    badge: 'Reject',
  },
];

export default function App() {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [report, setReport] = useState<DiagnosticReport | null>(null);
  const [chartData, setChartData] = useState<TelemetryPoint[]>([]);
  const [hypotheses, setHypotheses] = useState<HypothesisRank[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [running, setRunning] = useState(false);
  const [currentIncident, setCurrentIncident] = useState<string>('');
  const [aiStatus, setAiStatus] = useState<any>({});
  const [schemaError, setSchemaError] = useState<string | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/ai/status')
      .then((r) => r.json())
      .then(setAiStatus)
      .catch(() =>
        setAiStatus({ enabled: false, fallback_reason: 'Backend offline' }),
      );
  }, []);

  const runScenario = async (scenarioId: string) => {
    setRunning(true);
    setSchemaError(null);
    setMessages([]);
    setReport(null);

    const scenarioData: Record<string, any> = {
      normal: {
        device_id: 'HOSTEL_CORE_SW_01',
        latency_ms: 12.4,
        jitter_ms: 2.1,
        packet_loss_pct: 0.0,
        link_utilization_pct: 32.0,
        cpu_usage_pct: 22.0,
        memory_usage_pct: 38.0,
        queue_drops: 0,
        interface_errors: 0,
      },
      link_congestion: {
        device_id: 'HOSTEL_CORE_SW_01',
        latency_ms: 280.0,
        jitter_ms: 48.0,
        packet_loss_pct: 8.5,
        link_utilization_pct: 96.5,
        queue_drops: 195,
        cpu_usage_pct: 91.0,
        memory_usage_pct: 82.0,
      },
      weak_wifi: {
        device_id: 'AP_HOSTEL_BLOCK_A',
        wifi_rssi_dbm: -84.0,
        packet_loss_pct: 5.2,
        latency_ms: 92.0,
        jitter_ms: 36.0,
        link_utilization_pct: 28.0,
      },
      interface_failure: {
        device_id: 'DEPT_CSE_SW_01',
        interface_errors: 184,
        packet_loss_pct: 12.0,
        latency_ms: 45.0,
        queue_drops: 0,
      },
      dns_failure: {
        device_id: 'CAMPUS_CORE_RTR_01',
        dns_failure: true,
        latency_ms: 18.0,
        packet_loss_pct: 0.0,
        link_utilization_pct: 20.0,
      },
      dhcp_failure: {
        device_id: 'AP_HOSTEL_BLOCK_B',
        dhcp_lease_success: false,
        latency_ms: 14.0,
        packet_loss_pct: 0.0,
      },
      conflicting_evidence: {
        device_id: 'HOSTEL_CORE_SW_01',
        latency_ms: 310.0,
        packet_loss_pct: 9.5,
        link_utilization_pct: 12.0,
        queue_drops: 0,
      },
      malformed_units: {
        device_id: 'HOSTEL_CORE_SW_01',
        latency: 0.28,
        utilization: 0.94,
        packet_loss: 0.08,
        queue_drops: '160',
      },
      missing_telemetry: {
        device_id: 'UNKNOWN_NODE',
        latency_ms: 65.0,
      },
      invalid_schema: {
        protocol_version: '99.0',
        device_id: 'MALFORMED_NODE',
      },
    };

    const telemetry =
      scenarioData[scenarioId] || scenarioData['link_congestion'];

    try {
      const res = await fetch('http://localhost:8000/api/diagnose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(telemetry),
      });

      if (!res.ok) {
        const errDetail = await res.json();
        setSchemaError(errDetail.detail || 'Protocol validation error');
        setRunning(false);
        return;
      }

      const data = await res.json();
      const incId = data.incident_id;
      setCurrentIncident(incId);
      setReport(data.report);

      // Instant local chart grounding
      const now = new Date();
      const immediatePoints = [4, 3, 2, 1, 0].map((offset) => {
        const t = new Date(now.getTime() - offset * 15000).toLocaleTimeString();
        const factor = offset === 0 ? 1.0 : offset % 2 === 0 ? 0.95 : 1.05;
        return {
          timestamp: t,
          latency_ms: telemetry.latency_ms
            ? Math.round(telemetry.latency_ms * factor)
            : telemetry.latency
              ? Math.round(telemetry.latency * 1000 * factor)
              : 15,
          jitter_ms: telemetry.jitter_ms
            ? Math.round(telemetry.jitter_ms * factor)
            : 2,
          packet_loss_pct:
            telemetry.packet_loss_pct ??
            (telemetry.packet_loss ? telemetry.packet_loss * 100 : 0),
          link_utilization_pct:
            telemetry.link_utilization_pct ??
            (telemetry.utilization ? telemetry.utilization * 100 : 25),
          cpu_usage_pct: telemetry.cpu_usage_pct ?? 20,
          memory_usage_pct: telemetry.memory_usage_pct ?? 35,
          queue_drops: telemetry.queue_drops
            ? parseInt(String(telemetry.queue_drops))
            : 0,
          interface_errors: telemetry.interface_errors ?? 0,
          wifi_rssi_dbm: telemetry.wifi_rssi_dbm ?? null,
          dns_failure: telemetry.dns_failure ?? false,
          dhcp_lease_success: telemetry.dhcp_lease_success ?? true,
          device_id: telemetry.device_id || 'UNKNOWN_NODE',
        };
      });
      setChartData(immediatePoints);

      const [traceRes, chartRes, evRes, timeRes] = await Promise.all([
        fetch(`http://localhost:8000/api/incidents/${incId}/messages`),
        fetch(`http://localhost:8000/api/incidents/${incId}/chart-data`),
        fetch(`http://localhost:8000/api/incidents/${incId}/evidence`),
        fetch(`http://localhost:8000/api/incidents/${incId}/timeline`),
      ]);

      if (traceRes.ok) setMessages(await traceRes.json());
      if (chartRes.ok) {
        const cData = await chartRes.json();
        if (cData.timeseries && cData.timeseries.length > 0)
          setChartData(cData.timeseries);
      }
      if (evRes.ok) {
        const eData = await evRes.json();
        setHypotheses(eData.hypotheses_ranking || []);
      }
      if (timeRes.ok) {
        const tData = await timeRes.json();
        setTimeline(tData.timeline || []);
      }
    } catch (err) {
      console.error('Diagnosis failed:', err);
    } finally {
      setRunning(false);
    }
  };

  const handleDownload = (format: 'json' | 'markdown') => {
    if (!currentIncident) return;
    window.open(
      `http://localhost:8000/api/incidents/${currentIncident}/report/download?format=${format}`,
      '_blank',
    );
  };

  const getStatusBadge = (status?: string) => {
    if (status === 'healthy') {
      return (
        <span className='px-2.5 py-1 rounded bg-emerald-950 border border-emerald-800 text-emerald-300 font-bold text-xs uppercase'>
          Healthy Network
        </span>
      );
    }
    if (status === 'insufficient_evidence') {
      return (
        <span className='px-2.5 py-1 rounded bg-amber-950 border border-amber-800 text-amber-300 font-bold text-xs uppercase'>
          Insufficient Evidence
        </span>
      );
    }
    return (
      <span className='px-2.5 py-1 rounded bg-red-950 border border-red-800 text-red-300 font-bold text-xs uppercase'>
        Fault Diagnosed
      </span>
    );
  };

  return (
    <div className='min-h-screen bg-[#070b14] text-slate-100 flex flex-col font-sans'>
      {/* Top Header */}
      <header className='border-b border-slate-800 bg-[#0c1220] px-6 py-4 flex items-center justify-between sticky top-0 z-30'>
        <div className='flex items-center space-x-3'>
          <Activity className='w-7 h-7 text-cyan-400 animate-pulse' />
          <div>
            <h1 className='text-xl font-bold tracking-tight text-white flex items-center gap-2'>
              NetCoop AI{' '}
              <span className='text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800'>
                IIT Bhubaneswar
              </span>
            </h1>
            <p className='text-xs text-slate-400'>
              Autonomous Multi-Agent Campus Fault Diagnosis Platform
            </p>
          </div>
        </div>

        {/* AI Verification Badge */}
        <div className='flex items-center gap-3 text-xs'>
          <div className='flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-700'>
            <span
              className={`w-2.5 h-2.5 rounded-full ${aiStatus.enabled ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'}`}
            />
            <span>
              {aiStatus.enabled ? (
                <strong className='text-emerald-300'>
                  Gemini Active ({aiStatus.model})
                </strong>
              ) : (
                <span
                  className='text-amber-300'
                  title={aiStatus.fallback_reason}
                >
                  Fallback: {aiStatus.fallback_reason || 'Deterministic'}
                </span>
              )}
            </span>
          </div>
          <div className='px-3 py-1.5 rounded-full bg-cyan-950/60 border border-cyan-800 text-cyan-300 font-mono'>
            Protocol v1.0
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className='flex-1 flex overflow-hidden'>
        {/* Left Sidebar */}
        <aside className='w-80 border-r border-slate-800 bg-[#0a0f1d] p-4 flex flex-col gap-3 overflow-y-auto'>
          <h2 className='text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1'>
            Fault Injection Scenarios (10)
          </h2>
          <div className='flex flex-col gap-1.5'>
            {SCENARIOS.map((s) => {
              const Icon = s.icon;
              return (
                <button
                  key={s.id}
                  onClick={() => runScenario(s.id)}
                  disabled={running}
                  className='flex items-center justify-between w-full px-3 py-2 rounded-lg text-xs font-medium bg-slate-900/60 border border-slate-800 hover:border-cyan-500 hover:bg-slate-800/90 transition text-left text-slate-200'
                >
                  <div className='flex items-center gap-2.5 truncate'>
                    <Icon className='w-3.5 h-3.5 text-cyan-400 shrink-0' />
                    <span className='truncate'>{s.label}</span>
                  </div>
                  <span className='text-[9px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono'>
                    {s.badge}
                  </span>
                </button>
              );
            })}
          </div>

          {currentIncident && (
            <div className='mt-auto p-3.5 rounded-lg bg-slate-900 border border-slate-800 text-xs space-y-2'>
              <div>
                <span className='text-slate-400 block text-[10px]'>
                  Active Incident Reference
                </span>
                <span className='font-mono text-cyan-400 text-xs font-bold'>
                  {currentIncident}
                </span>
              </div>
              <div className='flex gap-2 pt-2 border-t border-slate-800'>
                <button
                  onClick={() => handleDownload('json')}
                  className='flex-1 py-1 px-2 bg-slate-800 hover:bg-slate-700 rounded text-[10px] font-mono flex items-center justify-center gap-1'
                >
                  <FileDown className='w-3 h-3' /> JSON
                </button>
                <button
                  onClick={() => handleDownload('markdown')}
                  className='flex-1 py-1 px-2 bg-slate-800 hover:bg-slate-700 rounded text-[10px] font-mono flex items-center justify-center gap-1'
                >
                  <FileDown className='w-3 h-3' /> Markdown
                </button>
              </div>
            </div>
          )}
        </aside>

        {/* Center Dashboard */}
        <main className='flex-1 overflow-y-auto p-6 space-y-6'>
          {/* Schema Validation Error Banner */}
          {schemaError && (
            <div className='p-4 rounded-xl bg-red-950/80 border border-red-700 text-red-200 text-xs flex items-center gap-3'>
              <Ban className='w-6 h-6 shrink-0 text-red-400' />
              <div>
                <strong className='block font-semibold'>
                  Protocol Rejection:
                </strong>
                <span>{schemaError}</span>
              </div>
            </div>
          )}

          {/* Diagnostic Report Card */}
          {report && (
            <div className='p-6 rounded-xl bg-[#0f172a] border border-slate-800 shadow-xl space-y-4'>
              <div className='flex items-start justify-between'>
                <div>
                  <div className='flex items-center gap-2 mb-1'>
                    <span className='text-[10px] font-mono text-cyan-400 uppercase tracking-wide'>
                      Corroborated Diagnosis
                    </span>
                    {getStatusBadge(report.status)}
                    <span className='text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono'>
                      Engine: {report.reasoning_mode || 'Hybrid'}
                    </span>
                  </div>
                  <h2 className='text-2xl font-bold text-white mt-1'>
                    {report.suspected_root_cause}
                  </h2>
                </div>
                <div className='text-right'>
                  <div className='inline-block px-3 py-1 rounded-md bg-cyan-950 border border-cyan-800 text-cyan-300 font-mono text-sm font-semibold'>
                    Confidence: {(report.confidence * 100).toFixed(0)}%
                  </div>
                  <span className='block text-[11px] text-slate-400 mt-1'>
                    {report.confidence_category}
                  </span>
                </div>
              </div>

              <p className='text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-3 rounded border border-slate-800'>
                {report.confidence_explanation}
              </p>

              {/* Grid: Actions & Limitations */}
              <div className='grid grid-cols-1 md:grid-cols-2 gap-4 pt-2'>
                <div className='space-y-2'>
                  <span className='text-xs font-semibold text-slate-400 uppercase tracking-wider block'>
                    Recommended Remediations:
                  </span>
                  {report.recommended_actions.map((act, i) => (
                    <div
                      key={i}
                      className='flex items-start gap-2 text-xs text-slate-200'
                    >
                      <ShieldCheck className='w-4 h-4 text-emerald-400 shrink-0 mt-0.5' />
                      <span>{act}</span>
                    </div>
                  ))}
                </div>

                <div className='space-y-2'>
                  <span className='text-xs font-semibold text-slate-400 uppercase tracking-wider block'>
                    Limitations & Uncertainty:
                  </span>
                  {report.limitations?.map((lim, i) => (
                    <div
                      key={i}
                      className='flex items-start gap-2 text-xs text-slate-400'
                    >
                      <HelpCircle className='w-4 h-4 text-amber-400 shrink-0 mt-0.5' />
                      <span>{lim}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Six Real-Time Telemetry Charts */}
          <div>
            <h3 className='text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2'>
              <Activity className='w-4 h-4 text-cyan-400' /> Grounded Network
              Telemetry Stream
            </h3>
            <TelemetryCharts
              data={chartData}
              loading={running}
              deviceId={report?.affected_devices?.[0] || 'HOSTEL_CORE_SW_01'}
            />
          </div>

          {/* Evidence Comparison Ranking Chart */}
          {hypotheses.length > 0 && (
            <EvidenceComparison
              hypotheses={hypotheses}
              conflictDetected={report?.conflict_detected}
            />
          )}

          {/* Multi-Agent Graph & Topology */}
          <div className='grid grid-cols-1 lg:grid-cols-2 gap-6'>
            <div>
              <h3 className='text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2'>
                <Cpu className='w-4 h-4 text-cyan-400' /> Five-Agent Execution
                Graph
              </h3>
              <AgentWorkflowGraph
                messages={messages}
                running={running}
                onSelectAgent={() => {}}
              />
            </div>

            <div>
              <h3 className='text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2'>
                <Network className='w-4 h-4 text-cyan-400' /> Campus L2/L3
                Network Topology
              </h3>
              <NetworkTopology
                affectedDevices={report?.affected_devices || []}
              />
            </div>
          </div>

          {/* Protocol Inspector */}
          <div className='p-5 rounded-xl bg-[#0f172a] border border-slate-800 space-y-4'>
            <div className='flex items-center justify-between'>
              <h3 className='text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2'>
                <Terminal className='w-4 h-4 text-cyan-400' /> Protocol v1.0
                Structured Message Bus Inspector
              </h3>
              <span className='text-xs font-mono text-slate-500'>
                {messages.length} Validated Transmissions
              </span>
            </div>

            <div className='space-y-3 max-h-80 overflow-y-auto'>
              {messages.length === 0 ? (
                <div className='text-xs text-slate-600 italic p-4 text-center'>
                  Select a scenario to observe inter-agent structured messages.
                </div>
              ) : (
                messages.map((m, i) => (
                  <div
                    key={i}
                    className='p-3.5 rounded-lg bg-[#0a0e1a] border border-slate-800 text-xs font-mono space-y-2'
                  >
                    <div className='flex items-center justify-between border-b border-slate-800 pb-1.5 text-[11px]'>
                      <div className='flex items-center gap-2'>
                        <span className='text-cyan-400 font-bold'>
                          {m.sender}
                        </span>
                        <span>→</span>
                        <span className='text-amber-400 font-bold'>
                          {m.receiver}
                        </span>
                      </div>
                      <span className='px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300'>
                        {m.message_type}
                      </span>
                    </div>
                    <pre className='text-slate-300 text-[10px] overflow-x-auto bg-slate-950 p-2 rounded'>
                      {JSON.stringify(m.payload, null, 2)}
                    </pre>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Timeline */}
          {timeline.length > 0 && <IncidentTimeline timeline={timeline} />}
        </main>
      </div>
    </div>
  );
}
