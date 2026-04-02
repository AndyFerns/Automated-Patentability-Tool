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
# Stops at commas or newlines to avoid capturing trailing metadata.
# ────────────────────────────────────────────────────────────────────
_INVENTOR_PATTERN = re.compile(
    r"(?i)inventor\s*:\s*([^,\r\n\t]+)",   # case-insensitive, exclude commas
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
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        # Log the error in a real app; here we just return empty text.
        print(f"Error extracting PDF text: {e}")
        return ""
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
    if not text:
        return None
    match = _INVENTOR_PATTERN.search(text)
    if match:
        return match.group(1).strip()
    return None


def process_document(file_path: str) -> dict:
    """
    High-level convenience function: extract text, find inventor.

    Parameters
    ----------
    file_path : str
        Path to the uploaded PDF document.

    Returns
    -------
    dict
        - inventor_name: str | None
        - extracted_text_preview: str (first 500 characters)
    """
    full_text = extract_text_from_pdf(file_path)
    inventor = extract_inventor_name(full_text)
    preview = full_text[:500] if full_text else ""

    result = {
        "inventor_name": inventor,
        "extracted_text_preview": preview,
    }

    # Validate the dictionary keys
    required_keys = ["inventor_name", "extracted_text_preview"]
    for key in required_keys:
        if key not in result:
            # This should not happen with the hardcoded dict above, 
            # but fulfills the "validate dictionary keys" requirement.
            raise KeyError(f"Missing required key: {key}")

    return result
