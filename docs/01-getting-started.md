# 01 · Getting Started

Everything you need to go from a fresh clone to a running app. Pick the path
that suits you: **local dev**, the **Windows one-click script**, or **Docker**.

---

## Prerequisites

- **Python 3.10+** (the Docker image uses 3.11)
- **pip** package manager
- ~200 MB of disk for dependencies (scikit-learn is the heavy one)

That's it. No external database, no API keys, no network access required at
runtime — the reference dataset ships in the repo.

---

## The pieces you'll run

The tool is **two processes**:

1. **FastAPI backend** on port **8000** — all the logic and data live here.
2. **Streamlit frontend** on port **8501** — the dashboard, which talks to the
   backend over HTTP.

You need **both** running for the full experience. The frontend reads the
backend's address from the `API_BASE` environment variable, which defaults to
`http://localhost:8000`.

---

## Option A — Local dev (any OS)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

Using a virtual environment is strongly recommended:

```bash
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### 2. Start the backend

```bash
uvicorn app.main:app --reload
```

- API root: **http://localhost:8000**
- Interactive Swagger docs: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

The SQLite database (`ipr_audit.db`) is created automatically in the project
root on first launch — no migration step needed.

### 3. Start the frontend

Open a **second terminal** (leave the backend running):

```bash
streamlit run ui/dashboard.py
```

The dashboard opens at **http://localhost:8501**. Check the sidebar — the
**Backend Status** badge should read *Connected*. If it says *Unreachable*, your
backend isn't up (or isn't on port 8000).

---

## Option B — Windows one-click

There's a batch script that launches both processes for you. It expects a
virtual environment named `.venv` in the project root.

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

run-dev.bat
```

`run-dev.bat` opens two new terminals — one for the backend (`--reload`) and one
for Streamlit — and activates the venv in each. Handy for day-to-day dev.

---

## Option C — Docker

The image runs **both** processes inside a single container.

```bash
docker build -t ipr-audit-tool .
docker run -p 8000:8000 -p 8501:8501 ipr-audit-tool
```

- Backend → http://localhost:8000
- Frontend → http://localhost:8501

> **Heads up:** the container's SQLite file lives inside the container. If you
> want your data to survive a container restart, mount a volume:
> ```bash
> docker run -p 8000:8000 -p 8501:8501 -v "$(pwd)/data-vol:/app" ipr-audit-tool
> ```

---

## Pointing the frontend at a different backend

If your backend isn't on `localhost:8000` (e.g. a remote host or a different
port), set `API_BASE` before starting Streamlit:

```bash
# macOS / Linux
API_BASE="http://my-host:9000" streamlit run ui/dashboard.py

# Windows (PowerShell)
$env:API_BASE="http://my-host:9000"; streamlit run ui/dashboard.py
```

---

## Verifying it works

Once both are up, a quick smoke test:

```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

Then open the dashboard, go to **tab 2 (Add Disclosure)**, submit a patent, and
watch the risk gauge appear. If that works end-to-end, you're good.

---

## Testing & security scan

### Run the unit tests

```bash
python -m pytest tests/
```

The suite covers the extractor, the scoring engine, and the similarity module.

Want coverage?

```bash
python -m pytest tests/ --cov=app
```

### Run the security scan

```bash
bandit -r app/
```

`bandit` statically audits the `app/` package for common Python security issues.

---

**Next:** [02 · Architecture](02-architecture.md) to see how it all fits
together, or [05 · User Guide](05-user-guide.md) to start clicking around.
