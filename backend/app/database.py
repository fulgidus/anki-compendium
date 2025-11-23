"""
Database connection and session management.
"""
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from app.config import settings

# Create async engine with optimized connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    # Connection pool configuration for reliability
    pool_size=5,  # Number of connections to maintain
    max_overflow=10,  # Additional connections when pool is exhausted
    pool_timeout=30,  # Seconds to wait for connection from pool
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before using them
    # Connection timeout settings
    connect_args={
        "timeout": 10,  # Connection timeout in seconds
        "command_timeout": 60,  # Query timeout in seconds
        "server_settings": {
            "application_name": "anki_compendium_api"
        }
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
