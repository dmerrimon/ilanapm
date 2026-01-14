# Ilana PM

**Clinical Trial Timeline Intelligence Platform for Microsoft Project**

Ilana PM brings clinical trial expertise to Microsoft Project, providing:
- **Regulatory Validation**: Ensure timelines comply with FDA, EMA, MHRA requirements
- **Risk Assessment**: ML-powered predictions for task durations and delay risks
- **Intelligent Advisory**: Suggest optimizations and identify issues before they happen
- **Multi-Platform Support**: Desktop (VSTO) and Web (Office.js) add-ins

## Architecture

- **Backend**: Python/FastAPI intelligence layer with REST API
- **Rules Engine**: YAML-driven validation rules (6+ validators)
- **Graph Analytics**: NetworkX-based dependency analysis and critical path calculation
- **ML Advisory**: Duration prediction and risk scoring
- **Add-ins**: Thin clients for MS Project Desktop and Web

## Development Status

- ✅ Phase 1: Foundation (Weeks 1-4) - In Progress
- ⏳ Phase 2: Backend Intelligence (Weeks 5-8)
- ⏳ Phase 3: Desktop Add-in (Weeks 9-12)
- ⏳ Phase 4: Web Add-in (Weeks 13-16)
- ⏳ Phase 5: ML & Polish (Weeks 17-20)

## Getting Started

### Prerequisites
- Python 3.11+
- pip

### Installation

```bash
cd ~/Projects/ilana-pm
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Backend

```bash
uvicorn backend.main:app --reload
```

API available at: http://localhost:8000
API docs: http://localhost:8000/docs

### Running Tests

```bash
pytest
pytest --cov=backend  # With coverage report
```

## Project Structure

```
ilana-pm/
├── backend/                    # Python FastAPI intelligence layer
│   ├── api/                    # REST API endpoints
│   ├── rules_engine/           # Validation rules
│   ├── ml_advisory/            # ML prediction services
│   ├── graph_analytics/        # NetworkX dependency analysis
│   └── models/                 # Data models (Pydantic)
├── config-templates/           # YAML configuration files
├── tests/                      # Pytest test suite
├── docs/                       # Documentation
└── deployments/                # Azure deployment configs
```

## Documentation

- [Implementation Plan](/.claude/plans/eager-sauteeing-sifakis.md)
- [Developer Guide](docs/developer-guide.md) - Coming soon
- [Clinical Reference](docs/clinical-reference.md) - Coming soon

## License

Proprietary - All Rights Reserved

## Contact

Don Merriman - Founder
