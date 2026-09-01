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
from typing import List, Optional

import pdfplumber


# ────────────────────────────────────────────────────────────────────
# Inventor extraction — production-style parser.
#
# The old regex stopped at the first comma or newline, which mangled
# multi-inventor listings ("Inventors: John Doe, Jane Smith") and
# multi-line entries. Real disclosure/patent documents commonly use:
#
#     Inventor: Dr. Priya Sharma
#     Inventors: John Doe, Jane Smith and Alice Roe
#     Inventor(s): Priya Sharma, PhD;
#                  John Doe, MSc
#
# Strategy:
#   1. Find the "Inventor(s):" label.
#   2. Capture text until the NEXT labeled section (Assignee, Filing
#      Date, Application No., Abstract, Field, Background, etc.) OR
#      a blank line, whichever comes first — this bounds the capture
#      without truncating legitimate multi-name lists.
#   3. Split on ',', ';', or the word 'and'.
#   4. Filter each candidate: must look like a person name (letters
#      + spaces + a small set of punctuation), reasonable length,
#      and not contain digits or e-mail/URL fragments.
#
# ``extract_inventor_name`` returns the first valid name for
# backward compatibility; ``extract_inventors`` returns the full list.
# ────────────────────────────────────────────────────────────────────

# Matches the "Inventor:" label line and captures the rest of THAT line.
# Continuation onto following lines is decided by ``_collect_block``
# using explicit end-of-line / start-of-line signals — this is more
# reliable than a single regex trying to bound a variable-length block.
_INVENTOR_LABEL_LINE = re.compile(
    r"(?im)^\s*inventor(?:s|\(s\))?\s*[:\-]\s*(?P<line>.*)$"
)

# A line that starts a NEW labeled section (Assignee:, Address:,
# Filing Date:, etc.) — recognized by "Word[ Word]*:" at line start.
_NEW_LABEL_LINE = re.compile(r"^\s*[A-Za-z][A-Za-z()/&\- ]{0,40}\s*[:\-]\s")

# Continuation signals — the block spans another line when either
# the previous line ends with one of these, or the next line begins
# with one.
_CONTINUES_ENDING = re.compile(r"(?:[,;&/]|\band)\s*$", re.IGNORECASE)
_CONTINUES_STARTING = re.compile(r"^\s*(?:,|;|&|/|and\b)", re.IGNORECASE)

# Split the captured block into individual name candidates.
_NAME_SEPARATOR = re.compile(r"\s*(?:,|;|\band\b|&|/)\s*", re.IGNORECASE)

# Trailing degree / honorific suffixes to strip from the end of a name.
_TRAILING_SUFFIX = re.compile(
    r"\s*,?\s*(?:ph\.?d\.?|m\.?d\.?|m\.?sc\.?|b\.?sc\.?|b\.?tech\.?|"
    r"m\.?tech\.?|ph\.?d|esq\.?|jr\.?|sr\.?|ii|iii|iv)\s*$",
    re.IGNORECASE,
)

# A plausible person-name shape:
#   • starts with a letter
#   • letters, spaces, dots, hyphens, apostrophes only
#   • 2–80 chars, at least one space (i.e. multi-token)
_NAME_SHAPE = re.compile(r"^[A-Za-z][A-Za-z .'\-]{1,79}$")


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


def _clean_candidate(raw: str) -> Optional[str]:
    """Normalize whitespace, strip trailing degrees, validate shape."""
    name = re.sub(r"\s+", " ", raw).strip(" .,;:-")
    if not name:
        return None
    # Strip trailing degrees/suffixes, then re-trim.
    prev = None
    while prev != name:
        prev = name
        name = _TRAILING_SUFFIX.sub("", name).strip(" .,;:-")
    # Reject candidates that clearly aren't names.
    if any(ch.isdigit() for ch in name):
        return None
    if "@" in name or "http" in name.lower():
        return None
    if not _NAME_SHAPE.match(name):
        return None
    # Require at least two tokens — filters single words like "The".
    if len(name.split()) < 2:
        return None
    return name


def _collect_block(text: str, label_match: re.Match) -> str:
    """
    Starting from the "Inventor:" line, collect that line's content
    plus any following continuation lines. A line continues the block
    only if either the prior line ends with a separator (``,`` ``;``
    ``and`` ``&`` ``/``) or the next line begins with one.

    Stops at:
      • a blank line
      • a new labeled section (``Assignee:``, ``Address:`` …)
      • end of text
    """
    first_line = label_match.group("line")
    # ``.*`` in the label regex doesn't consume the trailing newline,
    # so the tail starts with "\n<next line>..." — strip that single
    # boundary newline so splitlines doesn't emit a spurious empty
    # entry that would falsely terminate the block.
    tail = text[label_match.end():].lstrip("\n")
    collected = [first_line.rstrip()]

    for raw_line in tail.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            break
        if _NEW_LABEL_LINE.match(raw_line):
            break
        prev = collected[-1]
        if _CONTINUES_ENDING.search(prev) or _CONTINUES_STARTING.match(raw_line):
            collected.append(stripped)
            continue
        break

    return " ".join(part for part in collected if part)


def extract_inventors(text: str) -> List[str]:
    """
    Return every inventor name found in the document, in order.

    Handles single- and multi-inventor blocks, separators (comma,
    semicolon, "and", ampersand, slash), honorifics/degrees, and
    stops at the next labeled section so it doesn't spill into
    Assignee / Abstract / etc.
    """
    if not text:
        return []
    label = _INVENTOR_LABEL_LINE.search(text)
    if not label:
        return []
    block = _collect_block(text, label)

    seen: List[str] = []
    for chunk in _NAME_SEPARATOR.split(block):
        cleaned = _clean_candidate(chunk)
        if cleaned and cleaned not in seen:
            seen.append(cleaned)
    return seen


def extract_inventor_name(text: str) -> Optional[str]:
    """
    Return the primary inventor name (first in the listing), or None.

    Kept for backward compatibility with the existing single-name
    API surface. Callers that need the full roster should use
    :func:`extract_inventors`.
    """
    inventors = extract_inventors(text)
    return inventors[0] if inventors else None


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

    return {
        "inventor_name": inventor,
        "extracted_text_preview": preview,
    }
