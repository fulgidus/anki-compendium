"""
Authentication service for Keycloak integration.

Handles user authentication, token validation, and authorization.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.logging import logger
from app.models.user import User


class AuthService:
    """
    Authentication service for Keycloak integration.
    
    Manages OAuth2/OIDC flows, token validation, and user session management.
    """

    def __init__(self):
        """Initialize authentication service."""
        self.keycloak_url = settings.KEYCLOAK_URL
        self.realm = settings.KEYCLOAK_REALM
        self.client_id = settings.KEYCLOAK_CLIENT_ID
        self.client_secret = settings.KEYCLOAK_CLIENT_SECRET
        self.admin_username = settings.KEYCLOAK_ADMIN_USERNAME
        self.admin_password = settings.KEYCLOAK_ADMIN_PASSWORD
        
        # Cache for admin token (simple in-memory cache)
        self._admin_token: Optional[str] = None
        self._admin_token_expires_at: Optional[datetime] = None

    @property
    def token_endpoint(self) -> str:
        """Get Keycloak token endpoint URL."""
        return f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"

    @property
    def userinfo_endpoint(self) -> str:
        """Get Keycloak userinfo endpoint URL."""
        return f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/userinfo"

    @property
    def jwks_uri(self) -> str:
        """Get Keycloak JWKS URI for token verification."""
        return f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/certs"
    
    @property
    def admin_users_endpoint(self) -> str:
        """Get Keycloak admin users endpoint."""
        return f"{self.keycloak_url}/admin/realms/{self.realm}/users"
    
    @property
    def admin_token_endpoint(self) -> str:
        """Get Keycloak admin token endpoint."""
        return f"{self.keycloak_url}/realms/master/protocol/openid-connect/token"

    async def _get_keycloak_admin_token(self) -> str:
        """
        Get admin access token for Keycloak Admin API.
        
        Uses a simple cache to avoid requesting new tokens on every call.
        
        Returns:
            Admin access token
            
        Raises:
            HTTPException: If admin authentication fails
        """
        # Check if we have a valid cached token
        if self._admin_token and self._admin_token_expires_at:
            if datetime.utcnow() < self._admin_token_expires_at:
                return self._admin_token
        
        # Request new admin token
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.admin_token_endpoint,
                    data={
                        "grant_type": "password",
                        "client_id": "admin-cli",
                        "username": self.admin_username,
                        "password": self.admin_password,
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get Keycloak admin token: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to authenticate with Keycloak admin API"
                    )
                
                token_data = response.json()
                self._admin_token = token_data["access_token"]
                
                # Cache token with 5-minute buffer before expiration
                expires_in = token_data.get("expires_in", 300)
                from datetime import timedelta
                self._admin_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 300)
                
                return self._admin_token
                
            except httpx.RequestError as e:
                logger.error(f"Keycloak connection error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Cannot connect to authentication service"
                )

    async def register(
        self,
        email: str,
        username: str,
        password: str,
        display_name: Optional[str],
        db: AsyncSession
    ) -> User:
        """
        Register a new user in Keycloak and sync to local database.
        
        Args:
            email: User email address
            username: Unique username
            password: User password
            display_name: Optional display name
            db: Database session
            
        Returns:
            Created User object
            
        Raises:
            HTTPException: If registration fails or user already exists
        """
        # Check if user already exists in local DB
        result = await db.execute(
            select(User).where((User.email == email) | (User.username == username))
        )
        existing_user = result.scalars().first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email or username already exists"
            )
        
        # Get admin token
        admin_token = await self._get_keycloak_admin_token()
        
        # Create user in Keycloak
        user_data = {
            "username": username,
            "email": email,
            "enabled": True,
            "emailVerified": False,
            "attributes": {
                "display_name": [display_name] if display_name else []
            },
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": False
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.admin_users_endpoint,
                    json=user_data,
                    headers={
                        "Authorization": f"Bearer {admin_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 409:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="User already exists in Keycloak"
                    )
                
                if response.status_code != 201:
                    logger.error(f"Keycloak user creation failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create user in authentication service"
                    )
                
                # Extract keycloak_id from Location header
                location = response.headers.get("Location")
                if not location:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to retrieve user ID from Keycloak"
                    )
                
                keycloak_id = location.split("/")[-1]
                
                # Create user in local database
                user = User(
                    keycloak_id=keycloak_id,
                    email=email,
                    username=username,
                    display_name=display_name,
                    subscription_tier="free",
                    cards_generated_month=0,
                    cards_limit_month=settings.FREE_TIER_CARD_LIMIT,
                    is_active=True,
                    is_admin=False
                )
                
                db.add(user)
                await db.commit()
                await db.refresh(user)
                
                logger.info(f"User registered successfully: {email} (Keycloak ID: {keycloak_id})")
                return user
                
            except httpx.RequestError as e:
                logger.error(f"Keycloak connection error during registration: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Cannot connect to authentication service"
                )

    async def login(self, email: str, password: str, db: AsyncSession) -> tuple[dict, User]:
        """
        Authenticate user with Keycloak and sync/update local user record.
        
        Args:
            email: User email address
            password: User password
            db: Database session
            
        Returns:
            Tuple of (token_response, user_object)
            
        Raises:
            HTTPException: If authentication fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_endpoint,
                    data={
                        "grant_type": "password",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "username": email,
                        "password": password,
                        "scope": "openid profile email",
                    },
                    timeout=10.0
                )

                if response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password",
                    )
                
                if response.status_code != 200:
                    logger.error(f"Keycloak login failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Authentication service error"
                    )

                token_data = response.json()
                
                # Get user info from Keycloak
                user_info = await self.get_user_info(token_data["access_token"])
                
                # Sync user to local database
                user = await self._sync_user_from_keycloak(user_info, db)
                
                # Update last login
                user.last_login_at = datetime.utcnow()
                await db.commit()
                await db.refresh(user)
                
                logger.info(f"User logged in successfully: {email}")
                return token_data, user
                
            except httpx.RequestError as e:
                logger.error(f"Keycloak connection error during login: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Cannot connect to authentication service"
                )

    async def refresh_token(self, refresh_token: str) -> dict:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from previous authentication
            
        Returns:
            New token response
            
        Raises:
            HTTPException: If refresh fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.token_endpoint,
                    data={
                        "grant_type": "refresh_token",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": refresh_token,
                    },
                    timeout=10.0
                )

                if response.status_code == 400:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired refresh token",
                    )
                
                if response.status_code != 200:
                    logger.error(f"Keycloak token refresh failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Token refresh failed"
                    )

                return response.json()
                
            except httpx.RequestError as e:
                logger.error(f"Keycloak connection error during token refresh: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Cannot connect to authentication service"
                )

    async def get_user_info(self, access_token: str) -> dict:
        """
        Get user information from Keycloak.
        
        Args:
            access_token: Valid access token
            
        Returns:
            User information dictionary
            
        Raises:
            HTTPException: If token is invalid
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.userinfo_endpoint,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )

                if response.status_code == 401:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired access token",
                    )
                
                if response.status_code != 200:
                    logger.error(f"Keycloak userinfo request failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to retrieve user information"
                    )

                return response.json()
                
            except httpx.RequestError as e:
                logger.error(f"Keycloak connection error during userinfo: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Cannot connect to authentication service"
                )

    async def logout(self, refresh_token: str) -> None:
        """
        Logout user by invalidating refresh token in Keycloak.
        
        Args:
            refresh_token: Refresh token to invalidate
        """
        logout_endpoint = (
            f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/logout"
        )

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    logout_endpoint,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": refresh_token,
                    },
                    timeout=10.0
                )
                
                if response.status_code not in [204, 200]:
                    logger.warning(f"Keycloak logout returned unexpected status: {response.status_code}")
                    # Don't raise exception - logout should be best-effort
                
                logger.info("User logged out successfully")
                
            except httpx.RequestError as e:
                logger.error(f"Keycloak connection error during logout: {str(e)}")
                # Don't raise exception - logout should be best-effort

    async def _sync_user_from_keycloak(self, keycloak_user_info: dict, db: AsyncSession) -> User:
        """
        Sync user from Keycloak to local database.
        
        Creates user if not exists, updates if exists.
        
        Args:
            keycloak_user_info: User info from Keycloak userinfo endpoint
            db: Database session
            
        Returns:
            User object (created or updated)
        """
        keycloak_id = keycloak_user_info.get("sub")
        email = keycloak_user_info.get("email")
        username = keycloak_user_info.get("preferred_username")
        
        if not keycloak_id or not email:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid user information from Keycloak"
            )
        
        # Check if user exists
        result = await db.execute(
            select(User).where(User.keycloak_id == keycloak_id)
        )
        user = result.scalars().first()
        
        if user:
            # Update existing user
            user.email = email
            if username:
                user.username = username
            
            logger.debug(f"Updated existing user from Keycloak: {email}")
        else:
            # Create new user
            user = User(
                keycloak_id=keycloak_id,
                email=email,
                username=username,
                subscription_tier="free",
                cards_generated_month=0,
                cards_limit_month=settings.FREE_TIER_CARD_LIMIT,
                is_active=True,
                is_admin=False
            )
            db.add(user)
            logger.info(f"Created new user from Keycloak sync: {email}")
        
        await db.commit()
        await db.refresh(user)
        
        return user


# Singleton instance
auth_service = AuthService()
