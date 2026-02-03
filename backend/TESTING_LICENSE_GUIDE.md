# Testing License Guide

This guide shows you how to create a test license key to test all API functions in your desktop add-in.

## Quick Start

### Option 1: Using the Admin API (Recommended for Render)

Since your backend is deployed on Render, use the Admin API to create a test organization and license key:

```bash
curl -X POST "https://ilanapm.onrender.com/api/v1/admin/organizations" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: dev-admin-token-change-this" \
  -d '{
    "org_name": "My Test Organization",
    "tier": "professional",
    "seats_purchased": 5,
    "primary_contact_email": "test@example.com",
    "primary_contact_name": "Test Admin"
  }'
```

**Response:**
```json
{
  "org_id": "org_xxxxxxxxxx",
  "org_name": "My Test Organization",
  "license_key": "ILANA-A1B2-C3D4-E5F6-G7H8",
  "tier": "professional",
  "seats_purchased": 5,
  "subscription_end": "2027-02-02",
  "message": "Organization created successfully. Use license key to activate desktop add-in."
}
```

**Save the `license_key` - you'll need it to activate your add-in!**

#### Setting the Admin Token

For production, set a secure admin token as an environment variable in Render:

1. Go to your Render dashboard
2. Select your service
3. Go to Environment
4. Add: `ADMIN_TOKEN=your-secure-random-token-here`

For development/testing, the default token is `dev-admin-token-change-this`.

---

### Option 2: Using the Python Script (Local Development)

If you're running the backend locally or have SSH access to Render:

```bash
cd /Users/donmerriman/Projects/ilana-pm/backend

# Create a professional tier license with 5 seats
python create_test_license.py

# Or customize it
python create_test_license.py --tier enterprise --seats 10 --org-name "Acme Corp"
```

**Output:**
```
======================================================================
Creating Test License Key
======================================================================

✅ Test license created successfully!

License Key:       ILANA-A1B2-C3D4-E5F6-G7H8
Organization ID:   org_xxxxxxxxxxx
Organization Name: Test Organization
Tier:              professional
Seats:             5
Expires:           2027-02-02

======================================================================
How to use this license key:
======================================================================

1. Open your desktop add-in in MS Project
2. Go to Settings (or License Activation)
3. Enter this license key: ILANA-A1B2-C3D4-E5F6-G7H8
4. Enter any test email (e.g., yourname@test.com)
5. Click Activate

Your add-in will receive a JWT token valid for 90 days!
======================================================================
```

---

## Using the License Key in Your Add-In

### Step 1: Activate the License

1. Open Microsoft Project
2. Open your Ilana PM add-in
3. Go to **Settings** or **License Activation**
4. Enter:
   - **License Key:** `ILANA-A1B2-C3D4-E5F6-G7H8` (from above)
   - **Email:** `yourname@test.com` (any test email)
5. Click **Activate**

### Step 2: Verify Activation

The add-in will:
1. Send an activation request to: `POST https://ilanapm.onrender.com/api/v1/licensing/activate`
2. Receive a JWT token valid for 90 days
3. Store the token securely
4. Use the token for all subsequent API calls

### Step 3: Test API Functions

Now all API functions should work:
- ✅ **Template Generation** - Country-specific task templates
- ✅ **Duration Calculations** - ML-powered predictions
- ✅ **Feedback Submission** - Task outcome learning
- ✅ **Analytics** - Performance insights
- ✅ **Configuration** - Country/authority data

---

## Managing Test Organizations

### List All Organizations

```bash
curl -X GET "https://ilanapm.onrender.com/api/v1/admin/organizations" \
  -H "X-Admin-Token: dev-admin-token-change-this"
```

### Delete a Test Organization

```bash
curl -X DELETE "https://ilanapm.onrender.com/api/v1/admin/organizations/org_xxxxxxxxxx" \
  -H "X-Admin-Token: dev-admin-token-change-this"
```

**Note:** Deleting an organization cascades to all users, activations, and license keys.

---

## Troubleshooting

### Error: "Invalid license key"
- Verify the license key was created successfully
- Check that you copied the entire key (format: `ILANA-XXXX-XXXX-XXXX-XXXX`)

### Error: "No seats available"
- Check how many seats are purchased vs. used
- Create a new organization with more seats
- Or delete existing activations

### Error: "Subscription has expired"
- License subscriptions are valid for 365 days from creation
- Create a new test organization if expired

### Error: "Invalid admin token"
- Check the `X-Admin-Token` header is set correctly
- Verify the token matches your `ADMIN_TOKEN` environment variable

---

## What Happens Behind the Scenes

### License Activation Flow

1. **Add-in sends activation request:**
   ```json
   {
     "license_key": "ILANA-A1B2-C3D4-E5F6-G7H8",
     "user_email": "yourname@test.com",
     "device_id": "hashed-mac-address",
     "device_name": "MY-COMPUTER",
     "ms_project_version": "2021",
     "addin_version": "1.0.0"
   }
   ```

2. **Backend validates:**
   - ✅ License key exists and is active
   - ✅ Organization subscription is active
   - ✅ Seats are available (seats_used < seats_purchased)
   - ✅ Creates or retrieves user record
   - ✅ Creates activation record

3. **Backend returns JWT token:**
   ```json
   {
     "activation_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "org_id": "org_xxxxxxxxxx",
     "user_id": "usr_yyyyyyyyyy",
     "tier": "professional",
     "expires_at": "2026-05-03T10:30:00Z",
     "message": "License activated successfully"
   }
   ```

4. **Add-in uses token for all API calls:**
   - Includes in `Authorization: Bearer <token>` header
   - Token is validated on every API request
   - Token expires after 90 days (auto-refresh)

---

## Production Considerations

### Security

1. **Change the admin token immediately:**
   ```bash
   # Generate a secure random token
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Set in Render environment variables:**
   - `ADMIN_TOKEN=your-secure-random-token-here`

3. **Restrict admin endpoints:**
   - Consider IP whitelisting
   - Add additional authentication layers
   - Monitor admin API usage

### Database Backups

Since you're using SQLite on Render:
- Render doesn't persist SQLite databases across deploys
- Consider migrating to PostgreSQL for production
- Or implement database backup/restore mechanism

---

## Next Steps

1. ✅ Create a test license key (using Option 1 or 2)
2. ✅ Activate the license in your add-in
3. ✅ Test all API functions
4. 🔐 Change the admin token for security
5. 📊 Monitor activation and usage patterns

---

## Support

If you encounter any issues:
1. Check the backend logs in Render dashboard
2. Verify the license key in the database
3. Test the API endpoints directly with curl
4. Check the add-in logs for activation errors

Happy testing! 🚀
