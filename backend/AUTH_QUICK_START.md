# Authentication Quick Start Guide

## 🚀 Getting Started

### 1. Start Keycloak
```bash
cd infra/docker-compose
docker-compose -f docker-compose.dev.yml up -d keycloak postgres
```

Wait for Keycloak to be ready (~30 seconds):
```bash
docker-compose -f docker-compose.dev.yml logs -f keycloak
# Wait for "Started" message
```

### 2. Configure Keycloak

Access Keycloak Admin Console:
```
URL: http://localhost:8080
Username: admin
Password: admin
```

**Create Realm:**
1. Hover over "Master" (top-left) → Click "Add Realm"
2. Name: `anki-compendium`
3. Click "Create"

**Create Client:**
1. Click "Clients" → "Create"
2. Client ID: `anki-api`
3. Client Protocol: `openid-connect`
4. Root URL: `http://localhost:8000`
5. Click "Save"

**Configure Client:**
1. Access Type: `confidential`
2. Standard Flow Enabled: `ON`
3. Direct Access Grants Enabled: `ON`
4. Service Accounts Enabled: `ON`
5. Valid Redirect URIs: `http://localhost:3000/*`
6. Click "Save"

**Get Client Secret:**
1. Go to "Credentials" tab
2. Copy the "Secret" value
3. Save for `.env` configuration

### 3. Configure Backend

Update `backend/.env`:
```bash
# Keycloak Configuration
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=anki-compendium
KEYCLOAK_CLIENT_ID=anki-api
KEYCLOAK_CLIENT_SECRET=<paste-secret-here>
KEYCLOAK_ADMIN_USERNAME=admin
KEYCLOAK_ADMIN_PASSWORD=admin

# JWT Configuration
SECRET_KEY=your-super-secret-32-char-key-change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 4. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 5. Start Backend

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or with Docker
cd infra/docker-compose
docker-compose -f docker-compose.dev.yml up -d backend
```

### 6. Test Authentication

**Open API Docs:**
```
http://localhost:8000/docs
```

**Or use curl:**

**Register:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPassword123!"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

**Save the access_token from response, then:**

**Get Current User:**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <your-access-token>"
```

---

## 📋 Available Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/register` | POST | ❌ | Register new user |
| `/api/v1/auth/login` | POST | ❌ | Login and get tokens |
| `/api/v1/auth/refresh` | POST | ❌ | Refresh access token |
| `/api/v1/auth/logout` | POST | ✅ | Logout user |
| `/api/v1/auth/me` | GET | ✅ | Get current user |
| `/api/v1/auth/verify-token` | POST | ✅ | Verify token |

---

## 🐛 Troubleshooting

### "Cannot connect to authentication service" (503)
**Solution:**
```bash
# Check if Keycloak is running
docker ps | grep keycloak

# Check logs
docker-compose -f infra/docker-compose/docker-compose.dev.yml logs keycloak

# Restart Keycloak
docker-compose -f infra/docker-compose/docker-compose.dev.yml restart keycloak
```

### "Invalid credentials" (401)
**Solution:**
- Verify user exists in Keycloak Admin Console
- Check password is correct (case-sensitive)
- Ensure user is enabled

### "User already exists" (409)
**Solution:**
- Use different email/username
- Check existing users in Keycloak or login instead

### "Rate limit exceeded" (429)
**Solution:**
- Wait 60 seconds before retrying
- Check `retry_after` in response
- Reduce request frequency

---

## 🧪 Run Tests

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run auth tests
pytest tests/api/test_auth.py -v

# With coverage
pytest tests/api/test_auth.py --cov=app.api.v1.endpoints.auth --cov-report=html
```

---

## 📚 Documentation

- **Full Auth Docs:** `backend/AUTHENTICATION.md`
- **Implementation Summary:** `AUTHENTICATION_IMPLEMENTATION.md`
- **API Docs:** http://localhost:8000/docs (when running)
- **ReDoc:** http://localhost:8000/redoc (when running)

---

## ✅ Verification Checklist

- [ ] Keycloak running and accessible
- [ ] Realm `anki-compendium` created
- [ ] Client `anki-api` configured
- [ ] Client secret copied to `.env`
- [ ] Backend `.env` configured
- [ ] Database migrations applied
- [ ] Backend running successfully
- [ ] `/docs` accessible
- [ ] Registration works
- [ ] Login returns tokens
- [ ] `/auth/me` returns user info

---

## 🎯 Next Steps

1. **Frontend Integration:**
   - Implement login/register forms
   - Store tokens securely
   - Add Authorization headers to requests
   - Implement token refresh logic

2. **Production Preparation:**
   - Use HTTPS only
   - Rotate JWT secret keys
   - Implement Redis-based rate limiting
   - Add token blacklist for logout
   - Enable email verification
   - Set up monitoring

3. **Additional Features:**
   - Password reset flow
   - Email verification
   - 2FA support
   - OAuth social logins
   - User profile management

---

## 💡 Tips

- **Token Expiration:** Access tokens expire in 15 minutes. Use refresh tokens to get new access tokens.
- **Rate Limiting:** Login/register limited to 5 requests per minute per IP.
- **Security:** Never commit `.env` or expose `SECRET_KEY`.
- **Testing:** Use `/docs` for quick manual testing.
- **Monitoring:** Check logs at `docker-compose logs -f backend`.

---

**Ready to go! 🎉**
