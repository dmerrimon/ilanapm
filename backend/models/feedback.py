"""
Feedback models for task completion data

Tracks predicted vs actual durations to enable ML learning

VERSION: 2.0 - DD-MM-YYYY clinical research format
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class TaskCompletionFeedback(BaseModel):
    """Feedback when a task is completed"""

    # Task identification
    task_id: str = Field(..., min_length=1, description="Task ID from MS Project (cannot be empty)")
    task_name: str = Field(..., min_length=1, description="Task name (cannot be empty)")
    category: Optional[str] = Field(None, description="Task category (Regulatory, Operational, etc.)")

    # Prediction data (what ML predicted)
    predicted_duration_days: Optional[int] = Field(None, ge=0, description="What the ML model predicted (must be >= 0)")
    predicted_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score (0-1)")
    model_version: Optional[str] = Field(None, description="Which model made the prediction")

    # Actual outcome (what really happened)
    actual_duration_days: int = Field(..., ge=0, description="Actual duration from MS Project (must be >= 0)")
    actual_start_date: Optional[str] = Field(None, description="Actual start date (DD-MM-YYYY)")
    actual_end_date: Optional[str] = Field(None, description="Actual end date (DD-MM-YYYY)")

    # Context for learning
    country_code: Optional[str] = Field(None, description="ISO country code (US, KE, VN)")
    authority: Optional[str] = Field(None, description="Regulatory authority (FDA, PPB, etc.)")
    study_phase: Optional[str] = Field(None, description="Study phase (Phase I, II, III, IV)")
    therapeutic_area: Optional[str] = Field(None, description="Therapeutic area (Oncology, etc.)")

    # Metadata
    project_id: Optional[str] = Field(None, description="MS Project file identifier")
    recorded_by: Optional[str] = Field(None, description="User who submitted feedback")

    @field_validator('actual_start_date', 'actual_end_date', mode='before')
    @classmethod
    def validate_date_format(cls, v):
        """Validate date is in DD-MM-YYYY format (clinical research standard) - VERSION 2.0"""
        if v is None or v == '':
            return v
        if not isinstance(v, str):
            raise ValueError(f'Date must be a string, got {type(v)}')

        # Accept DD-MM-YYYY format (clinical research standard)
        try:
            datetime.strptime(v, '%d-%m-%Y')
            return v  # Return unchanged DD-MM-YYYY string
        except ValueError:
            raise ValueError(f'Date must be in DD-MM-YYYY format (e.g., 15-01-2025), got: {v}')


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
