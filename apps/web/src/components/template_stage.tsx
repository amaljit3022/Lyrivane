'use client';

import React, { useState } from 'react';
import { LayoutTemplate, Check, ArrowRight, Smartphone, Monitor, Square } from 'lucide-react';

interface TemplateItem {
  id: string;
  name: string;
  renderer: string;
  description: string;
  gradient: string;
}

const TEMPLATES_BY_RENDERER: Record<string, TemplateItem[]> = {
  karaoke: [
    { id: 'classic-two-line', name: 'Classic Two-Line', renderer: 'karaoke', description: 'Traditional karaoke text layout with bottom line highlighting.', gradient: 'from-blue-900 to-indigo-900' },
    { id: 'minimal-dark', name: 'Minimal Dark', renderer: 'karaoke', description: 'Sleek dark background with vibrant active word glows.', gradient: 'from-gray-900 to-black' },
    { id: 'album-art-bg', name: 'Album Art Focus', renderer: 'karaoke', description: 'Blurred album cover background with subtle lyric overlays.', gradient: 'from-purple-900 to-slate-900' },
  ],
  remotion: [
    { id: 'cinematic-minimal', name: 'Cinematic Minimal', renderer: 'remotion', description: 'Fluid typography transitions with smooth camera pans.', gradient: 'from-violet-900 to-slate-950' },
    { id: 'neon-pulse', name: 'Neon Pulse', renderer: 'remotion', description: 'Glow typography synced to peak audio energy frequencies.', gradient: 'from-fuchsia-900 to-cyan-950' },
    { id: 'typewriter', name: 'Floating Typewriter', renderer: 'remotion', description: 'Tactile word-by-word reveal with vintage grain.', gradient: 'from-amber-950 to-neutral-900' },
  ],
  blender: [
    { id: 'rainy-window', name: 'Rainy Window 3D', renderer: 'blender', description: 'Glass refraction with glowing neon lyrics behind rainfall.', gradient: 'from-cyan-950 to-slate-950' },
    { id: 'misty-forest', name: 'Misty Forest 3D', renderer: 'blender', description: 'Volumetric atmosphere with floating metallic text.', gradient: 'from-emerald-950 to-stone-950' },
    { id: 'galaxy-space', name: 'Galaxy Cosmic 3D', renderer: 'blender', description: 'Deep space particle fields with glowing celestial titles.', gradient: 'from-indigo-950 to-purple-950' },
  ],
};

interface TemplateStageProps {
  selectedRenderer: string;
  selectedTemplate: string;
  onSelectTemplate: (templateId: string) => void;
  onNext: () => void;
}

export const TemplateStage: React.FC<TemplateStageProps> = ({
  selectedRenderer,
  selectedTemplate,
  onSelectTemplate,
  onNext,
}) => {
  const templates = TEMPLATES_BY_RENDERER[selectedRenderer] || TEMPLATES_BY_RENDERER['karaoke'];
  const [aspectRatio, setAspectRatio] = useState<'16:9' | '9:16' | '1:1'>('16:9');

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Choose Template & Aspect Ratio</h2>
        <p className="text-gray-400 text-sm">Select a visual template configured for the <span className="text-indigo-400 font-semibold uppercase">{selectedRenderer}</span> engine.</p>
      </div>

      {/* Aspect Ratio Selector */}
      <div className="flex justify-center gap-3">
        {[
          { id: '16:9', label: '16:9 Landscape', icon: Monitor },
          { id: '9:16', label: '9:16 Vertical', icon: Smartphone },
          { id: '1:1', label: '1:1 Square', icon: Square },
        ].map((ar) => {
          const Icon = ar.icon;
          const isSelected = aspectRatio === ar.id;
          return (
            <button
              key={ar.id}
              onClick={() => setAspectRatio(ar.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold border transition-all ${
                isSelected
                  ? 'bg-indigo-600 border-indigo-500 text-white shadow-md shadow-indigo-500/20'
                  : 'glass-card border-surfaceBorder text-gray-400 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{ar.label}</span>
            </button>
          );
        })}
      </div>

      {/* Template Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {templates.map((tpl) => {
          const isSelected = selectedTemplate === tpl.id;
          return (
            <div
              key={tpl.id}
              onClick={() => onSelectTemplate(tpl.id)}
              className={`glass-card p-5 rounded-2xl cursor-pointer border-2 transition-all hover:scale-[1.02] flex flex-col justify-between ${
                isSelected
                  ? 'border-violet-500 bg-violet-950/20 ring-2 ring-violet-500/30'
                  : 'border-surfaceBorder hover:border-gray-600'
              }`}
            >
              <div>
                <div className={`w-full h-32 rounded-xl bg-gradient-to-tr ${tpl.gradient} flex items-center justify-center p-4 mb-4 relative overflow-hidden shadow-inner`}>
                  <span className="text-xs font-bold font-mono tracking-widest text-white/90 uppercase drop-shadow-md">
                    LYRICS PREVIEW
                  </span>
                  {isSelected && (
                    <div className="absolute top-2 right-2 w-6 h-6 rounded-full bg-violet-500 flex items-center justify-center text-white">
                      <Check className="w-4 h-4" />
                    </div>
                  )}
                </div>
                <h3 className="font-bold text-white text-base mb-1">{tpl.name}</h3>
                <p className="text-xs text-gray-400 leading-relaxed">{tpl.description}</p>
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
          <span>Continue to Preview</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
