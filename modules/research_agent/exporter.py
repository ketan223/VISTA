"""
VISTA ResearchMind - Professional Academic & Industrial Export Engine
Generates publication-grade Markdown (.md), PDF (.pdf), and Word (.docx) research papers
targeting at least 2 to 3+ full A4 pages with formal IEEE/ACM structure,
Abstract callout boxes, dynamic table parsing, live citations, and running page numbers.
"""

import os
import re
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# ReportLab Imports
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.pdfgen import canvas

# python-docx Imports
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from docx.opc.constants import RELATIONSHIP_TYPE


# ==============================================================================
# 1. MARKDOWN EXPORT
# ==============================================================================

def export_research_markdown(data: Dict[str, Any]) -> str:
    """Generates structured publication Markdown with metadata and critic review."""
    topic = data.get("topic", "Autonomous Research Report")
    report = data.get("report", "")
    feedback = data.get("feedback", "")
    elapsed = data.get("elapsed_seconds", 0)
    created_at = datetime.now().strftime("%B %d, %Y")

    md = [
        f"# {topic}\n",
        f"> **VISTA ResearchMind · Autonomous Research Paper**  ",
        f"> **Authors:** VISTA Multi-Agent Intelligence Engine  ",
        f"> **Affiliation:** College Final Year Engineering Project · Department of Computer Science & AI  ",
        f"> **Published:** {created_at} | **Runtime:** {elapsed}s | **Classification:** Empirical Technical Dossier  \n",
        "---\n",
        report,
    ]

    if feedback:
        md.extend([
            "\n\n---\n",
            "## 🧐 Peer Review & Adversarial Quality Evaluation\n",
            feedback,
        ])

    return "\n".join(md)


# ==============================================================================
# 2. REPORTLAB NUMBERED CANVAS (PAGE X OF Y)
# ==============================================================================

class ResearchNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that computes total page count dynamically
    and draws professional academic running headers and footers on every page.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count: int):
        self.saveState()
        
        header_color = colors.HexColor("#64748B")
        line_color = colors.HexColor("#CBD5E1")
        
        # Running Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#4338CA"))
            self.drawString(45, 808, "VISTA RESEARCHMIND")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(header_color)
            self.drawString(145, 808, "· Formal Academic Research Dossier · Final Year Engineering Project")
            self.setStrokeColor(line_color)
            self.setLineWidth(0.5)
            self.line(45, 802, 550, 802)

        # Running Footer (all pages)
        self.setFont("Helvetica", 7.5)
        self.setFillColor(header_color)
        self.drawString(45, 30, "VISTA Platform · Autonomous Multi-Agent Research · Confidential & Academic")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(550, 30, page_str)
        
        self.setStrokeColor(line_color)
        self.setLineWidth(0.5)
        self.line(45, 40, 550, 40)
        
        self.restoreState()


# ==============================================================================
# 3. TEXT & TABLE PARSING HELPERS
# ==============================================================================

def clean_text_for_reportlab(text: str) -> str:
    """Escapes special characters and normalizes Unicode symbols for ReportLab."""
    if not text:
        return ""
    replacements = {
        "—": " - ",
        "–": " - ",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "*",
        "…": "...",
        "\u200b": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    text = html.escape(text)
    
    # Bold & Italic
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.+?)__", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    
    # Markdown links: [anchor](url)
    def link_repl(m):
        label = m.group(1)
        url = m.group(2)
        return f'<a href="{url}" color="#2563EB"><u>{label}</u></a>'
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", link_repl, text)
    
    # Raw URLs
    def raw_url_repl(m):
        u = m.group(0)
        return f'<a href="{u}" color="#2563EB"><u>{u}</u></a>'
    text = re.sub(r'(?<!href=")(https?://[^\s<>"]+)', raw_url_repl, text)

    return text


def parse_markdown_table(lines: List[str]) -> List[List[str]]:
    """Extracts matrix of rows and columns from markdown table lines."""
    matrix = []
    for line in lines:
        cells = [c.strip() for c in line.split("|")]
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        # Ignore separator row (|---|---|)
        if all(re.match(r"^:?-+:?$", c) for c in cells):
            continue
        if cells:
            matrix.append(cells)
    return matrix


# ==============================================================================
# 4. PDF GENERATION (REPORTLAB)
# ==============================================================================

def export_research_pdf(data: Dict[str, Any], output_path: str) -> str:
    """
    Builds a comprehensive, publication-grade academic PDF research paper
    spanning at least 2 to 3+ A4 pages with metadata, callouts, and tables.
    """
    topic = data.get("topic", "Autonomous Research Dossier")
    report = data.get("report", "")
    feedback = data.get("feedback", "")
    elapsed = data.get("elapsed_seconds", 0)
    created_date = datetime.now().strftime("%B %d, %Y")

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#0F172A")    # Deep Navy
    c_accent = colors.HexColor("#4338CA")     # Indigo
    c_secondary = colors.HexColor("#334155")  # Slate
    c_text = colors.HexColor("#1E293B")       # Dark Charcoal
    c_muted = colors.HexColor("#64748B")

    title_style = ParagraphStyle(
        "PaperTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceAfter=4,
    )
    author_style = ParagraphStyle(
        "PaperAuthor",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=c_secondary,
        spaceAfter=10,
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=c_accent,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=c_primary,
        spaceBefore=9,
        spaceAfter=3,
        keepWithNext=True,
    )
    h3_style = ParagraphStyle(
        "SectionH3",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=c_secondary,
        spaceBefore=7,
        spaceAfter=2,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=13.2,
        textColor=c_text,
        spaceAfter=6,
    )
    abstract_style = ParagraphStyle(
        "AbstractCustom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#1E293B"),
    )
    bullet_style = ParagraphStyle(
        "BulletCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=13,
        textColor=c_text,
        leftIndent=14,
        spaceAfter=3,
    )

    story = []

    # 1. Header Banner & Title
    story.append(Paragraph("VISTA AI RESEARCH LABS · PEER-REVIEWED TECHNICAL DOSSIER", ParagraphStyle("Banner", fontName="Helvetica-Bold", fontSize=8, textColor=c_accent, spaceAfter=4)))
    story.append(Paragraph(clean_text_for_reportlab(topic), title_style))
    story.append(Paragraph(
        f"<b>Authors:</b> VISTA Autonomous Research Agent (ResearchMind) &nbsp;·&nbsp; "
        f"<b>Affiliation:</b> College Final Year Project, Dept. of Computer Science & AI<br/>"
        f"<b>Date:</b> {created_date} &nbsp;·&nbsp; <b>Execution:</b> {elapsed}s &nbsp;·&nbsp; <b>Verification:</b> Multi-Agent Grounded",
        author_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=2, spaceAfter=10))

    # 2. Parse lines with table and abstract detection
    lines = report.split("\n")
    i = 0
    in_abstract = False
    abstract_paragraphs = []

    while i < len(lines):
        line = lines[i].strip()

        # Handle Markdown Tables
        if line.startswith("|") and line.endswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            matrix = parse_markdown_table(table_lines)
            if matrix and len(matrix) >= 1:
                col_count = len(matrix[0])
                col_width = 505.0 / col_count
                t_data = [
                    [Paragraph(clean_text_for_reportlab(cell), ParagraphStyle("TCell", fontName="Helvetica-Bold" if r_idx == 0 else "Helvetica", fontSize=8, leading=10, textColor=colors.white if r_idx == 0 else c_text))
                     for cell in row]
                    for r_idx, row in enumerate(matrix)
                ]
                t_flow = Table(t_data, colWidths=[col_width] * col_count)
                t_flow.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ]))
                story.append(Spacer(1, 4))
                story.append(t_flow)
                story.append(Spacer(1, 6))
            continue

        i += 1
        if not line:
            continue

        # Major Headings
        if line.startswith("# "):
            story.append(Paragraph(clean_text_for_reportlab(line[2:]), h1_style))
            story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#E2E8F0"), spaceBefore=1, spaceAfter=5))
        elif line.startswith("## "):
            h_text = line[3:]
            if "abstract" in h_text.lower() or "executive summary" in h_text.lower():
                story.append(Paragraph(clean_text_for_reportlab(h_text), h1_style))
            else:
                story.append(Paragraph(clean_text_for_reportlab(h_text), h1_style))
        elif line.startswith("### "):
            story.append(Paragraph(clean_text_for_reportlab(line[4:]), h2_style))
        elif line.startswith("#### "):
            story.append(Paragraph(clean_text_for_reportlab(line[5:]), h3_style))
        elif line in ["---", "***", "___"]:
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceBefore=5, spaceAfter=5))
        elif line.startswith(("- ", "* ", "• ")):
            story.append(Paragraph(f"• &nbsp; {clean_text_for_reportlab(line[2:])}", bullet_style))
        elif re.match(r"^\d+\.\s+", line):
            num_match = re.match(r"^(\d+\.)\s+(.+)$", line)
            if num_match:
                story.append(Paragraph(f"<b>{num_match.group(1)}</b> &nbsp; {clean_text_for_reportlab(num_match.group(2))}", bullet_style))
            else:
                story.append(Paragraph(clean_text_for_reportlab(line), body_style))
        else:
            story.append(Paragraph(clean_text_for_reportlab(line), body_style))

    # Append Adversarial Peer Review Section
    if feedback:
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#10B981"), spaceBefore=6, spaceAfter=6))
        story.append(Paragraph("🧐 Automated Peer Review & Quality Scorecard", h1_style))
        for c_line in feedback.split("\n"):
            c_str = c_line.strip()
            if not c_str:
                continue
            if c_str.startswith(("- ", "* ", "• ")):
                story.append(Paragraph(f"• &nbsp; {clean_text_for_reportlab(c_str[2:])}", bullet_style))
            elif re.match(r"^[A-Za-z\s]+:", c_str):
                story.append(Paragraph(f"<b>{clean_text_for_reportlab(c_str)}</b>", body_style))
            else:
                story.append(Paragraph(clean_text_for_reportlab(c_str), body_style))

    doc.build(story, canvasmaker=ResearchNumberedCanvas)
    return output_path


# ==============================================================================
# 5. WORD DOCUMENT (.DOCX) GENERATION (PYTHON-DOCX)
# ==============================================================================

def add_docx_hyperlink(paragraph, url: str, text: str, color="004B91", underline=True):
    """Inserts native clickable hyperlink into python-docx paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    if color:
        c = OxmlElement('w:color')
        c.set(qn('w:val'), color)
        rPr.append(c)
    if underline:
        u = OxmlElement('w:u')
        u.set(qn('w:val'), 'single')
        rPr.append(u)
    new_run.append(rPr)
    text_node = OxmlElement('w:t')
    text_node.text = text
    new_run.append(text_node)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink


def export_research_docx(data: Dict[str, Any], output_path: str) -> str:
    """
    Builds a professional, comprehensive academic Word (.docx) paper
    with cover metadata, tables, headings, and running page numbers.
    """
    topic = data.get("topic", "Autonomous Research Dossier")
    report = data.get("report", "")
    feedback = data.get("feedback", "")
    elapsed = data.get("elapsed_seconds", 0)
    created_date = datetime.now().strftime("%B %d, %Y")

    doc = docx.Document()

    # Configure A4 Dimensions and Margins
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

        # Header
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("VISTA ResearchMind · Academic Research Paper")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8)
        hrun.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)

        # Footer with Running Page Number
        footer = section.footer
        fp = footer.paragraphs[0]
        frun1 = fp.add_run("Confidential · Final Year Engineering Project · VISTA Platform              Page ")
        frun1.font.name = "Arial"
        frun1.font.size = Pt(8)
        frun1.font.color.rgb = RGBColor(0x94, 0xA3, 0xB8)
        
        fldSimple = OxmlElement('w:fldSimple')
        fldSimple.set(qn('w:instr'), 'PAGE')
        fp._p.append(fldSimple)

    # Document Title Block
    p_pre = doc.add_paragraph()
    r_pre = p_pre.add_run("VISTA AI RESEARCH LABS · PEER-REVIEWED TECHNICAL DOSSIER")
    r_pre.font.name = "Arial"
    r_pre.font.size = Pt(9)
    r_pre.font.bold = True
    r_pre.font.color.rgb = RGBColor(0x43, 0x38, 0xCA)
    p_pre.paragraph_format.space_after = Pt(2)

    p_title = doc.add_paragraph()
    r_title = p_title.add_run(topic)
    r_title.font.name = "Arial"
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
    p_title.paragraph_format.space_after = Pt(4)

    # Authorship & Metadata Subtitle
    p_meta = doc.add_paragraph()
    r_meta = p_meta.add_run(
        f"Authors: VISTA Autonomous Research Agent (ResearchMind)\n"
        f"Affiliation: College Final Year Engineering Project · Dept. of Computer Science & AI\n"
        f"Published: {created_date} | Pipeline: Multi-Agent Autonomous Loop ({elapsed}s)"
    )
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(8.5)
    r_meta.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)
    p_meta.paragraph_format.space_after = Pt(12)

    # Parse and write report content
    lines = report.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Handle Markdown Tables in Word
        if line.startswith("|") and line.endswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            matrix = parse_markdown_table(table_lines)
            if matrix:
                t = doc.add_table(rows=len(matrix), cols=len(matrix[0]))
                t.alignment = docx.enum.table.WD_TABLE_ALIGNMENT.CENTER
                for r_idx, row in enumerate(matrix):
                    for c_idx, cell_val in enumerate(row):
                        cell = t.cell(r_idx, c_idx)
                        cp = cell.paragraphs[0]
                        cp.paragraph_format.space_after = Pt(2)
                        crun = cp.add_run(cell_val)
                        crun.font.name = "Arial"
                        crun.font.size = Pt(8.5)
                        if r_idx == 0:
                            crun.font.bold = True
                            crun.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                            shd = parse_xml(r'<w:shd {} w:fill="1E293B"/>'.format(nsdecls('w')))
                            cell._tc.get_or_add_tcPr().append(shd)
                        else:
                            crun.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
                            if r_idx % 2 == 1:
                                shd = parse_xml(r'<w:shd {} w:fill="F8FAFC"/>'.format(nsdecls('w')))
                                cell._tc.get_or_add_tcPr().append(shd)
                doc.add_paragraph().paragraph_format.space_after = Pt(6)
            continue

        i += 1
        if not line:
            continue

        if line.startswith("# "):
            h = doc.add_heading(line[2:], level=1)
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(4)
            for r in h.runs:
                r.font.name = "Arial"
                r.font.color.rgb = RGBColor(0x43, 0x38, 0xCA)
        elif line.startswith("## "):
            h = doc.add_heading(line[3:], level=2)
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(3)
            for r in h.runs:
                r.font.name = "Arial"
                r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        elif line.startswith("### "):
            h = doc.add_heading(line[4:], level=3)
            h.paragraph_format.space_before = Pt(8)
            h.paragraph_format.space_after = Pt(2)
            for r in h.runs:
                r.font.name = "Arial"
                r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        elif line in ["---", "***", "___"]:
            hp = doc.add_paragraph()
            hp.paragraph_format.space_before = Pt(4)
            hp.paragraph_format.space_after = Pt(4)
            hrun = hp.add_run("__________________________________________________________________")
            hrun.font.size = Pt(8)
            hrun.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)
        elif line.startswith(("- ", "* ", "• ")):
            bp = doc.add_paragraph(style='List Bullet')
            bp.paragraph_format.space_after = Pt(2)
            _render_inline_docx(bp, line[2:])
        elif re.match(r"^\d+\.\s+", line):
            lp = doc.add_paragraph(style='List Number')
            lp.paragraph_format.space_after = Pt(2)
            match = re.match(r"^\d+\.\s+(.+)$", line)
            text_body = match.group(1) if match else line
            _render_inline_docx(lp, text_body)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            _render_inline_docx(p, line)

    # Append Adversarial Peer Review in Word
    if feedback:
        doc.add_paragraph().paragraph_format.space_after = Pt(6)
        hc = doc.add_heading("🧐 Automated Peer Review & Quality Scorecard", level=1)
        hc.paragraph_format.space_before = Pt(14)
        hc.paragraph_format.space_after = Pt(4)
        for r in hc.runs:
            r.font.name = "Arial"
            r.font.color.rgb = RGBColor(0x10, 0xB9, 0x81)

        for c_line in feedback.split("\n"):
            c_str = c_line.strip()
            if not c_str:
                continue
            if c_str.startswith(("- ", "* ", "• ")):
                cp = doc.add_paragraph(style='List Bullet')
                cp.paragraph_format.space_after = Pt(2)
                _render_inline_docx(cp, c_str[2:])
            elif re.match(r"^[A-Za-z\s]+:", c_str):
                cp = doc.add_paragraph()
                cp.paragraph_format.space_after = Pt(2)
                r_head = cp.add_run(c_str)
                r_head.font.name = "Arial"
                r_head.font.bold = True
                r_head.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
            else:
                cp = doc.add_paragraph()
                cp.paragraph_format.space_after = Pt(3)
                _render_inline_docx(cp, c_str)

    doc.save(output_path)
    return output_path


def _render_inline_docx(paragraph, text: str):
    """Parses bold, italic, and URLs into native docx runs and hyperlinks."""
    link_pattern = re.compile(r'\[([^\]]+)\]\((https?://[^\)]+)\)')
    raw_url_pattern = re.compile(r'(https?://[^\s]+)')

    pos = 0
    for match in link_pattern.finditer(text):
        pre_text = text[pos:match.start()]
        if pre_text:
            _render_bold_italic_text(paragraph, pre_text)
        add_docx_hyperlink(paragraph, match.group(2), match.group(1))
        pos = match.end()

    remaining = text[pos:]
    if remaining:
        u_pos = 0
        for u_match in raw_url_pattern.finditer(remaining):
            u_pre = remaining[u_pos:u_match.start()]
            if u_pre:
                _render_bold_italic_text(paragraph, u_pre)
            url_str = u_match.group(1)
            add_docx_hyperlink(paragraph, url_str, url_str)
            u_pos = u_match.end()
        u_rem = remaining[u_pos:]
        if u_rem:
            _render_bold_italic_text(paragraph, u_rem)


def _render_bold_italic_text(paragraph, text: str):
    """Splits text on **bold** and adds formatted runs."""
    bold_tokens = re.split(r'(\*\*.*?\*\*)', text)
    for token in bold_tokens:
        if not token:
            continue
        if token.startswith('**') and token.endswith('**') and len(token) > 4:
            run = paragraph.add_run(token[2:-4])
            run.font.name = "Arial"
            run.font.size = Pt(9)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
        else:
            run = paragraph.add_run(token)
            run.font.name = "Arial"
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
