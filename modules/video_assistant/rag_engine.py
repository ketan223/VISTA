"""
VISTA AI Video Assistant - RAG Engine
Chunking with timestamp preservation, ChromaDB vector indexing, and
LangChain LCEL grounded question answering with timestamp citations.
"""

from typing import List, Dict, Any, Tuple
from pathlib import Path
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from config import CHROMA_DIR, EMBEDDING_MODEL_NAME, CHROMA_COLLECTION_PREFIX
from modules.video_assistant.summarizer import get_llm
from modules.video_assistant.transcriber import format_timestamp

_cached_embeddings = None

def get_embeddings() -> HuggingFaceEmbeddings:
    global _cached_embeddings
    if _cached_embeddings is None:
        print(f"[RAG] Loading embeddings model: {EMBEDDING_MODEL_NAME}...")
        _cached_embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    return _cached_embeddings

def build_documents_from_segments(
    segments: List[Dict[str, Any]],
    source_name: str,
    target_chunk_words: int = 120,
    overlap_segments: int = 1,
) -> List[Document]:
    """
    Groups transcript segments into coherent chunks while preserving exact
    start_time, end_time, and time_tag in document metadata.
    """
    if not segments:
        return []

    documents = []
    chunk_index = 0
    i = 0

    while i < len(segments):
        chunk_segs = []
        word_count = 0
        j = i

        while j < len(segments) and (word_count < target_chunk_words or len(chunk_segs) == 0):
            seg = segments[j]
            chunk_segs.append(seg)
            word_count += len(seg.get("text", "").split())
            j += 1

        if not chunk_segs:
            break

        start_time = chunk_segs[0].get("start", 0.0)
        end_time = chunk_segs[-1].get("end", start_time + 1.0)
        start_str = format_timestamp(start_time)
        end_str = format_timestamp(end_time)
        time_tag = f"[{start_str} - {end_str}]"

        text_content = " ".join([s.get("text", "") for s in chunk_segs])
        page_content = f"{time_tag} {text_content}"

        doc = Document(
            page_content=page_content,
            metadata={
                "chunk_index": chunk_index,
                "start_time": start_time,
                "end_time": end_time,
                "start_str": start_str,
                "end_str": end_str,
                "time_tag": time_tag,
                "source": source_name,
            },
        )
        documents.append(doc)
        chunk_index += 1

        # Advance with overlap
        step = max(1, len(chunk_segs) - overlap_segments)
        i += step

    return documents

def get_collection_name(source_hash: str) -> str:
    # Chroma collection names must be 3-63 chars, alphanumeric, start/end with alphanumeric
    clean_hash = "".join(c for c in source_hash if c.isalnum()).lower()
    return f"{CHROMA_COLLECTION_PREFIX}{clean_hash}"[:63]

def build_or_get_vector_store(
    source_hash: str,
    segments: List[Dict[str, Any]] = None,
    source_name: str = "Video Recording",
) -> Chroma:
    """
    Builds a new Chroma vector store collection or loads the existing one for this source.
    """
    embeddings = get_embeddings()
    collection_name = get_collection_name(source_hash)
    persist_path = str(CHROMA_DIR)

    # If segments provided, index them
    if segments:
        docs = build_documents_from_segments(segments, source_name=source_name)
        if docs:
            vector_store = Chroma.from_documents(
                documents=docs,
                embedding=embeddings,
                collection_name=collection_name,
                persist_directory=persist_path,
            )
            return vector_store

    # Otherwise load existing
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_path,
    )

def format_retrieved_docs(docs: List[Document]) -> str:
    formatted = []
    for d in docs:
        time_tag = d.metadata.get("time_tag", "")
        formatted.append(f"• {time_tag} {d.page_content}")
    return "\n\n".join(formatted)

def create_rag_chain(vector_store: Chroma, k: int = 4):
    """
    Builds an LCEL RAG chain that answers questions strictly using transcript context.
    """
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
    llm = get_llm(temperature=0.2)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """You are VISTA's Video Intelligence Assistant. Answer the user's question accurately and concisely based ONLY on the provided meeting/video transcript context.

Rules:
1. Ground every claim directly in the context.
2. If citing specific statements or events, mention their timestamp (e.g. [01:23 - 01:45]).
3. If the answer cannot be determined from the provided context, state clearly:
   "I could not find this information in the transcript."
4. Do not speculate or introduce outside knowledge.

Context from video transcript:
{context}"""
        ),
        ("human", "{question}"),
    ])

    rag_chain = (
        {
            "context": retriever | format_retrieved_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain, retriever

def ask_rag_question(
    vector_store: Chroma,
    question: str,
    k: int = 4,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Queries the vector store and generates an answer with timestamped source citations.
    """
    chain, retriever = create_rag_chain(vector_store, k=k)
    
    # Retrieve raw source documents for UI citations
    source_docs = retriever.invoke(question)
    citations = []
    for doc in source_docs:
        citations.append({
            "content": doc.page_content,
            "time_tag": doc.metadata.get("time_tag", "[00:00]"),
            "start_time": doc.metadata.get("start_time", 0.0),
            "end_time": doc.metadata.get("end_time", 0.0),
        })

    answer = chain.invoke(question)
    return answer.strip(), citations
