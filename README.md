# 🔬 IPR Audit & Patentability Scoring Tool

A **lightweight, modular** prototype for institutional IP auditing, patent
similarity analysis (TF-IDF + cosine similarity), and organization-level IPR
scoring.

---

## Architecture

```
ipr-prototype/
│
├── app/                        # FastAPI backend
│   ├── main.py                 # API entry-point (4 endpoints)
│   ├── models.py               # Pydantic request / response schemas
│   ├── database.py             # SQLite persistence (raw SQL, no ORM)
│   ├── credence_table.py       # IPR credence weights & tier logic
│   ├── score_engine.py         # Pure-function scoring engine
│   ├── patent_similarity.py    # TF-IDF + cosine similarity module
│   └── extractor.py            # PDF text extraction & inventor regex
│
├── data/
│   └── mock_patents.json       # 10 mock patents for similarity testing
│
├── ui/
│   └── dashboard.py            # Streamlit frontend (4 tabs)
│
├── requirements.txt
├── Dockerfile
└── README.md                   # ← You are here
```

---

## Quick Start

### 1. Prerequisites

- Python 3.10+ installed
- `pip` package manager

### 2. Install Dependencies

```bash
cd ipr-prototype
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
cd ipr-prototype
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

| Method | Path                              | Description                           |
|--------|-----------------------------------|---------------------------------------|
| POST   | `/disclosure`                     | Submit a new IP disclosure (JSON)     |
| POST   | `/upload-document`                | Upload PDF, extract inventor name     |
| GET    | `/organization/{org_name}/score`  | Aggregated IPR score card             |
| GET    | `/organization/{org_name}/details`| Full disclosure list + score          |
| GET    | `/organizations`                  | List all known organizations          |

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

## License

Internal prototype — for institutional use only.
