"""
ui/tabs/tab_org_score.py
────────────────────────
Tab 3 — View aggregated IPR score & breakdown for an organization.
"""

import requests
import streamlit as st

from components.helpers import (
    api_error,
    empty_state,
    fetch_organizations,
    next_step,
    tier_badge,
)
from config import API_BASE


def render() -> None:
    st.subheader("Step 3 · Organization IPR Score")
    st.caption(
        "Aggregated credence-weighted IPR score, tier classification, "
        "and per-IP-type breakdown for an organization."
    )

    orgs = fetch_organizations()
    prefill = st.session_state.get("prefill_org")

    if orgs:
        default_idx = orgs.index(prefill) if prefill in orgs else 0
        org_input = st.selectbox(
            "Organization",
            options=orgs,
            index=default_idx,
            key="score_org_pick",
        )
    else:
        empty_state(
            "🏢",
            "No organizations yet",
            "Register at least one disclosure to see aggregated scores here.",
            hint="→ Go back to step 2 to create your first disclosure.",
        )
        return

    if st.button("Get Score", type="primary"):
        with st.spinner(f"Aggregating disclosures for {org_input}…"):
            try:
                resp = requests.get(
                    f"{API_BASE}/organization/{org_input}/score",
                    timeout=15,
                )
            except requests.ConnectionError:
                st.error("🔌 Cannot connect to backend.")
                return

        if resp.status_code == 404:
            st.warning(f"No disclosures found for '{org_input}'.")
            return
        if resp.status_code != 200:
            st.error(f"❌ API Error: {api_error(resp)}")
            return

        data = resp.json()

        # ── Score & tier card ──
        tier_badge(data["innovation_tier"], data["total_ipr_score"])

        # ── Breakdown table ──
        st.markdown("##### Breakdown by IP Type")
        breakdown = data.get("breakdown", [])
        if breakdown:
            st.table(breakdown)
        else:
            st.info("No breakdown data available.")

        # ── Patent risk flags ──
        flags = data.get("patent_risk_flags", [])
        st.markdown("##### Patent Risk Flags")
        if flags:
            for f in flags:
                sim = f.get("similarity_score")
                sim_str = f"{sim:.1f}%" if isinstance(sim, (int, float)) else "—"
                st.warning(
                    f"**{f['title']}** — Similarity: {sim_str} "
                    f"({f['risk_level']}) — Closest: {f['most_similar_patent'] or '—'}"
                )
        else:
            st.success("No elevated-risk patents detected.")

        # ── Remember the org for the audit tab ──
        st.session_state["prefill_org"]         = org_input
        st.session_state["last_disclosure_org"] = org_input

        next_step(
            title="Generate the audit report",
            description=(
                f"Produce a structured compliance report for "
                f"**{org_input}** — search methodology, filtering rigor, "
                "and full distribution charts."
            ),
            tab_hint="5 · 📋 Audit Report",
        )
