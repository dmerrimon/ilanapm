# Quick Start: Deploy to Vercel

## Step-by-Step Checklist

### 1️⃣ Deploy Customer Portal (5 minutes)

1. Go to https://vercel.com/ and sign in with GitHub
2. Click **"Add New..." → "Project"**
3. Select repository: `dmerrimon/ilanapm`
4. Configure:
   - Project Name: `seleen-customer-portal`
   - Root Directory: `admin-portals/customer-portal` ⬅️ **Important!**
   - Framework: Next.js (auto-detected)
5. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL = https://ilanapm.onrender.com/api/v1
   ```
6. Click **"Deploy"** and wait 2-3 minutes
7. Copy your Vercel URL (e.g., `seleen-customer-portal.vercel.app`)

### 2️⃣ Deploy Founder Portal (5 minutes)

1. Click **"Add New..." → "Project"** again
2. Select repository: `dmerrimon/ilanapm`
3. Configure:
   - Project Name: `seleen-founder-portal`
   - Root Directory: `admin-portals/founder-portal` ⬅️ **Important!**
   - Framework: Next.js (auto-detected)
4. Add Environment Variable:
   ```
   NEXT_PUBLIC_API_URL = https://ilanapm.onrender.com/api/v1
   ```
5. Click **"Deploy"** and wait 2-3 minutes
6. Copy your Vercel URL (e.g., `seleen-founder-portal.vercel.app`)

### 3️⃣ Test Vercel Deployments (2 minutes)

**Customer Portal:**
- Visit: `https://[your-vercel-url]/login`
- Login: `admin@test.com` / `admin123`
- Should redirect to dashboard

**Founder Portal:**
- Visit: `https://[your-vercel-url]/login`
- Login: `founder@seleen.com` / `founder123`
- Should redirect to dashboard

### 4️⃣ Add Custom Domains in Vercel (2 minutes each)

**Customer Portal:**
1. Go to project → Settings → Domains
2. Add domain: `app.seleen.com` (or your choice)
3. Vercel shows: "Add CNAME record: app → cname.vercel-dns.com"

**Founder Portal:**
1. Go to project → Settings → Domains
2. Add domain: `admin.seleen.com` (or your choice)
3. Vercel shows: "Add CNAME record: admin → cname.vercel-dns.com"

### 5️⃣ Configure DNS in Squarespace (5 minutes)

1. Log into https://account.squarespace.com/
2. Go to your domain → DNS Settings
3. Add two CNAME records:

   **Customer Portal:**
   ```
   Type: CNAME
   Host: app
   Points to: cname.vercel-dns.com
   TTL: 3600
   ```

   **Founder Portal:**
   ```
   Type: CNAME
   Host: admin
   Points to: cname.vercel-dns.com
   TTL: 3600
   ```

4. Save and wait 10-30 minutes for DNS propagation

### 6️⃣ Update Backend CORS (5 minutes)

After deployment, update your backend with the actual Vercel URLs:

1. Edit `backend/main.py` line 113-123
2. Add your Vercel URLs to `allowed_origins`:
   ```python
   allowed_origins = [
       "https://app.seleen.com",       # Customer portal (custom domain)
       "https://admin.seleen.com",     # Founder portal (custom domain)
       "https://seleen-customer-portal.vercel.app",  # Vercel URL
       "https://seleen-founder-portal.vercel.app",   # Vercel URL
       "http://localhost:3000",        # Local dev
       "http://localhost:3001",        # Local dev
   ]
   ```
3. Commit and push:
   ```bash
   git add backend/main.py
   git commit -m "Add Vercel domains to CORS"
   git push origin main
   ```
4. Redeploy on Render (Manual Deploy → Deploy latest commit)

---

## What Domains Should I Use?

### Recommended Setup:
- **Customer Portal**: `app.seleen.com` (where customers log in)
- **Founder Portal**: `admin.seleen.com` (where you manage the system)
- **Main Website**: `seleen.com` or `www.seleen.com` (marketing site)

---

## Troubleshooting

**Build fails on Vercel:**
- ❌ Most common: Wrong Root Directory
- ✅ Fix: Go to Project Settings → General → Root Directory
- Must be: `admin-portals/customer-portal` or `admin-portals/founder-portal`

**Login works on localhost but not Vercel:**
- ❌ Backend CORS blocking requests
- ✅ Fix: Add Vercel URLs to backend CORS (Step 6 above)

**Domain shows "Not Found" error:**
- ❌ DNS not propagated yet
- ✅ Fix: Wait up to 1 hour, check with `nslookup app.seleen.com`

**SSL certificate not working:**
- ❌ DNS not fully propagated
- ✅ Fix: Wait 10-30 minutes, Vercel auto-provisions SSL

---

## Quick Test Commands

```bash
# Test DNS propagation
nslookup app.seleen.com
nslookup admin.seleen.com

# Test if sites are reachable
curl -I https://app.seleen.com
curl -I https://admin.seleen.com

# Test login API (should return token)
curl -X POST https://ilanapm.onrender.com/api/v1/portal/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}'
```

---

## Next Steps After Deployment

1. ✅ Test login on both production URLs
2. ✅ Verify dashboard loads data from backend
3. ✅ Create real admin accounts (not test users)
4. ✅ Set JWT_SECRET_KEY on Render (production security)
5. ✅ Add protected route middleware (prevent unauthorized access)
6. ✅ Set up monitoring (Vercel Analytics, Sentry, etc.)

---

## Need Help?

- Full guide: See `VERCEL_DEPLOYMENT_GUIDE.md`
- Vercel docs: https://vercel.com/docs
- DNS help: https://support.squarespace.com/hc/en-us/articles/360002101888
