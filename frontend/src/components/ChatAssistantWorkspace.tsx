import React, { useState, useEffect, useRef } from 'react';
import {
  ArrowLeft,
  Sparkles,
  Send,
  Trash2,
  Copy,
  Check,
  Bot,
  User,
  Sliders,
  Code2,
  Microscope,
  Zap,
  GraduationCap,
} from 'lucide-react';
import type { ChatTurn } from '../types';

interface ChatAssistantWorkspaceProps {
  onBackToHub: () => void;
}

const PERSONAS_CONFIG = [
  {
    id: 'general',
    name: 'VISTA Partner',
    role: 'General Intelligence',
    icon: Sparkles,
    badgeColor: 'border-violet-500/40 text-violet-300 bg-violet-500/10',
  },
  {
    id: 'coder',
    name: 'Architect',
    role: 'Code & Systems',
    icon: Code2,
    badgeColor: 'border-emerald-500/40 text-emerald-300 bg-emerald-500/10',
  },
  {
    id: 'researcher',
    name: 'Scientist',
    role: 'Academic Rigor',
    icon: Microscope,
    badgeColor: 'border-sky-500/40 text-sky-300 bg-sky-500/10',
  },
  {
    id: 'creative',
    name: 'Strategist',
    role: 'Product & Vision',
    icon: Zap,
    badgeColor: 'border-amber-500/40 text-amber-300 bg-amber-500/10',
  },
  {
    id: 'tutor',
    name: 'Mentor',
    role: 'Socratic Learning',
    icon: GraduationCap,
    badgeColor: 'border-rose-500/40 text-rose-300 bg-rose-500/10',
  },
];

const STARTER_PROMPTS = [
  'Explain how Transformer attention works using an intuitive analogy.',
  'Design a resilient distributed microservices caching architecture.',
  'Write a clean, production-ready React debounce hook in TypeScript.',
  'Analyze the trade-offs between monolithic and micro-frontend paradigms.',
];

export const ChatAssistantWorkspace: React.FC<ChatAssistantWorkspaceProps> = ({
  onBackToHub,
}) => {
  const [messages, setMessages] = useState<ChatTurn[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content:
        'Hello! I am your **VISTA AI Chat Assistant**, powered by **Google Gemini 3.8 Flash** with local Ollama fallback.\n\nSelect a specialist persona above or type any question below to get started!',
      engine: 'Google Gemini 3.8 Flash',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [selectedPersona, setSelectedPersona] = useState('general');
  const [temperature] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (textToSend?: string) => {
    const userText = (textToSend || input).trim();
    if (!userText || isLoading) return;

    const userMsg: ChatTurn = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    const botMsgId = `bot_${Date.now() + 1}`;
    const botMsg: ChatTurn = {
      id: botMsgId,
      role: 'assistant',
      content: '',
      engine: 'Google Gemini 3.8 Flash',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      isStreaming: true,
    };

    const newHistory = [...messages, userMsg];
    setMessages([...newHistory, botMsg]);
    setInput('');
    setIsLoading(true);

    try {
      // Send conversation context to stream endpoint
      const payloadMessages = newHistory.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const res = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: payloadMessages,
          persona: selectedPersona,
          temperature: temperature,
        }),
      });

      if (!res.ok || !res.body) {
        throw new Error('Chat service encountered an error.');
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data:')) continue;
          const jsonStr = trimmed.slice(5).trim();
          if (!jsonStr) continue;

          try {
            const data = JSON.parse(jsonStr);
            if (data.type === 'start' || data.type === 'switch') {
              setMessages((prev) =>
                prev.map((m) => (m.id === botMsgId ? { ...m, engine: data.engine } : m))
              );
            } else if (data.type === 'chunk' && data.text) {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === botMsgId ? { ...m, content: m.content + data.text } : m
                )
              );
            } else if (data.type === 'error') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === botMsgId
                    ? { ...m, content: (m.content ? m.content + '\n\n' : '') + `⚠️ ${data.text}` }
                    : m
                )
              );
            }
          } catch {
            // ignore non-json lines
          }
        }
      }
    } catch (err: any) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === botMsgId
            ? {
                ...m,
                content:
                  m.content ||
                  `⚠️ Error: ${err.message || 'Could not communicate with chat engine.'}`,
                engine: 'System Error',
              }
            : m
        )
      );
    } finally {
      setMessages((prev) =>
        prev.map((m) => (m.id === botMsgId ? { ...m, isStreaming: false } : m))
      );
      setIsLoading(false);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: 'welcome_reset',
        role: 'assistant',
        content: 'Conversation cleared. How can I assist you next?',
        engine: 'Google Gemini 3.8 Flash',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  };

  const currentPersonaInfo = PERSONAS_CONFIG.find((p) => p.id === selectedPersona) || PERSONAS_CONFIG[0];

  return (
    <div className="flex flex-col h-full max-w-6xl mx-auto p-4 lg:p-6 space-y-4">
      {/* Top Header & Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-white/[0.08] pb-3 shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToHub}
            className="flex items-center gap-2 rounded-lg border border-white/[0.08] bg-[#12121a] px-3 py-1.5 text-xs font-medium text-zinc-300 hover:border-white/20 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            VISTA Hub
          </button>
          <div className="h-4 w-[1px] bg-white/[0.1]" />
          <div className="inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-3 py-0.5 text-xs text-violet-300">
            <span className="flex h-1.5 w-1.5 rounded-full bg-violet-400 animate-pulse" />
            Module 03 · AI Chat Assistant
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Active Model Engine Badge */}
          <div className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-[#14141f] px-3 py-1 text-xs font-mono text-zinc-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            <span>Google Gemini 3.8 Flash</span>
          </div>

          <button
            onClick={handleClearChat}
            className="flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-[#14141f] px-3 py-1.5 text-xs font-medium text-zinc-400 hover:text-rose-300 hover:border-rose-500/30 transition-colors"
            title="Reset conversation"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* Persona Selector Bar */}
      <div className="flex flex-wrap items-center gap-2 rounded-xl border border-white/[0.06] bg-[#111118] p-2.5 shrink-0 shadow-sm">
        <div className="flex items-center gap-1.5 px-2 text-xs font-mono text-zinc-500 uppercase">
          <Sliders className="h-3 w-3" />
          <span>Persona:</span>
        </div>
        {PERSONAS_CONFIG.map((p) => {
          const Icon = p.icon;
          const isSelected = selectedPersona === p.id;
          return (
            <button
              key={p.id}
              onClick={() => setSelectedPersona(p.id)}
              className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                isSelected
                  ? 'border border-violet-500/50 bg-violet-500/20 text-white shadow-sm'
                  : 'border border-white/[0.04] bg-[#161622] text-zinc-400 hover:text-zinc-200 hover:border-white/10'
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              <span>{p.name}</span>
            </button>
          );
        })}
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 rounded-xl border border-white/[0.06] bg-[#0c0c12] p-4 lg:p-6 shadow-inner">
        {messages.map((m) => {
          const isUser = m.role === 'user';
          return (
            <div
              key={m.id}
              className={`flex gap-3 max-w-4xl ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
            >
              {/* Avatar */}
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border ${
                  isUser
                    ? 'border-indigo-500/40 bg-indigo-600 text-white'
                    : 'border-violet-500/40 bg-[#1a1728] text-violet-300'
                }`}
              >
                {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              </div>

              {/* Message Content Bubble */}
              <div
                className={`relative group rounded-2xl p-4 text-sm leading-relaxed ${
                  isUser
                    ? 'bg-gradient-to-tr from-indigo-600 to-indigo-700 text-white shadow-md'
                    : 'border border-white/[0.08] bg-[#14141e] text-zinc-200 shadow-md'
                }`}
              >
                {!isUser && m.engine && (
                  <div className="flex items-center justify-between gap-4 mb-2 border-b border-white/[0.06] pb-1.5 text-[10px] font-mono text-zinc-500">
                    <span className="text-violet-400 font-semibold">{m.engine}</span>
                    <span>{m.timestamp}</span>
                  </div>
                )}

                {!isUser && m.isStreaming && !m.content ? (
                  <div className="flex items-center gap-2 text-zinc-400 py-1">
                    <div className="h-3.5 w-3.5 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
                    <span className="text-xs text-zinc-400 font-mono">Generating response...</span>
                  </div>
                ) : (
                  <div className="prose prose-invert max-w-none text-sm whitespace-pre-wrap font-sans">
                    {m.content}
                    {m.isStreaming && (
                      <span className="inline-block w-1.5 h-3.5 ml-1 bg-violet-400 animate-pulse align-middle rounded-sm" />
                    )}
                  </div>
                )}

                {/* Copy Button */}
                <button
                  onClick={() => handleCopy(m.id, m.content)}
                  className={`absolute right-2 top-2 p-1 rounded border border-white/[0.1] bg-[#1a1a28] opacity-0 group-hover:opacity-100 transition-opacity text-zinc-400 hover:text-white ${
                    isUser || m.isStreaming ? 'hidden' : 'block'
                  }`}
                  title="Copy text"
                >
                  {copiedId === m.id ? (
                    <Check className="h-3 w-3 text-emerald-400" />
                  ) : (
                    <Copy className="h-3 w-3" />
                  )}
                </button>
              </div>
            </div>
          );
        })}

        <div ref={messagesEndRef} />
      </div>

      {/* Starter Chips (Only shown if 1 message) */}
      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-2 text-xs pt-1 shrink-0">
          <span className="text-zinc-500 font-mono text-[11px] uppercase tracking-wider py-1">Quick Starters:</span>
          {STARTER_PROMPTS.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              className="rounded-lg border border-white/[0.06] bg-[#14141d] px-3 py-1 text-zinc-300 hover:border-violet-500/30 hover:text-violet-300 transition-colors"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input Bar */}
      <div className="relative flex items-center gap-2 rounded-xl border border-white/[0.1] bg-[#12121a] p-2 shadow-lg shrink-0">
        <textarea
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder={`Message ${currentPersonaInfo.name}... (Press Enter to send, Shift+Enter for newline)`}
          disabled={isLoading}
          className="flex-1 resize-none bg-transparent px-3 py-1.5 text-sm text-white placeholder-zinc-500 focus:outline-none font-sans"
        />
        <button
          onClick={() => handleSend()}
          disabled={isLoading || !input.trim()}
          className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-violet-600 to-indigo-500 text-white hover:brightness-110 active:scale-95 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-md shadow-violet-500/20"
          title="Send message"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};
