"""
Anki Compendium - Main FastAPI Application
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings
from app.core.logging import setup_logging
from app.database import Base, engine

# Import all models to ensure they are registered with SQLAlchemy
from app.models import (  # noqa: F401
    User, Deck, Job, Setting, Subscription, AuditLog, Notification
)

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events with enhanced startup validation."""
    import time
    from sqlalchemy import text
    
    from app.core.logging import logger
    
    startup_start = time.time()
    logger.info("🚀 Starting Anki Compendium API...")
    
    try:
        # Step 0: Validate API key configuration
        logger.info("Validating configuration...")
        if not settings.GEMINI_API_KEY:
            logger.warning(
                "⚠️  GEMINI_API_KEY not configured! "
                "RAG pipeline will fail. Get your key from: https://makersuite.google.com/app/apikey"
            )
        else:
            # Mask key for logging (show first 8 chars only)
            masked_key = settings.GEMINI_API_KEY[:8] + "..." if len(settings.GEMINI_API_KEY) > 8 else "***"
            logger.info(f"✅ Gemini API key configured (key: {masked_key})")
        
        # Step 1: Validate database connectivity with retry
        logger.info("Validating database connection...")
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(1, max_retries + 1):
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                logger.info(f"✅ Database connection validated (attempt {attempt})")
                break
            except Exception as e:
                if attempt == max_retries:
                    logger.error(f"❌ Database connection failed after {max_retries} attempts: {e}")
                    raise
                logger.warning(f"Database connection attempt {attempt} failed, retrying in {retry_delay}s...")
                await __import__('asyncio').sleep(retry_delay)
        
        # Step 2: Create database tables (development only)
        if settings.ENVIRONMENT == "development":
            logger.info("Creating database tables (development mode)...")
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("✅ Database schema synchronized")
            except Exception as e:
                logger.error(f"❌ Database schema creation failed: {e}")
                raise
        
        # Step 3: Startup complete
        startup_time = time.time() - startup_start
        logger.info(f"✅ Application startup complete in {startup_time:.2f}s")
        
    except Exception as e:
        logger.error(f"❌ Application startup failed: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("👋 Shutting down Anki Compendium API...")
    try:
        await engine.dispose()
        logger.info("✅ Database connections closed gracefully")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}", exc_info=True)


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

# Custom middleware
from app.core.middleware import (
    add_process_time_header,
    rate_limit_auth_middleware,
    security_headers_middleware
)

app.middleware("http")(security_headers_middleware)
app.middleware("http")(rate_limit_auth_middleware)
app.middleware("http")(add_process_time_header)

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
