# Celery Worker System

## Overview

The Anki Compendium backend uses **Celery** with **RabbitMQ** as the message broker and **Redis** as the result backend to handle asynchronous PDF-to-Anki deck generation tasks.

## Architecture

```
┌─────────────┐        ┌──────────────┐        ┌─────────────┐
│   FastAPI   │        │   RabbitMQ   │        │   Celery    │
│   Upload    │ ─────> │   (Broker)   │ ─────> │   Worker    │
│  Endpoint   │        │   Message    │        │   Process   │
└─────────────┘        └──────────────┘        └─────────────┘
                                                       │
                                                       ▼
                                              ┌──────────────┐
                                              │ RAG Pipeline │
                                              │   8 Stages   │
                                              └──────────────┘
                                                       │
                                                       ▼
                                              ┌──────────────┐
                                              │    MinIO     │
                                              │ (.apkg file) │
                                              └──────────────┘
```

## Components

### 1. Celery Application (`app/celery_app.py`)
- **Configuration**: Defines Celery settings, timeouts, retry policies
- **Task Discovery**: Auto-discovers tasks from `app/workers/`
- **Routing**: Routes tasks to appropriate queues

### 2. Worker Tasks (`app/workers/tasks.py`)
- **`process_pdf_task`**: Main task for PDF processing
  - Downloads PDF from MinIO
  - Executes RAG pipeline
  - Uploads .apkg file to MinIO
  - Updates job and user statistics

### 3. Worker Entry Point (`run_worker.py`)
- CLI script to start Celery workers
- Configured for optimal PDF processing

## Task Flow

```mermaid
sequenceDiagram
    participant User
    participant FastAPI
    participant RabbitMQ
    participant Celery Worker
    participant RAG Pipeline
    participant MinIO
    participant PostgreSQL

    User->>FastAPI: POST /api/v1/upload (PDF)
    FastAPI->>PostgreSQL: Create Job (PENDING)
    FastAPI->>MinIO: Upload PDF
    FastAPI->>RabbitMQ: Queue Task
    FastAPI-->>User: Job ID

    RabbitMQ->>Celery Worker: Pick up Task
    Celery Worker->>PostgreSQL: Update Job (PROCESSING)
    Celery Worker->>MinIO: Download PDF
    Celery Worker->>RAG Pipeline: Generate Cards
    RAG Pipeline-->>Celery Worker: .apkg file + stats
    Celery Worker->>MinIO: Upload .apkg
    Celery Worker->>PostgreSQL: Create Deck record
    Celery Worker->>PostgreSQL: Update Job (COMPLETED)
    Celery Worker->>PostgreSQL: Update User card count
```

## Running the Worker

### Development (Local)

#### Prerequisites
1. **RabbitMQ** running on `localhost:5672`
2. **Redis** running on `localhost:6379`
3. **PostgreSQL** database accessible
4. **MinIO** running on `localhost:9000`
5. **Gemini API key** configured in `.env`

#### Start Worker

```bash
# From backend directory
python run_worker.py
```

#### Worker Configuration
- **Concurrency**: 2 workers (limited by Gemini API rate limits)
- **Pool**: `solo` (better asyncio compatibility)
- **Max tasks per child**: 10 (memory management)
- **Queue**: `pdf_processing`
- **Log level**: INFO

### Production (Docker)

```bash
# Start all services including worker
docker-compose -f infra/docker-compose/docker-compose.dev.yml up -d

# View worker logs
docker logs -f anki-celery-worker
```

## Configuration

### Environment Variables (`.env`)

```ini
# Celery Broker (RabbitMQ)
CELERY_BROKER_URL=amqp://admin:changeme@localhost:5672//

# Celery Result Backend (Redis)
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Queue Names
RABBITMQ_QUEUE_PDF_PROCESSING=pdf_processing
```

### Celery Settings (`app/celery_app.py`)

| Setting | Value | Purpose |
|---------|-------|---------|
| `task_time_limit` | 7200s (2h) | Hard limit for task execution |
| `task_soft_time_limit` | 6900s (1h 55m) | Soft limit (sends signal) |
| `task_acks_late` | True | Acknowledge after completion |
| `worker_prefetch_multiplier` | 1 | Fetch one task at a time |
| `task_reject_on_worker_lost` | True | Reject task if worker crashes |
| `task_autoretry_for` | (Exception,) | Retry on any exception |
| `max_retries` | 3 | Maximum retry attempts |
| `default_retry_delay` | 300s (5min) | Delay between retries |

## Task Details

### `process_pdf_task(job_id: str)`

**Purpose**: Asynchronously process PDF and generate Anki deck

**Arguments**:
- `job_id`: UUID of the job to process

**Returns**:
```python
{
    "status": "completed",
    "job_id": "uuid",
    "deck_id": "uuid",
    "num_cards": 50,
    "num_pages": 10,
    "num_chunks": 20,
    "num_topics": 5,
    "num_tags": 8
}
```

**Error Handling**:
- Automatic retry on failure (max 3 attempts)
- Exponential backoff with jitter
- Job status updated to FAILED after max retries
- Error messages and stack traces stored in database

**Stages**:
1. ✅ Retrieve job from database
2. ✅ Update status to PROCESSING
3. ✅ Download PDF from MinIO
4. ✅ Run RAG pipeline (8 stages)
5. ✅ Upload .apkg to MinIO
6. ✅ Create Deck record
7. ✅ Update job status to COMPLETED
8. ✅ Update user card count
9. ✅ Cleanup temp files

## Monitoring

### Celery Flower (Web UI)

```bash
# Install Flower
pip install flower

# Run Flower
celery -A app.celery_app flower --port=5555

# Access UI
# http://localhost:5555
```

Features:
- Real-time task monitoring
- Task history and statistics
- Worker status and health
- Rate limit management

### CLI Monitoring

```bash
# List active tasks
celery -A app.celery_app inspect active

# List scheduled tasks
celery -A app.celery_app inspect scheduled

# Worker status
celery -A app.celery_app inspect stats

# Purge queue (delete all pending tasks)
celery -A app.celery_app purge
```

### Logs

```bash
# Worker logs (if running in background)
tail -f /var/log/celery/worker.log

# Docker logs
docker logs -f anki-celery-worker

# Real-time log filtering
celery -A app.celery_app worker --loglevel=debug
```

## Debugging

### Common Issues

#### 1. **Task Not Picked Up**

**Symptoms**: Job stays in PENDING status indefinitely

**Causes**:
- Worker not running
- Worker listening to wrong queue
- RabbitMQ connection issue

**Solutions**:
```bash
# Check worker status
celery -A app.celery_app inspect active

# Check RabbitMQ queues
rabbitmqctl list_queues

# Restart worker
python run_worker.py
```

#### 2. **Task Fails Immediately**

**Symptoms**: Job goes to FAILED without processing

**Causes**:
- Missing dependencies
- Configuration errors
- Database connection issue
- MinIO not accessible

**Solutions**:
```bash
# Check worker logs
tail -f /var/log/celery/worker.log

# Test database connection
python -c "from app.database import engine; print('OK')"

# Test MinIO connection
python -c "from app.services.storage_service import storage_service; print('OK')"
```

#### 3. **RAG Pipeline Fails**

**Symptoms**: Task retries multiple times, then fails

**Causes**:
- Invalid Gemini API key
- Gemini API rate limit exceeded
- PDF parsing error
- Insufficient memory

**Solutions**:
```bash
# Check Gemini API key
echo $GEMINI_API_KEY

# Check PDF file
python -c "import pymupdf; doc = pymupdf.open('test.pdf'); print(len(doc))"

# Increase memory limits
# Edit docker-compose.yml or run with more resources
```

#### 4. **Worker Out of Memory**

**Symptoms**: Worker crashes during processing, tasks rejected

**Causes**:
- Large PDF files
- Memory leaks
- Too many concurrent tasks

**Solutions**:
```bash
# Reduce concurrency
celery -A app.celery_app worker --concurrency=1

# Restart worker more frequently
celery -A app.celery_app worker --max-tasks-per-child=5

# Monitor memory usage
top -p $(pgrep -f celery)
```

### Debug Mode

Run worker with verbose logging:

```bash
python run_worker.py --loglevel=debug
```

Or with Python debugger:

```python
# Add breakpoint in tasks.py
import pdb; pdb.set_trace()

# Run worker with --pool=solo
celery -A app.celery_app worker --loglevel=info --pool=solo
```

## Testing

### Manual Testing

```python
# Test task dispatch
from app.workers.tasks import process_pdf_task
result = process_pdf_task.delay("job-uuid-here")
print(result.id)  # Task ID

# Check task status
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE

# Get result (blocking)
print(result.get(timeout=3600))  # Wait up to 1 hour
```

### Unit Testing

```python
# tests/workers/test_pdf_processor.py
import pytest
from unittest.mock import patch, AsyncMock
from app.workers.tasks import process_pdf_task

@pytest.mark.asyncio
async def test_process_pdf_task_success(mock_db, mock_job):
    """Test successful PDF processing."""
    with patch('app.workers.tasks.job_service') as mock_service:
        mock_service.get_job.return_value = mock_job
        
        result = process_pdf_task.apply(args=["job-id"]).get()
        
        assert result['status'] == 'completed'
        assert result['num_cards'] > 0
```

## Performance Optimization

### Concurrency Tuning

```bash
# More workers for higher throughput (watch Gemini API limits)
celery -A app.celery_app worker --concurrency=4

# Use threading pool for I/O-bound tasks
celery -A app.celery_app worker --pool=threads --concurrency=10

# Use gevent for async I/O
celery -A app.celery_app worker --pool=gevent --concurrency=100
```

### Resource Limits

```bash
# Limit memory per worker
celery -A app.celery_app worker --max-memory-per-child=500000  # 500MB

# Restart worker after N tasks
celery -A app.celery_app worker --max-tasks-per-child=50
```

### Task Prioritization

```python
# High priority task
process_pdf_task.apply_async(args=[job_id], priority=9)

# Low priority task
process_pdf_task.apply_async(args=[job_id], priority=1)
```

## Security

### Best Practices

1. **Secure Broker Connection**
   ```ini
   CELERY_BROKER_URL=amqps://user:pass@broker.example.com:5671//
   ```

2. **Encrypt Result Backend**
   ```ini
   CELERY_RESULT_BACKEND=rediss://redis.example.com:6380/0
   ```

3. **Validate Task Arguments**
   ```python
   # Always validate job_id is a valid UUID
   try:
       job_id_uuid = UUID(job_id)
   except ValueError:
       raise ValueError("Invalid job_id format")
   ```

4. **Rate Limiting**
   ```python
   @celery_app.task(rate_limit='10/m')  # 10 tasks per minute
   def process_pdf_task(job_id: str):
       ...
   ```

## Deployment

### Docker Compose

```yaml
services:
  celery-worker:
    build: ./backend
    command: python run_worker.py
    environment:
      - CELERY_BROKER_URL=amqp://rabbitmq:5672//
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/db
      - MINIO_ENDPOINT=minio:9000
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - rabbitmq
      - redis
      - postgres
      - minio
    restart: always
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
spec:
  replicas: 2
  selector:
    matchLabels:
      app: celery-worker
  template:
    metadata:
      labels:
        app: celery-worker
    spec:
      containers:
      - name: worker
        image: anki-compendium-backend:latest
        command: ["python", "run_worker.py"]
        env:
        - name: CELERY_BROKER_URL
          valueFrom:
            secretKeyRef:
              name: celery-secret
              key: broker-url
        resources:
          limits:
            memory: "2Gi"
            cpu: "1000m"
          requests:
            memory: "512Mi"
            cpu: "250m"
```

## Scaling

### Horizontal Scaling

```bash
# Run multiple worker instances
python run_worker.py &  # Worker 1
python run_worker.py &  # Worker 2
python run_worker.py &  # Worker 3
```

### Autoscaling (Kubernetes HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: celery-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: celery-worker
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## Troubleshooting Checklist

- [ ] RabbitMQ is running and accessible
- [ ] Redis is running and accessible
- [ ] PostgreSQL is accessible
- [ ] MinIO is accessible
- [ ] Gemini API key is valid
- [ ] Worker is running (`celery inspect active`)
- [ ] Worker is listening to correct queue (`pdf_processing`)
- [ ] Job exists in database
- [ ] PDF file exists in MinIO
- [ ] Sufficient disk space in `/tmp`
- [ ] Sufficient memory available
- [ ] No firewall blocking connections
- [ ] Correct Python version (3.11+)
- [ ] All dependencies installed

## References

- [Celery Documentation](https://docs.celeryq.dev/)
- [RabbitMQ Documentation](https://www.rabbitmq.com/documentation.html)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Documentation](https://flower.readthedocs.io/)
