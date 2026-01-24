# Environment Variables Setup Guide

## Quick Start

### Step 1: Generate Your JWT Secret Key

Run this command to generate a secure random key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

**Example output:**
```
X7vN2kP9mR5sT8wQ3uY6zB1cF4hJ7lK0nM9pS2vX5yA8dG1jL4oR7tU0wZ3bE6hK9m
```

**⚠️ IMPORTANT:**
- Save this key somewhere secure (password manager)
- Never commit it to git
- Use the same key in development and production (otherwise tokens won't work across environments)

---

## Local Development Setup

### Step 2: Create `.env` File

Copy the template and add your key:

```bash
cd backend
cp .env.example .env
```

### Step 3: Edit `.env` File

Open `backend/.env` and replace the placeholder:

```bash
# Before
JWT_SECRET_KEY=your-generated-secret-key-here

# After (use YOUR generated key)
JWT_SECRET_KEY=X7vN2kP9mR5sT8wQ3uY6zB1cF4hJ7lK0nM9pS2vX5yA8dG1jL4oR7tU0wZ3bE6hK9m
```

### Step 4: Verify It Works

The backend will automatically read from `.env` file when you run it locally.

**Test it:**
```bash
cd backend
python3 main.py
```

You should see:
```
🚀 Ilana PM Intelligence API starting up...
(no warning about JWT_SECRET_KEY)
```

If you see `⚠️ JWT_SECRET_KEY not set!` then the `.env` file is not being read correctly.

---

## Production Deployment

### Render Setup

1. **Go to your backend service** on Render dashboard
2. **Click "Environment" tab**
3. **Add environment variable:**
   - **Key:** `JWT_SECRET_KEY`
   - **Value:** (paste your generated key)
   - Click "Save Changes"

4. **Verify it's set:**
   - Render will automatically redeploy
   - Check logs for the startup message (no warning should appear)

### Azure App Service Setup

**Option A: Azure Portal (GUI)**
1. Go to Azure Portal → App Services → ilanapm-backend
2. Click "Configuration" (left sidebar)
3. Click "New application setting"
4. Name: `JWT_SECRET_KEY`
5. Value: (paste your generated key)
6. Click "OK" then "Save"

**Option B: Azure CLI (Command Line)**
```bash
az webapp config appsettings set \
  --name ilanapm-backend \
  --resource-group ilanapm \
  --settings JWT_SECRET_KEY="X7vN2kP9mR5sT8wQ3uY6zB1cF4hJ7lK0nM9pS2vX5yA8dG1jL4oR7tU0wZ3bE6hK9m"
```

---

## How the Code Uses the Secret Key

### Before (Hardcoded - Insecure)
```python
SECRET_KEY = "your-secret-key-change-in-production"
```

### After (Environment Variable - Secure)
```python
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    # Fallback for development only
    SECRET_KEY = "dev-secret-key-change-in-production"
    logger.warning("⚠️ JWT_SECRET_KEY not set!")
```

**How it works:**
1. Code tries to read `JWT_SECRET_KEY` from environment
2. If found → uses that (production/local with .env)
3. If not found → uses fallback dev key and shows warning

---

## Testing Environment Variables Locally

### Option 1: Using `.env` file (Recommended)

**Install python-dotenv:**
```bash
pip3 install python-dotenv
```

**Update `main.py` to load `.env`:**
```python
from dotenv import load_dotenv
load_dotenv()  # Add this line at the top of main.py
```

Now when you run locally, it will read from `.env` file.

### Option 2: Set environment variable manually

**macOS/Linux:**
```bash
export JWT_SECRET_KEY="X7vN2kP9mR5sT8wQ3uY6zB1cF4hJ7lK0nM9pS2vX5yA8dG1jL4oR7tU0wZ3bE6hK9m"
python3 main.py
```

**Windows:**
```cmd
set JWT_SECRET_KEY=X7vN2kP9mR5sT8wQ3uY6zB1cF4hJ7lK0nM9pS2vX5yA8dG1jL4oR7tU0wZ3bE6hK9m
python main.py
```

---

## Security Best Practices

### ✅ DO:
- Generate a unique, random key for each environment
- Store keys in environment variables
- Use password manager to backup keys
- Rotate keys periodically (every 6-12 months)
- Use different keys for development vs production (optional but recommended)

### ❌ DON'T:
- Commit `.env` file to git (already in `.gitignore`)
- Share keys in Slack/email/Discord
- Use simple/guessable keys like "secret123"
- Hardcode keys in source code
- Reuse keys across different applications

---

## Troubleshooting

### Problem: Warning "JWT_SECRET_KEY not set!"

**Cause:** Environment variable not configured

**Fix:**
- Local: Create `backend/.env` file with your key
- Render: Add environment variable in dashboard
- Azure: Add application setting in portal

### Problem: Tokens Invalid After Changing Key

**Cause:** JWT tokens are signed with the old key, can't verify with new key

**Fix:** All users must re-activate their licenses (tokens expire after 90 days anyway)

### Problem: Different keys in development vs production

**Symptom:** Tokens generated locally don't work in production

**Fix:** Use the same key everywhere, OR clearly separate dev/prod keys (users can't share tokens between environments)

---

## What Happens If Key Is Compromised?

If your secret key is leaked (committed to git, shared publicly):

1. **Immediate action:**
   - Generate a new key
   - Update environment variable everywhere (local, Render, Azure)
   - Redeploy backend

2. **Impact:**
   - All existing JWT tokens become invalid
   - All users must re-activate their licenses
   - Attackers can no longer forge tokens

3. **Prevention:**
   - Never commit `.env` to git (`.gitignore` protects you)
   - Use git secrets scanning (GitHub Advanced Security)
   - Rotate keys periodically

---

## Additional Environment Variables (Future Use)

Your `.env.example` file includes placeholders for:

- **Stripe:** Payment processing
- **WorkOS:** SSO integration
- **SendGrid:** Email notifications
- **Sentry:** Error tracking

You'll add these in later weeks as you implement those features.

---

## Summary

**For Local Development:**
```bash
# Generate key
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Create .env file
cd backend
cp .env.example .env
nano .env  # Edit and paste your key

# Run backend
python3 main.py
```

**For Production (Render):**
1. Render Dashboard → Environment tab
2. Add `JWT_SECRET_KEY` = (your generated key)
3. Save → Auto-redeploys

**Verification:**
- No warning in logs = ✅ Working
- Warning "JWT_SECRET_KEY not set" = ❌ Not configured

---

**Questions?** Check logs for warnings, verify `.env` file exists, confirm Render environment variable is set.
