#!/usr/bin/env python3
"""
Database migration runner for admin portal features

Usage:
    python run_migration.py                    # Run all pending migrations
    python run_migration.py --migration 001    # Run specific migration
    python run_migration.py --rollback         # Rollback last migration (not implemented yet)
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.connection import get_db_connection, DB_TYPE


def run_migration(migration_file: Path):
    """Run a single migration file"""
    print(f"\n{'='*80}")
    print(f"Running migration: {migration_file.name}")
    print(f"{'='*80}")

    with open(migration_file, 'r') as f:
        migration_sql = f.read()

    # PostgreSQL adjustments
    if DB_TYPE == "postgresql":
        # Replace SQLite syntax with PostgreSQL equivalents
        migration_sql = migration_sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
        migration_sql = migration_sql.replace("AUTOINCREMENT", "")

        # PostgreSQL supports IF NOT EXISTS for ADD COLUMN
        # Keep as-is

    with get_db_connection() as conn:
        # Split into individual statements
        statements = []
        current_statement = []

        for line in migration_sql.split('\n'):
            # Skip comment lines starting with --
            if line.strip().startswith('--'):
                continue

            current_statement.append(line)

            # End of statement
            if line.strip().endswith(';'):
                statement = '\n'.join(current_statement).strip()
                if statement and statement != ';':
                    statements.append(statement)
                current_statement = []

        print(f"Found {len(statements)} statements to execute\n")

        success_count = 0
        skip_count = 0
        error_count = 0

        for i, statement in enumerate(statements, 1):
            # Show first 100 chars of statement
            preview = statement[:100].replace('\n', ' ')
            print(f"[{i}/{len(statements)}] {preview}...", end=" ")

            try:
                cursor = conn.cursor()

                # Convert ? to %s for PostgreSQL
                if DB_TYPE == "postgresql" and '?' in statement:
                    statement = statement.replace('?', '%s')

                cursor.execute(statement)
                conn.commit()
                print("✓ Success")
                success_count += 1

            except Exception as e:
                error_str = str(e).lower()

                # Check if error is benign (already exists)
                if any(phrase in error_str for phrase in [
                    'already exists',
                    'duplicate column',
                    'duplicate key',
                    'relation already exists',
                    'constraint already exists'
                ]):
                    print("⊘ Skipped (already exists)")
                    skip_count += 1
                    conn.rollback()
                else:
                    print(f"✗ Error: {e}")
                    error_count += 1
                    conn.rollback()

                    # For critical errors, stop execution
                    if "syntax error" in error_str:
                        print(f"\n❌ Syntax error detected. Stopping migration.")
                        print(f"Statement:\n{statement}\n")
                        return False

            finally:
                cursor.close()

        print(f"\n{'='*80}")
        print(f"Migration complete: {success_count} succeeded, {skip_count} skipped, {error_count} errors")
        print(f"{'='*80}\n")

        return error_count == 0


def get_migration_files():
    """Get all migration files in order"""
    migrations_dir = Path(__file__).parent / "migrations"

    if not migrations_dir.exists():
        migrations_dir.mkdir(parents=True)
        print(f"Created migrations directory: {migrations_dir}")
        return []

    # Get all .sql files
    migration_files = sorted(migrations_dir.glob("*.sql"))
    return migration_files


def main():
    """Main migration runner"""
    print(f"\n🗄️  Database Migration Runner")
    print(f"Database Type: {DB_TYPE}")
    print(f"{'='*80}\n")

    # Parse command line args
    import argparse
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument('--migration', help="Run specific migration (e.g., 001)")
    parser.add_argument('--rollback', action='store_true', help="Rollback last migration (not implemented)")
    args = parser.parse_args()

    if args.rollback:
        print("❌ Rollback not implemented yet")
        return 1

    migration_files = get_migration_files()

    if not migration_files:
        print("No migration files found")
        return 0

    if args.migration:
        # Run specific migration
        target_file = None
        for f in migration_files:
            if args.migration in f.name:
                target_file = f
                break

        if not target_file:
            print(f"❌ Migration not found: {args.migration}")
            print(f"Available migrations:")
            for f in migration_files:
                print(f"  - {f.name}")
            return 1

        success = run_migration(target_file)
        return 0 if success else 1

    else:
        # Run all migrations
        print(f"Found {len(migration_files)} migration file(s):\n")
        for f in migration_files:
            print(f"  - {f.name}")
        print()

        all_success = True
        for migration_file in migration_files:
            success = run_migration(migration_file)
            if not success:
                all_success = False
                print(f"❌ Migration failed: {migration_file.name}")
                print("Stopping migration sequence")
                break

        if all_success:
            print("✅ All migrations completed successfully")
            return 0
        else:
            print("❌ Some migrations failed")
            return 1


if __name__ == "__main__":
    sys.exit(main())
