export type ModuleStatus = 'active' | 'planned';

export interface ModuleItem {
  id: string;
  title: string;
  iconName: string;
  status: ModuleStatus;
  statusLabel: string;
  description: string;
  tags: string[];
}

export interface Segment {
  index: number;
  start: number;
  end: number;
  start_str: string;
  end_str: string;
  time_tag: string;
  text: string;
}

export interface VideoResult {
  title: string;
  source: string;
  duration: number;
  language: string;
  transcript: string;
  formatted_transcript: string;
  segments: Segment[];
  summary: string;
  action_items: string;
  key_decisions: string;
  open_questions: string;
  source_hash: string;
}

export interface Citation {
  content: string;
  time_tag: string;
  start_time: number;
  end_time: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: string;
}

export interface SystemHealth {
  status: string;
  platform: string;
  speech_engine: string;
  llm_engine: string;
  ollama_ready: boolean;
  vector_store: string;
  active_module: string;
}

export interface CriticFeedback {
  raw: string;
  score: string;
  strengths: string[];
  improvements: string[];
  verdict: string;
}

export interface ResearchResult {
  topic: string;
  search_results: string;
  scraped_content: string;
  report: string;
  feedback: string;
  parsed_feedback?: CriticFeedback;
  elapsed_seconds: number;
}

export interface ResearchJobStatus {
  job_id: string;
  topic: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  step: number;
  message: string;
  result?: ResearchResult | null;
}

export interface ChatPersona {
  id: string;
  name: string;
  role: string;
  icon: string;
  system_prompt: string;
}

export interface ChatTurn {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  engine?: string;
  timestamp?: string;
  isStreaming?: boolean;
}

export interface DocumentItem {
  doc_id: string;
  filename: string;
  file_size: number;
  total_pages: number;
  total_chunks: number;
  summary: string;
  sample_questions: string[];
}

export interface DocumentCitation {
  page: number;
  filename: string;
  snippet: string;
}

export interface DocumentQAResponse {
  doc_id: string;
  question: string;
  answer: string;
  citations: DocumentCitation[];
}
