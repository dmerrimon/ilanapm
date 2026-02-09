"""
Financial Impact Calculator

Converts timeline variances to financial impact based on industry benchmarks.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class FinancialImpactCalculator:
    """
    Calculate financial impact of timeline variances

    Formula: variance_days * (baseline_rate / 30 days)

    Default baseline: $733,000/month (WCG Clintrax data)
    """

    def __init__(self, baseline_rate_per_month: float = 733000.0):
        """
        Initialize calculator

        Args:
            baseline_rate_per_month: Cost per month of delay (default: $733K)
        """
        self.baseline_rate_per_month = baseline_rate_per_month
        self.daily_rate = baseline_rate_per_month / 30.0
        logger.info(f"FinancialImpactCalculator initialized: ${baseline_rate_per_month:,.0f}/month (${self.daily_rate:,.0f}/day)")

    def calculate_impact(
        self,
        variance_days: int,
        baseline_rate: Optional[float] = None
    ) -> float:
        """
        Calculate financial impact of variance

        Args:
            variance_days: Difference in days (actual - benchmark)
                          Positive = overestimate (customer timeline too long)
                          Negative = underestimate (customer timeline too short)
            baseline_rate: Optional override for baseline rate (per month)

        Returns:
            float: Financial impact in USD
                   Positive = cost of overestimate (wasted buffer time)
                   Negative = risk cost of underestimate (potential delay)
        """
        rate = baseline_rate or self.baseline_rate_per_month
        daily_rate = rate / 30.0

        impact = variance_days * daily_rate

        if variance_days > 0:
            logger.debug(f"Overestimate: {variance_days} days = ${impact:,.0f} (wasted buffer)")
        elif variance_days < 0:
            logger.debug(f"Underestimate: {abs(variance_days)} days = ${abs(impact):,.0f} (delay risk)")
        else:
            logger.debug("On target: zero variance")

        return impact

    def calculate_aggregate_impact(
        self,
        variance_list: list[int],
        baseline_rate: Optional[float] = None
    ) -> dict:
        """
        Calculate aggregate financial impact across multiple tasks

        Args:
            variance_list: List of variance values in days
            baseline_rate: Optional override for baseline rate

        Returns:
            dict with total_impact, positive_impact, negative_impact, count
        """
        total_impact = 0.0
        positive_impact = 0.0  # Overestimates (wasted buffer)
        negative_impact = 0.0  # Underestimates (delay risk)

        for variance_days in variance_list:
            impact = self.calculate_impact(variance_days, baseline_rate)
            total_impact += impact

            if impact > 0:
                positive_impact += impact
            else:
                negative_impact += abs(impact)

        return {
            "total_impact_usd": total_impact,
            "positive_impact_usd": positive_impact,  # Wasted buffer
            "negative_impact_usd": negative_impact,  # Delay risk
            "net_impact_usd": total_impact,
            "count": len(variance_list),
            "avg_impact_per_task_usd": total_impact / len(variance_list) if variance_list else 0.0
        }

    def calculate_monthly_impact(
        self,
        total_days_variance: int,
        baseline_rate: Optional[float] = None
    ) -> dict:
        """
        Calculate impact broken down by months

        Args:
            total_days_variance: Total variance in days
            baseline_rate: Optional override for baseline rate

        Returns:
            dict with months, total_impact, breakdown
        """
        rate = baseline_rate or self.baseline_rate_per_month

        months = total_days_variance / 30.0
        total_impact = self.calculate_impact(total_days_variance, baseline_rate)

        return {
            "total_days": total_days_variance,
            "months": round(months, 2),
            "total_impact_usd": total_impact,
            "monthly_rate_usd": rate,
            "explanation": (
                f"{abs(total_days_variance)} days variance = "
                f"{abs(months):.1f} months × ${rate:,.0f}/month = "
                f"${abs(total_impact):,.0f}"
            )
        }

    def get_cost_per_day(self) -> float:
        """Get daily cost rate"""
        return self.daily_rate

    def get_cost_per_month(self) -> float:
        """Get monthly cost rate"""
        return self.baseline_rate_per_month

    def update_baseline_rate(self, new_rate_per_month: float):
        """
        Update baseline rate (for Enterprise tier custom rates)

        Args:
            new_rate_per_month: New cost per month of delay
        """
        old_rate = self.baseline_rate_per_month
        self.baseline_rate_per_month = new_rate_per_month
        self.daily_rate = new_rate_per_month / 30.0
        logger.info(f"Updated baseline rate: ${old_rate:,.0f} → ${new_rate_per_month:,.0f}/month")
