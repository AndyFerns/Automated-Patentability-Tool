"""
models.py
─────────
Pydantic data models used throughout the application for request/response
validation and serialization.  Each model is deliberately flat and
self-documenting so that FastAPI's auto-generated docs stay clean.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .credence_table import VALID_IP_TYPES


# ═══════════════════════════════════════════════════════════════════
#  Disclosure Models
# ═══════════════════════════════════════════════════════════════════

class DisclosureCreate(BaseModel):
    """
    Schema for creating a new IP disclosure.

    Attributes
    ----------
    title : str
        Short descriptive title of the disclosure.
    description : str
        Detailed description / abstract of the IP.
    ip_type : str
        Category of IP — must be one of the types in the credence table.
    organization : str
        Name of the owning organization / institution.
    inventor_name : str, optional
        Name of the inventor.  Can be auto-extracted from an uploaded
        document if not provided.
    """
    title: str = Field(..., example="Solar-Powered Water Purifier")
    description: str = Field(
        ..., example="A novel device that uses concentrated solar energy ..."
    )
    ip_type: str = Field(..., example="Patent")
    organization: str = Field(..., example="Agnel Institute")
    inventor_name: Optional[str] = Field(
        None, example="Dr. Priya Sharma"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Solar-Powered Water Purifier",
                "description": "A novel device that uses concentrated solar "
                               "energy to purify contaminated water in "
                               "rural areas.",
                "ip_type": "Patent",
                "organization": "Agnel Institute",
                "inventor_name": "Dr. Priya Sharma",
            }
        }


class DisclosureResponse(BaseModel):
    """
    Response model returned after a disclosure is successfully stored.

    Includes the auto-generated ID and, for patents, the similarity
    analysis results.
    """
    id: int
    title: str
    description: str
    ip_type: str
    organization: str
    inventor_name: Optional[str] = None

    # Patent-specific fields — populated only when ip_type == "Patent"
    similarity_score: Optional[float] = Field(
        None,
        description="Highest cosine similarity to the mock patent dataset (0–1).",
    )
    risk_level: Optional[str] = Field(
        None,
        description="Risk flag: Low / Medium / High.",
    )
    most_similar_patent: Optional[str] = Field(
        None,
        description="Title of the closest matching patent.",
    )


# ═══════════════════════════════════════════════════════════════════
#  Organization / Score Models
# ═══════════════════════════════════════════════════════════════════

class IPBreakdown(BaseModel):
    """Single row in an IP-type breakdown table."""
    ip_type: str
    count: int
    credence: float
    subtotal: float


class OrganizationScore(BaseModel):
    """
    Aggregated IPR score card for an organization.

    Attributes
    ----------
    organization : str
        Organization name.
    total_ipr_score : float
        Weighted sum across all IP types.
    innovation_tier : str
        Tier label derived from the total score.
    breakdown : list[IPBreakdown]
        Per–IP-type count, weight, and subtotal.
    patent_risk_flags : list[dict]
        Any patents flagged as Medium or High risk.
    """
    organization: str
    total_ipr_score: float
    innovation_tier: str
    breakdown: List[IPBreakdown]
    patent_risk_flags: List[dict]


class DocumentExtraction(BaseModel):
    """Result returned after extracting info from an uploaded document."""
    inventor_name: Optional[str] = None
    extracted_text_preview: str = Field(
        ..., description="First 500 characters of extracted text."
    )
