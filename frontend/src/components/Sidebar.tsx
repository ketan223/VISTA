import React from 'react';
import {
  LayoutDashboard,
  Video,
  MessageSquare,
  FileText,
  Code2,
  Image as ImageIcon,
  BarChart3,
  Mic,
  Bot,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  currentPage: string;
  onNavigate: (pageId: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onNavigate,
  collapsed,
  onToggleCollapse,
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, active: true },
    { id: 'video_assistant', label: 'AI Video Assistant', icon: Video, active: true, tag: 'Ready' },
    { id: 'research_agent', label: 'Multi-AI Research', icon: Bot, active: true, tag: 'Ready' },
    { id: 'chat_assistant', label: 'AI Chat', icon: MessageSquare, active: true, tag: 'Ready' },
    { id: 'document_assistant', label: 'Document Assistant', icon: FileText, active: true, tag: 'Ready' },
    { id: 'code_assistant', label: 'Code Assistant', icon: Code2, active: false, tag: 'Soon' },
    { id: 'image_assistant', label: 'Image Assistant', icon: ImageIcon, active: false, tag: 'Soon' },
    { id: 'data_analysis', label: 'Data Analysis', icon: BarChart3, active: false, tag: 'Soon' },
    { id: 'speech_to_text', label: 'Speech-to-Text', icon: Mic, active: false, tag: 'Soon' },
    { id: 'agents_automation', label: 'AI Agents & Flows', icon: Bot, active: false, tag: 'Soon' },
  ];

  return (
    <aside
      className={`relative flex flex-col justify-between border-r border-white/[0.08] bg-[#0c0c11] transition-all duration-300 ${
        collapsed ? 'w-18' : 'w-64'
      } shrink-0 select-none z-30`}
    >
      {/* Top Header */}
      <div>
        <div className="flex h-16 items-center justify-between px-4 border-b border-white/[0.06]">
          {!collapsed ? (
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-violet-600 to-indigo-500 shadow-md shadow-violet-500/20">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <div className="font-semibold tracking-tight text-white text-base leading-none">
                  VISTA
                </div>
                <div className="text-[10px] uppercase font-mono tracking-wider text-zinc-400 mt-1">
                  AI Workspace
                </div>
              </div>
            </div>
          ) : (
            <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-violet-600 to-indigo-500 shadow-md shadow-violet-500/20">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
          )}

          <button
            onClick={onToggleCollapse}
            className="flex h-7 w-7 items-center justify-center rounded-md border border-white/[0.08] bg-[#16161f] text-zinc-400 hover:text-white hover:border-white/20 transition-colors"
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="h-3.5 w-3.5" /> : <ChevronLeft className="h-3.5 w-3.5" />}
          </button>
        </div>

        {/* Workspace telemetry chip */}
        {!collapsed && (
          <div className="mx-3 mt-4 mb-2 flex items-center justify-between rounded-md border border-white/[0.06] bg-[#14141d] px-3 py-2 text-xs">
            <div className="flex items-center gap-2">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="font-medium text-zinc-300">Final Year Project</span>
            </div>
            <span className="font-mono text-[10px] text-zinc-500">v1.0</span>
          </div>
        )}

        {/* Navigation items */}
        <nav className="mt-3 px-2 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isCurrent = currentPage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  if (item.active) {
                    onNavigate(item.id);
                  }
                }}
                disabled={!item.active}
                className={`group flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all duration-150 ${
                  isCurrent
                    ? 'bg-violet-600/15 text-violet-300 border border-violet-500/30 shadow-sm'
                    : item.active
                    ? 'text-zinc-300 hover:bg-white/[0.05] hover:text-white'
                    : 'text-zinc-600 cursor-not-allowed opacity-60'
                }`}
                title={!item.active ? `${item.label} (Coming Soon)` : item.label}
              >
                <Icon
                  className={`h-4 w-4 shrink-0 transition-colors ${
                    isCurrent ? 'text-violet-400' : item.active ? 'text-zinc-400 group-hover:text-white' : 'text-zinc-600'
                  }`}
                />
                {!collapsed && (
                  <div className="flex flex-1 items-center justify-between">
                    <span className="truncate">{item.label}</span>
                    {item.tag && (
                      <span
                        className={`font-mono text-[10px] px-1.5 py-0.5 rounded ${
                          item.tag === 'Ready'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-zinc-800 text-zinc-500'
                        }`}
                      >
                        {item.tag}
                      </span>
                    )}
                  </div>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Bottom Profile / Quick shortcuts */}
      <div className="p-3 border-t border-white/[0.06]">
        {!collapsed ? (
          <div className="flex items-center justify-between rounded-lg bg-[#14141e] p-2 border border-white/[0.04]">
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-purple-500 to-indigo-600 flex items-center justify-center font-bold text-xs text-white">
                V
              </div>
              <div className="overflow-hidden">
                <div className="text-xs font-medium text-white truncate">VISTA Workspace</div>
                <div className="text-[10px] text-zinc-400 truncate font-mono">Local Host : 5173</div>
              </div>
            </div>
            <kbd className="font-mono text-[10px] text-zinc-500 bg-white/[0.05] border border-white/10 px-1.5 py-0.5 rounded">
              ⌘K
            </kbd>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-purple-500 to-indigo-600 flex items-center justify-center font-bold text-xs text-white">
              V
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};
