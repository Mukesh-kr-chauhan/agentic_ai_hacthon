import React, { useMemo } from 'react';
import { ReactFlow, Background, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { AgentMessage } from '../types';

interface Props {
  messages: AgentMessage[];
  running: boolean;
  onSelectAgent: (agentId: string) => void;
}

export const AgentWorkflowGraph: React.FC<Props> = ({
  messages,
  running,
  onSelectAgent,
}) => {
  const getAgentStatus = (role: string) => {
    const hasMsg = messages.some((m) => m.sender === role);
    if (running && !hasMsg)
      return { label: 'Executing...', color: '#eab308', border: '#ca8a04' };
    if (hasMsg)
      return { label: 'Completed', color: '#10b981', border: '#059669' };
    return { label: 'Idle', color: '#64748b', border: '#475569' };
  };

  const nodes: Node[] = useMemo(
    () => [
      {
        id: 'telemetry_agent',
        position: { x: 30, y: 30 },
        data: {
          label: `Telemetry Agent\n[${getAgentStatus('telemetry_agent').label}]`,
        },
        style: {
          background: '#0f172a',
          color: '#e2e8f0',
          border: `2px solid ${getAgentStatus('telemetry_agent').border}`,
          borderRadius: '8px',
          fontSize: '11px',
          padding: '8px',
          cursor: 'pointer',
        },
      },
      {
        id: 'infrastructure_agent',
        position: { x: 230, y: 30 },
        data: {
          label: `Infrastructure Agent\n[${getAgentStatus('infrastructure_agent').label}]`,
        },
        style: {
          background: '#0f172a',
          color: '#e2e8f0',
          border: `2px solid ${getAgentStatus('infrastructure_agent').border}`,
          borderRadius: '8px',
          fontSize: '11px',
          padding: '8px',
          cursor: 'pointer',
        },
      },
      {
        id: 'connectivity_agent',
        position: { x: 430, y: 30 },
        data: {
          label: `Connectivity Agent\n[${getAgentStatus('connectivity_agent').label}]`,
        },
        style: {
          background: '#0f172a',
          color: '#e2e8f0',
          border: `2px solid ${getAgentStatus('connectivity_agent').border}`,
          borderRadius: '8px',
          fontSize: '11px',
          padding: '8px',
          cursor: 'pointer',
        },
      },
      {
        id: 'correlation_agent',
        position: { x: 230, y: 150 },
        data: {
          label: `Fault Correlation Agent\n[${getAgentStatus('correlation_agent').label}]`,
        },
        style: {
          background: '#0f172a',
          color: '#38bdf8',
          border: `2px solid ${getAgentStatus('correlation_agent').border}`,
          borderRadius: '8px',
          fontSize: '11px',
          fontWeight: 'bold',
          padding: '10px',
          cursor: 'pointer',
        },
      },
      {
        id: 'reporting_agent',
        position: { x: 230, y: 260 },
        data: {
          label: `Recommendation Agent\n[${getAgentStatus('reporting_agent').label}]`,
        },
        style: {
          background: '#0f172a',
          color: '#a78bfa',
          border: `2px solid ${getAgentStatus('reporting_agent').border}`,
          borderRadius: '8px',
          fontSize: '11px',
          fontWeight: 'bold',
          padding: '10px',
          cursor: 'pointer',
        },
      },
    ],
    [messages, running],
  );

  const edges: Edge[] = useMemo(
    () => [
      {
        id: 'w1',
        source: 'telemetry_agent',
        target: 'correlation_agent',
        animated: running,
        style: { stroke: '#38bdf8' },
      },
      {
        id: 'w2',
        source: 'infrastructure_agent',
        target: 'correlation_agent',
        animated: running,
        style: { stroke: '#38bdf8' },
      },
      {
        id: 'w3',
        source: 'connectivity_agent',
        target: 'correlation_agent',
        animated: running,
        style: { stroke: '#38bdf8' },
      },
      {
        id: 'w4',
        source: 'correlation_agent',
        target: 'reporting_agent',
        animated: running,
        style: { stroke: '#a78bfa' },
      },
    ],
    [running],
  );

  return (
    <div className='h-80 w-full rounded-xl bg-[#090d18] border border-slate-800 overflow-hidden relative'>
      <div className='absolute top-3 left-3 z-10 bg-slate-900/80 px-2.5 py-1 rounded border border-slate-700 text-[10px] text-slate-400'>
        Multi-Agent Interoperability Pipeline (Click agent for inspection)
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        onNodeClick={(_, node) => onSelectAgent(node.id)}
      >
        <Background color='#1e293b' gap={16} />
      </ReactFlow>
    </div>
  );
};
