"""
Pytest configuration and fixtures.
"""
from collections.abc import AsyncGenerator
from datetime import timedelta
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from unittest.mock import AsyncMock, patch

from app.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.database import Base, get_db
from app.main import app
from app.models.user import User

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://ankiuser:changeme@localhost:5432/anki_compendium_test"

# Test user credentials
TEST_USER_EMAIL = "test@example.com"
TEST_USER_USERNAME = "testuser"
TEST_USER_PASSWORD = "TestPassword123!"
TEST_USER_KEYCLOAK_ID = "test-keycloak-id-" + str(uuid4())


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
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
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with test database."""
    from httpx import ASGITransport

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(test_db: AsyncSession) -> User:
    """
    Create a test user in the database.
    
    Note: In real tests with Keycloak, you'd need to mock Keycloak API calls
    or have a test Keycloak instance.
    """
    user = User(
        id=uuid4(),
        keycloak_id=TEST_USER_KEYCLOAK_ID,
        email=TEST_USER_EMAIL,
        username=TEST_USER_USERNAME,
        display_name="Test User",
        subscription_tier="free",
        cards_generated_month=0,
        cards_limit_month=settings.FREE_TIER_CARD_LIMIT,
        is_active=True,
        is_admin=False
    )
    
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user


@pytest.fixture
def test_password() -> str:
    """Return test user password."""
    return TEST_USER_PASSWORD


@pytest.fixture
async def inactive_user(test_db: AsyncSession) -> User:
    """Create an inactive test user."""
    user = User(
        id=uuid4(),
        keycloak_id="inactive-keycloak-id-" + str(uuid4()),
        email="inactive@example.com",
        username="inactiveuser",
        display_name="Inactive User",
        subscription_tier="free",
        cards_generated_month=0,
        cards_limit_month=settings.FREE_TIER_CARD_LIMIT,
        is_active=False,
        is_admin=False
    )
    
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user


@pytest.fixture
def auth_tokens(test_user: User) -> dict:
    """
    Generate authentication tokens for test user.
    
    Returns dict with access_token and refresh_token.
    """
    access_token = create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email},
        expires_delta=timedelta(minutes=15)
    )
    
    refresh_token = create_refresh_token(
        data={"sub": str(test_user.id)}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@pytest.fixture
def auth_headers(auth_tokens: dict) -> dict:
    """
    Get authentication headers with Bearer token.
    
    Use this fixture to make authenticated requests.
    """
    return {
        "Authorization": f"Bearer {auth_tokens['access_token']}"
    }


@pytest.fixture
def db(test_db: AsyncSession) -> AsyncSession:
    """Alias for test_db to match expected naming in endpoints."""
    return test_db


@pytest.fixture
def mock_keycloak():
    """
    Mock Keycloak API responses for testing without real Keycloak instance.
    
    Usage in tests:
        @pytest.mark.usefixtures("mock_keycloak")
        async def test_something(client):
            ...
    """
    with patch("app.services.auth_service.httpx.AsyncClient") as mock_client:
        # Mock successful admin token
        mock_admin_response = AsyncMock()
        mock_admin_response.status_code = 200
        mock_admin_response.json.return_value = {
            "access_token": "mock_admin_token",
            "expires_in": 3600
        }
        
        # Mock successful user creation
        mock_create_response = AsyncMock()
        mock_create_response.status_code = 201
        mock_create_response.headers = {
            "Location": f"http://keycloak/users/{TEST_USER_KEYCLOAK_ID}"
        }
        
        # Mock successful login
        mock_login_response = AsyncMock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {
            "access_token": "mock_keycloak_access_token",
            "refresh_token": "mock_keycloak_refresh_token",
            "expires_in": 900
        }
        
        # Mock userinfo
        mock_userinfo_response = AsyncMock()
        mock_userinfo_response.status_code = 200
        mock_userinfo_response.json.return_value = {
            "sub": TEST_USER_KEYCLOAK_ID,
            "email": TEST_USER_EMAIL,
            "preferred_username": TEST_USER_USERNAME
        }
        
        # Configure mock client
        mock_instance = AsyncMock()
        mock_instance.post.return_value = mock_login_response
        mock_instance.get.return_value = mock_userinfo_response
        
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        yield mock_client
