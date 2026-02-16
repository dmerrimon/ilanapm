-- Migration 020: Seed Tracker Definitions
-- Description: Populates tracker_definitions with Risk Log, TMF, Budget, and Vendor trackers
-- Author: Implementation Script
-- Date: 2026-02-16
-- PostgreSQL-compatible version

-- This migration seeds the tracker_definitions table with 4 standard tracker types:
-- 1. Risk Log (TDEF_RISK_001)
-- 2. TMF Completeness Tracker (TDEF_TMF_001)
-- 3. Budget Tracker (TDEF_BUDGET_001)
-- 4. Vendor Performance Tracker (TDEF_VENDOR_001)

-- Each tracker includes:
-- - Schema definition (required/optional fields with data types)
-- - Signal extraction rules (hardcoded escalation thresholds)

-- ==================================================================
-- 1. RISK LOG TRACKER
-- ==================================================================

INSERT INTO tracker_definitions (
    tracker_def_id,
    tracker_name,
    tracker_type,
    description,
    schema_definition,
    signal_extraction_rules,
    version,
    created_at
) VALUES (
    'TDEF_RISK_001',
    'Risk Log',
    'risk_log',
    'Study risk register tracking with priority-based escalations',
    '{
        "required_fields": [
            {
                "field_name": "risk_number",
                "display_name": "Risk #",
                "data_type": "integer",
                "description": "Unique risk identifier"
            },
            {
                "field_name": "category",
                "display_name": "Risk Category",
                "data_type": "string",
                "description": "Risk category (Site, Clinical, Regulatory, Data, etc.)"
            },
            {
                "field_name": "risk_detail",
                "display_name": "Risk Description",
                "data_type": "string",
                "description": "Detailed description of the risk"
            },
            {
                "field_name": "priority",
                "display_name": "Priority",
                "data_type": "integer",
                "description": "Risk priority (1-9, calculated as Impact × Probability)"
            },
            {
                "field_name": "status",
                "display_name": "Status",
                "data_type": "string",
                "description": "Risk status (Open, In Progress, Mitigated, Closed)"
            }
        ],
        "optional_fields": [
            {
                "field_name": "impact",
                "display_name": "Impact (1-3)",
                "data_type": "integer",
                "description": "Impact level: 1=Low, 2=Medium, 3=High"
            },
            {
                "field_name": "probability",
                "display_name": "Probability (1-3)",
                "data_type": "integer",
                "description": "Probability: 1=Low, 2=Medium, 3=High"
            },
            {
                "field_name": "mitigation_plan",
                "display_name": "Mitigation Plan",
                "data_type": "string",
                "description": "Detailed mitigation strategy"
            },
            {
                "field_name": "owner",
                "display_name": "Risk Owner",
                "data_type": "string",
                "description": "Person responsible for managing the risk"
            },
            {
                "field_name": "target_date",
                "display_name": "Target Resolution Date",
                "data_type": "date",
                "description": "Target date for risk mitigation"
            },
            {
                "field_name": "actual_date",
                "display_name": "Actual Resolution Date",
                "data_type": "date",
                "description": "Actual date risk was resolved"
            },
            {
                "field_name": "escalation_notes",
                "display_name": "Escalation Notes",
                "data_type": "string",
                "description": "Notes about escalations to Director/VP"
            }
        ],
        "common_variations": {
            "risk_number": ["Risk #", "Risk ID", "ID", "Risk Number", "Number"],
            "category": ["Risk Category", "Category", "Type", "Risk Type"],
            "risk_detail": ["Risk Description", "Description", "Risk", "Risk Detail", "Details"],
            "priority": ["Priority", "Risk Priority", "Score", "Risk Score"],
            "status": ["Status", "Risk Status", "State"],
            "impact": ["Impact", "Severity", "Impact Level"],
            "probability": ["Probability", "Likelihood", "Chance"],
            "owner": ["Owner", "Risk Owner", "Responsible Party", "Assigned To"]
        }
    }',
    '{
        "rules": [
            {
                "rule_id": "RISK_PRIORITY_6_DIRECTOR",
                "signal_type": "risk_high_priority",
                "priority": 7,
                "escalation_level": "director",
                "description": "Priority ≥6 requires Director escalation",
                "condition": {
                    "all_of": [
                        {"field": "priority", "operator": "greater_than_or_equal", "value": 6},
                        {"field": "status", "operator": "not_equals", "value": "Closed"}
                    ]
                }
            },
            {
                "rule_id": "RISK_PRIORITY_9_VP",
                "signal_type": "risk_critical_priority",
                "priority": 9,
                "escalation_level": "vp",
                "description": "Priority 9 requires VP escalation",
                "condition": {
                    "all_of": [
                        {"field": "priority", "operator": "equals", "value": 9},
                        {"field": "status", "operator": "not_equals", "value": "Closed"}
                    ]
                }
            },
            {
                "rule_id": "RISK_NO_MITIGATION",
                "signal_type": "risk_no_mitigation_plan",
                "priority": 7,
                "escalation_level": "director",
                "description": "High priority risk (≥6) with no mitigation plan",
                "condition": {
                    "all_of": [
                        {"field": "priority", "operator": "greater_than_or_equal", "value": 6},
                        {"field": "mitigation_plan", "operator": "is_empty"},
                        {"field": "status", "operator": "not_equals", "value": "Closed"}
                    ]
                }
            },
            {
                "rule_id": "RISK_OVERDUE",
                "signal_type": "risk_overdue",
                "priority": 7,
                "escalation_level": "director",
                "description": "Risk target date passed without resolution",
                "condition": {
                    "all_of": [
                        {"field": "target_date", "operator": "is_past"},
                        {"field": "actual_date", "operator": "is_empty"},
                        {"field": "status", "operator": "not_equals", "value": "Closed"}
                    ]
                }
            },
            {
                "rule_id": "RISK_ESCALATION_NOTED",
                "signal_type": "risk_escalated",
                "priority": 8,
                "escalation_level": "vp",
                "description": "Explicit escalation noted in risk",
                "condition": {
                    "field": "escalation_notes", "operator": "is_not_empty"
                }
            }
        ]
    }',
    '1.0',
    datetime('now')
);

-- ==================================================================
-- 2. TMF COMPLETENESS TRACKER
-- ==================================================================

INSERT INTO tracker_definitions (
    tracker_def_id,
    tracker_name,
    tracker_type,
    description,
    schema_definition,
    signal_extraction_rules,
    version,
    created_at
) VALUES (
    'TDEF_TMF_001',
    'TMF Completeness Tracker',
    'tmf_completeness',
    'Trial Master File completeness tracking with document status monitoring',
    '{
        "required_fields": [
            {
                "field_name": "artifact_number",
                "display_name": "Artifact #",
                "data_type": "string",
                "description": "TMF artifact identifier"
            },
            {
                "field_name": "artifact_name",
                "display_name": "Document Name",
                "data_type": "string",
                "description": "Name of TMF document/artifact"
            },
            {
                "field_name": "status",
                "display_name": "Status",
                "data_type": "string",
                "description": "Document status (Complete, Missing, Pending, In Review)"
            }
        ],
        "optional_fields": [
            {
                "field_name": "completion_pct",
                "display_name": "Completion %",
                "data_type": "integer",
                "description": "Overall TMF completion percentage"
            },
            {
                "field_name": "responsible_party",
                "display_name": "Owner",
                "data_type": "string",
                "description": "Person responsible for document"
            },
            {
                "field_name": "target_date",
                "display_name": "Due Date",
                "data_type": "date",
                "description": "Target completion date"
            },
            {
                "field_name": "actual_date",
                "display_name": "Completion Date",
                "data_type": "date",
                "description": "Actual completion date"
            },
            {
                "field_name": "reviewer",
                "display_name": "Reviewer",
                "data_type": "string",
                "description": "Document reviewer"
            },
            {
                "field_name": "notes",
                "display_name": "Notes",
                "data_type": "string",
                "description": "Additional notes or comments"
            }
        ],
        "common_variations": {
            "artifact_number": ["Artifact #", "Artifact Number", "Artifact ID", "Doc #", "Document Number"],
            "artifact_name": ["Artifact Name", "Document Name", "Name", "Document", "Artifact"],
            "status": ["Status", "Document Status", "State", "Artifact Status"],
            "completion_pct": ["Completion %", "Completion Percentage", "% Complete", "Completeness"],
            "responsible_party": ["Owner", "Responsible Party", "Assignee", "Assigned To"]
        }
    }',
    '{
        "rules": [
            {
                "rule_id": "TMF_LOW_COMPLETION",
                "signal_type": "tmf_low_completion",
                "priority": 6,
                "escalation_level": "director",
                "description": "TMF completion <75% requires Director attention",
                "condition": {
                    "field": "completion_pct", "operator": "less_than", "value": 75
                }
            },
            {
                "rule_id": "TMF_CRITICAL_COMPLETION",
                "signal_type": "tmf_critical_completion",
                "priority": 8,
                "escalation_level": "vp",
                "description": "TMF completion <60% requires VP escalation",
                "condition": {
                    "field": "completion_pct", "operator": "less_than", "value": 60
                }
            },
            {
                "rule_id": "TMF_MISSING_DOC",
                "signal_type": "tmf_missing_document",
                "priority": 7,
                "escalation_level": "director",
                "description": "Missing TMF document",
                "condition": {
                    "field": "status", "operator": "equals", "value": "Missing"
                }
            },
            {
                "rule_id": "TMF_OVERDUE",
                "signal_type": "tmf_document_overdue",
                "priority": 7,
                "escalation_level": "director",
                "description": "TMF document overdue",
                "condition": {
                    "all_of": [
                        {"field": "target_date", "operator": "is_past"},
                        {"field": "status", "operator": "not_equals", "value": "Complete"}
                    ]
                }
            },
            {
                "rule_id": "TMF_PENDING_REVIEW",
                "signal_type": "tmf_pending_review",
                "priority": 6,
                "escalation_level": "director",
                "description": "TMF document pending review >14 days",
                "condition": {
                    "all_of": [
                        {"field": "status", "operator": "equals", "value": "Pending Review"},
                        {"field": "target_date", "operator": "older_than_days", "value": 14}
                    ]
                }
            }
        ]
    }',
    '1.0',
    datetime('now')
);

-- ==================================================================
-- 3. BUDGET TRACKER
-- ==================================================================

INSERT INTO tracker_definitions (
    tracker_def_id,
    tracker_name,
    tracker_type,
    description,
    schema_definition,
    signal_extraction_rules,
    version,
    created_at
) VALUES (
    'TDEF_BUDGET_001',
    'Budget Tracker',
    'budget_tracker',
    'Study budget and spend tracking with variance monitoring',
    '{
        "required_fields": [
            {
                "field_name": "category",
                "display_name": "Budget Category",
                "data_type": "string",
                "description": "Budget line item category (Site Costs, Vendor, Staff, etc.)"
            },
            {
                "field_name": "budgeted_amount",
                "display_name": "Budgeted Amount",
                "data_type": "decimal",
                "description": "Original budgeted amount"
            },
            {
                "field_name": "actual_spent",
                "display_name": "Actual Spent",
                "data_type": "decimal",
                "description": "Actual amount spent to date"
            },
            {
                "field_name": "variance_pct",
                "display_name": "Variance %",
                "data_type": "decimal",
                "description": "Variance percentage (positive = over budget)"
            }
        ],
        "optional_fields": [
            {
                "field_name": "forecast_amount",
                "display_name": "Forecast Amount",
                "data_type": "decimal",
                "description": "Forecasted final amount"
            },
            {
                "field_name": "committed",
                "display_name": "Committed Amount",
                "data_type": "decimal",
                "description": "Committed but not yet spent"
            },
            {
                "field_name": "notes",
                "display_name": "Notes",
                "data_type": "string",
                "description": "Budget notes or explanations"
            },
            {
                "field_name": "owner",
                "display_name": "Budget Owner",
                "data_type": "string",
                "description": "Person responsible for budget line"
            }
        ],
        "common_variations": {
            "category": ["Category", "Budget Category", "Line Item", "Budget Line", "Cost Category"],
            "budgeted_amount": ["Budget", "Budgeted", "Budgeted Amount", "Original Budget", "Allocated"],
            "actual_spent": ["Actual", "Actual Spent", "Spent", "Actual Cost", "YTD Spent"],
            "variance_pct": ["Variance %", "Variance", "% Variance", "Over/Under %", "Variance Percentage"],
            "forecast_amount": ["Forecast", "Forecasted", "Forecast Amount", "EAC", "Estimate at Completion"]
        }
    }',
    '{
        "rules": [
            {
                "rule_id": "BUDGET_OVERRUN_10",
                "signal_type": "budget_overrun",
                "priority": 7,
                "escalation_level": "director",
                "description": "Budget overrun ≥10%",
                "condition": {
                    "field": "variance_pct", "operator": "greater_than_or_equal", "value": 10
                }
            },
            {
                "rule_id": "BUDGET_OVERRUN_20",
                "signal_type": "budget_critical_overrun",
                "priority": 9,
                "escalation_level": "vp",
                "description": "Budget overrun ≥20% requires VP escalation",
                "condition": {
                    "field": "variance_pct", "operator": "greater_than_or_equal", "value": 20
                }
            },
            {
                "rule_id": "BUDGET_FORECAST_OVERRUN",
                "signal_type": "budget_forecast_overrun",
                "priority": 7,
                "escalation_level": "director",
                "description": "Forecasted amount exceeds budget by ≥10%",
                "condition": {
                    "field": "forecast_amount", "operator": "exceeds_budget_by_pct", "value": 10
                }
            }
        ]
    }',
    '1.0',
    datetime('now')
);

-- ==================================================================
-- 4. VENDOR PERFORMANCE TRACKER
-- ==================================================================

INSERT INTO tracker_definitions (
    tracker_def_id,
    tracker_name,
    tracker_type,
    description,
    schema_definition,
    signal_extraction_rules,
    version,
    created_at
) VALUES (
    'TDEF_VENDOR_001',
    'Vendor Performance Tracker',
    'vendor_tracker',
    'Vendor deliverable and performance tracking with deadline monitoring',
    '{
        "required_fields": [
            {
                "field_name": "vendor_name",
                "display_name": "Vendor Name",
                "data_type": "string",
                "description": "Name of vendor/CRO/supplier"
            },
            {
                "field_name": "deliverable",
                "display_name": "Deliverable",
                "data_type": "string",
                "description": "Description of deliverable"
            },
            {
                "field_name": "status",
                "display_name": "Status",
                "data_type": "string",
                "description": "Deliverable status (Not Started, In Progress, Complete, Overdue)"
            },
            {
                "field_name": "due_date",
                "display_name": "Due Date",
                "data_type": "date",
                "description": "Expected completion date"
            }
        ],
        "optional_fields": [
            {
                "field_name": "actual_date",
                "display_name": "Actual Completion Date",
                "data_type": "date",
                "description": "Actual completion date"
            },
            {
                "field_name": "days_late",
                "display_name": "Days Late",
                "data_type": "integer",
                "description": "Number of days past due date"
            },
            {
                "field_name": "quality_score",
                "display_name": "Quality Score",
                "data_type": "integer",
                "description": "Quality rating (1-5)"
            },
            {
                "field_name": "notes",
                "display_name": "Notes",
                "data_type": "string",
                "description": "Additional notes or comments"
            },
            {
                "field_name": "contact",
                "display_name": "Vendor Contact",
                "data_type": "string",
                "description": "Primary vendor contact person"
            }
        ],
        "common_variations": {
            "vendor_name": ["Vendor", "Vendor Name", "CRO", "Supplier", "Contractor"],
            "deliverable": ["Deliverable", "Milestone", "Task", "Work Item", "Service"],
            "status": ["Status", "State", "Deliverable Status"],
            "due_date": ["Due Date", "Due", "Expected Date", "Deadline", "Target Date"],
            "actual_date": ["Actual Date", "Completion Date", "Delivered Date", "Complete Date"]
        }
    }',
    '{
        "rules": [
            {
                "rule_id": "VENDOR_OVERDUE",
                "signal_type": "vendor_deliverable_overdue",
                "priority": 7,
                "escalation_level": "director",
                "description": "Vendor deliverable overdue",
                "condition": {
                    "all_of": [
                        {"field": "due_date", "operator": "is_past"},
                        {"field": "status", "operator": "not_equals", "value": "Complete"}
                    ]
                }
            },
            {
                "rule_id": "VENDOR_CRITICAL_OVERDUE",
                "signal_type": "vendor_critical_overdue",
                "priority": 9,
                "escalation_level": "vp",
                "description": "Vendor deliverable >30 days overdue",
                "condition": {
                    "all_of": [
                        {"field": "days_late", "operator": "greater_than", "value": 30},
                        {"field": "status", "operator": "not_equals", "value": "Complete"}
                    ]
                }
            },
            {
                "rule_id": "VENDOR_LOW_QUALITY",
                "signal_type": "vendor_quality_issue",
                "priority": 7,
                "escalation_level": "director",
                "description": "Vendor quality score ≤2",
                "condition": {
                    "field": "quality_score", "operator": "less_than_or_equal", "value": 2
                }
            },
            {
                "rule_id": "VENDOR_AT_RISK",
                "signal_type": "vendor_at_risk",
                "priority": 6,
                "escalation_level": "director",
                "description": "Vendor deliverable approaching due date (within 7 days) and not started",
                "condition": {
                    "all_of": [
                        {"field": "due_date", "operator": "within_days", "value": 7},
                        {"field": "status", "operator": "equals", "value": "Not Started"}
                    ]
                }
            }
        ]
    }',
    '1.0',
    datetime('now')
);

-- ==================================================================
-- VERIFICATION QUERIES
-- ==================================================================

-- Verify all 4 trackers were created
SELECT 'Tracker definitions created' as info, COUNT(*) as count
FROM tracker_definitions;

-- Show summary of each tracker
SELECT
    tracker_def_id,
    tracker_name,
    tracker_type,
    description,
    version
FROM tracker_definitions
ORDER BY tracker_name;
