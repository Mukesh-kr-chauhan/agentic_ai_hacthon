import React from 'react';
import { TimelineEvent } from '../types';
import { CheckCircle2, Clock, CircleDot, ArrowRight } from 'lucide-react';

interface Props {
  timeline: TimelineEvent[];
}

export const IncidentTimeline: React.FC<Props> = ({ timeline }) => {
  if (!timeline || timeline.length === 0) return null;

  return (
    <div className='p-5 rounded-xl bg-[#0f172a] border border-slate-800 space-y-4'>
      <h3 className='text-xs font-semibold uppercase tracking-wider text-slate-400'>
        Incident Diagnostic Lifecycle Timeline
      </h3>
      <div className='relative border-l border-slate-800 ml-3 space-y-4'>
        {timeline.map((step, idx) => {
          const isDone = step.status === 'completed';
          return (
            <div key={idx} className='relative pl-6'>
              <span className='absolute -left-2 top-0.5'>
                {isDone ? (
                  <CheckCircle2 className='w-4 h-4 text-emerald-400 bg-slate-950 rounded-full' />
                ) : (
                  <CircleDot className='w-4 h-4 text-slate-600 bg-slate-950 rounded-full' />
                )}
              </span>
              <div className='flex items-center justify-between text-xs'>
                <span
                  className={`font-medium ${isDone ? 'text-slate-200' : 'text-slate-500'}`}
                >
                  {step.stage}
                </span>
                <span className='font-mono text-[11px] text-slate-500'>
                  {step.timestamp
                    ? new Date(step.timestamp).toLocaleTimeString()
                    : 'Awaiting'}
                </span>
              </div>
              <div className='flex items-center gap-2 mt-0.5 text-[11px] font-mono text-cyan-400/80'>
                <span>{step.agent}</span>
                {step.message_id && (
                  <span className='text-slate-500'>
                    • Msg ID: {step.message_id}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
