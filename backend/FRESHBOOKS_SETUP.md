# FreshBooks Integration Setup Guide

This guide explains how to configure the FreshBooks integration for invoice management in the admin portals.

## Overview

The FreshBooks integration allows customers to:
- View their invoices from FreshBooks directly in the admin portal
- Download invoice PDFs
- Automatically sync invoice data

## Prerequisites

Before starting, ensure you have:
- [x] Created a FreshBooks application in the Developer Portal
- [x] Client ID from FreshBooks
- [x] Client Secret from FreshBooks (keep this secure!)
- [x] Configured redirect URI in FreshBooks app settings

## Environment Variables

Add these environment variables to your backend `.env` file:

### Required Variables

```bash
# FreshBooks API Credentials
FRESHBOOKS_CLIENT_ID=6b03cb3a8bc49ef2b5702481033423a2d1d2a3dfff601ae05d7471829eba4e7f
FRESHBOOKS_CLIENT_SECRET=your_client_secret_here

# FreshBooks Redirect URI (for OAuth callback)
FRESHBOOKS_REDIRECT_URI=https://ilanapm.onrender.com/api/v1/auth/freshbooks/callback
```

### Development Environment

For local development, use localhost redirect URI:

```bash
FRESHBOOKS_REDIRECT_URI=https://localhost:8000/api/v1/auth/freshbooks/callback
```

**Important:** When testing locally, FreshBooks will redirect to `https://localhost:8000/...`.
Manually change the URL in your browser from `https://` to `http://` to complete the OAuth flow.

### Production Environment (Render)

In your Render dashboard, add these environment variables:

1. Go to your backend service in Render
2. Navigate to the **Environment** tab
3. Click **Add Environment Variable**
4. Add each of the following:

| Key | Value | Description |
|-----|-------|-------------|
| `FRESHBOOKS_CLIENT_ID` | `6b03cb3a8bc49ef2b5702481033423a2d1d2a3dfff601ae05d7471829eba4e7f` | Your FreshBooks Client ID |
| `FRESHBOOKS_CLIENT_SECRET` | `your_secret_here` | Your FreshBooks Client Secret (from Developer Portal) |
| `FRESHBOOKS_REDIRECT_URI` | `https://ilanapm.onrender.com/api/v1/auth/freshbooks/callback` | Production OAuth callback URL |

4. Click **Save Changes**
5. Your backend will automatically redeploy with the new environment variables

## Local Development Setup

### Step 1: Create `.env` file

In the `backend` directory, create a `.env` file:

```bash
cd backend
touch .env
```

### Step 2: Add environment variables

Edit `.env` and add your credentials:

```bash
# FreshBooks Configuration
FRESHBOOKS_CLIENT_ID=6b03cb3a8bc49ef2b5702481033423a2d1d2a3dfff601ae05d7471829eba4e7f
FRESHBOOKS_CLIENT_SECRET=paste_your_client_secret_here
FRESHBOOKS_REDIRECT_URI=https://localhost:8000/api/v1/auth/freshbooks/callback

# Existing variables (keep these)
JWT_SECRET_KEY=your_jwt_secret
DATABASE_URL=postgresql://your_db_url
```

### Step 3: Verify `.gitignore`

Ensure `.env` is in your `.gitignore` file to prevent committing secrets:

```bash
# Check if .env is ignored
cat .gitignore | grep .env
```

If not present, add it:

```bash
echo ".env" >> .gitignore
```

## Testing the Integration

### Step 1: Start the backend

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Step 2: Check FreshBooks service status

Visit: http://localhost:8000/docs

Look for the `/auth/freshbooks/status` endpoint and test it with:
- Query parameter: `org_id=test-org`

It should return:
```json
{
  "connected": false,
  "account_id": null
}
```

### Step 3: Start the frontend

```bash
cd admin-portals/customer-portal
npm run dev
```

### Step 4: Test OAuth flow

1. Navigate to http://localhost:3000/billing
2. You should see a "Connect to FreshBooks" banner
3. Click the "Connect FreshBooks" button
4. You'll be redirected to FreshBooks authorization page
5. Authorize the application
6. FreshBooks will redirect to `https://localhost:8000/...`
7. **Manually change the URL** from `https://` to `http://` in your browser
8. Press Enter to complete the OAuth callback
9. You should be redirected back to the billing page
10. Invoices should now load from FreshBooks

## API Endpoints

Once configured, these endpoints will be available:

### OAuth Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/freshbooks/authorize` | GET | Initiate OAuth flow |
| `/api/v1/auth/freshbooks/callback` | GET | OAuth callback handler |
| `/api/v1/auth/freshbooks/status` | GET | Check connection status |
| `/api/v1/auth/freshbooks/disconnect` | POST | Disconnect FreshBooks |

### Billing Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/portal/customer/billing/invoices` | GET | List invoices |
| `/api/v1/portal/customer/billing/invoices/{id}` | GET | Get single invoice |
| `/api/v1/portal/customer/billing/invoices/{id}/pdf` | GET | Get invoice PDF URL |

## Architecture

### OAuth Flow

```
1. User clicks "Connect FreshBooks" in customer portal
   ↓
2. Frontend redirects to /api/v1/auth/freshbooks/authorize?org_id=...
   ↓
3. Backend redirects to FreshBooks authorization page
   ↓
4. User authorizes the application
   ↓
5. FreshBooks redirects to /api/v1/auth/freshbooks/callback?code=...&state=...
   ↓
6. Backend exchanges authorization code for access token
   ↓
7. Backend calls /auth/api/v1/users/me to get account_id
   ↓
8. Backend stores access_token + account_id for organization
   ↓
9. User is redirected back to billing page
   ↓
10. Frontend fetches invoices from /api/v1/portal/customer/billing/invoices
```

### Token Management

Tokens are stored in-memory in the `FreshBooksService` class:
- **Access Token:** Valid for ~1 hour (auto-refreshed)
- **Refresh Token:** Used to get new access tokens
- **Account ID:** Retrieved from identity endpoint, stored with token

**For production:** Consider storing tokens in database or Redis for persistence across server restarts.

## Troubleshooting

### Issue: "FreshBooks integration is not configured"

**Solution:** Ensure environment variables are set:
```bash
echo $FRESHBOOKS_CLIENT_ID
echo $FRESHBOOKS_CLIENT_SECRET
```

If empty, add them to `.env` and restart the server.

---

### Issue: "Failed to retrieve account_id from FreshBooks"

**Solution:** Check that your FreshBooks account has at least one business associated with it. The identity endpoint should return `business_memberships` with an `account_id`.

---

### Issue: OAuth redirect fails with SSL/HTTPS error

**Solution:** For local development:
1. FreshBooks redirects to `https://localhost:8000/...`
2. Manually change URL to `http://localhost:8000/...` in your browser
3. Press Enter to complete the callback

For production, ensure your redirect URI is HTTPS and matches exactly what's configured in FreshBooks.

---

### Issue: "Invalid redirect_uri"

**Solution:** The redirect URI in your OAuth request must exactly match what's configured in FreshBooks Developer Portal:
- Check for trailing slashes
- Verify http vs https
- Ensure domain and port match exactly

---

### Issue: Invoices not loading

**Solution:**
1. Check FreshBooks connection status: `/api/v1/auth/freshbooks/status?org_id=...`
2. Verify the organization has completed OAuth flow
3. Check backend logs for API errors
4. Ensure access token hasn't expired (auto-refresh should handle this)

---

### Issue: PDF download doesn't work

**Solution:** FreshBooks PDF URLs require the user to be logged into FreshBooks. The PDF URL format is:
```
https://my.freshbooks.com/invoice/{account_id}-{invoice_id}.pdf
```

Users must be logged into their FreshBooks account to access the PDF.

## Security Considerations

### Client Secret Protection

- ✅ Never commit `FRESHBOOKS_CLIENT_SECRET` to Git
- ✅ Use environment variables for all environments
- ✅ Rotate secrets regularly
- ✅ Use different credentials for development and production (if possible)

### Token Storage

Current implementation stores tokens in memory:
- **Pros:** Simple, works for single-server deployments
- **Cons:** Tokens lost on server restart, doesn't scale horizontally

**Recommended for production:**
- Store tokens in database with encryption
- OR use Redis for token caching
- Implement token rotation and expiry checks

### OAuth State Parameter

The integration uses `org_id` as the state parameter for CSRF protection. Consider using a randomly generated token stored in session for additional security.

## Files Modified

### Backend

- **New Files:**
  - `/backend/services/freshbooks_service.py` - FreshBooks API service
  - `/backend/api/freshbooks.py` - OAuth and billing endpoints

- **Modified Files:**
  - `/backend/main.py` - Added FreshBooks routers

### Frontend

- **Modified Files:**
  - `/admin-portals/customer-portal/app/billing/page.tsx` - Added FreshBooks integration

## Next Steps

Once the integration is working:

1. **Add organization context:** Replace `placeholder-org-id` with actual organization ID from user session
2. **Implement token persistence:** Store tokens in database for multi-server deployments
3. **Add webhook support:** Listen for FreshBooks webhooks for real-time invoice updates
4. **Enhance error handling:** Add retry logic and better error messages
5. **Add invoice filtering:** Allow users to filter invoices by date, status, etc.
6. **Cache invoice data:** Cache invoice list to reduce API calls
7. **Add founder portal integration:** Show all customer invoices in founder portal

## Support

If you encounter issues:
- Check backend logs: `tail -f backend.log`
- Review FreshBooks API documentation: https://www.freshbooks.com/api/start
- Contact FreshBooks API support: api@freshbooks.com

## Additional Resources

- [FreshBooks API Documentation](https://www.freshbooks.com/api/start)
- [FreshBooks Authentication Guide](https://www.freshbooks.com/api/authentication)
- [FreshBooks OAuth Scopes](https://www.freshbooks.com/api/scopes)
- [FreshBooks Identity Model](https://www.freshbooks.com/api/identity_model)
- [FreshBooks Invoicing API](https://www.freshbooks.com/api/invoices)
