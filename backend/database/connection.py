"""
Database connection management for feedback storage and licensing

Supports both PostgreSQL (production on Render) and SQLite (local development)
"""

import sqlite3
import os
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

# Check if running on Render with PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # PostgreSQL for production (Render)
    import psycopg2
    from psycopg2.extras import RealDictCursor
    DB_TYPE = "postgresql"
else:
    # SQLite for local development
    DB_PATH = Path(__file__).parent / "feedback.db"
    DB_TYPE = "sqlite"


def init_db():
    """Initialize database with schema"""
    schema_path = Path(__file__).parent / "schema.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    if DB_TYPE == "postgresql":
        # PostgreSQL - adjust schema syntax
        # Replace SQLite-specific syntax with PostgreSQL equivalents
        schema_sql = schema_sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        schema_sql = schema_sql.replace("AUTOINCREMENT", "")
        schema_sql = schema_sql.replace("BOOLEAN", "BOOLEAN")
        schema_sql = schema_sql.replace("IF NOT EXISTS", "IF NOT EXISTS")

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute(schema_sql)
        conn.commit()
        conn.close()
    else:
        # SQLite
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()


class PostgreSQLCursor:
    """Wrapper cursor that converts SQLite ? placeholders to PostgreSQL %s"""
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        # Convert ? to %s for PostgreSQL
        if '?' in query:
            query = query.replace('?', '%s')
        return self._cursor.execute(query, params)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchmany(self, size=None):
        return self._cursor.fetchmany(size)

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class PostgreSQLConnection:
    """Wrapper connection that returns our custom cursor"""
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return PostgreSQLCursor(self._conn.cursor())

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        return self._conn.close()

    def __getattr__(self, name):
        return getattr(self._conn, name)


@contextmanager
def get_db_connection():
    """
    Get database connection context manager

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ...")
    """
    if DB_TYPE == "postgresql":
        # PostgreSQL connection with query translation
        raw_conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        conn = PostgreSQLConnection(raw_conn)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    else:
        # SQLite connection
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()


def get_db():
    """Get database connection (non-context manager version)"""
    if DB_TYPE == "postgresql":
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


__all__ = ["get_db_connection", "get_db", "init_db", "DB_TYPE"]
