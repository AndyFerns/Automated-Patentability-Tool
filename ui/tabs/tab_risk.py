"""
ui/tabs/tab_risk.py
───────────────────
Tab 4 — Check patent similarity without creating a disclosure.
"""

import requests
import streamlit as st

from components.helpers import risk_banner
from config import API_BASE


def render() -> None:
    st.subheader("Patent Similarity & Risk Analysis")
    st.caption(
        "Enter a description to check it against the known patent dataset "
        "without creating a disclosure."
    )

    test_desc = st.text_area(
        "Patent Description",
        placeholder="Paste a patent abstract or description here …",
        height=150,
    )

    if not test_desc:
        return

    if st.button("Analyse Similarity", type="primary"):
        if not test_desc.strip():
            st.error("Please enter a description.")
            return
        try:
            resp = requests.post(
                f"{API_BASE}/similarity",
                json={"description": test_desc},
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()

                st.markdown("##### Results")
                c1, c2, c3 = st.columns(3)
                c1.metric("Similarity",     f"{data['similarity_score']:.1f}%")
                c2.metric("Risk Level",     data["risk_level"])
                c3.metric("Closest Patent", data["most_similar_patent"])

                st.write("")
                risk_banner(data["risk_level"])
            else:
                try:
                    detail = resp.json().get("detail", resp.text)
                except ValueError:
                    detail = resp.text
                st.error(f"❌ API Error: {detail}")
        except requests.ConnectionError:
            st.error("🔌 Cannot connect to backend.")