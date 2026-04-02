"""
ui/components/helpers.py
────────────────────────
Reusable UI helper components shared across tabs.
"""

import requests
import streamlit as st

from config import API_BASE


def risk_banner(risk: str) -> None:
    """Render a colour-coded risk banner for a given risk level string."""
    if risk == "High":
        st.error(
            "🔴 **HIGH RISK** — Significant overlap with existing patents. "
            "A thorough prior-art clearance is strongly advised."
        )
    elif risk == "Medium":
        st.warning(
            "🟡 **MEDIUM RISK** — Some overlap detected. "
            "Consider a detailed prior-art search before filing."
        )
    else:
        st.success(
            "🟢 **LOW RISK** — Minimal overlap with known patents."
        )


def fetch_organizations() -> list[str]:
    """Fetch the list of known organizations from the backend. Returns [] on failure."""
    try:
        resp = requests.get(f"{API_BASE}/organizations", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except requests.ConnectionError:
        pass
    return []


def backend_status() -> tuple[bool, str]:
    """
    Ping the backend health endpoint.
    Returns (online: bool, latency_label: str).
    """
    import time
    try:
        t0   = time.monotonic()
        resp = requests.get(f"{API_BASE}/", timeout=4)
        ms   = int((time.monotonic() - t0) * 1000)
        if resp.status_code < 500:
            return True, f"{ms} ms"
    except Exception:
        pass
    return False, "—"