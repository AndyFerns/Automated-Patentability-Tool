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

import streamlit as st

from components.helpers import backend_status
from config import API_BASE, APP_VERSION, IP_TYPES


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