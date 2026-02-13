"""
Signal Extraction Engine

Extracts signals from tracker files (TMF, Risk Log, etc.) using:
1. Org-specific column mappings (configured by Account Admin)
2. Signal extraction rules (defined in tracker_definitions)

Workflow:
1. Account Admin configures column mapping once in web portal
2. CPM uploads tracker via MS Project add-in
3. Engine uses saved mapping to parse file
4. Engine applies rules to extract signals
5. Signals stored in database for correlation
"""

import pandas as pd
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pathlib import Path
import logging
import uuid

logger = logging.getLogger(__name__)


class Signal:
    """Normalized signal object"""

    def __init__(
        self,
        signal_type: str,
        signal_category: Optional[str],
        signal_source: str,
        signal_description: str,
        priority: int,
        status: str = "open",
        signal_detail: Optional[Dict] = None,
        date_identified: Optional[date] = None,
        target_date: Optional[date] = None,
        escalation_level: Optional[str] = None,
        escalation_notes: Optional[str] = None
    ):
        self.signal_id = str(uuid.uuid4())
        self.signal_type = signal_type
        self.signal_category = signal_category
        self.signal_source = signal_source
        self.signal_description = signal_description
        self.signal_detail = signal_detail or {}
        self.priority = priority
        self.status = status
        self.date_identified = date_identified or datetime.now().date()
        self.target_date = target_date
        self.escalation_level = escalation_level
        self.escalation_notes = escalation_notes

    def to_dict(self) -> Dict:
        """Convert to dictionary for database storage"""
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type,
            "signal_category": self.signal_category,
            "signal_source": self.signal_source,
            "signal_description": self.signal_description,
            "signal_detail": json.dumps(self.signal_detail),
            "priority": self.priority,
            "status": self.status,
            "date_identified": self.date_identified.isoformat() if self.date_identified else None,
            "target_date": self.target_date.isoformat() if self.target_date else None,
            "escalation_level": self.escalation_level,
            "escalation_notes": self.escalation_notes
        }


class SignalExtractionEngine:
    """Extract signals from tracker files"""

    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.conn.row_factory = sqlite3.Row

    def extract_signals_from_tracker(
        self,
        file_path: str,
        tracker_type: str,
        org_id: str,
        project_id: str
    ) -> List[Signal]:
        """
        Extract signals from tracker file using org-specific column mapping

        Args:
            file_path: Path to Excel file
            tracker_type: Type of tracker (e.g., 'risk_log', 'tmf_completeness')
            org_id: Organization ID
            project_id: Project ID

        Returns:
            List of extracted Signal objects
        """
        logger.info(f"Extracting signals from {tracker_type} for org {org_id}, project {project_id}")

        # Get org's column mapping
        column_mapping = self._get_column_mapping(org_id, tracker_type)
        if not column_mapping:
            raise ValueError(f"No column mapping found for {tracker_type}. Account Admin must configure tracker first.")

        # Get tracker definition and rules
        tracker_def = self._get_tracker_definition(tracker_type)
        if not tracker_def:
            raise ValueError(f"Tracker definition not found for {tracker_type}")

        # Parse Excel file using column mapping
        rows = self._parse_tracker_file(file_path, column_mapping, tracker_def)

        # Apply signal extraction rules
        signals = self._apply_extraction_rules(rows, tracker_def, tracker_type)

        logger.info(f"Extracted {len(signals)} signals from {len(rows)} rows")

        return signals

    def _get_column_mapping(self, org_id: str, tracker_type: str) -> Optional[Dict]:
        """Get org-specific column mapping from database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT column_mappings, transformation_rules
            FROM tracker_column_mappings
            WHERE org_id = ? AND tracker_type = ?
        """, (org_id, tracker_type))

        row = cursor.fetchone()
        if not row:
            return None

        column_mappings = json.loads(row['column_mappings']) if isinstance(row['column_mappings'], str) else row['column_mappings']
        transformation_rules = json.loads(row['transformation_rules']) if row['transformation_rules'] else None

        return {
            "column_mappings": column_mappings,
            "transformation_rules": transformation_rules
        }

    def _get_tracker_definition(self, tracker_type: str) -> Optional[Dict]:
        """Get tracker definition from database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT tracker_def_id, tracker_name, schema_definition, signal_extraction_rules
            FROM tracker_definitions
            WHERE tracker_type = ?
        """, (tracker_type,))

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "tracker_def_id": row['tracker_def_id'],
            "tracker_name": row['tracker_name'],
            "schema_definition": json.loads(row['schema_definition']) if isinstance(row['schema_definition'], str) else row['schema_definition'],
            "signal_extraction_rules": json.loads(row['signal_extraction_rules']) if isinstance(row['signal_extraction_rules'], str) else row['signal_extraction_rules']
        }

    def _parse_tracker_file(
        self,
        file_path: str,
        column_mapping: Dict,
        tracker_def: Dict
    ) -> List[Dict]:
        """Parse Excel file using column mapping"""
        mappings = column_mapping['column_mappings']

        # Read Excel file
        # Check if multi-sheet tracker
        schema = tracker_def['schema_definition']
        if schema.get('multi_sheet_support'):
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            all_rows = []

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                # Map column names
                df_renamed = df.rename(columns=mappings)

                # Convert to dict rows
                rows = df_renamed.to_dict('records')

                # Add sheet name to each row
                for row in rows:
                    row['_sheet_name'] = sheet_name

                all_rows.extend(rows)

            return all_rows
        else:
            # Single sheet
            df = pd.read_excel(file_path)

            # Map column names
            df_renamed = df.rename(columns=mappings)

            # Convert to dict rows
            return df_renamed.to_dict('records')

    def _apply_extraction_rules(
        self,
        rows: List[Dict],
        tracker_def: Dict,
        tracker_type: str
    ) -> List[Signal]:
        """Apply signal extraction rules to rows"""
        signals = []

        rules = tracker_def['signal_extraction_rules']['rules']

        for row in rows:
            for rule in rules:
                # Check if rule applies to specific sheet
                if 'sheet' in rule:
                    if row.get('_sheet_name') != rule['sheet']:
                        continue

                # Evaluate rule condition
                if self._evaluate_condition(rule['condition'], row):
                    # Extract signal
                    signal = self._create_signal_from_rule(rule, row, tracker_type)
                    if signal:
                        signals.append(signal)

        return signals

    def _evaluate_condition(self, condition: Dict, row: Dict) -> bool:
        """Evaluate a rule condition against a row"""
        # Handle composite conditions
        if 'all_of' in condition:
            return all(self._evaluate_condition(c, row) for c in condition['all_of'])

        if 'any_of' in condition:
            return any(self._evaluate_condition(c, row) for c in condition['any_of'])

        # Handle simple conditions
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')

        row_value = row.get(field)

        # Handle null checks
        if operator == 'is_null':
            return pd.isna(row_value) or row_value is None or (isinstance(row_value, str) and row_value.strip() == '')

        if operator == 'is_not_null':
            return not (pd.isna(row_value) or row_value is None or (isinstance(row_value, str) and row_value.strip() == ''))

        # Handle comparisons
        if operator == 'equals':
            return str(row_value).strip() == str(value).strip() if row_value is not None else False

        if operator == 'greater_than_or_equal':
            try:
                return float(row_value) >= float(value)
            except (ValueError, TypeError):
                return False

        if operator == 'less_than':
            try:
                return float(row_value) < float(value)
            except (ValueError, TypeError):
                return False

        if operator == 'days_overdue':
            try:
                if pd.isna(row_value):
                    return False
                target_date = pd.to_datetime(row_value).date()
                today = datetime.now().date()
                days_overdue = (today - target_date).days
                return days_overdue > value
            except:
                return False

        if operator == 'is_past':
            try:
                if pd.isna(row_value):
                    return False
                target_date = pd.to_datetime(row_value).date()
                today = datetime.now().date()
                return target_date < today
            except:
                return False

        return False

    def _create_signal_from_rule(
        self,
        rule: Dict,
        row: Dict,
        tracker_type: str
    ) -> Optional[Signal]:
        """Create Signal object from rule and row data"""
        try:
            # Build signal description
            signal_description = self._build_signal_description(rule, row)

            # Extract relevant fields for signal detail
            signal_detail = {k: str(v) for k, v in row.items() if not k.startswith('_')}

            # Get signal category from row if available
            signal_category = row.get('category') or row.get('risk_category')

            return Signal(
                signal_type=rule['signal_type'],
                signal_category=signal_category,
                signal_source=tracker_type,
                signal_description=signal_description,
                priority=rule.get('priority', 5),
                signal_detail=signal_detail,
                date_identified=datetime.now().date(),
                target_date=self._extract_date(row.get('target_date')),
                escalation_level=rule.get('escalation_level'),
                escalation_notes=row.get('escalation_notes')
            )

        except Exception as e:
            logger.error(f"Failed to create signal from rule {rule['rule_id']}: {e}")
            return None

    def _build_signal_description(self, rule: Dict, row: Dict) -> str:
        """Build human-readable signal description"""
        description = rule.get('description', '')

        # For risk logs
        if 'risk_number' in row and 'risk_detail' in row:
            risk_num = row.get('risk_number', 'Unknown')
            risk_detail = row.get('risk_detail', 'No description')
            priority = row.get('priority', 'Unknown')
            return f"Risk #{risk_num} (Priority {priority}): {risk_detail}"

        # For TMF trackers
        if 'artifact_name' in row:
            artifact = row.get('artifact_name', 'Unknown artifact')
            status = row.get('status', 'Unknown status')
            return f"TMF Artifact '{artifact}': {status} - {description}"

        # Default
        return description

    def _extract_date(self, value) -> Optional[date]:
        """Extract date from various formats"""
        if pd.isna(value) or value is None:
            return None

        try:
            return pd.to_datetime(value).date()
        except:
            return None


def store_signals(
    conn: sqlite3.Connection,
    signals: List[Signal],
    upload_id: str,
    org_id: str,
    project_id: str
):
    """Store extracted signals in database"""
    cursor = conn.cursor()

    for signal in signals:
        signal_dict = signal.to_dict()

        cursor.execute("""
            INSERT INTO signals (
                signal_id, upload_id, org_id, project_id,
                signal_type, signal_category, signal_source,
                signal_description, signal_detail,
                priority, status,
                date_identified, target_date,
                escalation_level, escalation_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            signal_dict['signal_id'],
            upload_id,
            org_id,
            project_id,
            signal_dict['signal_type'],
            signal_dict['signal_category'],
            signal_dict['signal_source'],
            signal_dict['signal_description'],
            signal_dict['signal_detail'],
            signal_dict['priority'],
            signal_dict['status'],
            signal_dict['date_identified'],
            signal_dict['target_date'],
            signal_dict['escalation_level'],
            signal_dict['escalation_notes']
        ))

    conn.commit()
    logger.info(f"Stored {len(signals)} signals in database")
