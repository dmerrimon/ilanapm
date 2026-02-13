# Seleen Intelligence Layer - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the Seleen Intelligence Layer across all environments: Production, Staging, and Local Development.

**Architecture Components:**
- **Backend API**: Python/FastAPI REST API
- **Database**: SQLite (local/dev) or PostgreSQL (production)
- **Frontend Web Portal**: Next.js (app.seleen.io)
- **Desktop Add-in**: MS Project C# add-in
- **Background Jobs**: Python cron jobs for daily intelligence refresh
- **File Storage**: Local filesystem or cloud (S3/Azure Blob)

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Desktop Add-in Deployment](#desktop-add-in-deployment)
7. [Background Jobs Setup](#background-jobs-setup)
8. [Security Configuration](#security-configuration)
9. [Monitoring and Logging](#monitoring-and-logging)
10. [Backup and Recovery](#backup-and-recovery)
11. [Scaling Considerations](#scaling-considerations)
12. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements (Development)

- **OS**: Linux, macOS, or Windows 10+
- **Python**: 3.9+
- **Node.js**: 18+
- **RAM**: 4 GB
- **Disk**: 10 GB free space
- **Database**: SQLite (included)

### Production Requirements

- **OS**: Linux (Ubuntu 22.04 LTS recommended)
- **Python**: 3.11+
- **Node.js**: 18 LTS or 20 LTS
- **RAM**: 8 GB minimum, 16 GB recommended
- **CPU**: 4 cores minimum, 8 cores recommended
- **Disk**: 50 GB SSD minimum, 100 GB recommended
- **Database**: PostgreSQL 15+ or SQLite 3.40+
- **Web Server**: Nginx or Apache
- **Process Manager**: systemd or supervisor
- **SSL/TLS**: Let's Encrypt or commercial certificate

### Desktop Add-in Requirements

- **OS**: Windows 10+ or Windows Server 2019+
- **MS Project**: MS Project 2016, 2019, or Microsoft 365 Apps
- **.NET Framework**: 4.7.2 or higher
- **RAM**: 4 GB minimum
- **Disk**: 500 MB for add-in installation

---

## Environment Setup

### 1. Production Environment

**Infrastructure:**
- Cloud provider: AWS, Azure, or GCP
- Application server: EC2, Azure VM, or Compute Engine
- Database server: RDS PostgreSQL, Azure Database, or Cloud SQL
- File storage: S3, Azure Blob Storage, or Cloud Storage
- CDN: CloudFront, Azure CDN, or Cloud CDN

**Environment Variables:**

```bash
# Production environment variables
export ENV=production
export DEBUG=false

# Database
export DATABASE_URL=postgresql://user:pass@host:5432/seleen_prod
export DATABASE_POOL_SIZE=20
export DATABASE_MAX_OVERFLOW=40

# API Configuration
export API_BASE_URL=https://api.seleen.io
export API_PORT=8000
export API_WORKERS=4
export API_KEY_PREFIX=sk_live_

# Frontend
export NEXT_PUBLIC_API_URL=https://api.seleen.io/v1
export NEXT_PUBLIC_APP_URL=https://app.seleen.io

# File Storage
export STORAGE_TYPE=s3
export AWS_REGION=us-east-1
export AWS_S3_BUCKET=seleen-tracker-uploads
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...

# Security
export SECRET_KEY=<generate-with-openssl-rand-hex-32>
export ALLOWED_ORIGINS=https://app.seleen.io,https://www.seleen.io
export CORS_MAX_AGE=3600

# Monitoring
export SENTRY_DSN=https://...@sentry.io/...
export LOG_LEVEL=info
export LOG_FILE=/var/log/seleen/api.log

# Email (for notifications)
export SMTP_HOST=smtp.sendgrid.net
export SMTP_PORT=587
export SMTP_USER=apikey
export SMTP_PASSWORD=SG...
export FROM_EMAIL=noreply@seleen.io

# Rate Limiting
export RATE_LIMIT_PER_MINUTE=100
export RATE_LIMIT_PER_DAY=10000

# Background Jobs
export ENABLE_BACKGROUND_JOBS=true
export DAILY_REFRESH_TIME=00:00
```

### 2. Staging Environment

```bash
# Staging environment variables (similar to production but with staging prefixes)
export ENV=staging
export DEBUG=true

export DATABASE_URL=postgresql://user:pass@host:5432/seleen_staging
export API_BASE_URL=https://api-staging.seleen.io
export NEXT_PUBLIC_API_URL=https://api-staging.seleen.io/v1
export NEXT_PUBLIC_APP_URL=https://app-staging.seleen.io
export API_KEY_PREFIX=sk_test_

# Use separate S3 bucket or subdirectory
export AWS_S3_BUCKET=seleen-tracker-uploads-staging
```

### 3. Local Development Environment

```bash
# Local development environment variables
export ENV=development
export DEBUG=true

# Use SQLite for local development
export DATABASE_URL=sqlite:///database/feedback.db

export API_BASE_URL=http://localhost:8000
export API_PORT=8000
export NEXT_PUBLIC_API_URL=http://localhost:8000/v1
export NEXT_PUBLIC_APP_URL=http://localhost:3000

# Local file storage
export STORAGE_TYPE=local
export LOCAL_STORAGE_PATH=./uploads

export LOG_LEVEL=debug
export ENABLE_BACKGROUND_JOBS=false
```

---

## Database Setup

### Local Development (SQLite)

```bash
# 1. Ensure database directory exists
mkdir -p backend/database

# 2. Apply all migrations
cd backend
python scripts/apply_migrations.py

# 3. Verify schema
sqlite3 database/feedback.db ".schema"

# 4. (Optional) Load sample data
python scripts/load_sample_data.py
```

### Production (PostgreSQL)

```bash
# 1. Create production database
sudo -u postgres psql
CREATE DATABASE seleen_prod;
CREATE USER seleen_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE seleen_prod TO seleen_user;
\q

# 2. Set DATABASE_URL environment variable
export DATABASE_URL=postgresql://seleen_user:secure_password@localhost:5432/seleen_prod

# 3. Apply migrations (convert SQLite migrations to PostgreSQL)
cd backend
python scripts/apply_migrations_postgres.py

# 4. Verify schema
psql -U seleen_user -d seleen_prod -c "\dt"

# 5. Create database backup user
sudo -u postgres psql
CREATE USER seleen_backup WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE seleen_prod TO seleen_backup;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO seleen_backup;
```

### Migration Strategy

**SQLite → PostgreSQL Migration Script:**

```python
# scripts/apply_migrations_postgres.py

import psycopg2
import os
from pathlib import Path

def convert_sqlite_to_postgres(sql: str) -> str:
    """Convert SQLite SQL to PostgreSQL SQL"""
    # Replace SQLite types with PostgreSQL types
    sql = sql.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
    sql = sql.replace("TEXT", "VARCHAR")
    sql = sql.replace("REAL", "NUMERIC")
    sql = sql.replace("datetime('now')", "CURRENT_TIMESTAMP")
    sql = sql.replace("date('now')", "CURRENT_DATE")

    # Replace SQLite functions
    sql = sql.replace("IFNULL", "COALESCE")

    return sql

def apply_migrations():
    """Apply all migrations to PostgreSQL"""
    db_url = os.getenv("DATABASE_URL")

    if not db_url or not db_url.startswith("postgresql"):
        raise ValueError("DATABASE_URL must be set to PostgreSQL connection string")

    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    # Get all migration files
    migrations_dir = Path(__file__).parent.parent / "database" / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    for migration_file in migration_files:
        print(f"Applying {migration_file.name}...")

        sql = migration_file.read_text()

        # Convert SQLite SQL to PostgreSQL
        sql_postgres = convert_sqlite_to_postgres(sql)

        try:
            cursor.execute(sql_postgres)
            conn.commit()
            print(f"✓ {migration_file.name} applied successfully")
        except Exception as e:
            print(f"✗ {migration_file.name} failed: {e}")
            conn.rollback()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    apply_migrations()
```

---

## Backend Deployment

### 1. Install Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install production dependencies
pip install gunicorn uvicorn[standard] psycopg2-binary python-dotenv
```

### 2. Configure Application

```bash
# Create .env file with production settings
cat > .env << EOF
ENV=production
DATABASE_URL=${DATABASE_URL}
API_BASE_URL=https://api.seleen.io
SECRET_KEY=${SECRET_KEY}
# ... (copy all production environment variables)
EOF
```

### 3. Run Backend (Production)

**Option A: systemd Service (Recommended)**

```bash
# Create systemd service file
sudo nano /etc/systemd/system/seleen-api.service
```

```ini
[Unit]
Description=Seleen Intelligence Layer API
After=network.target postgresql.service

[Service]
Type=notify
User=seleen
Group=seleen
WorkingDirectory=/opt/seleen/backend
Environment="PATH=/opt/seleen/backend/venv/bin"
EnvironmentFile=/opt/seleen/backend/.env
ExecStart=/opt/seleen/backend/venv/bin/gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/seleen/access.log \
    --error-logfile /var/log/seleen/error.log \
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable seleen-api
sudo systemctl start seleen-api

# Check status
sudo systemctl status seleen-api

# View logs
sudo journalctl -u seleen-api -f
```

**Option B: Docker Deployment**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn uvicorn[standard]

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

```bash
# Build and run
docker build -t seleen-api:latest .
docker run -d --name seleen-api \
    -p 8000:8000 \
    --env-file .env \
    -v /opt/seleen/database:/app/database \
    -v /opt/seleen/logs:/app/logs \
    seleen-api:latest

# Check logs
docker logs -f seleen-api
```

### 4. Configure Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/seleen-api

upstream seleen_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.seleen.io;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.seleen.io;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.seleen.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.seleen.io/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Logging
    access_log /var/log/nginx/seleen-api-access.log;
    error_log /var/log/nginx/seleen-api-error.log;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Proxy Settings
    location / {
        proxy_pass http://seleen_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health Check Endpoint
    location /health {
        proxy_pass http://seleen_backend/health;
        access_log off;
    }

    # File Upload (larger body size)
    client_max_body_size 10M;
}
```

```bash
# Enable site and reload Nginx
sudo ln -s /etc/nginx/sites-available/seleen-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Frontend Deployment

### 1. Install Dependencies

```bash
cd frontend

# Install dependencies
npm install --production

# Build for production
npm run build
```

### 2. Deploy to Production

**Option A: Node.js Server**

```bash
# Run Next.js production server
npm start

# Or with PM2 process manager
npm install -g pm2
pm2 start npm --name "seleen-frontend" -- start
pm2 save
pm2 startup
```

**Option B: Static Export + CDN**

```bash
# Build static export
npm run build
npm run export

# Deploy to S3 + CloudFront
aws s3 sync out/ s3://seleen-frontend-prod --delete
aws cloudfront create-invalidation --distribution-id E123456 --paths "/*"
```

**Option C: Vercel/Netlify (Recommended for Next.js)**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

### 3. Configure Nginx for Frontend

```nginx
# /etc/nginx/sites-available/seleen-frontend

server {
    listen 80;
    server_name app.seleen.io;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.seleen.io;

    ssl_certificate /etc/letsencrypt/live/app.seleen.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.seleen.io/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # Proxy to Next.js server
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## Desktop Add-in Deployment

### 1. Build Add-in

```bash
cd desktop-addin/IlanaPM.AddIn

# Restore NuGet packages
nuget restore IlanaPM.AddIn.sln

# Build release version
msbuild IlanaPM.AddIn.sln /p:Configuration=Release /p:Platform="Any CPU"
```

### 2. Create Installer

**Using ClickOnce:**

```xml
<!-- IlanaPM.AddIn.csproj -->
<PropertyGroup>
  <PublishUrl>https://downloads.seleen.io/addin/</PublishUrl>
  <InstallUrl>https://downloads.seleen.io/addin/</InstallUrl>
  <ProductName>Seleen Intelligence Layer Add-in for MS Project</ProductName>
  <PublisherName>Seleen</PublisherName>
  <ApplicationRevision>1</ApplicationRevision>
  <ApplicationVersion>1.0.0.%2a</ApplicationVersion>
  <UseApplicationTrust>false</UseApplicationTrust>
  <PublishWizardCompleted>true</PublishWizardCompleted>
  <BootstrapperEnabled>true</BootstrapperEnabled>
</PropertyGroup>
```

```bash
# Publish ClickOnce deployment
msbuild /target:publish /p:Configuration=Release
```

**Using WiX Toolset (Advanced):**

```xml
<!-- Product.wxs -->
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="Seleen MS Project Add-in"
           Language="1033" Version="1.0.0.0"
           Manufacturer="Seleen" UpgradeCode="PUT-GUID-HERE">

    <Package InstallerVersion="200" Compressed="yes"
             InstallScope="perUser" />

    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate EmbedCab="yes" />

    <Feature Id="ProductFeature" Title="Seleen Add-in" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
  </Product>

  <Fragment>
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="AppDataFolder">
        <Directory Id="INSTALLFOLDER" Name="Seleen" />
      </Directory>
    </Directory>
  </Fragment>

  <Fragment>
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="IlanaPMAddIn" Guid="PUT-GUID-HERE">
        <File Source="$(var.IlanaPM.AddIn.TargetPath)" KeyPath="yes" />
        <RegistryValue Root="HKCU"
                       Key="Software\Microsoft\Office\MSProject\Addins\IlanaPM.AddIn"
                       Name="LoadBehavior" Value="3" Type="integer" />
      </Component>
    </ComponentGroup>
  </Fragment>
</Wix>
```

```bash
# Build MSI installer
candle Product.wxs
light -out SeleeenAddIn.msi Product.wixobj
```

### 3. Distribute Add-in

**Via Web Download:**

```bash
# Upload to download server
aws s3 cp SeleeenAddIn.msi s3://seleen-downloads/addin/SeleeenAddIn.msi
aws s3 cp setup.exe s3://seleen-downloads/addin/setup.exe
```

**Distribution URL:** `https://downloads.seleen.io/addin/setup.exe`

**Installation Instructions (for CPMs):**

1. Download installer from `https://app.seleen.io/downloads/addin`
2. Run `setup.exe`
3. Follow installation wizard
4. Restart MS Project
5. Look for "Seleen" ribbon in MS Project
6. Click "Settings" → Enter API key
7. Click "Sync Timeline" to test connection

---

## Background Jobs Setup

### 1. Daily Intelligence Refresh Job

```bash
# Add to crontab
crontab -e
```

```cron
# Run daily intelligence refresh at midnight
0 0 * * * cd /opt/seleen/backend && /opt/seleen/backend/venv/bin/python3 scripts/daily_intelligence_refresh.py >> /var/log/seleen/cron.log 2>&1

# Cleanup old logs weekly
0 3 * * 0 find /var/log/seleen -name "*.log" -mtime +30 -delete
```

### 2. Background Job Monitoring

```bash
# Create monitoring script
cat > /opt/seleen/scripts/check_cron_status.sh << 'EOF'
#!/bin/bash
# Check if daily refresh completed successfully today

LOG_FILE="/var/log/seleen/daily_intelligence_refresh.log"
TODAY=$(date +%Y-%m-%d)

if grep -q "$TODAY.*SUCCESS" "$LOG_FILE"; then
    echo "✓ Daily refresh completed successfully"
    exit 0
else
    echo "✗ Daily refresh failed or not run today"
    exit 1
fi
EOF

chmod +x /opt/seleen/scripts/check_cron_status.sh

# Add to monitoring (e.g., Datadog, New Relic)
# Run every hour to verify daily job completed
0 * * * * /opt/seleen/scripts/check_cron_status.sh || curl -X POST https://monitoring.seleen.io/alert
```

### 3. Alternative: systemd Timer

```ini
# /etc/systemd/system/seleen-daily-refresh.service
[Unit]
Description=Seleen Daily Intelligence Refresh
After=network.target postgresql.service

[Service]
Type=oneshot
User=seleen
Group=seleen
WorkingDirectory=/opt/seleen/backend
Environment="PATH=/opt/seleen/backend/venv/bin"
EnvironmentFile=/opt/seleen/backend/.env
ExecStart=/opt/seleen/backend/venv/bin/python3 scripts/daily_intelligence_refresh.py
StandardOutput=append:/var/log/seleen/daily_refresh.log
StandardError=append:/var/log/seleen/daily_refresh_error.log
```

```ini
# /etc/systemd/system/seleen-daily-refresh.timer
[Unit]
Description=Run Seleen Daily Intelligence Refresh at midnight
Requires=seleen-daily-refresh.service

[Timer]
OnCalendar=daily
OnCalendar=*-*-* 00:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable seleen-daily-refresh.timer
sudo systemctl start seleen-daily-refresh.timer

# Check timer status
sudo systemctl list-timers --all | grep seleen

# Manually trigger job
sudo systemctl start seleen-daily-refresh.service

# View logs
sudo journalctl -u seleen-daily-refresh.service -f
```

---

## Security Configuration

### 1. API Key Management

```python
# backend/security/api_keys.py

import secrets
import hashlib
from datetime import datetime

def generate_api_key(prefix: str = "sk_live") -> str:
    """Generate secure API key"""
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"

def hash_api_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()

# Generate keys for new organization
api_key = generate_api_key("sk_live")
api_key_hash = hash_api_key(api_key)

# Store hash in database, give key to user once
print(f"API Key (show to user once): {api_key}")
print(f"Store in database: {api_key_hash}")
```

### 2. Rate Limiting

```python
# backend/middleware/rate_limit.py

from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Apply to API routes
@limiter.limit("100/minute")
@router.post("/trackers/upload")
async def upload_tracker(request: Request, ...):
    # ...
    pass

@limiter.limit("1000/hour")
@router.get("/dashboard/leadership")
async def get_leadership_dashboard(request: Request, ...):
    # ...
    pass
```

### 3. Input Validation

```python
# backend/validation/schemas.py

from pydantic import BaseModel, Field, validator
import re

class TrackerUploadRequest(BaseModel):
    org_id: str = Field(..., min_length=3, max_length=100)
    project_id: str = Field(..., min_length=3, max_length=100)
    tracker_type: str = Field(..., regex="^(risk_log|tmf_completeness|budget|vendor)$")

    @validator('org_id', 'project_id')
    def validate_id_format(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('IDs must contain only alphanumeric, underscore, hyphen')
        return v

    @validator('tracker_type')
    def validate_tracker_type(cls, v):
        allowed_types = ['risk_log', 'tmf_completeness', 'budget', 'vendor']
        if v not in allowed_types:
            raise ValueError(f'Invalid tracker type. Allowed: {allowed_types}')
        return v
```

### 4. SQL Injection Prevention

```python
# Always use parameterized queries
cursor.execute(
    "SELECT * FROM signals WHERE org_id = ? AND project_id = ?",
    (org_id, project_id)  # Parameters
)

# NEVER concatenate user input
# BAD: cursor.execute(f"SELECT * FROM signals WHERE org_id = '{org_id}'")
```

### 5. CORS Configuration

```python
# backend/main.py

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.seleen.io",
        "https://www.seleen.io"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600
)
```

### 6. File Upload Security

```python
# backend/file_validation.py

import magic
from pathlib import Path

ALLOWED_MIME_TYPES = [
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
    'application/vnd.ms-excel',  # .xls
    'text/csv'  # .csv
]

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

def validate_uploaded_file(file_bytes: bytes, filename: str) -> bool:
    """Validate uploaded file"""
    # Check file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {len(file_bytes)} bytes (max: {MAX_FILE_SIZE})")

    # Check MIME type
    mime = magic.Magic(mime=True)
    detected_mime = mime.from_buffer(file_bytes)

    if detected_mime not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Invalid file type: {detected_mime}")

    # Check file extension
    allowed_extensions = ['.xlsx', '.xls', '.csv']
    file_ext = Path(filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise ValueError(f"Invalid file extension: {file_ext}")

    return True
```

---

## Monitoring and Logging

### 1. Application Logging

```python
# backend/logging_config.py

import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logging():
    """Configure application logging"""

    # Create logger
    logger = logging.getLogger('seleen')
    logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        '/var/log/seleen/api.log',
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=10
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_format)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
```

### 2. Health Check Endpoint

```python
# backend/api/health.py

from fastapi import APIRouter, HTTPException
import sqlite3
from datetime import datetime
import psutil

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring

    Returns:
    - Status: ok/degraded/down
    - Database connectivity
    - Disk space
    - Memory usage
    """
    health_status = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }

    # Database check
    try:
        conn = sqlite3.connect("database/feedback.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {e}"
        health_status["status"] = "degraded"

    # Disk space check
    disk = psutil.disk_usage('/')
    disk_free_gb = disk.free / (1024**3)
    health_status["checks"]["disk_free_gb"] = round(disk_free_gb, 2)

    if disk_free_gb < 5:
        health_status["status"] = "degraded"
        health_status["checks"]["disk"] = "warning: low disk space"
    else:
        health_status["checks"]["disk"] = "ok"

    # Memory check
    memory = psutil.virtual_memory()
    memory_available_gb = memory.available / (1024**3)
    health_status["checks"]["memory_available_gb"] = round(memory_available_gb, 2)

    if memory_available_gb < 1:
        health_status["status"] = "degraded"
        health_status["checks"]["memory"] = "warning: low memory"
    else:
        health_status["checks"]["memory"] = "ok"

    if health_status["status"] != "ok":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
```

### 3. Prometheus Metrics

```python
# backend/metrics.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Request counters
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Request duration
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Active signals gauge
active_signals_gauge = Gauge(
    'active_signals_total',
    'Total active signals',
    ['org_id', 'severity']
)

# Tracker uploads counter
tracker_uploads_total = Counter(
    'tracker_uploads_total',
    'Total tracker uploads',
    ['org_id', 'tracker_type', 'status']
)

# Middleware to track metrics
@app.middleware("http")
async def track_metrics(request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

### 4. Error Tracking (Sentry)

```python
# backend/main.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENV", "production"),
    integrations=[
        FastApiIntegration(),
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
    ],
    traces_sample_rate=0.1,  # 10% of requests
    send_default_pii=False
)
```

---

## Backup and Recovery

### 1. Database Backup

**SQLite Backup:**

```bash
#!/bin/bash
# /opt/seleen/scripts/backup_database.sh

BACKUP_DIR="/opt/seleen/backups"
DB_PATH="/opt/seleen/backend/database/feedback.db"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/feedback_db_$DATE.db"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"

# Compress backup
gzip "$BACKUP_FILE"

# Delete backups older than 30 days
find "$BACKUP_DIR" -name "feedback_db_*.db.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

**PostgreSQL Backup:**

```bash
#!/bin/bash
# /opt/seleen/scripts/backup_postgres.sh

BACKUP_DIR="/opt/seleen/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/seleen_prod_$DATE.sql"

# Create backup
pg_dump -U seleen_user -d seleen_prod -F c -f "$BACKUP_FILE"

# Compress
gzip "$BACKUP_FILE"

# Upload to S3 (optional)
aws s3 cp "$BACKUP_FILE.gz" "s3://seleen-backups/database/$DATE/"

# Delete local backups older than 7 days
find "$BACKUP_DIR" -name "seleen_prod_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
```

**Automated Backups (cron):**

```cron
# Backup database daily at 2 AM
0 2 * * * /opt/seleen/scripts/backup_database.sh >> /var/log/seleen/backup.log 2>&1
```

### 2. Restore Database

**SQLite Restore:**

```bash
# Stop application
sudo systemctl stop seleen-api

# Restore from backup
cp /opt/seleen/backups/feedback_db_20260213_020000.db.gz /tmp/
gunzip /tmp/feedback_db_20260213_020000.db.gz
cp /tmp/feedback_db_20260213_020000.db /opt/seleen/backend/database/feedback.db

# Restart application
sudo systemctl start seleen-api
```

**PostgreSQL Restore:**

```bash
# Stop application
sudo systemctl stop seleen-api

# Drop and recreate database
sudo -u postgres psql -c "DROP DATABASE seleen_prod;"
sudo -u postgres psql -c "CREATE DATABASE seleen_prod OWNER seleen_user;"

# Restore from backup
gunzip /opt/seleen/backups/seleen_prod_20260213_020000.sql.gz
pg_restore -U seleen_user -d seleen_prod -c /opt/seleen/backups/seleen_prod_20260213_020000.sql

# Restart application
sudo systemctl start seleen-api
```

### 3. Disaster Recovery Plan

1. **RPO (Recovery Point Objective)**: 24 hours (daily backups)
2. **RTO (Recovery Time Objective)**: 4 hours

**Recovery Steps:**

1. Provision new server (cloud provider console or IaC)
2. Install dependencies (Python, PostgreSQL, Nginx)
3. Clone application repository
4. Restore database from backup
5. Configure environment variables
6. Start services
7. Verify health check endpoint
8. Update DNS records
9. Monitor for errors

**Recovery Script:**

```bash
#!/bin/bash
# disaster_recovery.sh

set -e

echo "Starting disaster recovery..."

# 1. Install dependencies
sudo apt-get update
sudo apt-get install -y python3.11 python3-pip postgresql-15 nginx

# 2. Clone application
cd /opt
sudo git clone https://github.com/seleen/backend.git seleen
cd seleen/backend

# 3. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Restore database
aws s3 cp s3://seleen-backups/database/latest/seleen_prod.sql.gz /tmp/
gunzip /tmp/seleen_prod.sql.gz
sudo -u postgres psql -c "CREATE DATABASE seleen_prod;"
pg_restore -U seleen_user -d seleen_prod /tmp/seleen_prod.sql

# 5. Configure environment
cp .env.production .env

# 6. Start services
sudo systemctl enable seleen-api
sudo systemctl start seleen-api
sudo systemctl enable nginx
sudo systemctl start nginx

# 7. Verify
curl -f http://localhost:8000/health || exit 1

echo "Disaster recovery completed!"
```

---

## Scaling Considerations

### 1. Horizontal Scaling

**Load Balancer Configuration:**

```nginx
# /etc/nginx/nginx.conf

upstream seleen_backend_cluster {
    least_conn;  # Load balancing method

    server 10.0.1.10:8000 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8000 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 max_fails=3 fail_timeout=30s;

    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.seleen.io;

    location / {
        proxy_pass http://seleen_backend_cluster;
        # ... (rest of proxy config)
    }
}
```

### 2. Database Scaling

**Read Replicas (PostgreSQL):**

```python
# backend/database/connection.py

from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Master (write operations)
MASTER_DB_URL = "postgresql://user:pass@master.db.seleen.io:5432/seleen_prod"
master_engine = create_engine(
    MASTER_DB_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40
)

# Read replica (read operations)
REPLICA_DB_URL = "postgresql://user:pass@replica.db.seleen.io:5432/seleen_prod"
replica_engine = create_engine(
    REPLICA_DB_URL,
    poolclass=QueuePool,
    pool_size=50,
    max_overflow=100
)

def get_db_connection(read_only: bool = False):
    """Get database connection (master or replica)"""
    if read_only:
        return replica_engine.connect()
    else:
        return master_engine.connect()
```

### 3. Caching Strategy

```python
# backend/cache/redis_cache.py

import redis
import json
from typing import Optional

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

def get_cached_dashboard(org_id: str) -> Optional[dict]:
    """Get cached dashboard data"""
    cache_key = f"dashboard:leadership:{org_id}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    return None

def set_cached_dashboard(org_id: str, dashboard_data: dict, ttl: int = 900):
    """Cache dashboard data (15 minutes TTL)"""
    cache_key = f"dashboard:leadership:{org_id}"
    redis_client.setex(
        cache_key,
        ttl,
        json.dumps(dashboard_data)
    )

def invalidate_dashboard_cache(org_id: str):
    """Invalidate dashboard cache after tracker upload"""
    cache_key = f"dashboard:leadership:{org_id}"
    redis_client.delete(cache_key)
```

### 4. Auto-Scaling (AWS Example)

```yaml
# cloudformation/autoscaling.yaml

Resources:
  SeleeenASG:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      MinSize: 2
      MaxSize: 10
      DesiredCapacity: 2
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      LaunchTemplate:
        LaunchTemplateId: !Ref SeleeenLaunchTemplate
        Version: !GetAtt SeleeenLaunchTemplate.LatestVersionNumber
      TargetGroupARNs:
        - !Ref SeleeenTargetGroup

  SeleeenScaleUpPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AutoScalingGroupName: !Ref SeleeenASG
      PolicyType: TargetTrackingScaling
      TargetTrackingConfiguration:
        PredefinedMetricSpecification:
          PredefinedMetricType: ASGAverageCPUUtilization
        TargetValue: 70.0
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Error:** `sqlite3.OperationalError: database is locked`

**Solution:**
```bash
# Check for stale connections
lsof /opt/seleen/backend/database/feedback.db

# Kill processes holding locks
kill -9 <PID>

# Or use WAL mode for better concurrency
sqlite3 /opt/seleen/backend/database/feedback.db "PRAGMA journal_mode=WAL;"
```

#### 2. API Not Responding

**Error:** `Connection refused on port 8000`

**Solution:**
```bash
# Check if service is running
sudo systemctl status seleen-api

# Check logs
sudo journalctl -u seleen-api -n 100

# Check port binding
sudo netstat -tlnp | grep 8000

# Restart service
sudo systemctl restart seleen-api
```

#### 3. Tracker Upload Failing

**Error:** `Column mapping not found`

**Solution:**
```bash
# Verify column mapping exists in database
sqlite3 database/feedback.db "SELECT * FROM tracker_column_mappings WHERE org_id='org_123';"

# If missing, Account Admin must configure tracker in web portal
# app.seleen.io → Account Management → Tracker Configuration
```

#### 4. Daily Refresh Not Running

**Error:** `No health snapshots generated today`

**Solution:**
```bash
# Check cron job
crontab -l | grep daily_intelligence_refresh

# Check cron logs
tail -f /var/log/seleen/cron.log

# Manually run job
cd /opt/seleen/backend
/opt/seleen/backend/venv/bin/python3 scripts/daily_intelligence_refresh.py

# Check systemd timer (if using systemd)
sudo systemctl status seleen-daily-refresh.timer
sudo journalctl -u seleen-daily-refresh.service -n 50
```

#### 5. High Memory Usage

**Error:** `Out of memory errors`

**Solution:**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -n 10

# Reduce Gunicorn workers
# Edit /etc/systemd/system/seleen-api.service
# Change --workers 4 to --workers 2

# Add swap space
sudo dd if=/dev/zero of=/swapfile bs=1G count=4
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

#### 6. SSL Certificate Expired

**Error:** `SSL certificate verification failed`

**Solution:**
```bash
# Check certificate expiration
openssl x509 -in /etc/letsencrypt/live/api.seleen.io/fullchain.pem -noout -dates

# Renew Let's Encrypt certificate
sudo certbot renew

# Reload Nginx
sudo systemctl reload nginx

# Setup auto-renewal (cron)
0 3 * * * certbot renew --quiet && systemctl reload nginx
```

---

## Maintenance Checklist

### Daily

- [ ] Check API health endpoint: `curl https://api.seleen.io/health`
- [ ] Verify daily intelligence refresh completed
- [ ] Review error logs: `tail -f /var/log/seleen/error.log`

### Weekly

- [ ] Review disk space usage: `df -h`
- [ ] Check database size: `du -sh /opt/seleen/backend/database`
- [ ] Review slow query logs
- [ ] Update dependencies: `pip list --outdated`

### Monthly

- [ ] Review and rotate logs
- [ ] Database vacuum/optimize: `sqlite3 database/feedback.db "VACUUM;"`
- [ ] Review security patches: `sudo apt-get update && sudo apt-get upgrade`
- [ ] Test backup restoration
- [ ] Review API rate limits and adjust if needed

### Quarterly

- [ ] Update SSL certificates (if not using auto-renewal)
- [ ] Review and update documentation
- [ ] Performance benchmarking
- [ ] Disaster recovery drill

---

## Support and Resources

### Documentation

- **API Reference**: `https://docs.seleen.io/api`
- **User Guide**: `https://docs.seleen.io/guide`
- **GitHub**: `https://github.com/seleen/backend`

### Contact

- **Technical Support**: support@seleen.io
- **Emergency Hotline**: +1-800-SELEEN-911 (for production outages)
- **Slack Community**: seleen-users.slack.com

### Monitoring Dashboards

- **Application**: https://grafana.seleen.io
- **Infrastructure**: https://datadog.seleen.io
- **Logs**: https://kibana.seleen.io

---

**Document Version**: 1.0
**Last Updated**: 2026-02-13
**Author**: Seleen DevOps Team
