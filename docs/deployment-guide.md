# Ilana PM Deployment Guide

**Version:** 0.1.0
**Last Updated:** 2026-01-14
**Phase:** Phase 2 Complete - Backend Ready for Deployment

---

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Local Development Deployment](#local-development-deployment)
3. [Production Deployment Options](#production-deployment-options)
4. [Azure Deployment (Recommended)](#azure-deployment-recommended)
5. [Docker Deployment](#docker-deployment)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Troubleshooting](#troubleshooting)

---

## Deployment Overview

### Architecture

**Current State (Phase 2)**:
```
┌─────────────────────────────────────────┐
│         FastAPI Backend                  │
│  ┌────────────────────────────────────┐ │
│  │   REST API Endpoints               │ │
│  │   - /api/v1/validate               │ │
│  │   - /api/v1/analytics/*            │ │
│  │   - /api/v1/advisory/*             │ │
│  │   - /api/v1/config/*               │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │   Business Logic                   │ │
│  │   - Rules Engine (6 validators)    │ │
│  │   - Graph Analytics (NetworkX)     │ │
│  │   - ML Advisory (heuristic-based)  │ │
│  └────────────────────────────────────┘ │
│  ┌────────────────────────────────────┐ │
│  │   Configuration                    │ │
│  │   - YAML config loader             │ │
│  │   - Task ontology (25 tasks)       │ │
│  │   - Authority timelines            │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**Future State (Phase 3-5)**:
- Desktop Add-in (C# VSTO)
- Web Add-in (TypeScript/React)
- Trained ML models
- Database for historical data

### Deployment Requirements

**Minimum Requirements**:
- **Python**: 3.11+
- **Memory**: 512 MB (1 GB recommended)
- **CPU**: 1 core (2 cores recommended)
- **Storage**: 100 MB
- **Network**: HTTPS support for production

**Dependencies**:
- FastAPI 0.104.1
- Uvicorn 0.24.0
- NetworkX 3.2.1
- PyYAML 6.0.1
- Pydantic 2.10.5

---

## Local Development Deployment

### Quick Start

1. **Navigate to project**:
```bash
cd ~/Projects/ilana-pm
```

2. **Activate virtual environment**:
```bash
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

3. **Start server**:
```bash
uvicorn backend.main:app --reload
```

4. **Verify**:
```bash
curl http://localhost:8000/api/v1/health
```

### Development Server Options

**Standard mode**:
```bash
uvicorn backend.main:app --reload
```

**Custom port**:
```bash
uvicorn backend.main:app --reload --port 8080
```

**External access** (for testing from other devices):
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode** (no auto-reload):
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Configuration for Development

Create `.env` file (optional):
```bash
# .env
ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
CONFIG_DIR=config-templates
```

Load in code:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    config_dir: str = "config-templates"

    class Config:
        env_file = ".env"
```

---

## Production Deployment Options

### Option 1: Cloud Platform (Recommended)

**Best for**: Production deployment with scaling needs

**Platforms**:
- **Azure App Service** (recommended for Microsoft ecosystem integration)
- **AWS Elastic Beanstalk**
- **Google Cloud Run**
- **Heroku**

**Pros**:
- Managed infrastructure
- Auto-scaling
- Built-in monitoring
- SSL/TLS included

**Cons**:
- Monthly costs
- Platform lock-in

### Option 2: Docker Container

**Best for**: Flexible deployment, any infrastructure

**Pros**:
- Consistent environment
- Portable
- Works on any host

**Cons**:
- Requires container orchestration for scaling

### Option 3: VM/Server

**Best for**: Simple deployment, existing infrastructure

**Pros**:
- Full control
- No container overhead

**Cons**:
- Manual scaling
- More maintenance

---

## Azure Deployment (Recommended)

### Prerequisites

- **Azure Account**: https://azure.microsoft.com/
- **Azure CLI**: `brew install azure-cli` or https://aka.ms/installazurecli

### Step 1: Prepare Application

1. **Create requirements.txt** (already exists):
```bash
cat requirements.txt
```

2. **Test locally**:
```bash
pytest  # Ensure all tests pass
```

3. **Create startup script** (`startup.sh`):
```bash
#!/bin/bash
cd /home/site/wwwroot
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Step 2: Create Azure Resources

1. **Login to Azure**:
```bash
az login
```

2. **Create resource group**:
```bash
az group create --name ilana-pm-rg --location eastus
```

3. **Create App Service Plan**:
```bash
az appservice plan create \
  --name ilana-pm-plan \
  --resource-group ilana-pm-rg \
  --sku B1 \
  --is-linux
```

4. **Create Web App**:
```bash
az webapp create \
  --resource-group ilana-pm-rg \
  --plan ilana-pm-plan \
  --name ilana-pm-api \
  --runtime "PYTHON:3.11"
```

### Step 3: Deploy Application

**Option A: Deploy from local git**:

1. **Initialize git deployment**:
```bash
az webapp deployment source config-local-git \
  --name ilana-pm-api \
  --resource-group ilana-pm-rg
```

2. **Get deployment URL**:
```bash
az webapp deployment list-publishing-credentials \
  --name ilana-pm-api \
  --resource-group ilana-pm-rg \
  --query scmUri \
  --output tsv
```

3. **Add Azure remote**:
```bash
git remote add azure <deployment-url>
```

4. **Push to Azure**:
```bash
git push azure main
```

**Option B: Deploy from GitHub** (recommended for CI/CD):

1. **Setup GitHub Actions** (`.github/workflows/azure-deploy.yml`):
```yaml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest

      - name: Deploy to Azure
        uses: azure/webapps-deploy@v2
        with:
          app-name: 'ilana-pm-api'
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

2. **Configure Azure credentials** in GitHub Secrets.

### Step 4: Configure Application

1. **Set startup command**:
```bash
az webapp config set \
  --resource-group ilana-pm-rg \
  --name ilana-pm-api \
  --startup-file "uvicorn backend.main:app --host 0.0.0.0 --port 8000"
```

2. **Configure environment variables**:
```bash
az webapp config appsettings set \
  --resource-group ilana-pm-rg \
  --name ilana-pm-api \
  --settings ENV=production LOG_LEVEL=INFO
```

3. **Enable HTTPS only**:
```bash
az webapp update \
  --resource-group ilana-pm-rg \
  --name ilana-pm-api \
  --https-only true
```

### Step 5: Verify Deployment

1. **Get app URL**:
```bash
az webapp show \
  --resource-group ilana-pm-rg \
  --name ilana-pm-api \
  --query defaultHostName \
  --output tsv
```

2. **Test health endpoint**:
```bash
curl https://<your-app-name>.azurewebsites.net/api/v1/health
```

3. **View logs**:
```bash
az webapp log tail \
  --resource-group ilana-pm-rg \
  --name ilana-pm-api
```

### Azure Deployment Best Practices

1. **Use deployment slots** for staging:
```bash
az webapp deployment slot create \
  --name ilana-pm-api \
  --resource-group ilana-pm-rg \
  --slot staging
```

2. **Enable Application Insights** for monitoring:
```bash
az monitor app-insights component create \
  --app ilana-pm-insights \
  --location eastus \
  --resource-group ilana-pm-rg \
  --application-type web
```

3. **Setup auto-scaling**:
```bash
az monitor autoscale create \
  --resource-group ilana-pm-rg \
  --resource ilana-pm-plan \
  --resource-type Microsoft.Web/serverfarms \
  --name autoscale-plan \
  --min-count 1 \
  --max-count 5 \
  --count 1
```

---

## Docker Deployment

### Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY config-templates/ ./config-templates/

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV ENV=production

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create docker-compose.yml

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
      - LOG_LEVEL=INFO
    volumes:
      - ./config-templates:/app/config-templates:ro
    restart: unless-stopped
```

### Build and Run

1. **Build image**:
```bash
docker build -t ilana-pm-api:latest .
```

2. **Run container**:
```bash
docker run -d -p 8000:8000 --name ilana-pm ilana-pm-api:latest
```

3. **Using docker-compose**:
```bash
docker-compose up -d
```

4. **View logs**:
```bash
docker logs -f ilana-pm
```

5. **Stop container**:
```bash
docker stop ilana-pm
```

### Docker Hub Deployment

1. **Tag image**:
```bash
docker tag ilana-pm-api:latest yourusername/ilana-pm-api:latest
```

2. **Push to Docker Hub**:
```bash
docker login
docker push yourusername/ilana-pm-api:latest
```

3. **Pull and run on server**:
```bash
docker pull yourusername/ilana-pm-api:latest
docker run -d -p 8000:8000 yourusername/ilana-pm-api:latest
```

---

## Environment Configuration

### Environment Variables

**Required**:
- `ENV`: Environment name (`development`, `staging`, `production`)

**Optional**:
- `DEBUG`: Enable debug mode (`true`, `false`)
- `LOG_LEVEL`: Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`)
- `CONFIG_DIR`: Configuration directory path (default: `config-templates`)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)

### Configuration Files

**Production deployment**:

1. **Copy config templates**:
```bash
cp -r config-templates /opt/ilana-pm/config
```

2. **Set permissions**:
```bash
chmod 644 /opt/ilana-pm/config/*.yaml
```

3. **Point app to config**:
```bash
export CONFIG_DIR=/opt/ilana-pm/config
```

### Secrets Management

**Do NOT commit**:
- API keys
- Database credentials
- Certificates

**Use**:
- **Azure**: Azure Key Vault
- **AWS**: AWS Secrets Manager
- **Docker**: Docker secrets
- **Local**: `.env` file (add to `.gitignore`)

---

## Monitoring and Logging

### Application Logging

**Configure logging** in `backend/main.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/ilana-pm/app.log')
    ]
)
```

### Health Check Endpoint

**Endpoint**: `GET /api/v1/health`

**Response**:
```json
{
  "status": "healthy",
  "service": "Ilana PM Intelligence API",
  "version": "0.1.0",
  "timestamp": "2026-01-14T10:30:00Z"
}
```

**Use for**:
- Load balancer health checks
- Monitoring tools (Datadog, New Relic)
- Uptime monitoring (UptimeRobot, Pingdom)

### Monitoring Metrics

**Key metrics to track**:

1. **API Response Time**
   - Target: < 500ms for validation
   - Target: < 200ms for config endpoints

2. **Error Rate**
   - Target: < 1% of requests

3. **Request Volume**
   - Track requests per minute
   - Monitor for anomalies

4. **Memory Usage**
   - Target: < 80% of allocated memory

5. **CPU Usage**
   - Target: < 70% average

### Azure Application Insights

**Enable**:
```python
# Install package
pip install opencensus-ext-azure

# Configure in main.py
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=<your-key>'
))
```

**View metrics**:
- Azure Portal → Application Insights
- Performance tab
- Failures tab
- Live Metrics

---

## Troubleshooting

### Common Deployment Issues

#### 1. Application Won't Start

**Symptoms**: Container/service fails to start

**Check**:
```bash
# View logs
docker logs ilana-pm  # Docker
az webapp log tail ...  # Azure

# Common causes:
# - Missing dependencies
# - Syntax errors
# - Port already in use
# - Config files missing
```

**Fix**:
```bash
# Test locally first
python -m uvicorn backend.main:app

# Check dependencies
pip install -r requirements.txt

# Verify config files
ls config-templates/
```

#### 2. 500 Internal Server Error

**Symptoms**: API returns 500 errors

**Check logs**:
```bash
# Azure
az webapp log tail --name ilana-pm-api --resource-group ilana-pm-rg

# Docker
docker logs ilana-pm

# Look for:
# - Python exceptions
# - Missing config files
# - File permission errors
```

**Common fixes**:
- Check config file paths
- Verify file permissions
- Check for missing dependencies

#### 3. CORS Errors

**Symptoms**: Browser blocks requests from web add-in

**Fix** in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. Slow Performance

**Symptoms**: API responses take > 1 second

**Check**:
- CPU usage (should be < 70%)
- Memory usage (should be < 80%)
- Network latency

**Optimize**:
- Enable caching for config data
- Use connection pooling
- Scale horizontally (add instances)

#### 5. Configuration Not Loading

**Symptoms**: Validators not working, tasks not found

**Check**:
```bash
# Verify config directory
ls $CONFIG_DIR

# Check file permissions
ls -la config-templates/

# Test config loading
python -c "from backend.config import load_config; print(load_config())"
```

**Fix**:
- Ensure CONFIG_DIR environment variable set
- Check file permissions (readable by app user)
- Validate YAML syntax

### Debugging Tools

**Local debugging**:
```bash
# Run with debug mode
DEBUG=true uvicorn backend.main:app --reload

# Use Python debugger
python -m pdb -m uvicorn backend.main:app
```

**Remote debugging (Azure)**:
```bash
# SSH into container
az webapp ssh --name ilana-pm-api --resource-group ilana-pm-rg

# View file system
ls /home/site/wwwroot

# Check Python version
python --version

# Test imports
python -c "import backend; print('OK')"
```

### Performance Tuning

**Uvicorn workers**:
```bash
# Multiple workers for production
uvicorn backend.main:app --workers 4 --host 0.0.0.0 --port 8000
```

**Gunicorn with Uvicorn workers** (recommended):
```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn backend.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## Rollback Procedures

### Azure Deployment Slots

**If deployment fails**:

1. **Swap back to previous slot**:
```bash
az webapp deployment slot swap \
  --resource-group ilana-pm-rg \
  --name ilana-pm-api \
  --slot staging \
  --action swap
```

### Docker Rollback

**If container fails**:

1. **Stop current container**:
```bash
docker stop ilana-pm
docker rm ilana-pm
```

2. **Run previous version**:
```bash
docker run -d -p 8000:8000 --name ilana-pm ilana-pm-api:v0.0.9
```

### Git Rollback

**If code issue discovered**:

1. **Revert to previous commit**:
```bash
git revert <commit-hash>
git push origin main
```

2. **Redeploy**:
```bash
# Azure
git push azure main

# Or trigger CI/CD pipeline
```

---

## Security Considerations

### HTTPS/TLS

**Production must use HTTPS**:
- Azure: Enable HTTPS-only in portal
- Docker: Use reverse proxy (nginx, Caddy)
- Custom domain: Use Let's Encrypt certificates

### API Keys (Future)

**When adding authentication**:
- Use environment variables for secrets
- Rotate keys regularly
- Implement rate limiting
- Use Azure Key Vault or AWS Secrets Manager

### CORS Configuration

**Production**:
```python
# Restrict origins
allow_origins=[
    "https://yourdomain.com",
    "https://ms-project-addin.yourdomain.com"
]
```

### Rate Limiting (Future Enhancement)

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/validate")
@limiter.limit("100/minute")
async def validate_timeline(request: Request, timeline: Timeline):
    ...
```

---

## Next Steps

### Phase 3: Desktop Add-in Integration

**Requirements**:
- Azure deployment complete
- Custom domain configured
- SSL/TLS certificate in place

**Changes needed**:
- Add authentication
- Add user management
- Add usage tracking

### Phase 4: Web Add-in Integration

**Requirements**:
- Same as Phase 3
- CORS configured for Office.js

### Phase 5: ML Model Deployment

**Requirements**:
- ML model training complete
- Model serving infrastructure (Azure ML, SageMaker)
- Model versioning and A/B testing

---

**Document Version**: 1.0
**Author**: Ilana PM DevOps Team
**Last Review**: 2026-01-14
**Next Review**: 2026-03-14 (before Phase 3)

For deployment questions or issues, refer to this guide or consult Azure documentation.
