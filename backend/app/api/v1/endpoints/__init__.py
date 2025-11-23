"""
API v1 endpoints.
"""
from . import auth, dashboard, decks, jobs, upload, users

__all__ = ["auth", "dashboard", "decks", "jobs", "upload", "users"]
from app.api.v1.endpoints import auth, decks, jobs, upload

__all__ = ["auth", "decks", "jobs", "upload"]
