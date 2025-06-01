# Frontend Google OAuth Implementation Guide

## 🎯 Overview
The backend now supports Google OAuth login! Users can register/login with their Google account and get the same JWT token as email authentication.

## 🔗 New API Endpoint

### **POST** `/auth/google/login`
**URL:** `https://your-backend-url/auth/google/login`

**Request:**
```json
{
    "credential": "google-id-token-from-frontend"
}
```

**Response (Success):**
```json
{
    "message": "Google login successful",
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "user": {
        "id": 123,
        "email": "user@gmail.com",
        "nickname": "John Doe",
        "is_verified": true,
        "auth_provider": "google",
        "profile_picture": "https://lh3.googleusercontent.com/..."
    },
    "is_new_user": false
}
```

**Response (Error):**
```json
{
    "error": true,
    "message": "Invalid Google token. Please try again.",
    "status_code": 400
}
```

## 🚀 Frontend Implementation

### 1. Add Google Sign-In Library

Add to your HTML `<head>`:
```html
<script src="https://accounts.google.com/gsi/client" async defer></script>
```

### 2. Google Sign-In Button

```html
<div id="g_id_onload"
     data-client_id="YOUR_GOOGLE_CLIENT_ID"
     data-callback="handleCredentialResponse">
</div>
<div class="g_id_signin" data-type="standard"></div>
```

### 3. JavaScript Handler

```javascript
// Handle Google Sign-In response
function handleCredentialResponse(response) {
    // Send the credential to your backend
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
            // Store the JWT token
            localStorage.setItem('authToken', data.access_token);
            
            // Update UI with user info
            updateUserProfile(data.user);
            
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            // Handle error
            alert(data.message || 'Login failed');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Login failed. Please try again.');
    });
}

// Update UI with user profile
function updateUserProfile(user) {
    // Display user info
    document.getElementById('userName').textContent = user.nickname;
    document.getElementById('userEmail').textContent = user.email;
    
    // Show profile picture if available
    if (user.profile_picture) {
        document.getElementById('userAvatar').src = user.profile_picture;
    }
}
```

### 4. React/Next.js Implementation

```jsx
import { useEffect } from 'react';

function GoogleLoginButton() {
    useEffect(() => {
        // Load Google Sign-In
        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);

        // Initialize when loaded
        script.onload = () => {
            window.google.accounts.id.initialize({
                client_id: 'YOUR_GOOGLE_CLIENT_ID',
                callback: handleCredentialResponse
            });
            
            window.google.accounts.id.renderButton(
                document.getElementById('googleSignInButton'),
                { theme: 'outline', size: 'large' }
            );
        };
    }, []);

    const handleCredentialResponse = async (response) => {
        try {
            const res = await fetch('/auth/google/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ credential: response.credential })
            });
            
            const data = await res.json();
            
            if (data.access_token) {
                localStorage.setItem('authToken', data.access_token);
                // Handle successful login
                router.push('/dashboard');
            }
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    return <div id="googleSignInButton"></div>;
}
```

## 🔧 Configuration

### Required Environment Variables:
```env
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
REACT_APP_BACKEND_URL=https://your-backend-url
```

### Google Client ID:
- **Development:** Use the same Client ID from Google Cloud Console
- **Production:** Make sure `wisewords.online` is in authorized origins

## 🎨 UI/UX Recommendations

### 1. Login Page Layout
```html
<div class="login-container">
    <h2>Welcome to Wise Words</h2>
    
    <!-- Email Login Form -->
    <form id="emailLogin">
        <input type="email" placeholder="Email" required>
        <input type="password" placeholder="Password" required>
        <button type="submit">Login with Email</button>
    </form>
    
    <!-- Divider -->
    <div class="divider">
        <span>OR</span>
    </div>
    
    <!-- Google Login Button -->
    <div id="googleSignInButton"></div>
    
    <p>Don't have an account? <a href="/register">Sign up</a></p>
</div>
```

### 2. Registration Page
```html
<div class="register-container">
    <h2>Create Your Account</h2>
    
    <!-- Google Sign-Up (Instant) -->
    <div id="googleSignInButton"></div>
    
    <!-- Divider -->
    <div class="divider">
        <span>OR</span>
    </div>
    
    <!-- Email Registration Form -->
    <form id="emailRegister">
        <input type="email" placeholder="Email" required>
        <input type="text" placeholder="Nickname" required>
        <input type="password" placeholder="Password" required>
        <button type="submit">Register with Email</button>
    </form>
</div>
```

## 🔒 Security Notes

1. **Token Storage:** Store JWT in `localStorage` or `sessionStorage`
2. **Token Usage:** Include in API requests as `Authorization: Bearer <token>`
3. **Auto-logout:** Handle token expiration (24 hours)
4. **HTTPS Only:** Google OAuth requires HTTPS in production

## 🎯 User Flow

### New Google User:
1. Click "Sign in with Google"
2. Google popup → User selects account
3. Instant account creation + auto-verification
4. Welcome email sent
5. Redirected to dashboard

### Existing Google User:
1. Click "Sign in with Google"
2. Google popup → User selects account
3. Instant login
4. Redirected to dashboard

### Email Conflict:
1. If email exists with email auth → Error message
2. Show: "Account exists. Please login with email/password"

## 🧪 Testing

### Test with Development:
```javascript
// Test the endpoint directly
fetch('http://localhost:8000/auth/google/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ credential: 'REAL_GOOGLE_TOKEN_HERE' })
});
```

### Production Testing:
- Test on `wisewords.online` with real Google accounts
- Verify JWT tokens work with existing chat endpoints
- Test profile pictures display correctly

## 📱 Mobile Considerations

Google Sign-In works on mobile browsers, but consider:
- Button sizing for touch interfaces
- Popup handling on mobile
- Deep linking after authentication

## 🎉 Benefits for Users

- ✅ **No email verification needed** (instant access)
- ✅ **No password to remember**
- ✅ **Profile picture automatically set**
- ✅ **Same chat experience** as email users
- ✅ **Secure Google authentication**

## 🔗 Useful Links

- [Google Sign-In Documentation](https://developers.google.com/identity/gsi/web)
- [Google Sign-In Button Customization](https://developers.google.com/identity/gsi/web/reference/js-reference)
- [Backend API Documentation](http://localhost:8000/docs)

---

**Need help?** The backend developer has implemented everything. Just follow this guide and you'll have Google OAuth working in no time! 🚀 