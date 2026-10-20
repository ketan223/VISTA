import React, { useState, useEffect } from 'react';
import {
  Search,
  Video,
  MessageSquare,
  FileText,
  Code2,
  Image as ImageIcon,
  BarChart3,
  Mic,
  Bot,
  X,
  ArrowRight,
} from 'lucide-react';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectModule: (moduleId: string) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onSelectModule,
}) => {
  const [query, setQuery] = useState('');

  const commands = [
    { id: 'video_assistant', title: 'Open AI Video Assistant', icon: Video, active: true, category: 'Available Modules' },
    { id: 'research_agent', title: 'Open Multi-AI Research Agent', icon: Bot, active: true, category: 'Available Modules' },
    { id: 'chat_assistant', title: 'Open AI Chat Assistant (Gemini)', icon: MessageSquare, active: true, category: 'Available Modules' },
    { id: 'document_assistant', title: 'Open Document Assistant (PDF RAG)', icon: FileText, active: true, category: 'Available Modules' },
    { id: 'code_assistant', title: 'Code Assistant', icon: Code2, active: false, category: 'Planned Modules' },
    { id: 'image_assistant', title: 'Image Assistant', icon: ImageIcon, active: false, category: 'Planned Modules' },
    { id: 'data_analysis', title: 'Data Analysis', icon: BarChart3, active: false, category: 'Planned Modules' },
    { id: 'speech_to_text', title: 'Speech-to-Text', icon: Mic, active: false, category: 'Planned Modules' },
    { id: 'agents_automation', title: 'AI Agents & Automation', icon: Bot, active: false, category: 'Planned Modules' },
  ];

  const filtered = commands.filter((c) =>
    c.title.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/70 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="w-full max-w-xl overflow-hidden rounded-xl border border-white/[0.12] bg-[#14141e] shadow-2xl shadow-black/80">
        {/* Search header */}
        <div className="flex items-center border-b border-white/[0.08] px-4 py-3">
          <Search className="h-4 w-4 text-zinc-400 mr-3" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search commands, modules, or actions..."
            className="flex-1 bg-transparent text-sm text-white placeholder-zinc-500 outline-none"
            autoFocus
          />
          <button
            onClick={onClose}
            className="p-1 rounded text-zinc-500 hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-80 overflow-y-auto p-2">
          {filtered.length > 0 ? (
            filtered.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  disabled={!item.active}
                  onClick={() => {
                    if (item.active) {
                      onSelectModule(item.id);
                      onClose();
                    }
                  }}
                  className={`flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm text-left transition-colors ${
                    item.active
                      ? 'text-zinc-200 hover:bg-violet-600/15 hover:text-white cursor-pointer'
                      : 'text-zinc-600 cursor-not-allowed opacity-50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 rounded-md bg-white/[0.05] border border-white/5">
                      <Icon className="h-4 w-4 text-violet-400" />
                    </div>
                    <span>{item.title}</span>
                  </div>
                  {item.active ? (
                    <span className="flex items-center gap-1 text-xs text-violet-400">
                      Launch <ArrowRight className="h-3 w-3" />
                    </span>
                  ) : (
                    <span className="font-mono text-[10px] text-zinc-600 bg-white/[0.03] px-2 py-0.5 rounded">
                      Planned
                    </span>
                  )}
                </button>
              );
            })
          ) : (
            <div className="py-8 text-center text-sm text-zinc-500">
              No matching modules or commands found.
            </div>
          )}
        </div>

        {/* Footer shortcuts */}
        <div className="flex items-center justify-between border-t border-white/[0.06] bg-[#0f0f17] px-4 py-2 text-[11px] text-zinc-500 font-mono">
          <span>Navigation: ↑ ↓ to navigate</span>
          <span>ESC to dismiss</span>
        </div>
      </div>
    </div>
  );
};
