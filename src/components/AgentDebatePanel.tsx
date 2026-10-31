import React from 'react';
import {
  ShieldAlert,
  CheckCircle,
  MessageSquareQuote,
  ArrowRight,
} from 'lucide-react';

export interface HypothesisRecord {
  id: string;
  root_cause: string;
  confidence: number;
  proposed_by: string;
  supporting_evidence: string[];
  counter_evidence: string[];
  status: 'ACTIVE' | 'REVISED' | 'REJECTED' | 'CONFIRMED';
}

interface AgentDebatePanelProps {
  hypotheses: HypothesisRecord[];
  onSelectHypothesis?: (hypothesis: HypothesisRecord) => void;
}

export const AgentDebatePanel: React.FC<AgentDebatePanelProps> = ({
  hypotheses,
  onSelectHypothesis,
}) => {
  return (
    <div className='bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg'>
      <div className='flex items-center justify-between pb-4 border-b border-slate-800 mb-4'>
        <div className='flex items-center space-x-2'>
          <MessageSquareQuote className='w-5 h-5 text-indigo-400' />
          <h2 className='text-lg font-semibold text-slate-100'>
            Agent Multi-Round Debate & Critic
          </h2>
        </div>
        <span className='text-xs px-2.5 py-1 bg-slate-800 text-slate-400 rounded-full border border-slate-700'>
          Cross-Agent Verification
        </span>
      </div>

      <div className='space-y-4'>
        {hypotheses.map((item) => {
          const confidencePct = Math.round(item.confidence * 100);
          const badgeColor =
            item.status === 'CONFIRMED'
              ? 'bg-emerald-950 text-emerald-400 border-emerald-800'
              : item.status === 'REJECTED'
                ? 'bg-rose-950 text-rose-400 border-rose-800'
                : 'bg-amber-950 text-amber-400 border-amber-800';

          return (
            <div
              key={item.id}
              onClick={() => onSelectHypothesis?.(item)}
              className='p-4 bg-slate-950/60 rounded-lg border border-slate-800/80 hover:border-slate-700 transition cursor-pointer'
            >
              <div className='flex items-start justify-between'>
                <div>
                  <div className='flex items-center space-x-2'>
                    <span className='text-xs font-mono text-indigo-400 uppercase tracking-wider'>
                      {item.proposed_by}
                    </span>
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${badgeColor}`}
                    >
                      {item.status}
                    </span>
                  </div>
                  <h3 className='text-sm font-medium text-slate-200 mt-1'>
                    {item.root_cause}
                  </h3>
                </div>
                <div className='text-right'>
                  <div className='text-lg font-bold text-slate-100'>
                    {confidencePct}%
                  </div>
                  <div className='text-[10px] text-slate-400 uppercase tracking-wider'>
                    Confidence
                  </div>
                </div>
              </div>

              {/* Confidence Progress Bar */}
              <div className='w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden'>
                <div
                  className={`h-full transition-all duration-500 ${
                    confidencePct > 70
                      ? 'bg-emerald-500'
                      : confidencePct > 35
                        ? 'bg-amber-500'
                        : 'bg-rose-500'
                  }`}
                  style={{ width: `${confidencePct}%` }}
                />
              </div>

              {/* Critic & Supporting Evidence Lists */}
              <div className='mt-3 grid grid-cols-1 md:grid-cols-2 gap-2 text-xs'>
                {item.supporting_evidence.length > 0 && (
                  <div className='bg-emerald-950/20 border border-emerald-900/40 rounded p-2 text-emerald-300'>
                    <div className='flex items-center space-x-1 font-semibold mb-1'>
                      <CheckCircle className='w-3.5 h-3.5' />
                      <span>Corroboration</span>
                    </div>
                    <ul className='list-disc list-inside space-y-0.5 text-[11px] text-emerald-200/90'>
                      {item.supporting_evidence.map((sup, idx) => (
                        <li key={idx}>{sup}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {item.counter_evidence.length > 0 && (
                  <div className='bg-rose-950/20 border border-rose-900/40 rounded p-2 text-rose-300'>
                    <div className='flex items-center space-x-1 font-semibold mb-1'>
                      <ShieldAlert className='w-3.5 h-3.5' />
                      <span>Critic Challenge</span>
                    </div>
                    <ul className='list-disc list-inside space-y-0.5 text-[11px] text-rose-200/90'>
                      {item.counter_evidence.map((cnt, idx) => (
                        <li key={idx}>{cnt}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
