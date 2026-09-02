# 03 · API Reference

The complete contract for the FastAPI backend. Base URL is whatever you set as
`API_BASE` — locally that's **`http://localhost:8000`**.

Interactive, always-up-to-date versions live at:

- **Swagger UI** → `http://localhost:8000/docs`
- **ReDoc** → `http://localhost:8000/redoc`

---

## Endpoint summary

| Method | Path | Purpose | Persists? |
|--------|------|---------|-----------|
| `GET`  | `/` | Root health alias | — |
| `GET`  | `/health` | Liveness probe | — |
| `POST` | `/disclosure` | Create a disclosure (+ similarity for patents) | ✅ |
| `POST` | `/similarity` | Ad-hoc similarity check | ❌ |
| `POST` | `/upload-document` | Extract inventor + text from a PDF | ❌ |
| `GET`  | `/organization/{org_name}/score` | Aggregated IPR score card | — |
| `GET`  | `/organization/{org_name}/details` | Score card **+** full disclosure list | — |
| `GET`  | `/organizations` | List all known organizations | — |
| `GET`  | `/audit/{org_name}` | Structured audit & compliance report | — |

> **Pipeline note:** `/similarity`, `/health`, and `/` are the newest additions.
> `/similarity` in particular exists so the dashboard's **Risk Check** tab can run
> the same similarity math as `/disclosure` **without** writing a throwaway row to
> the database.

---

## Health

### `GET /`

Root alias, handy for a bare ping.

```json
{ "status": "ok", "service": "ipr-audit" }
```

### `GET /health`

Liveness probe used by the dashboard's sidebar status badge.

```json
{ "status": "ok" }
```

---

## `POST /disclosure`

Register a new IP disclosure. If `ip_type` is `"Patent"`, the description is run
through the similarity engine and the risk fields are populated inline.

### Request body

```json
{
    "title": "Solar-Powered Water Purifier",
    "description": "A novel device that uses concentrated solar energy to purify contaminated water in rural areas.",
    "ip_type": "Patent",
    "organization": "Agnel Institute",
    "inventor_name": "Dr. Priya Sharma"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `title` | string | ✅ | 1–500 chars |
| `description` | string | ✅ | 1–20 000 chars |
| `ip_type` | string | ✅ | Must be a valid credence-table type (see below) |
| `organization` | string | ✅ | 1–200 chars |
| `inventor_name` | string | ❌ | ≤ 200 chars, nullable |

**Valid `ip_type` values:** `Patent`, `Industrial Design`, `Copyright`,
`Trademark`, `Layout Design of Integrated Circuit (LD of IC)`,
`Geographical Indication (GI)`, `Trade Secret (TS)`,
`Protection of Plant Varieties and Farmers' Rights (PVFR)`.

### Response `200`

```json
{
    "id": 7,
    "title": "Solar-Powered Water Purifier",
    "description": "A novel device that uses concentrated solar energy ...",
    "ip_type": "Patent",
    "organization": "Agnel Institute",
    "inventor_name": "Dr. Priya Sharma",
    "similarity_score": 62.4,
    "risk_level": "Medium",
    "most_similar_patent": "Solar-Powered Water Purification System"
}
```

For non-patent types, `similarity_score`, `risk_level`, and
`most_similar_patent` are `null`. Note the returned `organization` may differ in
casing from what you sent — it's normalized to the canonical spelling.

### Errors

| Code | When |
|------|------|
| `400` | `ip_type` isn't in the credence table, or title/description/organization is blank after trimming. |
| `422` | Body fails Pydantic validation (missing field, length violation). |

---

## `POST /similarity`

Run a similarity check **without persisting anything**. Same engine as
`/disclosure`, but read-only — perfect for iterating on wording.

### Request body

```json
{ "description": "A device for purifying water using solar heat" }
```

### Response `200`

```json
{
    "similarity_score": 62.4,
    "risk_level": "Medium",
    "most_similar_patent": "Solar-Powered Water Purification System",
    "all_scores": [
        { "title": "Solar-Powered Water Purification System", "similarity_pct": 62.4 },
        { "title": "Portable Desalination Unit", "similarity_pct": 18.1 }
    ]
}
```

`all_scores` is the full per-patent breakdown, sorted descending — the dashboard
shows the top 5.

### Errors

| Code | When |
|------|------|
| `400` | `description` is empty or whitespace-only. |

---

## `POST /upload-document`

Upload a PDF; get back the extracted inventor name and a text preview. Used to
pre-fill the disclosure form. **Nothing is persisted.**

- **Content type:** `multipart/form-data`
- **Field name:** `file`
- **Max size:** 20 MB

### Response `200`

```json
{
    "inventor_name": "Dr. Priya Sharma",
    "extracted_text_preview": "Inventor: Dr. Priya Sharma\nTitle: Solar-Powered ..."
}
```

`inventor_name` is `null` if no name matched. `extracted_text_preview` is the
first 500 characters of extracted text (empty string for image-only PDFs, since
there's no OCR).

### Errors

| Code | When |
|------|------|
| `400` | File isn't a `.pdf`, or the upload is empty. |
| `413` | File exceeds the 20 MB limit. |
| `422` | The PDF couldn't be processed. |

### Example

```bash
curl -X POST http://localhost:8000/upload-document \
     -F "file=@disclosure.pdf"
```

---

## `GET /organization/{org_name}/score`

The aggregated IPR score card for one organization. `org_name` matching is
**case-insensitive**.

### Response `200`

```json
{
    "organization": "Agnel Institute",
    "total_ipr_score": 11.0,
    "innovation_tier": "Developing",
    "breakdown": [
        { "ip_type": "Copyright", "count": 2, "credence": 1.0, "subtotal": 2.0 },
        { "ip_type": "Patent",    "count": 3, "credence": 3.0, "subtotal": 9.0 }
    ],
    "patent_risk_flags": [
        {
            "title": "Solar-Powered Water Purifier",
            "similarity_score": 62.4,
            "risk_level": "Medium",
            "most_similar_patent": "Solar-Powered Water Purification System"
        }
    ]
}
```

`patent_risk_flags` lists only patents flagged **Medium** or **High**.

### Errors

| Code | When |
|------|------|
| `404` | No disclosures exist for that organization. |

---

## `GET /organization/{org_name}/details`

A **superset** of `/score` — the same score card plus the raw list of every
disclosure for the organization.

### Response `200`

```json
{
    "organization": "Agnel Institute",
    "total_ipr_score": 11.0,
    "innovation_tier": "Developing",
    "breakdown": [ ... ],
    "patent_risk_flags": [ ... ],
    "disclosures": [
        { "id": 1, "title": "...", "ip_type": "Patent", "organization": "Agnel Institute", ... }
    ]
}
```

### Errors

| Code | When |
|------|------|
| `404` | No disclosures exist for that organization. |

---

## `GET /organizations`

A sorted, de-duplicated list of every organization that has at least one
disclosure. Case variants are collapsed.

### Response `200`

```json
["Agnel Institute", "Fr. Conceicao Rodrigues Institute of Technology"]
```

---

## `GET /audit/{org_name}`

A structured audit & compliance report for an organization. It's a deterministic
summary of what the system already did — no ML runs here.

### Response `200`

```json
{
    "search_scope": {
        "databases": ["Google Patents", "USPTO", "WIPO"],
        "classification": ["IPC B64C", "CPC H02S"],
        "total_disclosures_analysed": 8
    },
    "search_logic": {
        "boolean_valid": true,
        "keyword_expansion": true,
        "filters": "ip_type, organization"
    },
    "metrics": {
        "total_hits": 30,
        "threshold": "40%",
        "final_docs": 3,
        "total_disclosures": 8,
        "patent_disclosures": 3
    },
    "system": {
        "algorithm": "TF-IDF + Cosine Similarity",
        "feature_limit": 15,
        "risk_thresholds": { "low": "<40%", "medium": "40–70%", "high": ">70%" }
    },
    "ip_distribution": [
        { "ip_type": "Copyright", "count": 2 },
        { "ip_type": "Patent", "count": 3 }
    ],
    "risk_breakdown": { "Low": 1, "Medium": 1, "High": 1 },
    "similarity_scores": [62.4, 12.1, 78.9]
}
```

> **On `total_hits`:** this is an honest count — the number of
> *(patent disclosure × reference patent)* similarity comparisons actually
> performed, not a fabricated figure. The dashboard labels it "Comparisons
> Performed".

### Errors

| Code | When |
|------|------|
| `404` | No disclosures exist for that organization. |

---

## CORS

The backend allows all origins (`allow_origins=["*"]`) with credentials
disabled — fine for the local Streamlit frontend and any dev tooling.

---

**Next:** [04 · Scoring Methodology](04-scoring-methodology.md) to understand the
numbers these endpoints return.
