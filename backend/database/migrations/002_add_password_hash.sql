-- ============================================================================
-- ADD PASSWORD HASH COLUMN FOR PORTAL AUTHENTICATION
-- Date: 2026-02-06
-- Description: Add password_hash column to users table for portal login
-- ============================================================================

-- Add password_hash column to users table
-- Note: SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN
-- This will fail if column already exists, which is handled by run_migration.py
ALTER TABLE users ADD COLUMN password_hash TEXT;

-- Note: For existing users, password_hash will be NULL
-- Use the create_portal_users.py script to set passwords for portal access
