'use client';

import React, { useState } from 'react';
import { Play, Pause, RotateCcw, Sparkles, ArrowRight, Volume2 } from 'lucide-react';

interface PreviewStageProps {
  selectedRenderer: string;
  selectedTemplate: string;
  onNext: () => void;
}

export const PreviewStage: React.FC<PreviewStageProps> = ({
  selectedRenderer,
  selectedTemplate,
  onNext,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTimeMs, setCurrentTimeMs] = useState(12420);

  const sampleLyrics = [
    { start: 12420, end: 16850, text: 'I remember when we were young' },
    { start: 17200, end: 21500, text: 'Walking under golden stars' },
    { start: 22000, end: 27000, text: 'Let every word move with the music' },
  ];

  const activeLine = sampleLyrics.find(
    (l) => currentTimeMs >= l.start && currentTimeMs <= l.end
  ) || sampleLyrics[0];

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Interactive Preview</h2>
        <p className="text-gray-400 text-sm">Instant real-time preview of your synchronized lyrics template. No full rendering required.</p>
      </div>

      {/* Video Preview Canvas Box */}
      <div className="glass-card rounded-2xl overflow-hidden border border-surfaceBorder shadow-2xl">
        <div className="aspect-video bg-gradient-to-tr from-slate-950 via-indigo-950 to-slate-900 flex flex-col items-center justify-center p-8 relative">
          {/* Virtual Canvas Title */}
          <div className="absolute top-4 left-4 flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-mono text-gray-300 capitalize">{selectedRenderer} • {selectedTemplate}</span>
          </div>

          {/* Dynamic Lyrical Overlay Preview */}
          <div className="text-center space-y-4 max-w-2xl">
            <p className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight drop-shadow-lg transition-all duration-300">
              {activeLine.text}
            </p>
            <p className="text-sm text-indigo-300 font-medium tracking-wide animate-pulse">
              [Synchronized Line Highlight]
            </p>
          </div>

          {/* Virtual Controls Overlay */}
          <div className="absolute bottom-4 left-4 right-4 bg-black/60 backdrop-blur-md px-4 py-3 rounded-xl border border-white/10 flex items-center justify-between gap-4">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="w-10 h-10 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center transition-colors"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
            </button>

            <div className="flex-1 flex items-center gap-3">
              <span className="text-xs font-mono text-gray-400">00:12.42</span>
              <input
                type="range"
                min={10000}
                max={30000}
                value={currentTimeMs}
                onChange={(e) => setCurrentTimeMs(Number(e.target.value))}
                className="w-full h-1.5 bg-surfaceBorder rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
              <span className="text-xs font-mono text-gray-400">03:00.00</span>
            </div>

            <Volume2 className="w-5 h-5 text-gray-400" />
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <button
          onClick={onNext}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold px-8 py-3.5 rounded-xl shadow-lg shadow-indigo-500/25 transition-all text-sm"
        >
          <Sparkles className="w-4 h-4" />
          <span>Proceed to Video Generation</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
