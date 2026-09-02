# 02 · Architecture

This is the "how it actually works" doc. We'll walk the data pipeline
end-to-end, then break down each module and the database schema.

---

## The big picture

The system is a classic **two-tier app**: a stateless-ish FastAPI backend that
owns all the logic and data, and a Streamlit frontend that's pure presentation.
They only ever talk over HTTP/JSON.

```
        ┌──────────────────────────────────────────────────────┐
        │                  Streamlit frontend                   │
        │  (ui/) — five tabs, session-state "pipeline glue"     │
        └───────────────────────────┬──────────────────────────┘
                                     │  HTTP / JSON  (API_BASE)
                                     ▼
        ┌──────────────────────────────────────────────────────┐
        │                    FastAPI backend                    │
        │  (app/main.py) — request validation & orchestration   │
        │                                                       │
        │   extractor.py   patent_similarity.py   score_engine  │
        │        │                  │                   │       │
        │        └────────┬─────────┴─────────┬─────────┘       │
        │                 ▼                   ▼                 │
        │           database.py         credence_table.py       │
        └─────────────────┬────────────────────────────────────┘
                          ▼
                   ipr_audit.db  (SQLite)
```

**Design principle:** each backend module is self-contained and side-effect-aware.
`score_engine.py` is a pure function (no I/O). `patent_similarity.py` owns its own
model cache. `database.py` is the only thing that touches SQLite. That separation
is what makes the pieces individually testable.

---

## The pipeline, step by step

The frontend presents the work as five ordered steps, but under the hood it's a
sequence of API calls. Here's the full data flow for the common path:

### Step 1 — Upload & extract (optional)

```
PDF bytes ──POST /upload-document──▶ extractor.process_document()
                                        │
                                        ├─ pdfplumber: PDF → text
                                        └─ regex parser: text → inventor name(s)
                                        ▼
                            { inventor_name, extracted_text_preview }
```

The frontend stashes the extracted inventor name in **session state** so the
disclosure form (step 2) can auto-fill it. Nothing is persisted yet.

### Step 2 — Disclose & score

```
disclosure JSON ──POST /disclosure──▶ validate ip_type against credence table
                                         │
                              is ip_type == "Patent"?
                                     │            │
                                    yes           no
                                     ▼            ▼
                     find_similar_patents()   similarity fields = null
                                     │
                     { similarity_score, risk_level, most_similar_patent }
                                     │
                                     ▼
                     database.insert_disclosure()  ← canonicalizes org name
                                     ▼
                             full record + new id
```

This is the heart of the pipeline: a single POST both **persists** the
disclosure and (for patents) **runs the similarity analysis** inline.

### Step 3 — Aggregate the org

```
GET /organization/{org}/score ─▶ database.get_disclosures_by_org()
                                      │
                                      ▼
                          score_engine.calculate_ipr_score()
                                      │
                    { total_score, breakdown[], innovation_tier }
                                      +
                          score_engine.get_patent_risk_flags()
```

Pure computation over whatever's in the DB — no ML here, just weighted counting.

### Step 4 — Ad-hoc risk check (non-persisting)

```
description ──POST /similarity──▶ find_similar_patents()  ← same engine as step 2
                                     │
                    { similarity_score, risk_level, most_similar_patent, all_scores }
```

Identical similarity math to step 2, but **nothing is written to the database**.
This lets users iterate on wording before committing to a real disclosure.

### Step 5 — Audit report

```
GET /audit/{org} ─▶ database.get_disclosures_by_org()
                        │
                        ▼
                 audit.generate_audit_report()
                        │
        { search_scope, search_logic, metrics, system,
          ip_distribution, risk_breakdown, similarity_scores }
```

A deterministic summary of what the system already did — methodology, filtering,
distributions. No ML, no external calls.

---

## Module reference (`app/`)

| Module | Responsibility | Key functions | Side effects |
|--------|----------------|---------------|--------------|
| `main.py` | FastAPI app + all endpoint handlers. Validates input, orchestrates the other modules. | endpoint handlers, `lifespan` (calls `init_db`) | HTTP |
| `models.py` | Pydantic v2 request/response schemas with field constraints. | `DisclosureCreate`, `DisclosureResponse`, `OrganizationScore`, `AuditReport`, … | none |
| `database.py` | SQLite persistence — raw SQL, no ORM. Owns the schema. | `init_db`, `insert_disclosure`, `get_disclosures_by_org`, `get_all_organizations`, `_canonical_organization` | filesystem (SQLite) |
| `credence_table.py` | Single source of truth for IP-type weights and tier thresholds. | `CREDENCE_TABLE`, `get_credence`, `classify_tier`, `VALID_IP_TYPES` | none |
| `score_engine.py` | Pure scoring functions — zero I/O. | `calculate_ipr_score`, `get_patent_risk_flags` | none |
| `patent_similarity.py` | TF-IDF + cosine similarity over the reference dataset. Caches the fitted model. | `find_similar_patents`, `classify_risk`, `_ensure_patents_loaded` | reads `data/mock_patents.json` once |
| `extractor.py` | PDF text extraction + production-grade inventor-name parsing. | `extract_text_from_pdf`, `extract_inventors`, `extract_inventor_name`, `process_document` | reads PDF file |
| `audit.py` | Deterministic audit-report builder. | `generate_audit_report` | none |

### A few implementation notes worth knowing

- **Similarity model caching.** `patent_similarity.py` loads `mock_patents.json`
  and fits the TF-IDF vectorizer exactly once, guarded by a thread lock (Uvicorn
  can serve requests from multiple threads). A failed load isn't retried on
  every request.
- **Empty / junk input is handled.** An empty or stop-word-only description
  returns a safe `Low / N/A / 0.0%` result instead of silently matching the
  first patent in the dataset.
- **Organization canonicalization.** On insert, `database.py` looks up any
  existing case-insensitive match for the org name and reuses that spelling, so
  `"Agnel"`, `"agnel"`, and `"Agnel "` all collapse into one organization.
- **The inventor parser is not a one-liner regex.** It finds the `Inventor(s):`
  label, follows continuation lines, splits on `,` `;` `and` `&` `/`, strips
  honorifics/degrees (PhD, MSc, Jr.…), and stops at the next labeled section
  (`Assignee:`, `Abstract:`, …). See [extractor.py](https://github.com/AndyFerns/Automated-Patentability-Tool/blob/master/app/extractor.py).

---

## Database schema

One table, created automatically by `init_db()`:

```sql
CREATE TABLE IF NOT EXISTS disclosures (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               TEXT    NOT NULL,
    description         TEXT    NOT NULL,
    ip_type             TEXT    NOT NULL,
    organization        TEXT    NOT NULL,
    inventor_name       TEXT,              -- nullable
    similarity_score    REAL,              -- nullable; patents only
    risk_level          TEXT,              -- nullable; patents only
    most_similar_patent TEXT               -- nullable; patents only
);
```

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Auto-increment primary key. |
| `title` | TEXT | Required. |
| `description` | TEXT | Required. For patents, this is what gets vectorized. |
| `ip_type` | TEXT | Required. Must be a valid credence-table key. |
| `organization` | TEXT | Required. Stored in canonical (deduplicated) spelling. |
| `inventor_name` | TEXT | Optional. |
| `similarity_score` | REAL | Populated only for `ip_type == "Patent"`. |
| `risk_level` | TEXT | `Low` / `Medium` / `High`; patents only. |
| `most_similar_patent` | TEXT | Title of the closest reference patent; patents only. |

The database file is `ipr_audit.db` in the project root. To reset all data,
stop the backend and delete that file — it'll be recreated empty on next start.

---

## The reference dataset

`data/mock_patents.json` holds **10 reference patents**, each with `title` and
`description` (plus some extra fields the similarity engine ignores). This is
what every patent disclosure gets compared against. Swapping in a real corpus is
as simple as replacing this file with the same `{title, description}` shape — no
code changes required.

---

## Frontend architecture (`ui/`)

```
ui/
├── dashboard.py            # entry point: page config, theme, sidebar, 5 tabs
├── config.py              # API_BASE, IP_TYPES, APP_VERSION
├── styles/theme.py        # full light/dark CSS injection
├── components/
│   ├── helpers.py         # pipeline session-state + visual widgets
│   └── sidebar.py         # branding, status, pipeline progress, reset
└── tabs/
    ├── tab_upload.py      # step 1
    ├── tab_disclosure.py  # step 2
    ├── tab_org_score.py   # step 3
    ├── tab_risk.py        # step 4
    └── tab_audit.py       # step 5
```

The tabs are wired into a coherent flow by a **session-state layer** in
`helpers.py`. Each successful action writes to shared keys (extracted inventor,
last disclosure org, last risk level) and renders a **"Next step" card** pointing
the user at the tab they'd naturally open next. The sidebar shows a **pipeline
progress stepper** that lights up as each stage completes.

---

**Next:** [03 · API Reference](03-api-reference.md) for the endpoint contracts.
