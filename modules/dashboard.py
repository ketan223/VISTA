"""
VISTA Platform - Master Landing Page & Module Dashboard
Displays the unified VISTA workspace hero, system telemetry, and clickable module cards.
"""

import streamlit as st

MODULES_DEF = [
    {
        "id": "video_assistant",
        "title": "AI Video Assistant",
        "icon": "🎬",
        "status": "active",
        "status_label": "Ready to Use",
        "badge_color": "#10b981",
        "desc": "YouTube ingestion, local audio/video extraction, Faster-Whisper timestamped transcription, Ollama executive summaries, and grounded RAG vector chat.",
        "tags": ["Whisper STT", "ChromaDB", "LCEL RAG", "ReportLab PDF"],
    },
    {
        "id": "research_agent",
        "title": "Multi-AI Research Agent",
        "icon": "🔬",
        "status": "active",
        "status_label": "Ready to Use",
        "badge_color": "#ff8c32",
        "desc": "Autonomous 4-stage research loop: live web search (Tavily & DDGS), deep URL reader scraping, publication report synthesis, and adversarial critic scoring.",
        "tags": ["Search Agent", "Reader Scraper", "Writer Chain", "Critic Review"],
    },
    {
        "id": "chat_assistant",
        "title": "AI Chat Assistant",
        "icon": "💬",
        "status": "active",
        "status_label": "Ready to Use",
        "badge_color": "#38bdf8",
        "desc": "Conversational intelligence powered by Google Gemini 3.8 Flash, 5 specialized personas, and local Ollama resilient fallback.",
        "tags": ["Gemini 3.8 Flash", "5 Personas", "Multi-turn Memory", "Ollama Fallback"],
    },
    {
        "id": "document_assistant",
        "title": "Document Assistant (PDF RAG)",
        "icon": "📑",
        "status": "active",
        "status_label": "Ready to Use",
        "badge_color": "#a855f7",
        "desc": "Deep document QA across PDFs, DOCX, and TXT with ChromaDB semantic vector retrieval and verified page-level citations.",
        "tags": ["PDF / DOCX RAG", "ChromaDB", "Page Citations", "Mistral / Ollama"],
    },
    {
        "id": "code_assistant",
        "title": "Code Assistant",
        "icon": "💻",
        "status": "planned",
        "status_label": "Coming Soon",
        "badge_color": "#64748b",
        "desc": "Autonomous coding agent for code review, refactoring, test generation, and multi-file repository exploration.",
        "tags": ["AST Analysis", "Unit Tests", "Refactoring"],
    },
    {
        "id": "image_assistant",
        "title": "Image Assistant",
        "icon": "🎨",
        "status": "planned",
        "status_label": "Coming Soon",
        "badge_color": "#64748b",
        "desc": "Multi-modal vision analysis, image captioning, OCR text extraction, and diffusion-based creative asset generation.",
        "tags": ["Vision LLM", "OCR", "Generative AI"],
    },
    {
        "id": "data_analysis",
        "title": "Data Analysis",
        "icon": "📊",
        "status": "planned",
        "status_label": "Coming Soon",
        "badge_color": "#64748b",
        "desc": "Automated exploratory data analysis, dataset cleaning, statistical summaries, and dynamic interactive charting.",
        "tags": ["Pandas EDA", "Plotly Charts", "Auto Insights"],
    },
]

def render_dashboard():
    # Hero Section
    st.markdown(
        """
        <div style="text-align: center; padding: 2rem 1rem 2.5rem 1rem;">
            <div style="display: inline-flex; align-items: center; gap: 8px; padding: 5px 14px; border-radius: 9999px; background: rgba(124, 58, 237, 0.12); border: 1px solid rgba(167, 139, 250, 0.3); margin-bottom: 1.2rem;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 8px #10b981;"></span>
                <span style="font-size: 0.75rem; font-weight: 600; color: #c084fc; letter-spacing: 0.1em; text-transform: uppercase;">
                    Final Year Engineering Project • VISTA 1.0
                </span>
            </div>
            <h1 style="font-size: clamp(2.4rem, 6vw, 4rem); font-weight: 800; letter-spacing: -0.03em; margin: 0; background: linear-gradient(135deg, #ffffff 20%, #c084fc 60%, #38bdf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                V I S T A
            </h1>
            <p style="font-size: 1.15rem; color: #94a3b8; max-width: 650px; margin: 0.8rem auto 0 auto; line-height: 1.6;">
                Visual & Intelligent System for Task Automation — A unified, modular AI workspace powering next-generation multimodal productivity.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Telemetry Bar
    telemetry_col1, telemetry_col2, telemetry_col3 = st.columns(3)
    with telemetry_col1:
        st.markdown(
            """
            <div style="background: #12121b; border: 1px solid #232334; border-radius: 8px; padding: 0.8rem 1rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em;">Speech Engine</div>
                <div style="font-size: 0.95rem; font-weight: 600; color: #38bdf8; margin-top: 2px;">⚡ Faster-Whisper</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with telemetry_col2:
        st.markdown(
            """
            <div style="background: #12121b; border: 1px solid #232334; border-radius: 8px; padding: 0.8rem 1rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em;">Local LLM Backend</div>
                <div style="font-size: 0.95rem; font-weight: 600; color: #a855f7; margin-top: 2px;">🦙 Ollama (qwen2.5)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with telemetry_col3:
        st.markdown(
            """
            <div style="background: #12121b; border: 1px solid #232334; border-radius: 8px; padding: 0.8rem 1rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em;">Vector Database</div>
                <div style="font-size: 0.95rem; font-weight: 600; color: #10b981; margin-top: 2px;">📦 ChromaDB + LCEL</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🎛️ Workspace Modules")
    st.markdown(
        '<p style="color: #94a3b8; font-size: 0.85rem; margin-top: -10px; margin-bottom: 20px;">'
        'Select an available module below to enter its specialized environment.'
        '</p>',
        unsafe_allow_html=True,
    )

    # 2-Column Responsive Card Grid
    col_left, col_right = st.columns(2, gap="medium")

    for i, mod in enumerate(MODULES_DEF):
        target_col = col_left if (i % 2 == 0) else col_right

        with target_col:
            is_active = (mod["status"] == "active")
            card_border = "#7c3aed" if is_active else "#232332"
            glow_style = "box-shadow: 0 4px 20px rgba(124, 58, 237, 0.15);" if is_active else ""

            tags_html = " ".join([
                f'<span style="display:inline-block; font-size:0.68rem; padding:2px 8px; border-radius:4px; background:rgba(255,255,255,0.05); color:#cbd5e1; margin-right:4px;">{tag}</span>'
                for tag in mod["tags"]
            ])

            st.markdown(
                f"""
                <div style="background: #13131c; border: 1px solid {card_border}; border-radius: 12px; padding: 1.4rem; min-height: 205px; display: flex; flex-direction: column; justify-content: space-between; {glow_style} margin-bottom: 1rem;">
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.7rem;">
                            <div style="font-size: 1.7rem;">{mod['icon']}</div>
                            <span style="font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 3px 9px; border-radius: 4px; background: rgba(0,0,0,0.3); color: {mod['badge_color']}; border: 1px solid {mod['badge_color']};">
                                {mod['status_label']}
                            </span>
                        </div>
                        <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.4rem;">
                            {mod['title']}
                        </div>
                        <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5; margin-bottom: 0.8rem;">
                            {mod['desc']}
                        </div>
                    </div>
                    <div>
                        <div style="margin-bottom: 0.8rem;">{tags_html}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if is_active:
                if st.button(f"🚀 Open {mod['title']} →", key=f"open_mod_{mod['id']}", type="primary", use_container_width=True):
                    st.session_state.current_page = mod["id"]
                    st.rerun()
            else:
                st.button(f"🔒 {mod['title']} ({mod['status_label']})", key=f"disabled_mod_{mod['id']}", disabled=True, use_container_width=True)
