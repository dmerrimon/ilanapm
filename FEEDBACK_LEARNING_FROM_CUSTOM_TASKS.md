# Feedback Learning from Custom Tasks

## Overview

**YES - The feedback system WILL learn from custom tasks that users add!**

The ML feedback system captures actual task durations for ANY task in MS Project - whether it's from our task ontology or a custom task specific to your study phase, therapeutic area, or country requirements.

---

## How It Works

### Database Schema

Every completed task is stored with rich contextual information:

```sql
CREATE TABLE task_outcomes (
    -- Task identification
    task_id TEXT NOT NULL,
    task_name TEXT NOT NULL,              ← Can be ANY task name!
    category TEXT,                         ← User-assigned category

    -- Prediction data (if available)
    predicted_duration_days INTEGER,
    predicted_confidence REAL,             ← 0-1 confidence score
    model_version TEXT,

    -- Actual outcome
    actual_duration_days INTEGER NOT NULL, ← What really happened
    actual_start_date DATE,
    actual_end_date DATE,

    -- Context for ML learning
    country_code TEXT,                     ← US, KE, VN, etc.
    authority TEXT,                        ← FDA, PPB, MHRA, etc.
    study_phase TEXT,                      ← Phase I, II, III, IV
    therapeutic_area TEXT,                 ← Oncology, Cardiology, etc.

    -- Accuracy metrics
    variance_days INTEGER,                 ← actual - predicted
    variance_percent REAL,
    was_accurate BOOLEAN,                  ← Within ±20%?

    -- Metadata
    project_id TEXT,
    recorded_at TIMESTAMP,
    recorded_by TEXT
);
```

### Key Insight: Task Name is Free-Form

**The `task_name` field accepts ANY text** - it doesn't need to match our ontology!

This means:
- ✅ Custom phase-specific tasks (e.g., "CAR-T Cell Manufacturing QC Review")
- ✅ Custom country-specific tasks (e.g., "Kenya County-Level Notification")
- ✅ Custom therapeutic area tasks (e.g., "Oncology Biomarker Analysis")
- ✅ Custom sponsor requirements (e.g., "Emmes DSMB Report Template Review")

All of these are captured and used for ML learning!

---

## Real-World Examples

### Example 1: Phase-Specific Custom Task

**Scenario**: Phase I Oncology trial needs "CAR-T Cell Manufacturing QC Review"

**First Time**:
```json
{
  "task_name": "CAR-T Cell Manufacturing QC Review",
  "category": "Operational",
  "study_phase": "Phase I",
  "therapeutic_area": "Oncology",
  "predicted_duration_days": null,    ← No prediction (new task)
  "actual_duration_days": 21,         ← User completes it in 21 days
  "country_code": "US",
  "authority": "FDA United States"
}
```

**Stored in Database**:
- Task name: "CAR-T Cell Manufacturing QC Review"
- Context: Phase I + Oncology + Operational + US
- Actual: 21 days

**Next Time** (Another Phase I Oncology trial):
```
User creates similar task: "CAR-T Manufacturing QC Process"

ML Model sees:
- Task name similarity: "CAR-T" + "Manufacturing" + "QC"
- Context match: Phase I + Oncology + Operational
- Historical data: 21 days (1 data point)

Prediction: 21 days (confidence: 30% - low due to limited data)
```

**After 10 Phase I CAR-T trials**:
```
Historical data:
- CAR-T Manufacturing QC (Phase I): 21, 18, 24, 19, 22, 20, 23, 21, 19, 22 days
- Average: 20.9 days
- Std Dev: 1.9 days

Prediction: 21 days (confidence: 85% - high due to consistent data)
```

---

### Example 2: Country-Specific Custom Task

**Scenario**: Kenya trials require county-level notifications (not in ontology)

**First Time**:
```json
{
  "task_name": "Nairobi County Health Department Notification",
  "category": "Regulatory",
  "country_code": "KE",
  "authority": "PPB Kenya",
  "study_phase": "Phase III",
  "therapeutic_area": "Infectious Disease",
  "predicted_duration_days": null,    ← No prediction
  "actual_duration_days": 14          ← User completes it in 14 days
}
```

**Next Kenya Trial**:
```
User creates: "Mombasa County Health Notification"

ML Model sees:
- Task name keywords: "County" + "Health" + "Notification"
- Context match: KE + Regulatory
- Historical data: 14 days (Nairobi County)

Prediction: 14 days (confidence: 40% - moderate for new location)
```

**After 20 Kenya trials**:
```
Historical data:
- Nairobi County: 14, 12, 15, 13, 14 days
- Mombasa County: 10, 11, 12, 10 days
- Kisumu County: 21, 18, 20, 19 days (slower - rural area)

ML learns:
- Urban counties (Nairobi, Mombasa): ~12 days
- Rural counties (Kisumu): ~20 days
- County context matters!

Prediction improves with location-specific data
```

---

### Example 3: Therapeutic Area-Specific Custom Task

**Scenario**: Rare disease trials need "Patient Advocacy Group Engagement"

**First Time**:
```json
{
  "task_name": "Patient Advocacy Group Engagement Meeting",
  "category": "Operational",
  "therapeutic_area": "Rare Disease",
  "study_phase": "Phase II",
  "predicted_duration_days": null,
  "actual_duration_days": 45          ← Takes 45 days to coordinate
}
```

**ML Learning**:
```
After 15 rare disease trials:
- "Patient Advocacy Group Engagement": 45, 42, 50, 38, 44, 46, 41, 49, 43, 45 days
- Average: 44.3 days
- Pattern recognized: Rare disease trials need ~45 days for advocacy engagement

When user creates similar task in new rare disease trial:
Prediction: 44 days (confidence: 90%)
```

**Contrast with Common Diseases**:
```
Oncology trials (common cancer):
- "Patient Advocacy Group Engagement": 10, 12, 8, 11, 9 days (much faster)
- Average: 10 days

ML learns: Rare disease advocacy is 4X slower than common disease
```

---

## ML Learning Process

### Phase 1: Data Collection (Current - Automatic)

**Automatic Feedback Capture**:
- When user marks task as 100% complete in MS Project
- On project save, add-in automatically captures:
  - Task name (free-form text)
  - Category (user-assigned)
  - Actual duration (from MS Project)
  - Start/end dates
  - Context (phase, country, authority, therapeutic area)

**Stored Locally First**:
- Desktop add-in stores feedback in user settings
- Prevents duplicate submissions
- Tracks submission count

**Submitted to Backend**:
- POST `/api/v1/feedback/task-completion`
- Background submission (non-blocking)
- No user intervention required

**Database Storage**:
- SQLite database: `backend/database/feedback.db`
- Table: `task_outcomes`
- Indexed by: country, category, date, accuracy

---

### Phase 2: Pattern Recognition (Future ML Training)

**Feature Extraction**:
```python
# ML extracts features from task names
"CAR-T Cell Manufacturing QC Review"
→ Features: ["CAR-T", "cell", "manufacturing", "QC", "review"]

"Kenya County-Level Notification"
→ Features: ["Kenya", "county", "notification", "regulatory"]

"DSMB Charter Review"
→ Features: ["DSMB", "charter", "review", "safety"]
```

**Contextual Matching**:
```python
# ML combines task name features with context
Task: "CAR-T Manufacturing QC"
Context: Phase I + Oncology + US + Operational

# Find similar historical tasks
Similar tasks in DB:
- "CAR-T Cell Manufacturing QC Review" (Phase I, Oncology, US): 21 days
- "CAR-T Production Quality Control" (Phase I, Oncology, US): 19 days
- "CAR-T Manufacturing Validation" (Phase I, Oncology, UK): 24 days

# Weighted average based on similarity scores
Prediction: 21.3 days (confidence: 75%)
```

**Statistical Modeling**:
```python
# Random Forest or XGBoost model
Features:
- Task name keywords (TF-IDF vectors)
- Category (one-hot encoded)
- Country (one-hot encoded)
- Study phase (ordinal: I < II < III < IV)
- Therapeutic area (one-hot encoded)
- Historical mean for similar tasks
- Historical std dev for similar tasks

Target: actual_duration_days

Model learns:
- "CAR-T" + Phase I + Oncology → 20-25 days
- "County notification" + Kenya → 12-20 days
- "DSMB charter" + any phase → 7-14 days
```

---

### Phase 3: Prediction (After Training)

**When User Creates New Task**:
```
User types: "CAR-T Manufacturing QC Review"
User sets: Category = Operational, Phase = Phase I, Area = Oncology
```

**ML Prediction Flow**:
```python
1. Extract features from task name
   → ["CAR-T", "manufacturing", "QC", "review"]

2. Query historical data
   → Find tasks with similar keywords + context

3. Calculate weighted prediction
   → Weight by similarity score and data freshness

4. Estimate confidence
   → Based on number of matching historical tasks
   → Higher confidence with more data points

5. Return prediction
   → Duration: 21 days
   → Confidence: 85%
   → Rationale: "Based on 10 similar Phase I CAR-T tasks"
```

**Prediction Displayed in MS Project**:
- Custom field: "ML Predicted Duration"
- Custom field: "ML Confidence %"
- Custom field: "Risk Score" (if prediction has high variance)

---

## Benefits for Users

### 1. Phase-Specific Learning

**Phase I Oncology** learns different patterns than **Phase III Cardiology**:
- Phase I Oncology: Complex manufacturing, extended QC, longer setup
- Phase III Cardiology: Simpler design, standard CROs, faster enrollment

ML recognizes these patterns from YOUR data!

### 2. Country-Specific Learning

**Kenya** learns different patterns than **United States**:
- Kenya: 3-layer approval, county notifications, local PI requirements
- US: 2-layer approval, parallel FDA/IRB, streamlined

ML adapts to country workflows from YOUR Kenya trial data!

### 3. Therapeutic Area-Specific Learning

**Rare Disease** learns different patterns than **Common Cancers**:
- Rare Disease: Limited sites, advocacy coordination, specialized IRBs
- Common Cancers: Many sites, standard protocols, faster reviews

ML captures these differences from YOUR rare disease trials!

### 4. Continuous Improvement

**Every completed task makes the system smarter**:
- First trial: No predictions (cold start)
- After 5 trials: Basic predictions (30-50% confidence)
- After 20 trials: Good predictions (70-85% confidence)
- After 100 trials: Excellent predictions (85-95% confidence)

**The more you use it, the better it gets!**

---

## Accuracy Tracking

### Accuracy Dashboard (Settings → History Tab)

**Overall Accuracy**:
- Total tasks predicted: 150
- Accurate predictions (±20%): 112
- Accuracy rate: 74.7%
- Trending: ↑ 5% (improving over time)

**By Category**:
- Regulatory: 85% accurate (65/77 tasks)
- Operational: 70% accurate (28/40 tasks)
- Data Management: 68% accurate (19/28 tasks)

**By Country**:
- Kenya: 80% accurate (24/30 tasks)
- US: 75% accurate (60/80 tasks)
- Vietnam: 65% accurate (13/20 tasks) ← Less data

**Top Prediction Errors**:
1. "Site Contract Execution" - Predicted 145 days, Actual 280 days (Academic sites are slower!)
2. "CAR-T Manufacturing" - Predicted 21 days, Actual 42 days (Supply chain delays)
3. "Kenya County Notification" - Predicted 14 days, Actual 28 days (Rural county was slower)

**Recommendations**:
- Consider adding "Site Type" field (Academic vs Independent) for better contract predictions
- Consider adding "Supply Chain Status" field for manufacturing tasks
- Consider adding "County Location" field (Urban vs Rural) for Kenya notifications

---

## Custom Task Examples by Domain

### Phase-Specific Custom Tasks

**Phase I**:
- "CAR-T Cell Manufacturing QC Review"
- "First-in-Human Safety Committee Review"
- "Dose Escalation Committee Meeting"
- "PK/PD Biomarker Development"

**Phase II**:
- "Interim Efficacy Analysis"
- "Patient-Reported Outcomes Development"
- "Adaptive Design Committee Review"

**Phase III**:
- "Health Economics Analysis"
- "Market Access Planning"
- "Pediatric Investigation Plan"

**Phase IV**:
- "Post-Marketing Surveillance Setup"
- "Real-World Evidence Collection"

### Country-Specific Custom Tasks

**Kenya**:
- "County Health Department Notification"
- "Local Co-PI Identification"
- "Community Advisory Board Engagement"

**Vietnam**:
- "Provincial Department of Health Approval"
- "Ministry of Public Security Clearance"
- "Local IRB Translation Review"

**India**:
- "DCGI Trial Registration"
- "Clinical Trials Registry India (CTRI) Registration"
- "State Drug Controller Notification"

### Therapeutic Area-Specific Custom Tasks

**Oncology**:
- "Tumor Board Presentation"
- "Biomarker-Driven Enrollment"
- "Precision Medicine Committee Review"

**Rare Disease**:
- "Patient Advocacy Group Engagement"
- "Natural History Study Coordination"
- "Expert Clinician Network Activation"

**Infectious Disease**:
- "Outbreak Response Committee Activation"
- "WHO Emergency Use Listing"
- "Global Health Security Coordination"

---

## Privacy & Data Sharing

### What's Shared (Automatic)

**Task-level data**:
- Task name (free-form text)
- Category, phase, country, authority, therapeutic area
- Actual duration (days)
- Start/end dates

**NOT shared**:
- Study name or protocol number
- Sponsor/CRO names
- Patient data
- Site names
- Budget/financial information

### Why Data Sharing is Mandatory

**Benefits everyone**:
- Your Kenya trial data → Helps next Kenya trial
- Your Phase I CAR-T data → Helps next Phase I CAR-T trial
- Your rare disease data → Helps next rare disease trial

**Network Effects**:
- More data = Better predictions
- Better predictions = Better timelines
- Better timelines = Faster drug development
- Faster drug development = **More lives saved**

**Regulated Industry Standards**:
- Clinical trials already share de-identified data (ClinicalTrials.gov, WHO ICTRP)
- Industry benchmarks (WCG Clintrax, Tufts CSDD) rely on shared data
- This system extends the same principle to operational timelines

---

## Future Enhancements

### Phase 1: Natural Language Processing (NLP)

**Better task name matching**:
```python
# Currently: Simple keyword matching
"CAR-T Manufacturing QC Review" matches "CAR-T Production QC"

# Future: Semantic similarity
"CAR-T Manufacturing QC Review" matches:
- "Chimeric Antigen Receptor T-Cell Production Review" (same concept, different words)
- "CAR-T Quality Control Validation" (similar meaning)
- "T-Cell Therapy Manufacturing Assessment" (related concept)
```

### Phase 2: Dependency Learning

**Learn task sequences**:
```python
# Pattern recognition
"Protocol Development" → "IRB Submission" (lag: 7 days)
"IRB Approval" → "Site Initiation" (lag: 14 days)
"Site Activation" → "First Patient In" (lag: 21 days)

# Predict dependencies
When user creates "Protocol Development":
→ Suggest creating "IRB Submission" with 7-day lag
→ Suggest creating "Site Initiation" with predecessor chain
```

### Phase 3: Risk Prediction

**Predict delay likelihood**:
```python
# Historical patterns
"Site Contract Execution" + Academic site:
- 80% probability of >200 day duration
- 50% probability of >280 day duration
- Risk: HIGH (delay likely)

"Site Contract Execution" + Independent site:
- 90% probability of <180 day duration
- Risk: LOW (on track)
```

### Phase 4: Recommendation Engine

**Suggest best practices**:
```
Based on your Kenya Phase III trial:
→ Consider adding "County Notification" task (14 days)
→ Consider adding "Local Co-PI Identification" task (30 days)
→ Consider budgeting +30 days for multi-layer approval

These tasks were used in 85% of successful Kenya trials
```

---

## Summary

### ✅ YES - System Learns from Custom Tasks

**Any task you add will be captured**:
- Phase-specific tasks
- Country-specific tasks
- Therapeutic area-specific tasks
- Sponsor-specific requirements
- CRO-specific workflows

**ML uses task name + context**:
- Task name keywords (free-form text)
- Category, phase, country, authority, therapeutic area
- Historical patterns from similar tasks

**Predictions improve over time**:
- Cold start: No predictions (0% confidence)
- 5 trials: Basic predictions (30-50% confidence)
- 20 trials: Good predictions (70-85% confidence)
- 100+ trials: Excellent predictions (85-95% confidence)

### 🎯 The More You Use It, The Better It Gets!

Every completed task makes the system smarter for:
- **You** - Better predictions in your next trial
- **Your team** - Shared learning across projects
- **Your organization** - Institutional knowledge captured
- **The industry** - Faster drug development for everyone

---

*Feedback learning system: Ready to capture and learn from your custom tasks!*
