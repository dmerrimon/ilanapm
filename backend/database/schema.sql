-- Task Outcomes Feedback Schema
-- Stores predicted vs actual durations to enable ML learning over time

CREATE TABLE IF NOT EXISTS task_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Task identification
    task_id TEXT NOT NULL,
    task_name TEXT NOT NULL,
    category TEXT,  -- Regulatory, Operational, Site Management, etc.

    -- Prediction data
    predicted_duration_days INTEGER,
    predicted_confidence REAL,  -- 0-1 confidence score
    model_version TEXT,  -- Which model made the prediction

    -- Actual outcome
    actual_duration_days INTEGER NOT NULL,
    actual_start_date DATE,
    actual_end_date DATE,

    -- Context (for learning patterns)
    country_code TEXT,  -- ISO code (US, KE, VN, etc.)
    authority TEXT,  -- FDA, PPB, MHRA, etc.
    study_phase TEXT,  -- Phase I, II, III, IV
    therapeutic_area TEXT,

    -- Accuracy metrics
    variance_days INTEGER,  -- actual - predicted
    variance_percent REAL,  -- (variance / predicted) * 100
    was_accurate BOOLEAN,  -- Within ±20% threshold

    -- Metadata
    project_id TEXT,  -- MS Project file identifier
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recorded_by TEXT  -- User who submitted feedback
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_country_authority ON task_outcomes(country_code, authority);
CREATE INDEX IF NOT EXISTS idx_category ON task_outcomes(category);
CREATE INDEX IF NOT EXISTS idx_recorded_at ON task_outcomes(recorded_at);
CREATE INDEX IF NOT EXISTS idx_accuracy ON task_outcomes(was_accurate);

-- Prediction accuracy summary view
CREATE VIEW IF NOT EXISTS prediction_accuracy_summary AS
SELECT
    country_code,
    authority,
    category,
    COUNT(*) as total_predictions,
    AVG(predicted_confidence) as avg_confidence,
    AVG(ABS(variance_days)) as avg_error_days,
    AVG(ABS(variance_percent)) as avg_error_percent,
    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as accuracy_rate,
    MIN(recorded_at) as first_recorded,
    MAX(recorded_at) as last_recorded
FROM task_outcomes
GROUP BY country_code, authority, category;

-- ============================================================================
-- MULTI-TENANCY & LICENSING TABLES
-- Added: 2026-01-23 for enterprise distribution
-- ============================================================================

-- Organizations table - Each paying customer organization
CREATE TABLE IF NOT EXISTS organizations (
    org_id TEXT PRIMARY KEY,
    org_name TEXT NOT NULL,
    tier TEXT NOT NULL CHECK(tier IN ('professional', 'enterprise')),

    -- Subscription details
    seats_purchased INTEGER NOT NULL CHECK(seats_purchased > 0),
    seats_used INTEGER DEFAULT 0 CHECK(seats_used >= 0),
    subscription_start DATE NOT NULL,
    subscription_end DATE NOT NULL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'suspended', 'canceled', 'expired')),

    -- Stripe integration
    stripe_customer_id TEXT UNIQUE,
    stripe_subscription_id TEXT,

    -- Enterprise features
    sso_enabled BOOLEAN DEFAULT 0,
    sso_provider TEXT,  -- 'okta', 'azure_ad', 'google', etc.

    -- Contact & metadata
    primary_contact_email TEXT,
    primary_contact_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table - Individual users within organizations
CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,

    -- Role within organization
    role TEXT DEFAULT 'user' CHECK(role IN ('user', 'admin', 'super_admin', 'support')),

    -- User details
    first_name TEXT,
    last_name TEXT,

    -- Status
    is_active BOOLEAN DEFAULT 1,
    last_login TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- License keys table - License keys for organizations
CREATE TABLE IF NOT EXISTS license_keys (
    license_key TEXT PRIMARY KEY,
    org_id TEXT NOT NULL REFERENCES organizations(org_id) ON DELETE CASCADE,

    -- License details
    tier TEXT NOT NULL CHECK(tier IN ('professional', 'enterprise')),
    seats INTEGER NOT NULL CHECK(seats > 0),

    -- Validity
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at DATE,
    is_active BOOLEAN DEFAULT 1,

    -- Metadata
    created_by TEXT,  -- Who generated this key (admin user_id)
    notes TEXT
);

-- Activations table - Desktop add-in activations
CREATE TABLE IF NOT EXISTS activations (
    activation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    license_key TEXT REFERENCES license_keys(license_key),

    -- Device identification
    device_id TEXT NOT NULL,  -- Hashed MAC address
    device_name TEXT,  -- Windows computer name

    -- Activation token (JWT)
    activation_token TEXT NOT NULL,
    token_expires_at TIMESTAMP NOT NULL,

    -- Status
    is_active BOOLEAN DEFAULT 1,
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deactivated_at TIMESTAMP,

    -- Last activity tracking
    last_api_call TIMESTAMP,
    api_call_count INTEGER DEFAULT 0,

    -- Metadata
    ms_project_version TEXT,  -- 2016, 2019, 2021, 365
    addin_version TEXT,

    -- Ensure one active activation per device per user
    UNIQUE(user_id, device_id)
);

-- Audit logs table - Track all critical actions
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id TEXT PRIMARY KEY,

    -- Who and where
    org_id TEXT REFERENCES organizations(org_id),
    user_id TEXT REFERENCES users(user_id),
    ip_address TEXT,

    -- What happened
    action TEXT NOT NULL,  -- 'license_activated', 'seat_deactivated', 'subscription_canceled', etc.
    resource_type TEXT,  -- 'organization', 'user', 'license', 'activation'
    resource_id TEXT,

    -- Details (JSON blob)
    metadata TEXT,  -- JSON: {"old_value": "...", "new_value": "...", etc.}

    -- When
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_org ON users(org_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_license_keys_org ON license_keys(org_id);
CREATE INDEX IF NOT EXISTS idx_activations_user ON activations(user_id);
CREATE INDEX IF NOT EXISTS idx_activations_device ON activations(device_id);
CREATE INDEX IF NOT EXISTS idx_activations_active ON activations(is_active);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org ON audit_logs(org_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_organizations_stripe ON organizations(stripe_customer_id);
