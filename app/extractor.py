"""
extractor.py
────────────
Document processing module for extracting information from uploaded
PDF/DOC files.

Current capabilities:
    • Extract full text from PDF files using pdfplumber.
    • Search for an inventor name using a simple regex pattern:
        ``Inventor:\\s*(.+)``
    • Return a text preview (first 500 chars) for the UI.

The extraction logic is deliberately simple and regex-based.  For
production use it could be extended with NLP-based named-entity
recognition, but that is out of scope for this prototype.
"""

import re
from pathlib import Path
from typing import Optional, Tuple

import pdfplumber


# ────────────────────────────────────────────────────────────────────
# Regex pattern for inventor extraction.
# Matches lines like:
#   Inventor: Dr. Priya Sharma
#   Inventor : John Doe
#   INVENTOR: Jane Smith
# ────────────────────────────────────────────────────────────────────
_INVENTOR_PATTERN = re.compile(
    r"(?i)inventor\s*:\s*(.+)",   # case-insensitive
)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text content from a PDF file.

    Parameters
    ----------
    file_path : str
        Absolute or relative path to the PDF file.

    Returns
    -------
    str
        Concatenated text from all pages, separated by newlines.
    """
    text_parts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_inventor_name(text: str) -> Optional[str]:
    """
    Attempt to find an inventor name in the extracted text.

    Uses a simple regex — looks for ``Inventor: <Name>`` anywhere in
    the document.

    Parameters
    ----------
    text : str
        The full extracted text.

    Returns
    -------
    str or None
        The inventor name if found, otherwise ``None``.
    """
    match = _INVENTOR_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return None


def process_document(file_path: str) -> Tuple[Optional[str], str]:
    """
    High-level convenience function: extract text, find inventor.

    Parameters
    ----------
    file_path : str
        Path to the uploaded PDF document.

    Returns
    -------
    tuple[str | None, str]
        - Inventor name (or ``None`` if not found).
        - Preview of the extracted text (first 500 characters).
    """
    full_text = extract_text_from_pdf(file_path)
    inventor = extract_inventor_name(full_text)
    preview = full_text[:500] if full_text else ""
    return inventor, preview
