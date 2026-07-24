'use client';

import React from 'react';
import { Zap, Sparkles, Check, ArrowRight } from 'lucide-react';

export interface RendererOption {
  id: string;
  name: string;
  badge: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  features: string[];
}

export const RENDERERS: RendererOption[] = [
  {
    id: 'karaoke',
    name: 'Fast Karaoke Engine',
    badge: 'Fast & Low Resource',
    description: 'High-speed ASS subtitle generation muxed with original audio via FFmpeg.',
    icon: Zap,
    features: ['Line & word highlighting', '2 verified templates', 'Fast CPU render', 'Original audio preserved']
  },
  {
    id: 'remotion',
    name: 'Creative Remotion Engine',
    badge: 'Modern Typography',
    description: 'React & WebGL based kinetic typography with fluid word-level animations.',
    icon: Sparkles,
    features: ['Animated word emphasis', 'Beat-aware visual plans', '16:9, 9:16, 1:1 layouts', 'Central and cinematic templates']
  }
];

interface RendererStageProps {
  selectedRenderer: string;
  onSelectRenderer: (rendererId: string) => void;
  onNext: () => void;
}

export const RendererStage: React.FC<RendererStageProps> = ({
  selectedRenderer,
  onSelectRenderer,
  onNext,
}) => {
  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Select Rendering Engine</h2>
        <p className="text-gray-400 text-sm">All engines utilize your cached synchronized timeline. Changing renderers never re-triggers alignment.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
        {RENDERERS.map((ren) => {
          const Icon = ren.icon;
          const isSelected = selectedRenderer === ren.id;

          return (
            <div
              key={ren.id}
              onClick={() => onSelectRenderer(ren.id)}
              className={`glass-card p-6 rounded-2xl flex flex-col justify-between cursor-pointer border-2 transition-all hover:scale-[1.02] ${
                isSelected
                  ? 'border-indigo-500 bg-indigo-950/20 shadow-xl shadow-indigo-500/10 ring-2 ring-indigo-500/30'
                  : 'border-surfaceBorder hover:border-gray-600'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-3 rounded-xl ${isSelected ? 'bg-indigo-600 text-white' : 'bg-surface text-gray-400'}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  {isSelected && (
                    <div className="w-6 h-6 rounded-full bg-indigo-500 flex items-center justify-center text-white">
                      <Check className="w-4 h-4" />
                    </div>
                  )}
                </div>

                <span className="inline-block text-[11px] font-bold uppercase tracking-wider text-indigo-400 mb-1">
                  {ren.badge}
                </span>
                <h3 className="text-lg font-bold text-white mb-2">{ren.name}</h3>
                <p className="text-xs text-gray-400 leading-relaxed mb-4">{ren.description}</p>

                <ul className="space-y-2 text-xs text-gray-300">
                  {ren.features.map((feat, idx) => (
                    <li key={idx} className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-400" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          );
        })}
      </div>

      <div className="flex justify-end pt-4">
        <button
          onClick={onNext}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold px-8 py-3.5 rounded-xl shadow-lg shadow-indigo-500/25 transition-all text-sm"
        >
          <span>Continue to Templates</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
