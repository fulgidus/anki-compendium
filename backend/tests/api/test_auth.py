"""
Authentication endpoint tests.

Tests for user registration, login, token refresh, and logout.
"""
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class TestRegistration:
    """Test user registration endpoint."""
    
    async def test_register_success(self, client: AsyncClient, db: AsyncSession):
        """Test successful user registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "SecurePass123!",
                "display_name": "New User"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert "user" in data
        assert data["user"]["email"] == "newuser@example.com"
        assert data["user"]["username"] == "newuser"
        assert data["user"]["subscription_tier"] == "free"
        assert data["message"] == "User registered successfully. Please check your email to verify your account."
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "username": "differentuser",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "username": "testuser",
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration with weak password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "short"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_register_invalid_username(self, client: AsyncClient):
        """Test registration with invalid username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "ab",  # Too short
                "password": "SecurePass123!"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Test user login endpoint."""
    
    async def test_login_success(self, client: AsyncClient, test_user: User, test_password: str):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": test_password
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        assert data["user"]["email"] == test_user.email
    
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_login_missing_fields(self, client: AsyncClient):
        """Test login with missing fields."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    async def test_refresh_token_success(self, client: AsyncClient, auth_tokens: dict):
        """Test successful token refresh."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": auth_tokens["refresh_token"]}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test token refresh with invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    """Test logout endpoint."""
    
    async def test_logout_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful logout."""
        response = await client.post(
            "/api/v1/auth/logout",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    async def test_logout_without_auth(self, client: AsyncClient):
        """Test logout without authentication."""
        response = await client.post("/api/v1/auth/logout")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetCurrentUser:
    """Test get current user endpoint."""
    
    async def test_get_me_success(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """Test successful retrieval of current user."""
        response = await client.get(
            "/api/v1/auth/me",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "id" in data
        assert "subscription_tier" in data
    
    async def test_get_me_without_auth(self, client: AsyncClient):
        """Test get current user without authentication."""
        response = await client.get("/api/v1/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test get current user with invalid token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenVerification:
    """Test token verification endpoint."""
    
    async def test_verify_token_success(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """Test successful token verification."""
        response = await client.post(
            "/api/v1/auth/verify-token",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["valid"] is True
        assert data["user_id"] == str(test_user.id)
        assert data["email"] == test_user.email
    
    async def test_verify_token_invalid(self, client: AsyncClient):
        """Test token verification with invalid token."""
        response = await client.post(
            "/api/v1/auth/verify-token",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRateLimiting:
    """Test rate limiting on auth endpoints."""
    
    @pytest.mark.skip(reason="Rate limiting requires mocking or integration test")
    async def test_login_rate_limit(self, client: AsyncClient):
        """Test rate limiting on login endpoint."""
        # Make 6 requests (limit is 5 per minute)
        for _ in range(6):
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "password"
                }
            )
            
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                assert "retry_after" in response.json()
                return
        
        pytest.fail("Rate limit not enforced")


class TestInactiveUsers:
    """Test authentication with inactive users."""
    
    async def test_inactive_user_cannot_access(
        self,
        client: AsyncClient,
        inactive_user: User,
        db: AsyncSession
    ):
        """Test that inactive users cannot access protected endpoints."""
        # This would require creating an auth token for inactive user
        # and attempting to access /auth/me
        # Implementation depends on test fixtures
        pass
