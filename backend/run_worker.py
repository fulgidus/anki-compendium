#!/usr/bin/env python3
"""
Celery worker entry point for Anki Compendium.

Usage:
    python run_worker.py

This script starts a Celery worker that processes PDF-to-Anki deck generation tasks.
"""

import logging
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.celery_app import celery_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Celery worker for Anki Compendium")
    
    # Start Celery worker with optimized settings for PDF processing
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=2",  # Limit concurrent tasks (Gemini API rate limits)
        "--max-tasks-per-child=10",  # Restart worker after 10 tasks (memory management)
        "--task-events",  # Enable task events for monitoring
        "--without-gossip",  # Disable gossip (not needed for single worker)
        "--without-mingle",  # Disable synchronization (faster startup)
        "--pool=solo",  # Use solo pool for better compatibility with asyncio
        "-Q",  # Queue specification
        "pdf_processing",  # Listen to pdf_processing queue
    ])
