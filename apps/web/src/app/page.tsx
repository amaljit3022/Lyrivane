'use client';

import React, { useState } from 'react';
import { StepperNavigation } from '@/components/stepper';
import { AudioLyricsStage } from '@/components/audio_lyrics_stage';
import { RendererStage } from '@/components/renderer_stage';
import { TemplateStage } from '@/components/template_stage';
import { PreviewStage } from '@/components/preview_stage';
import { GenerateStage } from '@/components/generate_stage';
import { AdvancedEditorDrawer } from '@/components/advanced_editor_drawer';

export default function HomePage() {
  const [currentStage, setCurrentStage] = useState(1);
  const [selectedRenderer, setSelectedRenderer] = useState('remotion');
  const [selectedTemplate, setSelectedTemplate] = useState('editorial-motion');
  const [aspectRatio, setAspectRatio] = useState<'16:9' | '9:16' | '1:1'>('16:9');
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);
  const [projectId, setProjectId] = useState<string>('demo');
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState('');

  const handleStage1Submit = async (data: { audioFile: File | null; lyricsText: string; title: string; artist: string }) => {
    setIsSyncing(true);

    try {
      // Step A: Create Project
      const createRes = await fetch('http://localhost:8005/api/v1/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: data.title || 'Untitled Song',
          artist: data.artist || 'Unknown Artist',
          language: 'en'
        })
      });

      let activeId = 'demo';
      if (createRes.ok) {
        const createData = await createRes.json();
        activeId = createData.project_id;
        setProjectId(activeId);
      }

      // Step B: Upload Audio File if provided
      if (data.audioFile) {
        const formData = new FormData();
        formData.append('file', data.audioFile);
        await fetch(`http://localhost:8005/api/v1/projects/${activeId}/audio`, {
          method: 'POST',
          body: formData
        });
      }

      // Step C: Upload Pasted Lyrics
      const lyricsFormData = new FormData();
      lyricsFormData.append('raw_text', data.lyricsText);
      await fetch(`http://localhost:8005/api/v1/projects/${activeId}/lyrics`, {
        method: 'POST',
        body: lyricsFormData
      });

      // Step D: Trigger Automated Synchronization
      await fetch(`http://localhost:8005/api/v1/projects/${activeId}/synchronize`, {
        method: 'POST'
      });

      // Step E: Poll for synchronization completion
      let isDone = false;
      while (!isDone) {
        await new Promise(r => setTimeout(r, 2000));
        const statusRes = await fetch(`http://localhost:8005/api/v1/projects/${activeId}`);
        if (statusRes.ok) {
          const statusData = await statusRes.json();
          if (statusData.sync_progress?.message) {
            setSyncMessage(`${statusData.sync_progress.message} (${statusData.sync_progress.percent}%)`);
          }
          if (statusData.status === 'synchronized' || statusData.status === 'error') {
            isDone = true;
          }
        }
      }

    } catch (err) {
      console.warn('Sync connection fallback:', err);
    } finally {
      setIsSyncing(false);
      setCurrentStage(2);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-background text-gray-100 font-sans">
      {/* 5-Stage Primary Stepper Header */}
      <StepperNavigation
        currentStage={currentStage}
        onSelectStage={(stageId) => setCurrentStage(stageId)}
        onToggleAdvanced={() => setIsAdvancedOpen(!isAdvancedOpen)}
        isAdvancedOpen={isAdvancedOpen}
      />

      {/* Main Stage Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-10">
        {currentStage === 1 && (
          <AudioLyricsStage
            onNext={handleStage1Submit}
            isSyncing={isSyncing}
            syncMessage={syncMessage}
          />
        )}

        {currentStage === 2 && (
          <RendererStage
            selectedRenderer={selectedRenderer}
            onSelectRenderer={(renId) => {
              setSelectedRenderer(renId);
              if (renId === 'karaoke') setSelectedTemplate('classic-two-line');
              if (renId === 'remotion') setSelectedTemplate('editorial-motion');
              if (renId === 'blender') setSelectedTemplate('rainy-window');
            }}
            onNext={() => setCurrentStage(3)}
          />
        )}

        {currentStage === 3 && (
          <TemplateStage
            selectedRenderer={selectedRenderer}
            selectedTemplate={selectedTemplate}
            aspectRatio={aspectRatio}
            onSelectTemplate={(tplId) => setSelectedTemplate(tplId)}
            onSelectAspectRatio={(ratio) => setAspectRatio(ratio)}
            onNext={() => setCurrentStage(4)}
          />
        )}

        {currentStage === 4 && (
          <PreviewStage
            projectId={projectId}
            selectedRenderer={selectedRenderer}
            selectedTemplate={selectedTemplate}
            aspectRatio={aspectRatio}
            onNext={() => setCurrentStage(5)}
          />
        )}

        {currentStage === 5 && (
          <GenerateStage
            projectId={projectId}
            selectedRenderer={selectedRenderer}
            selectedTemplate={selectedTemplate}
            aspectRatio={aspectRatio}
          />
        )}
      </main>

      {/* Optional Advanced Timing Editor Drawer */}
      <AdvancedEditorDrawer
        isOpen={isAdvancedOpen}
        onClose={() => setIsAdvancedOpen(false)}
      />

      {/* Footer */}
      <footer className="border-t border-surfaceBorder py-6 px-8 text-center text-xs text-gray-500">
        LyricFlow Studio (Lyrivane) &bull; A Krittika Labs Project &bull; Local-first Open Source Lyrical Video Engine
      </footer>
    </div>
  );
}
