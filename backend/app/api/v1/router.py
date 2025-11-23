"""
Main API v1 router.
"""
from fastapi import APIRouter

from app.api.v1 import health
from app.api.v1.endpoints import auth, dashboard, decks, jobs, upload, users

api_router = APIRouter()

# Include sub-routers
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(decks.router, prefix="/decks", tags=["decks"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(users.router, prefix="/user", tags=["user"])
