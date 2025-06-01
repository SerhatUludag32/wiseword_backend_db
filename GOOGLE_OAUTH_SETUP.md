# Google OAuth Setup Guide

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Google Cloud Console Setup

1. **Go to [Google Cloud Console](https://console.cloud.google.com/)**
2. **Create a new project** or select an existing one
3. **Enable Google+ API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" 
   - Click "Enable"

4. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add your authorized origins:
     - `http://localhost:3000` (for local frontend)
     - `https://yourdomain.com` (for production)

5. **Copy your credentials**:
   - Client ID: `your-client-id.apps.googleusercontent.com`
   - Client Secret: `your-client-secret`

### 3. Environment Variables

Add these to your `.env` file:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 4. Database Migration

Run the migration to add Google OAuth fields:

```bash
python migrate_google_oauth.py
```

### 5. Frontend Integration

Use Google's JavaScript library to get the ID token:

```javascript
// Example frontend code
function handleGoogleLogin(response) {
    fetch('/auth/google/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            credential: response.credential
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.access_token) {
            localStorage.setItem('token', data.access_token);
            // Redirect to dashboard
        }
    });
}
```

## 🔄 API Endpoints

### Google Login
```
POST /auth/google/login
Content-Type: application/json

{
    "credential": "google-id-token-here"
}
```

**Response:**
```json
{
    "message": "Google login successful",
    "access_token": "jwt-token-here",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "email": "user@gmail.com",
        "nickname": "John Doe",
        "is_verified": true,
        "auth_provider": "google",
        "profile_picture": "https://lh3.googleusercontent.com/..."
    },
    "is_new_user": false
}
```

## 🔒 Security Features

- ✅ **Token Verification**: Google ID tokens are verified server-side
- ✅ **Email Separation**: Users with existing email accounts can't be overridden
- ✅ **Auto-verification**: Google users are automatically verified
- ✅ **JWT Integration**: Same JWT system as email authentication
- ✅ **Profile Pictures**: Automatic profile picture from Google

## 🎯 User Flow

1. **New Google User**: Creates account → Auto-verified → Welcome email → JWT token
2. **Existing Google User**: Verifies token → JWT token  
3. **Email Conflict**: Returns error if email already exists with email auth

## 🛠️ Testing

Test the endpoint with a valid Google ID token:

```bash
curl -X POST "http://localhost:8000/auth/google/login" \
     -H "Content-Type: application/json" \
     -d '{"credential": "your-google-id-token"}'
```

## 📝 Notes

- Google users don't need email verification
- Profile pictures are automatically fetched from Google
- Existing email users cannot be linked (as requested)
- All authentication flows return the same JWT token format 