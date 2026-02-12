"""
main.py
───────
FastAPI application — the single entry-point for the backend API.

Endpoints
─────────
    POST  /disclosure                    — Submit a new IP disclosure.
    POST  /upload-document               — Upload a PDF and extract info.
    GET   /organization/{org_name}/score  — Aggregated IPR score card.
    GET   /organization/{org_name}/details — Full disclosure list + score.
    GET   /organizations                  — List all known organizations.

Run with:
    uvicorn app.main:app --reload
"""

import os
import tempfile
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .credence_table import VALID_IP_TYPES
from .database import (
    get_all_organizations,
    get_disclosures_by_org,
    init_db,
    insert_disclosure,
)
from .extractor import process_document
from .models import (
    DisclosureCreate,
    DisclosureResponse,
    DocumentExtraction,
    OrganizationScore,
)
from .patent_similarity import find_similar_patents
from .score_engine import calculate_ipr_score, get_patent_risk_flags

# ────────────────────────────────────────────────────────────────────
# App initialisation
# ────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="IPR Audit & Patentability Scoring Tool",
    description=(
        "Lightweight tool for institutional IP auditing, patentability "
        "scoring via TF-IDF similarity, and organization-level IPR "
        "aggregation."
    ),
    version="0.1.0",
)

# Allow the Streamlit frontend (typically on port 8501) to call us.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Ensure the database tables exist before serving requests."""
    init_db()


# ═══════════════════════════════════════════════════════════════════
#  POST /disclosure — Submit a new IP disclosure
# ═══════════════════════════════════════════════════════════════════

@app.post("/disclosure", response_model=DisclosureResponse)
def create_disclosure(payload: DisclosureCreate):
    """
    Accept a JSON IP disclosure, optionally run patent similarity
    analysis, persist to SQLite, and return the full record.

    If ``ip_type`` is ``"Patent"``, the description is compared
    against the mock patent dataset and similarity / risk fields are
    populated.
    """
    # Validate IP type against the credence table.
    if payload.ip_type not in VALID_IP_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid ip_type '{payload.ip_type}'. "
                   f"Must be one of: {VALID_IP_TYPES}",
        )

    # Build the record dict.
    record = payload.model_dump()

    # ── Patent-specific similarity analysis ─────────────────────
    if payload.ip_type == "Patent":
        sim_result = find_similar_patents(payload.description)
        record["similarity_score"] = sim_result["similarity_score"]
        record["risk_level"] = sim_result["risk_level"]
        record["most_similar_patent"] = sim_result["most_similar_patent"]
    else:
        record["similarity_score"] = None
        record["risk_level"] = None
        record["most_similar_patent"] = None

    # Persist and retrieve the auto-generated ID.
    row_id = insert_disclosure(record)
    record["id"] = row_id

    return DisclosureResponse(**record)


# ═══════════════════════════════════════════════════════════════════
#  POST /upload-document — Upload a PDF and extract inventor info
# ═══════════════════════════════════════════════════════════════════

@app.post("/upload-document", response_model=DocumentExtraction)
async def upload_document(file: UploadFile = File(...)):
    """
    Accept a PDF file upload, extract text, and attempt to identify
    the inventor name via regex.

    The extracted text preview and inventor name (if found) are
    returned so the frontend can pre-fill the disclosure form.
    """
    # Only PDFs are supported in this prototype.
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # Write to a temp file so pdfplumber can read it.
    suffix = ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        inventor, preview = process_document(tmp_path)
    finally:
        # Clean up the temp file.
        os.unlink(tmp_path)

    return DocumentExtraction(
        inventor_name=inventor,
        extracted_text_preview=preview,
    )


# ═══════════════════════════════════════════════════════════════════
#  GET /organization/{org_name}/score — Aggregated IPR score
# ═══════════════════════════════════════════════════════════════════

@app.get("/organization/{org_name}/score", response_model=OrganizationScore)
def get_org_score(org_name: str):
    """
    Compute and return the aggregated IPR score card for the given
    organization name.

    Includes:
        • Total IPR Score
        • Per-IP-type breakdown (count × credence)
        • Innovation Tier
        • Patent risk flags (Medium / High similarity matches)
    """
    disclosures = get_disclosures_by_org(org_name)

    if not disclosures:
        raise HTTPException(
            status_code=404,
            detail=f"No disclosures found for organization '{org_name}'.",
        )

    total_score, breakdown, tier = calculate_ipr_score(disclosures)
    risk_flags = get_patent_risk_flags(disclosures)

    return OrganizationScore(
        organization=org_name,
        total_ipr_score=total_score,
        innovation_tier=tier,
        breakdown=breakdown,
        patent_risk_flags=risk_flags,
    )


# ═══════════════════════════════════════════════════════════════════
#  GET /organization/{org_name}/details — Full disclosure list
# ═══════════════════════════════════════════════════════════════════

@app.get("/organization/{org_name}/details")
def get_org_details(org_name: str):
    """
    Return every disclosure record for the given organization, plus
    the aggregated score card.

    This endpoint is a superset of ``/score`` — it additionally
    returns the raw disclosure list.
    """
    disclosures = get_disclosures_by_org(org_name)

    if not disclosures:
        raise HTTPException(
            status_code=404,
            detail=f"No disclosures found for organization '{org_name}'.",
        )

    total_score, breakdown, tier = calculate_ipr_score(disclosures)
    risk_flags = get_patent_risk_flags(disclosures)

    return {
        "organization": org_name,
        "total_ipr_score": total_score,
        "innovation_tier": tier,
        "breakdown": breakdown,
        "patent_risk_flags": risk_flags,
        "disclosures": disclosures,
    }


# ═══════════════════════════════════════════════════════════════════
#  GET /organizations — List all known organizations
# ═══════════════════════════════════════════════════════════════════

@app.get("/organizations", response_model=List[str])
def list_organizations():
    """Return a list of all organizations that have submitted disclosures."""
    return get_all_organizations()
