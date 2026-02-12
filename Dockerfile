# ─────────────────────────────────────────────────────────────────
# Dockerfile — IPR Audit & Patentability Scoring Tool
# ─────────────────────────────────────────────────────────────────
# Runs both the FastAPI backend (port 8000) and the Streamlit
# dashboard (port 8501) inside a single lightweight container.
#
# Build:
#   docker build -t ipr-audit-tool .
#
# Run:
#   docker run -p 8000:8000 -p 8501:8501 ipr-audit-tool
# ─────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code.
COPY . .

# Expose ports for FastAPI and Streamlit.
EXPOSE 8000
EXPOSE 8501

# Start script: launch backend in background, then Streamlit in foreground.
CMD bash -c "\
    uvicorn app.main:app --host 0.0.0.0 --port 8000 & \
    streamlit run ui/dashboard.py --server.port 8501 --server.address 0.0.0.0 \
"
