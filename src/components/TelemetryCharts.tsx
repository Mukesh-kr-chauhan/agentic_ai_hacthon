import React, { useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
  Legend,
} from 'recharts';
import { TelemetryPoint } from '../types';
import { Activity, Cpu, AlertOctagon, Wifi, Clock, Server } from 'lucide-react';

interface Props {
  data: TelemetryPoint[];
  loading: boolean;
  deviceId: string;
}

export const TelemetryCharts: React.FC<Props> = ({
  data,
  loading,
  deviceId,
}) => {
  const [selectedDevice, setSelectedDevice] = useState<string>('ALL');

  if (loading) {
    return (
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className='h-64 bg-slate-900/60 rounded-xl border border-slate-800 animate-pulse flex items-center justify-center'
          >
            <span className='text-xs text-slate-500 font-mono'>
              Aggregating Telemetry Stream...
            </span>
          </div>
        ))}
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className='p-12 text-center border border-dashed border-slate-800 rounded-xl bg-slate-950/40'>
        <Activity className='w-8 h-8 text-slate-600 mx-auto mb-2' />
        <p className='text-sm text-slate-400'>
          No telemetry recorded for this incident yet.
        </p>
      </div>
    );
  }

  const customTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className='bg-[#0f172a] border border-slate-700 p-2.5 rounded shadow-xl text-xs font-mono'>
          <p className='text-slate-400 mb-1'>T-Stamp: {label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: <span className='font-bold'>{entry.value}</span>{' '}
              {entry.unit || ''}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className='space-y-4'>
      {/* Filters Header */}
      <div className='flex items-center justify-between bg-slate-900/70 p-3 rounded-lg border border-slate-800 text-xs'>
        <div className='flex items-center gap-2'>
          <Server className='w-4 h-4 text-cyan-400' />
          <span className='text-slate-300 font-semibold'>
            Active Device Filter:
          </span>
          <span className='font-mono text-cyan-300 px-2 py-0.5 rounded bg-slate-800 border border-slate-700'>
            {deviceId || 'CAMPUS_SW_CORE'}
          </span>
        </div>
        <div className='flex items-center gap-4 text-slate-400'>
          <span className='flex items-center gap-1.5'>
            <span className='w-2 h-2 rounded-full bg-red-500' /> Critical
            Warning Limit
          </span>
          <span className='flex items-center gap-1.5'>
            <Clock className='w-3.5 h-3.5' /> Sample Window: 60s
          </span>
        </div>
      </div>

      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
        {/* Chart 1: Latency */}
        <div className='p-4 rounded-xl bg-[#0d1322] border border-slate-800'>
          <div className='flex items-center justify-between mb-2'>
            <h4 className='text-xs font-semibold text-slate-200'>
              Path Latency (ms)
            </h4>
            <span className='text-[10px] text-cyan-400 font-mono'>RTT</span>
          </div>
          <div className='h-48'>
            <ResponsiveContainer width='100%' height='100%'>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray='3 3' stroke='#1e293b' />
                <XAxis dataKey='timestamp' stroke='#64748b' fontSize={10} />
                <YAxis stroke='#64748b' fontSize={10} domain={[0, 'auto']} />
                <Tooltip content={customTooltip} />
                <ReferenceLine
                  y={100}
                  stroke='#ef4444'
                  strokeDasharray='4 4'
                  label={{ value: '100ms Limit', fill: '#ef4444', fontSize: 9 }}
                />
                <Line
                  type='monotone'
                  dataKey='latency_ms'
                  name='Latency'
                  unit='ms'
                  stroke='#38bdf8'
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Packet Loss */}
        <div className='p-4 rounded-xl bg-[#0d1322] border border-slate-800'>
          <div className='flex items-center justify-between mb-2'>
            <h4 className='text-xs font-semibold text-slate-200'>
              Packet Discard / Loss (%)
            </h4>
            <span className='text-[10px] text-red-400 font-mono'>Drop %</span>
          </div>
          <div className='h-48'>
            <ResponsiveContainer width='100%' height='100%'>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray='3 3' stroke='#1e293b' />
                <XAxis dataKey='timestamp' stroke='#64748b' fontSize={10} />
                <YAxis stroke='#64748b' fontSize={10} domain={[0, 'auto']} />
                <Tooltip content={customTooltip} />
                <ReferenceLine
                  y={2.0}
                  stroke='#f59e0b'
                  strokeDasharray='3 3'
                  label={{ value: '2% Thresh', fill: '#f59e0b', fontSize: 9 }}
                />
                <Line
                  type='monotone'
                  dataKey='packet_loss_pct'
                  name='Loss'
                  unit='%'
                  stroke='#f43f5e'
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Link Utilization */}
        <div className='p-4 rounded-xl bg-[#0d1322] border border-slate-800'>
          <div className='flex items-center justify-between mb-2'>
            <h4 className='text-xs font-semibold text-slate-200'>
              Link Bandwidth Saturation (%)
            </h4>
            <span className='text-[10px] text-emerald-400 font-mono'>
              Capacity
            </span>
          </div>
          <div className='h-48'>
            <ResponsiveContainer width='100%' height='100%'>
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray='3 3' stroke='#1e293b' />
                <XAxis dataKey='timestamp' stroke='#64748b' fontSize={10} />
                <YAxis stroke='#64748b' fontSize={10} domain={[0, 100]} />
                <Tooltip content={customTooltip} />
                <ReferenceLine
                  y={85}
                  stroke='#ef4444'
                  strokeDasharray='3 3'
                  label={{
                    value: '85% Saturation',
                    fill: '#ef4444',
                    fontSize: 9,
                  }}
                />
                <Area
                  type='monotone'
                  dataKey='link_utilization_pct'
                  name='Util'
                  unit='%'
                  stroke='#10b981'
                  fill='#10b98120'
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Jitter */}
        <div className='p-4 rounded-xl bg-[#0d1322] border border-slate-800'>
          <div className='flex items-center justify-between mb-2'>
            <h4 className='text-xs font-semibold text-slate-200'>
              Jitter Variance (ms)
            </h4>
            <span className='text-[10px] text-amber-400 font-mono'>
              Delay Var
            </span>
          </div>
          <div className='h-48'>
            <ResponsiveContainer width='100%' height='100%'>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray='3 3' stroke='#1e293b' />
                <XAxis dataKey='timestamp' stroke='#64748b' fontSize={10} />
                <YAxis stroke='#64748b' fontSize={10} />
                <Tooltip content={customTooltip} />
                <Line
                  type='monotone'
                  dataKey='jitter_ms'
                  name='Jitter'
                  unit='ms'
                  stroke='#fbbf24'
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 5: CPU and Memory */}
        <div className='p-4 rounded-xl bg-[#0d1322] border border-slate-800'>
          <div className='flex items-center justify-between mb-2'>
            <h4 className='text-xs font-semibold text-slate-200'>
              Control Plane Resources (%)
            </h4>
            <span className='text-[10px] text-indigo-400 font-mono'>
              HW Health
            </span>
          </div>
          <div className='h-48'>
            <ResponsiveContainer width='100%' height='100%'>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray='3 3' stroke='#1e293b' />
                <XAxis dataKey='timestamp' stroke='#64748b' fontSize={10} />
                <YAxis stroke='#64748b' fontSize={10} domain={[0, 100]} />
                <Tooltip content={customTooltip} />
                <Legend iconSize={8} wrapperStyle={{ fontSize: 10 }} />
                <Bar
                  dataKey='cpu_usage_pct'
                  name='CPU'
                  fill='#6366f1'
                  radius={[2, 2, 0, 0]}
                />
                <Bar
                  dataKey='memory_usage_pct'
                  name='Memory'
                  fill='#a855f7'
                  radius={[2, 2, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 6: Queue Drops & Interface Errors */}
        <div className='p-4 rounded-xl bg-[#0d1322] border border-slate-800'>
          <div className='flex items-center justify-between mb-2'>
            <h4 className='text-xs font-semibold text-slate-200'>
              Buffer Drops & Frame Errors
            </h4>
            <span className='text-[10px] text-orange-400 font-mono'>
              Discards
            </span>
          </div>
          <div className='h-48'>
            <ResponsiveContainer width='100%' height='100%'>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray='3 3' stroke='#1e293b' />
                <XAxis dataKey='timestamp' stroke='#64748b' fontSize={10} />
                <YAxis stroke='#64748b' fontSize={10} />
                <Tooltip content={customTooltip} />
                <Legend iconSize={8} wrapperStyle={{ fontSize: 10 }} />
                <Bar
                  dataKey='queue_drops'
                  name='Queue Drops'
                  fill='#f97316'
                  radius={[2, 2, 0, 0]}
                />
                <Bar
                  dataKey='interface_errors'
                  name='CRC Errors'
                  fill='#ef4444'
                  radius={[2, 2, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
