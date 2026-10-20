"""
VISTA Multi-AI Research Agent Workspace (ResearchMind)
Autonomous 4-Stage Research Pipeline (Search -> Reader -> Writer -> Critic)
"""

import streamlit as st
import time
from modules.research_agent.pipeline import run_research_pipeline

def render_research_agent_ui():
    # Back to Dashboard Navigation
    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("← VISTA Hub", key="btn_back_vista_research", help="Return to VISTA Main Dashboard"):
            st.session_state.active_module = None
            st.rerun()

    # Custom Styling for ResearchMind
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

    .research-hero {
        text-align: center;
        padding: 1.5rem 0 1.2rem;
    }
    .research-eyebrow {
        font-family: 'DM Mono', monospace;
        font-size: 0.72rem;
        font-weight: 500;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        color: #ff8c32;
        margin-bottom: 0.5rem;
    }
    .research-hero h1 {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2rem, 4vw, 3.2rem);
        font-weight: 800;
        color: #f0ebe0;
        margin: 0 0 0.5rem;
    }
    .research-hero h1 span {
        color: #ff8c32;
    }
    .research-hero-sub {
        font-size: 0.95rem;
        font-weight: 300;
        color: #a09890;
        max-width: 580px;
        margin: 0 auto;
        line-height: 1.5;
    }

    .pipeline-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .pipeline-step {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        position: relative;
    }
    .pipeline-step.active {
        border-color: rgba(255,140,50,0.5);
        background: rgba(255,140,50,0.06);
    }
    .pipeline-step.done {
        border-color: rgba(80,200,120,0.4);
        background: rgba(80,200,120,0.04);
    }
    .step-num {
        font-family: 'DM Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.15em;
        color: #ff8c32;
        margin-bottom: 0.2rem;
    }
    .step-title {
        font-family: 'Syne', sans-serif;
        font-weight: 700;
        font-size: 0.88rem;
        color: #f0ebe0;
    }
    .step-desc {
        font-size: 0.75rem;
        color: #8c857b;
        margin-top: 0.2rem;
    }

    .report-panel {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,140,50,0.25);
        border-radius: 14px;
        padding: 1.8rem 2.2rem;
        margin-top: 1.2rem;
    }
    .feedback-panel {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(80,200,120,0.25);
        border-radius: 14px;
        padding: 1.8rem 2.2rem;
        margin-top: 1.2rem;
    }
    .badge-score {
        display: inline-block;
        background: rgba(80,200,120,0.15);
        color: #50c878;
        font-family: 'DM Mono', monospace;
        font-weight: 700;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        border: 1px solid rgba(80,200,120,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    # Hero
    st.markdown("""
    <div class="research-hero">
        <div class="research-eyebrow">VISTA Module 02 · Autonomous Intelligence</div>
        <h1>Research<span>Mind</span></h1>
        <p class="research-hero-sub">
            Four specialized agents collaborate in an autonomous loop: Search live web sources, scrape in-depth documents, write comprehensive reports, and critically critique findings.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Session states
    if "research_results" not in st.session_state:
        st.session_state.research_results = None
    if "research_running" not in st.session_state:
        st.session_state.research_running = False

    # Pipeline Steps Overview
    st.markdown("""
    <div class="pipeline-grid">
        <div class="pipeline-step">
            <div class="step-num">STAGE 01</div>
            <div class="step-title">Search Agent</div>
            <div class="step-desc">Queries live web sources (Tavily & DDGS)</div>
        </div>
        <div class="pipeline-step">
            <div class="step-num">STAGE 02</div>
            <div class="step-title">Reader Agent</div>
            <div class="step-desc">Scrapes and reads full content from top URLs</div>
        </div>
        <div class="pipeline-step">
            <div class="step-num">STAGE 03</div>
            <div class="step-title">Writer Chain</div>
            <div class="step-desc">Synthesizes rigorous publication report</div>
        </div>
        <div class="pipeline-step">
            <div class="step-num">STAGE 04</div>
            <div class="step-title">Critic Chain</div>
            <div class="step-desc">Adversarial evaluation & scoring</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Input Topic
    topic = st.text_input(
        "Enter Research Topic or Thesis:",
        placeholder="e.g. Breakthroughs in Quantum Error Correction 2025, or Agentic AI Workflows",
        key="research_topic_input"
    )

    col_btn, col_sample1, col_sample2 = st.columns([2, 2, 2])
    with col_sample1:
        if st.button("💡 Agentic AI in 2025", key="sample_agentic"):
            st.session_state.sample_topic = "Agentic AI in 2025"
            topic = "Agentic AI in 2025"
    with col_sample2:
        if st.button("⚛️ Quantum Computing", key="sample_quantum"):
            st.session_state.sample_topic = "Quantum Computing Breakthroughs"
            topic = "Quantum Computing Breakthroughs"

    if hasattr(st.session_state, "sample_topic") and st.session_state.sample_topic:
        topic = st.session_state.sample_topic

    if st.button("🚀 Launch Autonomous Research", key="btn_run_research", disabled=st.session_state.research_running):
        if not topic.strip():
            st.warning("Please enter a research topic to begin.")
            return

        st.session_state.research_running = True
        status_box = st.empty()

        def on_progress(step: int, msg: str):
            status_box.info(f"⏳ **Stage {step}/4**: {msg}")

        try:
            with st.spinner("🤖 Autonomous Multi-Agent Pipeline is running..."):
                results = run_research_pipeline(topic.strip(), progress_callback=on_progress)
                st.session_state.research_results = results
                status_box.success(f"✅ Research pipeline completed in {results.get('elapsed_seconds', 0)}s!")
        except Exception as e:
            status_box.error(f"Pipeline error: {str(e)}")
        finally:
            st.session_state.research_running = False

    # Display Results if present
    r = st.session_state.research_results
    if r:
        st.markdown("---")
        st.subheader("📑 Research Intelligence Report")

        # Critic Scorecard Banner
        pf = r.get("parsed_feedback", {})
        score = pf.get("score", "8/10")
        verdict = pf.get("verdict", "Thoroughly analyzed with key findings.")
        
        st.markdown(f"""
        <div style="background: rgba(80,200,120,0.06); border: 1px solid rgba(80,200,120,0.3); border-radius: 12px; padding: 1rem 1.5rem; margin-bottom: 1.5rem; display: flex; align-items: center; justify-content: space-between;">
            <div>
                <span class="badge-score">CRITIC SCORE: {score}</span>
                <p style="margin: 0.5rem 0 0; color: #e0e0e0; font-size: 0.95rem;"><strong>Verdict:</strong> {verdict}</p>
            </div>
            <div style="font-family: 'DM Mono', monospace; font-size: 0.8rem; color: #888;">
                Runtime: {r.get('elapsed_seconds', 0)}s
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab_report, tab_critic, tab_search, tab_scrape = st.tabs([
            "📝 Publication Report",
            "🧐 Critic Review",
            "🔍 Raw Web Search",
            "📄 Raw Scraped Content"
        ])

        with tab_report:
            st.markdown(r.get("report", ""))
            
            st.markdown("---")
            st.markdown("##### 📥 Export Dossier Options")
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.download_button(
                    label="⬇ Download Markdown (.md)",
                    data=r.get("report", ""),
                    file_name=f"VISTA_research_{int(time.time())}.md",
                    mime="text/markdown",
                    key="download_report_btn"
                )
            with col_d2:
                import config
                from modules.research_agent.exporter import export_research_pdf
                pdf_tmp = config.TEMP_DIR / f"VISTA_research_{int(time.time())}.pdf"
                try:
                    export_research_pdf(r, str(pdf_tmp))
                    with open(pdf_tmp, "rb") as f_pdf:
                        st.download_button(
                            label="⬇ Download PDF (3-Page A4)",
                            data=f_pdf.read(),
                            file_name=f"VISTA_research_{int(time.time())}.pdf",
                            mime="application/pdf",
                            key="download_pdf_btn"
                        )
                except Exception as e_pdf:
                    st.caption(f"PDF generation error: {e_pdf}")
            with col_d3:
                from modules.research_agent.exporter import export_research_docx
                docx_tmp = config.TEMP_DIR / f"VISTA_research_{int(time.time())}.docx"
                try:
                    export_research_docx(r, str(docx_tmp))
                    with open(docx_tmp, "rb") as f_docx:
                        st.download_button(
                            label="⬇ Download Word (.docx)",
                            data=f_docx.read(),
                            file_name=f"VISTA_research_{int(time.time())}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key="download_docx_btn"
                        )
                except Exception as e_docx:
                    st.caption(f"DOCX generation error: {e_docx}")

        with tab_critic:
            st.markdown(f"### Critic Evaluation\n\n{r.get('feedback', '')}")

        with tab_search:
            st.text_area("Live Web Search Raw Output", value=r.get("search_results", ""), height=300)

        with tab_scrape:
            st.text_area("Reader Agent Clean Scraped Text", value=r.get("scraped_content", ""), height=300)
