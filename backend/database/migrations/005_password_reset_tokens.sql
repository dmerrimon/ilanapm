-- Migration: Add password reset tokens table
-- Created: 2026-02-08
-- Purpose: Store temporary tokens for password reset functionality

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    expires_at TEXT NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast token lookup
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token
ON password_reset_tokens(token);

-- Index for email lookup
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_email
ON password_reset_tokens(email);

-- Index for expiry cleanup
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at
ON password_reset_tokens(expires_at);
