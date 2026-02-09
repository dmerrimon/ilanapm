"""
Benchmark Retriever - Query Ontology for Task-Specific Benchmarks

Implements fuzzy matching with fallback hierarchy to maximize benchmark coverage.
"""

import yaml
import os
from typing import Optional, Dict, List, Tuple
from difflib import SequenceMatcher
import logging
from pathlib import Path

from .models import BenchmarkData

logger = logging.getLogger(__name__)


class BenchmarkRetriever:
    """
    Retrieve benchmark data from task ontology with intelligent matching

    Match Priority:
    1. Exact match: category + task_name + country + authority
    2. Category + country + authority
    3. Category + special cases (site contracting, enrollment)
    4. Category baseline
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize BenchmarkRetriever

        Args:
            config_path: Path to task_ontology.yaml (if None, uses default)
        """
        self.config_path = config_path or self._get_default_config_path()
        self.ontology = self._load_ontology()
        self._build_cache()
        logger.info(f"BenchmarkRetriever initialized with {len(self.tasks)} tasks")

    def _get_default_config_path(self) -> str:
        """Get default path to task_ontology.yaml"""
        base_dir = Path(__file__).parent.parent
        return str(base_dir / "config" / "task_ontology.yaml")

    def _load_ontology(self) -> Dict:
        """Load task ontology from YAML"""
        try:
            with open(self.config_path, 'r') as f:
                ontology = yaml.safe_load(f)
            logger.info(f"Loaded ontology version {ontology.get('metadata', {}).get('version', 'unknown')}")
            return ontology
        except Exception as e:
            logger.error(f"Failed to load ontology: {e}")
            raise

    def _build_cache(self):
        """Build lookup caches for fast retrieval"""
        self.tasks = self.ontology.get('tasks', [])
        self.metadata = self.ontology.get('metadata', {})
        self.site_contracting = self.ontology.get('site_contracting', {})
        self.enrollment = self.ontology.get('enrollment', {})
        self.phase_durations = self.ontology.get('phase_durations', {})

        # Build category index
        self.category_index = {}
        for task in self.tasks:
            category = task.get('category', 'Unknown')
            if category not in self.category_index:
                self.category_index[category] = []
            self.category_index[category].append(task)

        # Build task name index
        self.task_name_index = {task['name'].lower(): task for task in self.tasks}

        logger.debug(f"Built caches: {len(self.category_index)} categories, {len(self.task_name_index)} task names")

    def get_benchmark(
        self,
        task_name: Optional[str] = None,
        category: Optional[str] = None,
        country: Optional[str] = None,
        authority: Optional[str] = None,
        phase: Optional[str] = None,
        therapeutic_area: Optional[str] = None,
        site_type: Optional[str] = None,
    ) -> Optional[BenchmarkData]:
        """
        Retrieve benchmark with fuzzy matching and fallback

        Args:
            task_name: Task name (e.g., "IRB Approval")
            category: Task category (e.g., "Regulatory")
            country: Country code (e.g., "US")
            authority: Regulatory authority (e.g., "FDA")
            phase: Study phase (e.g., "Phase III")
            therapeutic_area: Therapeutic area (e.g., "Oncology")
            site_type: Site type (e.g., "academic", "independent")

        Returns:
            BenchmarkData or None if no match found
        """
        # Try exact match first
        if task_name and category:
            benchmark = self._exact_match(task_name, category, country, authority)
            if benchmark:
                logger.debug(f"Exact match found for {task_name}")
                return benchmark

        # Try category + country match
        if category and country:
            benchmark = self._category_country_match(category, country, authority)
            if benchmark:
                logger.debug(f"Category+country match found for {category} in {country}")
                return benchmark

        # Try special case handlers
        if category:
            # Site contracting special case
            if category.lower() in ['site_contracting', 'contracting', 'site_contracts']:
                benchmark = self._site_contracting_benchmark(site_type or 'academic')
                if benchmark:
                    logger.debug(f"Site contracting benchmark found for {site_type}")
                    return benchmark

            # Enrollment special case
            if category.lower() in ['enrollment', 'patient_enrollment', 'recruitment']:
                benchmark = self._enrollment_benchmark(phase, therapeutic_area)
                if benchmark:
                    logger.debug(f"Enrollment benchmark found for {phase}/{therapeutic_area}")
                    return benchmark

        # Try fuzzy match on task name
        if task_name:
            benchmark = self._fuzzy_match(task_name, category)
            if benchmark:
                logger.debug(f"Fuzzy match found for {task_name}")
                return benchmark

        # Try category baseline
        if category:
            benchmark = self._category_baseline(category)
            if benchmark:
                logger.debug(f"Category baseline found for {category}")
                return benchmark

        logger.warning(f"No benchmark found for task_name={task_name}, category={category}, country={country}")
        return None

    def _exact_match(
        self,
        task_name: str,
        category: str,
        country: Optional[str] = None,
        authority: Optional[str] = None
    ) -> Optional[BenchmarkData]:
        """Try exact match: category + task_name + country + authority"""
        task_name_lower = task_name.lower()

        for task in self.tasks:
            if task.get('category', '').lower() != category.lower():
                continue

            if task['name'].lower() == task_name_lower:
                # Found matching task, now check for country-specific variation
                if country and 'country_variations' in task:
                    country_data = task['country_variations'].get(country.upper())
                    if country_data:
                        return self._build_benchmark_data(
                            task,
                            duration_override=country_data.get('duration_days', task['typical_duration_days']),
                            country=country,
                            authority=country_data.get('authority_code')
                        )

                # No country variation or no country specified, use base task
                return self._build_benchmark_data(task)

        return None

    def _category_country_match(
        self,
        category: str,
        country: str,
        authority: Optional[str] = None
    ) -> Optional[BenchmarkData]:
        """Try category + country match"""
        category_tasks = self.category_index.get(category, [])

        for task in category_tasks:
            if 'country_variations' in task and country.upper() in task['country_variations']:
                country_data = task['country_variations'][country.upper()]
                return self._build_benchmark_data(
                    task,
                    duration_override=country_data.get('duration_days', task['typical_duration_days']),
                    country=country,
                    authority=country_data.get('authority_code')
                )

        return None

    def _fuzzy_match(
        self,
        task_name: str,
        category: Optional[str] = None,
        threshold: float = 0.8
    ) -> Optional[BenchmarkData]:
        """Fuzzy match task name with similarity threshold"""
        best_match = None
        best_score = 0.0

        # Determine search space
        search_tasks = self.category_index.get(category, []) if category else self.tasks

        for task in search_tasks:
            score = SequenceMatcher(None, task_name.lower(), task['name'].lower()).ratio()
            if score > best_score and score >= threshold:
                best_score = score
                best_match = task

        if best_match:
            logger.info(f"Fuzzy match: '{task_name}' -> '{best_match['name']}' (score: {best_score:.2f})")
            return self._build_benchmark_data(best_match)

        return None

    def _category_baseline(self, category: str) -> Optional[BenchmarkData]:
        """Return baseline benchmark for category"""
        category_tasks = self.category_index.get(category, [])

        if not category_tasks:
            return None

        # Calculate median duration from all tasks in category
        durations = [task.get('typical_duration_days', 0) for task in category_tasks]
        durations = sorted([d for d in durations if d > 0])

        if not durations:
            return None

        median_duration = durations[len(durations) // 2]

        return BenchmarkData(
            task_id=f"BASELINE-{category.upper()}",
            task_name=f"{category} (Category Baseline)",
            category=category,
            median_days=median_duration,
            p25_days=int(median_duration * 0.75),
            p75_days=int(median_duration * 1.25),
            typical_duration_days=median_duration,
            source="Task Ontology Baseline",
            confidence="low",
            data_quality="Calculated from category median"
        )

    def _site_contracting_benchmark(self, site_type: str) -> Optional[BenchmarkData]:
        """Special handler for site contracting benchmarks"""
        site_type_lower = site_type.lower()

        if 'academic' in site_type_lower:
            data = self.site_contracting.get('academic_medical_centers', {})
        elif 'independent' in site_type_lower or 'private' in site_type_lower:
            data = self.site_contracting.get('independent_research_sites', {})
        else:
            # Default to academic (conservative estimate)
            data = self.site_contracting.get('academic_medical_centers', {})

        if not data:
            return None

        typical_days = data.get('typical_duration_days', 0)

        return BenchmarkData(
            task_id="SITE-CONTRACT-001",
            task_name=f"Site Contracting ({site_type})",
            category="Site_Contracting",
            median_days=typical_days,
            p25_days=data.get('min_days', int(typical_days * 0.75)),
            p75_days=data.get('max_days', int(typical_days * 1.3)),
            typical_duration_days=typical_days,
            source=data.get('source', 'WCG Clintrax'),
            confidence="high",
            data_quality=data.get('notes', '')
        )

    def _enrollment_benchmark(
        self,
        phase: Optional[str] = None,
        therapeutic_area: Optional[str] = None
    ) -> Optional[BenchmarkData]:
        """Special handler for enrollment benchmarks"""
        enrollment_data = self.enrollment.get('durations', {})

        # Try to find specific match
        if phase and therapeutic_area:
            key = f"{therapeutic_area.lower()}_phase_{phase.lower().replace('phase ', '').replace(' ', '_')}_days"
            if key in enrollment_data:
                duration = enrollment_data[key]
                return BenchmarkData(
                    task_id="ENROLL-001",
                    task_name=f"Enrollment ({therapeutic_area}, {phase})",
                    category="Enrollment",
                    median_days=duration,
                    p25_days=int(duration * 0.75),
                    p75_days=int(duration * 1.25),
                    typical_duration_days=duration,
                    source="CenterWatch Industry Surveys",
                    confidence="high",
                    phase=phase,
                    therapeutic_area=therapeutic_area
                )

        # Default to a conservative estimate
        default_duration = 365  # 12 months
        return BenchmarkData(
            task_id="ENROLL-BASELINE",
            task_name="Enrollment (Baseline)",
            category="Enrollment",
            median_days=default_duration,
            p25_days=270,
            p75_days=730,
            typical_duration_days=default_duration,
            source="CenterWatch Industry Surveys",
            confidence="medium",
            data_quality="Conservative baseline (90% must double timeline)"
        )

    def _build_benchmark_data(
        self,
        task: Dict,
        duration_override: Optional[int] = None,
        country: Optional[str] = None,
        authority: Optional[str] = None
    ) -> BenchmarkData:
        """Build BenchmarkData from task dict"""
        typical_duration = duration_override or task.get('typical_duration_days', 0)

        return BenchmarkData(
            task_id=task.get('id', 'UNKNOWN'),
            task_name=task.get('name', 'Unknown Task'),
            category=task.get('category', 'Unknown'),
            median_days=typical_duration,
            p25_days=task.get('min_duration_days', int(typical_duration * 0.75)),
            p75_days=task.get('max_duration_days', int(typical_duration * 1.25)),
            typical_duration_days=typical_duration,
            source=task.get('source', self.metadata.get('data_sources', ['Task Ontology'])[0]),
            confidence="high" if task.get('is_mandatory') else "medium",
            data_quality=task.get('notes', task.get('description', '')),
            country_code=country,
            authority=authority
        )

    def get_financial_baseline(self) -> float:
        """Get financial impact baseline (cost per month of delay)"""
        return self.metadata.get('financial_benchmarks', {}).get('cost_per_month_delay', 733000.0)

    def reload_ontology(self):
        """Reload ontology from disk (for hot-reload capability)"""
        logger.info("Reloading task ontology...")
        self.ontology = self._load_ontology()
        self._build_cache()
        logger.info("Ontology reloaded successfully")
