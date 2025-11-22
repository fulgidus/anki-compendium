"""
PDF document loaders using LangChain.
"""
from langchain_community.document_loaders import PyMuPDFLoader
from pathlib import Path
from typing import Optional


def load_pdf(pdf_path: str, page_range: Optional[tuple[int, int]] = None) -> list:
    """
    Load PDF and extract text with metadata using PyMuPDFLoader.

    Args:
        pdf_path: Path to PDF file
        page_range: Optional (start_page, end_page) tuple (0-indexed, inclusive)

    Returns:
        List of Document objects with text and metadata

    Example:
        >>> pages = load_pdf("document.pdf", page_range=(0, 5))
        >>> len(pages)
        6  # Pages 0-5 inclusive
    """
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()

    # Filter by page range if specified
    if page_range:
        start, end = page_range
        pages = [p for p in pages if start <= p.metadata.get("page", 0) <= end]

    return pages


def get_pdf_metadata(pdf_path: str) -> dict:
    """
    Extract metadata from PDF without loading full content.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Dictionary with metadata (page_count, title, author, etc.)
    """
    import pymupdf

    doc = pymupdf.open(pdf_path)
    metadata = {
        "page_count": len(doc),
        "title": doc.metadata.get("title", ""),
        "author": doc.metadata.get("author", ""),
        "subject": doc.metadata.get("subject", ""),
        "creator": doc.metadata.get("creator", ""),
    }
    doc.close()

    return metadata
