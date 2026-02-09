"""
Metadata Inferrer - Extract Missing Metadata from Timeline Content

Handles real-world challenge: timelines often don't explicitly specify phase,
therapeutic area, or study location.

Multi-Level Strategy:
1. Portal project profiles (proactive)
2. MS Project custom fields (user-defined)
3. Intelligent inference (automatic) - THIS MODULE
4. User confirmation modal (interactive)
"""

import logging
import re
from typing import Optional, List, Dict, Tuple
from collections import Counter

from .models import MetadataInference, MetadataConfirmationRequired

logger = logging.getLogger(__name__)


class MetadataInferrer:
    """
    Infer missing metadata from timeline content

    Methods:
    - infer_phase: Detect study phase from patterns
    - infer_therapeutic_area: Extract from task descriptions
    - infer_countries: Parse from authority names and task IDs
    """

    def __init__(self):
        """Initialize MetadataInferrer with pattern databases"""
        self._load_patterns()
        logger.info("MetadataInferrer initialized")

    def _load_patterns(self):
        """Load pattern databases for inference"""

        # Phase detection patterns
        self.phase_patterns = {
            "Phase I": [
                r"phase\s*i\b",
                r"phase\s*1\b",
                r"first\s*in\s*human",
                r"fih\b",
                r"safety\s*study",
                r"dose\s*escalation"
            ],
            "Phase II": [
                r"phase\s*ii\b",
                r"phase\s*2\b",
                r"proof\s*of\s*concept",
                r"poc\b",
                r"dose\s*finding"
            ],
            "Phase III": [
                r"phase\s*iii\b",
                r"phase\s*3\b",
                r"pivotal\s*trial",
                r"confirmatory\s*trial",
                r"registration\s*trial"
            ],
            "Phase IV": [
                r"phase\s*iv\b",
                r"phase\s*4\b",
                r"post\s*market",
                r"post-market",
                r"postmarket",
                r"observational\s*study"
            ]
        }

        # Therapeutic area keyword patterns
        self.therapeutic_area_keywords = {
            "Oncology": [
                "tumor", "cancer", "oncology", "chemotherapy", "radiation",
                "metastatic", "carcinoma", "leukemia", "lymphoma", "melanoma",
                "breast cancer", "lung cancer", "immunotherapy", "targeted therapy"
            ],
            "Infectious Disease": [
                "hiv", "aids", "antiretroviral", "viral load", "cd4",
                "hepatitis", "tuberculosis", "tb", "malaria", "infection",
                "antibacterial", "antiviral", "vaccine", "covid"
            ],
            "Cardiovascular": [
                "cardiovascular", "cardiac", "heart", "hypertension", "blood pressure",
                "cholesterol", "lipid", "statin", "arrhythmia", "ecg", "echo",
                "myocardial", "coronary", "stroke"
            ],
            "Neurology": [
                "neurology", "neurological", "alzheimer", "parkinson", "dementia",
                "epilepsy", "seizure", "migraine", "multiple sclerosis", "ms",
                "cognitive", "neuropathy", "brain", "neurodegeneration"
            ],
            "Diabetes": [
                "diabetes", "diabetic", "glucose", "insulin", "hba1c",
                "glycemic", "hyperglycemia", "hypoglycemia", "metabolic"
            ],
            "Rare Disease": [
                "rare disease", "orphan drug", "genetic disorder",
                "hemophilia", "cystic fibrosis", "sickle cell"
            ],
            "Respiratory": [
                "asthma", "copd", "respiratory", "pulmonary", "lung function",
                "fev1", "bronchodilator", "inhaler"
            ]
        }

        # Country code patterns (regulatory authorities)
        self.authority_country_map = {
            "FDA": "US",
            "EMA": "EU",
            "MHRA": "GB",
            "TGA": "AU",
            "NMPA": "CN",
            "PMDA": "JP",
            "DCGI": "IN",
            "PPB": "KE",
            "TMDA": "TZ",
            "MCAZ": "ZW",
            "SAHPRA": "ZA",
            "COFEPRIS": "MX",
            "ANVISA": "BR",
            "Health Canada": "CA",
            "NREC": "BD",
            "NDA": "UG",
            "PBSL": "SL",
            "INS": "PE",
            "ThaiFDA": "TH",
            "MOH": "VN"
        }

    def infer_metadata(
        self,
        timeline: Dict,
        confidence_threshold: float = 0.7
    ) -> Dict:
        """
        Infer all metadata from timeline

        Args:
            timeline: Timeline data with tasks
            confidence_threshold: Minimum confidence to accept inference

        Returns:
            dict with phase, therapeutic_area, countries, needs_confirmation
        """
        phase_inference = self.infer_phase(timeline)
        therapeutic_area_inference = self.infer_therapeutic_area(timeline)
        countries_inferences = self.infer_countries(timeline)

        # Check if any inference has low confidence
        needs_confirmation = (
            (phase_inference and phase_inference.confidence < confidence_threshold) or
            (therapeutic_area_inference and therapeutic_area_inference.confidence < confidence_threshold) or
            (countries_inferences and any(c.confidence < confidence_threshold for c in countries_inferences))
        )

        if needs_confirmation:
            return {
                "phase": phase_inference,
                "therapeutic_area": therapeutic_area_inference,
                "primary_country": countries_inferences[0] if countries_inferences else None,
                "additional_countries": countries_inferences[1:] if len(countries_inferences) > 1 else None,
                "needs_confirmation": True
            }
        else:
            return {
                "phase": phase_inference.inferred_value if phase_inference else None,
                "therapeutic_area": therapeutic_area_inference.inferred_value if therapeutic_area_inference else None,
                "primary_country": countries_inferences[0].inferred_value if countries_inferences else None,
                "additional_countries": [c.inferred_value for c in countries_inferences[1:]] if len(countries_inferences) > 1 else None,
                "needs_confirmation": False
            }

    def infer_phase(self, timeline: Dict) -> Optional[MetadataInference]:
        """
        Infer study phase from timeline content

        Strategy:
        1. Pattern matching in study name and task names
        2. Task count heuristics (Phase I = 20-40 tasks, Phase III = 100+)
        3. Presence of phase-specific tasks
        """
        study_name = timeline.get('study_name', '').lower()
        tasks = timeline.get('tasks', [])

        # Collect all text for pattern matching (filter out None tasks)
        all_text = study_name + " " + " ".join([
            task.get('name', '').lower() for task in tasks if task is not None
        ])

        # Pattern matching
        phase_scores = {}
        evidence = []

        for phase, patterns in self.phase_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, all_text, re.IGNORECASE))
                if matches > 0:
                    score += matches
                    evidence.append(f"Found '{pattern}' {matches} time(s)")

            if score > 0:
                phase_scores[phase] = score

        # Task count heuristics (exclude None tasks)
        task_count = len([t for t in tasks if t is not None])
        if task_count > 0:
            if 20 <= task_count <= 40:
                phase_scores["Phase I"] = phase_scores.get("Phase I", 0) + 2
                evidence.append(f"Task count ({task_count}) suggests Phase I (20-40 tasks typical)")
            elif 40 < task_count <= 80:
                phase_scores["Phase II"] = phase_scores.get("Phase II", 0) + 2
                evidence.append(f"Task count ({task_count}) suggests Phase II (40-80 tasks typical)")
            elif task_count > 100:
                phase_scores["Phase III"] = phase_scores.get("Phase III", 0) + 3
                evidence.append(f"Task count ({task_count}) suggests Phase III (100+ tasks typical)")

        if not phase_scores:
            logger.debug("No phase indicators found")
            return None

        # Get highest scoring phase
        best_phase = max(phase_scores.items(), key=lambda x: x[1])
        phase = best_phase[0]
        raw_score = best_phase[1]

        # Calculate confidence (normalize score)
        max_possible_score = 10  # Rough estimate
        confidence = min(raw_score / max_possible_score, 1.0)

        logger.info(f"Inferred phase: {phase} (confidence: {confidence:.2f})")

        return MetadataInference(
            field_name="phase",
            inferred_value=phase,
            confidence=confidence,
            evidence=evidence[:5],  # Top 5 pieces of evidence
            inference_method="pattern_matching_heuristics"
        )

    def infer_therapeutic_area(self, timeline: Dict) -> Optional[MetadataInference]:
        """
        Infer therapeutic area from task descriptions

        Strategy:
        - Keyword extraction from task names and descriptions
        - Score each therapeutic area by keyword matches
        """
        tasks = timeline.get('tasks', [])
        study_name = timeline.get('study_name', '').lower()

        # Collect all text (filter out None tasks)
        all_text = study_name + " " + " ".join([
            (task.get('name', '') + " " + task.get('description', '')).lower()
            for task in tasks if task is not None
        ])

        # Score therapeutic areas
        area_scores = {}
        evidence = {}

        for area, keywords in self.therapeutic_area_keywords.items():
            score = 0
            area_evidence = []

            for keyword in keywords:
                keyword_lower = keyword.lower()
                count = all_text.count(keyword_lower)
                if count > 0:
                    score += count
                    area_evidence.append(f"Found '{keyword}' {count} time(s)")

            if score > 0:
                area_scores[area] = score
                evidence[area] = area_evidence

        if not area_scores:
            logger.debug("No therapeutic area indicators found")
            return None

        # Get highest scoring area
        best_area = max(area_scores.items(), key=lambda x: x[1])
        area = best_area[0]
        raw_score = best_area[1]

        # Calculate confidence (normalize by task count, exclude None tasks)
        task_count = max(len([t for t in tasks if t is not None]), 1)
        confidence = min(raw_score / (task_count * 2), 1.0)

        logger.info(f"Inferred therapeutic area: {area} (confidence: {confidence:.2f})")

        return MetadataInference(
            field_name="therapeutic_area",
            inferred_value=area,
            confidence=confidence,
            evidence=evidence[area][:5],  # Top 5 pieces of evidence
            inference_method="keyword_extraction"
        )

    def infer_countries(self, timeline: Dict) -> List[MetadataInference]:
        """
        Infer countries from authority names and task IDs

        Strategy:
        1. Parse regulatory authority names
        2. Regex patterns in task IDs (e.g., "ZW-", "KE-")
        3. Country names in task names
        """
        tasks = timeline.get('tasks', [])

        country_mentions = Counter()
        evidence_by_country = {}

        # Filter out None tasks
        for task in tasks:
            if task is None:
                continue
            task_name = task.get('name', '')
            task_id = task.get('id', '')
            authority = task.get('authority', '')

            # Check authority mapping
            for auth_name, country_code in self.authority_country_map.items():
                if auth_name.lower() in task_name.lower() or auth_name.lower() in authority.lower():
                    country_mentions[country_code] += 1
                    if country_code not in evidence_by_country:
                        evidence_by_country[country_code] = []
                    evidence_by_country[country_code].append(f"Found authority '{auth_name}' in task: {task_name[:50]}")

            # Check task ID patterns (e.g., "KE-PPB-001")
            country_pattern = r'\b([A-Z]{2})-'
            matches = re.findall(country_pattern, task_id)
            for country_code in matches:
                if len(country_code) == 2:  # ISO 2-letter code
                    country_mentions[country_code] += 1
                    if country_code not in evidence_by_country:
                        evidence_by_country[country_code] = []
                    evidence_by_country[country_code].append(f"Found country code '{country_code}' in task ID: {task_id}")

        if not country_mentions:
            logger.debug("No country indicators found")
            return []

        # Convert to MetadataInference objects (exclude None tasks)
        inferences = []
        total_tasks = max(len([t for t in tasks if t is not None]), 1)

        for country_code, count in country_mentions.most_common(5):  # Top 5 countries
            confidence = min(count / total_tasks, 1.0)

            inferences.append(MetadataInference(
                field_name="country" if len(inferences) == 0 else "additional_country",
                inferred_value=country_code,
                confidence=confidence,
                evidence=evidence_by_country.get(country_code, [])[:3],  # Top 3 pieces of evidence
                inference_method="authority_parsing_regex"
            ))

        logger.info(f"Inferred {len(inferences)} countries: {[i.inferred_value for i in inferences]}")

        return inferences
