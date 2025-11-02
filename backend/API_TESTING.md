# API Testing Guide

This guide covers how to test all the authentication APIs in the Pasky application.

## API Endpoints

1. `POST /api/auth/register/start/` - Start registration process
2. `POST /api/auth/register/complete/` - Complete registration with passkey
3. `POST /api/auth/login/start/` - Start login process
4. `POST /api/auth/login/complete/` - Complete login with passkey
5. `GET /api/auth/user/` - Get current authenticated user
6. `POST /api/auth/logout/` - Logout current user

## Prerequisites

1. Start the Django server:
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

2. Install HTTP client tools (optional):
- `curl` (usually pre-installed)
- Or use Postman/Insomnia
- Or use the browser frontend

## Testing Methods

### Method 1: Using the Frontend (Easiest)

The easiest way to test is using the React frontend:
1. Start frontend: `cd frontend && npm install && npm run dev`
2. Navigate to `http://localhost:3000`
3. Use the UI to register and login

### Method 2: Using curl (Manual Testing)

#### 1. Start Registration

```bash
curl -X POST http://localhost:8000/api/auth/register/start/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com"
  }'
```

**Expected Response:**
```json
{
  "challenge": "...",
  "rp": {
    "id": "localhost",
    "name": "Pasky Auth App"
  },
  "user": {
    "id": "...",
    "name": "testuser",
    "displayName": "testuser"
  },
  "pubKeyCredParams": [...],
  "authenticatorSelection": {...},
  "timeout": 60000,
  "attestation": "none"
}
```

**Note:** The `register/complete` and `login/complete` endpoints require actual WebAuthn credentials created in a browser, so they cannot be fully tested with curl alone.

#### 2. Start Login

```bash
curl -X POST http://localhost:8000/api/auth/login/start/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser"
  }'
```

**Expected Response:**
```json
{
  "challenge": "...",
  "allowCredentials": [...],
  "timeout": 60000,
  "userVerification": "preferred",
  "rpId": "localhost"
}
```

#### 3. Get User Info (Requires Authentication)

First, you need to be logged in (via frontend or session cookie):

```bash
# After logging in through frontend, use the session cookie
curl -X GET http://localhost:8000/api/auth/user/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

#### 4. Logout

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Cookie: sessionid=YOUR_SESSION_ID"
```

### Method 3: Using Python Test Script

Run the automated test script:

```bash
cd backend
source venv/bin/activate
python test_apis.py
```

### Method 4: Using Django Test Suite

Run Django's built-in test framework:

```bash
cd backend
source venv/bin/activate
python manage.py test auth_app.tests
```

## Testing Flow

### Complete Registration Flow:

1. **Register Start** - Get registration options
2. **Browser creates passkey** - User authenticates via browser
3. **Register Complete** - Submit credential to server
4. **Get User Info** - Verify user is logged in

### Complete Login Flow:

1. **Login Start** - Get authentication options
2. **Browser uses passkey** - User authenticates via browser
3. **Login Complete** - Submit credential to server
4. **Get User Info** - Verify user is logged in

## Error Testing

### Test invalid registration:
```bash
curl -X POST http://localhost:8000/api/auth/register/start/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": ""
  }'
# Expected: 400 Bad Request
```

### Test duplicate username:
```bash
curl -X POST http://localhost:8000/api/auth/register/start/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "existinguser",
    "email": "test@example.com"
  }'
# Expected: 400 Bad Request if user exists
```

### Test login with non-existent user:
```bash
curl -X POST http://localhost:8000/api/auth/login/start/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nonexistent"
  }'
# Expected: 404 Not Found
```

### Test protected endpoint without auth:
```bash
curl -X GET http://localhost:8000/api/auth/user/
# Expected: 401 Unauthorized
```

## Notes

- WebAuthn requires HTTPS in production (localhost is allowed for development)
- Session-based authentication uses cookies
- Challenges are stored in-memory (will be lost on server restart)
- For production, use proper challenge storage (Redis/database)

