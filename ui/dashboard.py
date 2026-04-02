"""
ui/dashboard.py
───────────────
Main entry point for the IPR Audit & Patentability Scoring Tool.

Orchestrates page setup, theme injection, sidebar, and tab rendering.
All logic lives in sub-modules:

    ui/
    ├── config.py                   ← shared constants (API_BASE, IP_TYPES …)
    ├── styles/
    │   └── theme.py                ← inject_css()
    ├── components/
    │   ├── helpers.py              ← risk_banner(), fetch_organizations() …
    │   └── sidebar.py              ← render_sidebar()
    └── tabs/
        ├── tab_disclosure.py       ← Tab 1
        ├── tab_upload.py           ← Tab 2
        ├── tab_org_score.py        ← Tab 3
        ├── tab_risk.py             ← Tab 4
        └── tab_audit.py            ← Tab 5

Run with:
    streamlit run ui/dashboard.py
"""

import sys
import os

# ── Make sibling modules importable when launched via
#    `streamlit run ui/dashboard.py` from the project root.
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

from styles.theme import inject_css
from components.sidebar import render_sidebar
from tabs import tab_disclosure, tab_upload, tab_org_score, tab_risk, tab_audit

# ────────────────────────────────────────────────────────────────────
# Page config  (must be the very first Streamlit call)
# ────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="IPR Audit Tool",
    page_icon="🔬",
    layout="wide",
)

# ────────────────────────────────────────────────────────────────────
# Session state defaults
# ────────────────────────────────────────────────────────────────────

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# ────────────────────────────────────────────────────────────────────
# Theme injection  (before any visible content)
# ────────────────────────────────────────────────────────────────────

inject_css(st.session_state.dark_mode)

# ────────────────────────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────────────────────────

render_sidebar()

# ────────────────────────────────────────────────────────────────────
# Header
# ────────────────────────────────────────────────────────────────────

st.markdown("## 🔬 IPR Audit & Patentability Scoring Tool")
st.caption("Institutional IP auditing dashboard — powered by FastAPI")
st.divider()

# ────────────────────────────────────────────────────────────────────
# Tabs
# ────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Add Disclosure",
    "📄 Upload Document",
    "🏢 Organization Score",
    "⚠️ Patent Risk",
    "📋 Audit",
])

with tab1:
    tab_disclosure.render()

with tab2:
    tab_upload.render()

with tab3:
    tab_org_score.render()

with tab4:
    tab_risk.render()

with tab5:
    tab_audit.render()