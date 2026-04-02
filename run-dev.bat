@REM Dev Script for running both backend and streamlit frontend simultaneously
@echo off

call .venv\Scripts\activate

echo Starting FastAPI backend...
start cmd /k "cd /d %cd% && call .venv\Scripts\activate && uvicorn app.main:app --reload"

echo Starting Streamlit frontend...
start cmd /k "cd /d %cd% && call .venv\Scripts\activate && streamlit run ui/dashboard.py"

echo Both services started 🚀