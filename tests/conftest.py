import pytest
import sqlite3
import json
from pathlib import Path
from app.database import init_db

@pytest.fixture
def db_session(tmp_path, monkeypatch):
    """
    Provides a temporary SQLite database session for testing.
    """
    db_file = tmp_path / "test_ipr_audit.db"
    # Monkeypatch the DB_PATH in app.database to use our temporary file
    monkeypatch.setattr("app.database.DB_PATH", db_file)
    
    # Initialize the database schema
    init_db()
    
    # Open a connection for the fixture to yield
    conn = sqlite3.connect(str(db_file))
    conn.row_factory = sqlite3.Row
    
    yield conn
    
    conn.close()

@pytest.fixture
def mock_patents():
    """
    Provides a sample of patent data from data/mock_patents.json.
    """
    mock_data_path = Path(__file__).resolve().parent.parent / "data" / "mock_patents.json"
    if not mock_data_path.exists():
        # Fallback for unexpected path issues
        return [
            {
                "title": "Mock Patent",
                "description": "Mock Description",
                "ip_type": "Patent",
                "organization": "Mock Org",
                "inventor_name": "Mock Inventor"
            }
        ]
        
    with open(mock_data_path, "r", encoding="utf-8") as f:
        return json.load(f)
