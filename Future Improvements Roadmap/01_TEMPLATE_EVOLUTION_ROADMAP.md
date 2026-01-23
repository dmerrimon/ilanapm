# Template Evolution Roadmap

## Overview

Templates will evolve from static durations to ML-learned durations based on actual historical data from completed trials.

---

## Current State: Static Templates

**How it works now**:
```
Task Ontology (YAML)
  ↓ typical_duration_days: 45
Template Generator
  ↓ duration_days: 45
Generated Template (Kenya)
  ↓ IRB Approval: 45 days (same for everyone)
```

**Problem**:
- All users get same duration regardless of country/phase/area
- Doesn't learn from actual outcomes
- May be inaccurate for specific contexts

---

## Phase 1: Feedback-Learned Durations

**Target**: Q2 2026

**How it will work**:
```
Feedback Database (actual outcomes from completed trials)
  ↓ Query: Kenya IRB approvals → avg 60 days
Template Generator
  ↓ Check: Sample size >= 5? → Use learned duration
Generated Template (Kenya)
  ↓ IRB Approval: 60 days (learned from actual data!)
```

**Benefits**:
- Templates use real-world data instead of static estimates
- Improves accuracy over time as more trials complete
- Country-specific learning (Kenya ≠ US ≠ Vietnam)

**Implementation**:
```python
def generate_template(country_code, study_phase, therapeutic_area):
    """Generate template with learned durations"""

    tasks = []
    for task_def in task_ontology:
        # Try to get learned duration from feedback
        learned_duration = get_learned_duration(
            task_id=task_def.id,
            task_name=task_def.name,
            country_code=country_code,
            study_phase=study_phase,
            min_samples=5  # Need at least 5 data points
        )

        # Use learned duration if available, else fall back to YAML
        duration = learned_duration or task_def.typical_duration_days

        tasks.append(Task(
            id=task_def.id,
            name=task_def.name,
            duration_days=duration,
            category=task_def.category,
            # Include confidence in learned duration
            ml_confidence_pct=calculate_confidence(learned_duration)
        ))

    return Timeline(tasks=tasks, ...)
```

**Confidence Calculation**:
```python
def calculate_confidence(learned_duration):
    """Calculate confidence based on sample size and variance"""
    if learned_duration is None:
        return 0  # No data = 0% confidence

    sample_size = learned_duration.sample_count
    std_dev = learned_duration.std_deviation

    # Confidence increases with sample size, decreases with variance
    confidence = min(100, (sample_size / 20) * 100)  # 100% at 20+ samples
    confidence *= (1 - (std_dev / learned_duration.avg_duration))

    return max(0, confidence)
```

**Example Output**:
```
IRB Approval - Kenya: 60 days (Confidence: 75% - based on 15 Kenya trials)
```

---

## Phase 2: Context-Aware Durations

**Target**: Q3-Q4 2026

**How it will work**:
```
Feedback Database
  ↓ Query with multiple context filters:
    - Country: Kenya
    - Phase: Phase III
    - Therapeutic Area: Infectious Disease
    - Category: Regulatory
  ↓ ML Model: XGBoost/Random Forest
    - Features: task_name, country, phase, area, category
    - Target: actual_duration_days
  ↓ Prediction: 58 days (Kenya + Phase III + Infectious Disease)

Template Generator
  ↓ Use ML prediction instead of simple average
Generated Template (Kenya Phase III Infectious Disease)
  ↓ IRB Approval: 58 days (context-specific!)
```

**Benefits**:
- Even more accurate predictions
- Learns patterns: "Kenya Phase I takes longer than Phase III"
- Learns: "Oncology takes longer than Infectious Disease"
- Learns: "Academic sites take longer than independent sites"

**ML Model**:
```python
from sklearn.ensemble import RandomForestRegressor
import pandas as pd

def train_duration_model():
    """Train ML model to predict task durations"""

    # Load feedback data
    df = pd.read_sql("""
        SELECT
            task_name,
            category,
            country_code,
            study_phase,
            therapeutic_area,
            actual_duration_days as target
        FROM task_outcomes
    """, db_connection)

    # Feature engineering
    X = pd.get_dummies(df.drop('target', axis=1))
    y = df['target']

    # Train model
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)

    return model

def predict_duration_ml(task_name, country, phase, area, category):
    """Predict duration using ML model"""

    features = {
        'task_name': task_name,
        'country_code': country,
        'study_phase': phase,
        'therapeutic_area': area,
        'category': category
    }

    prediction = ml_model.predict([features])
    confidence = ml_model.feature_importances_.max()

    return prediction[0], confidence
```

**Example Predictions**:
```
Kenya Phase I Oncology:
  IRB Approval: 65 days (complex therapeutic area)

Kenya Phase III Infectious Disease:
  IRB Approval: 58 days (simpler, more data)

Kenya Phase III Observational:
  IRB Approval: 45 days (non-interventional, faster)
```

---

## Phase 3: Adaptive Templates with Recommendations

**Target**: 2027

**How it will work**:
```
Template Generator with AI Recommendations
  ↓
Generated Template (Kenya Phase III Infectious Disease)
  ↓ IRB Approval: 58 days (learned)
  ↓ + Recommendation: "Consider adding 'County Notification' (14 days)"
  ↓ + Recommendation: "Kenya trials average 3-layer approval (EC→PPB→NACOSTI)"
  ↓ + Risk Alert: "80% of Kenya trials exceed initial IRB estimate by 20%"
```

**Smart Recommendations**:
```python
def generate_template_with_recommendations(country_code, phase, area):
    """Generate template with AI-powered recommendations"""

    template = generate_base_template(country_code, phase, area)

    # Analyze similar completed trials
    similar_trials = find_similar_trials(country_code, phase, area)

    recommendations = []

    # Check for common additional tasks
    common_tasks = get_common_additional_tasks(similar_trials)
    for task in common_tasks:
        if task.frequency > 0.7:  # 70%+ of trials included this
            recommendations.append({
                'type': 'missing_task',
                'task_name': task.name,
                'duration_days': task.avg_duration,
                'reason': f'Used in {task.frequency*100:.0f}% of similar trials'
            })

    # Check for high-risk tasks
    risky_tasks = get_high_risk_tasks(similar_trials)
    for task in risky_tasks:
        recommendations.append({
            'type': 'risk_warning',
            'task_name': task.name,
            'risk_level': task.risk_score,
            'reason': f'{task.variance_pct:.0f}% of trials exceeded estimate'
        })

    # Add recommendations to template
    template.recommendations = recommendations

    return template
```

**Example Template with Recommendations**:
```
Kenya Phase III Infectious Disease Template
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REGULATORY TASKS
  IRB Approval - Kenya: 60 days (based on 15 trials)
  PPB Approval - Kenya: 30 days
  NACOSTI Clearance - Kenya: 30 days

📌 RECOMMENDATIONS:
  ✓ Add: "County Health Department Notification" (14 days)
    → Used in 85% of Kenya trials

  ⚠️ Risk: "IRB Approval - Kenya"
    → 80% of trials exceeded estimate by 15+ days
    → Consider adding buffer: 60 → 75 days

  💡 Tip: "Kenya 3-layer approval pathway"
    → EC → PPB → NACOSTI (sequential)
    → Total regulatory timeline: ~120 days
    → Plan for 4+ months before site activation
```

---

## Phase 4: Real-Time Template Updates

**Target**: 2027+

**How it will work**:
```
Active Templates in MS Project
  ↓ Periodic updates from backend
Backend ML Service
  ↓ Trains nightly on latest feedback
  ↓ Detects pattern changes (e.g., Kenya IRB now taking longer)
  ↓ Pushes updated predictions to active projects
Desktop Add-in
  ↓ Notification: "Updated duration available for 'IRB Approval'"
  ↓ User clicks "Review" → Shows old vs new estimate
  ↓ User clicks "Apply" → Task duration updated automatically
```

**Dynamic Updates**:
```python
# Backend service (runs nightly)
def detect_duration_changes():
    """Detect significant changes in task durations"""

    changes = []

    for task in task_catalog:
        # Compare recent durations vs historical
        recent_avg = get_avg_duration(task, days=90)
        historical_avg = get_avg_duration(task, days=365)

        change_pct = (recent_avg - historical_avg) / historical_avg * 100

        if abs(change_pct) > 20:  # 20%+ change
            changes.append({
                'task_name': task.name,
                'old_duration': historical_avg,
                'new_duration': recent_avg,
                'change_pct': change_pct,
                'reason': detect_reason(task, recent_avg, historical_avg)
            })

    return changes

# Desktop add-in (checks on project open)
def check_for_template_updates():
    """Check if any task durations have changed"""

    updates = api_client.get_duration_updates(
        project_id=current_project.id,
        last_check=last_update_timestamp
    )

    if updates:
        show_notification(f"{len(updates)} task durations updated")
        show_update_dialog(updates)
```

**Example Notification**:
```
┌─────────────────────────────────────────┐
│ Template Updates Available (3 tasks)    │
├─────────────────────────────────────────┤
│                                          │
│ IRB Approval - Kenya                     │
│   Current: 60 days                       │
│   Updated: 68 days (+13%)                │
│   Reason: Recent Kenya trials averaging  │
│           8 days longer due to increased │
│           review backlog                 │
│                                          │
│ Site Contract Execution                  │
│   Current: 145 days                      │
│   Updated: 165 days (+14%)               │
│   Reason: Academic sites now taking      │
│           longer for legal review        │
│                                          │
│ [Review All] [Apply Selected] [Dismiss] │
└─────────────────────────────────────────┘
```

---

## Evolution Metrics

### Success Criteria by Phase

**Phase 1 Success** (Feedback-Learned):
- ✅ 70%+ of tasks use learned durations (vs static YAML)
- ✅ Template accuracy improves 20%+ (avg error reduces)
- ✅ Minimum 5 samples per country-task combination

**Phase 2 Success** (Context-Aware):
- ✅ 85%+ accuracy within ±20% of actual duration
- ✅ Context-specific predictions (phase + area + country)
- ✅ Confidence scores >70% for major tasks

**Phase 3 Success** (Adaptive + Recommendations):
- ✅ 90%+ accuracy within ±15% of actual duration
- ✅ Recommendation acceptance rate >60%
- ✅ Risk alerts reduce overruns by 30%+

**Phase 4 Success** (Real-Time Updates):
- ✅ Update notifications within 24 hours of pattern change
- ✅ User acceptance rate >50% for updates
- ✅ Active templates stay current with latest data

---

## Data Requirements

### Minimum Sample Sizes

**Country-Level Learning**:
- Tier 1 (High priority): US, Kenya, Vietnam, India
  - Minimum: 20 trials per country
  - Target: 50+ trials per country

- Tier 2 (Medium priority): UK, Canada, Mexico, Peru, etc.
  - Minimum: 10 trials per country
  - Target: 30+ trials per country

- Tier 3 (Low priority): Smaller countries
  - Minimum: 5 trials per country
  - Target: 15+ trials per country

**Task-Level Learning**:
- Critical tasks (IRB, contracts, enrollment): 30+ samples
- Important tasks (site setup, data management): 20+ samples
- Standard tasks (admin, documentation): 10+ samples

**Context-Specific Learning** (Phase 2):
- Country + Phase: 15+ samples
- Country + Phase + Therapeutic Area: 10+ samples
- Full context (all filters): 5+ samples

---

## User Benefits Over Time

### Year 1 (Static Templates)

**Accuracy**: ~60% (based on industry benchmarks)
- Templates use static YAML durations
- May be inaccurate for specific contexts
- Same for all users

**Example**:
```
Kenya IRB Approval: 45 days (YAML static value)
Actual outcome: 62 days (38% over)
```

### Year 2 (Feedback-Learned Templates)

**Accuracy**: ~75% (+25% improvement)
- Templates use learned durations from 50+ trials
- Country-specific learning (Kenya ≠ US)
- Improves with more data

**Example**:
```
Kenya IRB Approval: 60 days (learned from 15 Kenya trials)
Actual outcome: 58 days (3% under - much better!)
```

### Year 3 (Context-Aware Templates)

**Accuracy**: ~85% (+42% improvement)
- ML model predicts based on full context
- Phase + Area + Country learning
- Adaptive to specific trial characteristics

**Example**:
```
Kenya Phase III Infectious Disease IRB: 58 days
Kenya Phase I Oncology IRB: 65 days (learns complexity!)
Actual outcomes: 59 and 67 days (within 5%)
```

### Year 4+ (Adaptive Templates + Real-Time Updates)

**Accuracy**: ~90%+ (+50% improvement)
- Templates stay current with pattern changes
- AI recommendations add missing tasks
- Risk alerts prevent common overruns

**Example**:
```
Kenya IRB: 68 days (updated from 60 - recent backlog detected!)
+ Recommendation: Add "County Notification" (14 days)
+ Risk Alert: 80% of recent trials exceeded estimate
Actual outcome: 70 days (within 3% - excellent!)
```

---

## Technical Architecture

### Database Schema Evolution

**Current** (Phase 0):
```sql
task_ontology.yaml (static file)
  → typical_duration_days: 45
```

**Phase 1** (Feedback-Learned):
```sql
-- Aggregate view for learned durations
CREATE VIEW learned_durations AS
SELECT
    task_name,
    country_code,
    study_phase,
    AVG(actual_duration_days) as learned_duration,
    STDDEV(actual_duration_days) as std_dev,
    COUNT(*) as sample_size,
    MIN(actual_duration_days) as min_duration,
    MAX(actual_duration_days) as max_duration
FROM task_outcomes
GROUP BY task_name, country_code, study_phase
HAVING COUNT(*) >= 5;  -- Minimum 5 samples
```

**Phase 2** (ML Model):
```python
# Trained model artifact
duration_predictor_model.pkl
  → Input: task_name, country, phase, area, category
  → Output: predicted_duration, confidence_score

# Model metadata
{
  "model_version": "v2.0",
  "training_date": "2026-06-15",
  "samples": 1500,
  "accuracy": 0.85,
  "features": ["task_name_tfidf", "country_onehot", "phase_ordinal", ...]
}
```

**Phase 3** (Recommendations Engine):
```sql
-- Task co-occurrence patterns
CREATE TABLE task_patterns AS
SELECT
    t1.country_code,
    t1.study_phase,
    t1.task_name as task_a,
    t2.task_name as task_b,
    COUNT(*) as co_occurrence_count,
    COUNT(*) * 1.0 / (SELECT COUNT(DISTINCT project_id)
                      FROM task_outcomes
                      WHERE country_code = t1.country_code) as frequency
FROM task_outcomes t1
JOIN task_outcomes t2 ON t1.project_id = t2.project_id
GROUP BY t1.country_code, t1.study_phase, t1.task_name, t2.task_name
HAVING frequency > 0.7;  -- Appears together in 70%+ of trials
```

---

## Migration Strategy

### Gradual Rollout

**Month 1-2**: Beta users only
- Test feedback-learned durations with 5-10 pilot users
- Validate accuracy improvements
- Gather feedback on confidence scores

**Month 3-4**: Opt-in for all users
- User setting: "Use ML-learned durations" (default: OFF)
- Users can toggle between static YAML and learned durations
- Monitor adoption and accuracy

**Month 5-6**: Default ON for new users
- New users get ML-learned durations by default
- Existing users can opt-in
- Confidence indicators show data quality

**Month 7+**: Full rollout
- All users get ML-learned durations
- Static YAML becomes fallback only
- Templates evolve automatically

### Backwards Compatibility

**Existing projects**: No automatic updates
- User must manually request update check
- User reviews proposed changes before applying
- User can reject updates and keep current durations

**New projects**: Use latest learned durations
- Templates generated with most recent data
- Confidence indicators show reliability
- User can always override with custom durations

---

## Summary

### Template Evolution Timeline

**2026 Q1**: Static templates (current)
  → Fixed durations from YAML
  → Same for all users

**2026 Q2**: Feedback-learned templates ← NEXT
  → Use actual outcomes from completed trials
  → Country-specific learning

**2026 Q3-Q4**: Context-aware templates
  → ML predictions based on full context
  → Phase + Area + Country learning

**2027+**: Adaptive templates with recommendations
  → Real-time updates
  → AI-powered recommendations
  → Risk alerts and pattern detection

### Key Benefits

**Accuracy Improvement**:
- Year 1: ~60% (static)
- Year 2: ~75% (feedback-learned)
- Year 3: ~85% (context-aware)
- Year 4+: ~90%+ (adaptive)

**User Impact**:
- Better timeline estimates
- Fewer overruns and delays
- Context-specific predictions
- Continuous improvement with more data

**Industry Impact**:
- Faster drug development
- Shared learning across organizations
- Data-driven decision making
- Network effects benefit everyone

---

*Your templates WILL evolve and improve over time!*
*The more trials completed, the smarter the system becomes.*
*Your data helps others, others' data helps you.*
