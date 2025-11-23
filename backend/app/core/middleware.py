"""
Custom middleware for request processing, rate limiting, and security.
"""
import time
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timedelta

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.logging import logger


# Simple in-memory rate limiter
class RateLimiter:
    """
    Simple in-memory rate limiter for authentication endpoints.
    
    In production, use Redis or similar distributed cache.
    """
    
    def __init__(self, requests_per_minute: int = 5):
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[datetime]] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed based on rate limit.
        
        Args:
            identifier: Unique identifier (e.g., IP address)
            
        Returns:
            True if request is allowed, False otherwise
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]
        
        # Check rate limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True
    
    def get_retry_after(self, identifier: str) -> int:
        """
        Get seconds until rate limit resets.
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Seconds until oldest request expires
        """
        if not self.requests[identifier]:
            return 0
        
        oldest = min(self.requests[identifier])
        reset_time = oldest + timedelta(minutes=1)
        seconds_until_reset = (reset_time - datetime.utcnow()).total_seconds()
        
        return max(0, int(seconds_until_reset))


# Global rate limiter instance (auth endpoints only)
auth_rate_limiter = RateLimiter(requests_per_minute=5)


async def add_process_time_header(request: Request, call_next: Callable):
    """Add X-Process-Time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


async def rate_limit_auth_middleware(request: Request, call_next: Callable):
    """
    Rate limiting middleware for authentication endpoints.
    
    Limits requests to prevent brute force attacks on login/register endpoints.
    """
    # Only apply to auth endpoints
    if not settings.RATE_LIMIT_ENABLED or not request.url.path.startswith("/api/v1/auth"):
        return await call_next(request)
    
    # Get client identifier (IP address)
    client_ip = request.client.host if request.client else "unknown"
    
    # Exempt certain paths from rate limiting
    exempt_paths = [
        "/api/v1/auth/me",
        "/api/v1/auth/verify-token",
        "/api/v1/auth/logout"
    ]
    
    if request.url.path in exempt_paths:
        return await call_next(request)
    
    # Check rate limit
    if not auth_rate_limiter.is_allowed(client_ip):
        retry_after = auth_rate_limiter.get_retry_after(client_ip)
        
        logger.warning(
            f"Rate limit exceeded for {client_ip} on {request.url.path}"
        )
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Too many requests. Please try again later.",
                "retry_after": retry_after
            },
            headers={"Retry-After": str(retry_after)}
        )
    
    response = await call_next(request)
    return response


async def security_headers_middleware(request: Request, call_next: Callable):
    """
    Add security headers to all responses.
    
    Implements basic security best practices.
    """
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response
