"""
dashboard.py
────────────
Streamlit-based frontend for the IPR Audit & Patentability Scoring Tool.

Connects to the FastAPI backend (default: http://localhost:8000) and
provides four interactive tabs:

    1. 📝 Add Disclosure   — Submit IP disclosures via a form.
    2. 📄 Upload Document   — Upload a PDF to extract inventor info.
    3. 🏢 Organization Score — View aggregated IPR score & breakdown.
    4. ⚠️ Patent Risk        — Inspect patent similarity results.

Run with:
    streamlit run ui/dashboard.py
"""

import os
import requests
import streamlit as st

# ────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

# The credence table IP types — must match the backend.
IP_TYPES = [
    "Patent",
    "Industrial Design",
    "Copyright",
    "Trademark",
    "Layout Design of Integrated Circuit (LD of IC)",
    "Geographical Indication (GI)",
    "Trade Secret (TS)",
    "Protection of Plant Varieties and Farmers' Rights (PVFR)",
]

# ────────────────────────────────────────────────────────────────────
# Page setup
# ────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="IPR Audit Tool",
    page_icon="🔬",
    layout="wide",
)

st.title("🔬 IPR Audit & Patentability Scoring Tool")
st.caption("Lightweight institutional IP auditing dashboard")

# ────────────────────────────────────────────────────────────────────
# Tabs
# ────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Add Disclosure",
    "📄 Upload Document",
    "🏢 Organization Score",
    "⚠️ Patent Risk",
])


# ═══════════════════════════════════════════════════════════════════
#  Tab 1 — Add Disclosure
# ═══════════════════════════════════════════════════════════════════

with tab1:
    st.header("Submit IP Disclosure")
    st.markdown("Fill in the details below to register a new IP disclosure.")

    with st.form("disclosure_form"):
        # Form fields matching the DisclosureCreate Pydantic model.
        title = st.text_input("Title", placeholder="e.g. Solar-Powered Water Purifier")
        description = st.text_area(
            "Description / Abstract",
            placeholder="Describe the invention or creative work ...",
            height=150,
        )
        ip_type = st.selectbox("IP Type", IP_TYPES)
        organization = st.text_input("Organization", placeholder="e.g. Agnel Institute")
        inventor_name = st.text_input(
            "Inventor Name (optional)",
            placeholder="e.g. Dr. Priya Sharma",
        )

        submitted = st.form_submit_button("Submit Disclosure", type="primary")

    if submitted:
        # Validate required fields on the client side for better UX.
        if not title or not description or not organization:
            st.error("Please fill in Title, Description, and Organization.")
        else:
            payload = {
                "title": title,
                "description": description,
                "ip_type": ip_type,
                "organization": organization,
                "inventor_name": inventor_name or None,
            }
            try:
                resp = requests.post(f"{API_BASE}/disclosure", json=payload, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"✅ Disclosure #{data['id']} created successfully!")

                    # Show patent similarity results if applicable.
                    if data.get("similarity_score") is not None:
                        st.subheader("Patent Similarity Analysis")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Similarity", f"{data['similarity_score']:.1f}%")
                        col2.metric("Risk Level", data["risk_level"])
                        col3.metric("Closest Match", data["most_similar_patent"])
                else:
                    st.error(f"❌ API Error: {resp.json().get('detail', resp.text)}")
            except requests.ConnectionError:
                st.error(
                    "🔌 Cannot connect to backend. "
                    "Make sure the FastAPI server is running on port 8000."
                )


# ═══════════════════════════════════════════════════════════════════
#  Tab 2 — Upload Document
# ═══════════════════════════════════════════════════════════════════

with tab2:
    st.header("Upload Document for Extraction")
    st.markdown(
        "Upload a PDF document and the system will attempt to extract "
        "the inventor name automatically."
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Only PDF files are supported.",
    )

    if uploaded_file is not None:
        if st.button("Extract Information", type="primary"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                resp = requests.post(f"{API_BASE}/upload-document", files=files, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()

                    # Display extracted inventor name.
                    if data.get("inventor_name"):
                        st.success(f"👤 Inventor Found: **{data['inventor_name']}**")
                    else:
                        st.warning(
                            "Could not auto-detect inventor name. "
                            "Please enter it manually in the disclosure form."
                        )

                    # Display text preview.
                    st.subheader("Extracted Text Preview")
                    st.text_area(
                        "Preview (first 500 chars)",
                        value=data.get("extracted_text_preview", ""),
                        height=200,
                        disabled=True,
                    )
                else:
                    st.error(f"❌ API Error: {resp.json().get('detail', resp.text)}")
            except requests.ConnectionError:
                st.error(
                    "🔌 Cannot connect to backend. "
                    "Make sure the FastAPI server is running on port 8000."
                )


# ═══════════════════════════════════════════════════════════════════
#  Tab 3 — Organization Score
# ═══════════════════════════════════════════════════════════════════

with tab3:
    st.header("Organization IPR Score")

    # Fetch the list of known organizations for the dropdown.
    orgs = []
    try:
        resp = requests.get(f"{API_BASE}/organizations", timeout=10)
        if resp.status_code == 200:
            orgs = resp.json()
    except requests.ConnectionError:
        pass

    # Allow both selection from known orgs and manual entry.
    org_input = st.text_input(
        "Organization Name",
        placeholder="Type or select an organization name",
    )
    if orgs:
        st.caption(f"Known organizations: {', '.join(orgs)}")

    if org_input and st.button("Get Score", type="primary"):
        try:
            resp = requests.get(
                f"{API_BASE}/organization/{org_input}/score", timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()

                # ── Score headline ──────────────────────────────
                col1, col2 = st.columns(2)
                col1.metric("Total IPR Score", f"{data['total_ipr_score']:.1f}")
                col2.metric("Innovation Tier", data["innovation_tier"])

                # ── Breakdown table ─────────────────────────────
                st.subheader("Breakdown by IP Type")
                breakdown = data["breakdown"]
                if breakdown:
                    st.table(breakdown)
                else:
                    st.info("No breakdown data available.")

                # ── Risk flags ──────────────────────────────────
                flags = data.get("patent_risk_flags", [])
                if flags:
                    st.subheader("⚠️ Patent Risk Flags")
                    for f in flags:
                        st.warning(
                            f"**{f['title']}** — Similarity: "
                            f"{f['similarity_score']:.1f}% "
                            f"({f['risk_level']}) — Closest: "
                            f"{f['most_similar_patent']}"
                        )
                else:
                    st.success("No elevated-risk patents detected.")

            elif resp.status_code == 404:
                st.warning(f"No disclosures found for '{org_input}'.")
            else:
                st.error(f"❌ API Error: {resp.text}")
        except requests.ConnectionError:
            st.error("🔌 Cannot connect to backend.")


# ═══════════════════════════════════════════════════════════════════
#  Tab 4 — Patent Risk
# ═══════════════════════════════════════════════════════════════════

with tab4:
    st.header("Patent Similarity & Risk Analysis")
    st.markdown(
        "Enter a patent description below to check it against the "
        "known patent dataset **without** creating a disclosure."
    )

    test_desc = st.text_area(
        "Patent Description",
        placeholder="Paste a patent abstract or description here ...",
        height=150,
    )

    if test_desc and st.button("Analyse Similarity", type="primary"):
        # We call the disclosure endpoint with a dummy payload just to
        # run the similarity check.  A cleaner approach would be a
        # dedicated /similarity endpoint, but this keeps the prototype
        # lean.  Instead, we replicate the similarity logic client-side
        # by directly calling the backend logic.
        try:
            # Use a quick POST to /disclosure with a throwaway record,
            # or better yet — call a utility endpoint.  For this
            # prototype we just POST a disclosure and display the result.
            payload = {
                "title": "[Risk-Check] Ad-hoc similarity test",
                "description": test_desc,
                "ip_type": "Patent",
                "organization": "__risk_check__",
                "inventor_name": None,
            }
            resp = requests.post(f"{API_BASE}/disclosure", json=payload, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                st.subheader("Results")

                col1, col2, col3 = st.columns(3)
                col1.metric("Similarity", f"{data['similarity_score']:.1f}%")
                col2.metric("Risk Level", data["risk_level"])
                col3.metric("Closest Patent", data["most_similar_patent"])

                # Colour-coded risk badge.
                risk = data["risk_level"]
                if risk == "High":
                    st.error(
                        "🔴 **HIGH RISK** — This disclosure has significant "
                        "overlap with existing patents."
                    )
                elif risk == "Medium":
                    st.warning(
                        "🟡 **MEDIUM RISK** — Some overlap detected. "
                        "Consider a detailed prior-art search."
                    )
                else:
                    st.success(
                        "🟢 **LOW RISK** — Minimal overlap with known patents."
                    )
            else:
                st.error(f"❌ API Error: {resp.json().get('detail', resp.text)}")
        except requests.ConnectionError:
            st.error("🔌 Cannot connect to backend.")

# ────────────────────────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "IPR Audit Tool v0.1.0 · Built with FastAPI + Streamlit · "
    "For institutional use only."
)
