"""
Document Parser — Multi-format document text extraction.
Supports PDF (PyMuPDF), DOCX (python-docx), and OCR fallback (pytesseract).
"""

import fitz  # PyMuPDF
from docx import Document
from pathlib import Path
from typing import Optional

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


def parse_document(file_path: str) -> dict:
    """
    Parse a document and extract text content.

    Returns:
        dict with keys: text, page_count, char_count, filename, format
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        return _parse_pdf(path)
    elif ext in (".docx", ".doc"):
        return _parse_docx(path)
    elif ext == ".txt":
        return _parse_txt(path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Supported: .pdf, .docx, .txt")


def _parse_pdf(path: Path) -> dict:
    """Extract text from PDF using PyMuPDF, with OCR fallback for scanned pages."""
    doc = fitz.open(str(path))
    pages_text = []

    for page_num, page in enumerate(doc):
        text = page.get_text("text")

        # If page has very little text, try OCR
        if len(text.strip()) < 50 and OCR_AVAILABLE:
            text = _ocr_page(page) or text

        pages_text.append(text)

    full_text = "\n\n".join(pages_text)
    doc.close()

    return {
        "text": full_text,
        "page_count": len(pages_text),
        "char_count": len(full_text),
        "filename": path.name,
        "format": "pdf",
    }


def _parse_docx(path: Path) -> dict:
    """Extract text from DOCX using python-docx."""
    doc = Document(str(path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    full_text = "\n\n".join(paragraphs)

    return {
        "text": full_text,
        "page_count": max(1, len(full_text) // 3000),  # Approximate
        "char_count": len(full_text),
        "filename": path.name,
        "format": "docx",
    }


def _parse_txt(path: Path) -> dict:
    """Read plain text files."""
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "text": text,
        "page_count": 1,
        "char_count": len(text),
        "filename": path.name,
        "format": "txt",
    }


def _ocr_page(page) -> Optional[str]:
    """OCR a PDF page using pytesseract."""
    try:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text = pytesseract.image_to_string(img)
        return text if text.strip() else None
    except Exception:
        return None
