"""
VISTA AI Chat Assistant - Conversational Engine
Integrates Google Gemini 3.8 Flash with local Ollama fallback,
multi-persona system prompts, and multi-turn message history.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Generator
from dotenv import load_dotenv

load_dotenv()

PERSONAS: Dict[str, Dict[str, str]] = {
    "general": {
        "id": "general",
        "name": "VISTA Intelligence Partner",
        "role": "General Purpose Copilot",
        "icon": "Sparkles",
        "system_prompt": (
            "You are VISTA Intelligence Partner, a state-of-the-art conversational AI developed for the VISTA platform. "
            "You are sharp, helpful, intellectually rigorous, and articulate. Provide thorough, well-structured responses "
            "formatted in clean GitHub Markdown with code blocks, bullet points, and clear conceptual explanations."
        ),
    },
    "coder": {
        "id": "coder",
        "name": "Principal Software Architect",
        "role": "Code Engineering & Architecture",
        "icon": "Code2",
        "system_prompt": (
            "You are a Principal Software Architect and Senior Systems Engineer. You write clean, robust, production-grade "
            "code with thorough error handling, typing, and modern best practices. Analyze architectural trade-offs, identify edge cases, "
            "and suggest clean refactorings."
        ),
    },
    "researcher": {
        "id": "researcher",
        "name": "Senior Research Fellow",
        "role": "Academic & Technical Analysis",
        "icon": "Microscope",
        "system_prompt": (
            "You are a Senior AI Research Fellow. You approach every question with scientific rigor, theoretical foundations, "
            "empirical benchmarks, and objective analytical clarity. Use formal academic prose and cite mechanisms where relevant."
        ),
    },
    "creative": {
        "id": "creative",
        "name": "Creative Product Strategist",
        "role": "Ideation & Product Vision",
        "icon": "Zap",
        "system_prompt": (
            "You are an Executive Product Strategist and Creative Director. You frame problems with compelling narratives, "
            "differentiated positioning, intuitive user experience design, and high-impact messaging."
        ),
    },
    "tutor": {
        "id": "tutor",
        "name": "Socratic Mentor",
        "role": "Step-by-Step Learning",
        "icon": "GraduationCap",
        "system_prompt": (
            "You are a dedicated Socratic Tutor and Mentor. You explain complex technical concepts using intuitive analogies, "
            "break problems down into logical first principles, and guide the student with thoughtful explanations."
        ),
    },
}

def get_gemini_model(system_prompt: str, temperature: float = 0.7):
    """Initializes Google Gemini model configured with REST transport for optimal latency."""
    import google.generativeai as genai
    
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set.")
    
    genai.configure(api_key=api_key, transport="rest")
    model_name = os.getenv("GEMINI_MODEL", "models/gemini-3.8-flash")
    
    return genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
        generation_config={"temperature": temperature, "max_output_tokens": 3000}
    )

def format_gemini_contents(messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    contents = []
    for m in messages:
        role = "user" if m.get("role") == "user" else "model"
        contents.append({"role": role, "parts": [m.get("content", "")]})
    return contents

def call_gemini_chat(messages: List[Dict[str, str]], system_prompt: str, temperature: float = 0.7) -> str:
    """Invokes Google Gemini with REST transport."""
    model = get_gemini_model(system_prompt, temperature)
    contents = format_gemini_contents(messages)
    response = model.generate_content(contents)
    return response.text.strip()

def stream_gemini_chat(messages: List[Dict[str, str]], system_prompt: str, temperature: float = 0.7) -> Generator[str, None, None]:
    """Streams Google Gemini token chunks in real time."""
    model = get_gemini_model(system_prompt, temperature)
    contents = format_gemini_contents(messages)
    response = model.generate_content(contents, stream=True)
    for chunk in response:
        if chunk.text:
            yield chunk.text

def stream_ollama_chat(messages: List[Dict[str, str]], system_prompt: str, temperature: float = 0.7) -> Generator[str, None, None]:
    """Local fallback streaming using Ollama."""
    from langchain_ollama import ChatOllama
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=temperature,
        num_predict=2500,
    )
    
    langchain_msgs = [SystemMessage(content=system_prompt)]
    for m in messages:
        if m.get("role") == "user":
            langchain_msgs.append(HumanMessage(content=m.get("content", "")))
        else:
            langchain_msgs.append(AIMessage(content=m.get("content", "")))
            
    for chunk in llm.stream(langchain_msgs):
        if chunk.content:
            yield chunk.content

def call_ollama_chat(messages: List[Dict[str, str]], system_prompt: str, temperature: float = 0.7) -> str:
    """Local fallback using Ollama (qwen2.5:1.5b)."""
    full_text = []
    for token in stream_ollama_chat(messages, system_prompt, temperature):
        full_text.append(token)
    return "".join(full_text).strip()

def generate_chat_response(
    messages: List[Dict[str, str]],
    persona_id: str = "general",
    temperature: float = 0.7
) -> Dict[str, Any]:
    """Generates standard complete response."""
    persona = PERSONAS.get(persona_id, PERSONAS["general"])
    system_prompt = persona["system_prompt"]
    
    t0 = time.time()
    active_engine = "Google Gemini 3.8 Flash"
    
    try:
        reply_text = call_gemini_chat(messages, system_prompt, temperature)
    except Exception as e_gemini:
        print(f"Gemini chat unavailable ({e_gemini}), falling back to local Ollama...")
        try:
            active_engine = f"Local Ollama ({os.getenv('OLLAMA_MODEL', 'qwen2.5:1.5b')})"
            reply_text = call_ollama_chat(messages, system_prompt, temperature)
        except Exception as e_ollama:
            reply_text = f"I encountered an issue processing your request: {str(e_ollama)}"
            active_engine = "System Error"

    elapsed = round(time.time() - t0, 2)
    return {
        "reply": reply_text,
        "engine": active_engine,
        "persona": persona["name"],
        "elapsed_seconds": elapsed,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }

def generate_chat_stream(
    messages: List[Dict[str, str]],
    persona_id: str = "general",
    temperature: float = 0.7
) -> Generator[str, None, None]:
    """
    Yields Server-Sent Events (SSE) in real-time as tokens are generated.
    SSE format: data: {"type": "start"|"chunk"|"done"|"error", ...}\n\n
    """
    persona = PERSONAS.get(persona_id, PERSONAS["general"])
    system_prompt = persona["system_prompt"]
    engine_name = "Google Gemini 3.8 Flash"

    # Send initial metadata
    yield f"data: {json.dumps({'type': 'start', 'engine': engine_name, 'persona': persona['name']})}\n\n"

    try:
        for chunk in stream_gemini_chat(messages, system_prompt, temperature):
            yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"
    except Exception as e_gemini:
        print(f"Gemini stream failed ({e_gemini}), falling back to local Ollama stream...")
        engine_name = f"Local Ollama ({os.getenv('OLLAMA_MODEL', 'qwen2.5:1.5b')})"
        yield f"data: {json.dumps({'type': 'switch', 'engine': engine_name})}\n\n"
        try:
            for chunk in stream_ollama_chat(messages, system_prompt, temperature):
                yield f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n"
        except Exception as e_ollama:
            yield f"data: {json.dumps({'type': 'error', 'text': f'AI Service Error: {str(e_ollama)}'})}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"
