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
from components.helpers import init_pipeline_state
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

init_pipeline_state()

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
st.caption(
    "Institutional IP auditing dashboard — the workflow reads left to right: "
    "upload a document, register a disclosure, review the organization's score, "
    "run risk checks, and generate an audit report."
)
st.divider()

# ────────────────────────────────────────────────────────────────────
# Tabs — ordered to match the pipeline flow.
#   1. Upload a PDF and extract inventor info
#   2. Register a disclosure (auto-fills from step 1)
#   3. See the organization's aggregated IPR score
#   4. Run ad-hoc similarity / risk checks
#   5. Generate a structured audit report
# ────────────────────────────────────────────────────────────────────

tab_up, tab_disc, tab_score, tab_r, tab_a = st.tabs([
    "1 · 📄 Upload Document",
    "2 · 📝 Add Disclosure",
    "3 · 🏢 Organization Score",
    "4 · ⚠️ Patent Risk Check",
    "5 · 📋 Audit Report",
])

with tab_up:
    tab_upload.render()

with tab_disc:
    tab_disclosure.render()

with tab_score:
    tab_org_score.render()

with tab_r:
    tab_risk.render()

with tab_a:
    tab_audit.render()