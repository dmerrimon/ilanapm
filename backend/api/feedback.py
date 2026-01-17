"""
Feedback API endpoints for collecting task completion data

Enables ML learning by tracking predicted vs actual durations
"""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from backend.models.feedback import (
    TaskCompletionFeedback,
    TaskCompletionResponse,
    AccuracyReport
)
from backend.database import get_db_connection

router = APIRouter()


@router.post("/feedback/task-completion", response_model=TaskCompletionResponse)
async def record_task_completion(feedback: TaskCompletionFeedback) -> TaskCompletionResponse:
    """
    Record task completion with predicted vs actual duration

    This data enables ML to learn from real project outcomes and improve predictions over time.
    """
    try:
        # Calculate variance
        variance_days = None
        variance_percent = None
        was_accurate = None

        if feedback.predicted_duration_days is not None and feedback.predicted_duration_days > 0:
            variance_days = feedback.actual_duration_days - feedback.predicted_duration_days
            variance_percent = (variance_days / feedback.predicted_duration_days) * 100
            # Consider accurate if within ±20% threshold
            was_accurate = abs(variance_percent) <= 20.0
        elif feedback.predicted_duration_days == 0 and feedback.actual_duration_days == 0:
            # Both predicted and actual are 0 - perfectly accurate instant task
            variance_days = 0
            variance_percent = 0.0
            was_accurate = True
        elif feedback.predicted_duration_days == 0:
            # Predicted 0 but actual > 0 - undefined percent variance, use absolute variance
            variance_days = feedback.actual_duration_days
            variance_percent = None  # Cannot calculate percentage
            was_accurate = False  # Predicted instant but took time

        # Insert into database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO task_outcomes (
                    task_id, task_name, category,
                    predicted_duration_days, predicted_confidence, model_version,
                    actual_duration_days, actual_start_date, actual_end_date,
                    country_code, authority, study_phase, therapeutic_area,
                    variance_days, variance_percent, was_accurate,
                    project_id, recorded_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.task_id,
                feedback.task_name,
                feedback.category,
                feedback.predicted_duration_days,
                feedback.predicted_confidence,
                feedback.model_version,
                feedback.actual_duration_days,
                feedback.actual_start_date,
                feedback.actual_end_date,
                feedback.country_code,
                feedback.authority,
                feedback.study_phase,
                feedback.therapeutic_area,
                variance_days,
                variance_percent,
                was_accurate,
                feedback.project_id,
                feedback.recorded_by
            ))

            # Get total count
            cursor.execute("SELECT COUNT(*) FROM task_outcomes")
            total_count = cursor.fetchone()[0]

        # Build accuracy summary if we have a prediction
        accuracy_summary = None
        if feedback.predicted_duration_days is not None:
            accuracy_summary = {
                "predicted_days": feedback.predicted_duration_days,
                "actual_days": feedback.actual_duration_days,
                "variance_days": variance_days,
                "variance_percent": round(variance_percent, 1) if variance_percent is not None else None,
                "was_accurate": was_accurate,
                "threshold": "±20%"
            }

        return TaskCompletionResponse(
            success=True,
            recorded_count=1,
            message=f"Task completion recorded. Total feedback entries: {total_count}",
            accuracy_summary=accuracy_summary
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")


@router.post("/feedback/task-completions", response_model=TaskCompletionResponse)
async def record_multiple_completions(
    completions: List[TaskCompletionFeedback]
) -> TaskCompletionResponse:
    """
    Record multiple task completions in bulk

    Useful when project completes and PM wants to submit all completed tasks at once.
    """
    if not completions:
        return TaskCompletionResponse(
            success=True,
            recorded_count=0,
            message="No completions to record"
        )

    try:
        recorded_count = 0

        with get_db_connection() as conn:
            cursor = conn.cursor()

            for feedback in completions:
                # Calculate variance
                variance_days = None
                variance_percent = None
                was_accurate = None

                if feedback.predicted_duration_days is not None and feedback.predicted_duration_days > 0:
                    variance_days = feedback.actual_duration_days - feedback.predicted_duration_days
                    variance_percent = (variance_days / feedback.predicted_duration_days) * 100
                    was_accurate = abs(variance_percent) <= 20.0
                elif feedback.predicted_duration_days == 0 and feedback.actual_duration_days == 0:
                    # Both predicted and actual are 0 - perfectly accurate instant task
                    variance_days = 0
                    variance_percent = 0.0
                    was_accurate = True
                elif feedback.predicted_duration_days == 0:
                    # Predicted 0 but actual > 0 - undefined percent variance
                    variance_days = feedback.actual_duration_days
                    variance_percent = None
                    was_accurate = False

                cursor.execute("""
                    INSERT INTO task_outcomes (
                        task_id, task_name, category,
                        predicted_duration_days, predicted_confidence, model_version,
                        actual_duration_days, actual_start_date, actual_end_date,
                        country_code, authority, study_phase, therapeutic_area,
                        variance_days, variance_percent, was_accurate,
                        project_id, recorded_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback.task_id,
                    feedback.task_name,
                    feedback.category,
                    feedback.predicted_duration_days,
                    feedback.predicted_confidence,
                    feedback.model_version,
                    feedback.actual_duration_days,
                    feedback.actual_start_date,
                    feedback.actual_end_date,
                    feedback.country_code,
                    feedback.authority,
                    feedback.study_phase,
                    feedback.therapeutic_area,
                    variance_days,
                    variance_percent,
                    was_accurate,
                    feedback.project_id,
                    feedback.recorded_by
                ))
                recorded_count += 1

            # Get total count
            cursor.execute("SELECT COUNT(*) FROM task_outcomes")
            total_count = cursor.fetchone()[0]

        return TaskCompletionResponse(
            success=True,
            recorded_count=recorded_count,
            message=f"Recorded {recorded_count} task completions. Total feedback entries: {total_count}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record feedback: {str(e)}")


@router.get("/feedback/accuracy-report", response_model=AccuracyReport)
async def get_accuracy_report() -> AccuracyReport:
    """
    Get model accuracy report based on collected feedback

    Shows how accurate predictions have been and identifies areas for improvement.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Overall statistics
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate,
                    AVG(ABS(variance_days)) as avg_error_days,
                    AVG(ABS(variance_percent)) as avg_error_percent,
                    MIN(recorded_at) as earliest,
                    MAX(recorded_at) as latest
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL
            """)
            overall = cursor.fetchone()

            if overall['total'] == 0:
                return AccuracyReport(
                    total_predictions=0,
                    accurate_predictions=0,
                    accuracy_rate=0.0,
                    avg_error_days=0.0,
                    avg_error_percent=0.0,
                    by_category={},
                    by_country={},
                    by_authority={},
                    recommendations=["No feedback data collected yet. Complete some tasks and submit feedback to see accuracy metrics."]
                )

            accuracy_rate = (overall['accurate'] / overall['total']) * 100 if overall['total'] > 0 else 0.0

            # By category
            cursor.execute("""
                SELECT
                    category,
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as accuracy_rate,
                    AVG(ABS(variance_days)) as avg_error_days
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL AND category IS NOT NULL
                GROUP BY category
            """)
            by_category = {
                row['category']: {
                    'total': row['total'],
                    'accuracy_rate': round(row['accuracy_rate'], 1),
                    'avg_error_days': round(row['avg_error_days'], 1)
                }
                for row in cursor.fetchall()
            }

            # By country
            cursor.execute("""
                SELECT
                    country_code,
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as accuracy_rate,
                    AVG(ABS(variance_days)) as avg_error_days
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL AND country_code IS NOT NULL
                GROUP BY country_code
            """)
            by_country = {
                row['country_code']: {
                    'total': row['total'],
                    'accuracy_rate': round(row['accuracy_rate'], 1),
                    'avg_error_days': round(row['avg_error_days'], 1)
                }
                for row in cursor.fetchall()
            }

            # By authority
            cursor.execute("""
                SELECT
                    authority,
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as accuracy_rate,
                    AVG(ABS(variance_days)) as avg_error_days
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL AND authority IS NOT NULL
                GROUP BY authority
            """)
            by_authority = {
                row['authority']: {
                    'total': row['total'],
                    'accuracy_rate': round(row['accuracy_rate'], 1),
                    'avg_error_days': round(row['avg_error_days'], 1)
                }
                for row in cursor.fetchall()
            }

        # Generate recommendations
        recommendations = []

        if overall['total'] < 10:
            recommendations.append(f"Only {overall['total']} tasks recorded. Collect more data (target: 50+) for meaningful insights.")

        if accuracy_rate < 70:
            recommendations.append(f"Overall accuracy is {accuracy_rate:.1f}%. Consider updating task ontology with more realistic durations.")

        # Identify worst performing categories
        worst_categories = sorted(
            [(cat, stats['accuracy_rate']) for cat, stats in by_category.items()],
            key=lambda x: x[1]
        )[:2]

        for cat, rate in worst_categories:
            if rate < 60:
                recommendations.append(f"{cat} tasks have {rate:.1f}% accuracy. Review {cat} duration estimates.")

        # Identify worst performing countries
        worst_countries = sorted(
            [(country, stats['accuracy_rate']) for country, stats in by_country.items()],
            key=lambda x: x[1]
        )[:2]

        for country, rate in worst_countries:
            if rate < 60:
                recommendations.append(f"{country} predictions have {rate:.1f}% accuracy. Update {country} regulatory workflow timelines.")

        if not recommendations:
            recommendations.append(f"✓ Good performance! {accuracy_rate:.1f}% accuracy across {overall['total']} tasks.")

        return AccuracyReport(
            total_predictions=overall['total'],
            accurate_predictions=overall['accurate'],
            accuracy_rate=round(accuracy_rate, 1),
            avg_error_days=round(overall['avg_error_days'], 1),
            avg_error_percent=round(overall['avg_error_percent'], 1),
            by_category=by_category,
            by_country=by_country,
            by_authority=by_authority,
            earliest_feedback=overall['earliest'],
            latest_feedback=overall['latest'],
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate accuracy report: {str(e)}")


__all__ = ["router"]
