# Vercel Deployment Guide - Customer & Founder Portals

## Overview
This guide walks you through deploying both admin portals to Vercel with custom domains managed by Squarespace.

---

## Part 1: Deploy Customer Portal to Vercel

### Step 1: Install Vercel CLI (Optional but recommended)
```bash
npm install -g vercel
```

### Step 2: Deploy Customer Portal via Vercel Dashboard

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/
   - Sign in with your GitHub account

2. **Create New Project**
   - Click "Add New..." → "Project"
   - Click "Import Git Repository"
   - Select your repository: `dmerrimon/ilanapm`
   - Click "Import"

3. **Configure Customer Portal Project**
   - **Project Name**: `seleen-customer-portal` (or your preferred name)
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: Click "Edit" → Select `admin-portals/customer-portal`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)

4. **Environment Variables**
   Click "Environment Variables" and add:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://ilanapm.onrender.com/api/v1
   Environment: Production, Preview, Development (select all)
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build to complete
   - You'll get a URL like: `seleen-customer-portal.vercel.app`

---

## Part 2: Deploy Founder Portal to Vercel

### Step 1: Create Second Vercel Project

1. **Go back to Vercel Dashboard**
   - Click "Add New..." → "Project"
   - Import the same repository: `dmerrimon/ilanapm`

2. **Configure Founder Portal Project**
   - **Project Name**: `seleen-founder-portal` (or your preferred name)
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: Click "Edit" → Select `admin-portals/founder-portal`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)

3. **Environment Variables**
   Add the same environment variable:
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://ilanapm.onrender.com/api/v1
   Environment: Production, Preview, Development (select all)
   ```

4. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for build to complete
   - You'll get a URL like: `seleen-founder-portal.vercel.app`

---

## Part 3: Configure Custom Domains (Squarespace DNS)

### Recommended Domain Setup
- **Customer Portal**: `app.seleen.com` or `portal.seleen.com`
- **Founder Portal**: `admin.seleen.com` or `founder.seleen.com`

### Step 1: Add Domain to Customer Portal in Vercel

1. **In Vercel Dashboard**
   - Go to your Customer Portal project
   - Click "Settings" → "Domains"
   - Enter your desired domain (e.g., `app.seleen.com`)
   - Click "Add"

2. **Vercel will show you DNS records to add:**
   ```
   Type: CNAME
   Name: app (or your subdomain)
   Value: cname.vercel-dns.com
   ```

### Step 2: Add Domain to Founder Portal in Vercel

1. **In Vercel Dashboard**
   - Go to your Founder Portal project
   - Click "Settings" → "Domains"
   - Enter your desired domain (e.g., `admin.seleen.com`)
   - Click "Add"

2. **Vercel will show you DNS records to add:**
   ```
   Type: CNAME
   Name: admin (or your subdomain)
   Value: cname.vercel-dns.com
   ```

### Step 3: Configure DNS in Squarespace

1. **Log into Squarespace**
   - Go to https://account.squarespace.com/
   - Navigate to your domain settings

2. **Access DNS Settings**
   - Click on your domain (seleen.com)
   - Click "DNS Settings" or "Advanced DNS"

3. **Add CNAME Records**

   **For Customer Portal (app.seleen.com):**
   - Click "Add Record"
   - Type: `CNAME`
   - Host: `app`
   - Data/Value: `cname.vercel-dns.com`
   - TTL: `3600` (default)
   - Save

   **For Founder Portal (admin.seleen.com):**
   - Click "Add Record"
   - Type: `CNAME`
   - Host: `admin`
   - Data/Value: `cname.vercel-dns.com`
   - TTL: `3600` (default)
   - Save

4. **Wait for DNS Propagation**
   - DNS changes can take 5-60 minutes to propagate
   - Vercel will automatically detect when DNS is configured
   - SSL certificates will be automatically provisioned

---

## Part 4: Update Backend CORS Settings

Your FastAPI backend needs to allow requests from your new Vercel domains.

### Update backend/main.py CORS origins:

```python
# Add your Vercel domains to allowed origins
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://app.seleen.com",           # Customer portal
    "https://admin.seleen.com",         # Founder portal
    "https://seleen-customer-portal.vercel.app",  # Vercel preview URL
    "https://seleen-founder-portal.vercel.app",   # Vercel preview URL
]
```

### Commit and push the CORS update:
```bash
git add backend/main.py
git commit -m "Add Vercel domains to CORS allowed origins"
git push origin main
```

### Redeploy backend on Render:
- Go to your Render dashboard
- Click "Manual Deploy" → "Deploy latest commit"
- Wait for deployment to complete

---

## Part 5: Test Your Deployments

### Test Customer Portal
1. Visit `https://app.seleen.com/login` (or your Vercel URL)
2. Login with: `admin@test.com` / `admin123`
3. Verify you can access the dashboard
4. Check that API calls work (dashboard loads data)

### Test Founder Portal
1. Visit `https://admin.seleen.com/login` (or your Vercel URL)
2. Login with: `founder@seleen.com` / `founder123`
3. Verify you can access the dashboard
4. Check that API calls work

---

## Part 6: Vercel CLI Deployment (Alternative Method)

If you prefer using the CLI:

### Customer Portal
```bash
cd admin-portals/customer-portal
vercel --prod
# Follow prompts:
# - Link to existing project or create new
# - Set root directory if needed
```

### Founder Portal
```bash
cd admin-portals/founder-portal
vercel --prod
# Follow prompts
```

---

## Troubleshooting

### Build Fails on Vercel
- Check build logs in Vercel dashboard
- Ensure `package.json` and `package-lock.json` are committed
- Verify root directory is set correctly

### DNS Not Working
- Wait up to 1 hour for DNS propagation
- Use `nslookup app.seleen.com` to check DNS status
- Ensure CNAME points to `cname.vercel-dns.com` (not your Vercel project URL)

### Authentication Fails
- Check browser console for errors
- Verify `NEXT_PUBLIC_API_URL` is set correctly in Vercel
- Ensure backend CORS includes your Vercel domains
- Check that backend is running on Render

### SSL Certificate Issues
- Vercel automatically provisions SSL certificates
- This can take 5-10 minutes after DNS propagation
- Certificate will auto-renew

---

## Production Checklist

- [ ] Customer portal deployed to Vercel
- [ ] Founder portal deployed to Vercel
- [ ] Environment variables configured (NEXT_PUBLIC_API_URL)
- [ ] Custom domains added in Vercel
- [ ] DNS CNAME records added in Squarespace
- [ ] DNS propagation complete (test with nslookup)
- [ ] SSL certificates provisioned (https:// works)
- [ ] Backend CORS updated with Vercel domains
- [ ] Backend redeployed on Render
- [ ] Customer portal login tested
- [ ] Founder portal login tested
- [ ] API calls working from both portals

---

## Domain Suggestions

### Option 1: Subdomain-based (Recommended)
- Customer Portal: `app.seleen.com`
- Founder Portal: `admin.seleen.com`
- Main site: `seleen.com` or `www.seleen.com`

### Option 2: Path-based (Alternative)
- Customer Portal: `portal.seleen.com`
- Founder Portal: `founder.seleen.com`

### Option 3: Separate domains
- Customer Portal: `portal.seleen.com`
- Founder Portal: `admin.seleen.io` (if you have multiple domains)

---

## Next Steps After Deployment

1. **Remove Test Users** (production)
   - Create real admin accounts
   - Remove or disable test accounts

2. **Add Protected Route Middleware**
   - Implement authentication checks on dashboard pages
   - Redirect unauthenticated users to login

3. **Configure Monitoring**
   - Set up Vercel analytics
   - Configure error tracking (Sentry, etc.)

4. **Set Production JWT Secret**
   - Set `JWT_SECRET_KEY` environment variable on Render
   - Use a secure random string (32+ characters)

5. **Update Documentation**
   - Document your production URLs
   - Update README with deployment info
