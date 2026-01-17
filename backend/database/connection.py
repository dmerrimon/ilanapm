"""
Database connection management for feedback storage

Uses SQLite for simplicity. Can migrate to PostgreSQL for production.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

# Database file location
DB_PATH = Path(__file__).parent / "feedback.db"


def init_db():
    """Initialize database with schema"""
    schema_path = Path(__file__).parent / "schema.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    conn = sqlite3.connect(DB_PATH)
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


@contextmanager
def get_db_connection():
    """
    Get database connection context manager

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_db() -> sqlite3.Connection:
    """Get database connection (non-context manager version)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


__all__ = ["get_db_connection", "get_db", "init_db"]
