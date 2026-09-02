"""
ui/tabs/tab_risk.py
───────────────────
Tab 4 — Ad-hoc patent similarity check that does NOT persist to the
database. Useful for exploring wording variations before committing
to a disclosure.
"""

import requests
import streamlit as st

from components.helpers import api_error, next_step, risk_banner, risk_gauge
from config import API_BASE


def render() -> None:
    st.subheader("Step 4 · Patent Similarity & Risk Check")
    st.caption(
        "Test a description against the reference patent dataset "
        "without creating a disclosure. Useful for iterating on wording "
        "before you file."
    )

    test_desc = st.text_area(
        "Patent Description",
        placeholder="Paste a patent abstract or description here…",
        height=160,
        key="risk_desc",
    )

    if not test_desc.strip():
        st.info(
            "Enter a description above and click **Analyse Similarity** "
            "to see how it compares against known patents. Nothing is "
            "saved to the database from this tab."
        )
        return

    if st.button("Analyse Similarity", type="primary"):
        with st.spinner("Running TF-IDF + cosine similarity against the reference dataset…"):
            try:
                resp = requests.post(
                    f"{API_BASE}/similarity",
                    json={"description": test_desc},
                    timeout=30,
                )
            except requests.ConnectionError:
                st.error("🔌 Cannot connect to backend.")
                return

        if resp.status_code != 200:
            st.error(f"❌ API Error: {api_error(resp)}")
            return

        data = resp.json()
        st.session_state["last_disclosure_risk"] = data["risk_level"]

        st.markdown("##### Results")
        c1, c2, c3 = st.columns(3)
        c1.metric("Similarity",     f"{data['similarity_score']:.1f}%")
        c2.metric("Risk Level",     data["risk_level"])
        c3.metric("Closest Patent", data["most_similar_patent"] or "—")
        risk_gauge(data["similarity_score"], data["risk_level"])
        risk_banner(data["risk_level"])

        # ── Top matches (context, not just the winner) ──
        top = (data.get("all_scores") or [])[:5]
        if top and any(row.get("similarity_pct", 0) > 0 for row in top):
            with st.expander("Top 5 matches", expanded=False):
                st.table(top)

        # ── Bridge back to the persistence path ──
        if data["risk_level"] == "Low":
            next_step(
                title="Ready to file",
                description=(
                    "Low risk — proceed to register this description as "
                    "a formal disclosure."
                ),
                tab_hint="2 · 📝 Add Disclosure",
            )
        else:
            next_step(
                title="Reconsider before filing",
                description=(
                    f"This description scored **{data['risk_level']} risk** "
                    "against the reference set. Revise the wording or "
                    "consult prior art before creating a disclosure."
                ),
                tab_hint="2 · 📝 Add Disclosure",
            )
