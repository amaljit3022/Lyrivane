'use client';

import React, { useState } from 'react';
import { Upload, Music, FileText, Sparkles, ArrowRight, Loader2 } from 'lucide-react';

interface Stage1Props {
  onNext: (data: { audioFile: File | null; lyricsText: string; title: string; artist: string }) => void;
  isSyncing?: boolean;
}

export const AudioLyricsStage: React.FC<Stage1Props> = ({ onNext, isSyncing = false }) => {
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [lyricsText, setLyricsText] = useState<string>(
    '[Verse 1]\nI remember when we were young\nWalking under golden stars\n\n[Chorus]\nLet every word move with the music\nFeel the energy tonight'
  );
  const [title, setTitle] = useState('Golden Stars');
  const [artist, setArtist] = useState('Krittika');

  const handleAudioUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setAudioFile(file);
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
      setTitle(nameWithoutExt);
    }
  };

  const handleLyricsFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        if (event.target?.result) {
          setLyricsText(event.target.result as string);
        }
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fadeIn">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-extrabold text-white tracking-tight">Audio & Lyrics Input</h2>
        <p className="text-gray-400 text-sm">Upload your audio/video file and paste your song lyrics below.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Audio / Video Upload Box */}
        <div className="glass-card p-6 rounded-2xl flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <Music className="w-5 h-5 text-indigo-400" />
              <h3 className="font-semibold text-white">1. Audio / Video Track</h3>
            </div>
            <label className="border-2 border-dashed border-surfaceBorder hover:border-indigo-500/50 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-all bg-surface/40 hover:bg-surface/80 group">
              <Upload className="w-8 h-8 text-gray-400 group-hover:text-indigo-400 mb-2 transition-colors" />
              <span className="text-sm font-medium text-gray-200">
                {audioFile ? audioFile.name : 'Upload MP3, WAV, FLAC, M4A, MP4, MKV'}
              </span>
              <span className="text-xs text-gray-500 mt-1">Drag & drop or click to browse</span>
              <input
                type="file"
                accept="audio/*,video/mp4,video/mkv,video/webm,.mp3,.wav,.flac,.m4a,.aac,.ogg,.opus,.mp4,.mkv,.webm"
                onChange={handleAudioUpload}
                className="hidden"
              />
            </label>
          </div>

          <div className="space-y-3 pt-2">
            <div>
              <label className="text-xs font-semibold text-gray-400">Song Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full mt-1 bg-surface border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
            <div>
              <label className="text-xs font-semibold text-gray-400">Artist Name</label>
              <input
                type="text"
                value={artist}
                onChange={(e) => setArtist(e.target.value)}
                className="w-full mt-1 bg-surface border border-surfaceBorder rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>
        </div>

        {/* Lyrics Input Box */}
        <div className="glass-card p-6 rounded-2xl flex flex-col justify-between space-y-4">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <FileText className="w-5 h-5 text-violet-400" />
                <h3 className="font-semibold text-white">2. Paste Song Lyrics</h3>
              </div>
              <label className="text-xs text-indigo-400 hover:underline cursor-pointer">
                Import File
                <input type="file" accept=".txt,.lrc" onChange={handleLyricsFileUpload} className="hidden" />
              </label>
            </div>
            <textarea
              rows={10}
              value={lyricsText}
              onChange={(e) => setLyricsText(e.target.value)}
              placeholder="Paste matching lyrics here..."
              className="w-full bg-surface border border-surfaceBorder rounded-xl p-3 text-sm text-gray-200 focus:outline-none focus:border-violet-500 font-mono resize-none"
            />
          </div>
        </div>
      </div>

      {/* Action CTA */}
      <div className="flex justify-end pt-4">
        <button
          disabled={isSyncing}
          onClick={() => onNext({ audioFile, lyricsText, title, artist })}
          className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 via-violet-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-semibold px-8 py-3.5 rounded-xl shadow-lg shadow-indigo-500/25 transition-all text-sm disabled:opacity-50 cursor-pointer"
        >
          {isSyncing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Synchronizing Audio & Lyrics...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Synchronize & Continue</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};
