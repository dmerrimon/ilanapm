"""
ML Model Performance Monitoring

Monitors prediction accuracy and determines when models need retraining
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


def check_model_performance() -> Dict[str, Any]:
    """
    Check if models need retraining based on accuracy metrics

    Returns:
        dict: {
            'needs_retraining': bool,
            'reasons': List[str],
            'report': dict  # Full accuracy report
        }
    """
    try:
        # Import here to avoid circular dependencies
        from database.feedback_db import get_accuracy_report

        report = get_accuracy_report()

        # Thresholds
        MIN_TASKS = 50  # Minimum tasks needed for meaningful retraining
        MIN_ACCURACY = 0.70  # 70% accuracy threshold

        needs_retraining = False
        reasons = []

        # Overall accuracy check
        if report['total_predictions'] >= MIN_TASKS:
            if report['accuracy_rate'] < MIN_ACCURACY:
                needs_retraining = True
                reasons.append(
                    f"Overall accuracy {report['accuracy_rate']:.1%} below {MIN_ACCURACY:.0%} threshold"
                )
                logger.warning(f"Model accuracy below threshold: {report['accuracy_rate']:.1%}")
        else:
            logger.info(
                f"Insufficient data for retraining: {report['total_predictions']} tasks "
                f"(need {MIN_TASKS}+)"
            )

        # Category-specific checks
        for category_stat in report.get('by_category', []):
            if category_stat['count'] >= 20:  # Enough data for category-specific check
                if category_stat['accuracy_rate'] < MIN_ACCURACY:
                    needs_retraining = True
                    reasons.append(
                        f"{category_stat['category']}: {category_stat['accuracy_rate']:.1%} accuracy"
                    )
                    logger.warning(
                        f"Category {category_stat['category']} below threshold: "
                        f"{category_stat['accuracy_rate']:.1%}"
                    )

        # Country-specific checks
        for country_stat in report.get('by_country', []):
            if country_stat['count'] >= 20:
                if country_stat['accuracy_rate'] < MIN_ACCURACY:
                    needs_retraining = True
                    reasons.append(
                        f"{country_stat['country']}: {country_stat['accuracy_rate']:.1%} accuracy"
                    )

        result = {
            'needs_retraining': needs_retraining,
            'reasons': reasons,
            'report': report
        }

        if needs_retraining:
            logger.warning(f"Model retraining recommended: {', '.join(reasons)}")
        else:
            logger.info(f"Model performance acceptable: {report['accuracy_rate']:.1%} accuracy")

        return result

    except Exception as e:
        logger.error(f"Error checking model performance: {e}")
        return {
            'needs_retraining': False,
            'reasons': [f"Error: {str(e)}"],
            'report': {}
        }


def get_performance_summary() -> Dict[str, Any]:
    """
    Get a summary of current model performance

    Returns:
        dict: Performance metrics and statistics
    """
    try:
        from database.feedback_db import get_accuracy_report, get_accuracy_trends

        accuracy_report = get_accuracy_report()
        trends = get_accuracy_trends()

        return {
            'overall_accuracy': accuracy_report.get('accuracy_rate', 0),
            'total_predictions': accuracy_report.get('total_predictions', 0),
            'avg_error_days': accuracy_report.get('avg_error_days', 0),
            'trend': trends.get('overall', {}).get('trend', 'unknown'),
            'by_category': accuracy_report.get('by_category', []),
            'by_country': accuracy_report.get('by_country', []),
            'recommendations': accuracy_report.get('recommendations', [])
        }
    except Exception as e:
        logger.error(f"Error getting performance summary: {e}")
        return {}


if __name__ == "__main__":
    # For testing
    logging.basicConfig(level=logging.INFO)
    result = check_model_performance()
    print(f"\nNeeds Retraining: {result['needs_retraining']}")
    print(f"Reasons: {result['reasons']}")
    print(f"Total Predictions: {result['report'].get('total_predictions', 0)}")
