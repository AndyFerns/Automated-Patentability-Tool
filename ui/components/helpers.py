"""
ui/components/helpers.py
────────────────────────
Reusable UI helper components shared across tabs.
"""

import html

import requests
import streamlit as st

from config import API_BASE


# ────────────────────────────────────────────────────────────────────
# Pipeline session-state keys — the "glue" that turns disconnected
# tabs into a coherent workflow.
# ────────────────────────────────────────────────────────────────────

PIPELINE_KEYS = {
    "extracted_inventor":       None,   # from Upload  → Disclosure
    "extracted_preview":        None,
    "extracted_source_name":    None,
    "last_disclosure_id":       None,
    "last_disclosure_org":      None,
    "last_disclosure_risk":     None,
    "prefill_org":              None,   # from Disclosure → Score / Audit
}


def init_pipeline_state() -> None:
    """Seed default session-state keys so tabs never KeyError."""
    for key, default in PIPELINE_KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = default


def reset_pipeline_state() -> None:
    """Clear all pipeline session state."""
    for key in PIPELINE_KEYS:
        st.session_state[key] = None


# ────────────────────────────────────────────────────────────────────
# Visual output components
# ────────────────────────────────────────────────────────────────────

_RISK_COLORS = {
    "High":   ("#b71c1c", "🔴"),
    "Medium": ("#e6a200", "🟡"),
    "Low":    ("#2e7d32", "🟢"),
}


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


def risk_gauge(similarity_pct: float, risk: str) -> None:
    """
    Horizontal bar showing similarity % with the 40% (Medium) and
    70% (High) threshold markers. Purely visual; complements the
    risk banner with an at-a-glance sense of *how close* to the
    next tier.
    """
    color, _icon = _RISK_COLORS.get(risk, ("#5c6bc0", "•"))
    pct = max(0.0, min(100.0, float(similarity_pct)))
    st.markdown(
        f"""
        <div style="margin: 0.4rem 0 1rem 0;">
            <div style="
                position: relative;
                height: 14px;
                background: rgba(128,128,128,0.15);
                border-radius: 999px;
                overflow: visible;
            ">
                <div style="
                    width: {pct:.1f}%;
                    height: 100%;
                    background: {color};
                    border-radius: 999px;
                    transition: width 0.4s ease;
                "></div>
                <div style="
                    position: absolute; left: 40%; top: -4px;
                    width: 2px; height: 22px;
                    background: rgba(230,162,0,0.75);
                " title="Medium threshold (40%)"></div>
                <div style="
                    position: absolute; left: 70%; top: -4px;
                    width: 2px; height: 22px;
                    background: rgba(183,28,28,0.75);
                " title="High threshold (70%)"></div>
            </div>
            <div style="
                display:flex; justify-content:space-between;
                font-size:0.72rem; opacity:0.65; margin-top:6px;
                font-family: 'Space Mono', monospace;
            ">
                <span>0%</span><span>40% Medium</span><span>70% High</span><span>100%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tier_badge(tier: str, score: float) -> None:
    """
    Colored tier badge with the current score and a progress bar
    toward the next tier boundary (Emerging → Developing → Strong).
    """
    tier_colors = {
        "Emerging":   ("#8892b0", "Emerging",   0,  5),
        "Developing": ("#5c6bc0", "Developing", 6, 15),
        "Strong":     ("#2e7d32", "Strong",    16, 30),
    }
    color, label, lo, hi = tier_colors.get(tier, ("#5c6bc0", tier, 0, 30))
    span = max(hi - lo, 1)
    pct = min(1.0, max(0.0, (score - lo) / span)) * 100

    if tier == "Emerging":
        next_label = f"{6 - score:.1f} pts to Developing" if score < 6 else ""
    elif tier == "Developing":
        next_label = f"{16 - score:.1f} pts to Strong" if score < 16 else ""
    else:
        next_label = "Top tier reached"

    st.markdown(
        f"""
        <div style="
            border: 1px solid {color}55;
            background: {color}18;
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin: 0.4rem 0 0.8rem 0;
        ">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div>
                    <div style="font-size:0.72rem; text-transform:uppercase;
                                letter-spacing:0.08em; opacity:0.7;">
                        Innovation tier
                    </div>
                    <div style="font-size:1.4rem; font-weight:600; color:{color};">
                        {html.escape(label)}
                    </div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:0.72rem; text-transform:uppercase;
                                letter-spacing:0.08em; opacity:0.7;">
                        Score
                    </div>
                    <div style="font-family:'Space Mono', monospace;
                                font-size:1.4rem;">
                        {score:.1f}
                    </div>
                </div>
            </div>
            <div style="height:6px; background:rgba(128,128,128,0.18);
                        border-radius:999px; margin-top:0.7rem; overflow:hidden;">
                <div style="width:{pct:.1f}%; height:100%; background:{color};
                            border-radius:999px;"></div>
            </div>
            <div style="font-size:0.72rem; opacity:0.65; margin-top:6px;">
                {html.escape(next_label)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def next_step(title: str, description: str, tab_hint: str) -> None:
    """
    Non-modal card that tells the user which tab to visit next.
    Streamlit can't programmatically switch tabs, so the CTA is
    an explicit textual pointer to the tab name at the top.
    """
    st.markdown(
        f"""
        <div style="
            border: 1px dashed rgba(92,107,192,0.5);
            background: rgba(92,107,192,0.08);
            border-radius: 12px;
            padding: 0.9rem 1.1rem;
            margin: 1rem 0 0.4rem 0;
        ">
            <div style="font-size:0.72rem; text-transform:uppercase;
                        letter-spacing:0.08em; opacity:0.7; margin-bottom:4px;">
                Next step
            </div>
            <div style="font-weight:600; font-size:1rem;">
                {html.escape(title)}
            </div>
            <div style="font-size:0.88rem; opacity:0.82; margin-top:4px;">
                {html.escape(description)}
            </div>
            <div style="
                display:inline-block; margin-top:8px; font-size:0.78rem;
                padding: 3px 10px; border-radius: 999px;
                background: rgba(92,107,192,0.18);
                font-family: 'Space Mono', monospace;
            ">
                → Open the “{html.escape(tab_hint)}” tab above
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(icon: str, title: str, body: str, hint: str | None = None) -> None:
    """Consistent empty-state card used when a tab has nothing to show."""
    hint_html = (
        f'<div style="font-size:0.82rem; opacity:0.7; margin-top:8px;">'
        f"{html.escape(hint)}</div>"
        if hint else ""
    )
    st.markdown(
        f"""
        <div style="
            text-align:center; padding: 2.2rem 1.2rem;
            border: 1px dashed rgba(128,128,128,0.35);
            border-radius: 14px; margin: 0.6rem 0;
        ">
            <div style="font-size:2.4rem; line-height:1;">{icon}</div>
            <div style="font-weight:600; font-size:1.05rem; margin-top:0.5rem;">
                {html.escape(title)}
            </div>
            <div style="font-size:0.9rem; opacity:0.75; margin-top:4px;">
                {html.escape(body)}
            </div>
            {hint_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def api_error(resp) -> str:
    """Best-effort extraction of a human-readable error from a response."""
    try:
        return str(resp.json().get("detail", resp.text))
    except ValueError:
        return resp.text or f"HTTP {resp.status_code}"


def fetch_organizations() -> list[str]:
    """Fetch the list of known organizations from the backend. Returns [] on failure."""
    try:
        resp = requests.get(f"{API_BASE}/organizations", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return data
    except (requests.RequestException, ValueError):
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
        resp = requests.get(f"{API_BASE}/health", timeout=4)
        ms   = int((time.monotonic() - t0) * 1000)
        if resp.status_code == 200:
            return True, f"{ms} ms"
    except requests.RequestException:
        pass
    return False, "—"