# Data Management and ML Training Infrastructure

## Overview

This document explains how user feedback data flows through the system, where it's stored, how to access it, and how to train ML models for template evolution.

---

## Data Flow Architecture

### End-to-End Data Journey

```
MS Project (User Desktop)
  ↓ Task marked 100% complete
  ↓ Project saved
Desktop Add-in (C#)
  ↓ AutoFeedbackService captures task data
  ↓ Stores in local settings (prevent duplicates)
  ↓ POST /api/v1/feedback/task-completion
  ↓
Backend API (FastAPI/Python)
  ↓ Validates data (Pydantic model)
  ↓ Calculates variance metrics
  ↓ INSERT INTO task_outcomes table
  ↓
SQLite Database (feedback.db)
  ↓ Stores task outcomes
  ↓ Available for queries and ML training
  ↓
Future: ML Training Pipeline
  ↓ Nightly export to training dataset
  ↓ Model training (XGBoost/Random Forest)
  ↓ Model deployment to API
  ↓ Enhanced template predictions
```

---

## Current Data Storage

### Backend Storage Location

**Server**: Render.com (https://ilanapm.onrender.com)
**Database File**: `/opt/render/project/src/backend/database/feedback.db`
**Database Type**: SQLite
**Backup**: Daily snapshots (Render automatic backups)

### Database Schema

```sql
-- Main table storing all task outcomes
CREATE TABLE task_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Task identification
    task_id TEXT NOT NULL,              -- MS Project task ID
    task_name TEXT NOT NULL,            -- Task name (free-form)
    category TEXT,                      -- Regulatory, Operational, etc.

    -- Prediction data (from ML model)
    predicted_duration_days INTEGER,
    predicted_confidence REAL,          -- 0-1 confidence score
    model_version TEXT,                 -- e.g., "v1.0"

    -- Actual outcome (what really happened)
    actual_duration_days INTEGER NOT NULL,
    actual_start_date DATE,
    actual_end_date DATE,

    -- Context (for ML learning)
    country_code TEXT,                  -- US, KE, VN, etc.
    authority TEXT,                     -- FDA, PPB, MHRA, etc.
    study_phase TEXT,                   -- Phase I, II, III, IV
    therapeutic_area TEXT,              -- Oncology, Cardiology, etc.

    -- Accuracy metrics (calculated by backend)
    variance_days INTEGER,              -- actual - predicted
    variance_percent REAL,              -- (variance / predicted) * 100
    was_accurate BOOLEAN,               -- Within ±20% threshold?

    -- Metadata
    project_id TEXT,                    -- MS Project file identifier
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recorded_by TEXT                    -- User who submitted
);

-- Indexes for fast queries
CREATE INDEX idx_country_authority ON task_outcomes(country_code, authority);
CREATE INDEX idx_category ON task_outcomes(category);
CREATE INDEX idx_recorded_at ON task_outcomes(recorded_at);
CREATE INDEX idx_accuracy ON task_outcomes(was_accurate);
CREATE INDEX idx_task_name ON task_outcomes(task_name);

-- View for quick accuracy summaries
CREATE VIEW prediction_accuracy_summary AS
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
```

---

## Accessing Feedback Data

### Method 1: Direct Database Access (Server)

**Step 1: SSH into Render server**
```bash
# Install Render CLI
npm install -g @render/cli

# Login to Render
render login

# Connect to your service
render services list
render shell ilanapm  # Your service name
```

**Step 2: Access SQLite database**
```bash
cd /opt/render/project/src/backend/database
sqlite3 feedback.db

# Check table structure
.schema task_outcomes

# View all data
SELECT * FROM task_outcomes;

# Count records
SELECT COUNT(*) FROM task_outcomes;

# Export to CSV
.mode csv
.output feedback_export.csv
SELECT * FROM task_outcomes;
.quit
```

---

### Method 2: API Endpoint (Recommended)

**Create Admin Endpoint for Data Access**

Add this to `backend/api/feedback.py`:

```python
@router.get("/feedback/export", tags=["admin"])
async def export_feedback_data(
    country_code: Optional[str] = None,
    study_phase: Optional[str] = None,
    limit: int = 1000
):
    """
    Export feedback data for analysis and ML training

    Query parameters:
    - country_code: Filter by country (e.g., 'KE', 'US')
    - study_phase: Filter by phase (e.g., 'Phase III')
    - limit: Maximum records to return (default: 1000)
    """
    try:
        with get_db_connection() as conn:
            query = "SELECT * FROM task_outcomes WHERE 1=1"
            params = []

            if country_code:
                query += " AND country_code = ?"
                params.append(country_code)

            if study_phase:
                query += " AND study_phase = ?"
                params.append(study_phase)

            query += f" ORDER BY recorded_at DESC LIMIT {limit}"

            cursor = conn.cursor()
            cursor.execute(query, params)

            # Get column names
            columns = [description[0] for description in cursor.description]

            # Fetch all rows
            rows = cursor.fetchall()

            # Convert to list of dicts
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))

            return {
                "success": True,
                "record_count": len(data),
                "data": data
            }

    except Exception as e:
        logger.error(f"Error exporting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/summary", tags=["admin"])
async def get_feedback_summary():
    """
    Get summary statistics of feedback data
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Overall stats
            cursor.execute("""
                SELECT
                    COUNT(*) as total_records,
                    COUNT(DISTINCT country_code) as countries,
                    COUNT(DISTINCT project_id) as projects,
                    MIN(recorded_at) as first_submission,
                    MAX(recorded_at) as last_submission,
                    AVG(CASE WHEN predicted_duration_days IS NOT NULL
                        THEN ABS(variance_percent) END) as avg_error_pct
                FROM task_outcomes
            """)

            overall = dict(cursor.fetchone())

            # By country
            cursor.execute("""
                SELECT
                    country_code,
                    COUNT(*) as record_count,
                    AVG(actual_duration_days) as avg_duration,
                    AVG(CASE WHEN predicted_duration_days IS NOT NULL
                        THEN ABS(variance_percent) END) as avg_error_pct
                FROM task_outcomes
                WHERE country_code IS NOT NULL
                GROUP BY country_code
                ORDER BY record_count DESC
            """)

            by_country = [dict(row) for row in cursor.fetchall()]

            # By category
            cursor.execute("""
                SELECT
                    category,
                    COUNT(*) as record_count,
                    AVG(actual_duration_days) as avg_duration
                FROM task_outcomes
                WHERE category IS NOT NULL
                GROUP BY category
                ORDER BY record_count DESC
            """)

            by_category = [dict(row) for row in cursor.fetchall()]

            return {
                "success": True,
                "overall": overall,
                "by_country": by_country,
                "by_category": by_category
            }

    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Using the API**:
```bash
# Get summary statistics
curl https://ilanapm.onrender.com/api/v1/feedback/summary

# Export all Kenya data
curl "https://ilanapm.onrender.com/api/v1/feedback/export?country_code=KE" > kenya_feedback.json

# Export Phase III data
curl "https://ilanapm.onrender.com/api/v1/feedback/export?study_phase=Phase%20III" > phase3_feedback.json

# Export recent 100 records
curl "https://ilanapm.onrender.com/api/v1/feedback/export?limit=100" > recent_feedback.json
```

---

### Method 3: Database Backup and Local Analysis

**Step 1: Download database backup**
```bash
# Via Render dashboard:
# 1. Go to Render dashboard → Your service
# 2. Click "Shell" tab
# 3. Run: cd backend/database && cat feedback.db | base64 > feedback_backup.txt
# 4. Copy the base64 text
# 5. Save locally and decode:

echo "paste_base64_text_here" | base64 -d > feedback_local.db
```

**Step 2: Analyze locally with SQLite**
```bash
sqlite3 feedback_local.db

-- View summary
SELECT
    COUNT(*) as total_records,
    COUNT(DISTINCT country_code) as countries,
    MIN(recorded_at) as first_record,
    MAX(recorded_at) as last_record
FROM task_outcomes;

-- View recent submissions
SELECT
    task_name,
    country_code,
    study_phase,
    actual_duration_days,
    recorded_at
FROM task_outcomes
ORDER BY recorded_at DESC
LIMIT 10;

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
```

**Step 3: Analyze with Python**
```python
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Connect to database
conn = sqlite3.connect('feedback_local.db')

# Load all data
df = pd.read_sql_query("SELECT * FROM task_outcomes", conn)

# Basic statistics
print(f"Total records: {len(df)}")
print(f"Countries: {df['country_code'].nunique()}")
print(f"Date range: {df['recorded_at'].min()} to {df['recorded_at'].max()}")

# Accuracy by country
accuracy = df[df['predicted_duration_days'].notna()].groupby('country_code').agg({
    'was_accurate': 'mean',
    'variance_days': 'mean',
    'task_name': 'count'
}).rename(columns={'task_name': 'sample_count'})

print("\nAccuracy by Country:")
print(accuracy)

# Plot variance distribution
plt.figure(figsize=(10, 6))
df[df['variance_days'].notna()]['variance_days'].hist(bins=30)
plt.xlabel('Variance (days)')
plt.ylabel('Frequency')
plt.title('Prediction Variance Distribution')
plt.savefig('variance_distribution.png')

# Task frequency
task_freq = df['task_name'].value_counts().head(10)
print("\nTop 10 Most Frequent Tasks:")
print(task_freq)

conn.close()
```

---

## ML Training Infrastructure

### Current State (Manual Training)

**When to Train Models**:
- After collecting 100+ feedback records
- After collecting 20+ records per country
- Quarterly or bi-annually initially
- Monthly once dataset grows to 500+ records

**Training Environment**:
- Local machine or cloud notebook (Google Colab, AWS SageMaker)
- Python 3.10+
- Libraries: pandas, scikit-learn, xgboost, joblib

---

### ML Training Pipeline (Future Implementation)

#### Step 1: Data Extraction and Preparation

```python
# scripts/ml_training/01_extract_data.py
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def extract_training_data(db_path, min_samples_per_task=5):
    """
    Extract and prepare data for ML training

    Filters:
    - Only tasks with sufficient samples
    - Only complete records (no missing critical fields)
    - Recent data (last 2 years)
    """
    conn = sqlite3.connect(db_path)

    # Load raw data
    query = """
        SELECT
            task_id,
            task_name,
            category,
            country_code,
            authority,
            study_phase,
            therapeutic_area,
            actual_duration_days,
            predicted_duration_days,
            recorded_at
        FROM task_outcomes
        WHERE actual_duration_days IS NOT NULL
          AND country_code IS NOT NULL
          AND category IS NOT NULL
          AND recorded_at >= date('now', '-2 years')
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    # Filter tasks with sufficient samples
    task_counts = df.groupby(['task_name', 'country_code']).size()
    valid_tasks = task_counts[task_counts >= min_samples_per_task].index

    df = df[df.set_index(['task_name', 'country_code']).index.isin(valid_tasks)]

    print(f"Training dataset: {len(df)} records")
    print(f"Unique tasks: {df['task_name'].nunique()}")
    print(f"Countries: {df['country_code'].unique()}")

    return df

# Usage
df_train = extract_training_data('feedback.db', min_samples_per_task=5)
df_train.to_csv('training_data.csv', index=False)
```

#### Step 2: Feature Engineering

```python
# scripts/ml_training/02_feature_engineering.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

def engineer_features(df):
    """
    Create features for ML model

    Features:
    - Task name keywords (TF-IDF)
    - Category (one-hot encoded)
    - Country (one-hot encoded)
    - Study phase (ordinal: I < II < III < IV)
    - Therapeutic area (one-hot encoded)
    """

    # Task name TF-IDF (extract keywords)
    tfidf = TfidfVectorizer(max_features=50, stop_words='english')
    task_name_features = tfidf.fit_transform(df['task_name']).toarray()
    task_name_df = pd.DataFrame(
        task_name_features,
        columns=[f'task_keyword_{i}' for i in range(50)]
    )

    # Category one-hot encoding
    category_dummies = pd.get_dummies(df['category'], prefix='category')

    # Country one-hot encoding
    country_dummies = pd.get_dummies(df['country_code'], prefix='country')

    # Study phase (ordinal encoding)
    phase_map = {'Phase I': 1, 'Phase II': 2, 'Phase III': 3, 'Phase IV': 4}
    df['phase_ordinal'] = df['study_phase'].map(phase_map).fillna(2)

    # Therapeutic area one-hot encoding
    area_dummies = pd.get_dummies(df['therapeutic_area'], prefix='area')

    # Combine all features
    X = pd.concat([
        task_name_df,
        category_dummies,
        country_dummies,
        df[['phase_ordinal']],
        area_dummies
    ], axis=1)

    # Target variable
    y = df['actual_duration_days']

    return X, y, tfidf

# Usage
X, y, tfidf_vectorizer = engineer_features(df_train)
print(f"Feature matrix shape: {X.shape}")
```

#### Step 3: Model Training

```python
# scripts/ml_training/03_train_model.py
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

def train_duration_model(X, y, model_type='xgboost'):
    """
    Train ML model to predict task durations

    Models:
    - RandomForest: Good baseline, interpretable
    - XGBoost: Better accuracy, handles missing data
    """

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    if model_type == 'xgboost':
        model = XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
    else:
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Calculate accuracy within ±20%
    within_20pct = sum(abs(y_test - y_pred) <= 0.2 * y_test) / len(y_test)

    print(f"\nModel Performance:")
    print(f"  MAE: {mae:.2f} days")
    print(f"  R²: {r2:.3f}")
    print(f"  Accuracy (±20%): {within_20pct*100:.1f}%")

    # Feature importance
    if hasattr(model, 'feature_importances_'):
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False).head(10)

        print("\nTop 10 Important Features:")
        print(feature_importance)

    return model

# Usage
model = train_duration_model(X, y, model_type='xgboost')

# Save model
joblib.dump(model, 'duration_predictor_v1.pkl')
joblib.dump(tfidf_vectorizer, 'tfidf_vectorizer_v1.pkl')
print("\nModel saved: duration_predictor_v1.pkl")
```

#### Step 4: Model Deployment

```python
# backend/ml/predictor.py
import joblib
import pandas as pd
from pathlib import Path

class DurationPredictor:
    """ML model for predicting task durations"""

    def __init__(self, model_path='ml/duration_predictor_v1.pkl',
                 tfidf_path='ml/tfidf_vectorizer_v1.pkl'):
        self.model = joblib.load(model_path)
        self.tfidf = joblib.load(tfidf_path)
        self.model_version = 'v1.0'

    def predict(self, task_name, category, country_code,
                study_phase, therapeutic_area):
        """
        Predict duration for a task

        Returns:
            predicted_duration: int (days)
            confidence: float (0-1)
        """

        # Prepare features (same as training)
        task_tfidf = self.tfidf.transform([task_name]).toarray()[0]

        # Create feature vector
        features = {
            **{f'task_keyword_{i}': val for i, val in enumerate(task_tfidf)},
            f'category_{category}': 1,
            f'country_{country_code}': 1,
            'phase_ordinal': self._phase_to_ordinal(study_phase),
            f'area_{therapeutic_area}': 1
        }

        # Fill missing features with 0
        all_features = self.model.feature_names_in_
        feature_vector = [features.get(f, 0) for f in all_features]

        # Predict
        X = pd.DataFrame([feature_vector], columns=all_features)
        prediction = self.model.predict(X)[0]

        # Calculate confidence (based on historical data similarity)
        confidence = self._calculate_confidence(
            task_name, category, country_code
        )

        return int(prediction), confidence

    def _phase_to_ordinal(self, phase):
        phase_map = {'Phase I': 1, 'Phase II': 2, 'Phase III': 3, 'Phase IV': 4}
        return phase_map.get(phase, 2)

    def _calculate_confidence(self, task_name, category, country_code):
        """
        Calculate confidence based on training data coverage

        Higher confidence when:
        - Similar task names in training data
        - Country has many samples
        - Category well-represented
        """
        # TODO: Implement confidence calculation
        # For now, return moderate confidence
        return 0.65

# Usage in API
predictor = DurationPredictor()

@router.get("/ml/predict-duration")
async def predict_task_duration(
    task_name: str,
    category: str,
    country_code: str,
    study_phase: str,
    therapeutic_area: str
):
    """Predict duration for a task using ML model"""

    predicted_duration, confidence = predictor.predict(
        task_name, category, country_code, study_phase, therapeutic_area
    )

    return {
        "predicted_duration_days": predicted_duration,
        "confidence": confidence,
        "model_version": predictor.model_version
    }
```

---

### Automated Training Pipeline (Advanced)

#### Nightly Training Job

```python
# scripts/ml_training/automated_pipeline.py
"""
Automated ML training pipeline - runs nightly via cron job
"""

import schedule
import time
from datetime import datetime

def train_and_deploy_model():
    """
    Complete training pipeline:
    1. Extract latest data
    2. Prepare features
    3. Train model
    4. Evaluate performance
    5. Deploy if better than current
    """

    print(f"\n{'='*60}")
    print(f"ML Training Pipeline - {datetime.now()}")
    print(f"{'='*60}\n")

    # Step 1: Extract data
    print("Step 1: Extracting training data...")
    df = extract_training_data('feedback.db')

    if len(df) < 100:
        print(f"  ⚠️  Insufficient data: {len(df)} records")
        print("  Minimum 100 records required for training")
        return

    # Step 2: Feature engineering
    print("\nStep 2: Engineering features...")
    X, y, tfidf = engineer_features(df)
    print(f"  ✓ Feature matrix: {X.shape}")

    # Step 3: Train new model
    print("\nStep 3: Training model...")
    new_model = train_duration_model(X, y)

    # Step 4: Compare with current model
    print("\nStep 4: Evaluating performance...")

    # Load current production model
    try:
        current_model = joblib.load('duration_predictor_v1.pkl')
        current_score = evaluate_model(current_model, X, y)
        new_score = evaluate_model(new_model, X, y)

        improvement = ((new_score - current_score) / current_score) * 100

        print(f"  Current model accuracy: {current_score*100:.1f}%")
        print(f"  New model accuracy: {new_score*100:.1f}%")
        print(f"  Improvement: {improvement:+.1f}%")

        # Deploy if better
        if new_score > current_score:
            print("\n  ✓ New model is better - deploying...")
            joblib.dump(new_model, 'duration_predictor_v1.pkl')
            joblib.dump(tfidf, 'tfidf_vectorizer_v1.pkl')
            print("  ✓ Deployment complete")
        else:
            print("\n  → Current model still better - keeping it")

    except FileNotFoundError:
        # No current model - deploy new one
        print("  → No current model - deploying new model...")
        joblib.dump(new_model, 'duration_predictor_v1.pkl')
        joblib.dump(tfidf, 'tfidf_vectorizer_v1.pkl')
        print("  ✓ Deployment complete")

    print(f"\n{'='*60}")
    print(f"Pipeline completed at {datetime.now()}")
    print(f"{'='*60}\n")

def evaluate_model(model, X, y):
    """Calculate model accuracy (% within ±20%)"""
    y_pred = model.predict(X)
    within_20pct = sum(abs(y - y_pred) <= 0.2 * y) / len(y)
    return within_20pct

# Schedule to run nightly at 2 AM
schedule.every().day.at("02:00").do(train_and_deploy_model)

print("ML Training Pipeline Scheduler Started")
print("Runs nightly at 2:00 AM")
print("Press Ctrl+C to stop\n")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

**Deploy as Background Service**:
```bash
# Create systemd service (Linux) or use cron job

# crontab -e
0 2 * * * cd /opt/render/project/src && python scripts/ml_training/automated_pipeline.py >> /var/log/ml_training.log 2>&1
```

---

## Data Privacy and Security

### Data Collection Policy

**What is collected**:
- ✅ Task name (free-form text)
- ✅ Category, phase, country, authority, therapeutic area
- ✅ Actual duration (days)
- ✅ Start/end dates
- ✅ Prediction accuracy metrics

**What is NOT collected**:
- ❌ Study name or protocol number
- ❌ Sponsor/CRO names
- ❌ Patient data or PII
- ❌ Site names or locations (beyond country)
- ❌ Budget or financial information
- ❌ Proprietary clinical data

### Data Retention

**Current**: Indefinite retention
- All feedback stored permanently
- Used for continuous ML improvement
- No automatic deletion

**Future**: Configurable retention policy
- Option to anonymize old data (>2 years)
- Option to delete project-specific data on request
- GDPR/CCPA compliance controls

### Data Access Control

**Current**: No authentication required
- API endpoints are public
- Anyone can query feedback data

**Recommended for Production**:
```python
# Add API key authentication
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "your_secret_api_key_here"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@router.get("/feedback/export")
async def export_feedback_data(api_key: str = Security(verify_api_key)):
    # Only accessible with valid API key
    ...
```

---

## Monitoring and Alerts

### Key Metrics to Monitor

**Data Quality**:
- Records per day
- Records per country
- Duplicate submissions
- Missing critical fields

**Model Performance**:
- Prediction accuracy (% within ±20%)
- Mean absolute error
- Accuracy by country/category
- Model drift detection

### Recommended Monitoring Setup

```python
# scripts/monitoring/daily_metrics.py
"""
Daily metrics report - email summary of feedback data
"""

def generate_daily_report():
    conn = sqlite3.connect('feedback.db')

    # Records today
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM task_outcomes
        WHERE DATE(recorded_at) = DATE('now')
    """)
    today_count = cursor.fetchone()[0]

    # Total records
    cursor.execute("SELECT COUNT(*) FROM task_outcomes")
    total_count = cursor.fetchone()[0]

    # Accuracy (last 7 days)
    cursor.execute("""
        SELECT
            AVG(CASE WHEN was_accurate THEN 1 ELSE 0 END) * 100 as accuracy
        FROM task_outcomes
        WHERE predicted_duration_days IS NOT NULL
          AND recorded_at >= DATE('now', '-7 days')
    """)
    weekly_accuracy = cursor.fetchone()[0]

    report = f"""
    Ilana PM - Daily Data Report
    Date: {datetime.now().strftime('%Y-%m-%d')}

    Records Submitted Today: {today_count}
    Total Records: {total_count}
    Weekly Accuracy: {weekly_accuracy:.1f}%

    Database: feedback.db
    Size: {get_db_size()} MB
    """

    # Email or log report
    print(report)
    # send_email(to='admin@example.com', subject='Daily Report', body=report)

    conn.close()

def get_db_size():
    """Get database file size in MB"""
    import os
    size_bytes = os.path.getsize('feedback.db')
    return size_bytes / (1024 * 1024)
```

---

## Summary

### Data Storage
- **Location**: Render server → SQLite database (feedback.db)
- **Access**: API endpoints, direct SSH, database backup
- **Schema**: task_outcomes table with full context

### Viewing Data
1. **API**: `/api/v1/feedback/export` (recommended)
2. **Direct**: SSH + sqlite3 commands
3. **Backup**: Download DB → analyze locally with Python/SQL

### ML Training
1. **Extract**: Query task_outcomes table
2. **Prepare**: Feature engineering (TF-IDF, one-hot, ordinal)
3. **Train**: XGBoost/RandomForest models
4. **Deploy**: Save .pkl files → API loads model
5. **Automate**: Nightly training pipeline (future)

### Next Steps
1. ✅ Collect feedback data (automatic)
2. → Reach 100+ records minimum
3. → Train first ML model manually
4. → Deploy model to API
5. → Set up automated training pipeline
6. → Monitor accuracy and iterate

---

*All infrastructure documented and ready for ML training when data threshold reached!*
