"""
VISTA AI Video Assistant - Export Engine
Generates downloadable Markdown (.md) and professional PDF (.pdf) reports
using ReportLab with timestamps, summaries, action items, decisions, and transcripts.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
    KeepTogether,
)

def export_as_markdown(data: Dict[str, Any]) -> str:
    """Generate structured Markdown document."""
    title = data.get("title", "Video Intelligence Report")
    source = data.get("source", "N/A")
    duration = data.get("duration", 0)
    mins = int(duration // 60)
    secs = int(duration % 60)
    timestamp_gen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = []
    md.append(f"# 🎬 VISTA Video Intelligence Report: {title}\n")
    md.append(f"- **Generated:** {timestamp_gen}")
    md.append(f"- **Source:** `{source}`")
    md.append(f"- **Duration:** {mins:02d}:{secs:02d}\n")
    md.append("---\n")

    md.append("## 📋 Executive Summary\n")
    md.append(f"{data.get('summary', 'No summary generated.')}\n")
    md.append("---\n")

    md.append("## ✅ Action Items\n")
    md.append(f"{data.get('action_items', 'None identified.')}\n")
    md.append("---\n")

    md.append("## 🔑 Key Decisions\n")
    md.append(f"{data.get('key_decisions', 'None recorded.')}\n")
    md.append("---\n")

    md.append("## ❓ Open Questions & Follow-ups\n")
    md.append(f"{data.get('open_questions', 'None found.')}\n")
    md.append("---\n")

    md.append("## 📝 Timestamped Transcript\n")
    formatted_transcript = data.get("formatted_transcript") or data.get("transcript", "")
    md.append("```text")
    md.append(formatted_transcript)
    md.append("```\n")

    return "\n".join(md)

def export_as_pdf(data: Dict[str, Any], output_path: str) -> str:
    """
    Generate an executive PDF report using ReportLab.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e1e2f"),
        spaceAfter=6,
    )

    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#64748b"),
    )

    h2_style = ParagraphStyle(
        "Heading2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#6d28d9"),
        spaceBefore=14,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )

    transcript_style = ParagraphStyle(
        "TranscriptBody",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569"),
    )

    story = []

    # Title & Metadata
    title = data.get("title", "Video Intelligence Report")
    source = data.get("source", "N/A")
    duration = data.get("duration", 0)
    mins = int(duration // 60)
    secs = int(duration % 60)
    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    story.append(Paragraph(f"VISTA • {title}", title_style))
    story.append(Paragraph(f"Source: {source} &nbsp;|&nbsp; Duration: {mins:02d}:{secs:02d} &nbsp;|&nbsp; Generated: {gen_time}", meta_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#7c3aed"), spaceAfter=12))

    # Helper to add section
    def add_section(header_text: str, content_text: str, is_code: bool = False):
        story.append(Paragraph(header_text, h2_style))
        cleaned = content_text.replace("\n", "<br/>").replace("\t", "&nbsp;&nbsp;")
        target_style = transcript_style if is_code else body_style
        story.append(Paragraph(cleaned, target_style))
        story.append(Spacer(1, 8))

    # Summary
    add_section("📋 Executive Summary", data.get("summary", "No summary generated."))

    # Action Items
    add_section("✅ Action Items", data.get("action_items", "No action items identified."))

    # Key Decisions
    add_section("🔑 Key Decisions", data.get("key_decisions", "No decisions recorded."))

    # Open Questions
    add_section("❓ Open Questions & Follow-ups", data.get("open_questions", "No unresolved questions."))

    # Transcript Section
    story.append(Paragraph("📝 Transcript with Timestamps", h2_style))
    raw_transcript = data.get("formatted_transcript") or data.get("transcript", "")
    
    # Chunk transcript lines so ReportLab doesn't choke on single massive paragraph
    lines = raw_transcript.splitlines()
    batch = []
    for line in lines:
        if line.strip():
            batch.append(line)
        if len(batch) >= 25:
            story.append(Paragraph("<br/>".join(batch), transcript_style))
            story.append(Spacer(1, 4))
            batch = []
    if batch:
        story.append(Paragraph("<br/>".join(batch), transcript_style))

    doc.build(story)
    return output_path
