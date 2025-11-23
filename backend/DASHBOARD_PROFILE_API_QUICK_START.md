# Dashboard & Profile API - Quick Start Guide

## Prerequisites
- Backend server running
- PostgreSQL database accessible
- Valid JWT token (from login)

## Step 1: Apply Database Migration

```bash
cd /home/fulgidus/Documents/anki-compendium/backend

# Check current migration status
python3 -c "from alembic.config import Config; from alembic import command; cfg = Config('alembic.ini'); command.current(cfg)"

# Apply the new migration
python3 -c "from alembic.config import Config; from alembic import command; cfg = Config('alembic.ini'); command.upgrade(cfg, 'head')"

# Verify migration applied
python3 -c "from alembic.config import Config; from alembic import command; cfg = Config('alembic.ini'); command.current(cfg)"
```

## Step 2: Start the Backend

```bash
cd /home/fulgidus/Documents/anki-compendium/backend

# Start with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Step 3: Get Authentication Token

```bash
# Login to get JWT token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "yourpassword"
  }'

# Extract the access_token from the response
# Example response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   ...
# }

# Set it as environment variable for convenience
export TOKEN="your_access_token_here"
```

## Step 4: Test Dashboard Endpoints

### Get Dashboard Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/stats" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Expected Response:**
```json
{
  "total_decks": 5,
  "total_cards": 150,
  "active_jobs": 1,
  "decks_this_week": 2,
  "decks_this_month": 4
}
```

### Get Recent Activity
```bash
curl -X GET "http://localhost:8000/api/v1/dashboard/activity?limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Expected Response:**
```json
[
  {
    "id": "uuid-here",
    "type": "job",
    "title": "Processing: document.pdf",
    "timestamp": "2025-11-23T10:30:00Z",
    "status": "processing",
    "metadata": {
      "progress": 75,
      "card_density": "medium"
    }
  },
  {
    "id": "uuid-here",
    "type": "deck",
    "title": "My Anki Deck",
    "timestamp": "2025-11-22T15:20:00Z",
    "status": null,
    "metadata": {
      "card_count": 30,
      "language": "en"
    }
  }
]
```

## Step 5: Test User/Profile Endpoints

### Get User Profile
```bash
curl -X GET "http://localhost:8000/api/v1/user/profile" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Update Profile
```bash
curl -X PUT "http://localhost:8000/api/v1/user/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "John Updated"
  }' | jq
```

### Get User Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/user/stats" \
  -H "Authorization: Bearer $TOKEN" | jq
```

### Get User Preferences
```bash
curl -X GET "http://localhost:8000/api/v1/user/preferences" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Expected Response (default preferences):**
```json
{
  "default_max_cards": 20,
  "default_difficulty": "medium",
  "include_images": true,
  "email_on_completion": true,
  "email_on_failure": true
}
```

### Update Preferences
```bash
curl -X PUT "http://localhost:8000/api/v1/user/preferences" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "default_max_cards": 30,
    "default_difficulty": "hard",
    "email_on_completion": false
  }' | jq
```

### Test Account Deletion (⚠️ WARNING: This will soft-delete the account)
```bash
# DO NOT RUN on production accounts!
curl -X DELETE "http://localhost:8000/api/v1/user/account" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "confirmation": "DELETE"
  }' | jq
```

## Step 6: View API Documentation

Open your browser to:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Navigate to the **dashboard** and **user** sections to explore all endpoints interactively.

## Step 7: Integration Testing

### Using Python Requests
```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_token_here"
headers = {"Authorization": f"Bearer {TOKEN}"}

# Dashboard stats
response = requests.get(f"{BASE_URL}/dashboard/stats", headers=headers)
print(response.json())

# Recent activity
response = requests.get(f"{BASE_URL}/dashboard/activity?limit=5", headers=headers)
print(response.json())

# User preferences
response = requests.get(f"{BASE_URL}/user/preferences", headers=headers)
print(response.json())

# Update preferences
data = {"default_max_cards": 40}
response = requests.put(f"{BASE_URL}/user/preferences", headers=headers, json=data)
print(response.json())
```

### Using Frontend (Axios/TypeScript)
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
});

// Test dashboard
const stats = await api.get('/dashboard/stats');
console.log('Dashboard Stats:', stats.data);

const activity = await api.get('/dashboard/activity?limit=10');
console.log('Recent Activity:', activity.data);

// Test user profile
const profile = await api.get('/user/profile');
console.log('User Profile:', profile.data);

const preferences = await api.get('/user/preferences');
console.log('User Preferences:', preferences.data);
```

## Troubleshooting

### Issue: 401 Unauthorized
**Solution:** Token expired or invalid. Login again to get a fresh token.

### Issue: 500 Internal Server Error
**Solution:** Check backend logs for detailed error messages:
```bash
# Backend terminal will show detailed traceback
# Or check log files if configured
```

### Issue: Migration not applied
**Solution:** Verify database connection and run migration manually:
```bash
cd backend
# Check if migration file exists
ls -l alembic/versions/20251123_add_user_preferences_field.py

# Run migration with verbose output
python3 -c "
from alembic.config import Config
from alembic import command
cfg = Config('alembic.ini')
cfg.set_main_option('sqlalchemy.url', 'YOUR_DATABASE_URL')
command.upgrade(cfg, 'head')
"
```

### Issue: Module not found errors
**Solution:** Ensure all dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

## Success Indicators

✅ All endpoints return 200 OK (except password change which returns 501)  
✅ Dashboard stats show correct counts  
✅ Activity feed combines jobs and decks  
✅ Preferences persist after update  
✅ Profile updates successfully  
✅ API documentation loads correctly

## Next Steps

1. ✅ Backend implementation complete
2. ⏳ Apply database migration
3. ⏳ Test all endpoints manually
4. ⏳ Integrate with frontend
5. ⏳ Write automated tests
6. ⏳ Deploy to staging environment

---

**Implementation Date:** November 23, 2025  
**Status:** Ready for Testing  
**Documentation:** See `DASHBOARD_PROFILE_API_IMPLEMENTATION.md` for full details
