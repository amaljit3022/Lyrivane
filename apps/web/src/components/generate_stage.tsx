'use client';

import React, { useState } from 'react';
import { Film, Download, CheckCircle2, FolderOpen, AlertCircle } from 'lucide-react';

interface GenerateStageProps {
  projectId: string;
  selectedRenderer: string;
  selectedTemplate: string;
  aspectRatio?: '16:9' | '9:16' | '1:1';
}

export const GenerateStage: React.FC<GenerateStageProps> = ({
  projectId,
  selectedRenderer,
  selectedTemplate,
  aspectRatio = '16:9',
}) => {
  const [resolution, setResolution] = useState('1080p');
  const [fps, setFps] = useState('30');
  const [codec, setCodec] = useState('h264');
  const [isRendering, setIsRendering] = useState(false);
  const [progress, setProgress] = useState(0);
  const [stageMessage, setStageMessage] = useState('Preparing render...');
  const [isComplete, setIsComplete] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string>(
    `http://localhost:8005/api/v1/projects/${projectId || 'demo'}/renders/download`
  );
  const [outputFolderMsg, setOutputFolderMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const startRender = async () => {
    setIsRendering(true);
    setProgress(0);
    setStageMessage('Submitting render job...');
    setIsComplete(false);
    setOutputFolderMsg(null);
    setErrorMsg(null);

    const targetProjectId = projectId || 'demo';

    try {
      const response = await fetch(`http://localhost:8005/api/v1/projects/${targetProjectId}/render`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          renderer: selectedRenderer,
          template_id: selectedTemplate,
          resolution,
          fps: parseInt(fps),
          codec,
          aspect_ratio: aspectRatio,
          motion_intensity: 0.6
        })
      });

      if (response.ok) {
        const data = await response.json();
        setDownloadUrl(`http://localhost:8005${data.download_url}`);
        if (!data.job_id || !data.progress_url) {
          throw new Error('Render service returned no job status endpoint');
        }

        let completed = false;
        while (!completed) {
          await new Promise((resolve) => setTimeout(resolve, 800));
          const statusResponse = await fetch(`http://localhost:8005${data.progress_url}`);
          if (!statusResponse.ok) {
            throw new Error(`Unable to read render progress (${statusResponse.status})`);
          }
          const status = await statusResponse.json();
          setProgress(Math.max(0, status.progress_percentage ?? 0));
          setStageMessage(status.stage_message || 'Rendering video...');

          if (status.status === 'completed') {
            completed = true;
          } else if (status.status === 'failed') {
            throw new Error(status.stage_message || 'Video generation failed');
          }
        }
        setProgress(100);
        setIsRendering(false);
        setIsComplete(true);
      } else {
        const message = await response.text();
        throw new Error(message || `Render failed (${response.status})`);
      }
    } catch (err) {
      console.error('Render API call failed:', err);
      setIsRendering(false);
      setErrorMsg(err instanceof Error ? err.message : 'Video generation failed');
      return;
    }

  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `${projectId || 'lyricflow'}_video.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleOpenFolder = () => {
    const targetProjectId = projectId || 'demo';
    setOutputFolderMsg(`Projects output directory: C:\\Worklab\\amaljit\\Lyrivane\\projects\\${targetProjectId}\\renders\\`);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Generate Final Lyrical Video</h2>
        <p className="text-gray-400 text-sm">Configure output encoding settings and launch high-resolution video rendering.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Quality Config */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Resolution</label>
          <div className="grid grid-cols-3 gap-2">
            {['1080p', '1440p', '4K'].map((res) => (
              <button
                key={res}
                onClick={() => setResolution(res)}
                className={`py-2 rounded-xl text-xs font-semibold border transition-all ${
                  resolution === res
                    ? 'bg-indigo-600 border-indigo-500 text-white'
                    : 'bg-surface border-surfaceBorder text-gray-400 hover:text-white'
                }`}
              >
                {res}
              </button>
            ))}
          </div>
        </div>

        {/* Frame Rate */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Frame Rate</label>
          <div className="grid grid-cols-2 gap-2">
            {['30', '60'].map((f) => (
              <button
                key={f}
                onClick={() => setFps(f)}
                className={`py-2 rounded-xl text-xs font-semibold border transition-all ${
                  fps === f
                    ? 'bg-indigo-600 border-indigo-500 text-white'
                    : 'bg-surface border-surfaceBorder text-gray-400 hover:text-white'
                }`}
              >
                {f} FPS
              </button>
            ))}
          </div>
        </div>

        {/* Codec */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Video Codec</label>
          <div className="grid grid-cols-2 gap-2">
            {['h264', 'h265'].map((c) => (
              <button
                key={c}
                onClick={() => setCodec(c)}
                className={`py-2 rounded-xl text-xs font-semibold border transition-all uppercase ${
                  codec === c
                    ? 'bg-indigo-600 border-indigo-500 text-white'
                    : 'bg-surface border-surfaceBorder text-gray-400 hover:text-white'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Render Action Box */}
      <div className="glass-card p-8 rounded-2xl text-center space-y-6">
        {errorMsg && (
          <div className="p-4 rounded-xl border border-red-500/40 bg-red-500/10 text-sm text-red-300">
            {errorMsg}
          </div>
        )}
        {!isRendering && !isComplete && (
          <div className="space-y-4">
            <p className="text-sm text-gray-300">
              Ready to encode video using <span className="text-indigo-400 font-semibold uppercase">{selectedRenderer}</span> with template <span className="text-violet-400 font-semibold">{selectedTemplate}</span>.
            </p>
            <button
              onClick={startRender}
              className="inline-flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold px-10 py-4 rounded-xl shadow-xl shadow-emerald-600/20 transition-all text-base cursor-pointer"
            >
              <Film className="w-5 h-5" />
              <span>Start Video Generation</span>
            </button>
          </div>
        )}

        {isRendering && (
          <div className="space-y-4 max-w-md mx-auto">
            <div className="flex justify-between text-xs font-semibold text-gray-300">
              <span>Rendering Video ({selectedRenderer})...</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full h-3 bg-surfaceBorder rounded-full overflow-hidden p-0.5">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className="text-xs text-gray-400 animate-pulse">{stageMessage}</p>
          </div>
        )}

        {isComplete && (
          <div className="space-y-6">
            <div className="flex flex-col items-center gap-2">
              <div className="w-12 h-12 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                <CheckCircle2 className="w-7 h-7" />
              </div>
              <h3 className="text-xl font-bold text-white">Video Render Complete!</h3>
              <p className="text-xs text-gray-400">Output saved to project storage in original master audio fidelity.</p>
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={handleDownload}
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-6 py-3 rounded-xl shadow-lg transition-all text-sm cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>Download Video MP4</span>
              </button>
              <button
                onClick={handleOpenFolder}
                className="flex items-center gap-2 bg-surface hover:bg-surfaceBorder border border-surfaceBorder text-gray-200 font-semibold px-6 py-3 rounded-xl transition-all text-sm cursor-pointer"
              >
                <FolderOpen className="w-4 h-4" />
                <span>Open Output Folder</span>
              </button>
            </div>

            {outputFolderMsg && (
              <div className="p-3 bg-surfaceBorder/50 rounded-xl text-xs font-mono text-emerald-400 flex items-center justify-center gap-2 border border-emerald-500/30 max-w-lg mx-auto">
                <FolderOpen className="w-4 h-4" />
                <span>{outputFolderMsg}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
