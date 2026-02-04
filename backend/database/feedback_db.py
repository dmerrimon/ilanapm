"""
Feedback database access functions

Provides direct database access for ML retraining pipeline
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from database.connection import get_db_connection

logger = logging.getLogger(__name__)


def get_task_outcomes() -> List[Dict[str, Any]]:
    """
    Get all task outcomes from database

    Returns:
        List of task outcome dictionaries
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    task_id,
                    task_name,
                    category,
                    predicted_duration_days,
                    predicted_confidence,
                    model_version,
                    actual_duration_days,
                    actual_start_date,
                    actual_end_date,
                    country_code,
                    authority,
                    study_phase,
                    therapeutic_area,
                    variance_days,
                    variance_percent,
                    was_accurate,
                    project_id,
                    recorded_at,
                    recorded_by
                FROM task_outcomes
                ORDER BY recorded_at DESC
            """)

            rows = cursor.fetchall()

            # Convert rows to dictionaries
            outcomes = []
            for row in rows:
                outcomes.append(dict(row))

            return outcomes

    except Exception as e:
        logger.error(f"Error fetching task outcomes: {e}")
        return []


def get_accuracy_report() -> Dict[str, Any]:
    """
    Get accuracy report with statistics

    Returns:
        Dictionary with accuracy metrics
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
                    AVG(ABS(variance_percent)) as avg_error_percent
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL
            """)
            overall = cursor.fetchone()

            if overall['total'] == 0:
                return {
                    'total_predictions': 0,
                    'accurate_predictions': 0,
                    'accuracy_rate': 0.0,
                    'avg_error_days': 0.0,
                    'avg_error_percent': 0.0,
                    'by_category': [],
                    'by_country': [],
                    'by_authority': [],
                    'recommendations': ['No data collected yet - start completing tasks!']
                }

            accuracy_rate = (overall['accurate'] / overall['total']) if overall['total'] > 0 else 0.0

            # By category
            cursor.execute("""
                SELECT
                    category,
                    COUNT(*) as count,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate,
                    AVG(ABS(variance_days)) as avg_error
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL AND category IS NOT NULL
                GROUP BY category
                ORDER BY count DESC
            """)
            by_category = []
            for row in cursor.fetchall():
                by_category.append({
                    'category': row['category'],
                    'count': row['count'],
                    'accurate': row['accurate'],
                    'accuracy_rate': (row['accurate'] / row['count']) if row['count'] > 0 else 0.0,
                    'avg_error': row['avg_error'] or 0.0
                })

            # By country
            cursor.execute("""
                SELECT
                    country_code,
                    COUNT(*) as count,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate,
                    AVG(ABS(variance_days)) as avg_error
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL AND country_code IS NOT NULL
                GROUP BY country_code
                ORDER BY count DESC
            """)
            by_country = []
            for row in cursor.fetchall():
                by_country.append({
                    'country': row['country_code'],
                    'count': row['count'],
                    'accurate': row['accurate'],
                    'accuracy_rate': (row['accurate'] / row['count']) if row['count'] > 0 else 0.0,
                    'avg_error': row['avg_error'] or 0.0
                })

            # By authority
            cursor.execute("""
                SELECT
                    authority,
                    COUNT(*) as count,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate,
                    AVG(ABS(variance_days)) as avg_error
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL AND authority IS NOT NULL
                GROUP BY authority
                ORDER BY count DESC
            """)
            by_authority = []
            for row in cursor.fetchall():
                by_authority.append({
                    'authority': row['authority'],
                    'count': row['count'],
                    'accurate': row['accurate'],
                    'accuracy_rate': (row['accurate'] / row['count']) if row['count'] > 0 else 0.0,
                    'avg_error': row['avg_error'] or 0.0
                })

            return {
                'total_predictions': overall['total'],
                'accurate_predictions': overall['accurate'],
                'accuracy_rate': accuracy_rate,
                'avg_error_days': overall['avg_error_days'] or 0.0,
                'avg_error_percent': overall['avg_error_percent'] or 0.0,
                'by_category': by_category,
                'by_country': by_country,
                'by_authority': by_authority,
                'recommendations': generate_recommendations(overall, by_category, by_country)
            }

    except Exception as e:
        logger.error(f"Error getting accuracy report: {e}")
        return {
            'total_predictions': 0,
            'accurate_predictions': 0,
            'accuracy_rate': 0.0,
            'avg_error_days': 0.0,
            'avg_error_percent': 0.0,
            'by_category': [],
            'by_country': [],
            'by_authority': [],
            'recommendations': [f'Error: {str(e)}']
        }


def get_accuracy_trends() -> Dict[str, Any]:
    """
    Get accuracy trends over time

    Returns:
        Dictionary with trend data
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Overall trend
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN was_accurate THEN 1 ELSE 0 END) as accurate,
                    AVG(ABS(variance_days)) as avg_error
                FROM task_outcomes
                WHERE predicted_duration_days IS NOT NULL
            """)
            overall = cursor.fetchone()

            overall_trend = {
                'total': overall['total'],
                'accurate': overall['accurate'],
                'accuracy_rate': (overall['accurate'] / overall['total']) if overall['total'] > 0 else 0.0,
                'avg_error_days': overall['avg_error'] or 0.0,
                'trend': 'stable'  # Simplified for now
            }

            return {
                'overall': overall_trend,
                'last_7_days': overall_trend,  # Simplified - would calculate actual time ranges
                'last_30_days': overall_trend,
                'last_90_days': overall_trend
            }

    except Exception as e:
        logger.error(f"Error getting accuracy trends: {e}")
        return {
            'overall': {'total': 0, 'accurate': 0, 'accuracy_rate': 0.0, 'avg_error_days': 0.0, 'trend': 'unknown'}
        }


def generate_recommendations(overall, by_category, by_country) -> List[str]:
    """Generate ML recommendations based on data"""
    recommendations = []

    total = overall['total']
    accuracy = (overall['accurate'] / total) if total > 0 else 0.0

    if total < 50:
        recommendations.append(
            f"📊 Collect more data: {total} tasks recorded, need 50+ for meaningful insights"
        )
        return recommendations

    if accuracy < 0.70:
        recommendations.append(
            f"⚠️  Overall accuracy {accuracy:.1%} below 70% threshold - model retraining recommended"
        )

    # Category-specific recommendations
    for cat in by_category:
        if cat['count'] >= 10 and cat['accuracy_rate'] < 0.70:
            recommendations.append(
                f"📉 {cat['category']}: {cat['accuracy_rate']:.1%} accuracy - review duration estimates"
            )

    # Country-specific recommendations
    for country in by_country:
        if country['count'] >= 10 and country['accuracy_rate'] < 0.70:
            recommendations.append(
                f"🌍 {country['country']}: {country['accuracy_rate']:.1%} accuracy - "
                f"update regulatory timelines"
            )

    if not recommendations:
        recommendations.append(f"✅ Model performing well: {accuracy:.1%} accuracy")

    return recommendations


__all__ = ['get_task_outcomes', 'get_accuracy_report', 'get_accuracy_trends']
