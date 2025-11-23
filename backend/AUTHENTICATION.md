# Authentication System Documentation

## Overview

The Anki Compendium backend uses **Keycloak** for authentication with **JWT tokens** for API access control. This document describes the authentication flow, API endpoints, and security considerations.

## Architecture

### Components

1. **Keycloak** - Identity and Access Management (IAM)
   - Handles user credentials securely
   - Issues OAuth2/OIDC tokens
   - Manages user sessions

2. **FastAPI Backend** - Application API
   - Validates JWT tokens
   - Manages user profiles in PostgreSQL
   - Enforces authorization rules

3. **PostgreSQL** - User data storage
   - Stores user profiles with `keycloak_id` reference
   - Never stores passwords (managed by Keycloak)

### Authentication Flow

```
┌──────────┐         ┌───────────┐         ┌──────────┐
│  Client  │ ──────> │  FastAPI  │ ──────> │ Keycloak │
│          │         │  Backend  │         │          │
└──────────┘         └───────────┘         └──────────┘
     │                      │                     │
     │  1. Login Request    │                     │
     │ ──────────────────> │                     │
     │                      │  2. Validate Creds  │
     │                      │ ──────────────────> │
     │                      │                     │
     │                      │  3. Keycloak Token  │
     │                      │ <────────────────── │
     │                      │                     │
     │                      │  4. Create User/Sync│
     │                      │     (PostgreSQL)    │
     │                      │                     │
     │  5. JWT Tokens + User│                     │
     │ <────────────────── │                     │
     │                      │                     │
     │  6. API Request      │                     │
     │  (with JWT)          │                     │
     │ ──────────────────> │                     │
     │                      │  7. Verify Token    │
     │                      │     (JWT decode)    │
     │                      │                     │
     │  8. API Response     │                     │
     │ <────────────────── │                     │
```

## API Endpoints

### Base URL
```
http://localhost:8000/api/v1/auth
```

### 1. Register User

**Endpoint:** `POST /auth/register`

**Description:** Register a new user account

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "display_name": "John Doe"
}
```

**Validation Rules:**
- **email**: Valid email format, unique
- **username**: 3-50 characters, alphanumeric with hyphens/underscores, unique
- **password**: Minimum 8 characters
- **display_name**: Optional, max 255 characters

**Response (201 Created):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "johndoe",
    "display_name": "John Doe",
    "keycloak_id": "abc123-def456",
    "subscription_tier": "free",
    "cards_generated_month": 0,
    "cards_limit_month": 30,
    "is_active": true,
    "is_admin": false,
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z",
    "last_login_at": null
  },
  "message": "User registered successfully. Please check your email to verify your account."
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `409 Conflict` - User already exists
- `503 Service Unavailable` - Keycloak connection error

---

### 2. Login

**Endpoint:** `POST /auth/login`

**Description:** Authenticate user and receive JWT tokens

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "johndoe",
    "display_name": "John Doe",
    "subscription_tier": "free",
    "cards_generated_month": 5,
    "cards_limit_month": 30,
    "is_active": true,
    "is_admin": false,
    "last_login_at": "2025-01-15T10:30:00Z"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - Account inactive or deleted
- `429 Too Many Requests` - Rate limit exceeded (5 requests/min)
- `503 Service Unavailable` - Keycloak connection error

---

### 3. Refresh Token

**Endpoint:** `POST /auth/refresh`

**Description:** Get a new access token using refresh token

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or expired refresh token
- `403 Forbidden` - User account inactive or deleted

---

### 4. Logout

**Endpoint:** `POST /auth/logout`

**Description:** Logout user and invalidate session

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body (Optional):**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (204 No Content)**

---

### 5. Get Current User

**Endpoint:** `GET /auth/me`

**Description:** Get current user profile

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "username": "johndoe",
  "display_name": "John Doe",
  "subscription_tier": "free",
  "cards_generated_month": 5,
  "cards_limit_month": 30,
  "is_active": true,
  "is_admin": false,
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "last_login_at": "2025-01-15T12:45:00Z"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - User account inactive or deleted

---

### 6. Verify Token

**Endpoint:** `POST /auth/verify-token`

**Description:** Verify token validity

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "valid": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com"
}
```

---

## Token Management

### Access Token
- **Purpose:** Authenticate API requests
- **Lifetime:** 15 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Storage:** Client-side (memory or sessionStorage recommended)
- **Usage:** Include in `Authorization: Bearer <token>` header

### Refresh Token
- **Purpose:** Obtain new access tokens
- **Lifetime:** 7 days (configurable via `REFRESH_TOKEN_EXPIRE_DAYS`)
- **Storage:** Secure HTTP-only cookie or secure storage
- **Usage:** Submit to `/auth/refresh` when access token expires

### Token Payload

**Access Token:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "exp": 1705324200,
  "iat": 1705323300,
  "type": "access"
}
```

**Refresh Token:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "exp": 1705928100,
  "iat": 1705323300,
  "type": "refresh"
}
```

---

## Security Features

### Rate Limiting
- **Login/Register:** 5 requests per minute per IP
- **Response:** HTTP 429 with `Retry-After` header
- **Exemptions:** `/auth/me`, `/auth/logout`, `/auth/verify-token`

### Security Headers
All responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`

### Password Policy
Enforced by Keycloak:
- Minimum 8 characters
- Recommend: uppercase, lowercase, numbers, special characters

### CORS
Configured origins (dev):
- `http://localhost:3000`
- `http://localhost:5173`

---

## Keycloak Setup

### Prerequisites
1. Docker and Docker Compose installed
2. Keycloak realm configured (`anki-compendium`)
3. Client created (`anki-compendium-backend`)

### Configuration

**Environment Variables:**
```bash
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=anki-compendium
KEYCLOAK_CLIENT_ID=anki-api
KEYCLOAK_CLIENT_SECRET=your-client-secret
KEYCLOAK_ADMIN_USERNAME=admin
KEYCLOAK_ADMIN_PASSWORD=admin
```

### Keycloak Client Settings
- **Client ID:** `anki-api`
- **Access Type:** `confidential`
- **Standard Flow:** Enabled
- **Direct Access Grants:** Enabled
- **Service Accounts:** Enabled
- **Valid Redirect URIs:** `http://localhost:3000/*`

---

## Testing

### Manual Testing

**1. Register User**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

**2. Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

**3. Access Protected Endpoint**
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

**4. Refresh Token**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

### Automated Tests

See `tests/test_auth.py` for comprehensive test coverage.

**Run tests:**
```bash
pytest tests/test_auth.py -v
```

---

## Error Handling

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid input format, validation errors |
| 401 | Unauthorized | Invalid credentials, expired token |
| 403 | Forbidden | Inactive account, insufficient permissions |
| 409 | Conflict | Duplicate email/username |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected backend error |
| 503 | Service Unavailable | Keycloak connection failure |

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Best Practices

### For Developers

1. **Never log sensitive data** (passwords, tokens)
2. **Use HTTPS in production**
3. **Rotate JWT secret keys** regularly
4. **Implement token blacklisting** for logout (Redis recommended)
5. **Monitor authentication failures** for security threats
6. **Use refresh tokens securely** (HTTP-only cookies)

### For Frontend Developers

1. **Store tokens securely**
   - Access token: Memory or sessionStorage
   - Refresh token: HTTP-only cookie (recommended) or secure storage

2. **Handle token expiration gracefully**
   ```javascript
   // Pseudo-code
   if (response.status === 401) {
     const newToken = await refreshAccessToken();
     retryRequest(newToken);
   }
   ```

3. **Implement automatic token refresh**
   - Refresh ~1 minute before expiration
   - Use interceptors (Axios/Fetch)

4. **Clear tokens on logout**
   ```javascript
   localStorage.removeItem('access_token');
   // Call /auth/logout endpoint
   ```

---

## Troubleshooting

### "Cannot connect to authentication service" (503)

**Cause:** Backend cannot reach Keycloak

**Solutions:**
1. Check Keycloak is running: `docker ps | grep keycloak`
2. Verify `KEYCLOAK_URL` in `.env`
3. Check network connectivity: `curl http://keycloak:8080`

---

### "Invalid credentials" (401)

**Cause:** Wrong email/password or user doesn't exist

**Solutions:**
1. Verify user exists in Keycloak admin console
2. Check password is correct
3. Ensure user is enabled in Keycloak

---

### "User already exists" (409)

**Cause:** Email or username already registered

**Solutions:**
1. Use different email/username
2. Check if user exists: Login instead of register

---

### "Rate limit exceeded" (429)

**Cause:** Too many requests from same IP

**Solutions:**
1. Wait for `retry_after` seconds (in response)
2. Implement exponential backoff
3. Reduce request frequency

---

## Security Considerations

### Production Checklist

- [ ] Use HTTPS only
- [ ] Set strong `SECRET_KEY` (32+ random characters)
- [ ] Configure Keycloak with SSL
- [ ] Use Redis for rate limiting (not in-memory)
- [ ] Implement token blacklist for logout
- [ ] Enable Keycloak email verification
- [ ] Configure CORS restrictively
- [ ] Set up monitoring and alerting
- [ ] Regular security audits
- [ ] Rotate secrets periodically

### Data Privacy

- **Passwords:** Never stored in backend DB (Keycloak only)
- **Tokens:** Logged only on debug level (redacted in production)
- **User Data:** Minimal PII stored, GDPR-compliant
- **Audit Logs:** All auth events logged with IP addresses

---

## References

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs backend`
2. Review Keycloak admin console
3. Consult this documentation
4. Open an issue on GitHub
