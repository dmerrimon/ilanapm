# Seleen (formerly Ilana PM)

**Clinical Trial Timeline Intelligence Platform for Microsoft Project**

Seleen brings clinical trial expertise and intelligence to Microsoft Project, providing CPMs with:
- **Database-Driven Templates**: 6 comprehensive timeline templates (291 tasks, 75 dependencies)
- **Regulatory Validation**: Ensure timelines comply with FDA, EMA, MHRA, and 23 regulatory authorities
- **Intelligence Layer**: Signal extraction from trackers (TMF, Risk Log, Budget) with timeline correlation
- **Multi-Country Support**: 23-country calculator with regulatory-specific workflows
- **Desktop Add-in**: Full-featured VSTO add-in for MS Project

## Architecture

### Backend (Python/FastAPI)
- **REST API**: Template library, validation, intelligence endpoints
- **Database**: PostgreSQL (Render) with SQLite local development
- **Template System**: Database-backed timeline templates replacing YAML ontology
- **Intelligence Engine**: Variance detection, benchmark retrieval, signal correlation

### Desktop Add-in (C# VSTO)
- **Clinical Project Manager**: Unified wizard for study timeline generation
- **Template Library**: Load from database (TPL_001-TPL_005) or legacy API
- **Validation**: Real-time timeline validation with regulatory rules
- **Licensing**: FreshBooks-integrated seat-based licensing
- **Telemetry**: ML feedback loop for continuous improvement

## Quick Start

### Backend Setup (Mac/Linux)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run locally
uvicorn main:app --reload --port 8000
```

**API Available:**
- Local: http://localhost:8000
- Production: https://ilanapm.onrender.com
- API Docs: http://localhost:8000/docs

### Desktop Add-in Setup (Windows)

```bash
cd desktop-addin/IlanaPM.AddIn
# Open IlanaPM.AddIn.sln in Visual Studio
# Build → Rebuild Solution
# Run with MS Project installed
```

**Requirements:**
- Windows 10/11
- Visual Studio 2019/2022 with VSTO
- Microsoft Project (Desktop version)
- .NET Framework 4.8

## Timeline Templates

### Database Templates (Recommended)

| ID | Name | Tasks | Dependencies | Duration | Type |
|----|------|-------|--------------|----------|------|
| TPL_001 | Study Start-Up | 86 | 52 | 180 days | Study-level |
| TPL_002 | Study Implementation | 10 | 0 | 730 days | Study-level |
| TPL_003 | Study Closeout | 23 | 23 | 300 days | Study-level |
| TPL_004 | Site Activation | 34 | 0 | 90 days | Site-specific |
| TPL_005 | Site Closeout | 19 | 0 | 30 days | Site-specific |

**To generate a complete study timeline (119 tasks):** Select all three study-level templates (TPL_001 + TPL_002 + TPL_003) in Step 3 of Clinical Project Manager wizard.

### Legacy API Templates

- Full Study Timeline (90 tasks estimate)
- Site Startup, Site Implementation, Site Closeout
- Study Closeout

## Project Structure

```
seleen/
├── backend/                           # Python FastAPI backend
│   ├── api/                           # REST endpoints
│   ├── database/                      # SQLite + PostgreSQL
│   │   ├── migrations/                # Database migrations
│   │   └── feedback.db                # Local SQLite database
│   ├── intelligence/                  # Variance detection, benchmarks
│   └── main.py                        # Application entry point
│
├── desktop-addin/                     # C# VSTO add-in
│   └── IlanaPM.AddIn/
│       ├── Models/                    # Data models
│       ├── Services/                  # API client, template manager
│       ├── ClinicalProjectManagerForm.cs  # Main wizard
│       └── ThisAddIn.cs               # VSTO entry point
│
├── config-templates/                  # YAML configs (authorities, rules)
├── docs/                              # Documentation
└── Future Improvements Roadmap/       # Planned features
```

## Key Documentation

### Current Implementation
- **[Database Template Integration Status](desktop-addin/IlanaPM.AddIn/DATABASE_TEMPLATE_INTEGRATION_STATUS.md)** - Implementation details
- **[Testing Guide](desktop-addin/TESTING_DATABASE_TEMPLATES.md)** - How to test templates in MS Project
- **[Intelligence Layer Plan](SELEEN_INTELLIGENCE_LAYER_PLAN.md)** - Architecture for signal extraction and correlation

### API Documentation
- **[API Integration Guide](backend/API_INTEGRATION_GUIDE.md)** - REST API usage
- **[Deployment Guide](backend/DEPLOYMENT.md)** - Render deployment instructions
- **[FreshBooks Setup](backend/FRESHBOOKS_SETUP.md)** - Licensing integration

### Development Guides
- **[Environment Setup](backend/ENVIRONMENT_SETUP.md)** - Development environment configuration
- **[Testing License Guide](backend/TESTING_LICENSE_GUIDE.md)** - How to test licensing features

## Deployment

### Production (Render)
- **Web Service**: https://ilanapm.onrender.com
- **Database**: PostgreSQL (Basic-256mb)
- **Auto-deploy**: Enabled on `main` branch

### Local Development
- **Backend**: SQLite (backend/database/feedback.db)
- **Frontend**: Admin portals in admin-portals/

## Development Status

✅ **Completed:**
- Database-backed timeline templates (5 templates, 172 tasks, 75 dependencies)
- Desktop add-in with Clinical Project Manager wizard
- Multi-country calculator (23 regulatory authorities)
- PostgreSQL deployment on Render
- FreshBooks licensing integration
- Variance detection and benchmark retrieval

🚧 **In Progress:**
- Intelligence layer: Signal extraction from trackers (TMF, Risk Log)
- Signal-to-timeline correlation engine
- Leadership dashboard (Director/VP escalation views)

🔮 **Planned:**
- Web add-in (Office.js for MS Project Online)
- Portfolio-level intelligence (cross-study pattern detection)
- Custom template creation (org-specific templates)
- Template versioning and import/export

## Testing

**Desktop Add-in:**
See [TESTING_DATABASE_TEMPLATES.md](desktop-addin/TESTING_DATABASE_TEMPLATES.md) for detailed test cases.

**Backend API:**
```bash
cd backend
pytest
pytest --cov=backend
```

**Manual Testing:**
1. Start backend: `uvicorn main:app --reload --port 8000`
2. Test templates: `curl http://localhost:8000/api/v1/templates/library` (should return 5 templates)
3. Open MS Project → Seleen → Clinical Project Manager
4. In Step 3, check all three study-level templates:
   - DB: Study Start-Up (86 tasks)
   - DB: Study Implementation (10 tasks)
   - DB: Study Closeout (23 tasks)
5. Generate and verify 119 tasks created (86 + 10 + 23)

## Contributing

This is a private project for Bordeaux Laboratories / Ilana Immersive LLC.

## License

Proprietary. All rights reserved.

---

**Contact:** Don Merriman - Bordeaux Laboratories / Ilana Immersive LLC
**Repository:** https://github.com/dmerrimon/ilanapm
