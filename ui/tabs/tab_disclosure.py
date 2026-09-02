"""
ui/tabs/tab_disclosure.py
─────────────────────────
Tab 2 — Register an IP disclosure. Auto-fills inventor from step 1
and organization from prior submissions, then surfaces the risk
result plus explicit next-step CTAs.
"""

import requests
import streamlit as st

from components.helpers import (
    api_error,
    fetch_organizations,
    next_step,
    risk_banner,
    risk_gauge,
)
from config import API_BASE, IP_TYPES


_NEW_ORG_SENTINEL = "＋ Add a new organization…"


def _org_input() -> str:
    """
    Smart organization picker: dropdown of known orgs + an "add new"
    option that reveals a text input. Falls back to a plain text
    input when no orgs exist yet.
    """
    known = fetch_organizations()
    default = st.session_state.get("prefill_org") or ""

    if not known:
        return st.text_input(
            "Organization",
            value=default,
            placeholder="e.g. Agnel Institute",
            key="disc_org_freeform",
        ).strip()

    options = known + [_NEW_ORG_SENTINEL]
    idx = options.index(default) if default in known else 0
    picked = st.selectbox(
        "Organization",
        options=options,
        index=idx,
        key="disc_org_pick",
        help="Pick an existing organization or add a new one.",
    )
    if picked == _NEW_ORG_SENTINEL:
        return st.text_input(
            "New organization name",
            value="",
            placeholder="e.g. Agnel Institute",
            key="disc_org_new",
        ).strip()
    return picked


def render() -> None:
    st.subheader("Step 2 · Register a disclosure")
    st.caption(
        "File a new IP disclosure. Patent-type disclosures are "
        "automatically checked against the reference dataset and "
        "assigned a risk level."
    )

    # ── Auto-fill notices (shown outside the form so they're visible) ──
    prefill_inventor = st.session_state.get("extracted_inventor") or ""
    if prefill_inventor:
        st.info(
            f"👤 Inventor name **{prefill_inventor}** was auto-filled "
            f"from the document uploaded in step 1."
        )
    prefill_org = st.session_state.get("prefill_org")
    if prefill_org:
        st.caption(f"Organization pre-selected: **{prefill_org}**")

    with st.form("disclosure_form", clear_on_submit=False):
        title = st.text_input(
            "Title *",
            placeholder="e.g. Solar-Powered Water Purifier",
        )
        description = st.text_area(
            "Description / Abstract *",
            placeholder="Describe the invention or creative work…",
            height=150,
            help="For patents this text is compared against the reference dataset.",
        )

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            ip_type = st.selectbox(
                "IP Type *",
                IP_TYPES,
                help="Determines credence weight and whether a similarity check runs.",
            )
        with col_f2:
            organization = _org_input()

        inventor_name = st.text_input(
            "Inventor Name",
            value=prefill_inventor,
            placeholder="e.g. Dr. Priya Sharma",
            help="Optional. Auto-filled if you uploaded a document in step 1.",
        )

        submitted = st.form_submit_button(
            "Submit Disclosure",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    # ── Client-side validation ──
    missing = [
        name for name, val in (
            ("Title", title),
            ("Description", description),
            ("Organization", organization),
        ) if not val or not val.strip()
    ]
    if missing:
        st.error(f"Please fill in: {', '.join(missing)}.")
        return

    payload = {
        "title":         title.strip(),
        "description":   description.strip(),
        "ip_type":       ip_type,
        "organization":  organization.strip(),
        "inventor_name": (inventor_name or "").strip() or None,
    }

    with st.spinner("Submitting disclosure…"):
        try:
            resp = requests.post(
                f"{API_BASE}/disclosure",
                json=payload,
                timeout=30,
            )
        except requests.ConnectionError:
            st.error("🔌 Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
            return

    if resp.status_code != 200:
        st.error(f"❌ API Error: {api_error(resp)}")
        return

    data = resp.json()
    # ── Persist for the rest of the pipeline ──
    st.session_state["last_disclosure_id"]  = data["id"]
    st.session_state["last_disclosure_org"] = data["organization"]
    st.session_state["prefill_org"]          = data["organization"]
    if data.get("risk_level"):
        st.session_state["last_disclosure_risk"] = data["risk_level"]
    # Consume the extracted inventor once it's been used.
    if prefill_inventor and payload["inventor_name"] == prefill_inventor:
        st.session_state["extracted_inventor"] = None

    st.success(
        f"✅ Disclosure **#{data['id']}** created for "
        f"**{data['organization']}**."
    )

    # ── Patent-specific result card ──
    if data.get("similarity_score") is not None:
        st.divider()
        st.markdown("##### Patent Similarity Analysis")
        c1, c2, c3 = st.columns(3)
        c1.metric("Similarity",    f"{data['similarity_score']:.1f}%")
        c2.metric("Risk Level",    data["risk_level"])
        c3.metric("Closest Match", data["most_similar_patent"] or "—")
        risk_gauge(data["similarity_score"], data["risk_level"])
        risk_banner(data["risk_level"])

    # ── Next-step CTAs ──
    if data.get("risk_level") in ("Medium", "High"):
        next_step(
            title="Investigate the risk match",
            description=(
                f"This patent flagged **{data['risk_level']} risk** against "
                f"'{data.get('most_similar_patent') or 'a reference patent'}'. "
                "Run a follow-up similarity check with adjusted wording, or "
                "jump straight to the audit report."
            ),
            tab_hint="4 · ⚠️ Patent Risk Check",
        )
    else:
        next_step(
            title="Review the organization's IPR score",
            description=(
                f"See how this disclosure changes **{data['organization']}**'s "
                "aggregated score and tier."
            ),
            tab_hint="3 · 🏢 Organization Score",
        )
