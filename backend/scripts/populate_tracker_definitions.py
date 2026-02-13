#!/usr/bin/env python3
"""
Populate Tracker Definitions

Creates pre-configured tracker schemas for:
- TMF Completeness Tracker
- Risk Log Tracker

These define the standard schema that orgs will map their columns to.
"""

import sqlite3
import json
import uuid
from pathlib import Path


def populate_tracker_definitions():
    """Populate standard tracker definitions"""

    db_path = Path(__file__).parent.parent / "database" / "feedback.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    print("=" * 80)
    print("POPULATING TRACKER DEFINITIONS")
    print("=" * 80)

    # TMF Completeness Tracker Definition
    tmf_tracker_def = {
        "tracker_def_id": str(uuid.uuid4()),
        "tracker_name": "TMF Completeness Tracker",
        "tracker_type": "tmf_completeness",
        "schema_definition": json.dumps({
            "required_fields": [
                {"field_name": "artifact_number", "field_type": "string", "description": "Artifact number (e.g., 01.01)"},
                {"field_name": "artifact_name", "field_type": "string", "description": "Name of regulatory artifact"},
                {"field_name": "status", "field_type": "string", "description": "Status (e.g., 'Complete', 'Missing Document', 'Pending Response')"},
            ],
            "optional_fields": [
                {"field_name": "reviewer", "field_type": "string", "description": "Reviewer name"},
                {"field_name": "missing_documents", "field_type": "string", "description": "List of missing documents"},
                {"field_name": "responsible_party", "field_type": "string", "description": "Person responsible for resolution"},
                {"field_name": "resolution", "field_type": "string", "description": "Resolution notes"},
                {"field_name": "closed_by", "field_type": "string", "description": "Name of person who closed"},
                {"field_name": "date_identified", "field_type": "date", "description": "Date issue identified"},
                {"field_name": "target_date", "field_type": "date", "description": "Target completion date"},
                {"field_name": "actual_completion_date", "field_type": "date", "description": "Actual completion date"}
            ],
            "multi_sheet_support": True,
            "sheets": [
                {
                    "sheet_name": "Main",
                    "description": "Main TMF artifacts list (~150 regulatory artifacts)"
                },
                {
                    "sheet_name": "Review Log",
                    "description": "Review log with action items, escalations, questions, findings"
                }
            ]
        }),
        "signal_extraction_rules": json.dumps({
            "rules": [
                {
                    "rule_id": "TMF_001",
                    "rule_name": "Missing Document",
                    "signal_type": "tmf_missing_document",
                    "condition": {
                        "field": "status",
                        "operator": "equals",
                        "value": "Missing Document"
                    },
                    "priority": 5,
                    "escalation_level": None,
                    "description": "Artifact status is 'Missing Document'"
                },
                {
                    "rule_id": "TMF_002",
                    "rule_name": "Overdue Pending Response",
                    "signal_type": "tmf_overdue",
                    "condition": {
                        "all_of": [
                            {"field": "status", "operator": "equals", "value": "Pending Response"},
                            {"field": "target_date", "operator": "days_overdue", "value": 14}
                        ]
                    },
                    "priority": 6,
                    "escalation_level": "director",
                    "description": "Status is 'Pending Response' and >14 days overdue"
                },
                {
                    "rule_id": "TMF_003",
                    "rule_name": "Low Completeness Before Milestone",
                    "signal_type": "tmf_completeness_risk",
                    "condition": {
                        "all_of": [
                            {"field": "completeness_pct", "operator": "less_than", "value": 75},
                            {"field": "days_to_milestone", "operator": "less_than", "value": 60}
                        ]
                    },
                    "priority": 8,
                    "escalation_level": "director",
                    "description": "Completeness <75% within 60 days of regulatory milestone"
                },
                {
                    "rule_id": "TMF_004",
                    "rule_name": "Escalation from Review Log",
                    "signal_type": "tmf_escalation",
                    "condition": {
                        "field": "item_type",
                        "operator": "equals",
                        "value": "Escalation"
                    },
                    "priority": 7,
                    "escalation_level": "director",
                    "description": "Review Log Item Type = 'Escalation'",
                    "sheet": "Review Log"
                }
            ]
        })
    }

    print("\n📋 Creating TMF Completeness Tracker definition...")
    cursor.execute("""
        INSERT INTO tracker_definitions (
            tracker_def_id,
            tracker_name,
            tracker_type,
            schema_definition,
            signal_extraction_rules
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        tmf_tracker_def["tracker_def_id"],
        tmf_tracker_def["tracker_name"],
        tmf_tracker_def["tracker_type"],
        tmf_tracker_def["schema_definition"],
        tmf_tracker_def["signal_extraction_rules"]
    ))
    print("  ✓ TMF Completeness Tracker definition created")

    # Risk Log Tracker Definition
    risk_log_def = {
        "tracker_def_id": str(uuid.uuid4()),
        "tracker_name": "Risk Log",
        "tracker_type": "risk_log",
        "schema_definition": json.dumps({
            "required_fields": [
                {"field_name": "risk_number", "field_type": "integer", "description": "Risk ID number"},
                {"field_name": "category", "field_type": "string", "description": "Risk category (Clinical, Site, Safety, etc.)"},
                {"field_name": "risk_detail", "field_type": "string", "description": "Description of the risk"},
                {"field_name": "impact", "field_type": "integer", "description": "Impact score (1-3)"},
                {"field_name": "probability", "field_type": "integer", "description": "Probability score (1-3)"},
                {"field_name": "priority", "field_type": "integer", "description": "Priority score (Impact × Probability, 1-9)"}
            ],
            "optional_fields": [
                {"field_name": "mitigation_plan", "field_type": "string", "description": "Mitigation plan"},
                {"field_name": "owner", "field_type": "string", "description": "Risk owner"},
                {"field_name": "target_date", "field_type": "date", "description": "Target resolution date"},
                {"field_name": "actual_completion_date", "field_type": "date", "description": "Actual completion date"},
                {"field_name": "status", "field_type": "string", "description": "Risk status (Open, In Progress, Resolved)"},
                {"field_name": "escalation_notes", "field_type": "string", "description": "Escalation notes"}
            ],
            "calculated_fields": [
                {
                    "field_name": "priority",
                    "formula": "impact * probability",
                    "description": "Priority = Impact × Probability"
                }
            ]
        }),
        "signal_extraction_rules": json.dumps({
            "rules": [
                {
                    "rule_id": "RISK_001",
                    "rule_name": "High Priority Risk",
                    "signal_type": "risk_high_priority",
                    "condition": {
                        "field": "priority",
                        "operator": "greater_than_or_equal",
                        "value": 6
                    },
                    "priority": 6,
                    "escalation_level": "director",
                    "description": "Priority ≥6 → Director escalation"
                },
                {
                    "rule_id": "RISK_002",
                    "rule_name": "Critical Priority Risk",
                    "signal_type": "risk_critical",
                    "condition": {
                        "field": "priority",
                        "operator": "equals",
                        "value": 9
                    },
                    "priority": 9,
                    "escalation_level": "vp",
                    "description": "Priority = 9 → VP escalation"
                },
                {
                    "rule_id": "RISK_003",
                    "rule_name": "No Mitigation Plan",
                    "signal_type": "risk_no_mitigation",
                    "condition": {
                        "all_of": [
                            {"field": "priority", "operator": "greater_than_or_equal", "value": 6},
                            {"field": "mitigation_plan", "operator": "is_null"}
                        ]
                    },
                    "priority": 7,
                    "escalation_level": "director",
                    "description": "Priority ≥6 AND no mitigation plan"
                },
                {
                    "rule_id": "RISK_004",
                    "rule_name": "Overdue Risk",
                    "signal_type": "risk_overdue",
                    "condition": {
                        "all_of": [
                            {"field": "target_date", "operator": "is_past"},
                            {"field": "actual_completion_date", "operator": "is_null"}
                        ]
                    },
                    "priority": 7,
                    "escalation_level": "director",
                    "description": "Target date passed AND not completed"
                },
                {
                    "rule_id": "RISK_005",
                    "rule_name": "Explicit Escalation",
                    "signal_type": "risk_escalated",
                    "condition": {
                        "field": "escalation_notes",
                        "operator": "is_not_null"
                    },
                    "priority": 8,
                    "escalation_level": "vp",
                    "description": "Escalation notes populated → VP escalation"
                },
                {
                    "rule_id": "RISK_006",
                    "rule_name": "Safety Risk",
                    "signal_type": "risk_safety",
                    "condition": {
                        "all_of": [
                            {"field": "category", "operator": "equals", "value": "Safety"},
                            {"field": "priority", "operator": "greater_than_or_equal", "value": 6}
                        ]
                    },
                    "priority": 9,
                    "escalation_level": "vp",
                    "description": "Safety category with Priority ≥6 → Immediate VP escalation"
                }
            ]
        })
    }

    print("\n📋 Creating Risk Log Tracker definition...")
    cursor.execute("""
        INSERT INTO tracker_definitions (
            tracker_def_id,
            tracker_name,
            tracker_type,
            schema_definition,
            signal_extraction_rules
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        risk_log_def["tracker_def_id"],
        risk_log_def["tracker_name"],
        risk_log_def["tracker_type"],
        risk_log_def["schema_definition"],
        risk_log_def["signal_extraction_rules"]
    ))
    print("  ✓ Risk Log Tracker definition created")

    conn.commit()
    conn.close()

    print("\n" + "=" * 80)
    print("✅ TRACKER DEFINITIONS POPULATED")
    print("=" * 80)
    print("\nSummary:")
    print("  - TMF Completeness Tracker: 4 signal extraction rules")
    print("  - Risk Log Tracker: 6 signal extraction rules")
    print("\nTracker definitions ready for Account Admin column mapping configuration.")
    print("=" * 80)


if __name__ == "__main__":
    populate_tracker_definitions()
