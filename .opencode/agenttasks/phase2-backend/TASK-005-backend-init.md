---
task_id: "TASK-005-BACKEND-INIT"
title: "Initialize Backend FastAPI Project Structure"
phase: "Phase 2: Backend Core"
complexity: "small"
estimated_duration: "2-3 hours"
assigned_to: "developer"
dependencies: ["TASK-001-DOCKERCOMPOSE"]
status: "pending"
priority: "high"
created_at: "2025-11-22"
---

# Task: Initialize Backend FastAPI Project Structure

## Objective
Create a production-ready FastAPI project structure with proper organization, configuration management, database setup (SQLAlchemy + Alembic), and basic health check endpoints.

## Context
This establishes the foundation for all backend development. The structure must be clean, scalable, and follow FastAPI best practices.

---

## Requirements

### Functional Requirements
1. FastAPI application with modular structure
2. Configuration management (environment variables, settings)
3. Database connection setup (PostgreSQL via SQLAlchemy)
4. Alembic for database migrations
5. Health check and info endpoints
6. CORS middleware configuration
7. Logging setup
8. Error handling middleware

### Non-Functional Requirements
- Type hints throughout (Python 3.11+)
- Async/await patterns for database operations
- Pydantic models for validation
- Clean separation of concerns (routers, services, models, schemas)
- Ready for Celery integration (workers)

---

## File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Settings and configuration
│   ├── database.py                # Database connection and session
│   ├── dependencies.py            # FastAPI dependencies (auth, db session, etc.)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py          # Main API router
│   │   │   ├── health.py          # Health check endpoints
│   │   │   └── endpoints/         # Feature-specific endpoints (placeholder)
│   │   │       └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py            # Security utilities (future: JWT, hashing)
│   │   ├── logging.py             # Logging configuration
│   │   └── middleware.py          # Custom middleware
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py                # SQLAlchemy base model
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── health.py              # Pydantic schemas for health endpoints
│   ├── services/
│   │   └── __init__.py            # Business logic layer (placeholder)
│   └── rag/                       # RAG pipeline (from TASK-004, placeholder)
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_main.py               # Basic app tests
│   └── api/
│       └── test_health.py         # Health endpoint tests
├── alembic/
│   ├── versions/                  # Migration files
│   ├── env.py                     # Alembic environment
│   ├── script.py.mako             # Migration template
│   └── README
├── alembic.ini                    # Alembic configuration
├── requirements.txt               # Python dependencies
├── requirements-dev.txt           # Development dependencies
├── .env.example                   # Environment variables template
├── .gitignore
├── Dockerfile                     # Container image definition
├── pyproject.toml                 # Python project metadata
└── README.md
```

---

## Acceptance Criteria

### Must Have
- [ ] FastAPI app starts successfully: `uvicorn app.main:app --reload`
- [ ] Health check endpoint responds: `GET /api/v1/health`
- [ ] Info endpoint responds: `GET /api/v1/info`
- [ ] Database connection successful (PostgreSQL from Docker Compose)
- [ ] Alembic migrations configured and working
- [ ] CORS middleware configured
- [ ] Logging to stdout (structured JSON)
- [ ] Environment variables loaded from `.env` file
- [ ] Basic tests pass: `pytest`
- [ ] Type checking passes: `mypy app/`
- [ ] Linting passes: `ruff check .`

### Nice to Have
- [ ] OpenAPI docs accessible at `/docs`
- [ ] ReDoc docs accessible at `/redoc`
- [ ] Automatic API documentation generation
- [ ] Docker image builds successfully

---

## Technical Specifications

### Dependencies (requirements.txt)

```txt
# Core Framework
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Database
sqlalchemy>=2.0.23
psycopg2-binary>=2.9.9
alembic>=1.12.1

# Async support
asyncpg>=0.29.0

# Validation & Serialization
python-multipart>=0.0.6
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Utilities
python-dotenv>=1.0.0
```

### Development Dependencies (requirements-dev.txt)

```txt
# Testing
pytest>=7.4.3
pytest-asyncio>=0.21.1
pytest-cov>=4.1.0
httpx>=0.25.2

# Code Quality
ruff>=0.1.6
mypy>=1.7.1
black>=23.11.0

# Type Stubs
types-passlib>=1.7.7
sqlalchemy[mypy]>=2.0.23
```

### Main Application (app/main.py)

```python
"""
Anki Compendium - Main FastAPI Application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.database import engine, Base

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting Anki Compendium API...")
    
    # Create database tables (for development only)
    # In production, use Alembic migrations
    if settings.ENVIRONMENT == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown
    print("👋 Shutting down Anki Compendium API...")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Anki Compendium API",
    description="AI-powered Anki flashcard generation from PDFs",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Anki Compendium API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
```

### Configuration (app/config.py)

```python
"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Anki Compendium"
    
    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://ankiuser:changeme@localhost:5432/anki_compendium_dev",
        env="DATABASE_URL"
    )
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    # Security (future)
    SECRET_KEY: str = Field(default="change-this-in-production", env="SECRET_KEY")
    
    # Gemini AI (future)
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    
    # MinIO (future)
    MINIO_ENDPOINT: str = Field(default="localhost:9000", env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="changeme", env="MINIO_SECRET_KEY")
    
    # RabbitMQ (future)
    RABBITMQ_URL: str = Field(
        default="amqp://admin:changeme@localhost:5672/",
        env="RABBITMQ_URL"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

### Database Setup (app/database.py)

```python
"""
Database connection and session management.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Health Endpoints (app/api/v1/health.py)

```python
"""
Health check and system info endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_db
from app.schemas.health import HealthResponse, InfoResponse
from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.
    Verifies database connectivity.
    """
    try:
        # Check database connection
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return HealthResponse(
        status="healthy" if db_status == "healthy" else "unhealthy",
        database=db_status,
    )


@router.get("/info", response_model=InfoResponse)
async def info():
    """
    System information endpoint.
    Returns application metadata.
    """
    return InfoResponse(
        name=settings.PROJECT_NAME,
        version="0.1.0",
        environment=settings.ENVIRONMENT,
    )
```

### Pydantic Schemas (app/schemas/health.py)

```python
"""
Pydantic schemas for health endpoints.
"""
from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str


class InfoResponse(BaseModel):
    """System info response."""
    name: str
    version: str
    environment: str
```

### API Router (app/api/v1/router.py)

```python
"""
Main API v1 router.
"""
from fastapi import APIRouter

from app.api.v1 import health

api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router)
```

### Logging Setup (app/core/logging.py)

```python
"""
Logging configuration.
"""
import logging
import sys
from typing import Any
import json


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_obj)


def setup_logging():
    """Setup application logging."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Set log level for specific loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
```

### Pytest Configuration (tests/conftest.py)

```python
"""
Pytest configuration and fixtures.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.database import Base, get_db
from app.config import settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://ankiuser:changeme@localhost:5432/anki_compendium_test"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def test_db():
    """Create test database and tables."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def client(test_db):
    """Create test client with test database."""
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()
```

### Basic Tests (tests/api/test_health.py)

```python
"""
Tests for health endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"]
    assert "database" in data


@pytest.mark.asyncio
async def test_info(client: AsyncClient):
    """Test info endpoint."""
    response = await client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Anki Compendium"
    assert "version" in data
    assert "environment" in data
```

---

## Testing Requirements

### Manual Testing

```bash
# Start backend (from backend/ directory)
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt

# Copy .env.example to .env and configure
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# Test endpoints
curl http://localhost:8000/
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/info

# Visit docs
open http://localhost:8000/docs
```

### Automated Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Type checking
mypy app/

# Linting
ruff check .
```

---

## Success Criteria
- FastAPI application structure created and organized
- Server starts without errors
- Health check endpoints functional
- Database connection working
- Alembic migrations configured
- Tests passing
- Documentation accessible
- Code quality checks passing

## Deliverables
1. Complete backend/ directory structure
2. Working FastAPI application with health endpoints
3. Database setup with SQLAlchemy
4. Alembic migrations configured
5. Tests with fixtures and coverage
6. requirements.txt and requirements-dev.txt
7. .env.example template
8. README.md with setup instructions

## Notes
- Use async/await throughout for better performance
- Keep configuration centralized in config.py
- Follow FastAPI best practices for project structure
- Prepare for Celery integration (separate workers)
- Ready for TASK-004 (LangChain integration)

## References
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
