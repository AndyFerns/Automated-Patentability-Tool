"""
ui/tabs/tab_org_score.py
────────────────────────
Tab 3 — View aggregated IPR score & breakdown for an organization.
"""

import requests
import streamlit as st

from components.helpers import fetch_organizations
from config import API_BASE


def render() -> None:
    st.subheader("Organization IPR Score")

    orgs      = fetch_organizations()
    org_input = st.text_input(
        "Organization Name",
        placeholder="Type or select an organization name",
    )
    if orgs:
        st.caption(f"Known organizations: {', '.join(orgs)}")

    if not org_input:
        return

    if st.button("Get Score", type="primary"):
        try:
            resp = requests.get(f"{API_BASE}/organization/{org_input}/score", timeout=15)
            if resp.status_code == 200:
                data = resp.json()

                c1, c2 = st.columns(2)
                c1.metric("Total IPR Score", f"{data['total_ipr_score']:.1f}")
                c2.metric("Innovation Tier", data["innovation_tier"])

                st.divider()
                st.markdown("##### Breakdown by IP Type")
                breakdown = data["breakdown"]
                if breakdown:
                    st.table(breakdown)
                else:
                    st.info("No breakdown data available.")

                flags = data.get("patent_risk_flags", [])
                if flags:
                    st.divider()
                    st.markdown("##### ⚠️ Patent Risk Flags")
                    for f in flags:
                        st.warning(
                            f"**{f['title']}** — "
                            f"Similarity: {f['similarity_score']:.1f}% "
                            f"({f['risk_level']}) — "
                            f"Closest: {f['most_similar_patent']}"
                        )
                else:
                    st.success("No elevated-risk patents detected.")

            elif resp.status_code == 404:
                st.warning(f"No disclosures found for '{org_input}'.")
            else:
                st.error(f"❌ API Error: {resp.text}")
        except requests.ConnectionError:
            st.error("🔌 Cannot connect to backend.")