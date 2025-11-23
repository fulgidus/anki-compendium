# n8n Deployment Guide

## Overview

n8n handles the entire document processing pipeline, eliminating the need for Celery workers and RabbitMQ.

---

## Architecture

```
┌────────────────────────────────────────────────┐
│        FastAPI Backend (CRUD + Auth)            │
│  POST /api/v1/upload → Triggers n8n webhook    │
└──────────────┬─────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────┐
│              n8n Workflow Engine                │
│  • Webhook trigger                              │
│  • PostgreSQL operations                        │
│  • MinIO file operations                        │
│  • Python Code nodes (RAG processing)           │
│  • HTTP Request nodes (Gemini API)              │
│  • Loop/batch processing                        │
└────────────────────────────────────────────────┘
```

---

## Deployment Steps

### 1. Build Custom n8n Image

```bash
cd infra/k8s/n8n
docker build -t <your-registry>/n8n-anki:latest .
docker push <your-registry>/n8n-anki:latest
```

**Update `deployment.yaml`**:
```yaml
containers:
- name: n8n
  image: <your-registry>/n8n-anki:latest
```

### 2. Create PostgreSQL Database for n8n

```sql
-- Connect to PostgreSQL
psql -h postgres -U ankiuser -d anki_compendium_prod

-- Create n8n database
CREATE DATABASE n8n;
```

### 3. Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f infra/k8s/namespace.yaml

# Create secrets (if not already done)
kubectl create secret generic anki-secrets \
  --namespace=anki-compendium \
  --from-literal=POSTGRES_PASSWORD='<password>' \
  --from-literal=GEMINI_API_KEY='<key>' \
  --from-literal=MINIO_ROOT_USER='minioadmin' \
  --from-literal=MINIO_ROOT_PASSWORD='<password>'

# Deploy n8n + Redis
kubectl apply -f infra/k8s/n8n/deployment.yaml

# Verify deployment
kubectl get pods -n anki-compendium -l app=n8n
kubectl logs -n anki-compendium -l app=n8n --tail=100
```

### 4. Access n8n UI

```bash
# Port forward for local access
kubectl port-forward -n anki-compendium svc/n8n 5678:5678

# Open browser
open http://localhost:5678
```

**First-time setup:**
1. Create owner account
2. Set up credentials:
   - PostgreSQL (for job/deck queries)
   - HTTP Header Auth (for MinIO)
   - HTTP Query Auth (for Gemini API)

### 5. Import Workflow

```bash
# In n8n UI: Workflows → Import from File
# Select: infra/n8n/workflow-anki-processing.json
```

**Configure credentials:**
- PostgreSQL: `postgres://ankiuser:<password>@postgres:5432/anki_compendium_prod`
- Gemini API Key: Use environment variable `{{ $env.GEMINI_API_KEY }}`
- MinIO: Configure S3-compatible credentials

### 6. Update Backend to Trigger n8n

```python
# backend/app/api/v1/upload.py

@router.post("/upload")
async def upload_pdf(...):
    # ... existing code ...
    
    # Instead of Celery task:
    # process_pdf_task.delay(str(job.id))
    
    # Trigger n8n webhook
    import httpx
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{settings.N8N_WEBHOOK_URL}/webhook/process-pdf",
            json={
                "job_id": str(job.id),
                "user_id": str(user.id)
            },
            timeout=10.0  # Don't wait for response
        )
    
    return job
```

---

## Configuration

### Environment Variables

Set in `deployment.yaml` or via ConfigMap:

```yaml
# n8n Core
N8N_HOST: "n8n.ankicompendium.com"
N8N_PROTOCOL: "https"
WEBHOOK_URL: "https://n8n.ankicompendium.com/"

# Database
DB_TYPE: "postgresdb"
DB_POSTGRESDB_HOST: "postgres"
DB_POSTGRESDB_DATABASE: "n8n"

# Execution
EXECUTIONS_MODE: "queue"  # For horizontal scaling
QUEUE_BULL_REDIS_HOST: "redis"

# External Services
GEMINI_API_KEY: "<from-secret>"
MINIO_ENDPOINT: "http://minio:9000"
BACKEND_URL: "http://backend:8000"
```

---

## Scaling

### Horizontal Scaling

n8n StatefulSet can scale horizontally with queue mode:

```bash
# Scale to 3 replicas
kubectl scale statefulset n8n --replicas=3 -n anki-compendium
```

**Requirements:**
- `EXECUTIONS_MODE=queue` (already configured)
- Redis for queue coordination (already deployed)
- Shared PostgreSQL database (already configured)

### Resource Limits

Adjust based on workload:

```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"  # Increase for heavy Python processing
    cpu: "1000m"
```

---

## Monitoring

### n8n Metrics

Access built-in metrics:

```bash
# Port forward to metrics endpoint
kubectl port-forward -n anki-compendium svc/n8n 9000:9000

# Prometheus scrape endpoint
curl http://localhost:9000/metrics
```

### Execution History

View in n8n UI:
- **Executions** tab shows all workflow runs
- Filter by status (success, error, waiting)
- View detailed logs per execution
- Retry failed executions

### Logging

```bash
# Real-time logs
kubectl logs -n anki-compendium -l app=n8n -f

# Logs from specific pod
kubectl logs -n anki-compendium n8n-0 -f
```

---

## Troubleshooting

### Workflow Not Triggering

**Check webhook URL:**
```bash
kubectl exec -n anki-compendium n8n-0 -- env | grep WEBHOOK
```

**Test webhook manually:**
```bash
curl -X POST https://n8n.ankicompendium.com/webhook/process-pdf \
  -H "Content-Type: application/json" \
  -d '{"job_id": "test-id", "user_id": "test-user"}'
```

### Python Code Node Errors

**Check installed packages:**
```bash
kubectl exec -n anki-compendium n8n-0 -- pip3 list | grep -E "PyMuPDF|langchain|genanki"
```

**View Code node logs:**
- In n8n UI: Workflow → Execution → Click on Code node
- View input/output and error messages

### Memory Issues

**Increase memory limits:**
```yaml
resources:
  limits:
    memory: "4Gi"  # For large PDFs
```

**Or process in smaller batches:**
- Reduce `page_end - page_start`
- Process 10-20 pages at a time

### Queue Stuck

**Check Redis:**
```bash
kubectl exec -n anki-compendium redis-0 -- redis-cli PING
```

**Clear queue (emergency):**
```bash
kubectl exec -n anki-compendium redis-0 -- redis-cli FLUSHALL
```

---

## Cost Optimization

### OVH Kubernetes Monthly Cost

```
n8n StatefulSet (2x 1GB):      ~€20/mese
Redis (1x 512MB):              ~€5/mese
PostgreSQL (shared):           €0 (già esistente)
MinIO (shared):                €0 (già esistente)
Keycloak (shared):             €0 (già esistente)
Backend (shared):              €0 (già esistente)
----------------------------------------------
TOTAL ADDITIONAL:              ~€25/mese

RISPARMI vs Celery+RabbitMQ:
RabbitMQ StatefulSet:          -€10/mese
Celery Workers (3x 1GB):       -€30/mese
----------------------------------------------
NET SAVINGS:                   -€15/mese 💰
```

---

## Security

### Webhook Security

Add authentication to webhook trigger:

```yaml
# In workflow JSON
"authentication": "headerAuth",
"headerAuth": {
  "name": "X-Webhook-Secret",
  "value": "={{ $env.WEBHOOK_SECRET }}"
}
```

Backend sends secret:
```python
headers = {"X-Webhook-Secret": settings.N8N_WEBHOOK_SECRET}
```

### Network Policies

Restrict n8n access:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: n8n-policy
  namespace: anki-compendium
spec:
  podSelector:
    matchLabels:
      app: n8n
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend  # Only backend can trigger
  - from:
    - podSelector:
        matchLabels:
          app: ingress-nginx  # External access via Ingress
```

---

## Backup & Recovery

### Backup n8n Database

```bash
# Backup n8n workflows and credentials
kubectl exec -n anki-compendium postgres-0 -- \
  pg_dump -U ankiuser n8n | gzip > n8n-backup-$(date +%Y%m%d).sql.gz
```

### Export Workflows

In n8n UI:
- Workflows → Select workflow → Download
- Store in version control: `infra/n8n/workflows/`

### Restore

```bash
# Restore from backup
gunzip -c n8n-backup-20251123.sql.gz | \
  kubectl exec -i -n anki-compendium postgres-0 -- \
    psql -U ankiuser n8n
```

---

**Maintainer**: DevOps Team  
**Last Updated**: 2025-11-23
