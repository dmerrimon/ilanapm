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
    import psycopg
    from psycopg.rows import dict_row
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

        conn = psycopg.connect(DATABASE_URL)

        # Split schema into individual statements
        # Remove comments and split by semicolon
        lines = []
        for line in schema_sql.split('\n'):
            # Skip comment lines
            if not line.strip().startswith('--'):
                lines.append(line)

        cleaned_sql = '\n'.join(lines)
        statements = [s.strip() for s in cleaned_sql.split(';') if s.strip()]

        # Execute each statement in its own transaction
        # This prevents one failure from aborting the entire batch
        success_count = 0
        error_count = 0

        for statement in statements:
            if statement.strip():
                try:
                    cursor = conn.cursor()
                    cursor.execute(statement)
                    conn.commit()
                    success_count += 1
                except Exception as e:
                    conn.rollback()
                    # Only show error if it's not "already exists"
                    if "already exists" not in str(e).lower():
                        print(f"Error executing statement: {statement[:80]}...")
                        print(f"Error: {e}")
                    error_count += 1
                finally:
                    cursor.close()

        print(f"Schema initialization: {success_count} statements succeeded, {error_count} skipped/failed")
        conn.close()
    else:
        # SQLite
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(schema_sql)
        conn.commit()
        conn.close()


def run_migrations():
    """Run all SQL migrations in order"""
    migrations_dir = Path(__file__).parent / "migrations"

    if not migrations_dir.exists():
        print("No migrations directory found, skipping migrations")
        return

    # Get all .sql files in migrations directory, sorted by name
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("No migration files found")
        return

    print(f"Found {len(migration_files)} migration file(s)")

    if DB_TYPE == "postgresql":
        conn = psycopg.connect(DATABASE_URL)

        for migration_file in migration_files:
            print(f"Running migration: {migration_file.name}")

            with open(migration_file, 'r') as f:
                migration_sql = f.read()

            # Replace SQLite-specific syntax
            migration_sql = migration_sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
            migration_sql = migration_sql.replace("AUTOINCREMENT", "")

            # Split into statements
            lines = []
            for line in migration_sql.split('\n'):
                if not line.strip().startswith('--'):
                    lines.append(line)

            cleaned_sql = '\n'.join(lines)
            statements = [s.strip() for s in cleaned_sql.split(';') if s.strip()]

            for statement in statements:
                if statement.strip():
                    try:
                        cursor = conn.cursor()
                        cursor.execute(statement)
                        conn.commit()
                        cursor.close()
                    except Exception as e:
                        conn.rollback()
                        if "already exists" not in str(e).lower() and "duplicate column" not in str(e).lower():
                            print(f"Migration warning: {e}")

            print(f"✅ Completed: {migration_file.name}")

        conn.close()
    else:
        # SQLite
        conn = sqlite3.connect(DB_PATH)

        for migration_file in migration_files:
            print(f"Running migration: {migration_file.name}")

            with open(migration_file, 'r') as f:
                migration_sql = f.read()

            try:
                conn.executescript(migration_sql)
                conn.commit()
                print(f"✅ Completed: {migration_file.name}")
            except Exception as e:
                conn.rollback()
                print(f"Migration error: {e}")

        conn.close()

    print("✅ All migrations completed")


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

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    def __iter__(self):
        return iter(self._cursor)

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

    def execute(self, query, params=None):
        # Support direct execute on connection
        cursor = self.cursor()
        cursor.execute(query, params)
        return cursor

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
        raw_conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
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
        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


__all__ = ["get_db_connection", "get_db", "init_db", "run_migrations", "DB_TYPE"]
