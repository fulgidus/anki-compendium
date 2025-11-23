# Google Gemini API Configuration Guide

## Overview

The Anki Compendium RAG (Retrieval-Augmented Generation) pipeline uses **Google's Gemini API** for AI-powered flashcard generation. This guide explains how to obtain and configure your API key.

---

## Prerequisites

- Google account
- Access to Google AI Studio (free tier available)
- Backend environment configured (see `README.md`)

---

## Step 1: Obtain Your Gemini API Key

### Option A: Google AI Studio (Recommended for Development)

1. **Navigate to Google AI Studio:**
   - Visit: https://makersuite.google.com/app/apikey
   - Or go to: https://aistudio.google.com/ → Click "Get API Key"

2. **Sign in with your Google account**

3. **Create an API Key:**
   - Click **"Create API Key"** or **"Get API Key"**
   - Select or create a Google Cloud Project
   - Copy the generated API key (starts with `AIza...`)

4. **Save your key securely**
   - ⚠️ **Never commit this key to version control**
   - Store it in your `.env` file only

### Option B: Google Cloud Console (For Production)

1. Go to: https://console.cloud.google.com/
2. Create or select a project
3. Enable **"Generative Language API"**
4. Navigate to **APIs & Services → Credentials**
5. Create credentials → **API Key**
6. (Optional) Restrict the API key to specific APIs and IP addresses

---

## Step 2: Configure Your Environment

### Add API Key to `.env` File

```bash
# Navigate to backend directory
cd backend

# Copy example environment file (if not already done)
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

### Update the `GEMINI_API_KEY` Variable

Find this line in your `.env` file:

```bash
# Google Gemini AI Configuration
# Required for RAG pipeline - Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here
```

Replace `your-gemini-api-key-here` with your actual API key:

```bash
GEMINI_API_KEY=AIzaSyD1234567890abcdefghijklmnopqrstuvwxyz
```

### Verify Configuration

The application will automatically:
1. Load `GEMINI_API_KEY` from your `.env` file
2. Set `GOOGLE_API_KEY` environment variable (required by LangChain)
3. Log a masked version of the key at startup for verification

---

## Step 3: Verify Integration

### Start the Backend Server

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Check Startup Logs

Look for this message in the console:

```
✅ Gemini API key configured (key: AIzaSyD1...)
```

If you see this warning, your key is not set:

```
⚠️  GEMINI_API_KEY not configured! RAG pipeline will fail. 
   Get your key from: https://makersuite.google.com/app/apikey
```

---

## Step 4: Test the RAG Pipeline

### Upload a Test PDF

```bash
# Get authentication token
export TOKEN="your-auth-token-here"

# Upload a small PDF for testing
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf" \
  -F "card_density=low" \
  -F "subject=Test"
```

### Monitor Job Progress

```bash
# Get job ID from upload response, then:
curl "http://localhost:8000/api/v1/jobs/{job_id}/status" \
  -H "Authorization: Bearer $TOKEN"
```

If the API key is invalid or missing, you'll see an error message in the job status.

---

## Configuration Details

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | `""` | **Yes** (for RAG pipeline) |
| `GEMINI_MODEL_DEFAULT` | Default Gemini model to use | `gemini-2.0-flash-exp` | No |

### How It Works

1. **Configuration Loading (`app/config.py`):**
   - `Settings` class loads `GEMINI_API_KEY` from `.env`
   - `model_post_init()` sets `GOOGLE_API_KEY` environment variable
   - LangChain's `ChatGoogleGenerativeAI` uses `GOOGLE_API_KEY` automatically

2. **Startup Validation (`app/main.py`):**
   - Application checks if `GEMINI_API_KEY` is configured
   - Logs warning if missing (doesn't fail startup)
   - Masks key in logs for security

3. **Pipeline Validation (`app/workers/tasks.py`):**
   - Worker validates API key before processing PDFs
   - Raises `ValueError` with clear message if key is missing
   - Provides link to obtain key

### Security Features

✅ **API key is never logged in full** - Only first 8 characters shown  
✅ **Key stored in `.env` file** - Already in `.gitignore`  
✅ **No hardcoded keys** - All keys loaded from environment  
✅ **Clear error messages** - Users know exactly how to fix issues  
✅ **Graceful degradation** - Other endpoints work even without API key  

---

## Models Available

### Current Default: `gemini-2.0-flash-exp`

- **Speed:** Very fast (~1-2s per request)
- **Cost:** Free tier: 1500 requests/day
- **Context:** 1M token context window
- **Best for:** Development and testing

### Alternative Models

You can change the model in `backend/app/config.py`:

```python
GEMINI_MODEL_DEFAULT: str = Field(default="gemini-2.0-flash-exp")
```

Available models:
- `gemini-2.0-flash-exp` - Fastest, experimental
- `gemini-1.5-flash` - Fast, stable
- `gemini-1.5-pro` - Slower, more capable
- `gemini-1.0-pro` - Legacy, still supported

See: https://ai.google.dev/models/gemini

---

## Quotas and Limits

### Free Tier (Google AI Studio)

| Resource | Limit |
|----------|-------|
| **Requests per day** | 1,500 |
| **Requests per minute** | 15 |
| **Tokens per minute** | 1,000,000 |
| **Context window** | 1M tokens |

### Paid Tier (Google Cloud)

- Pay-as-you-go pricing
- Higher rate limits
- Production SLA guarantees
- See: https://ai.google.dev/pricing

### Rate Limiting

The RAG pipeline respects Gemini API rate limits:
- Celery worker processes jobs sequentially
- Built-in retry logic with exponential backoff
- Failed jobs are retried up to 3 times

---

## Troubleshooting

### Issue: "GEMINI_API_KEY not configured" Error

**Symptoms:**
- Job fails immediately with configuration error
- Startup warning about missing API key

**Solution:**
1. Verify `.env` file exists in `backend/` directory
2. Check `GEMINI_API_KEY` is set and not empty
3. Restart the server after updating `.env`
4. Check for typos in variable name

---

### Issue: "403 Forbidden" or "Invalid API Key"

**Symptoms:**
- Job starts but fails during RAG pipeline execution
- Error message mentions authentication failure

**Solution:**
1. Verify your API key is correct (copy-paste again)
2. Check the key hasn't expired
3. Ensure API is enabled in Google Cloud Console:
   - Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
   - Click "Enable"
4. Wait 1-2 minutes for API activation to propagate

---

### Issue: "429 Too Many Requests" or Rate Limit Errors

**Symptoms:**
- Jobs fail intermittently
- Error mentions quota exceeded

**Solution:**
1. **Short-term:** Wait and retry (automatic with Celery)
2. **Long-term:** 
   - Upgrade to paid tier
   - Reduce concurrent workers
   - Implement request throttling

---

### Issue: API Key Appears in Logs

**Symptoms:**
- Full API key visible in application logs

**Solution:**
- This should NOT happen with current implementation
- File a bug report if you see full keys in logs
- Rotate your API key immediately at: https://makersuite.google.com/app/apikey

---

## Security Best Practices

### ✅ DO

- Store API keys in `.env` file only
- Use environment variables for all secrets
- Rotate keys periodically
- Restrict API keys by IP/referrer in production
- Use separate keys for dev/staging/production
- Monitor API usage and billing

### ❌ DON'T

- Commit `.env` file to git (it's in `.gitignore`)
- Hardcode API keys in source code
- Share API keys via email/chat
- Use production keys in development
- Expose keys in client-side code
- Log full API keys

---

## Integration with LangChain

### How LangChain Uses the API Key

The `langchain-google-genai` package expects `GOOGLE_API_KEY` in the environment:

```python
from langchain_google_genai import ChatGoogleGenerativeAI

# This automatically uses os.environ["GOOGLE_API_KEY"]
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
```

### Our Configuration Flow

```
1. User sets GEMINI_API_KEY in .env file
   ↓
2. Pydantic Settings loads GEMINI_API_KEY
   ↓
3. Settings.model_post_init() sets GOOGLE_API_KEY environment variable
   ↓
4. LangChain's ChatGoogleGenerativeAI automatically finds GOOGLE_API_KEY
   ↓
5. RAG pipeline chains use the configured LLM
```

### Benefits of This Approach

- ✅ Clear separation: `GEMINI_API_KEY` is our config variable
- ✅ Automatic setup: `GOOGLE_API_KEY` is set transparently
- ✅ LangChain compatibility: Works with standard LangChain patterns
- ✅ No code changes needed in RAG chains

---

## Testing Without API Key

### Health Check Endpoints

These work without an API key:

```bash
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/
```

### Upload Endpoint

The upload endpoint works without an API key (file is uploaded to MinIO), but the **job will fail** during RAG processing.

### Worker Testing

To test the worker without API key validation:
```bash
# This is NOT recommended - for debugging only
GEMINI_API_KEY=test python run_worker.py
```

---

## Production Deployment

### Environment Setup

```bash
# Use Google Cloud Secret Manager or similar
export GEMINI_API_KEY=$(gcloud secrets versions access latest --secret="gemini-api-key")

# Or use Docker secrets
docker run -e GEMINI_API_KEY=$GEMINI_API_KEY ...
```

### Kubernetes

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: gemini-api-key
type: Opaque
data:
  GEMINI_API_KEY: <base64-encoded-key>
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anki-backend
spec:
  template:
    spec:
      containers:
      - name: backend
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-api-key
              key: GEMINI_API_KEY
```

### Docker Compose

```yaml
services:
  backend:
    env_file:
      - .env
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
```

---

## Additional Resources

- **Google AI Studio:** https://aistudio.google.com/
- **API Documentation:** https://ai.google.dev/docs
- **Gemini Models:** https://ai.google.dev/models/gemini
- **Pricing:** https://ai.google.dev/pricing
- **LangChain Integration:** https://python.langchain.com/docs/integrations/chat/google_generative_ai

---

## Support

If you encounter issues not covered in this guide:

1. Check the application logs for detailed error messages
2. Review the API key setup steps carefully
3. Consult the backend `README.md` and `API_QUICK_START.md`
4. Check Google AI Studio for API status and usage
5. File an issue with reproduction steps

---

**Last Updated:** 2025-11-23  
**Version:** 1.0.0
