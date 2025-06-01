# 🚀 Google OAuth Deployment Checklist

## ✅ Pre-Deployment Verification

### 1. Local Testing Complete
- [x] Database migration successful
- [x] Google OAuth endpoint responding at `/auth/google/login`
- [x] FastAPI server running with new endpoints
- [x] Google credentials loaded correctly

### 2. Files to Deploy
Make sure these files are committed and pushed:

```bash
# New/Modified Files:
- requirements.txt          # Added Google OAuth dependencies
- models.py                 # Added Google OAuth fields to User model
- schemas.py               # Added GoogleAuthRequest/Response schemas
- crud.py                  # Added Google OAuth CRUD functions
- google_oauth.py          # NEW: Google OAuth service
- routes/auth.py           # Added /auth/google/login endpoint
- migrate_google_oauth.py  # Database migration script
- FRONTEND_GOOGLE_OAUTH_GUIDE.md  # Guide for frontend developer
```

## 🔧 Production Environment Setup

### 1. Environment Variables
Add these to your production `.env`:

```env
# Google OAuth (REQUIRED)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Existing variables (keep these)
DATABASE_URL=your-production-database-url
SECRET_KEY=your-jwt-secret-key
SMTP_SERVER=your-email-server
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-email-password
```

### 2. Database Migration
Run this on your production server:

```bash
python migrate_google_oauth.py
```

### 3. Dependencies Installation
```bash
pip install -r requirements.txt
```

## 🌐 Google Cloud Console Production Setup

### 1. Update Authorized Origins
In Google Cloud Console → APIs & Services → Credentials:

**Add these to "Authorized JavaScript origins":**
```
https://wisewords.online
https://your-backend-domain.com
```

**Add these to "Authorized redirect URIs":**
```
https://wisewords.online/auth/callback
```

### 2. Verify Domain Ownership
- Make sure `wisewords.online` is verified in Google Search Console
- This may be required for OAuth to work properly

## 📋 Deployment Steps

### 1. Git Commit & Push
```bash
git add .
git commit -m "feat: Add Google OAuth login support

- Add Google OAuth authentication endpoint
- Extend User model with Google fields
- Add database migration for OAuth fields
- Include frontend integration guide"

git push origin main
```

### 2. Deploy to Production Server
```bash
# On your production server:
git pull origin main
pip install -r requirements.txt
python migrate_google_oauth.py
# Restart your server (PM2, systemd, etc.)
```

### 3. Verify Deployment
Test these endpoints on production:

```bash
# Health check
curl https://your-backend-url/

# Google OAuth endpoint exists
curl -X POST https://your-backend-url/auth/google/login \
     -H "Content-Type: application/json" \
     -d '{"credential": "test"}'
# Should return: "Invalid Google token" (this is correct!)
```

## 📖 API Documentation

### New Endpoint Available at `/docs`:
- **🔐 Google OAuth Login** - `POST /auth/google/login`

Your API documentation will now show:
1. All existing email authentication endpoints
2. **NEW:** Google OAuth login endpoint
3. Updated user response schemas with `auth_provider` and `profile_picture`

## 🎯 Frontend Developer Handoff

### Give your frontend developer:
1. **`FRONTEND_GOOGLE_OAUTH_GUIDE.md`** - Complete implementation guide
2. **Google Client ID** - Same one you used for backend
3. **Backend URL** - Your production API URL
4. **API Documentation** - `https://your-backend-url/docs`

### Frontend needs to implement:
- Google Sign-In button
- Token handling
- API integration with `/auth/google/login`

## 🔍 Testing in Production

### 1. Manual Testing
1. Go to `https://wisewords.online`
2. Frontend developer implements Google button
3. Test Google login flow
4. Verify JWT token works with existing chat endpoints

### 2. User Scenarios to Test
- ✅ New Google user registration
- ✅ Existing Google user login
- ✅ Email conflict handling (Google email exists as email user)
- ✅ Profile picture display
- ✅ Chat functionality with Google users

## 🚨 Rollback Plan

If something goes wrong:

### 1. Database Rollback
```sql
-- Remove Google OAuth columns (if needed)
ALTER TABLE users DROP COLUMN IF EXISTS google_id;
ALTER TABLE users DROP COLUMN IF EXISTS auth_provider;
ALTER TABLE users DROP COLUMN IF EXISTS profile_picture;
```

### 2. Code Rollback
```bash
git revert HEAD  # Revert the Google OAuth commit
git push origin main
# Redeploy
```

## 📊 Monitoring

After deployment, monitor:
- Google OAuth login success/failure rates
- New user registrations via Google
- Any authentication errors in logs
- Database performance with new columns

## 🎉 Success Criteria

Deployment is successful when:
- [x] `/docs` shows Google OAuth endpoint
- [x] Google OAuth endpoint returns proper error for invalid tokens
- [x] Database has new Google OAuth columns
- [x] No existing functionality is broken
- [x] Frontend developer can implement Google login

---

**Ready to deploy!** 🚀 Your Google OAuth backend is production-ready! 