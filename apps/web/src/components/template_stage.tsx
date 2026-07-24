'use client';

import React, { useState, useEffect } from 'react';
import { Check, ArrowRight, Smartphone, Monitor, Square, Sparkles } from 'lucide-react';

interface TemplateItem {
  id: string;
  name: string;
  renderer: string;
  description: string;
  gradient?: string;
  supported_aspect_ratios?: string[];
  preview_gradient?: string;
}

const DEFAULT_TEMPLATES: TemplateItem[] = [
  { id: 'editorial-motion', name: 'Editorial Motion', renderer: 'remotion', description: 'Magazine kinetic typography with spring physics, uppercase emphasis, and dark editorial backgrounds.', gradient: 'from-amber-900 to-stone-950' },
  { id: 'cinematic-fade', name: 'Cinematic Fade', renderer: 'remotion', description: 'Emotional serif typography with radial dark ambient gradients, camera zoom, and blur transitions.', gradient: 'from-violet-950 to-slate-950' },
  { id: 'whispering-wind', name: 'Whispering Wind', renderer: 'remotion', description: 'Floating wave motion, horizontal drift, particle dispersion, and serene visual cyan tones.', gradient: 'from-cyan-950 to-blue-950' },
  { id: 'aurora-pulse', name: 'Aurora Pulse', renderer: 'remotion', description: 'Central lyric stage with glowing word emphasis and soft aurora motion.', gradient: 'from-cyan-900 to-violet-950' },
  { id: 'glass-halo', name: 'Glass Halo', renderer: 'remotion', description: 'Centered lyrics inside a calm translucent glass frame.', gradient: 'from-violet-900 to-slate-950' },
  { id: 'solar-flare', name: 'Solar Flare', renderer: 'remotion', description: 'Warm central lyrics with a restrained cinematic flare.', gradient: 'from-orange-900 to-rose-950' },
];

const KARAOKE_TEMPLATES: TemplateItem[] = [
  { id: 'classic-two-line', name: 'Central Aurora', renderer: 'karaoke', description: 'Centered lyrics with active-word highlighting and a dark contrast panel.', gradient: 'from-cyan-900 to-violet-950' },
  { id: 'minimal-dark', name: 'Minimal Dark', renderer: 'karaoke', description: 'Clean centered lyrics with restrained contrast and word highlighting.', gradient: 'from-slate-900 to-black' },
];

interface TemplateStageProps {
  selectedRenderer: string;
  selectedTemplate: string;
  aspectRatio: '16:9' | '9:16' | '1:1';
  onSelectTemplate: (templateId: string) => void;
  onSelectAspectRatio: (ratio: '16:9' | '9:16' | '1:1') => void;
  onNext: () => void;
}

export const TemplateStage: React.FC<TemplateStageProps> = ({
  selectedRenderer,
  selectedTemplate,
  aspectRatio,
  onSelectTemplate,
  onSelectAspectRatio,
  onNext,
}) => {
  const [templates, setTemplates] = useState<TemplateItem[]>(selectedRenderer === 'karaoke' ? KARAOKE_TEMPLATES : DEFAULT_TEMPLATES);

  useEffect(() => {
    const fetchTemplates = async () => {
      setTemplates(selectedRenderer === 'karaoke' ? KARAOKE_TEMPLATES : DEFAULT_TEMPLATES);
      try {
        const res = await fetch(`http://localhost:8005/api/v1/templates?renderer=${selectedRenderer}`);
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            setTemplates(data.map((t: any, i: number) => ({
              id: t.id,
              name: t.name,
              renderer: t.renderer || selectedRenderer,
              description: t.description || 'Custom kinetic typography template.',
              gradient: t.preview_gradient || DEFAULT_TEMPLATES[i % DEFAULT_TEMPLATES.length].gradient,
              supported_aspect_ratios: t.supported_aspect_ratios || ['16:9', '9:16', '1:1']
            })));
          }
        }
      } catch (err) {
        console.warn('API templates fallback:', err);
      }
    };
    fetchTemplates();
  }, [selectedRenderer]);

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
          { id: '9:16', label: '9:16 Vertical (Shorts/TikTok)', icon: Smartphone },
          { id: '1:1', label: '1:1 Square (Instagram)', icon: Square },
        ].map((ar) => {
          const Icon = ar.icon;
          const isSelected = aspectRatio === ar.id;
          return (
            <button
              key={ar.id}
              onClick={() => onSelectAspectRatio(ar.id as any)}
              className={`flex items-center gap-2 px-5 py-3 rounded-xl text-xs font-semibold border transition-all ${
                isSelected
                  ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-500/25 scale-105'
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
                <div className={`w-full h-32 rounded-xl bg-gradient-to-tr ${tpl.gradient || 'from-indigo-950 to-slate-900'} flex items-center justify-center p-4 mb-4 relative overflow-hidden shadow-inner`}>
                  <div className="flex items-center gap-1.5 text-xs font-bold font-mono tracking-widest text-white/90 uppercase drop-shadow-md">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                    <span>{tpl.name}</span>
                  </div>
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
          <span>Continue to Live Preview</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
