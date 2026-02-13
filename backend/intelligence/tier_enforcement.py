"""
Tier Enforcement for Intelligence Features

Provides decorators and utilities for checking tier-based access to intelligence features.
"""

from functools import wraps
from fastapi import HTTPException, status
from typing import List, Optional, Callable
import logging

logger = logging.getLogger(__name__)

# Tier hierarchy (higher number = more features)
# Updated: Single tier only - all customers get all features
# Kept for backward compatibility but all tiers have same level
TIER_HIERARCHY = {
    "enterprise": 1,
    "calibrated": 1,   # Backward compatibility
    "professional": 1,  # Backward compatibility
}

# Feature availability by tier
# Updated: Single tier - all customers get all features
ALL_FEATURES = [
    "variance_detection",
    "benchmark_retrieval",
    "financial_impact",
    "basic_task_normalization",
    "basic_metadata_inference",
    "view_task_mappings",
    "view_project_profiles",
    "leadership_dashboard",
    "tracker_upload",
    "signal_extraction",
    "study_health_score",
    "signal_correlation",
    "advanced_task_normalization",
    "metadata_inference",
    "edit_task_mappings",
    "create_project_profiles",
    "confidence_scoring",
    "benchmark_blending",
    "calibration_upload",
    "pattern_detection",
    "custom_column_mapping",
    "custom_signal_rules",
    "escalation_filtering",
    "intervention_recommendations",
    "portfolio_analytics",
    "resource_collision_detection",
    "portfolio_forecasting",
    "ml_task_classification",
    "custom_field_definitions",
    "portfolio_aggregation",
    "pattern_detection_cross_study",
    "api_access_full",
    "sso_saml",
    "custom_tracker_types",
]

TIER_FEATURES = {
    "enterprise": ALL_FEATURES,
    "calibrated": ALL_FEATURES,   # Backward compatibility
    "professional": ALL_FEATURES,  # Backward compatibility
}


def get_tier_level(tier: str) -> int:
    """Get numeric level for tier"""
    return TIER_HIERARCHY.get(tier.lower(), 0)


def check_tier(required_tier: str, user_tier: str) -> bool:
    """
    Check if user's tier meets the required tier level

    Updated: Always returns True (all customers get all features)
    Kept for backward compatibility

    Args:
        required_tier: Minimum tier required (ignored)
        user_tier: User's current tier (ignored)

    Returns:
        bool: Always True (no tier gating)
    """
    return True


def check_feature_access(feature: str, user_tier: str) -> bool:
    """
    Check if user's tier has access to a specific feature

    Updated: Always returns True (all customers get all features)
    Kept for backward compatibility

    Args:
        feature: Feature name to check (ignored)
        user_tier: User's current tier (ignored)

    Returns:
        bool: Always True (no feature gating)
    """
    return True


def require_tier(required_tier: str, feature_name: Optional[str] = None):
    """
    Decorator for backward compatibility - no longer enforces tier restrictions

    Updated: All customers get all features, so this decorator just logs and allows access
    Kept for backward compatibility with existing code

    Usage:
        @require_tier("enterprise", feature_name="portfolio_analytics")
        async def get_portfolio(...):
            ...

    Args:
        required_tier: Ignored (kept for backward compatibility)
        feature_name: Ignored (kept for backward compatibility)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # All features available to all customers
            # Just log for analytics purposes
            logger.info(f"Access granted to {func.__name__} (all features enabled)")
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def get_available_features(tier: str) -> List[str]:
    """
    Get list of features available for a tier

    Updated: Returns all features for any tier (no tier gating)
    Kept for backward compatibility

    Args:
        tier: Tier name (ignored)

    Returns:
        List of all feature names
    """
    return ALL_FEATURES


def get_upgrade_message(current_tier: str, feature: str) -> str:
    """
    Generate user-friendly upgrade message

    Args:
        current_tier: User's current tier
        feature: Feature they tried to access

    Returns:
        str: User-friendly upgrade message
    """
    for tier_name, features in TIER_FEATURES.items():
        if feature in features:
            required_tier = tier_name
            break
    else:
        required_tier = "enterprise"

    return (
        f"The '{feature}' feature requires {required_tier.title()} tier. "
        f"You are currently on {current_tier.title()} tier. "
        f"Please upgrade to access this feature."
    )
