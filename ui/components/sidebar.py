"""
ui/components/sidebar.py
────────────────────────
Renders the application sidebar:
  • Branding & version
  • Light / dark mode toggle
  • Backend status indicator
  • IP type quick-reference
  • Help & links
"""

import html

import streamlit as st

from components.helpers import backend_status, reset_pipeline_state
from config import API_BASE, APP_VERSION, IP_TYPES


def _pipeline_progress() -> None:
    """
    Small stepper that lights up each pipeline stage as the user
    completes it. Purely informational.
    """

    steps = [
        ("Upload", bool(st.session_state.get("extracted_preview"))),
        ("Disclose", bool(st.session_state.get("last_disclosure_id"))),
        ("Score", bool(st.session_state.get("last_disclosure_org"))),
        ("Risk", bool(st.session_state.get("last_disclosure_risk"))),
        ("Audit", bool(st.session_state.get("last_disclosure_org"))),
    ]

    dots = []

    for i, (label, done) in enumerate(steps, start=1):
        color = "#4caf50" if done else "rgba(128,128,128,0.35)"
        text_color = "inherit" if done else "rgba(128,128,128,0.75)"

        dots.append(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:8px;
                margin:4px 0;
            ">
                <div style="
                    width:18px;
                    height:18px;
                    border-radius:50%;
                    background:{color};
                    color:white;
                    font-size:0.7rem;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-family:'Space Mono', monospace;
                ">{i}</div>

                <div style="
                    font-size:0.82rem;
                    color:{text_color};
                ">
                    {html.escape(label)}
                </div>
            </div>
            """
        )

    st.html(
        f"""
        <div style="margin:4px 0 8px 0;">
            {"".join(dots)}
        </div>
        """
    )


def render_sidebar() -> None:
    """Call once per page render to populate st.sidebar."""

    with st.sidebar:
        # ── Branding ──────────────────────────────────────────
        st.markdown("## 🔬 IPR Audit")
        st.caption(f"Patentability Scoring Tool · {APP_VERSION}")

        st.divider()

        # ── Theme toggle ──────────────────────────────────────
        st.markdown("**Appearance**")
        label = "☀️  Switch to Light Mode" if st.session_state.dark_mode else "🌙  Switch to Dark Mode"
        if st.button(label, use_container_width=True, key="sidebar_theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.divider()

        # ── Backend status ────────────────────────────────────
        st.markdown("**Backend Status**")
        online, latency = backend_status()

        dot_class   = "online" if online else "offline"
        status_text = f"Connected &nbsp;·&nbsp; {latency}" if online else "Unreachable"

        st.markdown(
            f"""
            <div class="status-badge">
                <span class="status-dot {dot_class}"></span>
                {status_text}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div style="font-size:0.75rem; margin-top:6px; opacity:0.55;">
                {API_BASE}
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("↻  Refresh Status", use_container_width=True, key="refresh_status"):
            st.rerun()

        st.divider()

        # ── Pipeline progress ─────────────────────────────────
        st.markdown("**Pipeline Progress**", unsafe_allow_html=True,)
        _pipeline_progress()

        if any(
            st.session_state.get(k)
            for k in (
                "extracted_preview", "last_disclosure_id",
                "last_disclosure_org", "last_disclosure_risk",
            )
        ):
            if st.button(
                "Reset workflow",
                use_container_width=True,
                key="reset_pipeline",
                help="Clear all pipeline state — extracted data, last disclosure, and any pre-fills.",
            ):
                reset_pipeline_state()
                st.rerun()

        st.divider()

        # ── IP Type reference ─────────────────────────────────
        with st.expander("📚 Supported IP Types", expanded=False):
            for ip in IP_TYPES:
                st.markdown(f"- {ip}")

        st.divider()

        # ── Help links ────────────────────────────────────────
        st.markdown("**Resources**")
        st.markdown(
            """
            <div class="sidebar-card">
                <strong>API Docs</strong><br>
                <a href="http://localhost:8000/docs" target="_blank"
                   style="color:#7986cb; text-decoration:none;">
                    localhost:8000/docs ↗
                </a><br><br>
                <strong>Redoc</strong><br>
                <a href="http://localhost:8000/redoc" target="_blank"
                   style="color:#7986cb; text-decoration:none;">
                    localhost:8000/redoc ↗
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Footer ────────────────────────────────────────────
        st.markdown(
            "<div style='font-size:0.72rem; opacity:0.4; margin-top:auto; padding-top:1rem;'>"
            "For institutional use only."
            "</div>",
            unsafe_allow_html=True,
        )