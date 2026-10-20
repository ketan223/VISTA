"""
VISTA Document Assistant (PDF RAG) - Streamlit UI View
ChromaDB vector indexing, semantic search, and grounded page citations.
"""

import os
import streamlit as st
import tempfile
from pathlib import Path
from modules.document_assistant.rag_engine import index_document, query_document_rag

def render_document_assistant_ui():
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <div style="font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; color: #f1f5f9;">
                📑 Document Assistant (PDF RAG)
            </div>
            <div style="font-size: 0.9rem; color: #94a3b8; margin-top: 0.25rem;">
                Upload PDFs, DOCX, or TXT documents. Ask questions with verified page citations and ChromaDB vector retrieval.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "active_doc" not in st.session_state:
        st.session_state.active_doc = None
    if "doc_qa_history" not in st.session_state:
        st.session_state.doc_qa_history = []

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a Document (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        key="doc_uploader",
    )

    if uploaded_file is not None and (
        st.session_state.active_doc is None
        or st.session_state.active_doc.get("filename") != uploaded_file.name
    ):
        with st.spinner(f"Ingesting & vector-indexing '{uploaded_file.name}' into ChromaDB..."):
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            try:
                doc_meta = index_document(tmp_path)
                doc_meta["filename"] = uploaded_file.name
                st.session_state.active_doc = doc_meta
                st.session_state.doc_qa_history = []
                st.success(f"Successfully indexed '{uploaded_file.name}' ({doc_meta['total_pages']} pages, {doc_meta['chunk_count']} vector chunks)")
            except Exception as e:
                st.error(f"Failed to index document: {str(e)}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    # Document details & summary view
    active_doc = st.session_state.active_doc
    if active_doc:
        st.markdown("---")
        col_meta1, col_meta2, col_meta3 = st.columns(3)
        with col_meta1:
            st.metric("Document", active_doc["filename"])
        with col_meta2:
            st.metric("Total Pages", active_doc["total_pages"])
        with col_meta3:
            st.metric("Vector Chunks", active_doc["chunk_count"])

        with st.expander("📄 Document Executive Summary & Key Topics", expanded=True):
            st.markdown(active_doc["summary"])

        if active_doc.get("sample_questions"):
            st.markdown("##### 💡 Suggested Questions")
            q_cols = st.columns(len(active_doc["sample_questions"]))
            for i, q in enumerate(active_doc["sample_questions"]):
                with q_cols[i]:
                    if st.button(f"👉 {q}", key=f"sugg_q_{i}"):
                        st.session_state.pending_question = q

        st.markdown("---")
        st.markdown("#### 💬 Ask Questions About This Document")

        # Display QA History
        for item in st.session_state.doc_qa_history:
            with st.chat_message("user"):
                st.markdown(item["question"])
            with st.chat_message("assistant"):
                st.caption(f"⚡ Engine: {item['engine']}")
                st.markdown(item["answer"])
                if item.get("citations"):
                    st.markdown("**Grounded Page References:**")
                    for c in item["citations"]:
                        st.caption(f"• **Page {c['page']}** (Relevance: {round(c['score']*100)}%): *\"{c['snippet'][:150]}...\"*")

        # Input box
        prompt = st.chat_input("Ask any question grounded in the document...")
        if prompt:
            st.session_state.doc_qa_history.append({"question": prompt, "answer": "...", "engine": "Mistral / Ollama", "citations": []})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Retrieving vector embeddings & reasoning..."):
                    qa_res = query_document_rag(doc_id=active_doc["doc_id"], query=prompt)
                    st.caption(f"⚡ Engine: {qa_res.get('engine', 'Mistral / Ollama')}")
                    st.markdown(qa_res["answer"])
                    if qa_res.get("citations"):
                        st.markdown("**Grounded Page References:**")
                        for c in qa_res["citations"]:
                            st.caption(f"• **Page {c['page']}** (Relevance: {round(c['score']*100)}%): *\"{c['snippet'][:150]}...\"*")

            # Update last entry
            st.session_state.doc_qa_history[-1] = {
                "question": prompt,
                "answer": qa_res["answer"],
                "engine": qa_res["engine"],
                "citations": qa_res.get("citations", []),
            }
