# Render Deployment Guide

## Why Render?
- **Zero-config Python deployments** - automatically detects FastAPI
- **Free tier available** - perfect for development/testing
- **Much simpler than Azure** - no app service plans, app settings, or complex configuration
- **Automatic HTTPS** - free SSL certificates included
- **Fast deployments** - typically under 2 minutes

## Quick Start (5 minutes)

### 1. Push Code to GitHub
```bash
cd /Users/donmerriman/Projects/ilana-pm
git add backend/render.yaml backend/RENDER_DEPLOYMENT.md
git commit -m "Add Render deployment configuration"
git push origin main
```

### 2. Create Render Account
- Go to https://render.com
- Sign up with GitHub (easiest)

### 3. Deploy from Dashboard
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `ilana-pm`
3. Render will auto-detect the `render.yaml` configuration
4. Click **"Create Web Service"**

That's it! Render will:
- Detect Python 3.11
- Install dependencies from `requirements.txt`
- Start gunicorn with uvicorn workers
- Provide you with a URL like `https://ilanapm-api.onrender.com`

### 4. Update Desktop Add-in
Once deployed, update the API URL in your desktop add-in:

**File**: `desktop-addin/IlanaPM.AddIn/Services/ApiClient.cs`

```csharp
// Change from:
private const string API_BASE_URL = "https://ilanapm.azurewebsites.net";

// To:
private const string API_BASE_URL = "https://ilanapm-api.onrender.com";
```

### 5. Test Endpoints
```bash
# Health check
curl https://ilanapm-api.onrender.com/health

# API docs
open https://ilanapm-api.onrender.com/docs
```

## Configuration Details

### render.yaml
The `render.yaml` file configures:
- **Runtime**: Python 3.11
- **Region**: Oregon (or change to Ohio for East US)
- **Plan**: Free tier (upgradeable)
- **Workers**: 2 gunicorn workers with uvicorn
- **Health Check**: `/health` endpoint

### Free Tier Limitations
- **Spins down after 15 minutes of inactivity**
- **Cold start takes ~30 seconds** when waking up
- **750 hours/month free** (enough for development)

To upgrade to paid ($7/month):
- No spin-down
- More RAM/CPU
- Custom domains

## Troubleshooting

### Deployment Failed
Check build logs in Render dashboard - usually missing dependencies in requirements.txt

### 503 Errors
- Free tier services spin down after inactivity
- First request after sleep takes 30 seconds
- Subsequent requests are instant

### YAML Config Files Not Found
Ensure backend/config/ directory is committed to Git:
```bash
git add backend/config/*.yaml
git commit -m "Add config files"
git push
```

## Advantages Over Azure Web App

| Feature | Render | Azure Web App |
|---------|--------|---------------|
| Setup Time | 2 minutes | 30+ minutes |
| Configuration | render.yaml only | App settings, deployment slots, PYTHONPATH, startup commands |
| Free Tier | Yes | No (requires Basic plan $13+/month) |
| Auto-deploy from Git | Yes, automatic | Manual or GitHub Actions setup |
| Python Detection | Automatic | Manual configuration required |
| Logs | Real-time in dashboard | Azure CLI or portal only |
| Local Development Match | Identical | Often different behavior |

## Next Steps

1. Deploy to Render using steps above
2. Update desktop add-in API URL
3. Test Phase 1 features on Windows VM
4. If Render free tier is too slow (30s cold starts), upgrade to paid ($7/month)

## Alternative: Railway ($5/month credit)

If you prefer no cold starts even on free tier:
1. Go to https://railway.app
2. Connect GitHub repo
3. Railway auto-detects Python and deploys
4. No configuration file needed!
