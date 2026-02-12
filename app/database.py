"""
database.py
───────────
Lightweight SQLite persistence layer.

Uses raw SQL (no ORM) to keep things simple and dependency-free.
The database file is created automatically in the project root on
first run.

Table: disclosures
──────────────────
    id              INTEGER PRIMARY KEY
    title           TEXT
    description     TEXT
    ip_type         TEXT
    organization    TEXT
    inventor_name   TEXT (nullable)
    similarity_score REAL (nullable — only for patents)
    risk_level      TEXT (nullable — only for patents)
    most_similar_patent TEXT (nullable — only for patents)
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

# ────────────────────────────────────────────────────────────────────
# Database file lives at project root: ipr-prototype/ipr_audit.db
# ────────────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parent.parent / "ipr_audit.db"


def _get_connection() -> sqlite3.Connection:
    """
    Open (or create) the SQLite database and return a connection.

    Row factory is set to ``sqlite3.Row`` so that rows behave like
    dictionaries.
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    Create the ``disclosures`` table if it does not already exist.

    This is safe to call multiple times — the ``IF NOT EXISTS`` clause
    prevents duplicate-table errors.
    """
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS disclosures (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            title               TEXT    NOT NULL,
            description         TEXT    NOT NULL,
            ip_type             TEXT    NOT NULL,
            organization        TEXT    NOT NULL,
            inventor_name       TEXT,
            similarity_score    REAL,
            risk_level          TEXT,
            most_similar_patent TEXT
        )
        """
    )
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
#  CRUD Operations
# ═══════════════════════════════════════════════════════════════════

def insert_disclosure(data: Dict) -> int:
    """
    Insert a new disclosure record and return the auto-generated ID.

    Parameters
    ----------
    data : dict
        Must contain keys matching the ``disclosures`` columns:
        title, description, ip_type, organization, inventor_name,
        and optionally similarity_score, risk_level, most_similar_patent.

    Returns
    -------
    int
        The row ID of the newly inserted record.
    """
    conn = _get_connection()
    cursor = conn.execute(
        """
        INSERT INTO disclosures
            (title, description, ip_type, organization, inventor_name,
             similarity_score, risk_level, most_similar_patent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data["title"],
            data["description"],
            data["ip_type"],
            data["organization"],
            data.get("inventor_name"),
            data.get("similarity_score"),
            data.get("risk_level"),
            data.get("most_similar_patent"),
        ),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_disclosures_by_org(org_name: str) -> List[Dict]:
    """
    Retrieve all disclosures belonging to a specific organization.

    Parameters
    ----------
    org_name : str
        Case-insensitive organization name (compared via ``LOWER()``).

    Returns
    -------
    list[dict]
        Each dict represents one disclosure row.
    """
    conn = _get_connection()
    rows = conn.execute(
        "SELECT * FROM disclosures WHERE LOWER(organization) = LOWER(?)",
        (org_name,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_organizations() -> List[str]:
    """
    Return a sorted list of distinct organization names.

    Returns
    -------
    list[str]
        Unique organization names across all disclosures.
    """
    conn = _get_connection()
    rows = conn.execute(
        "SELECT DISTINCT organization FROM disclosures ORDER BY organization"
    ).fetchall()
    conn.close()
    return [row["organization"] for row in rows]
