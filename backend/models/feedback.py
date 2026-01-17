"""
Feedback models for task completion data

Tracks predicted vs actual durations to enable ML learning
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class TaskCompletionFeedback(BaseModel):
    """Feedback when a task is completed"""

    # Task identification
    task_id: str = Field(..., description="Task ID from MS Project")
    task_name: str = Field(..., description="Task name")
    category: Optional[str] = Field(None, description="Task category (Regulatory, Operational, etc.)")

    # Prediction data (what ML predicted)
    predicted_duration_days: Optional[int] = Field(None, ge=0, description="What the ML model predicted (must be >= 0)")
    predicted_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score (0-1)")
    model_version: Optional[str] = Field(None, description="Which model made the prediction")

    # Actual outcome (what really happened)
    actual_duration_days: int = Field(..., ge=0, description="Actual duration from MS Project (must be >= 0)")
    actual_start_date: Optional[str] = Field(None, description="Actual start date (YYYY-MM-DD)")
    actual_end_date: Optional[str] = Field(None, description="Actual end date (YYYY-MM-DD)")

    # Context for learning
    country_code: Optional[str] = Field(None, description="ISO country code (US, KE, VN)")
    authority: Optional[str] = Field(None, description="Regulatory authority (FDA, PPB, etc.)")
    study_phase: Optional[str] = Field(None, description="Study phase (Phase I, II, III, IV)")
    therapeutic_area: Optional[str] = Field(None, description="Therapeutic area (Oncology, etc.)")

    # Metadata
    project_id: Optional[str] = Field(None, description="MS Project file identifier")
    recorded_by: Optional[str] = Field(None, description="User who submitted feedback")

    @field_validator('actual_start_date', 'actual_end_date')
    @classmethod
    def validate_date_format(cls, v):
        """Validate date is in YYYY-MM-DD format"""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format (e.g., 2025-01-15)')
        return v


class TaskCompletionResponse(BaseModel):
    """Response after recording task completion"""
    success: bool
    recorded_count: int
    message: str
    accuracy_summary: Optional[dict] = None


class AccuracyReport(BaseModel):
    """Model accuracy report based on feedback data"""

    # Overall statistics
    total_predictions: int
    accurate_predictions: int  # Within ±20% threshold
    accuracy_rate: float  # Percentage
    avg_error_days: float
    avg_error_percent: float

    # By category
    by_category: dict  # category -> accuracy stats
    by_country: dict  # country_code -> accuracy stats
    by_authority: dict  # authority -> accuracy stats

    # Time range
    earliest_feedback: Optional[datetime] = None
    latest_feedback: Optional[datetime] = None

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)


__all__ = ["TaskCompletionFeedback", "TaskCompletionResponse", "AccuracyReport"]
