# Ilana PM Developer Guide

**Version:** 0.1.0
**Last Updated:** 2026-01-14
**Phase:** Phase 2 Complete

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Project Architecture](#project-architecture)
3. [Development Workflow](#development-workflow)
4. [Adding New Features](#adding-new-features)
5. [Configuration Management](#configuration-management)
6. [Testing Guidelines](#testing-guidelines)
7. [API Development](#api-development)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- **Python 3.11+** (3.13.7 recommended)
- **pip** (Python package manager)
- **Git** (for version control)
- **Text editor or IDE** (VS Code, PyCharm, etc.)

### Installation

1. **Clone the repository** (or navigate to project):
```bash
cd ~/Projects/ilana-pm
```

2. **Create virtual environment**:
```bash
python3 -m venv venv
```

3. **Activate virtual environment**:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

4. **Install dependencies**:
```bash
pip install -r requirements.txt
```

5. **Verify installation**:
```bash
python -m pytest
```

All tests should pass (90+ tests expected).

### Running Locally

**Start the API server**:
```bash
uvicorn backend.main:app --reload
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

**Test the API**:
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Ilana PM Intelligence API",
  "version": "0.1.0"
}
```

### Running Tests

**Run all tests**:
```bash
pytest
```

**Run with verbose output**:
```bash
pytest -v
```

**Run specific test file**:
```bash
pytest tests/test_validators.py
```

**Run specific test**:
```bash
pytest tests/test_validators.py::TestRegulatoryGating::test_missing_ind_submission
```

**Run with coverage**:
```bash
pytest --cov=backend --cov-report=html
```

Coverage report will be in `htmlcov/index.html`.

---

## Project Architecture

### Directory Structure

```
ilana-pm/
├── backend/                    # Python/FastAPI backend
│   ├── api/                    # REST API endpoints
│   │   ├── __init__.py
│   │   ├── health.py          # Health check endpoint
│   │   ├── validate.py        # Timeline validation API
│   │   ├── config.py          # Configuration API
│   │   ├── analytics.py       # Graph analytics API
│   │   └── advisory.py        # ML advisory API
│   ├── rules_engine/           # Validation rules
│   │   ├── __init__.py
│   │   ├── base_validator.py
│   │   ├── regulatory_gating.py
│   │   ├── duration_bounds.py
│   │   ├── operational_sequences.py
│   │   ├── dependency_validator.py
│   │   ├── checklist_validator.py
│   │   └── parallelization_validator.py
│   ├── graph_analytics/        # NetworkX dependency analysis
│   │   ├── __init__.py
│   │   └── dependency_graph.py
│   ├── ml_advisory/            # ML prediction services
│   │   ├── __init__.py
│   │   ├── duration_predictor.py
│   │   └── risk_scorer.py
│   ├── models/                 # Pydantic data models
│   │   ├── __init__.py
│   │   ├── timeline.py
│   │   └── validation.py
│   ├── config.py               # Configuration loader
│   └── main.py                 # FastAPI app entry point
├── config-templates/           # YAML configuration files
│   ├── authority_timelines.yaml
│   ├── task_ontology.yaml
│   ├── checklists.yaml
│   ├── duration_bounds.yaml
│   └── operational_sequences.yaml
├── tests/                      # Pytest test suite
│   ├── test_validators.py
│   ├── test_advanced_validators.py
│   ├── test_graph_analytics.py
│   ├── test_ml_advisory.py
│   ├── test_integration.py
│   └── test_models.py
├── docs/                       # Documentation
│   ├── developer-guide.md      # This file
│   ├── clinical-reference.md   # Clinical domain reference
│   └── deployment-guide.md     # Deployment instructions
├── requirements.txt            # Python dependencies
└── README.md                   # Project overview
```

### Core Components

#### 1. Data Models (`backend/models/`)

**Purpose**: Define the structure of clinical trial data.

**Key Models**:
- `Timeline`: Complete clinical trial timeline
- `Task`: Individual task with duration, category, phase
- `Dependency`: Predecessor/successor relationships
- `ValidationResult`: Validation output with issues

**Example**:
```python
from backend.models.timeline import Task, TaskCategory, StudyPhase

task = Task(
    id="T1",
    name="IND Submission",
    duration_days=60,
    category=TaskCategory.REGULATORY,
    phase=StudyPhase.PHASE_II,
    authority=RegulatoryAuthority.FDA,
    is_mandatory=True
)
```

#### 2. Rules Engine (`backend/rules_engine/`)

**Purpose**: Validate timelines against clinical trial best practices.

**Architecture**:
- `BaseValidator`: Abstract base class for all validators
- Concrete validators: Implement specific validation logic
- `RulesEngine`: Orchestrates all validators

**Validators**:
1. **Regulatory Gating**: Checks required regulatory approvals
2. **Duration Bounds**: Validates task durations against benchmarks
3. **Operational Sequences**: Verifies logical task order
4. **Dependency Validator**: Detects circular dependencies
5. **Checklist Validator**: Ensures required checklists are complete
6. **Parallelization Validator**: Identifies optimization opportunities

#### 3. Graph Analytics (`backend/graph_analytics/`)

**Purpose**: Analyze task dependencies using graph algorithms.

**Capabilities**:
- **Critical Path**: Calculate longest path through timeline
- **Slack Analysis**: Determine float/flexibility for each task
- **Parallelization**: Find tasks that can run concurrently

**Uses NetworkX** for graph algorithms.

#### 4. ML Advisory (`backend/ml_advisory/`)

**Purpose**: Provide intelligent recommendations.

**Services**:
- **Duration Predictor**: Predict task durations with confidence intervals
- **Risk Scorer**: Identify high-risk tasks with mitigation suggestions

**Note**: Phase 2 uses heuristic-based algorithms. Phase 5 will integrate trained ML models.

#### 5. API Endpoints (`backend/api/`)

**Purpose**: Expose backend functionality via REST API.

**Endpoints**:
- `/api/v1/health` - Health check
- `/api/v1/validate` - Timeline validation
- `/api/v1/config/*` - Configuration management
- `/api/v1/analytics/*` - Graph analytics
- `/api/v1/advisory/*` - ML advisory

#### 6. Configuration (`config-templates/`)

**Purpose**: Store domain knowledge in YAML files.

**Files**:
- `task_ontology.yaml`: 25 canonical clinical trial tasks
- `authority_timelines.yaml`: FDA, EMA, MHRA regulatory timelines
- `checklists.yaml`: Startup, SIV, Closeout checklists
- `duration_bounds.yaml`: Min/max durations by task type
- `operational_sequences.yaml`: Logical task ordering rules

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Write Code

Follow these principles:
- **Type hints**: Use Python type hints for all functions
- **Docstrings**: Document classes and methods
- **Validation**: Use Pydantic for data validation
- **Testing**: Write tests as you code

### 3. Run Tests

```bash
# Run tests
pytest

# Check coverage
pytest --cov=backend
```

### 4. Format Code

```bash
# Format with black
black backend/ tests/

# Check with flake8
flake8 backend/ tests/
```

### 5. Commit Changes

```bash
git add .
git commit -m "Add: Description of feature"
```

Commit message conventions:
- `Add:` - New feature
- `Fix:` - Bug fix
- `Update:` - Modify existing feature
- `Docs:` - Documentation changes
- `Test:` - Add/update tests

### 6. Run Full Test Suite

```bash
pytest -v
```

Ensure all tests pass before merging.

---

## Adding New Features

### Adding a New Validator

1. **Create validator file** in `backend/rules_engine/`:

```python
# backend/rules_engine/my_new_validator.py
from typing import List
from .base_validator import BaseValidator, ValidationIssue
from backend.models.timeline import Timeline

class MyNewValidator(BaseValidator):
    """Validates [description]"""

    @property
    def validator_name(self) -> str:
        return "My New Validator"

    def validate(self, timeline: Timeline) -> List[ValidationIssue]:
        """
        Validate timeline for [specific rule]

        Args:
            timeline: Timeline to validate

        Returns:
            List of validation issues found
        """
        issues = []

        # Validation logic here
        for task in timeline.tasks:
            if self._check_condition(task):
                issues.append(ValidationIssue(
                    rule_id="NEW-001",
                    severity="error",  # or "warning", "info"
                    category="my_category",
                    task_id=task.id,
                    message="Short description",
                    detail="Detailed explanation",
                    suggested_fix="How to fix it",
                    confidence=1.0
                ))

        return issues
```

2. **Register validator** in `backend/rules_engine/__init__.py`:

```python
from .my_new_validator import MyNewValidator

class RulesEngine:
    def __init__(self, config: dict):
        self.validators = [
            # ... existing validators ...
            MyNewValidator(config),
        ]
```

3. **Write tests** in `tests/test_validators.py`:

```python
def test_my_new_validator():
    """Test my new validator"""
    timeline = Timeline(...)  # Create test timeline
    validator = MyNewValidator({})
    issues = validator.validate(timeline)

    assert len(issues) > 0  # Should find issues
    assert issues[0].rule_id == "NEW-001"
```

4. **Update documentation** in `clinical-reference.md`.

### Adding a New API Endpoint

1. **Create endpoint** in appropriate API file (e.g., `backend/api/analytics.py`):

```python
@router.post("/analytics/my-endpoint")
async def my_new_endpoint(timeline: Timeline):
    """
    My new analytics endpoint

    Args:
        timeline: Clinical trial timeline

    Returns:
        Analysis results
    """
    # Implementation
    result = perform_analysis(timeline)

    return {
        "analysis": result,
        "metadata": {
            "task_count": len(timeline.tasks),
            "timestamp": datetime.now()
        }
    }
```

2. **Add input/output models** if needed in `backend/models/`:

```python
class MyAnalysisResult(BaseModel):
    """Result of my analysis"""
    score: float
    details: Dict[str, Any]
```

3. **Write integration tests** in `tests/test_integration.py`:

```python
def test_my_new_endpoint():
    """Test my new endpoint"""
    response = client.post("/api/v1/analytics/my-endpoint", json=timeline_data)
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
```

4. **Test via OpenAPI docs** at http://localhost:8000/docs.

### Adding Configuration Data

To add new tasks, checklists, or rules:

1. **Edit YAML file** in `config-templates/`:

```yaml
# config-templates/task_ontology.yaml
tasks:
  - id: NEW-001
    name: "My New Task"
    category: Regulatory
    typical_duration_days: 45
    min_duration_days: 30
    max_duration_days: 60
    is_mandatory: true
    description: "Description of task"
```

2. **Configuration loads automatically** on server start.

3. **Reload config** without restart:
```python
from backend.config import reload_config
reload_config()
```

4. **Test** that validators use the new configuration.

---

## Configuration Management

### YAML Configuration Files

Configuration is stored in `config-templates/` as YAML files.

**Loading Configuration**:
```python
from backend.config import load_config

config = load_config()

# Access configuration
tasks = config.get('task_ontology', [])
authorities = config.get('authorities', {})
```

**Configuration Structure**:
```python
{
    'authorities': {...},          # From authority_timelines.yaml
    'task_ontology': [...],        # From task_ontology.yaml
    'checklists': {...},           # From checklists.yaml
    'duration_bounds': [...],      # From duration_bounds.yaml
    'operational_sequences': [...] # From operational_sequences.yaml
}
```

### Modifying Configuration

1. Edit YAML file in `config-templates/`
2. Restart server OR call `reload_config()`
3. Test changes

**Example** - Adding a new authority:

```yaml
# config-templates/authority_timelines.yaml
authorities:
  PMDA:  # New authority
    name: "Pharmaceuticals and Medical Devices Agency (Japan)"
    regulatory_gates:
      - gate_id: PMDA-CTA
        name: "Clinical Trial Notification"
        typical_duration_days: 30
        blocking: true
```

---

## Testing Guidelines

### Test Organization

- `test_models.py`: Pydantic model validation
- `test_validators.py`: Basic validators
- `test_advanced_validators.py`: Complex validators
- `test_graph_analytics.py`: Graph algorithms
- `test_ml_advisory.py`: ML advisory services
- `test_integration.py`: API and multi-module workflows

### Writing Good Tests

**Unit Test Example**:
```python
def test_duration_bounds_validator():
    """Test duration bounds validator detects short durations"""
    # Arrange
    task = Task(
        id="T1",
        name="IND/CTA Submission",
        duration_days=15,  # Too short!
        category=TaskCategory.REGULATORY,
        phase=StudyPhase.PHASE_II,
        authority=RegulatoryAuthority.FDA
    )
    timeline = Timeline(
        study_name="Test",
        phase=StudyPhase.PHASE_II,
        authority=RegulatoryAuthority.FDA,
        tasks=[task],
        dependencies=[]
    )

    validator = DurationBoundsValidator(config)

    # Act
    issues = validator.validate(timeline)

    # Assert
    assert len(issues) > 0
    assert any("too short" in issue.message.lower() for issue in issues)
    assert issues[0].task_id == "T1"
```

**Integration Test Example**:
```python
def test_complete_validation_workflow():
    """Test full validation workflow"""
    # Arrange
    timeline_data = {...}  # Complete timeline JSON

    # Act
    response = client.post("/api/v1/validate", json=timeline_data)

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert result["total_tasks_analyzed"] == len(timeline_data["tasks"])
    assert "issues" in result
```

### Test Data Helpers

Create reusable test data:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_timeline():
    """Create sample timeline for testing"""
    return Timeline(
        study_name="Test Study",
        phase=StudyPhase.PHASE_II,
        authority=RegulatoryAuthority.FDA,
        tasks=[
            Task(id="T1", name="Task 1", ...),
            Task(id="T2", name="Task 2", ...)
        ],
        dependencies=[...]
    )

# Use in tests:
def test_with_fixture(sample_timeline):
    validator = MyValidator({})
    issues = validator.validate(sample_timeline)
    assert len(issues) >= 0
```

### Coverage Goals

- **Overall**: 80%+ coverage
- **Core modules**: 90%+ coverage
- **API endpoints**: Test all endpoints
- **Validators**: Test all rule paths

Check coverage:
```bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

---

## API Development

### FastAPI Basics

**Defining an endpoint**:
```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/my-endpoint")
async def my_endpoint(data: MyInputModel) -> MyOutputModel:
    """Endpoint description"""
    result = process(data)
    return result
```

**Request/Response Models**:
```python
from pydantic import BaseModel

class MyInputModel(BaseModel):
    field1: str
    field2: int

class MyOutputModel(BaseModel):
    result: str
    score: float
```

### Error Handling

```python
from fastapi import HTTPException

@router.post("/my-endpoint")
async def my_endpoint(data: MyInputModel):
    try:
        result = risky_operation(data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
```

### API Documentation

FastAPI auto-generates docs at `/docs`. Enhance with:

**Detailed docstrings**:
```python
@router.post("/validate")
async def validate_timeline(timeline: Timeline):
    """
    Validate a clinical trial timeline

    Runs all validation rules against the timeline and returns issues found.

    Args:
        timeline: Complete clinical trial timeline with tasks and dependencies

    Returns:
        ValidationResult with issues categorized by severity

    Raises:
        HTTPException: 400 if timeline is invalid, 500 if validation fails
    """
```

**Example responses**:
```python
@router.post(
    "/validate",
    responses={
        200: {
            "description": "Validation completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "warnings",
                        "issues": [...],
                        "error_count": 0,
                        "warning_count": 2
                    }
                }
            }
        },
        400: {"description": "Invalid timeline data"},
        500: {"description": "Validation failed"}
    }
)
```

---

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'backend'`

**Solution**:
```bash
# Make sure you're in the project root
cd ~/Projects/ilana-pm

# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. Configuration Not Loading

**Problem**: `⚠️  Config file not found: task_ontology.yaml`

**Solution**:
```bash
# Check config files exist
ls config-templates/

# Check file paths in backend/config.py
# Make sure config_dir points to correct location
```

#### 3. Tests Failing

**Problem**: Tests that previously passed now fail

**Solution**:
```bash
# Run tests with verbose output
pytest -v

# Run specific failing test
pytest tests/test_validators.py::test_name -v

# Check for:
# - Changed configuration
# - Modified validation rules
# - Updated dependencies
```

#### 4. Server Won't Start

**Problem**: `uvicorn` command fails

**Solution**:
```bash
# Check for syntax errors
python -m py_compile backend/main.py

# Check dependencies installed
pip list | grep fastapi

# Try with explicit path
python -m uvicorn backend.main:app --reload
```

#### 5. Circular Dependencies

**Problem**: Validation reports circular dependencies

**Solution**:
```python
# Use NetworkX to visualize
import networkx as nx
from backend.graph_analytics.dependency_graph import DependencyGraph

graph = DependencyGraph(timeline)
cycles = list(nx.simple_cycles(graph.graph))
print(f"Cycles found: {cycles}")
```

### Debugging Tips

**Enable debug logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Use FastAPI debugger**:
```python
# In endpoint
import pdb; pdb.set_trace()  # Breakpoint
```

**Test with curl**:
```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/sample_timeline.json
```

**Interactive testing**:
```bash
# Start Python REPL with backend loaded
python

>>> from backend.models.timeline import Timeline
>>> from backend.rules_engine import RulesEngine
>>> # Test interactively
```

---

## Code Style Guidelines

### Python Style

Follow **PEP 8** with these specifics:

- **Line length**: 88 characters (Black default)
- **Imports**: Grouped (stdlib, third-party, local)
- **Docstrings**: Google style
- **Type hints**: Required for all functions

**Example**:
```python
from typing import List, Optional
from backend.models.timeline import Timeline


def process_timeline(
    timeline: Timeline,
    strict_mode: bool = False,
    max_issues: Optional[int] = None
) -> List[ValidationIssue]:
    """
    Process timeline and return validation issues.

    Args:
        timeline: Timeline to process
        strict_mode: If True, treat warnings as errors
        max_issues: Maximum number of issues to return

    Returns:
        List of validation issues found

    Raises:
        ValueError: If timeline is invalid
    """
    if not timeline.tasks:
        raise ValueError("Timeline must have at least one task")

    # Implementation
    issues = []
    # ...
    return issues[:max_issues] if max_issues else issues
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `RegulatoryGatingValidator`)
- **Functions**: `snake_case` (e.g., `validate_timeline`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_DURATION_DAYS`)
- **Private**: `_leading_underscore` (e.g., `_internal_method`)

### Error Messages

Make error messages **actionable**:

```python
# Bad
raise ValueError("Invalid duration")

# Good
raise ValueError(
    f"Duration {duration} is outside valid range [{min_duration}, {max_duration}]. "
    f"Adjust duration or update configuration."
)
```

---

## Additional Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [NetworkX Documentation](https://networkx.org/)
- [Pytest Documentation](https://docs.pytest.org/)

### Project Documentation

- `README.md`: Project overview
- `docs/clinical-reference.md`: Clinical domain knowledge
- `docs/deployment-guide.md`: Deployment instructions
- `docs/MILESTONE_*.md`: Implementation milestones

### Getting Help

- **Issues**: Check `docs/` for troubleshooting guides
- **API Docs**: http://localhost:8000/docs (when server running)
- **Tests**: Look at existing tests for examples

---

## Appendix: Development Tools

### Recommended VS Code Extensions

- **Python**: Microsoft Python extension
- **Pylance**: Type checking and IntelliSense
- **Black Formatter**: Auto-formatting
- **GitLens**: Git integration

### Recommended PyCharm Plugins

- **Black**: Code formatting
- **Pydantic**: Enhanced Pydantic support
- **FastAPI**: FastAPI snippets

### Useful Commands

```bash
# Find TODO comments
grep -r "TODO" backend/

# Count lines of code
find backend -name "*.py" | xargs wc -l

# Check for unused imports
flake8 backend/ --select=F401

# Generate requirements.txt
pip freeze > requirements.txt

# Run specific test marker
pytest -m integration
```

---

**Document Version**: 1.0
**Author**: Ilana PM Development Team
**Last Review**: 2026-01-14

For questions or updates to this guide, please update this file and commit changes.
