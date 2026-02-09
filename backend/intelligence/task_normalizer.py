"""
Task Normalizer - Map Customer Task Names to Ontology Tasks

Handles real-world challenge: customers have task names that don't match canonical ontology.

Core Tier: Basic fuzzy matching (Levenshtein distance) + keyword extraction
Calibrated Tier: NLP semantic similarity (sentence-transformers)
Enterprise Tier: ML classification trained on customer data
"""

import logging
from typing import Optional, List, Dict, Tuple
from difflib import SequenceMatcher
import re
from datetime import datetime

from .models import TaskMappingSuggestion, UnconfirmedMatch

logger = logging.getLogger(__name__)


class TaskNormalizer:
    """
    Normalize customer task names to canonical ontology tasks

    Implements org-specific learning:
    1. Check cached mappings (task_mappings table)
    2. Fuzzy string matching (Levenshtein distance)
    3. Keyword extraction and category matching
    4. Return UnconfirmedMatch for low-confidence results
    """

    def __init__(
        self,
        ontology_tasks: List[Dict],
        db_connection=None,
        confidence_threshold: float = 0.7
    ):
        """
        Initialize TaskNormalizer

        Args:
            ontology_tasks: List of canonical tasks from ontology
            db_connection: Database connection for caching (optional)
            confidence_threshold: Minimum confidence for auto-mapping (default: 0.7)
        """
        self.ontology_tasks = ontology_tasks
        self.db_connection = db_connection
        self.confidence_threshold = confidence_threshold

        # Build indexes for fast lookups
        self._build_indexes()

        logger.info(f"TaskNormalizer initialized with {len(ontology_tasks)} ontology tasks")

    def _build_indexes(self):
        """Build lookup indexes"""
        self.task_by_name = {task['name'].lower(): task for task in self.ontology_tasks}

        self.task_by_id = {task['id']: task for task in self.ontology_tasks}

        # Build category index
        self.tasks_by_category = {}
        for task in self.ontology_tasks:
            category = task.get('category', 'Unknown')
            if category not in self.tasks_by_category:
                self.tasks_by_category[category] = []
            self.tasks_by_category[category].append(task)

        # Build keyword index (for keyword extraction matching)
        self.keyword_index = self._build_keyword_index()

    def _build_keyword_index(self) -> Dict[str, List[Dict]]:
        """Build index of keywords to tasks"""
        keyword_index = {}

        for task in self.ontology_tasks:
            # Extract keywords from task name
            keywords = self._extract_keywords(task['name'])

            for keyword in keywords:
                if keyword not in keyword_index:
                    keyword_index[keyword] = []
                keyword_index[keyword].append(task)

        return keyword_index

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

        # Split on non-alphanumeric and convert to lowercase
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter out stop words and short words
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords

    def normalize(
        self,
        customer_task_name: str,
        org_id: str,
        context: Optional[Dict] = None
    ) -> Tuple[Optional[str], Optional[TaskMappingSuggestion], Optional[UnconfirmedMatch]]:
        """
        Normalize customer task name to ontology task

        Args:
            customer_task_name: Task name from customer's timeline
            org_id: Organization ID (for cached mappings)
            context: Optional context (category hint, etc.)

        Returns:
            Tuple of (ontology_task_id, suggestion, unconfirmed_match)
            - If high confidence: (task_id, suggestion, None)
            - If low confidence: (None, None, unconfirmed_match)
        """
        # 1. Check org-specific mapping cache
        cached_mapping = self._get_cached_mapping(org_id, customer_task_name)
        if cached_mapping:
            logger.debug(f"Using cached mapping: {customer_task_name} -> {cached_mapping}")
            ontology_task = self.task_by_id.get(cached_mapping)
            if ontology_task:
                suggestion = TaskMappingSuggestion(
                    ontology_task_id=ontology_task['id'],
                    ontology_task_name=ontology_task['name'],
                    ontology_category=ontology_task['category'],
                    confidence=1.0,
                    match_method="cached",
                    match_score=1.0,
                    explanation="Previously confirmed mapping"
                )
                return (cached_mapping, suggestion, None)

        # 2. Try exact match
        exact_match = self.task_by_name.get(customer_task_name.lower())
        if exact_match:
            logger.debug(f"Exact match found: {customer_task_name}")
            suggestion = TaskMappingSuggestion(
                ontology_task_id=exact_match['id'],
                ontology_task_name=exact_match['name'],
                ontology_category=exact_match['category'],
                confidence=1.0,
                match_method="exact",
                match_score=1.0,
                explanation="Exact name match"
            )
            # Cache this mapping for future use
            self._save_mapping(org_id, customer_task_name, exact_match['id'], confidence=1.0, confirmed=True)
            return (exact_match['id'], suggestion, None)

        # 3. Try fuzzy matching
        fuzzy_suggestions = self._fuzzy_match_all(customer_task_name, category=context.get('category') if context else None)

        if not fuzzy_suggestions:
            # No matches found
            logger.warning(f"No matches found for: {customer_task_name}")
            return (None, None, UnconfirmedMatch(
                customer_task_name=customer_task_name,
                suggestions=[],
                needs_review=True,
                reason="No similar tasks found in ontology"
            ))

        # Check if best match exceeds confidence threshold
        best_match = fuzzy_suggestions[0]

        if best_match.confidence >= self.confidence_threshold:
            # High confidence, auto-map
            logger.info(f"High confidence match: {customer_task_name} -> {best_match.ontology_task_name} ({best_match.confidence:.2f})")
            # Save to cache (not confirmed yet)
            self._save_mapping(org_id, customer_task_name, best_match.ontology_task_id, confidence=best_match.confidence, confirmed=False)
            return (best_match.ontology_task_id, best_match, None)
        else:
            # Low confidence, return for user review
            logger.info(f"Low confidence matches for: {customer_task_name} (best: {best_match.confidence:.2f})")
            return (None, None, UnconfirmedMatch(
                customer_task_name=customer_task_name,
                suggestions=fuzzy_suggestions[:3],  # Top 3 suggestions
                needs_review=True,
                reason=f"Best match confidence {best_match.confidence:.2f} below threshold {self.confidence_threshold}"
            ))

    def _fuzzy_match_all(
        self,
        customer_task_name: str,
        category: Optional[str] = None,
        top_n: int = 5
    ) -> List[TaskMappingSuggestion]:
        """
        Find all fuzzy matches and return top N

        Args:
            customer_task_name: Customer task name
            category: Optional category hint
            top_n: Number of top matches to return

        Returns:
            List of TaskMappingSuggestion sorted by confidence
        """
        # Determine search space
        search_tasks = self.tasks_by_category.get(category, []) if category else self.ontology_tasks

        matches = []

        for ontology_task in search_tasks:
            # Calculate similarity score
            score = SequenceMatcher(
                None,
                customer_task_name.lower(),
                ontology_task['name'].lower()
            ).ratio()

            # Also check keyword overlap
            customer_keywords = set(self._extract_keywords(customer_task_name))
            ontology_keywords = set(self._extract_keywords(ontology_task['name']))

            if customer_keywords and ontology_keywords:
                keyword_overlap = len(customer_keywords & ontology_keywords) / len(customer_keywords | ontology_keywords)
            else:
                keyword_overlap = 0.0

            # Combined score (70% string similarity, 30% keyword overlap)
            combined_score = (score * 0.7) + (keyword_overlap * 0.3)

            if combined_score > 0.3:  # Minimum threshold to consider
                matches.append(TaskMappingSuggestion(
                    ontology_task_id=ontology_task['id'],
                    ontology_task_name=ontology_task['name'],
                    ontology_category=ontology_task['category'],
                    confidence=combined_score,
                    match_method="fuzzy",
                    match_score=score,
                    explanation=f"String similarity: {score:.2f}, Keyword overlap: {keyword_overlap:.2f}"
                ))

        # Sort by confidence descending
        matches.sort(key=lambda x: x.confidence, reverse=True)

        return matches[:top_n]

    def _get_cached_mapping(self, org_id: str, customer_task_name: str) -> Optional[str]:
        """Get cached mapping from database"""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT ontology_task_id FROM task_mappings
                WHERE org_id = ? AND customer_task_name = ?
                ORDER BY confirmed_by_user DESC, confidence DESC
                LIMIT 1
            """, (org_id, customer_task_name))

            row = cursor.fetchone()
            return row['ontology_task_id'] if row else None

        except Exception as e:
            logger.error(f"Error retrieving cached mapping: {e}")
            return None

    def _save_mapping(
        self,
        org_id: str,
        customer_task_name: str,
        ontology_task_id: str,
        confidence: float,
        confirmed: bool = False
    ):
        """Save mapping to database cache"""
        if not self.db_connection:
            return

        try:
            ontology_task = self.task_by_id.get(ontology_task_id)
            if not ontology_task:
                return

            cursor = self.db_connection.cursor()

            # Generate mapping ID
            import secrets
            mapping_id = f"map_{secrets.token_urlsafe(12)}"

            cursor.execute("""
                INSERT OR REPLACE INTO task_mappings
                (mapping_id, org_id, customer_task_name, ontology_task_id, ontology_task_name,
                 confidence, confirmed_by_user, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mapping_id,
                org_id,
                customer_task_name,
                ontology_task_id,
                ontology_task['name'],
                confidence,
                confirmed,
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat()
            ))

            self.db_connection.commit()
            logger.debug(f"Saved mapping: {customer_task_name} -> {ontology_task['name']} (confirmed: {confirmed})")

        except Exception as e:
            logger.error(f"Error saving mapping: {e}")

    def confirm_mapping(
        self,
        org_id: str,
        customer_task_name: str,
        ontology_task_id: str
    ) -> bool:
        """
        Confirm a mapping (user reviewed and approved)

        Args:
            org_id: Organization ID
            customer_task_name: Customer task name
            ontology_task_id: Ontology task ID

        Returns:
            bool: Success
        """
        if not self.db_connection:
            return False

        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE task_mappings
                SET confirmed_by_user = TRUE,
                    confidence = 1.0,
                    updated_at = ?
                WHERE org_id = ? AND customer_task_name = ? AND ontology_task_id = ?
            """, (datetime.utcnow().isoformat(), org_id, customer_task_name, ontology_task_id))

            self.db_connection.commit()
            logger.info(f"Confirmed mapping: {customer_task_name} -> {ontology_task_id}")
            return True

        except Exception as e:
            logger.error(f"Error confirming mapping: {e}")
            return False
