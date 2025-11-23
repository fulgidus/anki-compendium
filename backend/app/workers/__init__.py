"""
Celery worker tasks for Anki Compendium.
"""

from app.workers.tasks import process_pdf_task

__all__ = ["process_pdf_task"]
