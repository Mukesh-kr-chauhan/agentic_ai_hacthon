import React, { useMemo } from 'react';
import { ReactFlow, Background, Controls, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

interface Props {
  affectedDevices: string[];
}

export const NetworkTopology: React.FC<Props> = ({ affectedDevices = [] }) => {
  const isAffected = (id: string) => affectedDevices.includes(id);

  const nodes: Node[] = useMemo(
    () => [
      {
        id: 'CAMPUS_CORE_RTR_01',
        position: { x: 260, y: 30 },
        data: { label: 'Campus Core Router 01' },
        style: {
          background: isAffected('CAMPUS_CORE_RTR_01') ? '#450a0a' : '#0f172a',
          color: isAffected('CAMPUS_CORE_RTR_01') ? '#fca5a5' : '#38bdf8',
          border: `2px solid ${isAffected('CAMPUS_CORE_RTR_01') ? '#ef4444' : '#0284c7'}`,
          borderRadius: '8px',
          fontSize: '11px',
          fontWeight: 'bold',
          padding: '10px',
        },
      },
      {
        id: 'DNS_SRV_CAMPUS',
        position: { x: 490, y: 120 },
        data: { label: 'Primary DNS (10.0.0.53)' },
        style: {
          background: isAffected('DNS_SRV_CAMPUS') ? '#450a0a' : '#0f172a',
          color: isAffected('DNS_SRV_CAMPUS') ? '#fca5a5' : '#e2e8f0',
          border: `2px solid ${isAffected('DNS_SRV_CAMPUS') ? '#ef4444' : '#475569'}`,
          borderRadius: '8px',
          fontSize: '11px',
          padding: '10px',
        },
      },
      {
        id: 'HOSTEL_CORE_SW_01',
        position: { x: 120, y: 150 },
        data: { label: 'Hostel Core SW 01' },
        style: {
          background: isAffected('HOSTEL_CORE_SW_01') ? '#450a0a' : '#0f172a',
          color: isAffected('HOSTEL_CORE_SW_01') ? '#fca5a5' : '#38bdf8',
          border: `2px solid ${isAffected('HOSTEL_CORE_SW_01') ? '#ef4444' : '#0284c7'}`,
          borderRadius: '8px',
          fontSize: '11px',
          fontWeight: 'bold',
          padding: '10px',
        },
      },
      {
        id: 'DEPT_CSE_SW_01',
        position: { x: 340, y: 150 },
        data: { label: 'CSE Edge Switch 01' },
        style: {
          background: isAffected('DEPT_CSE_SW_01') ? '#450a0a' : '#0f172a',
          color: isAffected('DEPT_CSE_SW_01') ? '#fca5a5' : '#38bdf8',
          border: `2px solid ${isAffected('DEPT_CSE_SW_01') ? '#ef4444' : '#0284c7'}`,
          borderRadius: '8px',
          fontSize: '11px',
          padding: '10px',
        },
      },
      {
        id: 'AP_HOSTEL_BLOCK_A',
        position: { x: 30, y: 270 },
        data: { label: 'Hostel Blk A AP (Wi-Fi)' },
        style: {
          background: isAffected('AP_HOSTEL_BLOCK_A') ? '#450a0a' : '#0f172a',
          color: isAffected('AP_HOSTEL_BLOCK_A') ? '#fca5a5' : '#cbd5e1',
          border: `2px solid ${isAffected('AP_HOSTEL_BLOCK_A') ? '#ef4444' : '#475569'}`,
          borderRadius: '8px',
          fontSize: '11px',
          padding: '10px',
        },
      },
      {
        id: 'AP_HOSTEL_BLOCK_B',
        position: { x: 200, y: 270 },
        data: { label: 'Hostel Blk B AP (Wi-Fi)' },
        style: {
          background: isAffected('AP_HOSTEL_BLOCK_B') ? '#450a0a' : '#0f172a',
          color: isAffected('AP_HOSTEL_BLOCK_B') ? '#fca5a5' : '#cbd5e1',
          border: `2px solid ${isAffected('AP_HOSTEL_BLOCK_B') ? '#ef4444' : '#475569'}`,
          borderRadius: '8px',
          fontSize: '11px',
          padding: '10px',
        },
      },
    ],
    [affectedDevices],
  );

  const edges: Edge[] = useMemo(
    () => [
      {
        id: 'e1',
        source: 'CAMPUS_CORE_RTR_01',
        target: 'HOSTEL_CORE_SW_01',
        animated: isAffected('HOSTEL_CORE_SW_01'),
        style: {
          stroke: isAffected('HOSTEL_CORE_SW_01') ? '#ef4444' : '#0284c7',
          strokeWidth: 2,
        },
      },
      {
        id: 'e2',
        source: 'CAMPUS_CORE_RTR_01',
        target: 'DEPT_CSE_SW_01',
        animated: isAffected('DEPT_CSE_SW_01'),
        style: {
          stroke: isAffected('DEPT_CSE_SW_01') ? '#ef4444' : '#0284c7',
          strokeWidth: 2,
        },
      },
      {
        id: 'e3',
        source: 'CAMPUS_CORE_RTR_01',
        target: 'DNS_SRV_CAMPUS',
        animated: isAffected('DNS_SRV_CAMPUS'),
        style: {
          stroke: isAffected('DNS_SRV_CAMPUS') ? '#ef4444' : '#475569',
          strokeWidth: 2,
        },
      },
      {
        id: 'e4',
        source: 'HOSTEL_CORE_SW_01',
        target: 'AP_HOSTEL_BLOCK_A',
        animated: isAffected('AP_HOSTEL_BLOCK_A'),
        style: {
          stroke: isAffected('AP_HOSTEL_BLOCK_A') ? '#ef4444' : '#475569',
          strokeWidth: 2,
        },
      },
      {
        id: 'e5',
        source: 'HOSTEL_CORE_SW_01',
        target: 'AP_HOSTEL_BLOCK_B',
        animated: isAffected('AP_HOSTEL_BLOCK_B'),
        style: {
          stroke: isAffected('AP_HOSTEL_BLOCK_B') ? '#ef4444' : '#475569',
          strokeWidth: 2,
        },
      },
    ],
    [affectedDevices],
  );

  return (
    <div className='h-80 w-full rounded-xl bg-[#090d18] border border-slate-800 overflow-hidden relative'>
      <div className='absolute top-3 left-3 z-10 bg-slate-900/80 px-2.5 py-1 rounded border border-slate-700 text-[10px] text-slate-400'>
        IIT Bhubaneswar Layer 2/3 Campus Topology
      </div>
      <ReactFlow nodes={nodes} edges={edges} fitView>
        <Background color='#1e293b' gap={16} />
        <Controls />
      </ReactFlow>
    </div>
  );
};
