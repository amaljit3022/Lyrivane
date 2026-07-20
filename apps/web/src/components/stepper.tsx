'use client';

import React from 'react';
import { Music, Video, LayoutTemplate, PlayCircle, Film, Settings2 } from 'lucide-react';

export interface StageStep {
  id: number;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const STAGES: StageStep[] = [
  { id: 1, name: '1. Audio & Lyrics', icon: Music },
  { id: 2, name: '2. Renderer', icon: Video },
  { id: 3, name: '3. Template', icon: LayoutTemplate },
  { id: 4, name: '4. Preview', icon: PlayCircle },
  { id: 5, name: '5. Generate', icon: Film },
];

interface StepperProps {
  currentStage: number;
  onSelectStage: (stageId: number) => void;
  onToggleAdvanced: () => void;
  isAdvancedOpen: boolean;
}

export const StepperNavigation: React.FC<StepperProps> = ({
  currentStage,
  onSelectStage,
  onToggleAdvanced,
  isAdvancedOpen,
}) => {
  return (
    <header className="w-full border-b border-surfaceBorder bg-surface/80 backdrop-blur-md sticky top-0 z-40 px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand Identity */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-accent to-neonPurple flex items-center justify-center font-bold text-white shadow-lg shadow-accent/20">
            LF
          </div>
          <div>
            <h1 className="font-bold text-lg text-white leading-tight tracking-tight">LyricFlow Studio</h1>
            <p className="text-xs text-gray-400">Let every word move with the music</p>
          </div>
        </div>

        {/* Primary 5-Stage Stepper */}
        <nav className="flex items-center gap-1 sm:gap-2 bg-background/60 p-1.5 rounded-2xl border border-surfaceBorder">
          {STAGES.map((stage) => {
            const Icon = stage.icon;
            const isActive = currentStage === stage.id;
            const isCompleted = currentStage > stage.id;

            return (
              <button
                key={stage.id}
                onClick={() => onSelectStage(stage.id)}
                className={`flex items-center gap-2 px-3 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/20'
                    : isCompleted
                    ? 'text-indigo-400 hover:bg-surfaceBorder/40'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-surfaceBorder/30'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-gray-400'}`} />
                <span className="hidden md:inline">{stage.name}</span>
                <span className="md:hidden">{stage.id}</span>
              </button>
            );
          })}
        </nav>

        {/* Optional Advanced Action Menu */}
        <div className="relative">
          <button
            onClick={onToggleAdvanced}
            className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold border transition-all ${
              isAdvancedOpen
                ? 'bg-accent/20 border-accent text-accentGlow'
                : 'border-surfaceBorder text-gray-400 hover:text-white hover:border-gray-600'
            }`}
          >
            <Settings2 className="w-4 h-4" />
            <span>Advanced</span>
          </button>
        </div>
      </div>
    </header>
  );
};
