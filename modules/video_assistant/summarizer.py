"""
VISTA AI Video Assistant - Summarization and Insights Engine
Extracts comprehensive summaries, key decisions, action items, and follow-up questions
using local Ollama models (default) or optional cloud LLMs (Mistral) with LCEL.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    MISTRAL_API_KEY,
    MISTRAL_MODEL,
)

def get_llm(temperature: float = 0.2):
    """
    Returns an LLM instance based on availability and configuration.
    Priority:
    1. If MISTRAL_API_KEY is present and LLM_PROVIDER == 'mistral', use ChatMistralAI
    2. Default: ChatOllama (local, free, privacy-preserving)
    """
    if LLM_PROVIDER.lower() == "mistral" and MISTRAL_API_KEY:
        try:
            from langchain_mistralai import ChatMistralAI
            return ChatMistralAI(
                model=MISTRAL_MODEL,
                mistral_api_key=MISTRAL_API_KEY,
                temperature=temperature,
            )
        except Exception as e:
            print(f"[Summarizer] Mistral initialization failed ({e}), falling back to Ollama.")

    # Local Ollama default
    from langchain_ollama import ChatOllama
    return ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        temperature=temperature,
    )

def is_llm_available() -> bool:
    """Check whether any LLM backend (Ollama or Mistral) is reachable."""
    try:
        llm = get_llm()
        res = llm.invoke("Hi")
        return bool(res)
    except Exception:
        return False

def split_text_for_summary(text: str, chunk_size: int = 3500, chunk_overlap: int = 200) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)

def generate_title(transcript: str) -> str:
    """Generate a crisp, professional title for the recording."""
    try:
        llm = get_llm(temperature=0.3)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an executive assistant. Generate a concise, informative title (under 8 words) for this video transcript. Return ONLY the title text."),
            ("human", "{text}"),
        ])
        chain = prompt | llm | StrOutputParser()
        sample = transcript[:2500] if len(transcript) > 2500 else transcript
        title = chain.invoke({"text": sample}).strip().strip('"').strip("'")
        return title if title else "Meeting Analysis"
    except Exception as e:
        print(f"[Summarizer] Title generation fallback: {e}")
        return "Video / Meeting Intelligence Session"

def generate_summary(transcript: str, progress_callback=None) -> str:
    """Generate a structured, bulleted summary of the video transcript."""
    try:
        llm = get_llm(temperature=0.2)
        chunks = split_text_for_summary(transcript)

        if len(chunks) == 1:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are an executive analyst. Provide a structured, high-quality summary of the meeting/video transcript below. Use clear bullet points and bold key themes."),
                ("human", "{text}"),
            ])
            chain = prompt | llm | StrOutputParser()
            return chain.invoke({"text": chunks[0]}).strip()

        # Map-Reduce for longer recordings
        partial_summaries = []
        map_prompt = ChatPromptTemplate.from_messages([
            ("system", "Summarize this portion of a transcript concisely in 3-4 bullet points."),
            ("human", "{text}"),
        ])
        map_chain = map_prompt | llm | StrOutputParser()

        for idx, chunk in enumerate(chunks):
            if progress_callback:
                progress_callback(int((idx / len(chunks)) * 40) + 10, f"Summarizing segment {idx+1}/{len(chunks)}...")
            part = map_chain.invoke({"text": chunk}).strip()
            partial_summaries.append(part)

        combined_text = "\n\n".join(partial_summaries)
        combine_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert analyst. Consolidate these section summaries into one final executive summary with key themes and bullet points."),
            ("human", "{text}"),
        ])
        combine_chain = combine_prompt | llm | StrOutputParser()
        return combine_chain.invoke({"text": combined_text}).strip()

    except Exception as e:
        print(f"[Summarizer] Summary error: {e}")
        return f"Automatic summary could not be completed ({str(e)}). Transcript is available in the Transcript tab."

def extract_action_items(transcript: str) -> str:
    """Extract action items, responsible owners, and deadlines."""
    try:
        llm = get_llm(temperature=0.1)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a project manager. Extract all specific action items, tasks, and deliverables from the transcript. For each item specify:\n- Task\n- Owner (if mentioned, otherwise 'Unassigned')\n- Deadline (if mentioned, otherwise 'Not specified')\nFormat as a clean markdown numbered list. If none found, write 'No action items identified.'"),
            ("human", "{text}"),
        ])
        chain = prompt | llm | StrOutputParser()
        sample = transcript[:8000]
        return chain.invoke({"text": sample}).strip()
    except Exception as e:
        return f"Unable to extract action items: {str(e)}"

def extract_key_decisions(transcript: str) -> str:
    """Extract key decisions, conclusions, and agreements made."""
    try:
        llm = get_llm(temperature=0.1)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract all key decisions, major conclusions, or agreements reached in this transcript. Format as a markdown numbered list. If none found, write 'No formal decisions recorded.'"),
            ("human", "{text}"),
        ])
        chain = prompt | llm | StrOutputParser()
        sample = transcript[:8000]
        return chain.invoke({"text": sample}).strip()
    except Exception as e:
        return f"Unable to extract key decisions: {str(e)}"

def extract_questions(transcript: str) -> str:
    """Extract unresolved questions, open issues, or follow-ups."""
    try:
        llm = get_llm(temperature=0.1)
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract all unresolved questions, open doubts, or topics flagged for future follow-up from this transcript. Format as a markdown numbered list. If none found, write 'No unresolved questions found.'"),
            ("human", "{text}"),
        ])
        chain = prompt | llm | StrOutputParser()
        sample = transcript[:8000]
        return chain.invoke({"text": sample}).strip()
    except Exception as e:
        return f"Unable to extract open questions: {str(e)}"

def generate_full_insights(transcript: str, progress_callback=None) -> Dict[str, str]:
    """Run full analytical extraction suite."""
    if progress_callback:
        progress_callback(10, "Generating session title...")
    title = generate_title(transcript)

    if progress_callback:
        progress_callback(30, "Creating executive summary...")
    summary = generate_summary(transcript, progress_callback=progress_callback)

    if progress_callback:
        progress_callback(60, "Extracting action items...")
    action_items = extract_action_items(transcript)

    if progress_callback:
        progress_callback(75, "Extracting key decisions...")
    key_decisions = extract_key_decisions(transcript)

    if progress_callback:
        progress_callback(90, "Identifying open questions...")
    open_questions = extract_questions(transcript)

    return {
        "title": title,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": key_decisions,
        "open_questions": open_questions,
    }
