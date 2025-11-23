# Quick Start Guide: PDF Upload & Job Management API

## Prerequisites

```bash
# Start infrastructure
cd infra/docker-compose
docker-compose -f docker-compose.dev.yml up -d

# Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: `http://localhost:8000`  
Docs available at: `http://localhost:8000/docs`

---

## Authentication

All endpoints require authentication. Get a token first:

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password"
  }'

# Response:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {...}
}

# Save token
export TOKEN="eyJhbGc..."
```

---

## 1. Upload PDF

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/document.pdf" \
  -F "page_start=1" \
  -F "page_end=10" \
  -F "card_density=medium" \
  -F "subject=Physics" \
  -F "chapter=Mechanics" \
  -F 'custom_tags=["kinematics", "motion"]'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "...",
  "status": "pending",
  "progress": 0,
  "source_filename": "document.pdf",
  "source_pages": "1-10",
  "settings": {
    "card_density": "medium",
    "page_start": 1,
    "page_end": 10,
    "subject": "Physics",
    "chapter": "Mechanics",
    "custom_tags": ["kinematics", "motion"]
  },
  "created_at": "2025-11-23T12:00:00Z",
  ...
}
```

---

## 2. List Jobs

```bash
# All jobs
curl "http://localhost:8000/api/v1/jobs?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"

# Filter by status
curl "http://localhost:8000/api/v1/jobs?status=completed" \
  -H "Authorization: Bearer $TOKEN"

# Pagination
curl "http://localhost:8000/api/v1/jobs?page=2&page_size=50" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "total": 45,
  "page": 1,
  "page_size": 20,
  "pages": 3,
  "items": [...]
}
```

---

## 3. Get Job Status

```bash
# Full details
curl "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Authorization: Bearer $TOKEN"

# Lightweight status (for polling)
curl "http://localhost:8000/api/v1/jobs/{job_id}/status" \
  -H "Authorization: Bearer $TOKEN"
```

**Status Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "error_message": null,
  "result_deck_id": "660e8400-e29b-41d4-a716-446655440000"
}
```

---

## 4. Retry Failed Job

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/{job_id}/retry" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 5. Delete Job

```bash
curl -X DELETE "http://localhost:8000/api/v1/jobs/{job_id}" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 6. List Decks

```bash
curl "http://localhost:8000/api/v1/decks?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "total": 12,
  "page": 1,
  "page_size": 20,
  "pages": 1,
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440000",
      "name": "Physics - Mechanics",
      "description": "...",
      "card_count": 45,
      "file_size_bytes": 125000,
      "source_filename": "document.pdf",
      "tags": ["physics", "mechanics"],
      "created_at": "2025-11-23T12:00:00Z",
      ...
    }
  ]
}
```

---

## 7. Get Deck Details

```bash
curl "http://localhost:8000/api/v1/decks/{deck_id}" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 8. Download Deck

```bash
# Get download URL
curl "http://localhost:8000/api/v1/decks/{deck_id}/download" \
  -H "Authorization: Bearer $TOKEN"

# Response:
{
  "download_url": "https://minio:9000/decks/user-id/deck-id/deck.apkg?...",
  "expires_in": 3600
}

# Download file
curl -O "download_url_from_above"
```

**Note:** Download URL expires after 1 hour.

---

## 9. Delete Deck

```bash
curl -X DELETE "http://localhost:8000/api/v1/decks/{deck_id}" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | GET requests |
| 201 | Created | POST upload |
| 204 | No Content | DELETE requests |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Quota exceeded, not owner |
| 404 | Not Found | Job/deck doesn't exist |
| 413 | Payload Too Large | File exceeds 100MB |
| 500 | Server Error | Storage/database issues |

---

## Limits

| Resource | Free Tier | Premium Tier |
|----------|-----------|--------------|
| Cards/month | 30 | 1000 |
| Upload size | 100 MB | 100 MB |
| Upload rate | 10/hour | 10/hour |

---

## Status Flow

```
UPLOAD → PENDING → PROCESSING → COMPLETED → DOWNLOAD
                ↓
              FAILED → RETRY → PENDING
                ↓
            CANCELLED
```

---

## Polling Pattern

```bash
#!/bin/bash
JOB_ID="your-job-id"

while true; do
  STATUS=$(curl -s "http://localhost:8000/api/v1/jobs/$JOB_ID/status" \
    -H "Authorization: Bearer $TOKEN" \
    | jq -r '.status')
  
  echo "Status: $STATUS"
  
  if [[ "$STATUS" == "completed" ]]; then
    DECK_ID=$(curl -s "http://localhost:8000/api/v1/jobs/$JOB_ID/status" \
      -H "Authorization: Bearer $TOKEN" \
      | jq -r '.result_deck_id')
    
    echo "Deck ready: $DECK_ID"
    break
  elif [[ "$STATUS" == "failed" ]]; then
    echo "Job failed!"
    break
  fi
  
  sleep 2
done
```

---

## Python Example

```python
import httpx
import time

# Login
response = httpx.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "user@example.com", "password": "password"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Upload PDF
with open("document.pdf", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/api/v1/upload",
        headers=headers,
        files={"file": ("document.pdf", f, "application/pdf")},
        data={
            "card_density": "medium",
            "subject": "Physics"
        }
    )
job = response.json()
job_id = job["id"]

# Poll status
while True:
    response = httpx.get(
        f"http://localhost:8000/api/v1/jobs/{job_id}/status",
        headers=headers
    )
    status_data = response.json()
    
    print(f"Status: {status_data['status']} ({status_data['progress']}%)")
    
    if status_data["status"] == "completed":
        deck_id = status_data["result_deck_id"]
        
        # Get download URL
        response = httpx.get(
            f"http://localhost:8000/api/v1/decks/{deck_id}/download",
            headers=headers
        )
        download_url = response.json()["download_url"]
        
        # Download file
        deck_content = httpx.get(download_url).content
        with open("deck.apkg", "wb") as f:
            f.write(deck_content)
        
        print("Download complete!")
        break
    
    elif status_data["status"] == "failed":
        print(f"Error: {status_data['error_message']}")
        break
    
    time.sleep(2)
```

---

## Testing

```bash
# Run all tests
cd backend
pytest tests/api/test_upload.py -v

# Run specific test
pytest tests/api/test_upload.py::TestUploadEndpoint::test_upload_valid_pdf -v

# With coverage
pytest tests/api/test_upload.py --cov=app.api.v1.endpoints.upload
```

---

## OpenAPI/Swagger Docs

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Support

For issues or questions, contact the development team or check:
- `/backend/UPLOAD_IMPLEMENTATION.md` - Full implementation details
- `/backend/README.md` - Project overview
- `/docs/API_DOCUMENTATION.md` - Complete API reference

---

**Last Updated:** 2025-11-23  
**Version:** 1.0.0
