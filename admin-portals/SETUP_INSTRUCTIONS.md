# Admin Portals Setup Instructions

## Quick Start

### Customer Portal (app.seleen.com)

1. **Install Dependencies**
   ```bash
   cd customer-portal
   npm install
   ```

2. **Create Environment File**
   Create `.env.local`:
   ```env
   NEXT_PUBLIC_API_URL=https://ilanapm.onrender.com/api/v1
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=your-secret-key-here
   ```

3. **Run Development Server**
   ```bash
   npm run dev
   ```

4. **Open in Browser**
   Navigate to http://localhost:3000

### Founder Portal (admin.seleen.com)

Coming soon - will be created next.

---

## Testing the Customer Portal

### Pages to Test:
1. **Landing Page** (http://localhost:3000)
   - Logo displays correctly
   - Custom fonts load (Helvetica Light for headers, HF Monorita Light for body)
   - "Sign In" and "Go to Dashboard" buttons work

2. **Login Page** (http://localhost:3000/login)
   - Form inputs work
   - Email and password validation
   - Submit button shows loading state

3. **Dashboard** (http://localhost:3000/dashboard)
   - Stats cards display
   - Navigation menu works
   - Mock data shows correctly
   - Recent activity section displays

### Expected Issues (To Fix):
- [ ] API calls will fail (backend authentication not connected yet)
- [ ] Navigation links to `/users`, `/billing`, etc. will 404 (pages not created yet)
- [ ] "Sign Out" button does nothing (no auth implementation yet)

---

## Next Development Steps

### Phase 1: Complete Customer Portal Pages

1. **Users Page** (`/app/users/page.tsx`)
   - List all users in organization
   - Deactivate user button
   - Reassign seat functionality
   - User activity indicators

2. **Billing Page** (`/app/billing/page.tsx`)
   - Invoice list with download links
   - Payment methods management
   - Add seats via Stripe Checkout
   - Subscription management (pause, cancel, change cycle)

3. **Analytics Page** (`/app/analytics/page.tsx`)
   - Template generation charts (last 30 days)
   - Most used templates
   - Most active users
   - Feedback submission stats
   - Country/authority distribution charts

4. **Settings Page** (`/app/settings/page.tsx`)
   - Organization name (editable)
   - Billing email
   - Notification preferences
   - Admin transfer button → modal workflow
   - API access (future feature)

### Phase 2: API Integration

5. **Create API Client** (`/lib/api-client.ts`)
   ```typescript
   const API_BASE = process.env.NEXT_PUBLIC_API_URL;

   export async function fetchDashboard(token: string) {
     const res = await fetch(`${API_BASE}/portal/customer/dashboard`, {
       headers: { Authorization: `Bearer ${token}` }
     });
     return res.json();
   }
   ```

6. **Install NextAuth.js**
   ```bash
   npm install next-auth
   ```

7. **Configure NextAuth** (`/app/api/auth/[...nextauth]/route.ts`)
   - Connect to FastAPI JWT system
   - Session management
   - Protected route middleware

### Phase 3: Founder Portal

8. **Create Founder Portal** (`/admin-portals/founder-portal/`)
   - Mirror customer portal structure
   - Add super admin pages:
     - System dashboard
     - All customers list
     - Customer drill-down
     - License generation
     - System analytics
     - Logs viewer
     - GDPR export tools

---

## Deployment Checklist

### Prerequisites:
- [ ] Stripe account created
- [ ] Products configured in Stripe
- [ ] Webhook endpoint registered
- [ ] Vercel account set up
- [ ] Domains configured (seleen.com, app.seleen.com, admin.seleen.com)

### Deploy Customer Portal:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add customer portal"
   git push
   ```

2. **Connect to Vercel**
   - Go to vercel.com
   - Import project from GitHub
   - Set root directory: `admin-portals/customer-portal`
   - Framework: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`

3. **Environment Variables** (in Vercel):
   ```
   NEXT_PUBLIC_API_URL=https://ilanapm.onrender.com/api/v1
   NEXTAUTH_URL=https://app.seleen.com
   NEXTAUTH_SECRET=[generate secure key]
   NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=[from Stripe]
   ```

4. **Custom Domain**
   - Add domain: app.seleen.com
   - Configure DNS (CNAME to Vercel)
   - SSL auto-configured

5. **Deploy**
   - Vercel auto-deploys on push to main branch
   - Check deployment logs
   - Test production site

### Deploy Founder Portal:
   - Same process
   - Root directory: `admin-portals/founder-portal`
   - Domain: admin.seleen.com

---

## Troubleshooting

### Fonts Not Loading
- Check `/public/fonts/` directory exists
- Verify font files copied correctly
- Check `app/globals.css` has @font-face declarations
- Clear Next.js cache: `rm -rf .next`

### Images Not Showing
- Verify `/public/logo.png` exists
- Check Next.js Image component width/height props
- Restart dev server after adding new public files

### API Calls Failing
- Check NEXT_PUBLIC_API_URL in `.env.local`
- Verify FastAPI backend is running
- Check CORS configuration in `backend/main.py`
- Inspect browser console for errors

### Build Errors
- Run `npm run build` to see detailed errors
- Check TypeScript errors: `npx tsc --noEmit`
- Verify all imports are correct
- Clear `.next` and `node_modules`, reinstall

---

## Development Workflow

### Starting Development:
```bash
# Terminal 1: Backend
cd backend
python3 -m venv venv
source venv/bin/activate
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Customer Portal
cd admin-portals/customer-portal
npm run dev

# Terminal 3: Founder Portal (when created)
cd admin-portals/founder-portal
npm run dev
```

### Testing API Integration:
```bash
# Test FastAPI endpoint
curl -X GET "http://localhost:8000/api/v1/health"

# Test portal endpoint (requires auth token)
curl -X GET "http://localhost:8000/api/v1/portal/customer/dashboard" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Resources

- **Next.js Docs**: https://nextjs.org/docs
- **Tailwind CSS**: https://tailwindcss.com/docs
- **NextAuth.js**: https://next-auth.js.org/
- **Stripe Docs**: https://stripe.com/docs
- **Vercel Deployment**: https://vercel.com/docs

---

## Contact

For questions or issues, contact Don Merriman or refer to:
- Main plan: `/Users/donmerriman/.claude/plans/foamy-drifting-hopper.md`
- Implementation progress: `/IMPLEMENTATION_PROGRESS.md`
