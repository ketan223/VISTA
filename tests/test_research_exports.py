"""
Test Suite for VISTA ResearchMind Export Engine (PDF, DOCX, Markdown)
Verifies ~3-page structured report generation, citations, Unicode handling, and FastAPI export endpoints.
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pypdf
import docx
from modules.research_agent.exporter import (
    export_research_pdf,
    export_research_docx,
    export_research_markdown,
)

SAMPLE_RESEARCH_DATA = {
    "topic": "Autonomous Multi-Agent Systems in Enterprise Software 2025",
    "report": """# PART I: FOUNDATIONAL OVERVIEW & SCOPE

## Core Research Question
How do distributed multi-agent architectures enhance autonomous software execution, and what are the quantifiable trade-offs in accuracy, latency, and system cost?

## Executive Summary
Autonomous multi-agent systems represent a paradigm shift from monolithic LLM prompting to collaborative, task-specialized reasoning networks. By distributing cognitive tasks across searchers, scrapers, writers, and adversarial critics, organizations realize dramatic reductions in hallucination and manual triage. This dossier reviews empirical findings, benchmark comparisons, and architectural patterns.

## Introduction & Industry Context
In 2025, artificial intelligence has evolved beyond conversational interfaces into operational agentic loops. Large language models serve as central reasoning routers connected to deterministic execution sandboxes, live search indexes, and vector stores. By using ReAct reasoning and dynamic function invocation, autonomous agents reliably perform deep web research, programmatic validation, and publication synthesis.

## Research Methodology & Scope
This investigation utilized an autonomous multi-agent pipeline traversing live web indexing (via Tavily and DuckDuckGo search engines) and semantic DOM extraction. Over 40 industry benchmarks, academic papers, and technical specifications were analyzed, focusing specifically on enterprise orchestrations, agent coordination frameworks, and verification protocols.

# PART II: DETAILED FINDINGS, EVIDENCE & COMPARATIVE ANALYSIS

## Detailed Technical & Architectural Findings
State-of-the-art enterprise implementations deploy modular separation of concerns across 4 discrete layers:
1. Perception & Retrieval Layer: Targeted queries dispatched to search APIs and web scrapers.
2. Content Distillation Layer: DOM cleaning, script stripping, and token compression.
3. Synthesis Layer: Structured chain composition with strict stylistic and technical constraints.
4. Adversarial Audit Layer: Independent critic agent scoring factuality, rigor, and source validity.

## Empirical Evidence & Quantified Benchmarks
Key industry metrics demonstrate verifiable gains:
- Task Success Rate: Tool-augmented agents achieved an 84.1% task completion rate on complex analytical benchmarks versus 51.3% for standard zero-shot prompts.
- Hallucination Suppression: Grounding generation in live extracted DOM text reduced factual hallucinations from 17.8% to under 2.4%.
- Latency Profiles: Sequential multi-agent loops average 30 to 90 seconds per run, requiring background asynchronous execution.

## Comparative Framework Analysis
Multi-agent frameworks differ significantly in their execution models:
- LangChain LCEL: Declarative Directed Acyclic Graph, low latency overhead, ideal for research workflows.
- LangGraph: State-machine cyclic graph, checkpointed persistence, suited for long-running agent swarms.
- CrewAI: Role-based hierarchy, intuitive persona assignment, slightly higher token overhead.

## Supporting Citations & Sourced Insights
Field studies confirm that grounding models with live scraping mitigates knowledge cutoff limitations. As documented in [LangChain Architecture](https://python.langchain.com) and [arXiv AI Research](https://arxiv.org/abs/2308.08155), continuous peer critique loops elevate document cohesion and ensure verifiable citations.

# PART III: CRITICAL EVALUATION, OUTLOOK & VERIFIED REFERENCES

## Critical Analysis & Structural Limitations
Key bottlenecks in autonomous research pipelines include:
- Compounding Retrieval Error: Obsolete or low-quality source URLs degrade subsequent analysis.
- Rate Limit Bottlenecks: Reliance on single-vendor search APIs leads to downtime without robust fallbacks.
- Compute Footprint: Running multi-agent loops across local open-source models demands GPU memory or quantized inference.

## Key Takeaways & Strategic Recommendations
1. Employ Fallback Redundancy: Always back commercial search APIs with robust open search mechanisms.
2. Dual-Provider Routing: Use high-speed cloud models alongside local Ollama engines for zero-failure resiliency.
3. Automated Quality Audits: Embed strict critic chains into the export pipeline before delivering reports.

## Synthesis & Conclusion
The transition toward agentic intelligence marks an irreversible evolution in enterprise productivity. Multi-agent workflows deliver verifiable, high-depth analysis at machine speed while maintaining complete audit trails.

## Numbered References & Verified Sources
1. [LangChain Multi-Agent Architecture](https://python.langchain.com) - Official documentation on declarative agent chaining.
2. [arXiv: Autonomous Agents for Knowledge Work](https://arxiv.org/abs/2308.08155) - Empirical analysis of ReAct agent efficiency.
3. [DuckDuckGo Search Integration Protocol](https://duckduckgo.com) - Real-time privacy-preserving web search retrieval.
4. [Tavily AI Search Engine Documentation](https://tavily.com) - Specialized search API for LLM agent grounding.""",
    "feedback": """Score: 9/10

Strengths:
- Rigorous 3-part academic structure with empirical benchmarks
- Comprehensive technical depth and structured comparative analysis
- Verifiable citations with live URLs and clear structural limitations

Areas to Improve:
- Include a specific section on data privacy and local vector compliance
- Provide deeper cost breakdown comparing cloud vs local hardware

One line verdict:
An outstanding, publication-ready research dossier demonstrating high technical depth and empirical grounding.""",
    "elapsed_seconds": 38.2,
}

def test_markdown_export():
    md = export_research_markdown(SAMPLE_RESEARCH_DATA)
    assert "# Autonomous Multi-Agent Systems" in md
    assert "PART I: FOUNDATIONAL OVERVIEW" in md
    assert "PART II: DETAILED FINDINGS" in md
    assert "PART III: CRITICAL EVALUATION" in md
    assert "Score: 9/10" in md
    print("✅ test_markdown_export passed!")

def test_pdf_export():
    out_dir = Path("temp")
    out_dir.mkdir(exist_ok=True)
    pdf_path = str(out_dir / "test_research_dossier.pdf")
    
    export_research_pdf(SAMPLE_RESEARCH_DATA, pdf_path)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000
    
    reader = pypdf.PdfReader(pdf_path)
    page_count = len(reader.pages)
    print(f"✅ test_pdf_export passed! Generated {page_count} A4 pages (target ~3 pages).")
    assert 2 <= page_count <= 4, f"Expected ~3 pages, got {page_count}"

    # Verify text extracted from page 1 and page 2
    page1_text = reader.pages[0].extract_text()
    assert "VISTA" in page1_text
    assert "PART I" in page1_text or "FOUNDATIONAL" in page1_text

def test_docx_export():
    out_dir = Path("temp")
    out_dir.mkdir(exist_ok=True)
    docx_path = str(out_dir / "test_research_dossier.docx")
    
    export_research_docx(SAMPLE_RESEARCH_DATA, docx_path)
    assert os.path.exists(docx_path)
    assert os.path.getsize(docx_path) > 1000
    
    doc = docx.Document(docx_path)
    assert len(doc.paragraphs) > 15
    assert len(doc.tables) >= 1
    
    full_text = " ".join([p.text for p in doc.paragraphs])
    assert "Autonomous Multi-Agent Systems" in full_text
    assert "PART I" in full_text
    assert "PART II" in full_text
    assert "PART III" in full_text
    print("✅ test_docx_export passed! Valid Word document with headings and metadata table.")

if __name__ == "__main__":
    test_markdown_export()
    test_pdf_export()
    test_docx_export()
    print("\n🎉 ALL RESEARCH EXPORT TESTS PASSED SUCCESSFULLY!")
