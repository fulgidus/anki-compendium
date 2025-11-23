# Anki Compendium - Backend API

AI-powered FastAPI backend for generating Anki flashcards from PDF documents.

## Features

- **FastAPI** framework with async/await support
- **PostgreSQL** database with SQLAlchemy ORM (async)
- **Alembic** for database migrations
- **Pydantic** for data validation
- **Health check** endpoints
- **CORS** middleware configured
- **Structured logging** (JSON format)
- **Type hints** throughout
- **Comprehensive testing** with pytest

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (with pgvector extension)
- Docker Compose (for local development environment)

## Setup

### 1. Start Infrastructure Services

First, start the required services (PostgreSQL, RabbitMQ, MinIO, Keycloak):

```bash
cd ../infra/docker-compose
docker-compose -f docker-compose.dev.yml up -d
```

Verify all services are running:

```bash
./smoke-test.sh
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration (defaults work with Docker Compose)
nano .env
```

**Important:** Configure your **Google Gemini API key** for the RAG pipeline:

```bash
# Get your free API key from: https://makersuite.google.com/app/apikey
# Then add it to your .env file:
GEMINI_API_KEY=your-actual-api-key-here
```

📖 **See [GEMINI_API_SETUP.md](./GEMINI_API_SETUP.md) for detailed setup instructions.**

### 4. Initialize Database

```bash
# Run migrations
alembic upgrade head
```

### 5. Start Development Server

```bash
# Start FastAPI server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Health & Info
- `GET /` - Root endpoint with API information
- `GET /api/v1/health` - Health check (includes database connectivity)
- `GET /api/v1/info` - System information

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_health.py

# Run with verbose output
pytest -v
```

## Code Quality

```bash
# Type checking with mypy
mypy app/

# Linting with ruff
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code with black
black .
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   │   └── v1/           # API version 1
│   │       ├── health.py # Health check endpoints
│   │       └── router.py # Main API router
│   ├── core/             # Core utilities
│   │   ├── logging.py    # Logging configuration
│   │   ├── security.py   # Security utilities
│   │   └── middleware.py # Custom middleware
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic layer
│   ├── rag/              # RAG pipeline (future)
│   ├── config.py         # Application settings
│   ├── database.py       # Database connection
│   └── main.py           # FastAPI app entry point
├── tests/                # Test suite
│   ├── api/              # API tests
│   └── conftest.py       # Pytest fixtures
├── alembic/              # Database migrations
├── requirements.txt      # Python dependencies
├── requirements-dev.txt  # Development dependencies
└── pyproject.toml        # Python project configuration
```

## Environment Variables

See `.env.example` for all available configuration options.

### Key Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `GEMINI_API_KEY` | Google Gemini API key (for RAG pipeline) | **Yes** |
| `ENVIRONMENT` | development/staging/production | Yes |
| `DEBUG` | Enable debug mode | No |
| `CORS_ORIGINS` | Allowed CORS origins | Yes |
| `SECRET_KEY` | Application secret key | Yes |
| `MINIO_ENDPOINT` | MinIO S3 endpoint | Yes |
| `RABBITMQ_URL` | RabbitMQ connection string | Yes |

📖 **For Gemini API setup, see [GEMINI_API_SETUP.md](./GEMINI_API_SETUP.md)**

## Docker Support

Build and run with Docker:

```bash
# Build image
docker build -t anki-compendium-backend .

# Run container
docker run -p 8000:8000 \
  --env-file .env \
  anki-compendium-backend
```

## Next Steps

- **Phase 2**: Implement LangChain RAG pipeline (TASK-004)
- **Phase 3**: Add authentication with Keycloak
- **Phase 4**: Implement PDF processing and card generation
- **Phase 5**: Add Celery workers for async tasks

## Contributing

See main project README for contribution guidelines.

## License

See main project LICENSE file.
