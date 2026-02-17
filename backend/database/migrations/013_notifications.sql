-- Migration 013: Notifications System
-- Created: 2026-02-13
-- Description: Add notifications table for escalation alerts

-- ============================================================================
-- Notifications Table
-- ============================================================================

-- Stores all notifications sent to users
CREATE TABLE IF NOT EXISTS notifications (
    notification_id TEXT PRIMARY KEY,
    notification_type TEXT NOT NULL,  -- 'escalation', 'pattern', 'health_alert'

    -- Recipient
    recipient_user_id TEXT NOT NULL REFERENCES users(user_id),
    recipient_email TEXT NOT NULL,

    -- Content
    subject TEXT NOT NULL,
    body_html TEXT NOT NULL,
    body_text TEXT NOT NULL,

    -- Related entity
    related_entity_id TEXT NOT NULL,  -- escalation_id, pattern_id, etc.
    related_entity_type TEXT NOT NULL,  -- 'escalation', 'pattern', 'health_snapshot'

    -- Priority and status
    priority TEXT NOT NULL DEFAULT 'medium',  -- 'high', 'medium', 'low'
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'sent', 'failed'

    -- Timestamps
    created_at TEXT DEFAULT (NOW()),
    sent_at TEXT,

    -- Error tracking
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_notifications_recipient
    ON notifications(recipient_user_id);

CREATE INDEX IF NOT EXISTS idx_notifications_status
    ON notifications(status);

CREATE INDEX IF NOT EXISTS idx_notifications_type
    ON notifications(notification_type);

CREATE INDEX IF NOT EXISTS idx_notifications_created
    ON notifications(created_at);

CREATE INDEX IF NOT EXISTS idx_notifications_entity
    ON notifications(related_entity_id, related_entity_type);

-- ============================================================================
-- Update Users Table to Add Notification Preferences
-- ============================================================================

-- Add notification preferences column to users table (if not exists)
-- In production, this would be ALTER TABLE but SQLite has limitations
-- For now, assume users table already has notification_preferences column
-- or handle via application logic

-- Example preferences JSON:
-- {
--     "notify_director_escalations": true,
--     "notify_vp_escalations": true,
--     "notify_signal_detected": false,
--     "notify_pattern_detected": true,
--     "notify_health_critical": true,
--     "digest_mode": "immediate"  // "immediate", "daily", "weekly"
-- }

-- ============================================================================
-- Notification Digest Queue (for batched notifications)
-- ============================================================================

CREATE TABLE IF NOT EXISTS notification_digest_queue (
    queue_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id),
    digest_type TEXT NOT NULL,  -- 'daily', 'weekly'
    notification_ids TEXT NOT NULL,  -- JSON array of notification IDs
    scheduled_for TEXT NOT NULL,  -- When to send digest
    status TEXT DEFAULT 'pending',  -- 'pending', 'sent', 'failed'
    created_at TEXT DEFAULT (NOW()),
    sent_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_digest_queue_user
    ON notification_digest_queue(user_id);

CREATE INDEX IF NOT EXISTS idx_digest_queue_scheduled
    ON notification_digest_queue(scheduled_for);

CREATE INDEX IF NOT EXISTS idx_digest_queue_status
    ON notification_digest_queue(status);

-- ============================================================================
-- Documentation
-- ============================================================================

-- Notification Flow:
-- 1. Escalation created → notification_service.notify_escalation_created()
-- 2. Notification created with status='pending'
-- 3. If digest_mode='immediate': send immediately
-- 4. If digest_mode='daily'/'weekly': queue for digest
-- 5. Background job processes pending notifications
-- 6. Update status to 'sent' or 'failed'
--
-- Digest Flow:
-- 1. Multiple notifications queued for user
-- 2. Background job aggregates by digest_type
-- 3. Creates single digest email with all notifications
-- 4. Sends digest at scheduled time
-- 5. Marks individual notifications as 'sent'

-- ============================================================================
-- Migration Complete
-- ============================================================================
