"""
VISTA - Visual & Intelligent System for Task Automation
Main Application Entry Point and Multi-Module Router.
"""

import streamlit as st

# Import config early to apply Windows OpenMP & audioop patches
import config
from modules.dashboard import render_dashboard
from modules.video_assistant.ui import render_video_assistant_ui
from modules.research_agent.ui import render_research_agent_ui
from modules.chat_assistant.ui import render_chat_assistant_ui
from modules.document_assistant.ui import render_document_assistant_ui

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="VISTA - Unified AI Workspace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Global CSS Styling ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

    :root {
        --bg: #09090e;
        --surface: #101018;
        --surface-2: #181824;
        --border: #272738;
        --accent: #7c3aed;
        --accent-glow: #a855f7;
        --accent-cyan: #06b6d4;
        --text: #f1f5f9;
        --text-muted: #94a3b8;
    }

    html, body, [class*="css"] {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: var(--bg) !important;
        color: var(--text) !important;
    }

    .stApp {
        background-color: var(--bg) !important;
    }

    /* Subtle futuristic grid */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image:
            linear-gradient(rgba(124, 58, 237, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(124, 58, 237, 0.03) 1px, transparent 1px);
        background-size: 36px 36px;
        pointer-events: none;
        z-index: 0;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Syne', sans-serif !important;
        color: var(--text) !important;
    }

    /* Primary Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        border: 1px solid rgba(167, 139, 250, 0.3) !important;
        border-radius: 8px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.03em !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.35) !important;
        border-color: var(--accent-glow) !important;
    }

    /* Disabled buttons */
    .stButton > button:disabled {
        background: #1c1c28 !important;
        color: #64748b !important;
        border: 1px solid #272738 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* Form Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea {
        background: var(--surface-2) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2) !important;
    }

    /* Progress & Tabs */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent), var(--accent-cyan)) !important;
    }

    [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid var(--border) !important;
    }

    [data-baseweb="tab"] {
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
    }

    [aria-selected="true"] {
        color: var(--accent-glow) !important;
        border-bottom-color: var(--accent) !important;
    }

    /* Scrollbars */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent); }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session State Routing ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "dashboard"

# --- Sidebar Global Navigation ---
with st.sidebar:
    st.markdown(
        """
        <div style="padding-bottom: 0.8rem; margin-bottom: 1rem; border-bottom: 1px solid #232334;">
            <div style="font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 800; letter-spacing: -0.02em; background: linear-gradient(135deg, #ffffff, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ⚡ V I S T A
            </div>
            <div style="font-size: 0.7rem; color: #71717a; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 2px;">
                Unified AI Workspace
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Navigation")
    if st.button("🏠 VISTA Dashboard", use_container_width=True):
        st.session_state.current_page = "dashboard"
        st.rerun()

    if st.button("🎬 AI Video Assistant", use_container_width=True):
        st.session_state.current_page = "video_assistant"
        st.rerun()

    if st.button("🔬 Multi-AI Research Agent", use_container_width=True):
        st.session_state.current_page = "research_agent"
        st.rerun()

    if st.button("💬 AI Chat Assistant (Gemini)", use_container_width=True):
        st.session_state.current_page = "chat_assistant"
        st.rerun()

    if st.button("📑 Document Assistant (PDF RAG)", use_container_width=True):
        st.session_state.current_page = "document_assistant"
        st.rerun()

    st.markdown("---")
    st.markdown("#### Upcoming Modules")
    st.caption("• 💻 Code Assistant")
    st.caption("• 🎨 Image Assistant")
    st.caption("• 📊 Data Analysis")

    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.72rem; color: #64748b; line-height: 1.5;">
            <strong>College Final Year Project</strong><br>
            Engineered with Faster-Whisper, ChromaDB, Google Gemini, Ollama & LangChain LCEL.
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Page Router ---
if st.session_state.current_page == "video_assistant":
    render_video_assistant_ui()
elif st.session_state.current_page == "research_agent":
    render_research_agent_ui()
elif st.session_state.current_page == "chat_assistant":
    render_chat_assistant_ui()
elif st.session_state.current_page == "document_assistant":
    render_document_assistant_ui()
else:
    render_dashboard()
