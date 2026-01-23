# Viewing Feedback Data - Quick Start Guide

## Overview

This guide shows you exactly how to view and analyze the feedback data submitted by users.

---

## Current Data Status

**Database Location**:
- Server: Render.com (https://ilanapm.onrender.com)
- File: `backend/database/feedback.db`
- Type: SQLite

**What's In The Database**:
- Task names (what users called their tasks)
- Actual durations (how long tasks really took)
- Predictions (if ML provided estimates)
- Context (country, phase, therapeutic area, category)
- Timestamps (when feedback was submitted)

---

## Method 1: Use the API (Easiest)

### Step 1: Check if data exists

```bash
# Get summary statistics
curl https://ilanapm.onrender.com/api/v1/feedback/summary | python3 -m json.tool
```

**Expected Output**:
```json
{
  "success": true,
  "overall": {
    "total_records": 0,
    "countries": 0,
    "projects": 0,
    "first_submission": null,
    "last_submission": null,
    "avg_error_pct": null
  },
  "by_country": [],
  "by_category": []
}
```

**Note**: Currently shows 0 records because no users have submitted feedback yet. Once users complete tasks and save projects, data will appear here.

---

### Step 2: Export data when available

**Export all data**:
```bash
curl "https://ilanapm.onrender.com/api/v1/feedback/export" > feedback_data.json
```

**Export Kenya data only**:
```bash
curl "https://ilanapm.onrender.com/api/v1/feedback/export?country_code=KE" > kenya_feedback.json
```

**Export Phase III data**:
```bash
curl "https://ilanapm.onrender.com/api/v1/feedback/export?study_phase=Phase%20III" > phase3_feedback.json
```

**Export recent 50 records**:
```bash
curl "https://ilanapm.onrender.com/api/v1/feedback/export?limit=50" > recent_feedback.json
```

---

### Step 3: View the JSON data

```bash
# Pretty print JSON
cat feedback_data.json | python3 -m json.tool | head -100

# Or use jq (if installed)
cat feedback_data.json | jq '.data[0:5]'
```

**Example Output** (once data exists):
```json
{
  "success": true,
  "record_count": 45,
  "data": [
    {
      "id": 1,
      "task_id": "T001",
      "task_name": "IRB Approval - Kenya",
      "category": "Regulatory",
      "predicted_duration_days": 45,
      "actual_duration_days": 62,
      "country_code": "KE",
      "authority": "PPB Kenya",
      "study_phase": "Phase III",
      "therapeutic_area": "Infectious Disease",
      "variance_days": 17,
      "variance_percent": 37.78,
      "was_accurate": false,
      "project_id": "ABC-123",
      "recorded_at": "2026-02-15 14:30:00",
      "recorded_by": "user@example.com"
    },
    ...
  ]
}
```

---

## Method 2: Direct Database Access (Advanced)

### Option A: Via Render Shell (If you have access)

**Step 1: Install Render CLI**
```bash
npm install -g @render/cli
```

**Step 2: Login to Render**
```bash
render login
```

**Step 3: Connect to your service**
```bash
# List your services
render services list

# Connect to the ilanapm service
render shell ilanapm
```

**Step 4: Access the database**
```bash
cd backend/database
sqlite3 feedback.db

-- View table structure
.schema task_outcomes

-- Count records
SELECT COUNT(*) FROM task_outcomes;

-- View recent submissions
SELECT
    task_name,
    country_code,
    actual_duration_days,
    recorded_at
FROM task_outcomes
ORDER BY recorded_at DESC
LIMIT 10;

-- Exit
.quit
```

---

### Option B: Download Database File

**Step 1: Create download script**

Add this endpoint to `backend/api/feedback.py`:
```python
@router.get("/feedback/download-db", tags=["admin"])
async def download_database():
    """Download the entire feedback database file"""
    from fastapi.responses import FileResponse
    import os

    db_path = "backend/database/feedback.db"

    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Database not found")

    return FileResponse(
        path=db_path,
        filename="feedback.db",
        media_type="application/x-sqlite3"
    )
```

**Step 2: Download the file**
```bash
curl "https://ilanapm.onrender.com/api/v1/feedback/download-db" > feedback_local.db
```

**Step 3: Analyze locally**
```bash
sqlite3 feedback_local.db

-- Quick stats
SELECT
    COUNT(*) as total_records,
    COUNT(DISTINCT country_code) as countries,
    MIN(recorded_at) as first_record,
    MAX(recorded_at) as last_record
FROM task_outcomes;

-- Accuracy by country
SELECT
    country_code,
    COUNT(*) as samples,
    AVG(ABS(variance_percent)) as avg_error_pct,
    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as accuracy_rate
FROM task_outcomes
WHERE predicted_duration_days IS NOT NULL
GROUP BY country_code
ORDER BY samples DESC;

-- Most common tasks
SELECT
    task_name,
    COUNT(*) as frequency,
    AVG(actual_duration_days) as avg_duration
FROM task_outcomes
GROUP BY task_name
ORDER BY frequency DESC
LIMIT 10;
```

---

## Method 3: Python Analysis (Recommended for Data Scientists)

### Step 1: Download data via API

```python
import requests
import pandas as pd
import json

# Fetch data
response = requests.get('https://ilanapm.onrender.com/api/v1/feedback/export?limit=1000')
data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data['data'])

# Save locally
df.to_csv('feedback_data.csv', index=False)
print(f"Downloaded {len(df)} records")
```

---

### Step 2: Analyze with pandas

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('feedback_data.csv')

# Basic statistics
print("="*60)
print("FEEDBACK DATA SUMMARY")
print("="*60)
print(f"Total Records: {len(df)}")
print(f"Date Range: {df['recorded_at'].min()} to {df['recorded_at'].max()}")
print(f"Countries: {df['country_code'].nunique()}")
print(f"Unique Tasks: {df['task_name'].nunique()}")
print(f"Projects: {df['project_id'].nunique()}")
print()

# Accuracy statistics (if predictions exist)
if 'predicted_duration_days' in df.columns:
    predicted = df[df['predicted_duration_days'].notna()]
    print("PREDICTION ACCURACY")
    print("="*60)
    print(f"Tasks with predictions: {len(predicted)}")
    print(f"Accurate (±20%): {predicted['was_accurate'].sum()} ({predicted['was_accurate'].mean()*100:.1f}%)")
    print(f"Mean absolute error: {predicted['variance_days'].abs().mean():.1f} days")
    print()

# Country breakdown
print("RECORDS BY COUNTRY")
print("="*60)
country_counts = df['country_code'].value_counts()
print(country_counts)
print()

# Category breakdown
print("RECORDS BY CATEGORY")
print("="*60)
category_counts = df['category'].value_counts()
print(category_counts)
print()

# Most common tasks
print("TOP 10 MOST FREQUENT TASKS")
print("="*60)
task_freq = df['task_name'].value_counts().head(10)
for task, count in task_freq.items():
    avg_duration = df[df['task_name'] == task]['actual_duration_days'].mean()
    print(f"{task}: {count} occurrences (avg: {avg_duration:.1f} days)")
```

---

### Step 3: Visualizations

```python
# Duration distribution
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
df['actual_duration_days'].hist(bins=30, edgecolor='black')
plt.xlabel('Duration (days)')
plt.ylabel('Frequency')
plt.title('Task Duration Distribution')

# Variance distribution (if predictions exist)
if 'variance_days' in df.columns:
    plt.subplot(1, 2, 2)
    df['variance_days'].hist(bins=30, edgecolor='black', color='orange')
    plt.xlabel('Variance (days)')
    plt.ylabel('Frequency')
    plt.title('Prediction Variance Distribution')

plt.tight_layout()
plt.savefig('duration_analysis.png', dpi=150)
print("\nSaved: duration_analysis.png")

# Country comparison
if len(df['country_code'].unique()) > 1:
    plt.figure(figsize=(10, 6))
    df.groupby('country_code')['actual_duration_days'].mean().sort_values().plot(kind='barh')
    plt.xlabel('Average Duration (days)')
    plt.ylabel('Country')
    plt.title('Average Task Duration by Country')
    plt.tight_layout()
    plt.savefig('country_comparison.png', dpi=150)
    print("Saved: country_comparison.png")

# Category comparison
plt.figure(figsize=(10, 6))
df.groupby('category')['actual_duration_days'].mean().sort_values().plot(kind='barh', color='green')
plt.xlabel('Average Duration (days)')
plt.ylabel('Category')
plt.title('Average Task Duration by Category')
plt.tight_layout()
plt.savefig('category_comparison.png', dpi=150)
print("Saved: category_comparison.png")

# Timeline of submissions
df['recorded_date'] = pd.to_datetime(df['recorded_at']).dt.date
daily_submissions = df.groupby('recorded_date').size()

plt.figure(figsize=(12, 5))
daily_submissions.plot(kind='line', marker='o')
plt.xlabel('Date')
plt.ylabel('Submissions')
plt.title('Daily Feedback Submissions')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('submission_timeline.png', dpi=150)
print("Saved: submission_timeline.png")

print("\nAnalysis complete!")
```

---

## Method 4: Web Dashboard (Future Enhancement)

### Planned Features

**Real-time Dashboard** at `/admin/feedback`:
- Total records count
- Records by country (bar chart)
- Records by category (pie chart)
- Submission timeline (line chart)
- Accuracy metrics (gauge chart)
- Recent submissions table

**Mock-up**:
```
┌─────────────────────────────────────────────────────────────┐
│ Ilana PM - Feedback Dashboard                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Total Records: 245         Countries: 12                   │
│  Projects: 45               Accuracy: 78%                    │
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │ Records by Country  │  │ Records by Category │          │
│  │                     │  │                     │          │
│  │ Kenya:     45 ████  │  │ Regulatory:  85 ███ │          │
│  │ US:        38 ███   │  │ Operational: 60 ██  │          │
│  │ Vietnam:   32 ███   │  │ Data:        45 ██  │          │
│  │ India:     28 ██    │  │ Site:        35 █   │          │
│  │ ...                 │  │ ...                 │          │
│  └─────────────────────┘  └─────────────────────┘          │
│                                                              │
│  Recent Submissions:                                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Date       │ Task               │ Country │ Duration │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ 2026-02-15 │ IRB Approval       │ KE      │ 62 days  │  │
│  │ 2026-02-15 │ Site Contract      │ US      │ 145 days │  │
│  │ 2026-02-14 │ Protocol Dev       │ VN      │ 180 days │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Interpreting the Data

### Key Metrics to Look For

**1. Data Volume**:
- < 50 records: Too early for ML training
- 50-100 records: Can start basic analysis
- 100-500 records: Ready for first ML model
- 500+ records: Robust ML training possible
- 1000+ records: High-quality predictions expected

**2. Country Coverage**:
- Goal: 20+ samples per country
- Priority countries: US, Kenya, Vietnam, India, UK
- Need coverage for reliable country-specific predictions

**3. Category Distribution**:
```
Regulatory: 30%    ← High value (critical path tasks)
Operational: 25%   ← Important for planning
Site: 20%          ← Site activities
Data: 15%          ← Database and analysis
Closeout: 10%      ← Final study activities
```

**4. Accuracy Trends** (when predictions exist):
```
Month 1: 60% accurate (baseline)
Month 2: 65% accurate (slight improvement)
Month 3: 70% accurate (learning!)
Month 6: 75% accurate (good predictions)
Month 12: 80%+ accurate (excellent!)
```

---

### Red Flags to Watch For

**⚠️ Too Much Variance**:
```
Task: "Site Contract Execution"
Samples: 10
Min: 90 days, Max: 365 days (4X difference!)

→ Action: Investigate if different site types (Academic vs Independent)
→ Solution: Add "site_type" field to feedback
```

**⚠️ Biased Sample**:
```
Country breakdown:
US: 200 records (82%)
Kenya: 30 records (12%)
Vietnam: 15 records (6%)

→ Issue: US-biased predictions won't work well for Kenya/Vietnam
→ Solution: Encourage international users to submit feedback
```

**⚠️ Outliers**:
```
Task: "IRB Approval - Kenya"
Samples: 15
Typical: 55-65 days
Outlier: 180 days (one record)

→ Action: Investigate outlier (data entry error? Special circumstance?)
→ Solution: Implement outlier detection and validation
```

---

## What Data Looks Like Initially

### First Week (Expected)

**Total Records**: 0
- No users have completed tasks yet
- Desktop add-in installed but projects in progress
- Feedback captures on task completion only

**Status**: ⏳ Waiting for first data

---

### First Month (Expected)

**Total Records**: 5-15
- Early adopter users complete first few tasks
- Mix of task types
- Limited country coverage (probably US-heavy)

**Example Data**:
```
1. Protocol Development (US, Phase III, Oncology): 180 days
2. IRB Approval (US, Phase II, Cardiovascular): 45 days
3. Site Contract Execution (US, Phase III, Oncology): 145 days
4. Site Initiation Visit (Kenya, Phase III, Infectious Disease): 7 days
5. Data Collection Forms (US, Phase II, Neurology): 28 days
```

**Status**: 📊 Data collecting, not enough for ML yet

---

### After 3 Months (Expected)

**Total Records**: 50-100
- Multiple users contributing
- Starting to see patterns by country
- Some tasks have 3-5 samples (minimum for learning)

**Ready For**: Basic statistical analysis, identify high-variance tasks

---

### After 6 Months (Expected)

**Total Records**: 150-300
- Solid data coverage
- Multiple countries represented
- Many tasks have 5-10 samples

**Ready For**: First ML model training, initial predictions

---

### After 1 Year (Goal)

**Total Records**: 500-1000
- Comprehensive coverage
- All major countries represented
- High confidence predictions possible

**Ready For**: Production ML model deployment, context-aware predictions

---

## Quick Commands Cheat Sheet

```bash
# Check if data exists
curl https://ilanapm.onrender.com/api/v1/feedback/summary | python3 -m json.tool

# Export all data
curl https://ilanapm.onrender.com/api/v1/feedback/export > feedback.json

# Export by country
curl "https://ilanapm.onrender.com/api/v1/feedback/export?country_code=KE" > kenya.json

# Export by phase
curl "https://ilanapm.onrender.com/api/v1/feedback/export?study_phase=Phase%20III" > phase3.json

# View data (pretty print)
cat feedback.json | python3 -m json.tool | head -50

# Count records
cat feedback.json | python3 -c "import sys, json; print(len(json.load(sys.stdin)['data']))"

# Convert to CSV (requires jq)
cat feedback.json | jq -r '.data[] | [.task_name, .country_code, .actual_duration_days] | @csv' > feedback.csv
```

---

## Next Steps

1. **Now**: Deploy API endpoints for data access
2. **Week 1**: Monitor for first submissions
3. **Month 1**: Review data quality and coverage
4. **Month 3**: Start statistical analysis
5. **Month 6**: Train first ML model
6. **Year 1**: Production ML deployment

---

## Support

**Questions?**
- API not working? Check Render logs
- Database empty? Normal - waiting for user submissions
- Need specific query? Modify SQL in API endpoints

**Contact**: Check backend logs for errors, verify API endpoints are deployed

---

*Quick start guide complete - ready to view feedback data as soon as users submit!*
