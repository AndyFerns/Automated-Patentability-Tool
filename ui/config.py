"""
ui/config.py
────────────
Shared constants used across all dashboard modules.
"""

import os

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

IP_TYPES = [
    "Patent",
    "Industrial Design",
    "Copyright",
    "Trademark",
    "Layout Design of Integrated Circuit (LD of IC)",
    "Geographical Indication (GI)",
    "Trade Secret (TS)",
    "Protection of Plant Varieties and Farmers' Rights (PVFR)",
]

APP_VERSION = "v0.1.0"