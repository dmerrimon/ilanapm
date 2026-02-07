-- Migration: Add FreshBooks customer mapping table
-- Created: 2026-02-07
-- Purpose: Map portal organizations to FreshBooks customers for invoice filtering

-- This solves the ownership transfer problem: instead of matching by email
-- (which breaks when ownership changes), we map organizations to FreshBooks
-- customer IDs which persist across ownership changes.

CREATE TABLE IF NOT EXISTS freshbooks_customer_mapping (
    org_id TEXT PRIMARY KEY,
    freshbooks_customer_id TEXT NOT NULL,
    freshbooks_customer_name TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for reverse lookup (find org by FreshBooks customer)
CREATE INDEX IF NOT EXISTS idx_freshbooks_customer_mapping_customer_id
ON freshbooks_customer_mapping(freshbooks_customer_id);
