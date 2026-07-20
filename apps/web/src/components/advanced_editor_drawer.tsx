'use client';

import React, { useState } from 'react';
import { X, Lock, RotateCcw, Save, Sliders, Check } from 'lucide-react';

interface AdvancedEditorDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AdvancedEditorDrawer: React.FC<AdvancedEditorDrawerProps> = ({
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  const [lines, setLines] = useState([
    { id: 'l1', start_ms: 12420, end_ms: 16850, text: 'I remember when we were young', verified: true },
    { id: 'l2', start_ms: 17200, end_ms: 21500, text: 'Walking under golden stars', verified: false },
    { id: 'l3', start_ms: 22000, end_ms: 27000, text: 'Let every word move with the music', verified: false },
  ]);

  const toggleVerify = (id: string) => {
    setLines((prev) =>
      prev.map((l) => (l.id === id ? { ...l, verified: !l.verified } : l))
    );
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex justify-end animate-fadeIn">
      <div className="w-full max-w-2xl bg-surface border-l border-surfaceBorder h-full flex flex-col justify-between shadow-2xl p-6 overflow-y-auto">
        <div className="space-y-6">
          <div className="flex items-center justify-between border-b border-surfaceBorder pb-4">
            <div className="flex items-center gap-2">
              <Sliders className="w-5 h-5 text-indigo-400" />
              <h2 className="text-xl font-bold text-white">Advanced Lyrics & Timing Editor</h2>
            </div>
            <button onClick={onClose} className="p-2 rounded-xl text-gray-400 hover:text-white hover:bg-surfaceBorder">
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-4 bg-indigo-950/20 border border-indigo-500/20 rounded-xl text-xs text-indigo-300">
            <strong>Optional Fallback Mode:</strong> Manual timing changes are locked and preserved across all renderers and templates.
          </div>

          {/* Waveform Visualization Mock */}
          <div className="bg-background border border-surfaceBorder rounded-xl p-4 text-center space-y-2">
            <span className="text-xs font-mono text-gray-400">Waveform Navigation Timeline</span>
            <div className="h-16 bg-surface flex items-center justify-center rounded-lg border border-surfaceBorder">
              <span className="text-xs text-gray-500 font-mono">[ Interactive Audio Waveform Track ]</span>
            </div>
          </div>

          {/* Lines Table */}
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold text-white">Line Timings</h3>
              <button
                onClick={() => setLines((prev) => prev.map((l) => ({ ...l, verified: false })))}
                className="text-xs text-gray-400 hover:text-rose-400 flex items-center gap-1"
              >
                <RotateCcw className="w-3 h-3" />
                Reset to Automatic
              </button>
            </div>

            <div className="space-y-2">
              {lines.map((l) => (
                <div key={l.id} className="glass-card p-3 rounded-xl flex items-center justify-between gap-4">
                  <div className="flex-1 space-y-1">
                    <input
                      type="text"
                      value={l.text}
                      onChange={(e) => {
                        const val = e.target.value;
                        setLines((prev) => prev.map((item) => (item.id === l.id ? { ...item, text: val, verified: true } : item)));
                      }}
                      className="w-full bg-transparent border-none text-sm font-medium text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 rounded px-1"
                    />
                    <div className="flex items-center gap-3 text-xs font-mono text-gray-400">
                      <span>Start: {l.start_ms}ms</span>
                      <span>End: {l.end_ms}ms</span>
                    </div>
                  </div>

                  <button
                    onClick={() => toggleVerify(l.id)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                      l.verified
                        ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-400'
                        : 'border-surfaceBorder text-gray-400 hover:text-white'
                    }`}
                  >
                    {l.verified ? <Lock className="w-3 h-3 text-emerald-400" /> : <Check className="w-3 h-3" />}
                    <span>{l.verified ? 'Verified' : 'Auto'}</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-surfaceBorder flex justify-end gap-3">
          <button onClick={onClose} className="px-5 py-2.5 rounded-xl border border-surfaceBorder text-xs text-gray-300 hover:bg-surfaceBorder">
            Cancel
          </button>
          <button onClick={onClose} className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white shadow-lg">
            <Save className="w-4 h-4" />
            <span>Save Corrections</span>
          </button>
        </div>
      </div>
    </div>
  );
};
