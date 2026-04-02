"""
ui/tabs/tab_disclosure.py
─────────────────────────
Tab 1 — Submit a new IP disclosure via a form.
"""

import requests
import streamlit as st

from components.helpers import risk_banner
from config import API_BASE, IP_TYPES


def render() -> None:
    st.subheader("Submit IP Disclosure")
    st.caption("Register a new intellectual property disclosure below.")

    with st.form("disclosure_form"):
        title       = st.text_input("Title", placeholder="e.g. Solar-Powered Water Purifier")
        description = st.text_area(
            "Description / Abstract",
            placeholder="Describe the invention or creative work …",
            height=150,
        )
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            ip_type = st.selectbox("IP Type", IP_TYPES)
        with col_f2:
            organization = st.text_input("Organization", placeholder="e.g. Agnel Institute")

        inventor_name = st.text_input(
            "Inventor Name (optional)", placeholder="e.g. Dr. Priya Sharma"
        )
        submitted = st.form_submit_button("Submit Disclosure", type="primary")

    if submitted:
        if not title or not description or not organization:
            st.error("Please fill in Title, Description, and Organization.")
            return

        payload = {
            "title":         title,
            "description":   description,
            "ip_type":       ip_type,
            "organization":  organization,
            "inventor_name": inventor_name or None,
        }
        try:
            resp = requests.post(f"{API_BASE}/disclosure", json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                st.success(f"✅ Disclosure **#{data['id']}** created successfully!")

                if data.get("similarity_score") is not None:
                    st.divider()
                    st.markdown("##### Patent Similarity Analysis")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Similarity",    f"{data['similarity_score']:.1f}%")
                    c2.metric("Risk Level",    data["risk_level"])
                    c3.metric("Closest Match", data["most_similar_patent"])
                    risk_banner(data["risk_level"])
            else:
                st.error(f"❌ API Error: {resp.json().get('detail', resp.text)}")
        except requests.ConnectionError:
            st.error("🔌 Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")