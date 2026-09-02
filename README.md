# 🔬 IPR Audit & Patentability Scoring Tool

A **lightweight, modular** prototype for institutional IP auditing, patent
similarity analysis (TF-IDF + cosine similarity), and organization-level IPR
scoring.

---

## Architecture

```
Automated-Patentability-Tool/
│
├── app/                        # FastAPI backend
│   ├── main.py                 # API entry-point (9 endpoints)
│   ├── models.py               # Pydantic request / response schemas
│   ├── database.py             # SQLite persistence (raw SQL, no ORM)
│   ├── credence_table.py       # IPR credence weights & tier logic
│   ├── score_engine.py         # Pure-function scoring engine
│   ├── patent_similarity.py    # TF-IDF + cosine similarity module
│   ├── audit.py                # Deterministic audit-report builder
│   └── extractor.py            # PDF text extraction & inventor parser
│
├── data/
│   └── mock_patents.json       # 10 reference patents for similarity testing
│
├── ui/                         # Streamlit frontend (5-tab pipeline)
│   ├── dashboard.py            # entry point
│   ├── components/ tabs/ styles/
│
├── docs/                       # MkDocs documentation source
├── mkdocs.yml                  # MkDocs config
├── requirements.txt            # runtime deps
├── requirements-docs.txt       # docs toolchain (MkDocs + Material)
├── Dockerfile
└── README.md                   # ← You are here
```

📖 **Full documentation** lives in [`docs/`](docs/README.md) and builds into a
browsable site with MkDocs — see [Documentation](#documentation) below.

---

## Quick Start

### 1. Prerequisites

- Python 3.10+ installed
- `pip` package manager

### 2. Install Dependencies

```bash
cd Automated-Patentability-Tool
pip install -r requirements.txt
```

### 3. Start the Backend (FastAPI)

```bash
uvicorn app.main:app --reload
```

The API is now running at **http://localhost:8000**.  
Interactive docs (Swagger UI) at **http://localhost:8000/docs**.

### 4. Start the Frontend (Streamlit)

Open a **second terminal**:

```bash
cd Automated-Patentability-Tool
streamlit run ui/dashboard.py
```

Dashboard opens at **http://localhost:8501**.

---

## Docker (Alternative)

```bash
docker build -t ipr-audit-tool .
docker run -p 8000:8000 -p 8501:8501 ipr-audit-tool
```

- Backend → http://localhost:8000
- Frontend → http://localhost:8501

---

## Testing & Security

### 1. Run Unit Tests

Use `pytest` to run the test suite:

```bash
python -m pytest tests/
```

### 2. Run Security Scan

Use `bandit` to perform a security audit of the `app` directory:

```bash
bandit -r app/
```

---

## API Endpoints

| Method | Path                              | Description                                   |
|--------|-----------------------------------|-----------------------------------------------|
| GET    | `/`                               | Root health alias                             |
| GET    | `/health`                         | Liveness probe                                |
| POST   | `/disclosure`                     | Submit a new IP disclosure (+ similarity for patents) |
| POST   | `/similarity`                     | Ad-hoc similarity check (does **not** persist)|
| POST   | `/upload-document`                | Upload PDF, extract inventor name             |
| GET    | `/organization/{org_name}/score`  | Aggregated IPR score card                     |
| GET    | `/organization/{org_name}/details`| Full disclosure list + score                  |
| GET    | `/organizations`                  | List all known organizations                  |
| GET    | `/audit/{org_name}`               | Structured audit & compliance report          |

Full request/response contracts are in the
[API Reference](docs/03-api-reference.md).

### Example: POST /disclosure

```json
{
    "title": "Solar-Powered Water Purifier",
    "description": "A novel device that uses concentrated solar energy to purify water.",
    "ip_type": "Patent",
    "organization": "Agnel Institute",
    "inventor_name": "Dr. Priya Sharma"
}
```

---

## Credence Table

| IP Type                                                   | Weight |
|-----------------------------------------------------------|--------|
| Patent                                                    | 3.0    |
| Industrial Design                                         | 2.0    |
| Copyright                                                 | 1.0    |
| Trademark                                                 | 1.5    |
| Layout Design of Integrated Circuit (LD of IC)            | 0.2    |
| Geographical Indication (GI)                              | 1.5    |
| Trade Secret (TS)                                         | 0.0    |
| Protection of Plant Varieties and Farmers' Rights (PVFR)  | 3.0    |

**IPR Score** = Σ (count × weight)

### Innovation Tiers

| Score Range | Tier       |
|-------------|------------|
| 0 – 5      | Emerging   |
| 6 – 15     | Developing |
| 16+         | Strong     |

---

## Patent Similarity & Risk

- **Algorithm**: TF-IDF vectorization + cosine similarity
- **Dataset**: 10 mock patents in `data/mock_patents.json`
- **Risk thresholds**:
  - `> 70%` → 🔴 High Risk
  - `40–70%` → 🟡 Medium Risk
  - `< 40%` → 🟢 Low Risk

---

## Tech Stack

| Layer     | Technology         |
|-----------|--------------------|
| Backend   | FastAPI + Uvicorn  |
| Database  | SQLite             |
| NLP       | scikit-learn       |
| PDF       | pdfplumber         |
| Frontend  | Streamlit          |
| Schemas   | Pydantic v2        |

---

## Documentation

Full docs live in [`docs/`](docs/README.md) and are built with **MkDocs +
Material**. The Markdown is readable as-is on GitHub, or you can serve/build the
polished site.

### Install the docs toolchain

```bash
pip install -r requirements-docs.txt
```

### Live-preview while editing

```bash
mkdocs serve
```

Opens a live-reloading dev server at **http://localhost:8000** (stop your
backend first, or it'll clash on that port).

### Build the static site

```bash
mkdocs build
```

Outputs a self-contained site to `./site/` (git-ignored).

### Deploy to GitHub Pages

```bash
mkdocs gh-deploy
```

Builds and pushes to the `gh-pages` branch in one command — your docs go live at
`https://andyferns.github.io/Automated-Patentability-Tool/`.

**Doc map:** [Getting Started](docs/01-getting-started.md) ·
[Architecture](docs/02-architecture.md) ·
[API Reference](docs/03-api-reference.md) ·
[Scoring Methodology](docs/04-scoring-methodology.md) ·
[User Guide](docs/05-user-guide.md)

---

## License

Internal prototype — for institutional use only.
