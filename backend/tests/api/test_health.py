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
