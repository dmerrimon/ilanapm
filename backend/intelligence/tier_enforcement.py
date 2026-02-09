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
TIER_HIERARCHY = {
    "core": 1,
    "calibrated": 2,
    "enterprise": 3,
    "professional": 2,  # Alias for calibrated (backward compatibility)
}

# Feature availability by tier
TIER_FEATURES = {
    "core": [
        "variance_detection",
        "benchmark_retrieval",
        "financial_impact",
        "basic_task_normalization",
        "basic_metadata_inference",
        "view_task_mappings",
        "view_project_profiles",
    ],
    "calibrated": [
        # Core features (inherited)
        "variance_detection",
        "benchmark_retrieval",
        "financial_impact",
        "basic_task_normalization",
        "basic_metadata_inference",
        "view_task_mappings",
        "view_project_profiles",
        # Calibrated-specific features
        "advanced_task_normalization",  # NLP semantic similarity
        "metadata_inference",
        "edit_task_mappings",
        "create_project_profiles",
        "confidence_scoring",
        "benchmark_blending",
        "calibration_upload",
        "pattern_detection",
    ],
    "enterprise": [
        # Core features (inherited)
        "variance_detection",
        "benchmark_retrieval",
        "financial_impact",
        "basic_task_normalization",
        "basic_metadata_inference",
        "view_task_mappings",
        "view_project_profiles",
        # Calibrated features (inherited)
        "advanced_task_normalization",
        "metadata_inference",
        "edit_task_mappings",
        "create_project_profiles",
        "confidence_scoring",
        "benchmark_blending",
        "calibration_upload",
        "pattern_detection",
        # Enterprise-specific features
        "portfolio_analytics",
        "resource_collision_detection",
        "portfolio_forecasting",
        "ml_task_classification",
        "custom_field_definitions",
    ]
}


def get_tier_level(tier: str) -> int:
    """Get numeric level for tier"""
    return TIER_HIERARCHY.get(tier.lower(), 0)


def check_tier(required_tier: str, user_tier: str) -> bool:
    """
    Check if user's tier meets the required tier level

    Args:
        required_tier: Minimum tier required
        user_tier: User's current tier

    Returns:
        bool: True if user has access, False otherwise
    """
    required_level = get_tier_level(required_tier)
    user_level = get_tier_level(user_tier)
    return user_level >= required_level


def check_feature_access(feature: str, user_tier: str) -> bool:
    """
    Check if user's tier has access to a specific feature

    Args:
        feature: Feature name to check
        user_tier: User's current tier

    Returns:
        bool: True if user has access, False otherwise
    """
    tier_features = TIER_FEATURES.get(user_tier.lower(), [])
    return feature in tier_features


def require_tier(required_tier: str, feature_name: Optional[str] = None):
    """
    Decorator to enforce tier-based access control on API endpoints

    Usage:
        @require_tier("calibrated", feature_name="confidence_scoring")
        async def get_confidence_score(...):
            ...

    Args:
        required_tier: Minimum tier required ("core", "calibrated", "enterprise")
        feature_name: Optional specific feature name to check
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract tier from kwargs (should be injected by auth middleware)
            user_tier = kwargs.get('tier') or kwargs.get('user_tier')

            if not user_tier:
                # Try to get from request context if available
                request = kwargs.get('request')
                if request and hasattr(request.state, 'tier'):
                    user_tier = request.state.tier
                else:
                    logger.error(f"No tier information found for {func.__name__}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )

            # Check tier level
            if not check_tier(required_tier, user_tier):
                logger.warning(
                    f"Tier access denied: {func.__name__} requires {required_tier}, user has {user_tier}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "Tier upgrade required",
                        "message": f"This feature requires {required_tier.title()} tier or higher",
                        "user_tier": user_tier,
                        "required_tier": required_tier,
                        "feature": feature_name or func.__name__,
                        "upgrade_url": "/portal/settings/billing"
                    }
                )

            # Check specific feature access if specified
            if feature_name and not check_feature_access(feature_name, user_tier):
                logger.warning(
                    f"Feature access denied: {feature_name} not available in {user_tier} tier"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error": "Feature not available",
                        "message": f"Feature '{feature_name}' is not available in your tier",
                        "user_tier": user_tier,
                        "feature": feature_name,
                        "upgrade_url": "/portal/settings/billing"
                    }
                )

            # Access granted, proceed with function
            logger.info(f"Tier access granted: {func.__name__} for tier {user_tier}")
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def get_available_features(tier: str) -> List[str]:
    """
    Get list of features available for a tier

    Args:
        tier: Tier name

    Returns:
        List of feature names
    """
    return TIER_FEATURES.get(tier.lower(), [])


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
