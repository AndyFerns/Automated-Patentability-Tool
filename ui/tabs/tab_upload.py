"""
ui/tabs/tab_upload.py
─────────────────────
Tab 2 — Upload a PDF to extract inventor information.
"""

import requests
import streamlit as st

from config import API_BASE


def render() -> None:
    st.subheader("Upload Document for Extraction")
    st.caption("Upload a PDF and the system will attempt to extract the inventor name automatically.")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Only PDF files are supported.",
    )

    if uploaded_file is not None:
        if st.button("Extract Information", type="primary"):
            try:
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
                }
                resp = requests.post(f"{API_BASE}/upload-document", files=files, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()

                    if data.get("inventor_name"):
                        st.success(f"👤 Inventor detected: **{data['inventor_name']}**")
                    else:
                        st.warning(
                            "Could not auto-detect inventor name. "
                            "Please enter it manually in the disclosure form."
                        )

                    st.divider()
                    st.markdown("##### Extracted Text Preview")
                    st.text_area(
                        "First 500 characters",
                        value=data.get("extracted_text_preview", ""),
                        height=200,
                        disabled=True,
                    )
                else:
                    st.error(f"❌ API Error: {resp.json().get('detail', resp.text)}")
            except requests.ConnectionError:
                st.error("🔌 Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")