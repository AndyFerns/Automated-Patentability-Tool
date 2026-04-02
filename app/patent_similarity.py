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
from typing import Any, Dict, List, Optional

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
        Each dict has ``"title"`` and ``"description"`` keys.
    """
    try:
        with open(_MOCK_PATENTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        # Gracefully handle missing or malformed mock data.
        return []


# Module-level cache for patents and fitted vectorizer.
_patents: List[Dict[str, str]] = []
_vectorizer: Optional[TfidfVectorizer] = None
_patent_tfidf_matrix: Optional[Any] = None


def _ensure_patents_loaded() -> None:
    """
    Lazily load patents and pre-fit the TF-IDF vectorizer on first use.
    
    This optimization ensures we only pay the fit cost once.
    """
    global _patents, _vectorizer, _patent_tfidf_matrix
    if not _patents:
        _patents = _load_mock_patents()
        if _patents:
            _vectorizer = TfidfVectorizer(stop_words="english")
            descriptions = [p["description"] for p in _patents]
            _patent_tfidf_matrix = _vectorizer.fit_transform(descriptions)


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

    # If no mock data is available, return a safe default.
    if not _patents or not _vectorizer or _patent_tfidf_matrix is None:
        return {
            "similarity_score": 0.0,
            "risk_level": "Low",
            "most_similar_patent": "N/A",
            "all_scores": [],
        }

    # Transform the candidate description using the pre-fitted vectorizer.
    candidate_vec = _vectorizer.transform([description])
    
    # Compute similarity against the pre-computed patent matrix.
    similarities = cosine_similarity(candidate_vec, _patent_tfidf_matrix).flatten()

    # Identify the best match.
    best_idx = int(similarities.argmax())
    best_score = float(similarities[best_idx]) * 100  # Convert to %

    # Build per-patent score list.
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
