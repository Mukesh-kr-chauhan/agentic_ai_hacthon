import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';
import { HypothesisRank } from '../types';
import { ShieldCheck, AlertTriangle, Layers } from 'lucide-react';

interface Props {
  hypotheses: HypothesisRank[];
  conflictDetected?: boolean;
}

export const EvidenceComparison: React.FC<Props> = ({
  hypotheses,
  conflictDetected,
}) => {
  if (!hypotheses || hypotheses.length === 0) return null;

  return (
    <div className='p-5 rounded-xl bg-[#0f172a] border border-slate-800 space-y-4'>
      <div className='flex items-center justify-between'>
        <div>
          <h3 className='text-xs font-semibold uppercase tracking-wider text-slate-400'>
            Multi-Agent Hypothesis Confidence Ranking
          </h3>
          <p className='text-[11px] text-slate-500'>
            Computed by deterministic evidence weights corroborated by Gemini AI
          </p>
        </div>
        {conflictDetected && (
          <div className='flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-950/70 border border-amber-800 text-amber-300 text-xs font-medium'>
            <AlertTriangle className='w-3.5 h-3.5 shrink-0' />
            Contradictory Telemetry Detected
          </div>
        )}
      </div>

      <div className='h-44'>
        <ResponsiveContainer width='100%' height='100%'>
          <BarChart
            data={hypotheses}
            layout='vertical'
            margin={{ left: 80, right: 30, top: 10, bottom: 10 }}
          >
            <XAxis
              type='number'
              domain={[0, 100]}
              unit='%'
              stroke='#64748b'
              fontSize={10}
            />
            <YAxis
              type='category'
              dataKey='hypothesis'
              stroke='#cbd5e1'
              fontSize={11}
              width={160}
              tickFormatter={(val) =>
                val.length > 24 ? `${val.substring(0, 24)}...` : val
              }
            />
            <Tooltip
              formatter={(val: any) => [`${val}%`, 'Confidence Score']}
              contentStyle={{
                backgroundColor: '#0f172a',
                borderColor: '#334155',
                borderRadius: '6px',
                fontSize: '11px',
              }}
            />
            <Bar dataKey='confidence' radius={[0, 4, 4, 0]}>
              {hypotheses.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.type === 'Primary' ? '#38bdf8' : '#64748b'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
