"""
Tests for main application.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Anki Compendium API"
    assert data["version"] == "0.1.0"
    assert "docs" in data
    assert "health" in data
