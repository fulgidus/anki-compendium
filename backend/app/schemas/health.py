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
