"""
VISTA Platform - FastAPI Backend Server
Exposes modular REST endpoints for VISTA and the AI Video Assistant,
connecting the high-performance React UI directly to the Python AI engine.
"""

import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel

import config
from modules.video_assistant.cache_manager import CacheManager
from modules.video_assistant.downloader import (
    download_youtube_media,
    convert_uploaded_file,
    MediaError,
)
from modules.video_assistant.transcriber import transcribe_audio
from modules.video_assistant.summarizer import generate_full_insights, is_llm_available
from modules.video_assistant.rag_engine import (
    build_or_get_vector_store,
    ask_rag_question,
)
from modules.video_assistant.exporter import export_as_markdown, export_as_pdf
from modules.research_agent.pipeline import run_research_pipeline
from modules.research_agent.exporter import (
    export_research_markdown,
    export_research_pdf,
    export_research_docx,
)
from modules.chat_assistant.engine import (
    generate_chat_response,
    generate_chat_stream,
    PERSONAS as CHAT_PERSONAS,
)
from modules.document_assistant.rag_engine import (
    index_document,
    query_document_rag,
)

app = FastAPI(
    title="VISTA Unified AI Workspace API",
    version="1.0.0",
    description="Backend API for VISTA Multimodal Intelligence Platform",
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Models ---
class ProcessURLRequest(BaseModel):
    url: str
    language: Optional[str] = "english"
    model_size: Optional[str] = "base"

class ChatRequest(BaseModel):
    source_hash: str
    question: str

class ResearchRequest(BaseModel):
    topic: str

class ExportResearchRequest(BaseModel):
    topic: str
    report: str
    feedback: Optional[str] = ""
    elapsed_seconds: Optional[float] = 0.0

class ChatMessagePayload(BaseModel):
    messages: List[Dict[str, str]]
    persona: Optional[str] = "general"
    temperature: Optional[float] = 0.7

class DocumentQueryRequest(BaseModel):
    doc_id: str
    question: str

# In-memory stores
research_jobs: Dict[str, Dict[str, Any]] = {}
indexed_documents: Dict[str, Dict[str, Any]] = {}

# --- Endpoints ---

@app.get("/api/health")
def get_health():
    """Returns system status, active models, and module readiness."""
    ollama_ready = is_llm_available()
    return {
        "status": "healthy",
        "platform": "VISTA 1.0",
        "speech_engine": "Faster-Whisper",
        "llm_engine": f"Ollama ({config.OLLAMA_MODEL})" if ollama_ready else "Ollama (Offline/Standby)",
        "ollama_ready": ollama_ready,
        "vector_store": "ChromaDB",
        "active_module": "AI Video Assistant",
    }

@app.post("/api/video/process-url")
def process_youtube_url(req: ProcessURLRequest):
    """
    Downloads, transcribes, summarizes, and indexes a YouTube video.
    """
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="YouTube URL is required.")

    # 1. Check Cache
    cached = CacheManager.load_cached_result(url, is_file=False)
    if cached:
        # Re-attach/verify vector store exists
        build_or_get_vector_store(cached["source_hash"])
        return cached

    # 2. Media Download
    try:
        media_meta = download_youtube_media(url)
    except MediaError as me:
        raise HTTPException(status_code=400, detail=str(me))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

    wav_path = media_meta["wav_path"]
    title = media_meta["title"]
    duration = media_meta.get("duration", 0)

    # 3. Transcribe with Faster-Whisper
    try:
        transcription = transcribe_audio(
            wav_path=wav_path,
            language=req.language or "english",
            model_size=req.model_size or "base",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    # 4. Generate Insights
    try:
        insights = generate_full_insights(transcription["text"])
    except Exception as e:
        insights = {
            "title": title,
            "summary": f"Could not generate summary ({str(e)}). Transcript is available.",
            "action_items": "None generated.",
            "key_decisions": "None generated.",
            "open_questions": "None generated.",
        }

    # 5. ChromaDB Vector Store
    source_hash = CacheManager.get_source_hash(url, is_file=False)
    try:
        build_or_get_vector_store(
            source_hash=source_hash,
            segments=transcription["segments"],
            source_name=title,
        )
    except Exception as e:
        print(f"[API] Warning: Vector store creation failed: {e}")

    # 6. Assemble Result & Cache
    result = {
        "title": insights.get("title") or title,
        "source": url,
        "duration": duration or transcription.get("duration", 0),
        "language": transcription.get("language", req.language),
        "transcript": transcription["text"],
        "formatted_transcript": transcription["formatted_text"],
        "segments": transcription["segments"],
        "summary": insights["summary"],
        "action_items": insights["action_items"],
        "key_decisions": insights["key_decisions"],
        "open_questions": insights["open_questions"],
        "source_hash": source_hash,
    }
    CacheManager.save_result(url, result, is_file=False)
    return result

@app.post("/api/video/upload")
async def upload_media_file(
    file: UploadFile = File(...),
    language: str = Form("english"),
    model_size: str = Form("base"),
):
    """
    Accepts and converts an uploaded media file, then runs the intelligence pipeline.
    """
    filename = file.filename or "uploaded_media.mp4"
    temp_path = config.UPLOAD_DIR / f"api_{abs(hash(filename)) % 1000000}_{filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Convert to 16kHz mono WAV
    class MockFileObj:
        def getbuffer(self):
            with open(temp_path, "rb") as f:
                return f.read()

    try:
        media_meta = convert_uploaded_file(MockFileObj(), filename)
    except MediaError as me:
        raise HTTPException(status_code=400, detail=str(me))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

    wav_path = media_meta["wav_path"]
    title = media_meta["title"]
    duration = media_meta.get("duration", 0)

    # 2. Transcribe
    try:
        transcription = transcribe_audio(
            wav_path=wav_path,
            language=language,
            model_size=model_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

    # 3. Insights
    insights = generate_full_insights(transcription["text"])

    # 4. RAG Vector Store
    source_hash = CacheManager.get_source_hash(filename, is_file=False)
    build_or_get_vector_store(
        source_hash=source_hash,
        segments=transcription["segments"],
        source_name=title,
    )

    # 5. Assemble Result
    result = {
        "title": insights.get("title") or title,
        "source": filename,
        "duration": duration or transcription.get("duration", 0),
        "language": transcription.get("language", language),
        "transcript": transcription["text"],
        "formatted_transcript": transcription["formatted_text"],
        "segments": transcription["segments"],
        "summary": insights["summary"],
        "action_items": insights["action_items"],
        "key_decisions": insights["key_decisions"],
        "open_questions": insights["open_questions"],
        "source_hash": source_hash,
    }
    CacheManager.save_result(filename, result, is_file=False)
    return result

@app.post("/api/video/chat")
def chat_with_video(req: ChatRequest):
    """
    Queries the video ChromaDB index and returns an answer citing source timestamps.
    """
    if not req.source_hash or not req.question.strip():
        raise HTTPException(status_code=400, detail="Source hash and question are required.")

    vector_store = build_or_get_vector_store(req.source_hash)
    try:
        answer, citations = ask_rag_question(vector_store, req.question.strip())
        return {
            "answer": answer,
            "citations": citations,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@app.get("/api/video/export/markdown/{source_hash}")
def download_markdown(source_hash: str):
    """Returns downloadable Markdown report for the given session."""
    cache_file = CacheManager.get_cache_path(source_hash)
    if not cache_file.exists():
        raise HTTPException(status_code=404, detail="Session not found.")

    import json
    with open(cache_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    md_content = export_as_markdown(data)
    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="VISTA_{source_hash}_report.md"'},
    )

@app.get("/api/video/export/pdf/{source_hash}")
def download_pdf(source_hash: str):
    """Generates and returns downloadable ReportLab PDF briefing."""
    cache_file = CacheManager.get_cache_path(source_hash)
    if not cache_file.exists():
        raise HTTPException(status_code=404, detail="Session not found.")

    import json
    with open(cache_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    pdf_path = config.TEMP_DIR / f"VISTA_{source_hash}_report.pdf"
    export_as_pdf(data, str(pdf_path))

    return FileResponse(
        path=str(pdf_path),
        filename=f"VISTA_{source_hash}_report.pdf",
        media_type="application/pdf",
    )

# --- Multi-AI Research Agent Endpoints ---

def execute_research_job_bg(job_id: str, topic: str):
    """Executes 4-agent research pipeline in background with stage updates."""
    def on_progress(step: int, msg: str):
        if job_id in research_jobs:
            research_jobs[job_id]["step"] = step
            research_jobs[job_id]["message"] = msg

    try:
        results = run_research_pipeline(topic, progress_callback=on_progress)
        if job_id in research_jobs:
            research_jobs[job_id]["status"] = "completed"
            research_jobs[job_id]["step"] = 5
            research_jobs[job_id]["message"] = f"Research complete in {results.get('elapsed_seconds', 0)}s!"
            research_jobs[job_id]["result"] = results
    except Exception as e:
        if job_id in research_jobs:
            research_jobs[job_id]["status"] = "error"
            research_jobs[job_id]["message"] = str(e)

@app.post("/api/research/run")
def start_research_job(req: ResearchRequest, background_tasks: BackgroundTasks):
    """Initiates an autonomous 4-stage research pipeline for the given topic."""
    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    job_id = uuid.uuid4().hex[:12]
    research_jobs[job_id] = {
        "job_id": job_id,
        "topic": topic,
        "status": "running",
        "step": 1,
        "message": "Initializing multi-agent pipeline...",
        "result": None,
    }

    background_tasks.add_task(execute_research_job_bg, job_id, topic)
    return {"job_id": job_id, "status": "running", "topic": topic}

@app.get("/api/research/status/{job_id}")
def get_research_status(job_id: str):
    """Returns real-time status and output of a running or completed research job."""
    if job_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Research job not found.")
    return research_jobs[job_id]

@app.get("/api/research/export/markdown/{job_id}")
def download_research_markdown(job_id: str):
    """Returns downloadable Markdown report for the research job."""
    if job_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Research job not found.")
    
    job = research_jobs[job_id]
    if job["status"] != "completed" or not job["result"]:
        raise HTTPException(status_code=400, detail="Research job is not completed yet.")

    res = job["result"]
    content = export_research_markdown(res)
    safe_topic = re.sub(r'[^a-zA-Z0-9]', '_', job['topic'])[:30]
    return Response(
        content=content,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="VISTA_Research_{safe_topic}.md"'},
    )

@app.get("/api/research/export/pdf/{job_id}")
def download_research_pdf(job_id: str):
    """Generates and returns professional 3-page publication-grade PDF report."""
    if job_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Research job not found.")
    
    job = research_jobs[job_id]
    if job["status"] != "completed" or not job["result"]:
        raise HTTPException(status_code=400, detail="Research job is not completed yet.")

    res = job["result"]
    safe_topic = re.sub(r'[^a-zA-Z0-9]', '_', job['topic'])[:30]
    pdf_path = config.TEMP_DIR / f"VISTA_Research_{job_id}.pdf"
    export_research_pdf(res, str(pdf_path))

    return FileResponse(
        path=str(pdf_path),
        filename=f"VISTA_Research_{safe_topic}.pdf",
        media_type="application/pdf",
    )

@app.get("/api/research/export/docx/{job_id}")
def download_research_docx(job_id: str):
    """Generates and returns structured Word (.docx) report with citations and page numbers."""
    if job_id not in research_jobs:
        raise HTTPException(status_code=404, detail="Research job not found.")
    
    job = research_jobs[job_id]
    if job["status"] != "completed" or not job["result"]:
        raise HTTPException(status_code=400, detail="Research job is not completed yet.")

    res = job["result"]
    safe_topic = re.sub(r'[^a-zA-Z0-9]', '_', job['topic'])[:30]
    docx_path = config.TEMP_DIR / f"VISTA_Research_{job_id}.docx"
    export_research_docx(res, str(docx_path))

    return FileResponse(
        path=str(docx_path),
        filename=f"VISTA_Research_{safe_topic}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

# ==============================================================================
# AI CHAT ASSISTANT ENDPOINTS (Powered by Google Gemini 3.8 Flash)
# ==============================================================================

@app.get("/api/chat/personas")
def get_chat_personas():
    """Returns available conversational personas."""
    return list(CHAT_PERSONAS.values())

@app.post("/api/chat/message")
def send_chat_message(payload: ChatMessagePayload):
    """Generates conversational response using Google Gemini with local Ollama fallback."""
    if not payload.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty.")
    
    res = generate_chat_response(
        messages=payload.messages,
        persona_id=payload.persona or "general",
        temperature=payload.temperature or 0.7
    )
    return res

@app.post("/api/chat/stream")
def stream_chat_message(payload: ChatMessagePayload):
    """
    Streams conversational response tokens using Server-Sent Events (SSE).
    Real-time character-by-character generation for low latency.
    """
    if not payload.messages:
        raise HTTPException(status_code=400, detail="Messages array cannot be empty.")
        
    return StreamingResponse(
        generate_chat_stream(
            messages=payload.messages,
            persona_id=payload.persona or "general",
            temperature=payload.temperature or 0.7,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

# ==============================================================================
# DOCUMENT ASSISTANT ENDPOINTS (PDF & Document RAG Application)
# ==============================================================================

@app.post("/api/document/upload")
async def upload_document_rag(file: UploadFile = File(...)):
    """Uploads, parses, and indexes a PDF, Word (.docx), or TXT document into ChromaDB."""
    filename = file.filename or "uploaded_doc.pdf"
    suffix = Path(filename).suffix.lower()
    if suffix not in [".pdf", ".docx", ".doc", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {suffix}. Supported: PDF, DOCX, TXT, MD")

    temp_path = config.TEMP_DIR / f"doc_{uuid.uuid4().hex[:8]}_{filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        doc_info = index_document(str(temp_path))
        doc_id = doc_info["doc_id"]
        indexed_documents[doc_id] = doc_info
        return doc_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")

@app.post("/api/document/query")
def query_document(req: DocumentQueryRequest):
    """Queries an indexed document using ChromaDB dense vector search with page-level citations."""
    doc_id = req.doc_id.strip()
    question = req.question.strip()
    if not doc_id:
        raise HTTPException(status_code=400, detail="Document ID is required.")
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        res = query_document_rag(doc_id, question)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

@app.get("/api/document/list")
def list_documents():
    """Returns list of currently indexed documents."""
    return list(indexed_documents.values())

from fastapi.staticfiles import StaticFiles

# --- Static Frontend Serving ---
dist_dir = Path(__file__).resolve().parent / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
