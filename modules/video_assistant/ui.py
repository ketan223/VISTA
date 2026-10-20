"""
VISTA AI Video Assistant - Dedicated Workspace UI
Interactive Streamlit interface with tabs: Overview, Transcript, AI Chat, and Export.
"""

import os
import time
import tempfile
from pathlib import Path
import streamlit as st

from config import (
    WHISPER_MODEL,
    LLM_PROVIDER,
    OLLAMA_MODEL,
    MISTRAL_API_KEY,
    TEMP_DIR,
)
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

def render_video_assistant_ui():
    # --- Top Navigation Bar ---
    nav_col1, nav_col2 = st.columns([1, 4])
    with nav_col1:
        if st.button("← Back to Hub", key="va_back_btn"):
            st.session_state.current_page = "dashboard"
            st.rerun()
    with nav_col2:
        st.markdown(
            '<div style="font-size: 0.85rem; color: #a1a1aa; padding-top: 6px;">'
            'VISTA Platform &nbsp;/&nbsp; <strong style="color: #c084fc;">AI Video Assistant</strong>'
            '</div>',
            unsafe_allow_html=True,
        )

    # Header
    st.markdown(
        """
        <div style="margin: 0.8rem 0 1.5rem 0;">
            <h1 style="font-size: 2.2rem; margin-bottom: 0.2rem;">🎬 AI Video Assistant</h1>
            <p style="color: #94a3b8; font-size: 0.95rem; margin: 0;">
                Extract audio, transcribe multilingual speech, generate structured intelligence, and chat with your recordings using grounded RAG.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Sidebar Controls ---
    with st.sidebar:
        st.markdown("### ⚙️ Video Assistant Settings")
        
        # Whisper Model Selection
        whisper_models = ["tiny", "base", "small", "medium"]
        current_model_idx = whisper_models.index(WHISPER_MODEL) if WHISPER_MODEL in whisper_models else 1
        selected_whisper_model = st.selectbox(
            "Whisper Model Size",
            whisper_models,
            index=current_model_idx,
            help="Base is fast and lightweight. Small/Medium provide higher accuracy for difficult audio.",
        )

        # Language Selection
        languages = [
            ("English", "english"),
            ("Auto Detect", "auto"),
            ("Hindi", "hindi"),
            ("Hinglish", "hinglish"),
            ("Spanish", "spanish"),
            ("French", "french"),
            ("German", "german"),
        ]
        selected_lang_tuple = st.selectbox(
            "Audio Language",
            languages,
            format_func=lambda x: x[0],
            index=0,
        )
        selected_language = selected_lang_tuple[1]

        # LLM Engine Indicator
        st.markdown("---")
        st.markdown("**Active LLM Engine:**")
        if LLM_PROVIDER.lower() == "mistral" and MISTRAL_API_KEY:
            st.info("☁️ **Mistral Cloud** (API Active)")
        else:
            st.success(f"🖥️ **Ollama Local** (`{OLLAMA_MODEL}`)")

        # Clear Cache / Reset Current Video
        if st.session_state.get("va_result"):
            st.markdown("---")
            if st.button("🔄 Start New Video Analysis", use_container_width=True):
                st.session_state.va_result = None
                st.session_state.va_chat_history = []
                st.session_state.va_source_hash = None
                st.session_state.va_vector_store = None
                st.rerun()

    # --- Session State Defaults ---
    if "va_result" not in st.session_state:
        st.session_state.va_result = None
    if "va_chat_history" not in st.session_state:
        st.session_state.va_chat_history = []
    if "va_source_hash" not in st.session_state:
        st.session_state.va_source_hash = None
    if "va_vector_store" not in st.session_state:
        st.session_state.va_vector_store = None

    # --- Input Section (if no result yet) ---
    if not st.session_state.va_result:
        input_container = st.container()
        with input_container:
            st.markdown("### 📥 Select Video or Audio Source")
            input_mode = st.radio(
                "Input Method:",
                ["YouTube URL", "Upload Audio/Video File"],
                horizontal=True,
            )

            source_to_process = None
            is_file_upload = False
            uploaded_file_obj = None

            if input_mode == "YouTube URL":
                yt_url = st.text_input(
                    "YouTube Video Link:",
                    placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/...",
                )
                if yt_url.strip():
                    source_to_process = yt_url.strip()
            else:
                uploaded_file = st.file_uploader(
                    "Choose an audio or video file (MP4, MP3, WAV, MKV, MOV, etc.):",
                    type=["mp4", "mp3", "wav", "mkv", "mov", "m4a", "flac", "ogg"],
                )
                if uploaded_file is not None:
                    source_to_process = uploaded_file.name
                    is_file_upload = True
                    uploaded_file_obj = uploaded_file

            process_btn = st.button("⚡ Run Video Intelligence", type="primary", use_container_width=False)

            if process_btn:
                if not source_to_process:
                    st.error("Please enter a valid YouTube URL or upload a media file.")
                    return

                # Check Cache first
                cached_data = CacheManager.load_cached_result(
                    source=source_to_process,
                    is_file=is_file_upload,
                )

                if cached_data:
                    st.info("⚡ Loading previously indexed analysis from cache...")
                    # Reconnect vector store
                    vector_store = build_or_get_vector_store(cached_data["source_hash"])
                    st.session_state.va_result = cached_data
                    st.session_state.va_source_hash = cached_data["source_hash"]
                    st.session_state.va_vector_store = vector_store
                    st.rerun()

                # Execution pipeline with progress bars
                progress_box = st.empty()
                progress_bar = st.progress(0)
                status_text = st.empty()

                def update_progress(pct: int, msg: str):
                    progress_bar.progress(min(100, max(0, pct)))
                    status_text.markdown(f"**Status:** {msg}")

                try:
                    # Step 1: Media acquisition & audio extraction
                    update_progress(5, "Acquiring audio stream...")
                    if is_file_upload:
                        media_meta = convert_uploaded_file(uploaded_file_obj, source_to_process)
                    else:
                        media_meta = download_youtube_media(source_to_process, progress_callback=lambda p, m: update_progress(int(p * 0.2), m))

                    wav_path = media_meta["wav_path"]
                    media_title = media_meta["title"]
                    media_duration = media_meta.get("duration", 0)

                    # Step 2: Speech-to-Text with Faster-Whisper
                    update_progress(25, "Transcribing speech with Faster-Whisper...")
                    transcription = transcribe_audio(
                        wav_path=wav_path,
                        language=selected_language,
                        model_size=selected_whisper_model,
                        progress_callback=lambda p, m: update_progress(int(25 + p * 0.35), m),
                    )

                    # Step 3: LLM Insights (Summary, Action items, Decisions, Questions)
                    update_progress(65, "Generating structured insights & summaries...")
                    insights = generate_full_insights(
                        transcript=transcription["text"],
                        progress_callback=lambda p, m: update_progress(int(65 + p * 0.2), m),
                    )

                    # Step 4: RAG Vector Indexing with ChromaDB & HuggingFace
                    update_progress(88, "Building RAG vector database with segment timestamps...")
                    source_hash = CacheManager.get_source_hash(source_to_process, is_file=is_file_upload)
                    vector_store = build_or_get_vector_store(
                        source_hash=source_hash,
                        segments=transcription["segments"],
                        source_name=media_title,
                    )

                    # Compile result package
                    result_data = {
                        "title": insights.get("title") or media_title,
                        "source": source_to_process,
                        "duration": media_duration or transcription.get("duration", 0),
                        "language": transcription.get("language", selected_language),
                        "transcript": transcription["text"],
                        "formatted_transcript": transcription["formatted_text"],
                        "segments": transcription["segments"],
                        "summary": insights["summary"],
                        "action_items": insights["action_items"],
                        "key_decisions": insights["key_decisions"],
                        "open_questions": insights["open_questions"],
                        "source_hash": source_hash,
                    }

                    # Save to cache
                    CacheManager.save_result(source_to_process, result_data, is_file=is_file_upload)

                    st.session_state.va_result = result_data
                    st.session_state.va_source_hash = source_hash
                    st.session_state.va_vector_store = vector_store

                    update_progress(100, "Analysis complete!")
                    time.sleep(0.5)
                    progress_box.empty()
                    progress_bar.empty()
                    status_text.empty()
                    st.rerun()

                except MediaError as me:
                    st.error(f"Media Error: {str(me)}")
                except Exception as ex:
                    st.error(f"Processing Failed: {str(ex)}")

    # --- Render Result Tabs ---
    if st.session_state.va_result:
        res = st.session_state.va_result
        source_hash = st.session_state.va_source_hash or res.get("source_hash", "default")
        vector_store = st.session_state.va_vector_store
        if vector_store is None:
            vector_store = build_or_get_vector_store(source_hash)
            st.session_state.va_vector_store = vector_store

        # Header card with title & meta
        mins = int(res.get("duration", 0) // 60)
        secs = int(res.get("duration", 0) % 60)
        st.markdown(
            f"""
            <div style="background: #181824; border: 1px solid #2e2e42; border-radius: 10px; padding: 1.2rem; margin-bottom: 1.2rem;">
                <div style="font-size: 0.75rem; color: #a78bfa; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem;">
                    Active Video Intelligence Session
                </div>
                <div style="font-size: 1.4rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.5rem;">
                    {res.get('title', 'Video Analysis')}
                </div>
                <div style="display: flex; gap: 1rem; flex-wrap: wrap; font-size: 0.85rem; color: #94a3b8;">
                    <span>⏱️ Duration: <strong>{mins:02d}:{secs:02d}</strong></span>
                    <span>🌐 Language: <strong>{res.get('language', 'Auto').upper()}</strong></span>
                    <span>🔗 Source: <strong style="color: #cbd5e1;">{res.get('source', 'Uploaded')}</strong></span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Tab Navigation
        tab_overview, tab_transcript, tab_chat, tab_export = st.tabs([
            "📋 Overview & Insights",
            "📝 Timestamped Transcript",
            "💬 AI Chat (RAG)",
            "📥 Export Reports",
        ])

        # TAB 1: Overview
        with tab_overview:
            col_sum1, col_sum2 = st.columns([3, 2], gap="medium")
            with col_sum1:
                st.markdown("#### 📋 Executive Summary")
                st.markdown(
                    f'<div style="background:#13131c; border:1px solid #272738; border-radius:8px; padding:1.2rem; line-height:1.7;">'
                    f'{res.get("summary", "No summary.")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with col_sum2:
                st.markdown("#### 🔑 Key Decisions")
                st.markdown(
                    f'<div style="background:#13131c; border:1px solid #272738; border-radius:8px; padding:1.2rem; line-height:1.7;">'
                    f'{res.get("key_decisions", "No decisions recorded.")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("<br>", unsafe_allow_html=True)
            col_act, col_quest = st.columns(2, gap="medium")
            with col_act:
                st.markdown("#### ✅ Action Items & Tasks")
                st.markdown(
                    f'<div style="background:#13131c; border:1px solid #272738; border-radius:8px; padding:1.2rem; line-height:1.7;">'
                    f'{res.get("action_items", "No action items.")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with col_quest:
                st.markdown("#### ❓ Open Questions & Follow-ups")
                st.markdown(
                    f'<div style="background:#13131c; border:1px solid #272738; border-radius:8px; padding:1.2rem; line-height:1.7;">'
                    f'{res.get("open_questions", "No unresolved questions.")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # TAB 2: Transcript
        with tab_transcript:
            st.markdown("#### 📝 Full Audio Transcript with Timestamps")
            formatted_text = res.get("formatted_transcript") or res.get("transcript", "")
            
            filter_search = st.text_input("🔍 Search transcript for keyword:", "")
            if filter_search.strip():
                lines = [line for line in formatted_text.splitlines() if filter_search.lower() in line.lower()]
                display_text = "\n".join(lines) if lines else f"No matches found for '{filter_search}'."
            else:
                display_text = formatted_text

            st.text_area(
                "Transcript Content",
                value=display_text,
                height=420,
                label_visibility="collapsed",
            )
            st.download_button(
                "⬇️ Download Raw Transcript (.txt)",
                data=formatted_text,
                file_name=f"{source_hash}_transcript.txt",
                mime="text/plain",
            )

        # TAB 3: AI Chat (RAG)
        with tab_chat:
            st.markdown("#### 💬 Grounded Meeting Assistant (RAG)")
            st.markdown(
                '<p style="font-size:0.85rem; color:#94a3b8;">'
                'Answers are generated strictly using retrieved segments from this transcript with timestamp citations.'
                '</p>',
                unsafe_allow_html=True,
            )

            # Display Chat Messages
            chat_container = st.container()
            with chat_container:
                if not st.session_state.va_chat_history:
                    st.info("👋 Ask any question about this video (e.g. 'What was decided about the budget?', 'Who is responsible for the deadline?').")
                else:
                    for msg in st.session_state.va_chat_history:
                        if msg["role"] == "user":
                            st.chat_message("user").write(msg["content"])
                        else:
                            with st.chat_message("assistant"):
                                st.write(msg["content"])
                                if "citations" in msg and msg["citations"]:
                                    with st.expander("📌 Source Citations & Timestamps", expanded=False):
                                        for cit in msg["citations"]:
                                            st.markdown(f"**{cit['time_tag']}**: `{cit['content']}`")

            # Chat Input Form
            with st.form("va_chat_form", clear_on_submit=True):
                user_question = st.text_input("Ask a question about the video:", placeholder="What are the key takeaways?")
                submit_q = st.form_submit_button("Send Question →", type="primary")

            if submit_q and user_question.strip():
                st.session_state.va_chat_history.append({"role": "user", "content": user_question.strip()})
                with st.spinner("Searching transcript context and synthesizing answer..."):
                    try:
                        answer, citations = ask_rag_question(vector_store, user_question.strip())
                    except Exception as err:
                        answer = f"Error querying video RAG engine: {str(err)}"
                        citations = []

                st.session_state.va_chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": citations,
                })
                st.rerun()

            if st.session_state.va_chat_history:
                if st.button("🗑️ Clear Chat History"):
                    st.session_state.va_chat_history = []
                    st.rerun()

        # TAB 4: Export
        with tab_export:
            st.markdown("#### 📥 Export Intelligence Reports")
            st.markdown("Download full structured reports including executive summaries, decision matrices, action items, and timestamped transcripts.")

            col_exp_md, col_exp_pdf = st.columns(2, gap="large")

            # Markdown Export
            with col_exp_md:
                st.markdown("##### 📄 Markdown (.md)")
                st.caption("Clean, structured Markdown document suitable for Obsidian, Notion, or GitHub.")
                md_content = export_as_markdown(res)
                st.download_button(
                    label="⬇️ Download Markdown Report",
                    data=md_content,
                    file_name=f"VISTA_{source_hash}_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            # PDF Export
            with col_exp_pdf:
                st.markdown("##### 📕 PDF Executive Briefing (.pdf)")
                st.caption("Publication-ready PDF document created via ReportLab with styled headings and tables.")
                pdf_temp_path = TEMP_DIR / f"VISTA_{source_hash}_report.pdf"
                
                # Generate PDF on the fly
                export_as_pdf(res, str(pdf_temp_path))
                
                with open(pdf_temp_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()

                st.download_button(
                    label="⬇️ Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"VISTA_{source_hash}_report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
