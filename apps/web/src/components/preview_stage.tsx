'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, Sparkles, ArrowRight, Volume2, Loader2, Wand2, Layers, Music } from 'lucide-react';

interface PreviewStageProps {
  projectId: string;
  selectedRenderer: string;
  selectedTemplate: string;
  aspectRatio?: '16:9' | '9:16' | '1:1';
  onNext: () => void;
}

interface LyricLine {
  id: string;
  display_text: string;
  start_ms: number;
  end_ms: number;
  words?: Array<{ text: string; start_ms: number; end_ms: number }>;
}

type PreviewTheme = {
  name: string;
  background: string;
  panel: string;
  accent: string;
  text: string;
  fontFamily: string;
  kind: 'aurora' | 'glass' | 'solar' | 'neon' | 'paper' | 'signal' | 'editorial' | 'cinematic' | 'wind';
};

const PREVIEW_THEMES: Record<string, PreviewTheme> = {
  'aurora-pulse': { name: 'Aurora Pulse', background: 'radial-gradient(circle at 50% 42%, rgba(87, 228, 255, .32), transparent 36%), linear-gradient(140deg, #090b1a, #05060d)', panel: 'rgba(13, 18, 45, .42)', accent: '#8cf6ff', text: '#f8fbff', fontFamily: 'Inter, system-ui, sans-serif', kind: 'aurora' },
  'glass-halo': { name: 'Glass Halo', background: 'radial-gradient(circle at 50% 42%, rgba(164, 143, 255, .32), transparent 38%), linear-gradient(140deg, #080b18, #05060d)', panel: 'rgba(22, 26, 57, .62)', accent: '#b8a7ff', text: '#f8fbff', fontFamily: 'Inter, system-ui, sans-serif', kind: 'glass' },
  'solar-flare': { name: 'Solar Flare', background: 'radial-gradient(circle at 50% 45%, rgba(255, 155, 67, .34), transparent 35%), linear-gradient(140deg, #140b0a, #080506)', panel: 'rgba(49, 20, 12, .46)', accent: '#ffe28a', text: '#fff7e6', fontFamily: 'Inter, system-ui, sans-serif', kind: 'solar' },
  'neon-orbit': { name: 'Neon Orbit', background: 'radial-gradient(circle at 50% 50%, rgba(52, 219, 255, .3), transparent 30%), linear-gradient(135deg, #070716, #160726 70%, #03040b)', panel: 'rgba(7, 12, 34, .66)', accent: '#55f6ff', text: '#f4ffff', fontFamily: 'Inter, system-ui, sans-serif', kind: 'neon' },
  'paper-bloom': { name: 'Paper Bloom', background: 'radial-gradient(circle at 20% 18%, rgba(255,255,255,.92), transparent 28%), linear-gradient(135deg, #f4ead8, #e6c9ae)', panel: 'rgba(255, 250, 239, .78)', accent: '#b54836', text: '#2b211d', fontFamily: 'Georgia, serif', kind: 'paper' },
  'signal-noir': { name: 'Signal Noir', background: 'linear-gradient(135deg, #0b0d0d, #171b19 50%, #050606)', panel: 'rgba(9, 12, 12, .86)', accent: '#a4ff42', text: '#f8f8f2', fontFamily: 'ui-monospace, SFMono-Regular, monospace', kind: 'signal' },
  'editorial-motion': { name: 'Editorial Motion', background: 'linear-gradient(135deg, #1c1711, #090909 65%)', panel: 'rgba(20, 18, 16, .68)', accent: '#f2b544', text: '#fffaf0', fontFamily: 'Inter, system-ui, sans-serif', kind: 'editorial' },
  'cinematic-fade': { name: 'Cinematic Fade', background: 'radial-gradient(circle at center, #252540, #0a0a12 75%)', panel: 'rgba(20, 20, 38, .68)', accent: '#d9c2ff', text: '#f4efff', fontFamily: 'Georgia, serif', kind: 'cinematic' },
  'whispering-wind': { name: 'Whispering Wind', background: 'linear-gradient(135deg, #0b132b, #1c2541 50%, #3a506b)', panel: 'rgba(18, 35, 62, .5)', accent: '#8de7e0', text: '#edf2f4', fontFamily: 'Quicksand, system-ui, sans-serif', kind: 'wind' },
};

export const PreviewStage: React.FC<PreviewStageProps> = ({
  projectId,
  selectedRenderer,
  selectedTemplate,
  aspectRatio = '16:9',
  onNext,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTimeMs, setCurrentTimeMs] = useState(0);
  const [durationMs, setDurationMs] = useState(30000);
  const [lyrics, setLyrics] = useState<LyricLine[]>([]);
  const [visualPlan, setVisualPlan] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const fetchProjectAndPlan = async () => {
      const targetId = projectId || 'demo';
      try {
        const [projRes, planRes] = await Promise.all([
          fetch(`http://localhost:8005/api/v1/projects/${targetId}`),
          fetch(`http://localhost:8005/api/v1/projects/${targetId}/visual-plan?style=${selectedTemplate}&aspect_ratio=${aspectRatio}`)
        ]);

        if (projRes.ok) {
          const data = await projRes.json();
          const linesData = data.lines || data.canonical_timeline?.lines || [];
          if (linesData.length > 0) {
            setLyrics(linesData.map((l: any) => ({
              id: l.id,
              display_text: l.display_text,
              start_ms: l.start_ms,
              end_ms: l.end_ms,
              words: (l.words || []).map((w: any) => ({
                text: w.text ?? w.display_text ?? '',
                start_ms: w.start_ms,
                end_ms: w.end_ms,
              }))
            })));
          }
          const projectDuration = data.audio_meta?.duration_ms || data.canonical_timeline?.audio?.duration_ms;
          if (projectDuration) setDurationMs(projectDuration);
        }

        if (planRes.ok) {
          const planData = await planRes.json();
          setVisualPlan(planData);
        }
      } catch (err) {
        console.warn('Failed to fetch project data for preview', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProjectAndPlan();
  }, [projectId, selectedTemplate, aspectRatio]);

  useEffect(() => {
    let animationFrameId: number;
    
    const updateTime = () => {
      if (audioRef.current) {
        setCurrentTimeMs(audioRef.current.currentTime * 1000);
      }
      animationFrameId = requestAnimationFrame(updateTime);
    };

    if (isPlaying) {
      audioRef.current?.play().catch(e => console.warn('Audio play failed', e));
      animationFrameId = requestAnimationFrame(updateTime);
    } else {
      audioRef.current?.pause();
    }

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [isPlaying]);

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTimeMs = Number(e.target.value);
    setCurrentTimeMs(newTimeMs);
    if (audioRef.current) {
      audioRef.current.currentTime = newTimeMs / 1000;
    }
  };

  const activeLine = lyrics.find(
    (l) => currentTimeMs >= l.start_ms && currentTimeMs <= l.end_ms
  );
  const nextLine = lyrics.find(l => l.start_ms > currentTimeMs);
  const theme = PREVIEW_THEMES[selectedTemplate] || PREVIEW_THEMES['aurora-pulse'];

  const formatTime = (ms: number) => {
    const totalSecs = Math.floor(ms / 1000);
    const mins = Math.floor(totalSecs / 60);
    const secs = totalSecs % 60;
    const msFract = Math.floor((ms % 1000) / 10);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${msFract.toString().padStart(2, '0')}`;
  };

  // Determine aspect ratio frame style
  let containerAspectClass = "aspect-video";
  if (aspectRatio === "9:16") {
    containerAspectClass = "aspect-[9/16] max-w-sm mx-auto";
  } else if (aspectRatio === "1:1") {
    containerAspectClass = "aspect-square max-w-lg mx-auto";
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fadeIn">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Live Studio & Storyboard Preview</h2>
        <p className="text-gray-400 text-sm">Real-time dynamic composition preview & section-aware visual storyboard.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Left 2 Cols: Player Canvas */}
        <div className="lg:col-span-2 space-y-4">
          <div className={`glass-card rounded-2xl overflow-hidden border border-surfaceBorder shadow-2xl ${containerAspectClass}`}>
            {isLoading ? (
              <div className="h-full bg-gradient-to-tr from-slate-950 via-indigo-950 to-slate-900 flex flex-col items-center justify-center p-8">
                <Loader2 className="w-8 h-8 text-indigo-400 animate-spin mb-4" />
                <p className="text-gray-300">Loading Preview Canvas...</p>
              </div>
            ) : (
              <div className="h-full flex flex-col items-center justify-center p-8 relative min-h-[360px] overflow-hidden" style={{ background: theme.background, color: theme.text }}>
                <audio 
                  ref={audioRef} 
                  src={`http://localhost:8005/api/v1/projects/${projectId || 'demo'}/audio`} 
                  onEnded={() => setIsPlaying(false)}
                />
                
                {theme.kind === 'neon' && <>
                  <div className="absolute w-[70%] aspect-square rounded-full border opacity-60 animate-spin" style={{ borderColor: `${theme.accent}88`, boxShadow: `0 0 36px ${theme.accent}55`, animationDuration: '18s' }} />
                  <div className="absolute w-[42%] h-[18%] rounded-[50%] border opacity-50 -rotate-12" style={{ borderColor: '#ff4fd888', boxShadow: '0 0 26px #ff4fd844' }} />
                </>}
                {theme.kind === 'signal' && <div className="absolute inset-0 opacity-15" style={{ backgroundImage: `repeating-linear-gradient(0deg, transparent 0 5px, ${theme.accent} 6px, transparent 7px)` }} />}
                {theme.kind === 'paper' && <div className="absolute top-8 right-10 w-28 h-28 rounded-full blur-2xl opacity-30" style={{ background: theme.accent }} />}

                <div className="absolute top-4 left-4 flex items-center gap-2 bg-black/30 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 z-10">
                  <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: theme.accent }} />
                  <span className="text-xs font-mono opacity-80">{theme.name} • {aspectRatio}</span>
                </div>

                {/* Animated Word Display */}
                <div className="text-center space-y-4 max-w-3xl px-4 relative z-10">
                  <div className="rounded-3xl px-8 py-8 border transition-all duration-300" style={{ background: theme.panel, borderColor: `${theme.accent}55`, boxShadow: `0 0 55px ${theme.accent}22`, backdropFilter: theme.kind === 'glass' ? 'blur(16px)' : 'blur(4px)' }}>
                    <div className={`text-3xl sm:text-5xl font-extrabold tracking-tight drop-shadow-2xl transition-all duration-300 ${
                    activeLine ? 'scale-105 opacity-100' : 'opacity-50'
                  }`} style={{ color: theme.text, fontFamily: theme.fontFamily }}>
                      {activeLine?.words?.length ? activeLine.words.map((word, index) => {
                        const activeWord = currentTimeMs >= word.start_ms && currentTimeMs <= word.end_ms;
                        return <span key={`${word.text}-${index}`} className="inline-block mx-1 transition-all duration-200" style={{ color: activeWord ? theme.accent : theme.text, transform: activeWord ? 'translateY(-3px) scale(1.06)' : undefined, textShadow: activeWord ? `0 0 18px ${theme.accent}` : undefined }}>{word.text}</span>;
                      }) : (activeLine?.display_text || (nextLine ? 'Waiting for the next line…' : 'Music Playing…'))}
                    </div>
                  </div>
                  {activeLine?.words && activeLine.words.length > 0 && (
                    <div className="flex flex-wrap justify-center gap-2 pt-2">
                      {activeLine.words.map((w, i) => {
                        const isCurrentWord = currentTimeMs >= w.start_ms && currentTimeMs <= w.end_ms;
                        return (
                          <span
                            key={i}
                            className={`text-xs px-2.5 py-1 rounded-md font-mono transition-all ${
                              isCurrentWord 
                                ? 'bg-amber-500 text-black font-bold scale-110 shadow-lg shadow-amber-500/30' 
                                : 'bg-white/10 text-gray-300'
                            }`}
                          >
                            {w.text}
                          </span>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* Transport Controls */}
                <div className="absolute bottom-4 left-4 right-4 bg-black/70 backdrop-blur-md px-4 py-3 rounded-xl border border-white/10 flex items-center justify-between gap-4">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className="w-10 h-10 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white flex items-center justify-center transition-colors shrink-0"
                  >
                    {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5 ml-0.5" />}
                  </button>

                  <div className="flex-1 flex items-center gap-3">
                    <span className="text-xs font-mono text-gray-400 shrink-0 w-16 text-right">{formatTime(currentTimeMs)}</span>
                    <input
                      type="range"
                      min={0}
                      max={durationMs}
                      value={currentTimeMs}
                      onChange={handleSeek}
                      className="w-full h-1.5 bg-surfaceBorder rounded-lg appearance-none cursor-pointer accent-indigo-500"
                    />
                    <span className="text-xs font-mono text-gray-400 shrink-0 w-16">{formatTime(durationMs)}</span>
                  </div>

                  <Volume2 className="w-5 h-5 text-gray-400 shrink-0" />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right 1 Col: Visual Intelligence & Storyboard Details */}
        <div className="space-y-4">
          <div className="glass-card p-5 rounded-2xl space-y-4">
            <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
              <Wand2 className="w-4 h-4" />
              <span>Visual Intelligence Storyboard</span>
            </div>

            {visualPlan ? (
              <div className="space-y-3 text-xs">
                <div className="flex justify-between items-center bg-surface p-2.5 rounded-lg border border-surfaceBorder">
                  <span className="text-gray-400">Song Mood</span>
                  <span className="font-mono text-emerald-400 capitalize">{visualPlan.mood || 'dramatic'}</span>
                </div>
                <div className="flex justify-between items-center bg-surface p-2.5 rounded-lg border border-surfaceBorder">
                  <span className="text-gray-400">Motion Intensity</span>
                  <span className="font-mono text-amber-400">{Math.round((visualPlan.motion_intensity || 0.5) * 100)}%</span>
                </div>
                <div className="flex justify-between items-center bg-surface p-2.5 rounded-lg border border-surfaceBorder">
                  <span className="text-gray-400">Aspect Ratio</span>
                  <span className="font-mono text-indigo-400">{visualPlan.aspect_ratio || aspectRatio}</span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-gray-500">Auto-generating section storyboard...</p>
            )}
          </div>

          <div className="glass-card p-5 rounded-2xl space-y-3">
            <div className="flex items-center gap-2 text-violet-400 font-semibold text-sm">
              <Layers className="w-4 h-4" />
              <span>Lyrics Timeline ({lyrics.length} lines)</span>
            </div>

            <div className="max-h-60 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
              {lyrics.map((l, idx) => {
                const isActive = currentTimeMs >= l.start_ms && currentTimeMs <= l.end_ms;
                return (
                  <div
                    key={l.id || idx}
                    onClick={() => {
                      setCurrentTimeMs(l.start_ms);
                      if (audioRef.current) audioRef.current.currentTime = l.start_ms / 1000;
                    }}
                    className={`p-2.5 rounded-xl border text-xs cursor-pointer transition-all ${
                      isActive
                        ? 'bg-violet-950/40 border-violet-500 text-white font-semibold shadow-md'
                        : 'bg-surface/50 border-surfaceBorder/50 text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    <div className="flex justify-between items-center mb-1">
                      <span className="font-mono text-[10px] text-indigo-400">{formatTime(l.start_ms)}</span>
                      <span className="text-[10px] text-gray-500 uppercase">{l.words?.length || 0} words</span>
                    </div>
                    <p className="line-clamp-1">{l.display_text}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <button
          onClick={onNext}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold px-8 py-3.5 rounded-xl shadow-lg shadow-indigo-500/25 transition-all text-sm cursor-pointer"
        >
          <Sparkles className="w-4 h-4" />
          <span>Proceed to Video Generation</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
