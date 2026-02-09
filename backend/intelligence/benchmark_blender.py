"""
Benchmark Blending Engine
Blends organization-specific benchmarks with industry benchmarks
"""

from typing import List, Dict, Optional
from .models import OrgBenchmark, BenchmarkData, BlendedBenchmark


class BenchmarkBlender:
    """
    Blends organization-specific benchmarks with industry benchmarks
    using configurable ratios
    """

    def __init__(self, default_org_weight: float = 0.7):
        """
        Initialize blender

        Args:
            default_org_weight: Default weight for org benchmarks (0-1)
                               Industry weight = 1 - org_weight
        """
        self.default_org_weight = default_org_weight
        self.default_industry_weight = 1.0 - default_org_weight

    def blend_benchmarks(
        self,
        org_benchmarks: List[OrgBenchmark],
        industry_benchmarks: List[BenchmarkData],
        org_weight: Optional[float] = None,
        min_org_samples: int = 3
    ) -> List[BlendedBenchmark]:
        """
        Blend organization and industry benchmarks

        Args:
            org_benchmarks: Organization-specific benchmarks from calibration
            industry_benchmarks: Industry benchmarks from ontology
            org_weight: Optional custom org weight (overrides default)
            min_org_samples: Minimum org samples required to use org benchmark

        Returns:
            List of blended benchmarks
        """
        # Use custom weight or default
        org_w = org_weight if org_weight is not None else self.default_org_weight
        ind_w = 1.0 - org_w

        # Create lookup maps
        org_map = {b.ontology_task_id: b for b in org_benchmarks}
        industry_map = {b.task_id: b for b in industry_benchmarks}

        blended = []

        # Get all unique task IDs
        all_task_ids = set(org_map.keys()) | set(industry_map.keys())

        for task_id in all_task_ids:
            org_bench = org_map.get(task_id)
            ind_bench = industry_map.get(task_id)

            # Determine blending strategy
            if org_bench and ind_bench:
                # Both available - blend if org has enough samples
                if org_bench.sample_size >= min_org_samples:
                    blended_median = (
                        org_bench.median_days * org_w +
                        ind_bench.median_days * ind_w
                    )

                    blended.append(BlendedBenchmark(
                        task_id=task_id,
                        task_name=org_bench.task_name,
                        category=org_bench.category,
                        org_median_days=org_bench.median_days,
                        industry_median_days=ind_bench.median_days,
                        blended_median_days=round(blended_median, 1),
                        blend_ratio={"org": org_w, "industry": ind_w},
                        org_sample_size=org_bench.sample_size,
                        confidence=self._calculate_blend_confidence(
                            org_bench.sample_size,
                            org_bench.confidence
                        )
                    ))
                else:
                    # Not enough org samples - use industry only
                    blended.append(BlendedBenchmark(
                        task_id=task_id,
                        task_name=ind_bench.task_name,
                        category=ind_bench.category,
                        org_median_days=org_bench.median_days,
                        industry_median_days=ind_bench.median_days,
                        blended_median_days=ind_bench.median_days,
                        blend_ratio={"org": 0.0, "industry": 1.0},
                        org_sample_size=org_bench.sample_size,
                        confidence=0.5  # Medium confidence - not enough org data
                    ))

            elif ind_bench:
                # Only industry available
                blended.append(BlendedBenchmark(
                    task_id=task_id,
                    task_name=ind_bench.task_name,
                    category=ind_bench.category,
                    org_median_days=None,
                    industry_median_days=ind_bench.median_days,
                    blended_median_days=ind_bench.median_days,
                    blend_ratio={"org": 0.0, "industry": 1.0},
                    org_sample_size=0,
                    confidence=0.6  # Industry-only confidence
                ))

            elif org_bench:
                # Only org available (rare - means task not in ontology)
                blended.append(BlendedBenchmark(
                    task_id=task_id,
                    task_name=org_bench.task_name,
                    category=org_bench.category,
                    org_median_days=org_bench.median_days,
                    industry_median_days=0.0,  # No industry data
                    blended_median_days=org_bench.median_days,
                    blend_ratio={"org": 1.0, "industry": 0.0},
                    org_sample_size=org_bench.sample_size,
                    confidence=org_bench.confidence * 0.8  # Lower confidence without industry validation
                ))

        return blended

    def _calculate_blend_confidence(
        self,
        org_sample_size: int,
        org_confidence: float
    ) -> float:
        """
        Calculate confidence score for blended benchmark

        Higher confidence with more org samples and higher org confidence
        """
        # Base confidence from org data quality
        base_confidence = org_confidence

        # Bonus for sample size (up to +0.2 at 10+ samples)
        sample_bonus = min(org_sample_size / 50, 0.2)

        # Blend confidence (max 1.0)
        return min(base_confidence + sample_bonus, 1.0)

    def get_benchmark_for_task(
        self,
        task_id: str,
        blended_benchmarks: List[BlendedBenchmark]
    ) -> Optional[BlendedBenchmark]:
        """
        Retrieve a specific blended benchmark by task ID
        """
        for benchmark in blended_benchmarks:
            if benchmark.task_id == task_id:
                return benchmark
        return None

    def calculate_blend_statistics(
        self,
        blended_benchmarks: List[BlendedBenchmark]
    ) -> Dict[str, any]:
        """
        Calculate statistics about the blended benchmark set
        """
        if not blended_benchmarks:
            return {
                "total_benchmarks": 0,
                "org_only": 0,
                "industry_only": 0,
                "blended": 0,
                "avg_org_samples": 0,
                "avg_confidence": 0
            }

        org_only = sum(1 for b in blended_benchmarks if b.blend_ratio["org"] == 1.0)
        ind_only = sum(1 for b in blended_benchmarks if b.blend_ratio["industry"] == 1.0)
        blended = sum(1 for b in blended_benchmarks
                     if 0 < b.blend_ratio["org"] < 1.0)

        avg_samples = sum(b.org_sample_size for b in blended_benchmarks) / len(blended_benchmarks)
        avg_confidence = sum(b.confidence for b in blended_benchmarks) / len(blended_benchmarks)

        return {
            "total_benchmarks": len(blended_benchmarks),
            "org_only": org_only,
            "industry_only": ind_only,
            "blended": blended,
            "avg_org_samples": round(avg_samples, 1),
            "avg_confidence": round(avg_confidence, 2)
        }
