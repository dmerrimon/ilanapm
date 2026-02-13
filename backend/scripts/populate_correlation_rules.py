#!/usr/bin/env python3
"""
Populate Signal-to-Timeline Correlation Rules

Creates pre-configured correlation rules that map signals to timeline milestones:
- Risk signals → Affected milestones (Site Activation, LPI, Clinical DB Lock, etc.)
- TMF signals → Regulatory submissions
- Safety signals → FPD, DSMB reviews

These rules define how signals from trackers correlate with timeline impacts.
"""

import sqlite3
import json
import uuid
from pathlib import Path


def populate_correlation_rules():
    """Populate correlation rules for signal-to-timeline mapping"""

    db_path = Path(__file__).parent.parent / "database" / "feedback.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    print("=" * 80)
    print("POPULATING CORRELATION RULES")
    print("=" * 80)

    # Clear existing rules
    cursor.execute("DELETE FROM correlation_rules")
    print("\n🧹 Cleared existing correlation rules")

    # ========================================================================
    # CORRELATION RULE 1: High Priority Risk → Site Activation
    # ========================================================================
    rule_1 = {
        "rule_id": str(uuid.uuid4()),
        "rule_name": "High Priority Risk → Site Activation",
        "signal_type": "risk_high_priority",
        "signal_category": "Site",
        "signal_detail_pattern": json.dumps({
            "pattern_type": "keyword_match",
            "keywords": ["site activation", "site contract", "site selection", "site startup"]
        }),
        "affected_milestones": json.dumps(["Site Activation"]),
        "affected_milestone_codes": json.dumps(["SITE_ACT"]),
        "correlation_type": "risk",
        "confidence_score": 0.85,
        "impact_type": "delay",
        "delay_estimation_logic": json.dumps({
            "type": "multiplier",
            "formula": "priority * 7",
            "description": "Priority score × 7 days"
        }),
        "escalation_trigger": True,
        "escalation_level": "director",
        "reasoning_template": "Risk #{priority}: '{signal_description}' affects {milestone}. Estimated delay: {delay_days} days."
    }

    cursor.execute("""
        INSERT INTO correlation_rules (
            rule_id, rule_name, signal_type, signal_category, signal_detail_pattern,
            affected_milestones, affected_milestone_codes, correlation_type,
            confidence_score, impact_type, delay_estimation_logic,
            escalation_trigger, escalation_level, reasoning_template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rule_1["rule_id"],
        rule_1["rule_name"],
        rule_1["signal_type"],
        rule_1["signal_category"],
        rule_1["signal_detail_pattern"],
        rule_1["affected_milestones"],
        rule_1["affected_milestone_codes"],
        rule_1["correlation_type"],
        rule_1["confidence_score"],
        rule_1["impact_type"],
        rule_1["delay_estimation_logic"],
        rule_1["escalation_trigger"],
        rule_1["escalation_level"],
        rule_1["reasoning_template"]
    ))
    print("  ✓ Rule 1: High Priority Risk → Site Activation")

    # ========================================================================
    # CORRELATION RULE 2: Enrollment Risk → LPI Milestone
    # ========================================================================
    rule_2 = {
        "rule_id": str(uuid.uuid4()),
        "rule_name": "Enrollment Risk → LPI Milestone",
        "signal_type": "risk_high_priority",
        "signal_category": "Clinical",
        "signal_detail_pattern": json.dumps({
            "pattern_type": "keyword_match",
            "keywords": ["enrollment", "screen failure", "dropout", "drop out", "drop-out", "recruitment"]
        }),
        "affected_milestones": json.dumps(["LPI", "Last Patient In"]),
        "affected_milestone_codes": json.dumps(["LPI"]),
        "correlation_type": "risk",
        "confidence_score": 0.90,
        "impact_type": "delay",
        "delay_estimation_logic": json.dumps({
            "type": "multiplier",
            "formula": "priority * 14",
            "description": "Priority score × 14 days (enrollment risks compound)"
        }),
        "escalation_trigger": True,
        "escalation_level": "director",
        "reasoning_template": "Enrollment Risk (Priority {priority}): '{signal_description}'. {milestone} may slip. Recommend enrollment forecasting review."
    }

    cursor.execute("""
        INSERT INTO correlation_rules (
            rule_id, rule_name, signal_type, signal_category, signal_detail_pattern,
            affected_milestones, affected_milestone_codes, correlation_type,
            confidence_score, impact_type, delay_estimation_logic,
            escalation_trigger, escalation_level, reasoning_template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rule_2["rule_id"],
        rule_2["rule_name"],
        rule_2["signal_type"],
        rule_2["signal_category"],
        rule_2["signal_detail_pattern"],
        rule_2["affected_milestones"],
        rule_2["affected_milestone_codes"],
        rule_2["correlation_type"],
        rule_2["confidence_score"],
        rule_2["impact_type"],
        rule_2["delay_estimation_logic"],
        rule_2["escalation_trigger"],
        rule_2["escalation_level"],
        rule_2["reasoning_template"]
    ))
    print("  ✓ Rule 2: Enrollment Risk → LPI Milestone")

    # ========================================================================
    # CORRELATION RULE 3: Site Closeout AE Resolution → Clinical DB Lock
    # ========================================================================
    rule_3 = {
        "rule_id": str(uuid.uuid4()),
        "rule_name": "Site Closeout AE Resolution → Clinical DB Lock",
        "signal_type": "site_closeout_blocker",
        "signal_category": None,  # Applies regardless of category
        "signal_detail_pattern": json.dumps({
            "pattern_type": "task_code_match",
            "task_codes": ["HS_CO_002"]  # Specific task: AE resolution
        }),
        "affected_milestones": json.dumps(["Clinical DB Lock"]),
        "affected_milestone_codes": json.dumps(["CDB_LOCK"]),
        "correlation_type": "blocker",  # HARD BLOCKER
        "confidence_score": 1.0,
        "impact_type": "delay",
        "delay_estimation_logic": json.dumps({
            "type": "fixed",
            "days": 14,
            "description": "Fixed 14-day delay for AE resolution"
        }),
        "escalation_trigger": True,
        "escalation_level": "director",
        "reasoning_template": "BLOCKER: Adverse event resolution (HS_CO_002) incomplete. {milestone} cannot proceed. Critical path impact."
    }

    cursor.execute("""
        INSERT INTO correlation_rules (
            rule_id, rule_name, signal_type, signal_category, signal_detail_pattern,
            affected_milestones, affected_milestone_codes, correlation_type,
            confidence_score, impact_type, delay_estimation_logic,
            escalation_trigger, escalation_level, reasoning_template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rule_3["rule_id"],
        rule_3["rule_name"],
        rule_3["signal_type"],
        rule_3["signal_category"],
        rule_3["signal_detail_pattern"],
        rule_3["affected_milestones"],
        rule_3["affected_milestone_codes"],
        rule_3["correlation_type"],
        rule_3["confidence_score"],
        rule_3["impact_type"],
        rule_3["delay_estimation_logic"],
        rule_3["escalation_trigger"],
        rule_3["escalation_level"],
        rule_3["reasoning_template"]
    ))
    print("  ✓ Rule 3: Site Closeout AE Resolution → Clinical DB Lock (BLOCKER)")

    # ========================================================================
    # CORRELATION RULE 4: TMF Completeness <75% → Regulatory Submission
    # ========================================================================
    rule_4 = {
        "rule_id": str(uuid.uuid4()),
        "rule_name": "TMF Completeness <75% → Regulatory Submission",
        "signal_type": "tmf_completeness_risk",
        "signal_category": None,
        "signal_detail_pattern": json.dumps({
            "pattern_type": "any",
            "description": "Any TMF completeness risk"
        }),
        "affected_milestones": json.dumps([
            "IND Submission",
            "CTA Submission",
            "Regulatory Authority Submission"
        ]),
        "affected_milestone_codes": json.dumps(["IND_SUB", "CTA_SUB", "REG_SUB"]),
        "correlation_type": "risk",
        "confidence_score": 0.80,
        "impact_type": "delay",
        "delay_estimation_logic": json.dumps({
            "type": "fixed",
            "days": 30,
            "description": "Fixed 30-day delay for TMF remediation"
        }),
        "escalation_trigger": True,
        "escalation_level": "director",
        "reasoning_template": "TMF completeness at {completeness_pct}% (target: 75%). {milestone} at risk. {missing_count} artifacts missing."
    }

    cursor.execute("""
        INSERT INTO correlation_rules (
            rule_id, rule_name, signal_type, signal_category, signal_detail_pattern,
            affected_milestones, affected_milestone_codes, correlation_type,
            confidence_score, impact_type, delay_estimation_logic,
            escalation_trigger, escalation_level, reasoning_template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rule_4["rule_id"],
        rule_4["rule_name"],
        rule_4["signal_type"],
        rule_4["signal_category"],
        rule_4["signal_detail_pattern"],
        rule_4["affected_milestones"],
        rule_4["affected_milestone_codes"],
        rule_4["correlation_type"],
        rule_4["confidence_score"],
        rule_4["impact_type"],
        rule_4["delay_estimation_logic"],
        rule_4["escalation_trigger"],
        rule_4["escalation_level"],
        rule_4["reasoning_template"]
    ))
    print("  ✓ Rule 4: TMF Completeness <75% → Regulatory Submission")

    # ========================================================================
    # CORRELATION RULE 5: Safety/Toxicity Risk → FPD and DSMB
    # ========================================================================
    rule_5 = {
        "rule_id": str(uuid.uuid4()),
        "rule_name": "Safety/Toxicity Risk → FPD and DSMB",
        "signal_type": "risk_high_priority",
        "signal_category": "Safety",
        "signal_detail_pattern": json.dumps({
            "pattern_type": "keyword_match",
            "keywords": ["toxicity", "SAE", "serious adverse event", "DSMB", "safety"]
        }),
        "affected_milestones": json.dumps([
            "FPD",
            "First Patient Dosed",
            "DSMB Review"
        ]),
        "affected_milestone_codes": json.dumps(["FPD", "DSMB"]),
        "correlation_type": "risk",
        "confidence_score": 0.95,
        "impact_type": "delay",
        "delay_estimation_logic": json.dumps({
            "type": "fixed",
            "days": 21,
            "description": "Fixed 21-day delay for safety review"
        }),
        "escalation_trigger": True,
        "escalation_level": "vp",  # VP escalation for safety
        "reasoning_template": "SAFETY RISK (Priority {priority}): '{signal_description}'. {milestone} may be paused. VP-level escalation required."
    }

    cursor.execute("""
        INSERT INTO correlation_rules (
            rule_id, rule_name, signal_type, signal_category, signal_detail_pattern,
            affected_milestones, affected_milestone_codes, correlation_type,
            confidence_score, impact_type, delay_estimation_logic,
            escalation_trigger, escalation_level, reasoning_template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rule_5["rule_id"],
        rule_5["rule_name"],
        rule_5["signal_type"],
        rule_5["signal_category"],
        rule_5["signal_detail_pattern"],
        rule_5["affected_milestones"],
        rule_5["affected_milestone_codes"],
        rule_5["correlation_type"],
        rule_5["confidence_score"],
        rule_5["impact_type"],
        rule_5["delay_estimation_logic"],
        rule_5["escalation_trigger"],
        rule_5["escalation_level"],
        rule_5["reasoning_template"]
    ))
    print("  ✓ Rule 5: Safety/Toxicity Risk → FPD and DSMB (VP ESCALATION)")

    # ========================================================================
    # CORRELATION RULE 6: Budget Overrun → All Milestones
    # ========================================================================
    rule_6 = {
        "rule_id": str(uuid.uuid4()),
        "rule_name": "Budget Overrun → All Milestones",
        "signal_type": "budget_overrun",
        "signal_category": None,
        "signal_detail_pattern": json.dumps({
            "pattern_type": "any",
            "description": "Budget overrun affects all downstream work"
        }),
        "affected_milestones": json.dumps(["*"]),  # Wildcard: affects all
        "affected_milestone_codes": json.dumps(["*"]),
        "correlation_type": "risk",
        "confidence_score": 0.70,
        "impact_type": "cost_increase",
        "delay_estimation_logic": json.dumps({
            "type": "variable",
            "description": "Delay depends on budget variance percentage"
        }),
        "escalation_trigger": True,
        "escalation_level": "director",
        "reasoning_template": "Budget overrun: {variance_pct}% over budget. All milestones at risk if resources reduced."
    }

    cursor.execute("""
        INSERT INTO correlation_rules (
            rule_id, rule_name, signal_type, signal_category, signal_detail_pattern,
            affected_milestones, affected_milestone_codes, correlation_type,
            confidence_score, impact_type, delay_estimation_logic,
            escalation_trigger, escalation_level, reasoning_template
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        rule_6["rule_id"],
        rule_6["rule_name"],
        rule_6["signal_type"],
        rule_6["signal_category"],
        rule_6["signal_detail_pattern"],
        rule_6["affected_milestones"],
        rule_6["affected_milestone_codes"],
        rule_6["correlation_type"],
        rule_6["confidence_score"],
        rule_6["impact_type"],
        rule_6["delay_estimation_logic"],
        rule_6["escalation_trigger"],
        rule_6["escalation_level"],
        rule_6["reasoning_template"]
    ))
    print("  ✓ Rule 6: Budget Overrun → All Milestones")

    conn.commit()
    conn.close()

    print("\n" + "=" * 80)
    print("✅ CORRELATION RULES POPULATED")
    print("=" * 80)
    print("\nSummary:")
    print("  - 6 correlation rules created")
    print("  - Rule types:")
    print("    • 3 Risk-to-Milestone correlations")
    print("    • 1 TMF-to-Regulatory correlation")
    print("    • 1 Site Closeout blocker")
    print("    • 1 Budget-to-All correlation")
    print("  - Escalation levels:")
    print("    • 5 Director-level")
    print("    • 1 VP-level (Safety risks)")
    print("=" * 80)


if __name__ == "__main__":
    populate_correlation_rules()
