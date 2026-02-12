"""
score_engine.py
───────────────
Pure-function scoring engine.

This module has ZERO side effects — it does not touch the database,
the filesystem, or the network.  It receives a list of disclosure
dicts and returns the aggregated IPR score, per-type breakdown, and
the Innovation Tier label.

IPR Score Formula:
    IPR Score = Σ (count_of_ip_type × credence_weight)

Innovation Tier thresholds:
    0–5   → Emerging
    6–15  → Developing
    16+   → Strong
"""

from collections import Counter
from typing import Any, Dict, List, Tuple

from .credence_table import CREDENCE_TABLE, classify_tier


def calculate_ipr_score(
    disclosures: List[Dict[str, Any]],
) -> Tuple[float, List[Dict[str, Any]], str]:
    """
    Compute the aggregate IPR score for a set of disclosures.

    This is the core scoring function and is intentionally side-effect
    free: give it data, get back a result.

    Parameters
    ----------
    disclosures : list[dict]
        Each dict must have at least an ``ip_type`` key whose value is
        a valid credence-table entry.

    Returns
    -------
    tuple[float, list[dict], str]
        - **total_score** — the weighted sum.
        - **breakdown** — a list of dicts, each containing:
            ``ip_type``, ``count``, ``credence``, ``subtotal``.
        - **tier** — ``"Emerging"`` | ``"Developing"`` | ``"Strong"``.

    Example
    -------
    >>> disclosures = [
    ...     {"ip_type": "Patent"},
    ...     {"ip_type": "Patent"},
    ...     {"ip_type": "Copyright"},
    ... ]
    >>> score, breakdown, tier = calculate_ipr_score(disclosures)
    >>> score
    7.0
    """
    # Count occurrences of each IP type.
    type_counts: Counter = Counter(d["ip_type"] for d in disclosures)

    breakdown: List[Dict[str, Any]] = []
    total_score: float = 0.0

    for ip_type, count in sorted(type_counts.items()):
        # Fall back to 0.0 for any unrecognised type (defensive).
        credence = CREDENCE_TABLE.get(ip_type, 0.0)
        subtotal = count * credence
        total_score += subtotal
        breakdown.append(
            {
                "ip_type": ip_type,
                "count": count,
                "credence": credence,
                "subtotal": subtotal,
            }
        )

    tier = classify_tier(total_score)
    return total_score, breakdown, tier


def get_patent_risk_flags(
    disclosures: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Extract patent-specific risk flags from disclosure records.

    Only disclosures with ``ip_type == "Patent"`` and a non-null
    ``risk_level`` that is not ``"Low"`` are flagged.

    Parameters
    ----------
    disclosures : list[dict]
        All disclosure records for a given organization.

    Returns
    -------
    list[dict]
        Each dict contains ``title``, ``similarity_score``,
        ``risk_level``, and ``most_similar_patent``.
    """
    flags: List[Dict[str, Any]] = []
    for d in disclosures:
        if d.get("ip_type") != "Patent":
            continue
        if d.get("risk_level") in ("Medium", "High"):
            flags.append(
                {
                    "title": d["title"],
                    "similarity_score": d.get("similarity_score"),
                    "risk_level": d["risk_level"],
                    "most_similar_patent": d.get("most_similar_patent"),
                }
            )
    return flags
