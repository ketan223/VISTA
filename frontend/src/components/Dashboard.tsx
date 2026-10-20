import React from 'react';
import {
  Video,
  MessageSquare,
  FileText,
  Code2,
  Image as ImageIcon,
  BarChart3,
  Mic,
  Bot,
  ArrowRight,
  CheckCircle2,
  Lock,
  Sparkles,
  Zap,
} from 'lucide-react';
import type { ModuleItem } from '../types';

interface DashboardProps {
  onSelectModule: (moduleId: string) => void;
}

const MODULES_LIST: ModuleItem[] = [
  {
    id: 'video_assistant',
    title: 'AI Video Assistant',
    iconName: 'Video',
    status: 'active',
    statusLabel: 'Ready to Use',
    description:
      'Ingest YouTube streams or uploaded audio/video files. Powered by Faster-Whisper, local Ollama executive insights, and ChromaDB grounded RAG QA.',
    tags: ['Faster-Whisper', 'ChromaDB', 'LCEL RAG', 'PDF Export'],
  },
  {
    id: 'research_agent',
    title: 'Multi-AI Research Agent',
    iconName: 'Bot',
    status: 'active',
    statusLabel: 'Ready to Use',
    description:
      'Autonomous 4-stage research loop: live web search (Tavily & DDGS), deep URL reader scraping, publication report synthesis, and adversarial critic scoring.',
    tags: ['Search Agent', 'Reader Scraper', 'Writer Chain', 'Critic Review'],
  },
  {
    id: 'chat_assistant',
    title: 'AI Chat Assistant',
    iconName: 'MessageSquare',
    status: 'active',
    statusLabel: 'Ready to Use',
    description:
      'Powered by Google Gemini 3.8 Flash with 5 specialized personas (General, Coder, Researcher, Creative, Tutor) and local Ollama resilient fallback.',
    tags: ['Gemini 3.8 Flash', '5 Personas', 'Multi-turn Memory', 'Ollama Fallback'],
  },
  {
    id: 'document_assistant',
    title: 'Document Assistant (PDF RAG)',
    iconName: 'FileText',
    status: 'active',
    statusLabel: 'Ready to Use',
    description:
      'Deep multimodal analysis across PDFs, DOCX, and TXT files with ChromaDB vector retrieval, executive summaries, and grounded page citations.',
    tags: ['PDF / DOCX RAG', 'Page Citations', 'ChromaDB', 'Mistral / Ollama'],
  },
  {
    id: 'code_assistant',
    title: 'Code Assistant',
    iconName: 'Code2',
    status: 'planned',
    statusLabel: 'Coming Soon',
    description:
      'Autonomous software engineering partner for multi-file refactoring, AST analysis, unit test generation, and bug fixing.',
    tags: ['AST Parser', 'Unit Tests', 'Refactoring'],
  },
  {
    id: 'image_assistant',
    title: 'Image Assistant',
    iconName: 'ImageIcon',
    status: 'planned',
    statusLabel: 'Coming Soon',
    description:
      'Vision LLM document OCR, visual question answering, schematic diagram breakdown, and generative asset synthesis.',
    tags: ['Vision LLM', 'OCR', 'Diagrams'],
  },
  {
    id: 'data_analysis',
    title: 'Data Analysis',
    iconName: 'BarChart3',
    status: 'planned',
    statusLabel: 'Coming Soon',
    description:
      'Automated exploratory data analysis, dataset anomaly cleaning, statistical summaries, and dynamic interactive charting.',
    tags: ['Pandas EDA', 'Plotly Charts', 'Auto Insights'],
  },
  {
    id: 'speech_to_text',
    title: 'Speech-to-Text Studio',
    iconName: 'Mic',
    status: 'planned',
    statusLabel: 'Coming Soon',
    description:
      'Real-time live mic streaming and bulk audio batch transcription with speaker diarization and custom vocabulary training.',
    tags: ['Live Streaming', 'Diarization', 'Multi-speaker'],
  },
  {
    id: 'agents_automation',
    title: 'AI Agents & Automation',
    iconName: 'Bot',
    status: 'planned',
    statusLabel: 'Coming Soon',
    description:
      'Autonomous multi-agent orchestration for recurring background research, notification triggers, and autonomous task execution.',
    tags: ['Cron Schedules', 'Multi-Agent', 'Webhooks'],
  },
];

export const Dashboard: React.FC<DashboardProps> = ({ onSelectModule }) => {
  const getIcon = (name: string) => {
    switch (name) {
      case 'Video': return Video;
      case 'MessageSquare': return MessageSquare;
      case 'FileText': return FileText;
      case 'Code2': return Code2;
      case 'ImageIcon': return ImageIcon;
      case 'BarChart3': return BarChart3;
      case 'Mic': return Mic;
      case 'Bot': return Bot;
      default: return Sparkles;
    }
  };

  return (
    <div className="min-h-full p-8 max-w-7xl mx-auto space-y-10">
      {/* Hero Section */}
      <div className="relative text-center py-8">
        <div className="inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-3.5 py-1 text-xs text-violet-300 mb-4 shadow-sm">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="font-semibold tracking-wide uppercase text-[11px]">
            Final Year Engineering Project • VISTA 1.0
          </span>
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white mb-3 bg-gradient-to-r from-white via-zinc-200 to-violet-300 bg-clip-text text-transparent">
          Your Unified AI Workspace
        </h1>
        <p className="max-w-2xl mx-auto text-base text-zinc-400 leading-relaxed">
          Visual & Intelligent System for Task Automation. One integrated interface replacing disconnected AI apps with local, privacy-first models and grounded retrieval.
        </p>
      </div>

      {/* Featured Primary Card: AI Video Assistant */}
      <div className="relative overflow-hidden rounded-2xl border border-violet-500/30 bg-gradient-to-br from-[#161624] via-[#12121c] to-[#0d0d15] p-8 shadow-xl shadow-violet-950/20">
        <div className="absolute top-0 right-0 -mt-10 -mr-10 h-72 w-72 rounded-full bg-violet-600/15 blur-3xl pointer-events-none" />

        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-4 max-w-2xl">
            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 px-3 py-0.5 text-xs font-semibold text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" /> Ready to Use
              </span>
              <span className="font-mono text-xs text-zinc-500">Primary Core Module</span>
            </div>

            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-2.5">
                <Video className="h-6 w-6 text-violet-400" />
                AI Video Assistant
              </h2>
              <p className="text-zinc-300 text-sm mt-1.5 leading-relaxed">
                Transform YouTube videos or local MP4, MP3, WAV recordings into structured intelligence. Features local <strong>Faster-Whisper</strong> timestamped speech-to-text, executive summaries, decision matrices, and grounded RAG Q&A with direct timestamp citations.
              </p>
            </div>

            <div className="flex flex-wrap gap-2 pt-1">
              {['YouTube & File Ingest', 'Segment Timestamps', 'Local Ollama LLM', 'ChromaDB Vector Store', 'PDF & Markdown Export'].map((t) => (
                <span
                  key={t}
                  className="rounded-md border border-white/[0.08] bg-white/[0.04] px-2.5 py-1 text-xs font-mono text-zinc-300"
                >
                  {t}
                </span>
              ))}
            </div>
          </div>

          <div className="shrink-0 flex flex-col sm:flex-row lg:flex-col gap-3">
            <button
              onClick={() => onSelectModule('video_assistant')}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-6 py-3.5 font-semibold text-white shadow-lg shadow-violet-600/30 hover:from-violet-500 hover:to-indigo-500 transition-all hover:scale-[1.02] cursor-pointer"
            >
              <span>Launch Workspace</span>
              <ArrowRight className="h-4 w-4" />
            </button>
            <div className="text-center font-mono text-[11px] text-zinc-500">
              Zero API keys required • 100% Local
            </div>
          </div>
        </div>
      </div>

      {/* Grid of 8 Modules */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
            <Zap className="h-4 w-4 text-violet-400" />
            Workspace Modules
          </h3>
          <span className="font-mono text-xs text-zinc-500">8 Modules Planned • 1 Active</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {MODULES_LIST.map((mod) => {
            const Icon = getIcon(mod.iconName);
            const isActive = mod.status === 'active';

            return (
              <div
                key={mod.id}
                className={`relative flex flex-col justify-between rounded-xl border p-5 transition-all duration-200 ${
                  isActive
                    ? 'border-violet-500/40 bg-[#141420] shadow-md shadow-violet-950/20 hover:border-violet-400 cursor-pointer hover:-translate-y-0.5'
                    : 'border-white/[0.06] bg-[#101017] opacity-80 hover:opacity-100'
                }`}
                onClick={() => {
                  if (isActive) onSelectModule(mod.id);
                }}
              >
                <div>
                  <div className="flex items-center justify-between mb-3.5">
                    <div
                      className={`flex h-10 w-10 items-center justify-center rounded-lg border ${
                        isActive
                          ? 'border-violet-500/30 bg-violet-500/15 text-violet-300'
                          : 'border-white/[0.06] bg-white/[0.03] text-zinc-500'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                    </div>

                    <span
                      className={`font-mono text-[11px] px-2 py-0.5 rounded-full border ${
                        isActive
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-zinc-800 text-zinc-500 border-zinc-700/50'
                      }`}
                    >
                      {mod.statusLabel}
                    </span>
                  </div>

                  <h4 className="font-semibold text-white text-base mb-1.5">{mod.title}</h4>
                  <p className="text-xs text-zinc-400 line-clamp-3 leading-relaxed mb-4">
                    {mod.description}
                  </p>
                </div>

                <div>
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {mod.tags.map((tag) => (
                      <span
                        key={tag}
                        className="font-mono text-[10px] text-zinc-400 bg-white/[0.03] border border-white/[0.05] px-2 py-0.5 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {isActive ? (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectModule(mod.id);
                      }}
                      className="w-full flex items-center justify-center gap-2 rounded-lg bg-violet-600 hover:bg-violet-500 py-2 text-xs font-semibold text-white transition-colors cursor-pointer"
                    >
                      <span>Open Workspace</span>
                      <ArrowRight className="h-3.5 w-3.5" />
                    </button>
                  ) : (
                    <div className="w-full flex items-center justify-center gap-1.5 py-2 text-xs text-zinc-600 font-medium">
                      <Lock className="h-3 w-3" />
                      <span>Planned Feature</span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
