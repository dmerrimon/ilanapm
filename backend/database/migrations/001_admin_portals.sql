-- ============================================================================
-- ADMIN PORTAL MIGRATION - Phase 6 Features
-- Date: 2026-02-06
-- Description: Add tables and columns for dual admin portals (customer + founder)
-- ============================================================================

-- 1. Add role column to users table (if not exists)
-- Roles: 'user', 'admin', 'super_admin', 'support'
-- Note: SQLite doesn't support ADD COLUMN IF NOT EXISTS, so we'll check first

-- For PostgreSQL (production):
-- ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'user' CHECK(role IN ('user', 'admin', 'super_admin', 'support'));

-- For SQLite (local dev), the column already exists in schema.sql


-- 2. Add billing fields to organizations table
-- Note: SQLite doesn't support IF NOT EXISTS with ADD COLUMN
-- We'll try to add and ignore errors if columns already exist

-- PostgreSQL: ALTER TABLE organizations ADD COLUMN IF NOT EXISTS ...
-- SQLite: ALTER TABLE organizations ADD COLUMN ... (will fail if exists, but we catch that)

ALTER TABLE organizations ADD COLUMN plan_type TEXT DEFAULT 'standard' CHECK(plan_type IN ('standard', 'pilot'));
ALTER TABLE organizations ADD COLUMN seat_rate DECIMAL(10, 2);
ALTER TABLE organizations ADD COLUMN billing_cycle TEXT DEFAULT 'monthly' CHECK(billing_cycle IN ('monthly', 'annual'));
ALTER TABLE organizations ADD COLUMN mrr DECIMAL(10, 2);
ALTER TABLE organizations ADD COLUMN next_billing_date DATE;

-- Note: stripe_customer_id and stripe_subscription_id already exist in schema.sql


-- 3. Create admin_transfer_requests table for admin ownership transfer
CREATE TABLE IF NOT EXISTS admin_transfer_requests (
    id SERIAL PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    from_user_id TEXT NOT NULL REFERENCES users(user_id),
    to_user_email TEXT NOT NULL,

    -- Transfer token
    token TEXT UNIQUE NOT NULL,
    message TEXT,

    -- Status tracking
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'accepted', 'expired', 'cancelled')),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    accepted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_admin_transfer_org ON admin_transfer_requests(org_id);
CREATE INDEX IF NOT EXISTS idx_admin_transfer_token ON admin_transfer_requests(token);
CREATE INDEX IF NOT EXISTS idx_admin_transfer_status ON admin_transfer_requests(status);


-- 4. Rename audit_logs to audit_log for consistency (optional)
-- Keeping as audit_logs since it's already in schema.sql


-- 5. Add additional audit_log columns for portal tracking
-- Note: audit_logs already has org_id, user_id, ip_address, action, resource_type, resource_id, metadata, timestamp
-- No additional columns needed


-- 6. Create portal_sessions table for NextAuth.js integration
CREATE TABLE IF NOT EXISTS portal_sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Session data
    session_token TEXT UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,

    -- Portal type (customer vs founder)
    portal_type TEXT NOT NULL CHECK(portal_type IN ('customer', 'founder')),

    -- Metadata
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_portal_sessions_user ON portal_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_portal_sessions_token ON portal_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_portal_sessions_expires ON portal_sessions(expires_at);


-- 7. Create stripe_events table for webhook event tracking
CREATE TABLE IF NOT EXISTS stripe_events (
    id SERIAL PRIMARY KEY,
    stripe_event_id TEXT UNIQUE NOT NULL,

    -- Event details
    event_type TEXT NOT NULL,  -- 'customer.subscription.created', 'invoice.payment_succeeded', etc.

    -- Related resources
    org_id TEXT REFERENCES organizations(org_id),
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,

    -- Event payload (JSON)
    payload TEXT,  -- Full Stripe event JSON

    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    error_message TEXT,

    -- Timestamps
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stripe_events_event_id ON stripe_events(stripe_event_id);
CREATE INDEX IF NOT EXISTS idx_stripe_events_org ON stripe_events(org_id);
CREATE INDEX IF NOT EXISTS idx_stripe_events_processed ON stripe_events(processed);
CREATE INDEX IF NOT EXISTS idx_stripe_events_received ON stripe_events(received_at);


-- 8. Create invoices table for billing history
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,

    -- Stripe reference
    stripe_invoice_id TEXT UNIQUE NOT NULL,
    stripe_payment_intent_id TEXT,

    -- Invoice details
    amount_cents INTEGER NOT NULL,
    amount_usd DECIMAL(10, 2) NOT NULL,
    currency TEXT DEFAULT 'USD',

    -- Billing period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Status
    status TEXT NOT NULL CHECK(status IN ('draft', 'open', 'paid', 'uncollectible', 'void')),
    paid_at TIMESTAMP,

    -- Line items (JSON)
    line_items TEXT,  -- JSON array of items

    -- PDF URL
    invoice_pdf_url TEXT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_invoices_org ON invoices(org_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_period ON invoices(period_start, period_end);


-- 9. Create payment_methods table
CREATE TABLE IF NOT EXISTS payment_methods (
    payment_method_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,

    -- Stripe reference
    stripe_payment_method_id TEXT UNIQUE NOT NULL,

    -- Card details (masked)
    card_brand TEXT,  -- 'visa', 'mastercard', 'amex', etc.
    card_last4 TEXT,
    card_exp_month INTEGER,
    card_exp_year INTEGER,

    -- Status
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_payment_methods_org ON payment_methods(org_id);
CREATE INDEX IF NOT EXISTS idx_payment_methods_default ON payment_methods(org_id, is_default);


-- 10. Create usage_analytics table for portal analytics
CREATE TABLE IF NOT EXISTS usage_analytics (
    id SERIAL PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    user_id TEXT REFERENCES users(user_id) ON DELETE SET NULL,

    -- Event tracking
    event_type TEXT NOT NULL,  -- 'template_generated', 'feedback_submitted', 'api_call', etc.
    event_category TEXT,  -- 'templates', 'feedback', 'analytics', etc.

    -- Event details (JSON)
    event_data TEXT,  -- JSON: {"template_type": "full_study", "country": "US", etc.}

    -- Metadata
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    ip_address TEXT
);

CREATE INDEX IF NOT EXISTS idx_usage_analytics_org ON usage_analytics(org_id);
CREATE INDEX IF NOT EXISTS idx_usage_analytics_user ON usage_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_analytics_timestamp ON usage_analytics(timestamp);
CREATE INDEX IF NOT EXISTS idx_usage_analytics_event_type ON usage_analytics(event_type);


-- 11. Add portal access columns to users table
ALTER TABLE users ADD COLUMN customer_portal_access BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN founder_portal_access BOOLEAN DEFAULT FALSE;


-- ============================================================================
-- POSTGRESQL-SPECIFIC ADJUSTMENTS
-- These will be handled by connection.py's schema translation
-- ============================================================================

-- SERIAL PRIMARY KEY (PostgreSQL) vs INTEGER PRIMARY KEY AUTOINCREMENT (SQLite)
-- Connection.py already handles this conversion

-- TEXT columns for JSON (works in both PostgreSQL and SQLite)
-- For PostgreSQL, we could use JSONB for better performance, but TEXT works for both


-- ============================================================================
-- DATA MIGRATION (Optional - for existing data)
-- ============================================================================

-- Set all existing users to 'user' role if not already set
UPDATE users SET role = 'user' WHERE role IS NULL;

-- Set default billing cycle for existing orgs
UPDATE organizations SET billing_cycle = 'monthly' WHERE billing_cycle IS NULL;

-- Calculate MRR for existing orgs (if seats_purchased and tier are set)
-- This would need custom logic based on pricing tiers
-- For now, we'll leave it NULL and calculate in the API


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify new tables exist:
-- SELECT name FROM sqlite_master WHERE type='table' AND name IN ('admin_transfer_requests', 'portal_sessions', 'stripe_events', 'invoices', 'payment_methods', 'usage_analytics');

-- Verify new columns exist:
-- PRAGMA table_info(organizations);
-- PRAGMA table_info(users);

-- For PostgreSQL:
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'organizations';
-- SELECT column_name FROM information_schema.columns WHERE table_name = 'users';
