"""
Feedback API endpoints for collecting task completion data

Enables ML learning by tracking predicted vs actual durations
"""

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import logging

from models.feedback import (
    TaskCompletionFeedback,
    TaskCompletionResponse,
    AccuracyReport
)
from database import get_db_connection
from database.connection import DB_TYPE
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


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

            # Check for duplicate submission (if project_id and task_id provided)
            if feedback.project_id and feedback.task_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM task_outcomes WHERE project_id=? AND task_id=?",
                    (feedback.project_id, feedback.task_id)
                )
                if cursor.fetchone()[0] > 0:
                    logger.warning(
                        f"Duplicate feedback attempt: project={feedback.project_id}, "
                        f"task={feedback.task_id} - updating existing record"
                    )
                    # Update existing record instead of inserting new one
                    cursor.execute("""
                        UPDATE task_outcomes
                        SET actual_duration_days=?, actual_start_date=?, actual_end_date=?,
                            variance_days=?, variance_percent=?, was_accurate=?,
                            recorded_by=?, category=?, country_code=?, authority=?,
                            study_phase=?, therapeutic_area=?
                        WHERE project_id=? AND task_id=?
                    """, (
                        feedback.actual_duration_days,
                        feedback.actual_start_date,
                        feedback.actual_end_date,
                        variance_days,
                        variance_percent,
                        was_accurate,
                        feedback.recorded_by,
                        feedback.category,
                        feedback.country_code,
                        feedback.authority,
                        feedback.study_phase,
                        feedback.therapeutic_area,
                        feedback.project_id,
                        feedback.task_id
                    ))

                    # Get total count
                    cursor.execute("SELECT COUNT(*) FROM task_outcomes")
                    total_count = cursor.fetchone()[0]

                    # Build accuracy summary
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

                    logger.info(
                        f"Feedback updated: task_id={feedback.task_id}, "
                        f"task_name='{feedback.task_name}', country={feedback.country_code}, "
                        f"authority={feedback.authority}, variance={variance_days} days, "
                        f"accurate={was_accurate}, total_entries={total_count}"
                    )

                    return TaskCompletionResponse(
                        success=True,
                        recorded_count=1,
                        message=f"Task completion updated (duplicate). Total feedback entries: {total_count}",
                        accuracy_summary=accuracy_summary
                    )

            # No duplicate - insert new record
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

        # Log successful feedback submission
        logger.info(
            f"Feedback recorded: task_id={feedback.task_id}, "
            f"task_name='{feedback.task_name}', country={feedback.country_code}, "
            f"authority={feedback.authority}, variance={variance_days} days, "
            f"accurate={was_accurate}, total_entries={total_count}"
        )

        return TaskCompletionResponse(
            success=True,
            recorded_count=1,
            message=f"Task completion recorded. Total feedback entries: {total_count}",
            accuracy_summary=accuracy_summary
        )

    except Exception as e:
        logger.error(f"Failed to record feedback for task {feedback.task_id}: {str(e)}")
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

                # Check for duplicate in bulk submission
                is_duplicate = False
                if feedback.project_id and feedback.task_id:
                    cursor.execute(
                        "SELECT COUNT(*) FROM task_outcomes WHERE project_id=? AND task_id=?",
                        (feedback.project_id, feedback.task_id)
                    )
                    if cursor.fetchone()[0] > 0:
                        is_duplicate = True
                        logger.warning(
                            f"Duplicate in bulk: project={feedback.project_id}, task={feedback.task_id} - updating"
                        )
                        cursor.execute("""
                            UPDATE task_outcomes
                            SET actual_duration_days=?, actual_start_date=?, actual_end_date=?,
                                variance_days=?, variance_percent=?, was_accurate=?,
                                recorded_by=?, category=?, country_code=?, authority=?,
                                study_phase=?, therapeutic_area=?
                            WHERE project_id=? AND task_id=?
                        """, (
                            feedback.actual_duration_days,
                            feedback.actual_start_date,
                            feedback.actual_end_date,
                            variance_days,
                            variance_percent,
                            was_accurate,
                            feedback.recorded_by,
                            feedback.category,
                            feedback.country_code,
                            feedback.authority,
                            feedback.study_phase,
                            feedback.therapeutic_area,
                            feedback.project_id,
                            feedback.task_id
                        ))
                        recorded_count += 1

                if not is_duplicate:
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

        # Log bulk submission
        logger.info(
            f"Bulk feedback recorded: {recorded_count} tasks, "
            f"total_entries={total_count}"
        )

        return TaskCompletionResponse(
            success=True,
            recorded_count=recorded_count,
            message=f"Recorded {recorded_count} task completions. Total feedback entries: {total_count}"
        )

    except Exception as e:
        logger.error(f"Failed to record bulk feedback: {str(e)}")
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

        # Log accuracy report generation
        logger.info(
            f"Accuracy report generated: total={overall['total']}, "
            f"accurate={overall['accurate']}, accuracy_rate={accuracy_rate:.1f}%, "
            f"avg_error={overall['avg_error_days']:.1f} days"
        )

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
        logger.error(f"Failed to generate accuracy report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate accuracy report: {str(e)}")


class AccuracyTrends(BaseModel):
    """ML Accuracy Dashboard - Trends over time"""
    overall_trend: dict
    last_7_days: dict
    last_30_days: dict
    last_90_days: dict
    improvement: dict
    monthly_breakdown: List[dict]


@router.get("/feedback/accuracy-trends", response_model=AccuracyTrends)
async def get_accuracy_trends() -> AccuracyTrends:
    """
    Get ML accuracy trends over time for dashboard

    Shows how prediction accuracy is improving/declining over different time periods.
    Useful for ML Accuracy Dashboard UI.

    Returns:
        AccuracyTrends with:
        - overall_trend: All-time accuracy stats
        - last_7_days: Recent week performance
        - last_30_days: Last month performance
        - last_90_days: Last quarter performance
        - improvement: Change from previous period
        - monthly_breakdown: Month-by-month accuracy

    Example Response:
        ```json
        {
            "overall_trend": {
                "total": 150,
                "accurate": 112,
                "accuracy_rate": 74.7,
                "avg_error_days": 12.3
            },
            "last_30_days": {
                "total": 45,
                "accurate": 38,
                "accuracy_rate": 84.4,
                "avg_error_days": 8.1
            },
            "improvement": {
                "accuracy_change_pct": +9.7,
                "trending": "improving"
            },
            "monthly_breakdown": [
                {"month": "2026-01", "accuracy_rate": 84.4, "total": 45},
                {"month": "2025-12", "accuracy_rate": 71.2, "total": 62}
            ]
        }
        ```
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Overall trend (all time)
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate,
                    AVG(ABS(variance_days)) as avg_error_days,
                    AVG(ABS(variance_percent)) as avg_error_percent
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL
            """)
            overall = cursor.fetchone()

            overall_trend = {
                "total": overall['total'],
                "accurate": overall['accurate'],
                "accuracy_rate": round((overall['accurate'] / overall['total']) * 100, 1) if overall['total'] > 0 else 0.0,
                "avg_error_days": round(overall['avg_error_days'], 1) if overall['avg_error_days'] else 0.0
            }

            # Last 7 days
            if DB_TYPE == "postgresql":
                date_7_days = "NOW() - INTERVAL '7 days'"
            else:
                date_7_days = "datetime('now', '-7 days')"

            cursor.execute(f"""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate,
                    AVG(ABS(variance_days)) as avg_error_days
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL
                AND recorded_at >= {date_7_days}
            """)
            last_7 = cursor.fetchone()

            last_7_days = {
                "total": last_7['total'],
                "accurate": last_7['accurate'],
                "accuracy_rate": round((last_7['accurate'] / last_7['total']) * 100, 1) if last_7['total'] > 0 else 0.0,
                "avg_error_days": round(last_7['avg_error_days'], 1) if last_7['avg_error_days'] else 0.0
            }

            # Last 30 days
            if DB_TYPE == "postgresql":
                date_30_days = "NOW() - INTERVAL '30 days'"
            else:
                date_30_days = "datetime('now', '-30 days')"

            cursor.execute(f"""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate,
                    AVG(ABS(variance_days)) as avg_error_days
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL
                AND recorded_at >= {date_30_days}
            """)
            last_30 = cursor.fetchone()

            last_30_days = {
                "total": last_30['total'],
                "accurate": last_30['accurate'],
                "accuracy_rate": round((last_30['accurate'] / last_30['total']) * 100, 1) if last_30['total'] > 0 else 0.0,
                "avg_error_days": round(last_30['avg_error_days'], 1) if last_30['avg_error_days'] else 0.0
            }

            # Last 90 days
            if DB_TYPE == "postgresql":
                date_90_days = "NOW() - INTERVAL '90 days'"
            else:
                date_90_days = "datetime('now', '-90 days')"

            cursor.execute(f"""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate,
                    AVG(ABS(variance_days)) as avg_error_days
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL
                AND recorded_at >= {date_90_days}
            """)
            last_90 = cursor.fetchone()

            last_90_days = {
                "total": last_90['total'],
                "accurate": last_90['accurate'],
                "accuracy_rate": round((last_90['accurate'] / last_90['total']) * 100, 1) if last_90['total'] > 0 else 0.0,
                "avg_error_days": round(last_90['avg_error_days'], 1) if last_90['avg_error_days'] else 0.0
            }

            # Previous 30 days (for comparison)
            if DB_TYPE == "postgresql":
                date_60_days = "NOW() - INTERVAL '60 days'"
                date_30_days_cmp = "NOW() - INTERVAL '30 days'"
            else:
                date_60_days = "datetime('now', '-60 days')"
                date_30_days_cmp = "datetime('now', '-30 days')"

            cursor.execute(f"""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL
                AND recorded_at >= {date_60_days}
                AND recorded_at < {date_30_days_cmp}
            """)
            prev_30 = cursor.fetchone()

            prev_30_rate = round((prev_30['accurate'] / prev_30['total']) * 100, 1) if prev_30['total'] > 0 else 0.0

            # Calculate improvement
            accuracy_change = last_30_days['accuracy_rate'] - prev_30_rate if prev_30['total'] > 0 else 0.0
            trending = "improving" if accuracy_change > 2 else ("declining" if accuracy_change < -2 else "stable")

            improvement = {
                "accuracy_change_pct": round(accuracy_change, 1),
                "trending": trending,
                "previous_period_rate": prev_30_rate,
                "current_period_rate": last_30_days['accuracy_rate']
            }

            # Monthly breakdown (last 6 months)
            if DB_TYPE == "postgresql":
                month_format = "to_char(recorded_at, 'YYYY-MM')"
                date_6_months = "NOW() - INTERVAL '6 months'"
            else:
                month_format = "strftime('%Y-%m', recorded_at)"
                date_6_months = "datetime('now', '-6 months')"

            cursor.execute(f"""
                SELECT
                    {month_format} as month,
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate,
                    AVG(ABS(variance_days)) as avg_error_days
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL
                AND recorded_at >= {date_6_months}
                GROUP BY {month_format}
                ORDER BY month DESC
            """)
            monthly_breakdown = [
                {
                    "month": row['month'],
                    "total": row['total'],
                    "accurate": row['accurate'],
                    "accuracy_rate": round((row['accurate'] / row['total']) * 100, 1) if row['total'] > 0 else 0.0,
                    "avg_error_days": round(row['avg_error_days'], 1) if row['avg_error_days'] else 0.0
                }
                for row in cursor.fetchall()
            ]

        logger.info(
            f"Accuracy trends generated: overall={overall_trend['accuracy_rate']}%, "
            f"last_30d={last_30_days['accuracy_rate']}%, "
            f"trend={trending}"
        )

        return AccuracyTrends(
            overall_trend=overall_trend,
            last_7_days=last_7_days,
            last_30_days=last_30_days,
            last_90_days=last_90_days,
            improvement=improvement,
            monthly_breakdown=monthly_breakdown
        )

    except Exception as e:
        logger.error(f"Failed to generate accuracy trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate accuracy trends: {str(e)}")


__all__ = ["router"]
