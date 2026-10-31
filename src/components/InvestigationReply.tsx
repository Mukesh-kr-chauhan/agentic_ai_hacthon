import React, { useState } from 'react';
import { Play, Pause, RotateCcw, StepForward, Activity } from 'lucide-react';

export interface TurnRecord {
  turn_id: int;
  timestamp: string;
  active_agent: string;
  action_type: string;
  rationale: string;
}

interface InvestigationReplayProps {
  history: TurnRecord[];
  onStepChange?: (currentStep: TurnRecord) => void;
}

export const InvestigationReplay: React.FC<InvestigationReplayProps> = ({
  history,
  onStepChange,
}) => {
  const [currentIdx, setCurrentIdx] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  const handleStep = (index: number) => {
    if (index >= 0 && index < history.length) {
      setCurrentIdx(index);
      onStepChange?.(history[index]);
    }
  };

  const handleReset = () => {
    setCurrentIdx(0);
    setIsPlaying(false);
    if (history.length > 0) {
      onStepChange?.(history[0]);
    }
  };

  React.useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isPlaying && currentIdx < history.length - 1) {
      timer = setTimeout(() => {
        handleStep(currentIdx + 1);
      }, 1400);
    } else if (currentIdx >= history.length - 1) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, currentIdx, history.length]);

  if (!history || history.length === 0) {
    return (
      <div className='p-4 bg-slate-900 border border-slate-800 rounded-xl text-slate-400 text-sm'>
        No investigation turns recorded yet.
      </div>
    );
  }

  const activeTurn = history[currentIdx];

  return (
    <div className='bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg'>
      <div className='flex items-center justify-between pb-3 border-b border-slate-800'>
        <div className='flex items-center space-x-2'>
          <Activity className='w-5 h-5 text-cyan-400' />
          <h2 className='text-base font-semibold text-slate-100'>
            Investigation Replay Engine
          </h2>
        </div>
        <div className='flex items-center space-x-1.5 bg-slate-950 px-2 py-1 rounded-lg border border-slate-800'>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className='p-1.5 hover:bg-slate-800 text-slate-200 rounded transition'
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? (
              <Pause className='w-4 h-4 text-amber-400' />
            ) : (
              <Play className='w-4 h-4 text-emerald-400' />
            )}
          </button>
          <button
            onClick={() => handleStep(currentIdx + 1)}
            disabled={currentIdx >= history.length - 1}
            className='p-1.5 hover:bg-slate-800 text-slate-200 rounded disabled:opacity-40 transition'
            title='Step Forward'
          >
            <StepForward className='w-4 h-4' />
          </button>
          <button
            onClick={handleReset}
            className='p-1.5 hover:bg-slate-800 text-slate-200 rounded transition'
            title='Reset'
          >
            <RotateCcw className='w-4 h-4 text-slate-400' />
          </button>
        </div>
      </div>

      {/* Stepper Timeline Bar */}
      <div className='flex items-center space-x-1 mt-4 mb-4'>
        {history.map((turn, i) => (
          <button
            key={turn.turn_id}
            onClick={() => handleStep(i)}
            className={`h-2 flex-1 rounded transition-all ${
              i === currentIdx
                ? 'bg-cyan-500 ring-2 ring-cyan-400/50'
                : i < currentIdx
                  ? 'bg-indigo-600'
                  : 'bg-slate-800'
            }`}
          />
        ))}
      </div>

      {/* Turn Inspector Display */}
      {activeTurn && (
        <div className='p-3.5 bg-slate-950/70 border border-slate-800/80 rounded-lg'>
          <div className='flex justify-between items-center text-xs mb-2'>
            <span className='font-mono text-cyan-400 font-semibold'>
              TURN #{activeTurn.turn_id} • {activeTurn.active_agent}
            </span>
            <span className='text-[10px] px-2 py-0.5 bg-slate-800 text-slate-300 rounded font-mono'>
              {activeTurn.action_type}
            </span>
          </div>
          <p className='text-xs text-slate-300 leading-relaxed font-sans'>
            {activeTurn.rationale}
          </p>
        </div>
      )}
    </div>
  );
};
