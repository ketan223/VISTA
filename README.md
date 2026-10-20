# ⚡ VISTA — Visual & Intelligent System for Task Automation

> **College Final-Year Engineering Project**  
> Premium Multimodal AI Workspace inspired by Linear & Raycast aesthetics.

---

## 🌟 Executive Overview

**VISTA** is an all-in-one AI platform engineered to replace fragmented AI tools with a unified, high-performance workspace. 

The application architecture features:
- **Frontend**: A high-end **React + Vite + TypeScript + Tailwind CSS** interface inspired by Linear and Raycast dark mode ("Obsidian Precision" design system generated via Stitch MCP).
- **Backend**: High-performance **FastAPI** REST API exposing modular Python intelligence pipelines.
- **Legacy / Rapid Prototype UI**: Streamlit application preserved and functional at `http://localhost:8501`.

The first fully functional module is the **AI Video Assistant**, which transforms video and audio recordings into structured intelligence, grounded RAG Q&A, and downloadable executive reports.

---

## 🎛️ VISTA Modules Overview

| Module | Status | Technology Stack | Capabilities |
| :--- | :---: | :--- | :--- |
| **🎬 AI Video Assistant** | 🟢 **Ready to Use** | Faster-Whisper + Ollama + ChromaDB | YouTube download, media upload, timestamped STT, structured insights, grounded LCEL RAG, Markdown & PDF export. |
| **🔬 Multi-AI Research Agent** | 🟢 **Ready to Use** | Tavily + DuckDuckGo + Mistral/Ollama + python-docx + ReportLab | Autonomous 4-stage research loop: live search, reader scraper, publication writer, adversarial critic scoring, and 3-page PDF/DOCX downloads. |
| **💬 AI Chat Assistant** | 🟢 **Ready to Use** | Google Gemini 3.8 Flash + Local Ollama Fallback + SSE Streaming | Real-time token streaming chat, 5 specialized personas (General, Coder, Researcher, Creative, Tutor), and low latency REST transport. |
| **📑 Document Assistant** | 🟢 **Ready to Use** | ChromaDB + HuggingFace Embeddings + pypdf + python-docx | Multimodal PDF, DOCX, and TXT RAG QA with verified page citations, auto executive summaries, and recommended questions. |
| **💻 Code Assistant** | 🟡 *Planned* | Code LLM + AST Analysis | Multi-file code review, refactoring, test generation, and bug fixing. |
| **🎨 Image Assistant** | 🟡 *Planned* | Vision LLM + Diffusion | Image captioning, document OCR, schematic breakdown, and generative asset synthesis. |
| **📊 Data Analysis** | 🟡 *Planned* | Pandas + Plotly | Automated dataset cleaning, statistical breakdowns, and interactive charts. |
| **🎙️ Speech-to-Text** | 🟡 *Planned* | Faster-Whisper Batching | Real-time live mic streaming and bulk audio batch transcription with diarization. |
| **🤖 AI Agents & Automation** | 🟡 *Planned* | Cron multi-agent loops | Autonomous background research, notification triggers, and autonomous task execution. |

---

## 🎨 Design Direction: Obsidian Precision (Stitch MCP)

Generated using connected **Stitch MCP** tools:
- **Project ID**: `17443805051527174527`
- **Theme**: "Obsidian Precision"
- **Surfaces**: Jet black canvas (`#09090b`), surface elevations (`#121217`, `#181820`, `#22222e`)
- **Accents**: Restrained Violet (`#8b5cf6`), Indigo (`#6366f1`), and Emerald status beacons (`#10b981`)
- **Borders**: Translucent hairline boundaries (`rgba(255, 255, 255, 0.08)`)
- **Keyboard-First**: Global command palette accessible via `⌘K` or `Ctrl+K`.

---

## 🏗️ Repository Architecture

```text
VISTA/
├── api.py                     # FastAPI REST API (serves API endpoints & React static build)
├── app.py                     # Preserved Streamlit dashboard & router
├── config.py                  # Global settings, paths, Windows & Python 3.13 patches
├── requirements.txt           # Unified Python dependencies
├── .env.example               # Template environment configuration
├── frontend/                  # React + Vite + TypeScript + Tailwind CSS application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Sidebar.tsx               # Collapsible navigation rail
│   │   │   ├── Header.tsx                # Breadcrumbs, telemetry, Command+K trigger
│   │   │   ├── Dashboard.tsx             # VISTA Hub, telemetry pills, 8 module cards
│   │   │   ├── VideoAssistantWorkspace.tsx # AI Video Assistant workspace & 4 tabs
│   │   │   └── CommandPalette.tsx        # ⌘K / Ctrl+K quick launcher modal
│   │   ├── types.ts                      # TypeScript data interfaces
│   │   ├── App.tsx                       # Root application view
│   │   └── index.css                     # Obsidian Precision theme & Tailwind tokens
│   ├── vite.config.ts                    # Vite config with backend API proxy
│   └── package.json
├── modules/
│   ├── dashboard.py           # Streamlit landing page
│   └── video_assistant/       # Core Python AI Video engine
│       ├── downloader.py      # yt-dlp YouTube audio download & local file conversion
│       ├── transcriber.py     # Faster-Whisper timestamped speech-to-text
│       ├── summarizer.py      # Ollama / Mistral executive summary & analytical extraction
│       ├── rag_engine.py      # ChromaDB vector store + HuggingFace embeddings + LCEL RAG
│       ├── exporter.py        # ReportLab PDF & Markdown report generation
│       └── cache_manager.py   # Hash-based caching to avoid redundant computation
├── data/
│   ├── chroma_db/             # Persistent vector store databases
│   └── cache/                 # Cached transcripts & metadata
├── temp/
│   ├── downloads/             # Temporary YouTube downloads
│   └── uploads/               # Temporary uploaded media files
└── tests/
    ├── test_downloader.py     # URL validation & local file checks
    ├── test_cache.py          # Hash consistency & cache save/load
    ├── test_rag_engine.py     # Timestamp formatting & chunk metadata
    ├── test_exporter.py       # Markdown & ReportLab PDF generation
    └── test_pipeline_e2e.py   # End-to-end integration test (audio → STT → LLM → RAG → PDF)
```

---

## 💻 Exact Windows Commands to Run VISTA

### Option 1: Premium React Workspace (Recommended)

1. **Start the FastAPI Backend & Integrated React Production App**:
```powershell
python api.py
```
Open your browser at:
```text
http://127.0.0.1:8000
```

2. **For Frontend Developers (Vite Hot-Reloading Dev Server)**:
```powershell
# In a separate terminal:
cd C:\VISTA_Boss\frontend
npm run dev
```
Open your browser at:
```text
http://127.0.0.1:5173
```
*(Any requests to `/api/*` are automatically proxied to the backend at port 8000.)*

---

### Option 2: Streamlit Dashboard (Preserved)

```powershell
streamlit run app.py
```
Access at `http://localhost:8501`.

---

## 🧪 Automated Test Verification

Run all unit and end-to-end integration tests:
```powershell
python -m unittest discover tests
```
Output:
```text
...........
----------------------------------------------------------------------
Ran 11 tests in 57.252s

OK
```
