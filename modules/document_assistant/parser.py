"""
VISTA Document Assistant - Document Ingestion & Parser
Extracts clean semantic text from PDF, DOCX, and TXT files with page-level metadata.
"""

from pathlib import Path
from typing import List, Dict, Any

def extract_text_from_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Extracts text page-by-page from a PDF file using pypdf."""
    import pypdf
    pages_data = []
    reader = pypdf.PdfReader(file_path)
    filename = Path(file_path).name

    for idx, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        clean_text = " ".join(text.split())
        if clean_text:
            pages_data.append({
                "page": idx + 1,
                "text": clean_text,
                "source": filename,
            })
    return pages_data

def extract_text_from_docx(file_path: str) -> List[Dict[str, Any]]:
    """Extracts paragraphs and tables from a Word (.docx) document."""
    import docx
    doc = docx.Document(file_path)
    filename = Path(file_path).name
    text_blocks = []

    for p in doc.paragraphs:
        t = p.text.strip()
        if t:
            text_blocks.append(t)

    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
            if row_text:
                text_blocks.append(row_text)

    combined = "\n\n".join(text_blocks)
    return [{
        "page": 1,
        "text": combined,
        "source": filename,
    }]

def extract_text_from_txt(file_path: str) -> List[Dict[str, Any]]:
    """Extracts text from a plain text file."""
    filename = Path(file_path).name
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    return [{
        "page": 1,
        "text": " ".join(content.split()),
        "source": filename,
    }]

def parse_document(file_path: str) -> List[Dict[str, Any]]:
    """Universal document parser routing to appropriate extractor based on extension."""
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    elif suffix in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    elif suffix in [".txt", ".md"]:
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Supported: .pdf, .docx, .txt, .md")
