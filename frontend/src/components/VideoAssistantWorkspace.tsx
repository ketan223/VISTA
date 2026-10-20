import React, { useState } from 'react';
import {
  ArrowLeft,
  Upload,
  Sparkles,
  FileText,
  MessageSquare,
  Download,
  Search,
  Copy,
  Check,
  Send,
  Clock,
  AlertCircle,
  FileCode,
  FileDown,
  Volume2,
  ListTodo,
  HelpCircle,
  KeyRound,
  RotateCcw,
  Play,
} from 'lucide-react';
import type { VideoResult, ChatMessage } from '../types';

interface VideoAssistantWorkspaceProps {
  onBackToHub: () => void;
}

export const VideoAssistantWorkspace: React.FC<VideoAssistantWorkspaceProps> = ({
  onBackToHub,
}) => {
  const [inputTab, setInputTab] = useState<'youtube' | 'upload'>('youtube');
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [language, setLanguage] = useState('english');
  const [modelSize, setModelSize] = useState('base');

  const [loading, setLoading] = useState(false);
  const [progressStep, setProgressStep] = useState('');
  const [progressPercent, setProgressPercent] = useState(0);
  const [errorMsg, setErrorMsg] = useState('');

  const [result, setResult] = useState<VideoResult | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'transcript' | 'chat' | 'export'>('overview');

  // Search in transcript
  const [transcriptSearch, setTranscriptSearch] = useState('');
  const [copiedTranscript, setCopiedTranscript] = useState(false);

  // Chat State
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Helper: Format seconds to MM:SS
  const formatSeconds = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = Math.floor(sec % 60);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Run Intelligence Pipeline
  const handleProcess = async () => {
    setErrorMsg('');
    setLoading(true);
    setProgressPercent(15);
    setProgressStep('Acquiring audio stream...');

    try {
      let data: VideoResult;

      if (inputTab === 'youtube') {
        if (!youtubeUrl.trim()) {
          throw new Error('Please provide a valid YouTube link.');
        }

        setProgressPercent(30);
        setProgressStep('Transcribing speech with Faster-Whisper...');

        const response = await fetch('/api/video/process-url', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            url: youtubeUrl.trim(),
            language,
            model_size: modelSize,
          }),
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || 'Failed to process YouTube video.');
        }

        data = await response.json();
      } else {
        if (!selectedFile) {
          throw new Error('Please select an audio or video file to upload.');
        }

        setProgressPercent(25);
        setProgressStep('Uploading and normalizing media to 16kHz WAV...');

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('language', language);
        formData.append('model_size', modelSize);

        const response = await fetch('/api/video/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.detail || 'Failed to process uploaded media.');
        }

        data = await response.json();
      }

      setProgressPercent(100);
      setProgressStep('Complete!');
      setResult(data);
      setChatMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content: `Analysis for "${data.title}" is ready! Ask me anything about the content, specific decisions, or deadlines.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch (err: any) {
      setErrorMsg(err.message || 'An error occurred during video analysis.');
    } finally {
      setLoading(false);
    }
  };

  // Chat Submission
  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!chatInput.trim() || !result || chatLoading) return;

    const userText = chatInput.trim();
    setChatInput('');

    const newMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setChatMessages((prev) => [...prev, newMsg]);
    setChatLoading(true);

    try {
      const response = await fetch('/api/video/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_hash: result.source_hash,
          question: userText,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to retrieve answer from RAG engine.');
      }

      const resData = await response.json();
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: resData.answer,
        citations: resData.citations,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setChatMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setChatMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `Error: ${err.message || 'Unable to query transcript.'}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  // Copy transcript
  const handleCopyTranscript = () => {
    if (!result) return;
    navigator.clipboard.writeText(result.formatted_transcript || result.transcript);
    setCopiedTranscript(true);
    setTimeout(() => setCopiedTranscript(false), 2000);
  };

  return (
    <div className="min-h-full p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Header & Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/[0.08] pb-5">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToHub}
            className="flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-[#14141e] px-3 py-1.5 text-xs font-medium text-zinc-300 hover:text-white hover:border-white/20 transition-all cursor-pointer"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>Back to VISTA</span>
          </button>
          <div className="h-4 w-px bg-white/[0.1]" />
          <div>
            <h1 className="text-xl font-bold text-white flex items-center gap-2">
              <span className="p-1 rounded bg-violet-600/20 text-violet-400">🎬</span>
              AI Video Assistant
            </h1>
            <p className="text-xs text-zinc-400">
              Multilingual Whisper Transcription • Executive Summarization • Grounded LCEL RAG
            </p>
          </div>
        </div>

        {result && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setResult(null);
                setChatMessages([]);
                setYoutubeUrl('');
                setSelectedFile(null);
              }}
              className="flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-[#14141e] px-3 py-1.5 text-xs text-zinc-400 hover:text-white hover:border-white/20 cursor-pointer"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>New Analysis</span>
            </button>
          </div>
        )}
      </div>

      {/* Ingestion Card (Shown when no result yet) */}
      {!result && (
        <div className="rounded-2xl border border-white/[0.08] bg-[#12121a] p-6 space-y-6 shadow-xl">
          <div className="flex items-center justify-between border-b border-white/[0.06] pb-4">
            <div>
              <h2 className="text-base font-semibold text-white">Select Video or Audio Source</h2>
              <p className="text-xs text-zinc-400 mt-0.5">
                Provide a YouTube video URL or upload your local media recording.
              </p>
            </div>

            {/* Input Segment Switcher */}
            <div className="flex rounded-lg border border-white/[0.08] bg-[#0d0d14] p-1">
              <button
                onClick={() => setInputTab('youtube')}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-xs font-medium transition-all cursor-pointer ${
                  inputTab === 'youtube'
                    ? 'bg-violet-600 text-white shadow-sm'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                <Play className="h-3.5 w-3.5" />
                <span>YouTube URL</span>
              </button>
              <button
                onClick={() => setInputTab('upload')}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1 text-xs font-medium transition-all cursor-pointer ${
                  inputTab === 'upload'
                    ? 'bg-violet-600 text-white shadow-sm'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                <Upload className="h-3.5 w-3.5" />
                <span>Upload Media</span>
              </button>
            </div>
          </div>

          {/* Tab 1: YouTube Input */}
          {inputTab === 'youtube' ? (
            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-300">YouTube Video Link</label>
                <div className="relative">
                  <input
                    type="url"
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/..."
                    className="w-full rounded-xl border border-white/[0.08] bg-[#181824] px-4 py-3 text-sm text-white placeholder-zinc-500 outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 font-mono"
                  />
                  {youtubeUrl && (
                    <button
                      onClick={() => setYoutubeUrl('')}
                      className="absolute right-3 top-3 text-xs text-zinc-400 hover:text-white"
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
            </div>
          ) : (
            /* Tab 2: Drag & Drop File Upload */
            <div className="space-y-4">
              <div
                className="relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-white/[0.12] bg-[#161622]/60 p-8 text-center hover:border-violet-500/50 transition-colors"
                onDragOver={(e) => e.preventDefault()}
                onDrop={(e) => {
                  e.preventDefault();
                  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    setSelectedFile(e.dataTransfer.files[0]);
                  }
                }}
              >
                <Upload className="h-8 w-8 text-violet-400 mb-2" />
                <p className="text-sm font-medium text-white mb-1">
                  {selectedFile ? selectedFile.name : 'Drag & drop your recording here, or browse'}
                </p>
                <p className="text-xs text-zinc-500 mb-4 font-mono">
                  {selectedFile
                    ? `${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB`
                    : 'Supported: MP4, MP3, WAV, MKV, MOV, M4A up to 500MB'}
                </p>

                <label className="inline-flex items-center gap-1.5 rounded-lg bg-[#222230] border border-white/[0.08] px-4 py-2 text-xs font-medium text-zinc-300 hover:text-white hover:border-white/20 cursor-pointer">
                  <span>Browse File</span>
                  <input
                    type="file"
                    className="hidden"
                    accept="video/*,audio/*"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setSelectedFile(e.target.files[0]);
                      }
                    }}
                  />
                </label>
              </div>
            </div>
          )}

          {/* Model & Language Controls */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-300">Whisper Model Size</label>
              <select
                value={modelSize}
                onChange={(e) => setModelSize(e.target.value)}
                className="w-full rounded-lg border border-white/[0.08] bg-[#181824] px-3 py-2 text-xs text-zinc-200 outline-none focus:border-violet-500 font-mono"
              >
                <option value="tiny">Tiny (Ultra-fast, lowest memory)</option>
                <option value="base">Base (Recommended default • Fast & accurate)</option>
                <option value="small">Small (Higher precision for accents)</option>
                <option value="medium">Medium (Maximum accuracy for noisy audio)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-300">Audio Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full rounded-lg border border-white/[0.08] bg-[#181824] px-3 py-2 text-xs text-zinc-200 outline-none focus:border-violet-500 font-mono"
              >
                <option value="english">English</option>
                <option value="auto">Auto-detect Language</option>
                <option value="hindi">Hindi</option>
                <option value="hinglish">Hinglish</option>
                <option value="spanish">Spanish</option>
                <option value="french">French</option>
                <option value="german">German</option>
              </select>
            </div>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div className="flex items-center gap-2 rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Primary Action Button */}
          <button
            onClick={handleProcess}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 py-3.5 text-sm font-semibold text-white shadow-lg shadow-violet-600/25 hover:from-violet-500 hover:to-indigo-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {loading ? (
              <>
                <span className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
                <span>{progressStep} ({progressPercent}%)</span>
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                <span>Run Video Intelligence</span>
              </>
            )}
          </button>
        </div>
      )}

      {/* Result Workspace */}
      {result && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Active Session Strip */}
          <div className="rounded-xl border border-white/[0.08] bg-[#12121a] p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="font-mono text-[10px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full font-semibold">
                  Indexed & Synced
                </span>
                <span className="text-xs text-zinc-500 font-mono">ID: {result.source_hash}</span>
              </div>
              <h2 className="text-lg font-bold text-white">{result.title}</h2>
            </div>

            <div className="flex items-center gap-3 text-xs text-zinc-400 font-mono">
              <div className="flex items-center gap-1.5 bg-[#181824] px-2.5 py-1.5 rounded-md border border-white/[0.06]">
                <Clock className="h-3.5 w-3.5 text-violet-400" />
                <span>{formatSeconds(result.duration)}</span>
              </div>
              <div className="flex items-center gap-1.5 bg-[#181824] px-2.5 py-1.5 rounded-md border border-white/[0.06]">
                <Volume2 className="h-3.5 w-3.5 text-indigo-400" />
                <span className="uppercase">{result.language}</span>
              </div>
            </div>
          </div>

          {/* Workspace Tabs */}
          <div className="flex border-b border-white/[0.08] gap-1">
            <button
              onClick={() => setActiveTab('overview')}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors cursor-pointer ${
                activeTab === 'overview'
                  ? 'border-violet-500 text-violet-300'
                  : 'border-transparent text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <FileText className="h-4 w-4" />
              <span>Overview & Insights</span>
            </button>

            <button
              onClick={() => setActiveTab('transcript')}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors cursor-pointer ${
                activeTab === 'transcript'
                  ? 'border-violet-500 text-violet-300'
                  : 'border-transparent text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Clock className="h-4 w-4" />
              <span>Timestamped Transcript</span>
            </button>

            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors cursor-pointer ${
                activeTab === 'chat'
                  ? 'border-violet-500 text-violet-300'
                  : 'border-transparent text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <MessageSquare className="h-4 w-4" />
              <span>AI Chat (RAG)</span>
            </button>

            <button
              onClick={() => setActiveTab('export')}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors cursor-pointer ${
                activeTab === 'export'
                  ? 'border-violet-500 text-violet-300'
                  : 'border-transparent text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Download className="h-4 w-4" />
              <span>Export Suite</span>
            </button>
          </div>

          {/* TAB 1: Overview & Insights */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Executive Summary */}
                <div className="lg:col-span-2 rounded-xl border border-white/[0.08] bg-[#12121a] p-6 space-y-3">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2 text-violet-400">
                    <FileText className="h-4 w-4" />
                    Executive Summary
                  </h3>
                  <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line bg-[#161622] p-4 rounded-lg border border-white/[0.04]">
                    {result.summary}
                  </div>
                </div>

                {/* Key Decisions */}
                <div className="rounded-xl border border-white/[0.08] bg-[#12121a] p-6 space-y-3">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2 text-indigo-400">
                    <KeyRound className="h-4 w-4" />
                    Key Decisions
                  </h3>
                  <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line bg-[#161622] p-4 rounded-lg border border-white/[0.04]">
                    {result.key_decisions}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Action Items */}
                <div className="rounded-xl border border-white/[0.08] bg-[#12121a] p-6 space-y-3">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2 text-emerald-400">
                    <ListTodo className="h-4 w-4" />
                    Action Items & Deliverables
                  </h3>
                  <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line bg-[#161622] p-4 rounded-lg border border-white/[0.04]">
                    {result.action_items}
                  </div>
                </div>

                {/* Open Questions */}
                <div className="rounded-xl border border-white/[0.08] bg-[#12121a] p-6 space-y-3">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono flex items-center gap-2 text-amber-400">
                    <HelpCircle className="h-4 w-4" />
                    Open Questions & Follow-ups
                  </h3>
                  <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line bg-[#161622] p-4 rounded-lg border border-white/[0.04]">
                    {result.open_questions}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Timestamped Transcript */}
          {activeTab === 'transcript' && (
            <div className="rounded-xl border border-white/[0.08] bg-[#12121a] p-6 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div className="relative flex-1 max-w-md">
                  <Search className="absolute left-3 top-2.5 h-4 w-4 text-zinc-500" />
                  <input
                    type="text"
                    value={transcriptSearch}
                    onChange={(e) => setTranscriptSearch(e.target.value)}
                    placeholder="Search keywords in transcript..."
                    className="w-full rounded-lg border border-white/[0.08] bg-[#181824] pl-9 pr-3 py-2 text-xs text-white placeholder-zinc-500 outline-none focus:border-violet-500"
                  />
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={handleCopyTranscript}
                    className="flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-[#161622] px-3 py-2 text-xs text-zinc-300 hover:text-white hover:border-white/20 transition-all cursor-pointer"
                  >
                    {copiedTranscript ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
                    <span>{copiedTranscript ? 'Copied' : 'Copy All'}</span>
                  </button>
                  <a
                    href={`/api/video/export/markdown/${result.source_hash}`}
                    download
                    className="flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-[#161622] px-3 py-2 text-xs text-zinc-300 hover:text-white hover:border-white/20 transition-all"
                  >
                    <Download className="h-3.5 w-3.5" />
                    <span>Download TXT</span>
                  </a>
                </div>
              </div>

              {/* Segment List */}
              <div className="max-h-[500px] overflow-y-auto space-y-2 pr-1">
                {result.segments && result.segments.length > 0 ? (
                  result.segments
                    .filter((seg) =>
                      transcriptSearch
                        ? seg.text.toLowerCase().includes(transcriptSearch.toLowerCase())
                        : true
                    )
                    .map((seg, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-3 rounded-lg border border-white/[0.04] bg-[#161622] p-3 hover:border-white/[0.09] transition-colors"
                      >
                        <span className="font-mono text-xs text-violet-400 bg-violet-500/10 border border-violet-500/20 px-2 py-0.5 rounded shrink-0">
                          {seg.time_tag || `[${formatSeconds(seg.start)} - ${formatSeconds(seg.end)}]`}
                        </span>
                        <p className="text-sm text-zinc-300 leading-relaxed">{seg.text}</p>
                      </div>
                    ))
                ) : (
                  <div className="whitespace-pre-line text-sm text-zinc-300 font-mono bg-[#161622] p-4 rounded-lg">
                    {result.formatted_transcript || result.transcript}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: AI Chat (RAG) */}
          {activeTab === 'chat' && (
            <div className="rounded-xl border border-white/[0.08] bg-[#12121a] flex flex-col h-[600px] overflow-hidden">
              <div className="border-b border-white/[0.06] p-4 flex items-center justify-between bg-[#151520]">
                <div>
                  <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <MessageSquare className="h-4 w-4 text-violet-400" />
                    Grounded Video Intelligence Chat
                  </h3>
                  <p className="text-[11px] text-zinc-400">
                    Answers are strictly synthesized from retrieved transcript segments with timestamp citations.
                  </p>
                </div>
                {chatMessages.length > 1 && (
                  <button
                    onClick={() => setChatMessages([])}
                    className="text-xs text-zinc-500 hover:text-zinc-300 cursor-pointer"
                  >
                    Clear History
                  </button>
                )}
              </div>

              {/* Chat Messages Scroll */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {chatMessages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex flex-col ${
                      msg.role === 'user' ? 'items-end' : 'items-start'
                    }`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                        msg.role === 'user'
                          ? 'bg-violet-600 text-white rounded-br-none'
                          : 'bg-[#181824] border border-white/[0.08] text-zinc-200 rounded-bl-none'
                      }`}
                    >
                      <div className="whitespace-pre-line">{msg.content}</div>

                      {/* Source Citations with timestamps */}
                      {msg.citations && msg.citations.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-white/[0.08] space-y-1.5">
                          <div className="text-[11px] font-mono text-violet-300 uppercase font-semibold">
                            Timestamp Citations:
                          </div>
                          {msg.citations.map((c, i) => (
                            <div
                              key={i}
                              className="text-xs font-mono bg-white/[0.04] p-2 rounded border border-white/[0.04] text-zinc-300"
                            >
                              <span className="text-violet-400 font-bold mr-1.5">{c.time_tag}</span>
                              <span className="text-zinc-400 text-[11px]">{c.content}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    <span className="text-[10px] text-zinc-500 mt-1 px-1 font-mono">
                      {msg.timestamp}
                    </span>
                  </div>
                ))}

                {chatLoading && (
                  <div className="flex items-center gap-2 text-xs text-zinc-400 bg-[#181824] border border-white/[0.08] p-3 rounded-xl max-w-sm">
                    <span className="animate-spin rounded-full h-3 w-3 border-2 border-violet-400 border-t-transparent" />
                    <span>Searching transcript vectors and formulating answer...</span>
                  </div>
                )}
              </div>

              {/* Input Bar */}
              <form onSubmit={handleSendMessage} className="p-3 border-t border-white/[0.08] bg-[#14141e] flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask a question about the video (e.g. 'What was decided about the budget?')..."
                  className="flex-1 rounded-xl border border-white/[0.08] bg-[#181826] px-4 py-2.5 text-sm text-white placeholder-zinc-500 outline-none focus:border-violet-500"
                />
                <button
                  type="submit"
                  disabled={!chatInput.trim() || chatLoading}
                  className="flex items-center justify-center rounded-xl bg-violet-600 px-4 py-2.5 text-white hover:bg-violet-500 transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
                >
                  <Send className="h-4 w-4" />
                </button>
              </form>
            </div>
          )}

          {/* TAB 4: Export Suite */}
          {activeTab === 'export' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Markdown Export */}
              <div className="rounded-xl border border-white/[0.08] bg-[#12121a] p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-violet-600/15 border border-violet-500/20 text-violet-400">
                    <FileCode className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Markdown Intelligence Report</h3>
                    <p className="text-xs text-zinc-400">
                      Standard `.md` file formatted for Obsidian, Notion, or GitHub documentation.
                    </p>
                  </div>
                </div>

                <a
                  href={`/api/video/export/markdown/${result.source_hash}`}
                  download
                  className="w-full flex items-center justify-center gap-2 rounded-lg bg-[#181824] hover:bg-[#202030] border border-white/[0.08] py-2.5 text-xs font-semibold text-white transition-colors cursor-pointer"
                >
                  <Download className="h-4 w-4 text-violet-400" />
                  <span>Download Markdown (.md)</span>
                </a>
              </div>

              {/* PDF Briefing Export */}
              <div className="rounded-xl border border-white/[0.08] bg-[#12121a] p-6 space-y-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-lg bg-indigo-600/15 border border-indigo-500/20 text-indigo-400">
                    <FileDown className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white">Executive PDF Briefing</h3>
                    <p className="text-xs text-zinc-400">
                      Publication-ready PDF with structured headers, action matrix, and transcript.
                    </p>
                  </div>
                </div>

                <a
                  href={`/api/video/export/pdf/${result.source_hash}`}
                  download
                  className="w-full flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 py-2.5 text-xs font-semibold text-white transition-colors shadow-md shadow-violet-600/20 cursor-pointer"
                >
                  <Download className="h-4 w-4" />
                  <span>Download Executive PDF (.pdf)</span>
                </a>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
