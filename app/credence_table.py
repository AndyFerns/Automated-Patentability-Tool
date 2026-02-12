"""
credence_table.py
─────────────────
Defines the official IPR credence weights and the Innovation Tier
classification logic.  This module is the single source of truth for
all scoring constants — any change to the credence values should be
made here and will propagate automatically to the score engine.

Credence weights are mandated by institutional policy:
    Patent                                          = 3.0
    Industrial Design                               = 2.0
    Copyright                                       = 1.0
    Trademark                                       = 1.5
    Layout Design of Integrated Circuit (LD of IC)  = 0.2
    Geographical Indication (GI)                    = 1.5
    Trade Secret (TS)                               = 0.0
    Protection of Plant Varieties & Farmers' Rights = 3.0
"""

from typing import Dict

# ────────────────────────────────────────────────────────────────────
# Credence Table — maps each IP type to its institutional weight.
# ────────────────────────────────────────────────────────────────────
CREDENCE_TABLE: Dict[str, float] = {
    "Patent":                                                       3.0,
    "Industrial Design":                                            2.0,
    "Copyright":                                                    1.0,
    "Trademark":                                                    1.5,
    "Layout Design of Integrated Circuit (LD of IC)":               0.2,
    "Geographical Indication (GI)":                                 1.5,
    "Trade Secret (TS)":                                            0.0,
    "Protection of Plant Varieties and Farmers' Rights (PVFR)":     3.0,
}

# Convenience list of all valid IP type strings.
VALID_IP_TYPES = list(CREDENCE_TABLE.keys())


def get_credence(ip_type: str) -> float:
    """
    Return the credence weight for the given IP type.

    Parameters
    ----------
    ip_type : str
        One of the keys in ``CREDENCE_TABLE``.

    Returns
    -------
    float
        The credence weight.

    Raises
    ------
    ValueError
        If ``ip_type`` is not found in the table.
    """
    if ip_type not in CREDENCE_TABLE:
        raise ValueError(
            f"Unknown IP type '{ip_type}'. "
            f"Must be one of: {VALID_IP_TYPES}"
        )
    return CREDENCE_TABLE[ip_type]


def classify_tier(score: float) -> str:
    """
    Map a numeric IPR score to an Innovation Tier label.

    Tier thresholds (inclusive):
        0  – 5   →  Emerging
        6  – 15  →  Developing
        16+      →  Strong

    Parameters
    ----------
    score : float
        The aggregate IPR score.

    Returns
    -------
    str
        One of ``"Emerging"``, ``"Developing"``, or ``"Strong"``.
    """
    if score <= 5:
        return "Emerging"
    elif score <= 15:
        return "Developing"
    else:
        return "Strong"
