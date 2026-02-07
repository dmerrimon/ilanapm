-- Migration: Add FreshBooks OAuth tokens table
-- Created: 2026-02-07
-- Purpose: Persistent storage for FreshBooks access tokens and refresh tokens

CREATE TABLE IF NOT EXISTS freshbooks_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id TEXT NOT NULL UNIQUE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    account_id TEXT,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast lookup by org_id
CREATE INDEX IF NOT EXISTS idx_freshbooks_tokens_org_id ON freshbooks_tokens(org_id);

-- Index for expiration checks
CREATE INDEX IF NOT EXISTS idx_freshbooks_tokens_expires_at ON freshbooks_tokens(expires_at);
