# Seleen Rules Engine Design

**Version:** 1.0  
**Component:** Backend Intelligence Layer  
**Purpose:** Configuration-driven clinical trial timeline validation

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Rule Categories](#rule-categories)
4. [Rule Definition Format](#rule-definition-format)
5. [Validator Implementations](#validator-implementations)
6. [Configuration Structure](#configuration-structure)
7. [Validation Flow](#validation-flow)
8. [Extension Points](#extension-points)

---

## 1. Overview

### 1.1 Purpose

The Seleen Rules Engine validates clinical trial timelines against:
- Regulatory authority requirements
- Operational best practices
- Logical dependencies
- Duration benchmarks
- Checklist completeness

### 1.2 Design Principles

1. **Configuration-Driven**: Business logic externalized to YAML files
2. **Composable**: Rules combine to form complex validations
3. **Explainable**: Every violation includes clear description + fix
4. **Extensible**: New rules added without code changes
5. **Authority-Aware**: Rules adapt to FDA, EMA, MHRA, etc.
6. **Fail-Fast**: Critical errors detected early

---

## 2. Architecture

### 2.1 Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   Rules Engine                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Rule Registry                           │  │
│  │  - Loads rules from YAML                          │  │
│  │  - Maintains rule metadata                        │  │
│  │  - Version management                             │  │
│  └───────────────────────────────────────────────────┘  │
│                          │                              │
│  ┌───────────────────────▼───────────────────────────┐  │
│  │         Validation Orchestrator                   │  │
│  │  - Executes validators in order                   │  │
│  │  - Aggregates results                             │  │
│  │  - Handles dependencies between validators        │  │
│  └───────────────────────────────────────────────────┘  │
│                          │                              │
│         ┌────────────────┴────────────────┐             │
│         │                                 │             │
│  ┌──────▼─────────┐              ┌───────▼──────────┐  │
│  │   Regulatory   │              │   Operational    │  │
│  │   Validators   │              │   Validators     │  │
│  └────────────────┘              └──────────────────┘  │
│         │                                 │             │
│  ┌──────▼─────────┐              ┌───────▼──────────┐  │
│  │   Checklist    │              │   Duration       │  │
│  │   Validators   │              │   Validators     │  │
│  └────────────────┘              └──────────────────┘  │
│         │                                 │             │
│  ┌──────▼─────────┐              ┌───────▼──────────┐  │
│  │   Dependency   │              │   Graph          │  │
│  │   Validators   │              │   Validators     │  │
│  └────────────────┘              └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Class Structure

```python
# rules_engine.py

from abc import ABC, abstractmethod
from typing import List, Dict
from app.models import ProjectData, ValidationViolation

class Validator(ABC):
    """Base class for all validators"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.rule_id_prefix = self.__class__.__name__
    
    @abstractmethod
    def validate(self, project: ProjectData) -> List[ValidationViolation]:
        """Execute validation and return violations"""
        pass
    
    def create_violation(self, 
                        task_id: int,
                        task_name: str,
                        violation_type: str,
                        severity: str,
                        description: str,
                        suggested_fix: str = None,
                        rule_id: str = None) -> ValidationViolation:
        """Helper to create standardized violations"""
        return ValidationViolation(
            task_id=task_id,
            task_name=task_name,
            violation_type=violation_type,
            severity=severity,
            description=description,
            suggested_fix=suggested_fix,
            rule_id=rule_id or f"{self.rule_id_prefix}_{violation_type}"
        )

class RulesEngine:
    """Main orchestrator for timeline validation"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.validators = self._initialize_validators()
    
    def _initialize_validators(self) -> List[Validator]:
        """Load and initialize all validators"""
        return [
            RegulatoryGatingValidator(self.config_manager.load_authority_timelines()),
            OperationalSequenceValidator(self.config_manager.load_task_ontology()),
            ChecklistCompletenessValidator(self.config_manager.load_checklists()),
            DurationBoundsValidator(self.config_manager.load_authority_timelines()),
            DependencyValidator(self.config_manager.load_task_ontology()),
            ParallelizationValidator(self.config_manager.load_task_ontology())
        ]
    
    def validate(self, project: ProjectData) -> List[ValidationViolation]:
        """Execute all validators and aggregate violations"""
        all_violations = []
        
        for validator in self.validators:
            violations = validator.validate(project)
            all_violations.extend(violations)
        
        # Sort by severity: Error > Warning > Info
        return self._sort_violations(all_violations)
    
    def _sort_violations(self, violations: List[ValidationViolation]) -> List[ValidationViolation]:
        """Sort violations by severity and task ID"""
        severity_order = {"Error": 0, "Warning": 1, "Info": 2}
        return sorted(violations, 
                     key=lambda v: (severity_order.get(v.severity, 3), v.task_id))
```

---

## 3. Rule Categories

### 3.1 Regulatory Gating Rules

**Purpose**: Enforce authority-specific task sequences

**Examples**:
- FDA: Protocol → IND → IRB → SIV
- EMA: Protocol → CTA → Ethics → SIV
- MHRA: Protocol → CTA → REC → SIV

**Rule Structure**:
```yaml
regulatory_gating:
  FDA:
    mandatory_sequence:
      - task: protocol_development
        must_precede: [ind_submission, irb_submission]
      
      - task: ind_submission
        must_precede: [irb_submission, siv]
        min_gap_days: 30  # IND review period
      
      - task: irb_submission
        must_precede: [siv, first_patient_in]
        must_follow: [protocol_development, ind_submission]
        min_gap_days: 45  # IRB review period
```

---

### 3.2 Operational Sequence Rules

**Purpose**: Enforce logical operational prerequisites

**Examples**:
- Pharmacy setup before IP shipment
- EDC configuration before SIV
- Training materials before investigator meeting

**Rule Structure**:
```yaml
operational_sequences:
  - rule_id: OPS_001
    name: Pharmacy before IP Shipment
    prerequisite: pharmacy_setup
    dependent: ip_shipment
    description: "Pharmacy must be operational before shipping IP"
    severity: Error
    
  - rule_id: OPS_002
    name: EDC before SIV
    prerequisite: edc_configuration
    dependent: siv
    description: "EDC system must be ready before site activation"
    severity: Error
```

---

### 3.3 Duration Bounds Rules

**Purpose**: Flag unrealistic task durations

**Examples**:
- Protocol development: 60-120 days typical
- IRB approval: 30-60 days (FDA)
- SIV: 7-21 days

**Rule Structure**:
```yaml
duration_bounds:
  protocol_development:
    min_days: 60
    max_days: 120
    typical_days: 90
    warning_threshold_pct: 20  # Warn if >20% outside range
    
  irb_approval:
    authority_specific:
      FDA:
        min_days: 30
        max_days: 60
        typical_days: 45
      EMA:
        min_days: 45
        max_days: 90
        typical_days: 60
```

---

### 3.4 Dependency Rules

**Purpose**: Validate task dependencies and detect cycles

**Examples**:
- No circular dependencies
- Finish-to-start relationships validated
- Critical path dependencies verified

**Rule Structure**:
```yaml
dependency_rules:
  - rule_id: DEP_001
    name: No Circular Dependencies
    check_type: cycle_detection
    severity: Error
    
  - rule_id: DEP_002
    name: Valid Predecessor Types
    allowed_types: [FS, SS, FF, SF]  # Microsoft Project types
    severity: Error
    
  - rule_id: DEP_003
    name: Mandatory Dependencies
    task: siv
    required_predecessors: [protocol_development, irb_approval, site_selection]
    severity: Error
```

---

### 3.5 Checklist Completeness Rules

**Purpose**: Ensure all required tasks are present

**Examples**:
- Study Startup checklist (15+ items)
- SIV checklist (12+ items)
- Closeout checklist (10+ items)

**Rule Structure**:
```yaml
checklist_rules:
  startup:
    checklist_id: startup
    required_tasks:
      - protocol_development
      - budget_approval
      - cro_contracting
      - regulatory_submission
      - insurance_setup
    optional_tasks:
      - feasibility_assessment
      - vendor_selection
    completeness_threshold_pct: 80  # Must have 80% of required items
```

---

### 3.6 Parallelization Rules

**Purpose**: Identify tasks that should/could run in parallel

**Examples**:
- Site contracts can parallel site training
- Multiple site activations can parallel
- Some regulatory submissions can parallel

**Rule Structure**:
```yaml
parallelization_rules:
  - rule_id: PAR_001
    task: site_contracts
    can_parallel_with: [site_training_materials, regulatory_binder_prep]
    suggestion: "These tasks can run in parallel to save time"
    severity: Info
    potential_savings_days: 14
```

---

## 4. Rule Definition Format

### 4.1 Rule Metadata

Every rule includes:

```yaml
rule:
  id: REG_GATE_001
  name: "IND Before IRB"
  category: regulatory_gating
  severity: Error
  authority: FDA
  description: "IND submission must be complete before IRB submission"
  rationale: "FDA requires IND clearance before institutional review"
  reference: "21 CFR 312.20"
  enabled: true
  version: 1.0
```

### 4.2 Rule Execution Specification

```yaml
execution:
  type: prerequisite_check
  parameters:
    prerequisite_task: ind_submission
    dependent_task: irb_submission
    min_gap_days: 30
    max_gap_days: null
  
violation:
  template: "{dependent_task} cannot start until {min_gap_days} days after {prerequisite_task}"
  suggested_fix: "Add dependency: {dependent_task} → {prerequisite_task} + {min_gap_days} days"
```

---

## 5. Validator Implementations

### 5.1 RegulatoryGatingValidator

**Responsibility**: Enforce authority-specific task sequences

```python
class RegulatoryGatingValidator(Validator):
    """Validates regulatory authority gating requirements"""
    
    def validate(self, project: ProjectData) -> List[ValidationViolation]:
        violations = []
        authority = project.regulatory_authority
        
        if authority not in self.config:
            return violations
        
        # Get authority-specific gating rules
        gating_config = self.config[authority]
        mandatory_sequence = gating_config.get('mandatory_sequence', [])
        
        # Build task lookup
        task_dict = {t.id: t for t in project.tasks}
        task_by_name = {self._normalize_name(t.name): t for t in project.tasks}
        
        # Check each gating rule
        for rule in mandatory_sequence:
            prerequisite_name = rule['task']
            must_precede = rule.get('must_precede', [])
            min_gap_days = rule.get('min_gap_days', 0)
            
            prerequisite_task = task_by_name.get(prerequisite_name)
            if not prerequisite_task:
                continue  # Task not in project - handled by checklist validator
            
            # Check each dependent task
            for dependent_name in must_precede:
                dependent_task = task_by_name.get(dependent_name)
                if not dependent_task:
                    continue
                
                # Verify dependency exists
                if prerequisite_task.id not in dependent_task.predecessors:
                    violations.append(self.create_violation(
                        task_id=dependent_task.id,
                        task_name=dependent_task.name,
                        violation_type="MissingGatingDependency",
                        severity="Error",
                        description=f"{dependent_task.name} must follow {prerequisite_task.name} per {authority} requirements",
                        suggested_fix=f"Add dependency: Task {dependent_task.id} → Task {prerequisite_task.id}",
                        rule_id=f"REG_GATE_{authority}_001"
                    ))
                
                # Check minimum gap
                if min_gap_days > 0:
                    # TODO: Calculate actual gap from dates
                    pass
        
        return violations
    
    def _normalize_name(self, name: str) -> str:
        """Normalize task name for matching"""
        return name.lower().replace(' ', '_').replace('-', '_')
```

---

### 5.2 OperationalSequenceValidator

**Responsibility**: Enforce logical operational prerequisites

```python
class OperationalSequenceValidator(Validator):
    """Validates operational task sequences"""
    
    def validate(self, project: ProjectData) -> List[ValidationViolation]:
        violations = []
        
        # Load operational sequence rules
        sequences = self.config.get('operational_sequences', [])
        
        # Build task lookup
        task_by_name = {self._normalize_name(t.name): t for t in project.tasks}
        
        for seq_rule in sequences:
            prereq_name = seq_rule['prerequisite']
            dependent_name = seq_rule['dependent']
            
            prereq_task = task_by_name.get(prereq_name)
            dependent_task = task_by_name.get(dependent_name)
            
            if not prereq_task or not dependent_task:
                continue
            
            # Check if dependency exists
            if prereq_task.id not in dependent_task.predecessors:
                violations.append(self.create_violation(
                    task_id=dependent_task.id,
                    task_name=dependent_task.name,
                    violation_type="MissingOperationalDependency",
                    severity=seq_rule.get('severity', 'Error'),
                    description=seq_rule['description'],
                    suggested_fix=f"Add dependency: Task {dependent_task.id} → Task {prereq_task.id}",
                    rule_id=seq_rule['rule_id']
                ))
        
        return violations
```

---

### 5.3 DurationBoundsValidator

**Responsibility**: Flag unrealistic durations

```python
class DurationBoundsValidator(Validator):
    """Validates task durations against benchmarks"""
    
    def validate(self, project: ProjectData) -> List[ValidationViolation]:
        violations = []
        
        # Load duration bounds
        bounds = self.config.get('duration_bounds', {})
        
        for task in project.tasks:
            task_key = self._normalize_name(task.name)
            
            if task_key not in bounds:
                continue
            
            bound_config = bounds[task_key]
            
            # Check for authority-specific bounds
            if 'authority_specific' in bound_config:
                if project.regulatory_authority in bound_config['authority_specific']:
                    bound_config = bound_config['authority_specific'][project.regulatory_authority]
            
            min_days = bound_config.get('min_days')
            max_days = bound_config.get('max_days')
            typical_days = bound_config.get('typical_days')
            warning_threshold = bound_config.get('warning_threshold_pct', 20)
            
            # Check if duration is outside bounds
            if min_days and task.duration_days < min_days:
                violations.append(self.create_violation(
                    task_id=task.id,
                    task_name=task.name,
                    violation_type="DurationTooShort",
                    severity="Warning",
                    description=f"Duration ({task.duration_days} days) is below minimum ({min_days} days)",
                    suggested_fix=f"Consider increasing duration to at least {min_days} days",
                    rule_id=f"DUR_MIN_{task_key}"
                ))
            
            if max_days and task.duration_days > max_days:
                violations.append(self.create_violation(
                    task_id=task.id,
                    task_name=task.name,
                    violation_type="DurationTooLong",
                    severity="Warning",
                    description=f"Duration ({task.duration_days} days) exceeds maximum ({max_days} days)",
                    suggested_fix=f"Review if duration can be reduced to {max_days} days or less",
                    rule_id=f"DUR_MAX_{task_key}"
                ))
            
            # Check if significantly different from typical
            if typical_days:
                deviation_pct = abs(task.duration_days - typical_days) / typical_days * 100
                if deviation_pct > warning_threshold:
                    violations.append(self.create_violation(
                        task_id=task.id,
                        task_name=task.name,
                        violation_type="DurationAtypical",
                        severity="Info",
                        description=f"Duration differs {deviation_pct:.1f}% from typical ({typical_days} days)",
                        suggested_fix=f"Typical duration is {typical_days} days - verify current estimate",
                        rule_id=f"DUR_TYP_{task_key}"
                    ))
        
        return violations
```

---

### 5.4 DependencyValidator

**Responsibility**: Validate graph structure and detect cycles

```python
import networkx as nx

class DependencyValidator(Validator):
    """Validates task dependencies and graph structure"""
    
    def validate(self, project: ProjectData) -> List[ValidationViolation]:
        violations = []
        
        # Build dependency graph
        G = nx.DiGraph()
        
        for task in project.tasks:
            G.add_node(task.id, name=task.name)
            for pred_id in task.predecessors:
                G.add_edge(pred_id, task.id)
        
        # Detect circular dependencies
        try:
            cycles = list(nx.simple_cycles(G))
            for cycle in cycles:
                cycle_names = [G.nodes[nid]['name'] for nid in cycle]
                violations.append(self.create_violation(
                    task_id=cycle[0],
                    task_name=G.nodes[cycle[0]]['name'],
                    violation_type="CircularDependency",
                    severity="Error",
                    description=f"Circular dependency detected: {' → '.join(cycle_names)}",
                    suggested_fix="Remove or reorder dependencies to break the cycle",
                    rule_id="DEP_CYCLE_001"
                ))
        except nx.NetworkXNoCycle:
            pass  # No cycles - good!
        
        # Check for orphaned tasks (no predecessors or successors)
        for task in project.tasks:
            if not task.predecessors and G.out_degree(task.id) == 0:
                if task.category != "Regulatory" or not task.is_mandatory:
                    violations.append(self.create_violation(
                        task_id=task.id,
                        task_name=task.name,
                        violation_type="OrphanedTask",
                        severity="Warning",
                        description="Task has no dependencies - verify it's correctly linked",
                        suggested_fix="Add appropriate predecessor or successor tasks",
                        rule_id="DEP_ORPHAN_001"
                    ))
        
        return violations
```

---

### 5.5 ChecklistCompletenessValidator

**Responsibility**: Ensure required tasks are present

```python
class ChecklistCompletenessValidator(Validator):
    """Validates checklist completeness"""
    
    def validate(self, project: ProjectData) -> List[ValidationViolation]:
        violations = []
        
        # Load checklist definitions
        checklists = self.config.get('checklists', {})
        
        # Build task name set
        task_names = {self._normalize_name(t.name) for t in project.tasks}
        
        for checklist_id, checklist_config in checklists.items():
            required_tasks = checklist_config.get('required_tasks', [])
            threshold = checklist_config.get('completeness_threshold_pct', 100)
            
            # Check how many required tasks are present
            present_count = sum(1 for req_task in required_tasks if req_task in task_names)
            total_count = len(required_tasks)
            completeness_pct = (present_count / total_count * 100) if total_count > 0 else 100
            
            if completeness_pct < threshold:
                missing_tasks = [t for t in required_tasks if t not in task_names]
                violations.append(self.create_violation(
                    task_id=0,  # Checklist violations aren't task-specific
                    task_name=f"{checklist_id.upper()} Checklist",
                    violation_type="IncompleteChecklist",
                    severity="Warning" if completeness_pct > 50 else "Error",
                    description=f"{checklist_id.title()} checklist is {completeness_pct:.0f}% complete (threshold: {threshold}%)",
                    suggested_fix=f"Add missing tasks: {', '.join(missing_tasks[:5])}{'...' if len(missing_tasks) > 5 else ''}",
                    rule_id=f"CHK_{checklist_id.upper()}_001"
                ))
        
        return violations
```

---

### 5.6 ParallelizationValidator

**Responsibility**: Identify parallelization opportunities

```python
class ParallelizationValidator(Validator):
    """Identifies tasks that could be parallelized"""
    
    def validate(self, project: ProjectData) -> List[ValidationViolation]:
        violations = []
        
        # Load parallelization rules
        parallel_rules = self.config.get('parallelization_rules', [])
        
        # Build task lookup
        task_by_name = {self._normalize_name(t.name): t for t in project.tasks}
        
        for rule in parallel_rules:
            task_name = rule['task']
            can_parallel_with = rule.get('can_parallel_with', [])
            
            main_task = task_by_name.get(task_name)
            if not main_task:
                continue
            
            for parallel_name in can_parallel_with:
                parallel_task = task_by_name.get(parallel_name)
                if not parallel_task:
                    continue
                
                # Check if tasks are currently sequential
                if (main_task.id in parallel_task.predecessors or 
                    parallel_task.id in main_task.predecessors):
                    
                    violations.append(self.create_violation(
                        task_id=main_task.id,
                        task_name=main_task.name,
                        violation_type="ParallelizationOpportunity",
                        severity="Info",
                        description=rule['suggestion'],
                        suggested_fix=f"Remove dependency between tasks {main_task.id} and {parallel_task.id}",
                        rule_id=rule['rule_id']
                    ))
        
        return violations
```

---

## 6. Configuration Structure

### 6.1 Master Rules Configuration

```yaml
# config/rules_config.yaml

version: 1.0
enabled_validators:
  - RegulatoryGatingValidator
  - OperationalSequenceValidator
  - DurationBoundsValidator
  - DependencyValidator
  - ChecklistCompletenessValidator
  - ParallelizationValidator

validator_order:
  - DependencyValidator          # Run first - must have valid graph
  - ChecklistCompletenessValidator  # Check required tasks present
  - RegulatoryGatingValidator    # Check regulatory sequences
  - OperationalSequenceValidator # Check operational logic
  - DurationBoundsValidator      # Check durations
  - ParallelizationValidator     # Optimization suggestions

severity_levels:
  Error: 
    blocks_validation: true
    requires_fix: true
  Warning:
    blocks_validation: false
    requires_review: true
  Info:
    blocks_validation: false
    requires_review: false
```

### 6.2 Authority-Specific Rules

```yaml
# config/authority_rules.yaml

FDA:
  rules:
    - id: FDA_REG_001
      type: regulatory_gating
      prerequisite: protocol_development
      dependent: ind_submission
      min_gap_days: 0
      
    - id: FDA_REG_002
      type: regulatory_gating
      prerequisite: ind_submission
      dependent: irb_submission
      min_gap_days: 30  # IND review period
      
    - id: FDA_REG_003
      type: regulatory_gating
      prerequisite: irb_submission
      dependent: siv
      min_gap_days: 45  # IRB review period

EMA:
  rules:
    - id: EMA_REG_001
      type: regulatory_gating
      prerequisite: protocol_development
      dependent: cta_submission
      min_gap_days: 0
      
    - id: EMA_REG_002
      type: regulatory_gating
      prerequisite: cta_submission
      dependent: ethics_submission
      min_gap_days: 60  # CTA review period
```

---

## 7. Validation Flow

### 7.1 Execution Sequence

```
1. Receive ProjectData from API
2. Load applicable rules from configuration
3. Initialize validators in priority order
4. Execute each validator:
   a. DependencyValidator (graph must be valid)
   b. ChecklistCompletenessValidator (required tasks present)
   c. RegulatoryGatingValidator (authority-specific rules)
   d. OperationalSequenceValidator (operational logic)
   e. DurationBoundsValidator (duration checks)
   f. ParallelizationValidator (optimization)
5. Aggregate violations
6. Sort by severity and task ID
7. Return ValidationResult
```

### 7.2 Performance Considerations

- **Caching**: Config files cached in memory (5 min TTL)
- **Early Exit**: Stop on critical errors if configured
- **Parallel Execution**: Independent validators can run in parallel
- **Incremental Validation**: Cache results for unchanged tasks

---

## 8. Extension Points

### 8.1 Adding New Validators

```python
# 1. Create new validator class
class CustomValidator(Validator):
    def validate(self, project: ProjectData) -> List[ValidationViolation]:
        # Implementation
        pass

# 2. Register in rules_engine.py
validators = [
    # ... existing validators
    CustomValidator(config)
]

# 3. Add configuration
# config/custom_rules.yaml
custom_rules:
  - rule_id: CUSTOM_001
    # ... rule definition
```

### 8.2 Adding New Rule Types

```yaml
# config/new_rule_type.yaml
resource_utilization:
  rules:
    - id: RES_001
      max_concurrent_tasks: 10
      warning_threshold: 8
      severity: Warning
```

### 8.3 Authority-Specific Extensions

```yaml
# config/authority_timelines.yaml
MHRA:  # Adding new authority
  rules:
    - id: MHRA_REG_001
      type: regulatory_gating
      prerequisite: protocol_development
      dependent: cta_submission
      min_gap_days: 0
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

```python
# tests/test_regulatory_validator.py

def test_fda_gating_violation():
    """Test FDA IND before IRB rule"""
    config = load_config('authority_timelines.yaml')
    validator = RegulatoryGatingValidator(config)
    
    project = ProjectData(
        regulatory_authority="FDA",
        tasks=[
            TaskData(id=1, name="IRB Submission", predecessors=[]),
            TaskData(id=2, name="IND Submission", predecessors=[1])  # Wrong order!
        ]
    )
    
    violations = validator.validate(project)
    assert len(violations) > 0
    assert violations[0].violation_type == "MissingGatingDependency"

def test_fda_gating_valid():
    """Test valid FDA sequence"""
    config = load_config('authority_timelines.yaml')
    validator = RegulatoryGatingValidator(config)
    
    project = ProjectData(
        regulatory_authority="FDA",
        tasks=[
            TaskData(id=1, name="IND Submission", predecessors=[]),
            TaskData(id=2, name="IRB Submission", predecessors=[1])  # Correct!
        ]
    )
    
    violations = validator.validate(project)
    assert len(violations) == 0
```

### 9.2 Integration Tests

```python
# tests/test_rules_engine_integration.py

def test_full_validation_flow():
    """Test complete validation with all validators"""
    engine = RulesEngine(config_manager)
    
    project = load_test_project('valid_fda_phase3.json')
    result = engine.validate(project)
    
    assert result.is_valid == True
    assert len(result.violations) == 0

def test_multiple_violations():
    """Test detection of multiple violation types"""
    engine = RulesEngine(config_manager)
    
    project = load_test_project('invalid_mixed.json')
    result = engine.validate(project)
    
    assert result.is_valid == False
    assert any(v.violation_type == "CircularDependency" for v in result.violations)
    assert any(v.violation_type == "MissingGatingDependency" for v in result.violations)
```

---

## 10. Future Enhancements

### 10.1 Machine Learning Integration

Rules engine could integrate with ML to:
- Learn organization-specific patterns
- Adapt rules based on historical outcomes
- Predict which violations are most critical

### 10.2 Real-Time Validation

- WebSocket connection for live validation
- Incremental validation as user edits
- Instant feedback in MS Project

### 10.3 Custom Rule Builder

- UI for creating custom rules without YAML editing
- Visual rule designer
- Rule testing sandbox

---

**End of Rules Engine Design Document**
