"""
ML Model Retraining Pipeline

Retrains duration prediction models using feedback data from completed tasks
"""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def retrain_duration_model() -> bool:
    """
    Retrain duration predictor using feedback data from task completions

    Returns:
        bool: True if retraining succeeded, False otherwise
    """
    try:
        logger.info("=" * 80)
        logger.info("Starting ML model retraining...")
        logger.info("=" * 80)

        # Import here to avoid circular dependencies
        from database.feedback_db import get_task_outcomes

        # Fetch all task outcomes
        outcomes = get_task_outcomes()

        if len(outcomes) < 50:
            logger.warning(
                f"Insufficient data for retraining: {len(outcomes)} tasks (need 50+)"
            )
            return False

        logger.info(f"Processing {len(outcomes)} task outcomes for retraining")

        # Group data by (category, country, authority)
        training_data = group_training_data(outcomes)

        logger.info(
            f"Grouped into {len(training_data)} unique (category, country, authority) combinations"
        )

        # Calculate adjustment factors
        adjustments = calculate_adjustment_factors(training_data)

        if not adjustments:
            logger.warning("No adjustment factors calculated (insufficient data per group)")
            return False

        logger.info(f"Calculated {len(adjustments)} adjustment factors")

        # Log adjustment factors
        log_adjustment_factors(adjustments)

        # TODO: Persist adjustments to database or model file
        # For now, adjustments are logged but not persisted
        # In production, would save to:
        # - Database table: model_adjustments(category, country, authority, factor, samples)
        # - Or model file: duration_predictor_adjustments.json

        logger.info("=" * 80)
        logger.info("Model retraining completed successfully")
        logger.info("=" * 80)

        return True

    except Exception as e:
        logger.error(f"Error during model retraining: {e}")
        return False


def group_training_data(outcomes: List[Dict]) -> Dict[Tuple, List[Dict]]:
    """
    Group outcomes by (category, country, authority)

    Args:
        outcomes: List of task outcome dictionaries

    Returns:
        dict: Grouped training data
    """
    training_data = {}

    for outcome in outcomes:
        # Create grouping key
        category = outcome.get('category', 'Unknown')
        country = outcome.get('country_code', 'Unknown')
        authority = outcome.get('authority', 'Unknown')

        key = (category, country, authority)

        if key not in training_data:
            training_data[key] = []

        training_data[key].append({
            'predicted': outcome.get('predicted_duration_days', 0),
            'actual': outcome.get('actual_duration_days', 0),
            'variance': outcome.get('variance_days', 0),
            'task_name': outcome.get('task_name', 'Unknown')
        })

    return training_data


def calculate_adjustment_factors(
    training_data: Dict[Tuple, List[Dict]]
) -> Dict[Tuple, Dict[str, Any]]:
    """
    Calculate adjustment factors for each group

    Args:
        training_data: Grouped training data

    Returns:
        dict: Adjustment factors by group
    """
    adjustments = {}
    MIN_SAMPLES = 10  # Need at least 10 samples per group

    for key, data in training_data.items():
        if len(data) < MIN_SAMPLES:
            continue

        # Calculate averages
        predicted_values = [d['predicted'] for d in data if d['predicted'] > 0]
        actual_values = [d['actual'] for d in data if d['actual'] > 0]

        if not predicted_values or not actual_values:
            continue

        avg_predicted = sum(predicted_values) / len(predicted_values)
        avg_actual = sum(actual_values) / len(actual_values)

        # Calculate adjustment factor
        adjustment_factor = avg_actual / avg_predicted if avg_predicted > 0 else 1.0

        # Calculate variance metrics
        variances = [d['variance'] for d in data]
        avg_variance = sum(variances) / len(variances)
        abs_variances = [abs(v) for v in variances]
        avg_abs_variance = sum(abs_variances) / len(abs_variances)

        adjustments[key] = {
            'factor': adjustment_factor,
            'sample_count': len(data),
            'avg_predicted': avg_predicted,
            'avg_actual': avg_actual,
            'avg_variance': avg_variance,
            'avg_abs_variance': avg_abs_variance,
            'improvement_needed': adjustment_factor < 0.8 or adjustment_factor > 1.2
        }

    return adjustments


def log_adjustment_factors(adjustments: Dict[Tuple, Dict[str, Any]]):
    """
    Log calculated adjustment factors

    Args:
        adjustments: Dictionary of adjustment factors
    """
    logger.info("\nAdjustment Factors:")
    logger.info("-" * 100)
    logger.info(
        f"{'Category':<20} {'Country':<10} {'Authority':<15} {'Factor':<10} "
        f"{'Samples':<10} {'Avg Error':<12}"
    )
    logger.info("-" * 100)

    # Sort by factor (most needing adjustment first)
    sorted_adjustments = sorted(
        adjustments.items(),
        key=lambda x: abs(x[1]['factor'] - 1.0),
        reverse=True
    )

    for key, adj in sorted_adjustments:
        category, country, authority = key

        # Format output
        factor_str = f"{adj['factor']:.2f}"
        if adj['improvement_needed']:
            factor_str += " ⚠️"

        logger.info(
            f"{category:<20} {country:<10} {authority:<15} {factor_str:<10} "
            f"{adj['sample_count']:<10} {adj['avg_variance']:+.1f} days"
        )

    logger.info("-" * 100)


def get_retraining_status() -> Dict[str, Any]:
    """
    Get current retraining status and statistics

    Returns:
        dict: Retraining status information
    """
    try:
        from database.feedback_db import get_task_outcomes

        outcomes = get_task_outcomes()

        return {
            'total_outcomes': len(outcomes),
            'can_retrain': len(outcomes) >= 50,
            'last_check': datetime.utcnow().isoformat(),
            'min_samples_required': 50
        }
    except Exception as e:
        logger.error(f"Error getting retraining status: {e}")
        return {}


if __name__ == "__main__":
    # For testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    success = retrain_duration_model()
    print(f"\nRetraining {'succeeded' if success else 'failed'}")
