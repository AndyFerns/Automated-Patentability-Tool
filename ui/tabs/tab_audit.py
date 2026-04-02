"""
ui/tabs/tab_audit.py
────────────────────
Tab 5 — Generate structured audit & compliance reports.
"""

import pandas as pd
import requests
import streamlit as st

from components.helpers import fetch_organizations
from config import API_BASE


def render() -> None:
    st.subheader("Audit & Compliance Report")
    st.caption(
        "Generate a structured audit report for an organization's IP portfolio — "
        "including search methodology, filtering rigor, and system configuration."
    )

    audit_orgs      = fetch_organizations()
    audit_org_input = st.text_input(
        "Organization Name",
        placeholder="Type an organization name",
        key="audit_org_input",
    )
    if audit_orgs:
        st.caption(f"Known organizations: {', '.join(audit_orgs)}")

    if not audit_org_input:
        return

    if st.button("Generate Audit Report", type="primary"):
        try:
            resp = requests.get(f"{API_BASE}/audit/{audit_org_input}", timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                _render_report(data)
            elif resp.status_code == 404:
                st.warning(f"No disclosures found for '{audit_org_input}'.")
            else:
                st.error(f"❌ API Error: {resp.text}")
        except requests.ConnectionError:
            st.error("🔌 Cannot connect to backend.")


# ── Private helpers ────────────────────────────────────────────────

def _render_report(data: dict) -> None:
    """Render all sections of the audit report."""
    _section_search_scope(data["search_scope"])
    st.divider()
    _section_search_logic(data["search_logic"])
    st.divider()
    _section_metrics(data["metrics"])
    st.divider()
    _section_system(data["system"])
    st.divider()
    _section_charts(data)


def _section_search_scope(scope: dict) -> None:
    st.markdown("#### 🔍 Search Scope")
    c1, c2, c3 = st.columns(3)
    c1.metric("Databases Searched",   len(scope["databases"]))
    c2.metric("Classifications",      len(scope["classification"]))
    c3.metric("Disclosures Analysed", scope["total_disclosures_analysed"])

    col_db, col_cl = st.columns(2)
    with col_db:
        st.caption("**Databases**")
        st.markdown("  \n".join(f"• {d}" for d in scope["databases"]))
    with col_cl:
        st.caption("**Patent Classifications**")
        st.markdown("  \n".join(f"• {c}" for c in scope["classification"]))


def _section_search_logic(logic: dict) -> None:
    st.markdown("#### 🧠 Search Logic Validation")
    c1, c2, c3 = st.columns(3)
    c1.metric("Boolean Query Valid", "✅ Yes" if logic["boolean_valid"]    else "❌ No")
    c2.metric("Keyword Expansion",   "✅ On"  if logic["keyword_expansion"] else "❌ Off")
    c3.metric("Filters Applied",     logic["filters"])


def _section_metrics(metrics: dict) -> None:
    st.markdown("#### 📊 Quantitative Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Search Hits",  f"{metrics['total_hits']:,}")
    c2.metric("Risk Threshold",     metrics["threshold"])
    c3.metric("Final Documents",    metrics["final_docs"])

    c4, c5 = st.columns(2)
    c4.metric("Total Disclosures",  metrics["total_disclosures"])
    c5.metric("Patent Disclosures", metrics["patent_disclosures"])


def _section_system(system: dict) -> None:
    st.markdown("#### ⚙️ System Configuration")
    c1, c2 = st.columns(2)
    c1.metric("Algorithm",     system["algorithm"])
    c2.metric("Feature Limit", system["feature_limit"])

    thresholds = system["risk_thresholds"]
    st.table(pd.DataFrame([
        {"Risk Level": "Low",    "Threshold": thresholds["low"]},
        {"Risk Level": "Medium", "Threshold": thresholds["medium"]},
        {"Risk Level": "High",   "Threshold": thresholds["high"]},
    ]))


def _section_charts(data: dict) -> None:
    st.markdown("#### 📈 Visual Insights")
    metrics = data["metrics"]

    # Result Funnel
    st.markdown("**Result Funnel**")
    st.caption("How the system narrows from total search hits to final scored documents.")
    funnel_df = pd.DataFrame({
        "Stage": ["Total Hits", "Total Disclosures", "Patent Disclosures", "Final Docs (Scored)"],
        "Count": [
            metrics["total_hits"],
            metrics["total_disclosures"],
            metrics["patent_disclosures"],
            metrics["final_docs"],
        ],
    })
    st.bar_chart(funnel_df, x="Stage", y="Count")

    # Similarity Distribution
    similarity_scores = data.get("similarity_scores", [])
    if similarity_scores:
        st.markdown("**Similarity Score Distribution vs Threshold**")
        st.caption("Each bar is the similarity score of a patent disclosure; reference line marks the 40% risk threshold.")
        sim_labels = [f"Patent {i + 1}" for i in range(len(similarity_scores))]
        sim_df = pd.DataFrame({
            "Patent":          sim_labels,
            "Similarity %":    similarity_scores,
            "Threshold (40%)": [40.0] * len(similarity_scores),
        })
        st.bar_chart(sim_df, x="Patent", y=["Similarity %", "Threshold (40%)"])
    else:
        st.info("No patent similarity scores yet — submit patent-type disclosures to populate this chart.")

    # IP Type Distribution
    ip_dist = data.get("ip_distribution", [])
    if ip_dist:
        st.markdown("**IP Type Distribution**")
        st.caption("Breakdown of disclosures by IP type.")
        ip_df = pd.DataFrame(ip_dist)
        st.bar_chart(ip_df, x="ip_type", y="count")
    else:
        st.info("No IP distribution data available.")

    # Risk Level Breakdown
    risk_breakdown = data.get("risk_breakdown", {})
    if risk_breakdown:
        st.markdown("**Patent Risk Level Breakdown**")
        st.caption("Distribution of patent disclosures across risk levels.")
        risk_df = pd.DataFrame([
            {"Risk Level": level, "Count": count}
            for level, count in risk_breakdown.items()
        ])
        st.bar_chart(risk_df, x="Risk Level", y="Count")