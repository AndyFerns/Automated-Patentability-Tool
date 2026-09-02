"""
ui/tabs/tab_upload.py
─────────────────────
Tab 1 — Upload a PDF to extract inventor information.

On success the extracted inventor name and text preview are stashed
in ``st.session_state`` so the Disclosure tab can auto-fill.
"""

import requests
import streamlit as st

from components.helpers import api_error, next_step
from config import API_BASE


def render() -> None:
    st.subheader("Step 1 · Upload a source document")
    st.caption(
        "Drop a patent brief or invention disclosure PDF. The system "
        "will attempt to extract the inventor name and preview the "
        "text so you can pre-fill the disclosure form in step 2."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Only PDF files are supported. Max 20 MB.",
    )

    # ── Show a compact file summary before the user clicks Extract ──
    if uploaded_file is not None:
        size_kb = len(uploaded_file.getvalue()) / 1024
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"**Selected:** `{uploaded_file.name}`")
        c2.markdown(
            f"<div style='text-align:right; opacity:0.7;'>{size_kb:,.1f} KB</div>",
            unsafe_allow_html=True,
        )

        if st.button("Extract Information", type="primary", use_container_width=True):
            with st.spinner("Reading PDF and searching for inventor…"):
                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    }
                    resp = requests.post(
                        f"{API_BASE}/upload-document",
                        files=files,
                        timeout=60,
                    )
                except requests.ConnectionError:
                    st.error("🔌 Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
                    return

            if resp.status_code == 200:
                data = resp.json()
                # Stash into pipeline state for the disclosure form.
                st.session_state["extracted_inventor"] = data.get("inventor_name")
                st.session_state["extracted_preview"] = data.get("extracted_text_preview", "")
                st.session_state["extracted_source_name"] = uploaded_file.name
                st.rerun()
            else:
                st.error(f"❌ API Error: {api_error(resp)}")

    # ── Show whatever's currently in the pipeline (survives reruns) ──
    if st.session_state.get("extracted_preview") is not None:
        st.divider()
        st.markdown("##### Extraction Result")

        inv = st.session_state.get("extracted_inventor")
        src = st.session_state.get("extracted_source_name") or "the uploaded document"
        preview = st.session_state.get("extracted_preview") or ""

        c1, c2 = st.columns([2, 1])
        with c1:
            if inv:
                st.success(f"👤 Inventor detected: **{inv}**")
            else:
                st.warning(
                    "No inventor name matched the expected pattern. "
                    "You'll enter it manually in step 2."
                )
        with c2:
            st.metric("Chars extracted", f"{len(preview):,}")

        with st.expander("📄 Text preview (first 500 chars)", expanded=False):
            st.text_area(
                "Preview",
                value=preview,
                height=180,
                disabled=True,
                label_visibility="collapsed",
            )

        next_step(
            title="Register the disclosure",
            description=(
                "The extracted inventor name is queued for auto-fill on "
                "the disclosure form."
                if inv else
                "Continue to the disclosure form and enter the inventor "
                "name manually."
            ),
            tab_hint="2 · 📝 Add Disclosure",
        )
