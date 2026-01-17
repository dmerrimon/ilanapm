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
