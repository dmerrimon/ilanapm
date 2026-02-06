-- ============================================================================
-- ADD PASSWORD HASH COLUMN FOR PORTAL AUTHENTICATION
-- Date: 2026-02-06
-- Description: Add password_hash column to users table for portal login
-- ============================================================================

-- Add password_hash column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT;

-- Note: For existing users, password_hash will be NULL
-- Use the create_portal_users.py script to set passwords for portal access
