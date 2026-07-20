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
  const [selectedRenderer, setSelectedRenderer] = useState('karaoke');
  const [selectedTemplate, setSelectedTemplate] = useState('classic-two-line');
  const [isAdvancedOpen, setIsAdvancedOpen] = useState(false);

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
            onNext={() => setCurrentStage(2)}
          />
        )}

        {currentStage === 2 && (
          <RendererStage
            selectedRenderer={selectedRenderer}
            onSelectRenderer={(renId) => {
              setSelectedRenderer(renId);
              // Set default template for renderer
              if (renId === 'karaoke') setSelectedTemplate('classic-two-line');
              if (renId === 'remotion') setSelectedTemplate('cinematic-minimal');
              if (renId === 'blender') setSelectedTemplate('rainy-window');
            }}
            onNext={() => setCurrentStage(3)}
          />
        )}

        {currentStage === 3 && (
          <TemplateStage
            selectedRenderer={selectedRenderer}
            selectedTemplate={selectedTemplate}
            onSelectTemplate={(tplId) => setSelectedTemplate(tplId)}
            onNext={() => setCurrentStage(4)}
          />
        )}

        {currentStage === 4 && (
          <PreviewStage
            selectedRenderer={selectedRenderer}
            selectedTemplate={selectedTemplate}
            onNext={() => setCurrentStage(5)}
          />
        )}

        {currentStage === 5 && (
          <GenerateStage
            selectedRenderer={selectedRenderer}
            selectedTemplate={selectedTemplate}
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
