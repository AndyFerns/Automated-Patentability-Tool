"""
patent_similarity.py
────────────────────
Independent module for patent similarity analysis.

Workflow:
    1. Load a mock patent dataset from ``data/mock_patents.json``.
    2. Vectorize abstracts using TF-IDF.
    3. Compute cosine similarity between a candidate disclosure
       description and every patent in the dataset.
    4. Return the highest similarity percentage, the matching patent
       title, and a risk level.

Risk thresholds:
    > 70%   →  High
    40–70%  →  Medium
    < 40%   →  Low

This module is completely self-contained and can be tested or swapped
out without touching any other part of the codebase.
"""

import json
from pathlib import Path
from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ────────────────────────────────────────────────────────────────────
# Load the mock patent dataset once at module import time.
# ────────────────────────────────────────────────────────────────────
_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_MOCK_PATENTS_PATH = _DATA_DIR / "mock_patents.json"


def _load_mock_patents() -> List[Dict[str, str]]:
    """
    Read the mock patent dataset from disk.

    Returns
    -------
    list[dict]
        Each dict has ``"title"`` and ``"abstract"`` keys.
    """
    with open(_MOCK_PATENTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Pre-load so we pay the I/O cost only once.
_patents: List[Dict[str, str]] = []


def _ensure_patents_loaded() -> None:
    """Lazily load patents on first use (avoids crash if file missing at import)."""
    global _patents
    if not _patents:
        _patents = _load_mock_patents()


def classify_risk(similarity_pct: float) -> str:
    """
    Map a similarity percentage to a risk label.

    Parameters
    ----------
    similarity_pct : float
        Similarity as a percentage (0–100).

    Returns
    -------
    str
        ``"Low"`` | ``"Medium"`` | ``"High"``
    """
    if similarity_pct > 70:
        return "High"
    elif similarity_pct >= 40:
        return "Medium"
    else:
        return "Low"


def find_similar_patents(description: str) -> Dict[str, Any]:
    """
    Compare a candidate disclosure description against the mock patent
    dataset using TF-IDF + cosine similarity.

    Parameters
    ----------
    description : str
        The patent disclosure description / abstract to evaluate.

    Returns
    -------
    dict
        Keys:
        - ``similarity_score``  — float (0–100, rounded to 2 dp)
        - ``risk_level``        — str
        - ``most_similar_patent`` — str (title of closest match)
        - ``all_scores``        — list of dicts with per-patent scores

    Example
    -------
    >>> result = find_similar_patents("A device for purifying water")
    >>> result["risk_level"]
    'Low'
    """
    _ensure_patents_loaded()

    # Build the corpus: all patent abstracts + the candidate description.
    corpus = [p["abstract"] for p in _patents] + [description]

    # Fit TF-IDF on the full corpus.
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # The last vector is the candidate; compute similarity to all others.
    candidate_vec = tfidf_matrix[-1]
    patent_vecs = tfidf_matrix[:-1]
    similarities = cosine_similarity(candidate_vec, patent_vecs).flatten()

    # Identify the best match.
    best_idx = int(similarities.argmax())
    best_score = float(similarities[best_idx]) * 100  # Convert to %

    # Build per-patent score list (useful for debugging / UI display).
    all_scores = [
        {
            "title": _patents[i]["title"],
            "similarity_pct": round(float(similarities[i]) * 100, 2),
        }
        for i in range(len(_patents))
    ]
    # Sort descending by similarity.
    all_scores.sort(key=lambda x: x["similarity_pct"], reverse=True)

    return {
        "similarity_score": round(best_score, 2),
        "risk_level": classify_risk(best_score),
        "most_similar_patent": _patents[best_idx]["title"],
        "all_scores": all_scores,
    }
