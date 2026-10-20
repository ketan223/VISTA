import os
import httpx
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent

from modules.research_agent.tools import web_search, scrape_url

load_dotenv()

def is_mistral_available() -> bool:
    """Quick 1-second check to see if Mistral API key is functional and not rate-limited."""
    key = os.getenv("MISTRAL_API_KEY", "").strip()
    if not key:
        return False
    try:
        r = httpx.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "mistral-small-latest", "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1},
            timeout=1.5
        )
        return r.status_code == 200
    except Exception:
        return False

def get_resilient_llm():
    """
    Returns Mistral LLM if the API key is active and healthy.
    Otherwise seamlessly uses local Ollama (qwen2.5:1.5b) configured with a large output context
    (num_predict=4096) to generate comprehensive, publication-grade multi-page research reports.
    """
    from langchain_ollama import ChatOllama
    fallback_llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.25,
        num_predict=4096,
        num_ctx=8192,
    )

    if is_mistral_available():
        try:
            from langchain_mistralai import ChatMistralAI
            return ChatMistralAI(
                model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
                api_key=os.getenv("MISTRAL_API_KEY"),
                temperature=0.2,
                max_retries=1,
                max_tokens=4096,
            )
        except Exception:
            pass

    return fallback_llm

# Shared LLM instance
llm = get_resilient_llm()

# 1st Agent: Search Agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search]
    )

# 2nd Agent: Reader Agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )

# 3rd Chain: Writer Chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a distinguished Senior Research Fellow and Principal Technical Author writing a comprehensive, formal research paper (minimum 1,200 to 1,600 words, targeting 3+ full A4 pages).
Your objective is to produce an exhaustive, publication-grade academic and industrial dossier.
Do NOT write brief summaries, superficial lists, or generic placeholder text.
Write in formal, authoritative research prose with deep technical specificity, conceptual breakdowns, historical context, empirical metrics, and clear trade-off analyses.
Ensure every numbered section is thoroughly elaborated with substantive paragraphs."""),
    ("human", """Write an exhaustive, publication-grade research paper on the topic below based on the gathered research.

TOPIC: {topic}

RESEARCH GATHERED FROM WEB & DEEP DOM EXTRACTION:
{research}

YOU MUST STRUCTURE YOUR PAPER ACCORDING TO THIS COMPREHENSIVE 8-SECTION SPECIFICATION:

# [FORMAL RESEARCH PAPER TITLE]

## Abstract & Executive Summary
Write a rigorous, 180-250 word formal abstract covering: (1) Background and core motivation, (2) Problem statement and operational bottlenecks, (3) Investigation methodology and discovery scope, (4) Primary technical findings and quantified benchmarks, (5) Strategic implications for industry and academia. Include 4-6 Keywords.

## 1. Introduction & Contextual Background
Write 3-4 comprehensive paragraphs covering the historical evolution of this field, why this topic is critical in 2025/2026, the underlying theoretical principles, and the specific research questions investigated in this paper.

## 2. Theoretical Foundations & State-of-the-Art Review
Examine existing paradigms and prior approaches. Detail what existing technologies, frameworks, or market standards achieve, where current industry solutions fall short, and the paradigm shift driving current developments.

## 3. Autonomous Multi-Agent Methodology & Scope
Detail the multi-agent autonomous investigation methodology: live multi-index retrieval (Tavily and DuckDuckGo engines), semantic DOM tree filtering, content distillation, and adversarial validation loops.

## 4. In-Depth Technical Findings & Architectural Breakdown
Provide an exhaustive, multi-faceted technical breakdown with at least 3 detailed subsections:
- 4.1 Core Architecture & Underlying Mechanisms
- 4.2 Empirical Benchmarks, Quantitative Data & Metrics
- 4.3 Practical Deployments & Field Case Studies
Write thorough, substantive paragraphs for each subsection with concrete evidence and figures.

## 5. Comparative Evaluation & Trade-off Matrix
Construct an extensive comparative analysis. Contrast traditional vs modern approaches, outlining trade-offs in accuracy, latency, computational overhead, economic cost, and maintainability. Include a structured comparison table in markdown.

## 6. Critical Analysis, Structural Limitations & Risk Factors
Provide a sharp, objective critique: What are the engineering bottlenecks, security vulnerabilities, edge-case failures, ethical concerns, or integration barriers?

## 7. Actionable Recommendations & Implementation Roadmap
Provide concrete, step-by-step guidance for engineering teams and decision-makers:
- Phase 1: Near-term adoption and architectural best practices
- Phase 2: Production hardening and evaluation telemetry
- Phase 3: Long-term strategic governance

## 8. Conclusion & Future Scientific Trajectory
Synthesize the primary findings, project the 3-5 year trajectory of this technology, and deliver the final scientific verdict.

## References & Documented Sources
Provide a clean numbered list of all authentic sources, academic papers, and canonical URLs retrieved during the research process with descriptive titles and contextual relevance.

Write authoritatively and deeply. Ensure the content easily spans multiple full pages with zero superficial filler."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()

# 4th Chain: Critic Chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
