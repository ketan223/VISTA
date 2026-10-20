import React, { useState, useRef } from 'react';
import {
  ArrowLeft,
  FileText,
  UploadCloud,
  AlertCircle,
  HelpCircle,
  Send,
  BookOpen,
  FileCheck,
  Tag,
  Copy,
  Check,
  Sparkles,
} from 'lucide-react';
import type { DocumentItem, DocumentCitation } from '../types';

interface DocumentAssistantWorkspaceProps {
  onBackToHub: () => void;
}

interface QATurn {
  id: string;
  question: string;
  answer: string;
  citations: DocumentCitation[];
  timestamp: string;
}

export const DocumentAssistantWorkspace: React.FC<DocumentAssistantWorkspaceProps> = ({
  onBackToHub,
}) => {
  const [doc, setDoc] = useState<DocumentItem | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [qaHistory, setQaHistory] = useState<QATurn[]>([]);
  const [question, setQuestion] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);
    setIsUploading(true);
    setUploadStatus('Reading file and extracting semantic text...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadStatus('Generating ChromaDB vector embeddings and executive summary...');
      const res = await fetch('/api/document/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: 'Failed to process document.' }));
        throw new Error(errData.detail || 'Upload failed.');
      }

      const data: DocumentItem = await res.json();
      setDoc(data);
      setQaHistory([]);
    } catch (err: any) {
      setError(err.message || 'Error occurred while processing document.');
    } finally {
      setIsUploading(false);
      setUploadStatus('');
    }
  };

  const handleAskQuestion = async (qText?: string) => {
    const query = (qText || question).trim();
    if (!query || !doc || isQuerying) return;

    setError(null);
    setIsQuerying(true);
    const tempId = `qa_${Date.now()}`;

    try {
      const res = await fetch('/api/document/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          doc_id: doc.doc_id,
          question: query,
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to query document.');
      }

      const data = await res.json();
      const newTurn: QATurn = {
        id: tempId,
        question: query,
        answer: data.answer,
        citations: data.citations || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setQaHistory((prev) => [...prev, newTurn]);
      setQuestion('');
    } catch (err: any) {
      setError(err.message || 'Error querying vector store.');
    } finally {
      setIsQuerying(false);
    }
  };

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="min-h-full p-4 lg:p-8 max-w-7xl mx-auto space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/[0.08] pb-4">
        <div className="flex items-center gap-3">
          <button
            onClick={onBackToHub}
            className="flex items-center gap-2 rounded-lg border border-white/[0.08] bg-[#12121a] px-3.5 py-1.5 text-xs font-medium text-zinc-300 hover:border-white/20 hover:text-white transition-colors"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            VISTA Hub
          </button>
          <div className="h-4 w-[1px] bg-white/[0.1]" />
          <div className="inline-flex items-center gap-2 rounded-full border border-sky-500/30 bg-sky-500/10 px-3 py-0.5 text-xs text-sky-300">
            <span className="flex h-1.5 w-1.5 rounded-full bg-sky-400 animate-pulse" />
            Module 04 · Document Intelligence & RAG
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono text-zinc-400">
          <span>ChromaDB Vector Store</span>
          <span>·</span>
          <span>HuggingFace MiniLM-L6</span>
        </div>
      </div>

      {/* Upload Zone (If no doc loaded or replace) */}
      {!doc ? (
        <div className="relative overflow-hidden rounded-2xl border border-dashed border-white/[0.15] bg-[#101018] p-10 text-center hover:border-sky-500/40 transition-colors shadow-xl">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf,.docx,.doc,.txt,.md"
            className="hidden"
          />

          <div className="max-w-md mx-auto space-y-4">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-sky-500/30 bg-sky-500/10 text-sky-400 shadow-md shadow-sky-500/10">
              <UploadCloud className="h-8 w-8" />
            </div>

            <div>
              <h3 className="text-xl font-bold text-white">Upload Research Paper or Document</h3>
              <p className="text-xs text-zinc-400 mt-1">
                Supports PDF, Microsoft Word (.docx), and text files. Automated chunking and ChromaDB indexing.
              </p>
            </div>

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-sky-500 to-indigo-600 px-6 py-2.5 text-sm font-semibold text-white hover:brightness-110 active:scale-95 transition-all shadow-md shadow-sky-500/20 disabled:opacity-50"
            >
              {isUploading ? (
                <>
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>{uploadStatus || 'Processing...'}</span>
                </>
              ) : (
                <>
                  <FileText className="h-4 w-4" />
                  <span>Choose File</span>
                </>
              )}
            </button>
          </div>
        </div>
      ) : (
        /* Document Loaded View */
        <div className="space-y-6">
          {/* Document Telemetry Banner */}
          <div className="rounded-xl border border-sky-500/30 bg-gradient-to-r from-sky-950/20 via-[#101520] to-[#12121a] p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-sky-500/40 bg-sky-500/20 text-sky-300">
                <FileCheck className="h-6 w-6" />
              </div>
              <div>
                <h2 className="text-base font-bold text-white">{doc.filename}</h2>
                <div className="flex items-center gap-3 text-xs font-mono text-zinc-400 mt-0.5">
                  <span>{doc.total_pages} Page(s)</span>
                  <span>·</span>
                  <span>{doc.total_chunks} Vector Chunks</span>
                  <span>·</span>
                  <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setDoc(null)}
                className="rounded-lg border border-white/[0.1] bg-[#1a1a26] px-3.5 py-1.5 text-xs font-medium text-zinc-300 hover:text-white hover:border-white/20 transition-colors"
              >
                Upload Different File
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column: Summary & Sample Questions */}
            <div className="space-y-5 lg:col-span-1">
              {/* Executive Summary Card */}
              <div className="rounded-xl border border-white/[0.08] bg-[#111118] p-5 shadow-lg space-y-3">
                <div className="flex items-center gap-2 text-xs font-mono text-sky-400 uppercase tracking-wider font-semibold">
                  <BookOpen className="h-4 w-4" />
                  <span>Document Intelligence</span>
                </div>
                <div className="prose prose-invert text-xs text-zinc-300 leading-relaxed whitespace-pre-wrap max-h-80 overflow-y-auto pr-1">
                  {doc.summary}
                </div>
              </div>

              {/* Sample Questions Chips */}
              {doc.sample_questions && doc.sample_questions.length > 0 && (
                <div className="rounded-xl border border-white/[0.08] bg-[#111118] p-5 shadow-lg space-y-3">
                  <div className="flex items-center gap-2 text-xs font-mono text-amber-400 uppercase tracking-wider font-semibold">
                    <Sparkles className="h-4 w-4" />
                    <span>Suggested Inquiries</span>
                  </div>
                  <div className="space-y-2">
                    {doc.sample_questions.map((sq, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleAskQuestion(sq)}
                        className="w-full text-left rounded-lg border border-white/[0.06] bg-[#161622] p-2.5 text-xs text-zinc-300 hover:border-sky-500/30 hover:text-sky-300 transition-colors flex items-start gap-2"
                      >
                        <HelpCircle className="h-3.5 w-3.5 shrink-0 mt-0.5 text-sky-400" />
                        <span>{sq}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Grounded RAG Chat Interface */}
            <div className="lg:col-span-2 flex flex-col rounded-xl border border-white/[0.08] bg-[#111118] shadow-xl overflow-hidden min-h-[500px]">
              <div className="border-b border-white/[0.06] px-5 py-3.5 flex items-center justify-between bg-[#14141f]">
                <div className="flex items-center gap-2 text-xs font-mono text-zinc-300">
                  <Tag className="h-3.5 w-3.5 text-sky-400" />
                  <span>Grounded Citation QA</span>
                </div>
                <span className="text-[11px] font-mono text-zinc-500">
                  {qaHistory.length} Question(s) answered
                </span>
              </div>

              {/* QA Feed */}
              <div className="flex-1 p-5 overflow-y-auto space-y-5">
                {qaHistory.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-64 text-center text-zinc-500 text-xs space-y-2">
                    <BookOpen className="h-8 w-8 text-zinc-600" />
                    <p>Ask any question about this document above or click a suggested inquiry.</p>
                  </div>
                ) : (
                  qaHistory.map((qa) => (
                    <div key={qa.id} className="space-y-3">
                      {/* User Query */}
                      <div className="flex items-start gap-2.5 justify-end">
                        <div className="rounded-xl bg-sky-600 px-4 py-2 text-sm text-white max-w-xl shadow-md">
                          {qa.question}
                        </div>
                      </div>

                      {/* Bot Answer */}
                      <div className="relative group rounded-xl border border-white/[0.08] bg-[#151522] p-4 text-sm text-zinc-200 space-y-3 shadow-md max-w-2xl">
                        <div className="prose prose-invert max-w-none text-sm whitespace-pre-wrap font-sans">
                          {qa.answer}
                        </div>

                        {/* Citations Box */}
                        {qa.citations && qa.citations.length > 0 && (
                          <div className="border-t border-white/[0.08] pt-3 space-y-2">
                            <div className="text-[11px] font-mono font-semibold text-sky-400 uppercase tracking-wider">
                              Verified Citations:
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                              {qa.citations.map((c, cIdx) => (
                                <div
                                  key={cIdx}
                                  className="rounded-lg border border-white/[0.06] bg-[#0c0c14] p-2 space-y-1 text-zinc-300 font-mono text-[11px]"
                                >
                                  <div className="flex items-center justify-between text-sky-300 font-bold">
                                    <span>Page {c.page}</span>
                                    <span className="text-[10px] text-zinc-500 truncate max-w-[120px]">
                                      {c.filename}
                                    </span>
                                  </div>
                                  <p className="text-zinc-400 font-sans text-[11px] line-clamp-3">
                                    "{c.snippet}"
                                  </p>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <button
                          onClick={() => handleCopy(qa.id, qa.answer)}
                          className="absolute right-3 top-3 p-1 rounded border border-white/[0.1] bg-[#1a1a28] opacity-0 group-hover:opacity-100 transition-opacity text-zinc-400 hover:text-white"
                          title="Copy answer"
                        >
                          {copiedId === qa.id ? (
                            <Check className="h-3 w-3 text-emerald-400" />
                          ) : (
                            <Copy className="h-3 w-3" />
                          )}
                        </button>
                      </div>
                    </div>
                  ))
                )}

                {isQuerying && (
                  <div className="flex items-center gap-2 rounded-xl border border-white/[0.08] bg-[#151522] p-4 text-xs text-zinc-400">
                    <div className="h-3.5 w-3.5 border-2 border-sky-400 border-t-transparent rounded-full animate-spin" />
                    <span>Retrieving vector chunks and formulating grounded answer...</span>
                  </div>
                )}
              </div>

              {/* Query Input */}
              <div className="border-t border-white/[0.08] p-3 bg-[#13131c]">
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && !isQuerying && handleAskQuestion()}
                    placeholder="Ask a question about this document..."
                    disabled={isQuerying}
                    className="flex-1 rounded-lg border border-white/[0.1] bg-[#181826] px-3.5 py-2 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-sky-500/50 font-sans"
                  />
                  <button
                    onClick={() => handleAskQuestion()}
                    disabled={isQuerying || !question.trim()}
                    className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-600 text-white hover:bg-sky-500 transition-colors disabled:opacity-40"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="flex items-center gap-2.5 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-xs text-red-300">
          <AlertCircle className="h-4 w-4 shrink-0 text-red-400" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
};
