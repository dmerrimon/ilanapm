"""
Template Generator Service

Generates country-specific clinical trial timeline templates by combining:
- Country-specific regulatory workflows (23 countries)
- Canonical task ontology with country variations
- Emmes industry-standard timelines (study startup, closeout)
"""

from config import load_config
from models.timeline import Timeline, Task, Dependency
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TemplateGenerator:
    """Generates country-specific timeline templates"""

    def __init__(self):
        """Initialize template generator with config data"""
        config = load_config()
        self.tasks = config.get('task_ontology', [])
        self.workflows = config.get('regulatory_workflows', [])
        self.authorities = config.get('authorities', [])

        logger.info(f"TemplateGenerator initialized: {len(self.tasks)} tasks, {len(self.workflows)} workflows")

    def generate_template(
        self,
        country_code: str,
        study_phase: str,
        therapeutic_area: str,
        include_optional: bool = True
    ) -> Timeline:
        """
        Generate country-specific timeline template

        Args:
            country_code: ISO country code (e.g., "US", "KE", "VN")
            study_phase: Study phase ("Phase I", "Phase II", "Phase III", "Phase IV")
            therapeutic_area: Therapeutic area (e.g., "Oncology", "Infectious Disease")
            include_optional: Include optional tasks

        Returns:
            Timeline object with country-specific tasks and dependencies
            All 92 tasks from ontology are included based on category filters

        Example:
            >>> generator = TemplateGenerator()
            >>> timeline = generator.generate_template("KE", "Phase III", "Infectious Disease")
            >>> len(timeline.tasks)  # Returns task count including Kenya 3-layer workflow
        """
        # Get country workflow
        workflow = self._get_workflow(country_code)
        logger.info(f"Generating template for {workflow['country_name']} - {study_phase} - {therapeutic_area}")

        # Build regulatory tasks (country-specific)
        regulatory_tasks = self._build_regulatory_tasks(workflow, study_phase, therapeutic_area)

        # Build operational tasks from ontology (92 tasks)
        operational_tasks = self._build_operational_tasks(
            study_phase,
            therapeutic_area,
            include_optional,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            )
        )

        # Build industry-standard milestone tasks (fills gaps in ontology)
        # These provide key milestones for Protocol Development, Data Entry, Data Cleaning
        # which are missing from the ontology
        industry_tasks = self._build_industry_standard_tasks(
            study_phase,
            therapeutic_area,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            )
        )

        # Combine all tasks
        all_tasks = regulatory_tasks + operational_tasks + industry_tasks
        logger.info(f"Generated {len(all_tasks)} tasks: {len(regulatory_tasks)} regulatory, " +
                   f"{len(operational_tasks)} operational (from ontology), " +
                   f"{len(industry_tasks)} industry-standard milestones")

        # Organize tasks with category dividers
        organized_tasks = self._organize_tasks_with_categories(all_tasks, workflow)
        logger.info(f"Organized {len(organized_tasks)} tasks (including category dividers)")

        # Build dependencies
        dependencies = self._build_dependencies(all_tasks, workflow)

        # Create timeline
        timeline = Timeline(
            study_name=f"{workflow['country_name']} {study_phase} - {therapeutic_area}",
            phase=study_phase,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            therapeutic_area=therapeutic_area,
            tasks=organized_tasks,
            dependencies=dependencies
        )

        return timeline

    def _organize_tasks_with_categories(self, tasks: List[Task], workflow: Dict) -> List[Task]:
        """
        Organize tasks with category dividers (summary tasks)

        Groups tasks by category and creates summary tasks (dividers) for each category.
        Returns tasks in organized order with summary tasks followed by their child tasks.

        Category order: Regulatory → Operational → Site → Data → Pharmacy → Laboratory → Safety → Documents → Closeout
        """
        from collections import defaultdict

        # Group tasks by category
        tasks_by_category = defaultdict(list)
        for task in tasks:
            # Normalize category name (handle both enum and string values)
            category = task.category.value if hasattr(task.category, 'value') else str(task.category)
            tasks_by_category[category].append(task)

        # Define category order and labels
        # Order follows logical clinical trial workflow: Regulatory → Operational → Data → Site → Closeout
        category_order = [
            ('Regulatory', '═══ REGULATORY TASKS ═══'),
            ('Operational', '═══ OPERATIONAL TASKS ═══'),
            ('Data', '═══ DATA MANAGEMENT TASKS ═══'),
            ('Site', '═══ SITE MANAGEMENT TASKS ═══'),
            ('Pharmacy', '═══ PHARMACY TASKS ═══'),
            ('Laboratory', '═══ LABORATORY TASKS ═══'),
            ('Safety', '═══ SAFETY OVERSIGHT TASKS ═══'),
            ('Documents', '═══ DOCUMENT MANAGEMENT TASKS ═══'),
            ('Closeout', '═══ STUDY CLOSEOUT TASKS ═══')
        ]

        organized_tasks = []

        for category_key, category_label in category_order:
            category_tasks = tasks_by_category.get(category_key, [])

            if not category_tasks:
                continue  # Skip categories with no tasks

            # Sort tasks within category by workflow sequence
            category_tasks = self._sort_tasks_by_workflow(category_tasks, category_key)

            # Create summary task (category divider)
            summary_task = Task(
                id=f"SUMMARY-{category_key}",
                name=category_label,
                duration_days=0,  # Summary tasks have zero duration (calculated from children)
                category=category_tasks[0].category,  # Use same category as children
                phase=category_tasks[0].phase,
                authority=category_tasks[0].authority,
                country=category_tasks[0].country,
                therapeutic_area=category_tasks[0].therapeutic_area,
                is_mandatory=True,
                is_summary=True,
                outline_level=1  # Level 1 = Summary/parent task
            )
            organized_tasks.append(summary_task)

            # Add child tasks (set outline_level=2 for indentation)
            for task in category_tasks:
                task.outline_level = 2  # Level 2 = Child task (indented under summary)
                organized_tasks.append(task)

        logger.info(f"Created {len([t for t in organized_tasks if t.is_summary])} category dividers")
        return organized_tasks

    def _sort_tasks_by_workflow(self, tasks: List[Task], category: str) -> List[Task]:
        """
        Sort tasks within a category by their logical workflow sequence

        Returns tasks sorted in the order they typically occur in a clinical trial
        """

        def get_task_priority(task: Task) -> tuple:
            """
            Get priority for sorting tasks within category
            Returns (priority_group, task_id) where lower numbers come first
            """
            task_id = task.id
            task_name_lower = task.name.lower()

            # Define workflow order for each category
            if category == 'Data':
                # Data Management workflow order
                if 'data collection forms first draft' in task_name_lower or task_id == 'IND-010':
                    return (1, task_id)
                elif 'data collection forms' in task_name_lower and 'first draft' not in task_name_lower:
                    return (2, task_id)  # Final DCF (IND-002)
                elif 'ecrfinstructions' in task_name_lower or 'mop appendix' in task_name_lower:
                    return (3, task_id)
                elif 'mop first draft' in task_name_lower or task_id == 'IND-012':
                    return (4, task_id)
                elif 'manual of procedures available' in task_name_lower or 'mop v1.0' in task_name_lower or task_id == 'IND-003':
                    return (5, task_id)
                elif 'draft statistical analysis plan' in task_name_lower or 'draft sap' in task_name_lower:
                    return (6, task_id)
                elif 'interim sap' in task_name_lower or task_id == 'IND-022':
                    return (7, task_id)
                elif 'data system configuration' in task_name_lower or task_id == 'IND-004':
                    return (8, task_id)
                elif 'ecrfs programmed' in task_name_lower or 'direct data entry' in task_name_lower:
                    return (9, task_id)
                elif 'database deployed' in task_name_lower:
                    return (10, task_id)
                elif 'sdcc database training' in task_name_lower:
                    return (11, task_id)
                elif 'data management training completed' in task_name_lower:
                    return (12, task_id)
                elif 'site pi database access' in task_name_lower:
                    return (13, task_id)
                elif 'paper dcfs' in task_name_lower or 'paper crfs' in task_name_lower:
                    return (14, task_id)
                elif 'data system opens' in task_name_lower or task_id == 'IND-018':
                    return (15, task_id)
                elif 'dsmb' in task_name_lower and 'charter' in task_name_lower:
                    return (16, task_id)
                elif 'dsmb' in task_name_lower and 'report shell' in task_name_lower:
                    return (17, task_id)
                elif 'barcode labels' in task_name_lower:
                    return (18, task_id)
                elif 'randomization materials' in task_name_lower:
                    return (19, task_id)
                elif 'programmatic queries' in task_name_lower:
                    return (20, task_id)
                elif 'website initial' in task_name_lower:
                    return (21, task_id)
                elif 'web report programming' in task_name_lower:
                    return (22, task_id)
                elif 'statistical analysis' in task_name_lower and 'plan' not in task_name_lower:
                    return (23, task_id)
                else:
                    return (99, task_id)

            elif category == 'Closeout':
                # Study Closeout workflow order
                if 'clinical data entry' in task_name_lower or task_id == 'IND-105':
                    return (1, task_id)
                elif 'data cleaning' in task_name_lower and 'resolution' not in task_name_lower:
                    return (2, task_id)
                elif 'serious adverse event reconciliation' in task_name_lower or 'sae reconciliation' in task_name_lower:
                    return (3, task_id)
                elif 'final monitoring visit' in task_name_lower:
                    return (4, task_id)
                elif 'resolution of data management queries' in task_name_lower or 'resolution of all data' in task_name_lower:
                    return (5, task_id)
                elif 'clinical database lock' in task_name_lower and 'laboratory' not in task_name_lower:
                    return (6, task_id)
                elif 'laboratory assay completion' in task_name_lower or 'assay completion and transfer' in task_name_lower:
                    return (7, task_id)
                elif 'qc of laboratory data' in task_name_lower:
                    return (8, task_id)
                elif 'resolution of laboratory queries' in task_name_lower:
                    return (9, task_id)
                elif 'laboratory database lock' in task_name_lower:
                    return (10, task_id)
                elif 'pharmacovigilance' in task_name_lower and 'sae narratives' in task_name_lower:
                    return (11, task_id)
                elif 'preparation of draft csr' in task_name_lower or (task_id == 'REG-020' and 'draft csr' in task_name_lower):
                    return (12, task_id)
                elif 'distribute draft csr to pi' in task_name_lower and 'sponsor' not in task_name_lower:
                    return (13, task_id)
                elif 'pi reviews and completes csr' in task_name_lower:
                    return (14, task_id)
                elif 'incorporate pi text and comments' in task_name_lower:
                    return (15, task_id)
                elif 'distribute draft csr to sponsor and pi' in task_name_lower or 'distribute draft csr to sponsor' in task_name_lower:
                    return (16, task_id)
                elif 'sponsor reviews draft csr' in task_name_lower:
                    return (17, task_id)
                elif 'incorporate sponsor comments' in task_name_lower:
                    return (18, task_id)
                elif 'receive sponsor and pi approval' in task_name_lower or 'approval to finalize csr' in task_name_lower:
                    return (19, task_id)
                elif 'prepare approved csr' in task_name_lower:
                    return (20, task_id)
                elif 'lead pi signs csr' in task_name_lower or 'pi signs csr signature page' in task_name_lower:
                    return (21, task_id)
                elif 'distribute approved csr' in task_name_lower:
                    return (22, task_id)
                elif 'final csr submission' in task_name_lower or 'submit final csr' in task_name_lower:
                    return (23, task_id)
                elif 'site closeout visits' in task_name_lower:
                    return (24, task_id)
                elif 'study archival' in task_name_lower:
                    return (25, task_id)
                elif 'final regulatory submissions' in task_name_lower:
                    return (26, task_id)
                # Remove duplicate "Database Lock" entries - already have Clinical and Lab DB locks above
                elif task_name_lower == 'database lock':
                    return (999, task_id)  # Push generic "Database Lock" to end (will be filtered)
                else:
                    return (99, task_id)

            elif category == 'Site':
                # Site Management workflow order
                if 'site identification' in task_name_lower or 'site feasibility' in task_name_lower:
                    return (1, task_id)
                elif 'site assessment visit' in task_name_lower:
                    return (2, task_id)
                elif 'site initiation visit' in task_name_lower:
                    return (3, task_id)
                elif 'essential documents' in task_name_lower:
                    return (4, task_id)
                elif 'investigator brochure' in task_name_lower:
                    return (5, task_id)
                elif 'psrl' in task_name_lower:
                    return (6, task_id)
                elif 'training' in task_name_lower and 'pi attestation' not in task_name_lower:
                    return (7, task_id)
                elif 'pi attestation' in task_name_lower:
                    return (8, task_id)
                elif 'site activation' in task_name_lower:
                    return (9, task_id)
                elif 'first patient in' in task_name_lower or 'fpi' in task_name_lower:
                    return (10, task_id)
                elif 'patient enrollment' in task_name_lower:
                    return (11, task_id)
                elif 'last patient last visit' in task_name_lower or 'lplv' in task_name_lower:
                    return (12, task_id)
                elif 'site closeout' in task_name_lower:
                    return (13, task_id)
                else:
                    return (99, task_id)

            elif category == 'Regulatory':
                # Regulatory workflow order (approvals first, then ongoing compliance)
                # Country-specific approvals first (EC → PPB → NACOSTI, etc.)
                if 'irb approval' in task_name_lower or 'ec approval' in task_name_lower or 'ethics committee approval' in task_name_lower:
                    return (1, task_id)
                elif 'pharmacy and poisons board' in task_name_lower or 'ppb approval' in task_name_lower:
                    return (2, task_id)
                elif 'nacosti' in task_name_lower:
                    return (3, task_id)
                elif 'ind submission' in task_name_lower:
                    return (4, task_id)
                elif 'clinicaltrials.gov' in task_name_lower or 'nct' in task_name_lower:
                    return (5, task_id)
                elif 'protocol amendment' in task_name_lower:
                    return (6, task_id)
                elif 'irb continuing review' in task_name_lower:
                    return (7, task_id)
                elif 'annual safety report' in task_name_lower:
                    return (8, task_id)
                else:
                    return (99, task_id)

            elif category == 'Operational':
                # Operational workflow order
                if 'protocol development' in task_name_lower:
                    return (1, task_id)
                elif 'site identification' in task_name_lower:
                    return (2, task_id)
                elif 'site contract' in task_name_lower:
                    return (3, task_id)
                else:
                    return (99, task_id)

            elif category == 'Pharmacy':
                # Pharmacy workflow order
                if 'pharmacist list' in task_name_lower or 'blinded' in task_name_lower or 'unblinded' in task_name_lower:
                    return (1, task_id)
                elif 'study product available' in task_name_lower:
                    return (2, task_id)
                elif 'randomization process' in task_name_lower or 'unblinding table' in task_name_lower:
                    return (3, task_id)
                else:
                    return (99, task_id)

            elif category == 'Laboratory':
                # Laboratory workflow order
                if 'cap' in task_name_lower or 'specimen table' in task_name_lower or 'assay table' in task_name_lower:
                    return (1, task_id)
                elif 'ldms' in task_name_lower or 'equipment tested' in task_name_lower:
                    return (2, task_id)
                elif 'lab readiness' in task_name_lower:
                    return (3, task_id)
                else:
                    return (99, task_id)

            elif category == 'Safety':
                # Safety workflow order
                if 'dsmb' in task_name_lower or 'smc' in task_name_lower:
                    if 'organizational meeting' in task_name_lower:
                        return (1, task_id)
                    elif 'charter' in task_name_lower:
                        return (2, task_id)
                    elif 'report shell' in task_name_lower:
                        return (3, task_id)
                return (99, task_id)

            elif category == 'Documents':
                # Documents workflow order
                if 'clinical trial agreement' in task_name_lower or 'cta' in task_name_lower or 'mou' in task_name_lower:
                    return (1, task_id)
                elif 'monitoring plan' in task_name_lower:
                    return (2, task_id)
                elif 'mta' in task_name_lower or 'dta' in task_name_lower or 'agreements in place' in task_name_lower:
                    return (3, task_id)
                else:
                    return (99, task_id)

            # Default: sort by task ID
            return (99, task_id)

        # Sort tasks by priority, then by ID for stable ordering
        sorted_tasks = sorted(tasks, key=get_task_priority)

        # Filter out duplicate entries
        if category == 'Closeout':
            filtered_tasks = []
            seen_names = set()
            has_clinical_db_lock = any('clinical database lock' in t.name.lower() for t in sorted_tasks)
            has_lab_db_lock = any('laboratory database lock' in t.name.lower() for t in sorted_tasks)

            for task in sorted_tasks:
                task_name_lower = task.name.lower()

                # Skip generic "Database Lock" if we have specific ones
                if task_name_lower == 'database lock' and (has_clinical_db_lock or has_lab_db_lock):
                    continue

                # Skip exact duplicates (keep first occurrence only)
                if task_name_lower in seen_names:
                    continue

                seen_names.add(task_name_lower)
                filtered_tasks.append(task)
            return filtered_tasks

        return sorted_tasks

    def _get_workflow(self, country_code: str) -> Dict:
        """Get regulatory workflow for a country"""
        for workflow in self.workflows:
            if workflow['country_code'] == country_code:
                return workflow

        # If not found, raise error with helpful message
        available_codes = [w['country_code'] for w in self.workflows]
        raise ValueError(
            f"No workflow found for country: {country_code}. " +
            f"Available countries: {', '.join(sorted(available_codes))}"
        )

    def _build_regulatory_tasks(
        self,
        workflow: Dict,
        phase: str,
        therapeutic_area: str
    ) -> List[Task]:
        """Build country-specific regulatory tasks"""
        tasks = []

        # Find regulatory tasks in ontology
        regulatory_task_defs = [t for t in self.tasks if t.get('category') == 'Regulatory']

        # Country-specific task exclusions
        country_code = workflow['country_code']
        workflow_type = workflow.get('workflow_type')
        us_only_tasks = ['REG-001', 'REG-011']  # IND/CTA and IND Submission are US-specific

        for task_def in regulatory_task_defs:
            task_id = task_def['id']

            # Check if task has applicable_countries field
            applicable_countries = task_def.get('applicable_countries', [])
            if applicable_countries and country_code not in applicable_countries:
                continue

            # Skip US-only tasks for non-US countries
            if country_code != 'US' and task_id in us_only_tasks:
                continue

            # Skip generic "Ministerial/Final Approval" for countries with specific multi-layer workflows
            # These countries have their own specific approval tasks (EC → PPB → NACOSTI, etc.)
            if task_id == 'REG-INT-003' and workflow_type in ['three_layer_sequential', 'four_layer_sequential']:
                continue

            # Skip if this is a country-specific task for a different country
            # Example: REG-US-xxx tasks should only appear in US templates
            if '-' in task_id and len(task_id.split('-')) >= 3:
                task_country = task_id.split('-')[1]
                if task_country != country_code and task_country != 'INT':
                    continue

            # Apply country-specific variation
            duration = self._get_country_duration(task_def, workflow, phase)

            # Skip if duration is None (task not applicable to this country)
            if duration is None:
                continue

            # Use task name as-is (don't append country name for generic tasks)
            task_name = task_def['name']

            task = Task(
                id=task_def['id'],
                name=task_name,
                duration_days=duration,
                category='Regulatory',
                phase=phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=task_def.get('is_mandatory', True)
            )
            tasks.append(task)

        # Add country-specific multi-layer approvals
        # Three-layer: e.g., Kenya EC → PPB → NACOSTI
        if workflow.get('workflow_type') == 'three_layer_sequential':
            tasks.extend(self._build_three_layer_tasks(workflow, phase, therapeutic_area))

        # Four-layer: e.g., Vietnam CEBRGL → ASTT → NECBR → Minister
        if workflow.get('workflow_type') == 'four_layer_sequential':
            tasks.extend(self._build_four_layer_tasks(workflow, phase, therapeutic_area))

        return tasks

    def _map_category(self, category: str) -> str:
        """Map ontology categories to TaskCategory enum values"""
        category_map = {
            'Planning': 'Operational',
            'Site Management': 'Site',
            'Data Management': 'Data',
            'Operational': 'Operational',
            'Regulatory': 'Regulatory',
            'Closeout': 'Closeout',
            'Data': 'Data',
            'Site': 'Site',
            'Safety': 'Safety',
            'Pharmacy': 'Pharmacy',
            'Laboratory': 'Laboratory',
            'Documents': 'Documents'
        }
        return category_map.get(category, 'Operational')

    def _map_authority(self, authority_code: str, country_code: str, country_name: str) -> str:
        """Map authority codes to RegulatoryAuthority enum values"""
        # Authority mapping based on country
        authority_map = {
            # Africa
            'MCAZ-ZW': 'MCAZ Zimbabwe',
            'PPB': 'PPB Kenya',
            'NACOSTI': 'PPB Kenya',  # Map NACOSTI to PPB Kenya (same regulatory framework)
            'LMHRA': 'LMHRA Liberia',
            'PMRA': 'MCAZ Malawi',
            'DPM': 'DPM Mali',
            'PBSL': 'PSLB Sierra Leone',
            'SAHPRA': 'SAHPRA South Africa',
            'TMDA': 'TFDA Tanzania',
            'NDA': 'NDA Uganda',
            'ACOREP': 'DGRDF DRC',
            'DNPM': 'DNPL Guinea',
            # Americas
            'FDA': 'FDA' if country_code == 'US' else 'FDA United States',
            'COFEPRIS': 'COFEPRIS Mexico',
            'INS': 'DIGEMID Peru',
            # Asia-Pacific
            'TGA': 'TGA Australia',
            'DGDA': 'BFDA Bangladesh',
            'NMPA': 'NMPA China',
            'DCGI': 'CDSCO India',
            'Thai FDA': 'FDA Thailand',
            'MOH': 'MOH Vietnam',
            'MOH_ASTT': 'MOH Vietnam',
            'CEBRGL': 'MOH Vietnam',
            'NECBR': 'MOH Vietnam',
            'Minister': 'MOH Vietnam',
            # Europe
            'MHRA': 'MHRA' if country_code == 'GB' else 'MHRA United Kingdom',
            # Ethics authorities
            'EC': 'FDA',  # Default to FDA for ethics committees
            'HREC': 'TGA Australia',
            'REB': 'Health Canada',
            'IRB': 'FDA'
        }

        mapped = authority_map.get(authority_code, authority_code)
        # If still just a code and not in the map, default to primary authority for the country
        if mapped == authority_code and authority_code not in ['FDA', 'EMA', 'MHRA', 'PMDA']:
            # Default to the country's primary regulatory authority
            country_authorities = {
                'KE': 'PPB Kenya',
                'US': 'FDA',
                'GB': 'MHRA United Kingdom',
                'AU': 'TGA Australia',
                'CA': 'Health Canada',
                'ZW': 'MCAZ Zimbabwe',
                'UG': 'NDA Uganda',
                'TZ': 'TFDA Tanzania',
                'ZA': 'SAHPRA South Africa',
                'SL': 'PSLB Sierra Leone',
                'ML': 'DPM Mali',
                'MW': 'MCAZ Malawi',
                'LR': 'LMHRA Liberia',
                'CD': 'DGRDF DRC',
                'GN': 'DNPL Guinea',
                'MX': 'COFEPRIS Mexico',
                'PE': 'DIGEMID Peru',
                'BD': 'BFDA Bangladesh',
                'CN': 'NMPA China',
                'IN': 'CDSCO India',
                'TH': 'FDA Thailand',
                'VN': 'MOH Vietnam'
            }
            return country_authorities.get(country_code, 'FDA')
        return mapped

    def _get_country_duration(self, task_def: Dict, workflow: Dict, phase: str) -> Optional[int]:
        """Get country-specific duration for a task"""
        country_code = workflow['country_code']

        # Check for country-specific variation
        country_variations = task_def.get('country_variations', {})
        if country_code in country_variations:
            return country_variations[country_code].get('duration_days', task_def['typical_duration_days'])

        # Use workflow authority review days for regulatory tasks
        if task_def.get('category') == 'Regulatory':
            return workflow['regulatory_authority'].get('review_days', task_def.get('typical_duration_days', 30))

        return task_def.get('typical_duration_days', 30)

    def _build_three_layer_tasks(
        self,
        workflow: Dict,
        phase: str,
        therapeutic_area: str
    ) -> List[Task]:
        """Build tasks for three-layer sequential workflows (e.g., Kenya: EC → PPB → NACOSTI)"""
        tasks = []

        # Layer 1: Ethics Committee (use specific authority name)
        ec_duration = workflow['ethics_authority'].get('review_days')
        if ec_duration is None:
            ec_duration = 30  # Default to 30 days if not specified

        tasks.append(Task(
            id=f"REG-{workflow['country_code']}-EC",
            name=f"IRB Approval - {workflow['country_name']}",
            duration_days=ec_duration,
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(
                workflow['ethics_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            country=workflow['country_code'],
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Layer 2: Primary Regulatory Authority (e.g., PPB in Kenya)
        tasks.append(Task(
            id=f"REG-{workflow['country_code']}-REG",
            name=f"{workflow['regulatory_authority']['name']} Approval - {workflow['country_name']}",
            duration_days=workflow['regulatory_authority'].get('review_days', 30),
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            country=workflow['country_code'],
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Layer 3: Additional authorities/bodies (e.g., NACOSTI in Kenya)
        additional_bodies = workflow.get('additional_bodies', workflow.get('additional_authorities', []))
        for auth in additional_bodies:
            tasks.append(Task(
                id=f"REG-{workflow['country_code']}-{auth['code']}",
                name=f"{auth['name']} Clearance - {workflow['country_name']}",
                duration_days=auth.get('review_days', 30),
                category='Regulatory',
                phase=phase,
                authority=self._map_authority(
                    auth['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ))

        return tasks

    def _build_four_layer_tasks(
        self,
        workflow: Dict,
        phase: str,
        therapeutic_area: str
    ) -> List[Task]:
        """Build tasks for four-layer sequential workflows (e.g., Vietnam: CEBRGL → ASTT → NECBR → Minister)"""
        tasks = []

        # Layer 1: Local/Institutional Ethics Committee (CEBRGL)
        ec_duration = workflow['ethics_authority'].get('review_days')
        if ec_duration is None:
            ec_duration = 30  # Default to 30 days if not specified

        tasks.append(Task(
            id=f"REG-{workflow['country_code']}-EC",
            name=f"IRB Approval - {workflow['country_name']}",
            duration_days=ec_duration,
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(
                workflow['ethics_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            country=workflow['country_code'],
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Layer 2: Regulatory Authority (ASTT in Vietnam)
        tasks.append(Task(
            id=f"REG-{workflow['country_code']}-REG",
            name=f"{workflow['regulatory_authority']['name']} Review - {workflow['country_name']}",
            duration_days=workflow['regulatory_authority'].get('review_days', 30),
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            country=workflow['country_code'],
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Layer 3 & 4: Additional bodies (NECBR, Minister)
        additional_bodies = workflow.get('additional_bodies', [])
        for auth in additional_bodies:
            tasks.append(Task(
                id=f"REG-{workflow['country_code']}-{auth['code']}",
                name=f"{auth['name']} - {workflow['country_name']}",
                duration_days=auth.get('review_days', 30),
                category='Regulatory',
                phase=phase,
                authority=self._map_authority(
                    auth['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ))

        return tasks

    def _build_operational_tasks(
        self,
        phase: str,
        therapeutic_area: str,
        include_optional: bool,
        authority: str = "FDA"
    ) -> List[Task]:
        """Build operational (non-regulatory) tasks"""
        tasks = []

        # Find operational tasks in ontology
        # Fixed: Use actual category names from task_ontology.yaml
        # Includes ALL non-regulatory categories (92 tasks total)
        operational_categories = ['Operational', 'Site', 'Data', 'Closeout',
                                 'Pharmacy', 'Laboratory', 'Documents', 'Safety']
        operational_task_defs = [
            t for t in self.tasks
            if t.get('category') in operational_categories
        ]

        for task_def in operational_task_defs:
            # Skip optional tasks if not included
            if not include_optional and not task_def.get('is_mandatory', False):
                continue

            task = Task(
                id=task_def['id'],
                name=task_def['name'],
                duration_days=task_def.get('typical_duration_days', 30),
                category=self._map_category(task_def.get('category', 'Operational')),
                phase=phase,
                authority=authority,
                therapeutic_area=therapeutic_area,
                is_mandatory=task_def.get('is_mandatory', False)
            )
            tasks.append(task)

        return tasks

    def _build_industry_standard_tasks(self, phase: str, therapeutic_area: str, authority: str = "FDA") -> List[Task]:
        """
        Build industry-standard timeline tasks

        Based on standard CRO timelines and CPM site activation checklists
        """
        industry_tasks = []

        # ===== STUDY STARTUP TASKS =====

        # Protocol Development (~6 months)
        industry_tasks.append(Task(
            id='IND-100',
            name='Protocol Development',
            duration_days=180,
            category='Operational',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Data Collection Forms (4 weeks after protocol)
        industry_tasks.append(Task(
            id='IND-101',
            name='Data Collection Forms Development',
            duration_days=28,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Manual of Procedures (2 weeks after protocol)
        industry_tasks.append(Task(
            id='IND-102',
            name='Manual of Procedures (MOP) v1.0',
            duration_days=14,
            category='Operational',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Data System Configuration (6 weeks after final forms)
        industry_tasks.append(Task(
            id='IND-103',
            name='Data System Configuration',
            duration_days=42,
            category='Data',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Site Training (before activation)
        industry_tasks.append(Task(
            id='IND-104',
            name='Site Training',
            duration_days=3,
            category='Site',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # ===== STUDY CLOSEOUT TASKS =====

        # Clinical Data Entry (4 days after LPLV)
        industry_tasks.append(Task(
            id='IND-105',
            name='Clinical Data Entry',
            duration_days=4,
            category='Closeout',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Data Cleaning (2 weeks after entry)
        industry_tasks.append(Task(
            id='IND-106',
            name='Data Cleaning',
            duration_days=14,
            category='Closeout',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Database Lock
        industry_tasks.append(Task(
            id='IND-107',
            name='Database Lock',
            duration_days=1,
            category='Closeout',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        # Clinical Study Report (8 weeks after database lock)
        industry_tasks.append(Task(
            id='IND-108',
            name='Clinical Study Report (CSR)',
            duration_days=56,
            category='Regulatory',
            phase=phase,
            authority=authority,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        ))

        return industry_tasks

    def _build_dependencies(self, tasks: List[Task], workflow: Dict) -> List[Dependency]:
        """Build dependencies between tasks"""
        dependencies = []
        task_map = {t.id: t for t in tasks}

        # ===== TASK ONTOLOGY PREREQUISITES =====
        # Convert task ontology prerequisites to MS Project dependencies
        # This reads the 'prerequisites' field from task_ontology.yaml and creates
        # predecessor relationships in MS Project
        for task_def in self.tasks:
            task_id = task_def['id']
            prerequisites = task_def.get('prerequisites', [])

            # Only create dependencies if both tasks exist in the generated template
            if task_id in task_map:
                for predecessor_id in prerequisites:
                    if predecessor_id in task_map:
                        dependencies.append(Dependency(
                            predecessor_id=predecessor_id,
                            successor_id=task_id,
                            type='finish-to-start',
                            lag_days=0
                        ))
                        logger.debug(f"Added ontology dependency: {predecessor_id} → {task_id}")

        logger.info(f"Created {len(dependencies)} dependencies from task ontology prerequisites")

        # ===== STUDY STARTUP DEPENDENCIES =====
        # Based on industry-standard CRO timelines and Emmes workflows
        startup_deps = [
            # CRITICAL: Protocol Development must complete BEFORE regulatory submissions
            # User requirement: "before we can submit to the various authorities and irbs
            # the protocol development must be completed and it must be reviewed and
            # approved by the sponsor/study leadership"
            ('IND-100', 'REG-001'),   # Protocol Development → IND/CTA Submission
            ('IND-100', 'REG-002'),   # Protocol Development → IRB/EC Approval

            # Protocol-dependent operational tasks
            ('IND-100', 'IND-101'),   # Protocol Development → Data Collection Forms
            ('IND-100', 'IND-102'),   # Protocol Development → MOP

            # Data management workflow
            ('IND-101', 'IND-103'),   # Data Collection Forms → Data System Configuration
            ('IND-103', 'DATA-016'),  # Data System Configuration → Database Deployed

            # Site preparation workflow
            ('DATA-016', 'IND-104'),  # Database Deployed → Site Training
            ('IND-104', 'SITE-001'),  # Site Training → Site Initiation Visit
            ('SITE-001', 'SITE-002'), # Site Initiation Visit → Site Activation
        ]

        # ===== STUDY EXECUTION DEPENDENCIES =====
        execution_deps = [
            ('SITE-002', 'SITE-003'), # Site Activation → First Patient In
            ('SITE-003', 'SITE-004'), # First Patient In → Patient Enrollment Period
            ('SITE-004', 'SITE-005'), # Patient Enrollment Period → Last Patient Last Visit (LPLV)
        ]

        # ===== STUDY CLOSEOUT DEPENDENCIES =====
        closeout_deps = [
            ('SITE-005', 'IND-105'),  # LPLV → Clinical Data Entry
            ('IND-105', 'IND-106'),   # Clinical Data Entry → Data Cleaning
            ('IND-106', 'IND-107'),   # Data Cleaning → Database Lock (industry-standard milestone)
            ('IND-107', 'DATA-001'),  # Database Lock milestone → Clinical Database Lock (ontology task)
            ('DATA-001', 'DATA-004'), # Clinical Database Lock → CSR Writing
            ('DATA-004', 'REG-031'),  # CSR Writing → Final Regulatory Submissions
        ]

        # Combine all industry-standard dependencies
        all_industry_deps = startup_deps + execution_deps + closeout_deps

        # Track existing dependency pairs to avoid duplicates
        existing_pairs = {(d.predecessor_id, d.successor_id) for d in dependencies}

        for predecessor_id, successor_id in all_industry_deps:
            if predecessor_id in task_map and successor_id in task_map:
                # Only add if this dependency pair doesn't already exist
                if (predecessor_id, successor_id) not in existing_pairs:
                    dependencies.append(Dependency(
                        predecessor_id=predecessor_id,
                        successor_id=successor_id,
                        type='finish-to-start',
                        lag_days=0
                    ))
                    existing_pairs.add((predecessor_id, successor_id))

        # ===== PROTOCOL DEVELOPMENT → COUNTRY-SPECIFIC REGULATORY TASKS =====
        # Protocol must be complete BEFORE any country-specific regulatory submissions
        # This links IND-100 to dynamically-created country regulatory tasks
        if 'IND-100' in task_map:
            country_code = workflow['country_code']

            # Link to country-specific EC (if exists)
            ec_id = f"REG-{country_code}-EC"
            if ec_id in task_map and ('IND-100', ec_id) not in existing_pairs:
                dependencies.append(Dependency(
                    predecessor_id='IND-100',
                    successor_id=ec_id,
                    type='finish-to-start',
                    lag_days=0
                ))
                existing_pairs.add(('IND-100', ec_id))

            # Link to country-specific Regulatory Authority (if exists)
            reg_id = f"REG-{country_code}-REG"
            if reg_id in task_map and ('IND-100', reg_id) not in existing_pairs:
                dependencies.append(Dependency(
                    predecessor_id='IND-100',
                    successor_id=reg_id,
                    type='finish-to-start',
                    lag_days=0
                ))
                existing_pairs.add(('IND-100', reg_id))

        # Three-layer sequential dependencies (e.g., Kenya: EC → PPB → NACOSTI)
        if workflow.get('workflow_type') == 'three_layer_sequential':
            country_code = workflow['country_code']

            # EC → Regulatory Authority
            ec_id = f"REG-{country_code}-EC"
            reg_id = f"REG-{country_code}-REG"
            if ec_id in task_map and reg_id in task_map:
                if (ec_id, reg_id) not in existing_pairs:
                    dependencies.append(Dependency(
                        predecessor_id=ec_id,
                        successor_id=reg_id,
                        type='finish-to-start',
                        lag_days=0
                    ))
                    existing_pairs.add((ec_id, reg_id))

            # Regulatory Authority → Additional authorities/bodies
            additional_bodies = workflow.get('additional_bodies', workflow.get('additional_authorities', []))
            for auth in additional_bodies:
                auth_id = f"REG-{country_code}-{auth['code']}"
                if reg_id in task_map and auth_id in task_map:
                    if (reg_id, auth_id) not in existing_pairs:
                        dependencies.append(Dependency(
                            predecessor_id=reg_id,
                            successor_id=auth_id,
                            type='finish-to-start',
                            lag_days=0
                        ))
                        existing_pairs.add((reg_id, auth_id))

        # Four-layer sequential dependencies (e.g., Vietnam: CEBRGL → ASTT → NECBR → Minister)
        if workflow.get('workflow_type') == 'four_layer_sequential':
            country_code = workflow['country_code']

            # Layer 1 → Layer 2: EC → Regulatory Authority
            ec_id = f"REG-{country_code}-EC"
            reg_id = f"REG-{country_code}-REG"
            if ec_id in task_map and reg_id in task_map:
                if (ec_id, reg_id) not in existing_pairs:
                    dependencies.append(Dependency(
                        predecessor_id=ec_id,
                        successor_id=reg_id,
                        type='finish-to-start',
                        lag_days=0
                    ))
                    existing_pairs.add((ec_id, reg_id))

            # Layer 2 → Layer 3 → Layer 4: Sequential chain through additional bodies
            additional_bodies = workflow.get('additional_bodies', [])
            predecessor_id = reg_id
            for auth in additional_bodies:
                auth_id = f"REG-{country_code}-{auth['code']}"
                if predecessor_id in task_map and auth_id in task_map:
                    if (predecessor_id, auth_id) not in existing_pairs:
                        dependencies.append(Dependency(
                            predecessor_id=predecessor_id,
                            successor_id=auth_id,
                            type='finish-to-start',
                            lag_days=0
                        ))
                        existing_pairs.add((predecessor_id, auth_id))
                    predecessor_id = auth_id  # Chain to next layer

        # ====================================================================================
        # CRITICAL: Link regulatory approvals to operational tasks
        # ====================================================================================
        # In reality, you CANNOT start site activation or patient enrollment without
        # regulatory approval. This links the final regulatory approval to key milestones.

        final_approval_task_id = self._get_final_regulatory_approval_id(workflow, task_map)

        # Tasks that require regulatory approval before starting
        tasks_requiring_approval = [
            'SITE-002',     # Site Activation
            'SITE-003',     # First Patient In (FPI)
            'SITE-004',     # Patient Enrollment Period
            'IND-018',      # Data System Opens for Enrollment
        ]

        if final_approval_task_id and final_approval_task_id in task_map:
            for task_id in tasks_requiring_approval:
                if task_id in task_map:
                    if (final_approval_task_id, task_id) not in existing_pairs:
                        dependencies.append(Dependency(
                            predecessor_id=final_approval_task_id,
                            successor_id=task_id,
                            type='finish-to-start',
                            lag_days=0
                        ))
                        existing_pairs.add((final_approval_task_id, task_id))

        logger.info(f"Total dependencies created: {len(dependencies)}")
        return dependencies

    def _get_final_regulatory_approval_id(self, workflow: Dict, task_map: Dict) -> Optional[str]:
        """
        Get the final regulatory approval task ID for a workflow

        This is the LAST regulatory approval that must complete before
        operational activities (site activation, enrollment) can begin.

        Args:
            workflow: Country workflow configuration
            task_map: Map of task IDs to Task objects

        Returns:
            Task ID of final regulatory approval, or None if not found
        """
        workflow_type = workflow.get('workflow_type')
        country_code = workflow['country_code']

        # Three-layer sequential (e.g., Kenya: EC → PPB → NACOSTI)
        # Final approval = last additional body (NACOSTI)
        if workflow_type == 'three_layer_sequential':
            additional_bodies = workflow.get('additional_bodies', workflow.get('additional_authorities', []))
            if additional_bodies:
                # Last body in the list is the final approval
                last_auth = additional_bodies[-1]
                final_id = f"REG-{country_code}-{last_auth['code']}"
                if final_id in task_map:
                    return final_id
            # Fallback to regulatory authority if no additional bodies
            return f"REG-{country_code}-REG" if f"REG-{country_code}-REG" in task_map else None

        # Four-layer sequential (e.g., Vietnam: CEBRGL → ASTT → NECBR → Minister)
        # Final approval = last additional body (Minister)
        elif workflow_type == 'four_layer_sequential':
            additional_bodies = workflow.get('additional_bodies', [])
            if additional_bodies:
                last_auth = additional_bodies[-1]
                final_id = f"REG-{country_code}-{last_auth['code']}"
                if final_id in task_map:
                    return final_id
            # Fallback to regulatory authority
            return f"REG-{country_code}-REG" if f"REG-{country_code}-REG" in task_map else None

        # Parallel workflows (e.g., US: FDA || IRB)
        # Both must complete - we'll link BOTH to operational tasks
        # For parallel workflows, use ontology-based regulatory tasks (REG-001, REG-002)
        elif workflow_type in ['parallel', 'parallel_integrated']:
            # Check for ontology regulatory tasks that represent final approval
            # REG-001: IND/CTA Submission & Review (FDA-equivalent)
            # REG-002: IRB/EC Approval (IRB-equivalent)
            # REG-INT-003: Ministerial/Final Approval (if exists)

            # Priority: Final approval > IND/CTA > IRB/EC
            if 'REG-INT-003' in task_map:
                return 'REG-INT-003'
            elif 'REG-002' in task_map:
                return 'REG-002'  # IRB/EC approval is typically the gate for enrollment
            elif 'REG-001' in task_map:
                return 'REG-001'

            return None

        # Sequential workflows (e.g., Bangladesh: NREC → DGDA)
        # Final approval = regulatory authority (second layer)
        elif workflow_type == 'sequential':
            final_id = f"REG-{country_code}-REG"
            if final_id in task_map:
                return final_id
            # Fallback to ontology regulatory tasks
            return self._get_ontology_regulatory_fallback(task_map)

        # Concurrent-sequential (e.g., DRC, India: Submit both, but regulatory waits for EC)
        # Final approval = regulatory authority (must approve after EC)
        elif workflow_type in ['concurrent_sequential', 'concurrent_sequential_multibody']:
            final_id = f"REG-{country_code}-REG"
            if final_id in task_map:
                return final_id
            return self._get_ontology_regulatory_fallback(task_map)

        # Flexible workflows (e.g., Sierra Leone: can be sequential OR parallel)
        # Assume sequential by default - regulatory authority is final
        elif workflow_type == 'flexible':
            final_id = f"REG-{country_code}-REG"
            if final_id in task_map:
                return final_id
            return self._get_ontology_regulatory_fallback(task_map)

        # Multi-body systems (e.g., Tanzania: TMDA + NatHREC + COSTECH)
        # Final approval = regulatory authority (TMDA in Tanzania)
        elif workflow_type in ['three_body_hybrid', 'four_body_parallel']:
            final_id = f"REG-{country_code}-REG"
            if final_id in task_map:
                return final_id
            return self._get_ontology_regulatory_fallback(task_map)

        # Dual pathway (China: standard vs HGR)
        # Assume standard pathway - regulatory authority
        elif workflow_type == 'dual_pathway':
            final_id = f"REG-{country_code}-REG"
            if final_id in task_map:
                return final_id
            return self._get_ontology_regulatory_fallback(task_map)

        # Default fallback - use ontology tasks
        return self._get_ontology_regulatory_fallback(task_map)

    def _get_ontology_regulatory_fallback(self, task_map: Dict) -> Optional[str]:
        """
        Fallback to ontology-based regulatory tasks when country-specific tasks don't exist

        For countries using parallel or other workflows that don't create custom regulatory
        tasks, we fall back to the ontology tasks.

        Args:
            task_map: Map of task IDs to Task objects

        Returns:
            Task ID of ontology regulatory task, or None
        """
        # Priority order:
        # 1. Ministerial/Final Approval (highest authority)
        # 2. IRB/EC Approval (required for patient protection)
        # 3. IND/CTA Submission (regulatory submission)

        if 'REG-INT-003' in task_map:
            return 'REG-INT-003'  # Ministerial/Final Approval
        elif 'REG-002' in task_map:
            return 'REG-002'  # IRB/EC Approval
        elif 'REG-001' in task_map:
            return 'REG-001'  # IND/CTA Submission & Review

        return None

    def generate_site_startup(
        self,
        country_code: str,
        site_id: str,
        study_phase: str,
        therapeutic_area: str,
        include_optional: bool = True
    ) -> Timeline:
        """
        Generate site startup template with authority-specific details

        Creates tasks specific to activating a clinical trial site, including:
        - Authority-specific regulatory submissions (e.g., "Submit IRAS Application to MHRA" for UK)
        - Multi-authority workflows (e.g., NDA + UNCST + EC for Uganda)
        - Site readiness and training tasks
        - GCP compliance and monitoring setup

        Args:
            country_code: ISO country code (e.g., "UG", "GB")
            site_id: Site identifier (e.g., "SITE-001")
            study_phase: Study phase
            therapeutic_area: Therapeutic area
            include_optional: Include optional tasks

        Returns:
            Timeline with authority-rich site startup tasks
        """
        workflow = self._get_workflow(country_code)
        logger.info(f"Generating site startup template for {site_id} in {workflow['country_name']}")

        tasks = []

        # ===== REGULATORY TASKS (AUTHORITY-SPECIFIC) =====
        regulatory_tasks = self._build_site_regulatory_tasks(
            workflow, site_id, study_phase, therapeutic_area
        )
        tasks.extend(regulatory_tasks)

        # ===== SITE READINESS TASKS =====
        site_readiness_tasks = [
            Task(
                id=f"{site_id}-READY-001",
                name=f"Site Assessment Visit - {site_id}",
                duration_days=1,
                category='Site',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id=f"{site_id}-READY-002",
                name=f"Essential Documents Collection - {site_id}",
                duration_days=14,
                category='Site',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id=f"{site_id}-READY-003",
                name=f"Site Initiation Visit (SIV) - {site_id}",
                duration_days=3,
                category='Site',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id=f"{site_id}-READY-004",
                name=f"GCP Training Completion - {site_id}",
                duration_days=2,
                category='Site',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id=f"{site_id}-READY-005",
                name=f"Site Activation - {site_id}",
                duration_days=1,
                category='Site',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
        ]
        tasks.extend(site_readiness_tasks)

        # Build dependencies
        dependencies = self._build_site_startup_dependencies(tasks, workflow, site_id)

        # Create timeline
        timeline = Timeline(
            study_name=f"{workflow['country_name']} Site Startup - {site_id}",
            phase=study_phase,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            therapeutic_area=therapeutic_area,
            tasks=tasks,
            dependencies=dependencies
        )

        logger.info(f"Site startup template generated: {len(tasks)} tasks, {len(dependencies)} dependencies")
        return timeline

    def _build_site_regulatory_tasks(
        self,
        workflow: Dict,
        site_id: str,
        phase: str,
        therapeutic_area: str
    ) -> List[Task]:
        """
        Build authority-specific regulatory tasks for site startup

        Returns tasks with full authority metadata (authority_full_name, authority_type, submission_form)
        """
        tasks = []
        country_code = workflow['country_code']
        country_name = workflow['country_name']

        # ===== ETHICS COMMITTEE SUBMISSION =====
        ec_authority = workflow.get('ethics_authority', {})
        ec_code = ec_authority.get('code', 'EC')
        ec_name = ec_authority.get('name', 'Ethics Committee')
        ec_duration = ec_authority.get('review_days', 30)

        # Determine submission form based on country
        if country_code == 'GB':
            ec_submission_form = "IRAS Application" if phase in ["Phase II", "Phase III", "Phase IV"] else "REC Application"
            ec_task_name = f"Submit {ec_submission_form} to REC"
        elif country_code == 'UG':
            ec_submission_form = "Ethics Application"
            ec_task_name = f"Submit to {ec_name}"
        else:
            ec_submission_form = "Ethics Application"
            ec_task_name = f"Submit to {ec_name}"

        ec_task = Task(
            id=f"{site_id}-REG-EC",
            name=ec_task_name,
            duration_days=ec_duration,
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(ec_code, country_code, country_name),
            country=country_code,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        )
        # Add authority-specific metadata
        ec_task.authority_full_name = ec_name
        ec_task.authority_type = "ethics"
        ec_task.submission_form = ec_submission_form
        tasks.append(ec_task)

        # ===== REGULATORY AUTHORITY SUBMISSION =====
        reg_authority = workflow.get('regulatory_authority', {})
        reg_code = reg_authority.get('code', 'REG')
        reg_name = reg_authority.get('name', 'Regulatory Authority')
        reg_duration = reg_authority.get('review_days', 30)

        # Determine submission form based on country
        if country_code == 'GB':
            reg_submission_form = "Clinical Trial Authorization (CTA)"
            reg_task_name = f"Submit {reg_submission_form} to MHRA"
        elif country_code == 'UG':
            reg_submission_form = "Clinical Trial Application"
            reg_task_name = f"Submit to National Drug Authority (NDA)"
        elif country_code == 'US':
            reg_submission_form = "Investigational New Drug (IND) Application"
            reg_task_name = f"Submit {reg_submission_form} to FDA"
        else:
            reg_submission_form = "Clinical Trial Application"
            reg_task_name = f"Submit to {reg_name}"

        reg_task = Task(
            id=f"{site_id}-REG-AUTH",
            name=reg_task_name,
            duration_days=reg_duration,
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(reg_code, country_code, country_name),
            country=country_code,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        )
        reg_task.authority_full_name = reg_name
        reg_task.authority_type = "regulatory"
        reg_task.submission_form = reg_submission_form
        tasks.append(reg_task)

        # ===== ADDITIONAL AUTHORITIES (MULTI-LAYER WORKFLOWS) =====
        additional_bodies = workflow.get('additional_bodies', workflow.get('additional_authorities', []))
        for auth in additional_bodies:
            auth_code = auth.get('code')
            auth_name = auth.get('name')
            auth_duration = auth.get('review_days', 30)
            auth_type = auth.get('type', 'permits')

            # Country-specific task naming
            if country_code == 'UG' and auth_code == 'UNCST':
                task_name = f"Obtain UNCST Research Permit"
                submission_form = "UNCST Research Permit Application"
            elif country_code == 'GB' and 'NHS' in auth_code:
                task_name = f"Obtain NHS R&D Approval"
                submission_form = "NHS R&D Application"
            elif country_code == 'KE' and auth_code == 'NACOSTI':
                task_name = f"Obtain NACOSTI Research Clearance"
                submission_form = "NACOSTI Application"
            else:
                task_name = f"Submit to {auth_name}"
                submission_form = f"{auth_name} Application"

            auth_task = Task(
                id=f"{site_id}-REG-{auth_code}",
                name=task_name,
                duration_days=auth_duration,
                category='Regulatory',
                phase=phase,
                authority=self._map_authority(auth_code, country_code, country_name),
                country=country_code,
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            )
            auth_task.authority_full_name = auth_name
            auth_task.authority_type = auth_type
            auth_task.submission_form = submission_form
            tasks.append(auth_task)

        logger.info(f"Built {len(tasks)} authority-specific regulatory tasks for {country_name}")
        return tasks

    def _build_site_startup_dependencies(
        self,
        tasks: List[Task],
        workflow: Dict,
        site_id: str
    ) -> List[Dependency]:
        """Build dependencies for site startup tasks"""
        dependencies = []
        task_map = {t.id: t for t in tasks}

        # Sequential regulatory approval workflow
        workflow_type = workflow.get('workflow_type')

        if workflow_type in ['three_layer_sequential', 'four_layer_sequential', 'sequential']:
            # EC → Regulatory Authority
            if f"{site_id}-REG-EC" in task_map and f"{site_id}-REG-AUTH" in task_map:
                dependencies.append(Dependency(
                    predecessor_id=f"{site_id}-REG-EC",
                    successor_id=f"{site_id}-REG-AUTH",
                    type='finish-to-start',
                    lag_days=0
                ))

            # Regulatory Authority → Additional bodies (sequential)
            additional_bodies = workflow.get('additional_bodies', workflow.get('additional_authorities', []))
            predecessor_id = f"{site_id}-REG-AUTH"
            for auth in additional_bodies:
                auth_id = f"{site_id}-REG-{auth['code']}"
                if predecessor_id in task_map and auth_id in task_map:
                    dependencies.append(Dependency(
                        predecessor_id=predecessor_id,
                        successor_id=auth_id,
                        type='finish-to-start',
                        lag_days=0
                    ))
                    predecessor_id = auth_id

        # Site readiness workflow
        readiness_chain = [
            (f"{site_id}-READY-001", f"{site_id}-READY-002"),  # Assessment → Documents
            (f"{site_id}-READY-002", f"{site_id}-READY-003"),  # Documents → SIV
            (f"{site_id}-READY-003", f"{site_id}-READY-004"),  # SIV → Training
            (f"{site_id}-READY-004", f"{site_id}-READY-005"),  # Training → Activation
        ]

        for pred, succ in readiness_chain:
            if pred in task_map and succ in task_map:
                dependencies.append(Dependency(
                    predecessor_id=pred,
                    successor_id=succ,
                    type='finish-to-start',
                    lag_days=0
                ))

        # Regulatory approval gates site activation
        final_reg_task = self._get_final_site_regulatory_task(workflow, site_id, task_map)
        if final_reg_task and final_reg_task in task_map and f"{site_id}-READY-005" in task_map:
            dependencies.append(Dependency(
                predecessor_id=final_reg_task,
                successor_id=f"{site_id}-READY-005",
                type='finish-to-start',
                lag_days=0
            ))

        return dependencies

    def _get_final_site_regulatory_task(self, workflow: Dict, site_id: str, task_map: Dict) -> Optional[str]:
        """Get the final regulatory approval task for a site"""
        # Check for additional bodies (multi-layer)
        additional_bodies = workflow.get('additional_bodies', workflow.get('additional_authorities', []))
        if additional_bodies:
            last_auth_id = f"{site_id}-REG-{additional_bodies[-1]['code']}"
            if last_auth_id in task_map:
                return last_auth_id

        # Fallback to regulatory authority
        if f"{site_id}-REG-AUTH" in task_map:
            return f"{site_id}-REG-AUTH"

        # Fallback to EC
        if f"{site_id}-REG-EC" in task_map:
            return f"{site_id}-REG-EC"

        return None

    def generate_site_closeout(
        self,
        country_code: str,
        site_id: str,
        study_phase: str,
        therapeutic_area: str,
        include_optional: bool = True
    ) -> Timeline:
        """
        Generate site closeout template with authority-specific details

        Creates tasks for closing a clinical trial site, including:
        - Final monitoring visits
        - IP accountability
        - Authority-specific closeout reporting
        - Essential document archiving

        Args:
            country_code: ISO country code
            site_id: Site identifier
            study_phase: Study phase
            therapeutic_area: Therapeutic area
            include_optional: Include optional tasks

        Returns:
            Timeline with authority-rich site closeout tasks
        """
        workflow = self._get_workflow(country_code)
        logger.info(f"Generating site closeout template for {site_id} in {workflow['country_name']}")

        tasks = []

        # ===== CLOSEOUT MONITORING TASKS =====
        monitoring_tasks = [
            Task(
                id=f"{site_id}-CLOSE-001",
                name=f"Final Monitoring Visit - {site_id}",
                duration_days=5,
                category='Site',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id=f"{site_id}-CLOSE-002",
                name=f"IP Accountability & Return - {site_id}",
                duration_days=7,
                category='Pharmacy',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id=f"{site_id}-CLOSE-003",
                name=f"Essential Documents Archiving - {site_id}",
                duration_days=14,
                category='Documents',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
        ]
        tasks.extend(monitoring_tasks)

        # ===== AUTHORITY-SPECIFIC CLOSEOUT REPORTING =====
        closeout_reporting_tasks = self._build_site_closeout_reporting_tasks(
            workflow, site_id, study_phase, therapeutic_area
        )
        tasks.extend(closeout_reporting_tasks)

        # Build dependencies
        dependencies = self._build_site_closeout_dependencies(tasks, site_id)

        # Create timeline
        timeline = Timeline(
            study_name=f"{workflow['country_name']} Site Closeout - {site_id}",
            phase=study_phase,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            therapeutic_area=therapeutic_area,
            tasks=tasks,
            dependencies=dependencies
        )

        logger.info(f"Site closeout template generated: {len(tasks)} tasks")
        return timeline

    def _build_site_closeout_reporting_tasks(
        self,
        workflow: Dict,
        site_id: str,
        phase: str,
        therapeutic_area: str
    ) -> List[Task]:
        """Build authority-specific closeout reporting tasks"""
        tasks = []
        country_code = workflow['country_code']
        country_name = workflow['country_name']

        # ===== REGULATORY AUTHORITY CLOSEOUT =====
        reg_authority = workflow.get('regulatory_authority', {})
        reg_code = reg_authority.get('code', 'REG')
        reg_name = reg_authority.get('name', 'Regulatory Authority')

        if country_code == 'GB':
            task_name = f"Submit Study Completion Notice to MHRA"
            submission_form = "MHRA End of Trial Declaration"
        elif country_code == 'UG':
            task_name = f"Submit Completion Report to NDA"
            submission_form = "NDA Study Completion Report"
        elif country_code == 'US':
            task_name = f"Submit Final Report to FDA"
            submission_form = "FDA Final Study Report"
        else:
            task_name = f"Submit Completion Report to {reg_name}"
            submission_form = f"{reg_name} Completion Report"

        reg_task = Task(
            id=f"{site_id}-REPORT-REG",
            name=task_name,
            duration_days=15,
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(reg_code, country_code, country_name),
            country=country_code,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        )
        reg_task.authority_full_name = reg_name
        reg_task.authority_type = "regulatory"
        reg_task.submission_form = submission_form
        tasks.append(reg_task)

        # ===== ETHICS COMMITTEE CLOSEOUT =====
        ec_authority = workflow.get('ethics_authority', {})
        ec_code = ec_authority.get('code', 'EC')
        ec_name = ec_authority.get('name', 'Ethics Committee')

        if country_code == 'GB':
            task_name = f"Submit Final Report to REC"
            submission_form = "REC End of Study Notification"
        else:
            task_name = f"Submit Final Report to {ec_name}"
            submission_form = f"{ec_name} Final Report"

        ec_task = Task(
            id=f"{site_id}-REPORT-EC",
            name=task_name,
            duration_days=7,
            category='Regulatory',
            phase=phase,
            authority=self._map_authority(ec_code, country_code, country_name),
            country=country_code,
            therapeutic_area=therapeutic_area,
            is_mandatory=True
        )
        ec_task.authority_full_name = ec_name
        ec_task.authority_type = "ethics"
        ec_task.submission_form = submission_form
        tasks.append(ec_task)

        # ===== ADDITIONAL AUTHORITIES =====
        additional_bodies = workflow.get('additional_bodies', workflow.get('additional_authorities', []))
        for auth in additional_bodies:
            auth_code = auth.get('code')
            auth_name = auth.get('name')
            auth_type = auth.get('type', 'permits')

            if country_code == 'UG' and auth_code == 'UNCST':
                task_name = f"Submit Final Report to UNCST"
                submission_form = "UNCST Final Research Report"
            else:
                task_name = f"Notify {auth_name} of Study Completion"
                submission_form = f"{auth_name} Completion Notice"

            auth_task = Task(
                id=f"{site_id}-REPORT-{auth_code}",
                name=task_name,
                duration_days=7,
                category='Regulatory',
                phase=phase,
                authority=self._map_authority(auth_code, country_code, country_name),
                country=country_code,
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            )
            auth_task.authority_full_name = auth_name
            auth_task.authority_type = auth_type
            auth_task.submission_form = submission_form
            tasks.append(auth_task)

        return tasks

    def _build_site_closeout_dependencies(self, tasks: List[Task], site_id: str) -> List[Dependency]:
        """Build dependencies for site closeout tasks"""
        dependencies = []
        task_map = {t.id: t for t in tasks}

        # Closeout workflow
        closeout_chain = [
            (f"{site_id}-CLOSE-001", f"{site_id}-CLOSE-002"),  # Monitoring → IP Return
            (f"{site_id}-CLOSE-002", f"{site_id}-CLOSE-003"),  # IP Return → Archiving
            (f"{site_id}-CLOSE-003", f"{site_id}-REPORT-REG"), # Archiving → Regulatory Report
            (f"{site_id}-REPORT-REG", f"{site_id}-REPORT-EC"), # Regulatory → Ethics
        ]

        for pred, succ in closeout_chain:
            if pred in task_map and succ in task_map:
                dependencies.append(Dependency(
                    predecessor_id=pred,
                    successor_id=succ,
                    type='finish-to-start',
                    lag_days=0
                ))

        return dependencies

    def generate_study_closeout(
        self,
        country_code: str,
        study_phase: str,
        therapeutic_area: str,
        include_optional: bool = True
    ) -> Timeline:
        """
        Generate study-wide closeout template

        Creates study-level closeout tasks that occur after all sites are closed:
        - Database lock
        - Statistical analysis
        - Clinical Study Report (CSR)
        - Final regulatory submissions
        - Study archiving

        Args:
            country_code: ISO country code
            study_phase: Study phase
            therapeutic_area: Therapeutic area
            include_optional: Include optional tasks

        Returns:
            Timeline with study-level closeout tasks
        """
        workflow = self._get_workflow(country_code)
        logger.info(f"Generating study closeout template for {workflow['country_name']}")

        tasks = []

        # ===== DATABASE LOCK & ANALYSIS =====
        analysis_tasks = [
            Task(
                id='STUDY-CLOSE-001',
                name='All Sites Closed',
                duration_days=1,
                category='Closeout',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id='STUDY-CLOSE-002',
                name='Database Lock',
                duration_days=1,
                category='Data',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id='STUDY-CLOSE-003',
                name='Statistical Analysis',
                duration_days=28,
                category='Data',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id='STUDY-CLOSE-004',
                name='Clinical Study Report (CSR) Preparation',
                duration_days=56,
                category='Regulatory',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id='STUDY-CLOSE-005',
                name='Final Regulatory Submissions (All Authorities)',
                duration_days=30,
                category='Regulatory',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
            Task(
                id='STUDY-CLOSE-006',
                name='Study Master File Archiving',
                duration_days=14,
                category='Documents',
                phase=study_phase,
                authority=self._map_authority(
                    workflow['regulatory_authority']['code'],
                    workflow['country_code'],
                    workflow['country_name']
                ),
                country=workflow['country_code'],
                therapeutic_area=therapeutic_area,
                is_mandatory=True
            ),
        ]
        tasks.extend(analysis_tasks)

        # Build dependencies
        dependencies = self._build_study_closeout_dependencies(tasks)

        # Create timeline
        timeline = Timeline(
            study_name=f"{workflow['country_name']} Study Closeout",
            phase=study_phase,
            authority=self._map_authority(
                workflow['regulatory_authority']['code'],
                workflow['country_code'],
                workflow['country_name']
            ),
            therapeutic_area=therapeutic_area,
            tasks=tasks,
            dependencies=dependencies
        )

        logger.info(f"Study closeout template generated: {len(tasks)} tasks")
        return timeline

    def _build_study_closeout_dependencies(self, tasks: List[Task]) -> List[Dependency]:
        """Build dependencies for study closeout tasks"""
        dependencies = []
        task_map = {t.id: t for t in tasks}

        # Study closeout workflow
        closeout_chain = [
            ('STUDY-CLOSE-001', 'STUDY-CLOSE-002'),  # All Sites Closed → DB Lock
            ('STUDY-CLOSE-002', 'STUDY-CLOSE-003'),  # DB Lock → Analysis
            ('STUDY-CLOSE-003', 'STUDY-CLOSE-004'),  # Analysis → CSR
            ('STUDY-CLOSE-004', 'STUDY-CLOSE-005'),  # CSR → Final Submissions
            ('STUDY-CLOSE-005', 'STUDY-CLOSE-006'),  # Submissions → Archiving
        ]

        for pred, succ in closeout_chain:
            if pred in task_map and succ in task_map:
                dependencies.append(Dependency(
                    predecessor_id=pred,
                    successor_id=succ,
                    type='finish-to-start',
                    lag_days=0
                ))

        return dependencies
