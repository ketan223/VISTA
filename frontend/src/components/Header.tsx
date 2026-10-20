import React from 'react';
import { Search, Cpu, HardDrive, Terminal } from 'lucide-react';
import type { SystemHealth } from '../types';

interface HeaderProps {
  currentPage: string;
  onOpenCommand: () => void;
  health: SystemHealth | null;
}

export const Header: React.FC<HeaderProps> = ({
  currentPage,
  onOpenCommand,
  health,
}) => {
  const getPageTitle = (page: string) => {
    switch (page) {
      case 'video_assistant':
        return 'AI Video Assistant';
      case 'chat_assistant':
        return 'AI Chat Assistant';
      default:
        return 'Platform Hub';
    }
  };

  return (
    <header className="flex h-16 w-full items-center justify-between border-b border-white/[0.08] bg-[#0c0c11]/80 backdrop-blur-md px-6 z-20">
      {/* Left: Breadcrumbs */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-zinc-500 hover:text-zinc-300 cursor-pointer font-medium">VISTA</span>
        <span className="text-zinc-600">/</span>
        <span className="text-zinc-200 font-semibold">{getPageTitle(currentPage)}</span>
      </div>

      {/* Middle: Command Bar Trigger */}
      <button
        onClick={onOpenCommand}
        className="flex w-72 items-center justify-between rounded-lg border border-white/[0.08] bg-[#14141e] px-3.5 py-1.5 text-xs text-zinc-400 hover:border-white/20 hover:text-zinc-200 transition-all shadow-sm"
      >
        <div className="flex items-center gap-2">
          <Search className="h-3.5 w-3.5 text-zinc-500" />
          <span>Jump to module or command...</span>
        </div>
        <kbd className="font-mono text-[10px] text-zinc-400 bg-white/[0.06] border border-white/10 px-1.5 py-0.5 rounded">
          ⌘K
        </kbd>
      </button>

      {/* Right: Engine Telemetry Badges */}
      <div className="flex items-center gap-3">
        <div className="hidden lg:flex items-center gap-2 rounded-md border border-white/[0.06] bg-[#13131c] px-2.5 py-1 text-xs">
          <Cpu className="h-3.5 w-3.5 text-violet-400" />
          <span className="text-zinc-400 font-mono text-[11px]">
            {health?.speech_engine || 'Faster-Whisper'}
          </span>
        </div>

        <div className="hidden md:flex items-center gap-2 rounded-md border border-white/[0.06] bg-[#13131c] px-2.5 py-1 text-xs">
          <Terminal className="h-3.5 w-3.5 text-indigo-400" />
          <span className="text-zinc-300 font-mono text-[11px]">
            {health?.llm_engine || 'Ollama (qwen2.5:1.5b)'}
          </span>
          <span className={`inline-block h-1.5 w-1.5 rounded-full ${health?.ollama_ready ? 'bg-emerald-400' : 'bg-amber-400'}`} />
        </div>

        <div className="hidden xl:flex items-center gap-2 rounded-md border border-white/[0.06] bg-[#13131c] px-2.5 py-1 text-xs">
          <HardDrive className="h-3.5 w-3.5 text-emerald-400" />
          <span className="text-zinc-400 font-mono text-[11px]">ChromaDB RAG</span>
        </div>
      </div>
    </header>
  );
};
