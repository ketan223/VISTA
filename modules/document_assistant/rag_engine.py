"""
VISTA Document Assistant - PDF RAG Engine
ChromaDB vector indexing, recursive semantic chunking, and grounded citation QA.
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import config
from modules.document_assistant.parser import parse_document
from modules.research_agent.agents import get_resilient_llm

load_dotenv()

# Dedicated ChromaDB Storage for Documents
DOCS_CHROMA_DIR = config.DATA_DIR / "chroma_db_documents"
DOCS_CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Shared Local Embeddings
_embedding_model: Optional[HuggingFaceEmbeddings] = None

def get_doc_embeddings() -> HuggingFaceEmbeddings:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embedding_model

def get_doc_vector_store(doc_id: str) -> Chroma:
    """Gets or creates a ChromaDB vector store collection for a specific document."""
    embeddings = get_doc_embeddings()
    collection_name = f"doc_{doc_id}"[:63]
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(DOCS_CHROMA_DIR),
    )

def index_document(file_path: str) -> Dict[str, Any]:
    """
    Parses, chunks, embeds, and indexes an uploaded document.
    Generates an executive summary and starter query recommendations.
    """
    path_obj = Path(file_path)
    filename = path_obj.name
    
    # Generate unique document hash
    with open(file_path, "rb") as f:
        file_bytes = f.read()
    doc_id = hashlib.sha256(file_bytes).hexdigest()[:16]

    # 1. Parse Document
    pages_data = parse_document(file_path)
    if not pages_data:
        raise ValueError(f"Could not extract readable text from {filename}.")

    total_pages = max([p["page"] for p in pages_data])
    full_text = "\n\n".join([f"[Page {p['page']}]: {p['text']}" for p in pages_data])

    # 2. Semantic Chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    texts = []
    metadatas = []

    chunk_idx = 0
    for page_info in pages_data:
        page_num = page_info["page"]
        page_chunks = splitter.split_text(page_info["text"])
        for chunk in page_chunks:
            chunk_idx += 1
            texts.append(chunk)
            metadatas.append({
                "doc_id": doc_id,
                "filename": filename,
                "page": page_num,
                "chunk_index": chunk_idx,
            })

    # 3. Embed & Store in ChromaDB
    vector_store = get_doc_vector_store(doc_id)
    # Clear existing if re-uploading
    try:
        vector_store.delete_collection()
        vector_store = get_doc_vector_store(doc_id)
    except Exception:
        pass

    vector_store.add_texts(texts=texts, metadatas=metadatas)

    # 4. Generate Document Executive Summary & Sample Questions
    llm = get_resilient_llm()
    summary_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert document intelligence assistant. Provide a structured, insightful summary of the document."),
        ("human", """Analyze the following document text and provide:
1. Executive Summary (2-3 concise paragraphs covering the main theme, arguments, and conclusions).
2. Key Topics Covered (4-5 bullet points).
3. 3 Recommended Questions a reader should ask about this document.

Document Excerpt (First 3500 chars):
{text}"""),
    ])

    summary_chain = summary_prompt | llm | StrOutputParser()
    try:
        summary_result = summary_chain.invoke({"text": full_text[:3500]})
    except Exception as e:
        summary_result = f"Document '{filename}' successfully indexed with {len(texts)} chunks across {total_pages} page(s)."

    return {
        "doc_id": doc_id,
        "filename": filename,
        "file_size": len(file_bytes),
        "total_pages": total_pages,
        "total_chunks": len(texts),
        "summary": summary_result,
        "sample_questions": [
            "What are the primary findings or conclusions?",
            "What methodologies or frameworks are discussed?",
            "What limitations or key risks are highlighted?",
        ]
    }

def query_document_rag(doc_id: str, question: str) -> Dict[str, Any]:
    """
    Answers a question over the indexed document with ChromaDB retrieval
    and returns grounded citations with page numbers and source snippets.
    """
    vector_store = get_doc_vector_store(doc_id)
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(question)

    citations = []
    context_blocks = []
    for d in docs:
        meta = d.metadata
        page_num = meta.get("page", 1)
        snippet = d.page_content.strip()
        citations.append({
            "page": page_num,
            "filename": meta.get("filename", "Document"),
            "snippet": snippet[:250] + ("..." if len(snippet) > 250 else ""),
        })
        context_blocks.append(f"[Source Page {page_num}]:\n{snippet}")

    context_str = "\n\n---\n\n".join(context_blocks)

    llm = get_resilient_llm()
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a grounded Document Intelligence Assistant.
Answer the user's question accurately using ONLY the provided document context.
If the answer cannot be determined from the context, state honestly that the document does not mention it.
Always cite the source page (e.g., "[Page 2]") when making specific factual claims."""),
        ("human", """Document Context:
{context}

User Question:
{question}

Provide a direct, detailed, and well-structured answer with page citations:"""),
    ])

    qa_chain = qa_prompt | llm | StrOutputParser()
    try:
        answer = qa_chain.invoke({"context": context_str, "question": question})
    except Exception as e:
        answer = f"Error generating answer: {str(e)}"

    return {
        "doc_id": doc_id,
        "question": question,
        "answer": answer,
        "citations": citations,
    }
