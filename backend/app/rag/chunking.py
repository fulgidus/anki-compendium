"""
Text chunking using LangChain text splitters.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Optional


def create_chunks(
    documents: list,
    chunk_size: Optional[int] = None,
    overlap: Optional[int] = None,
) -> list:
    """
    Split documents into semantic chunks using RecursiveCharacterTextSplitter.

    Args:
        documents: List of Document objects from loader
        chunk_size: Override default chunk size (tokens, default 500)
        overlap: Override default overlap (tokens, default 100)

    Returns:
        List of Document chunks with preserved metadata

    Example:
        >>> from app.rag.loaders import load_pdf
        >>> pages = load_pdf("doc.pdf")
        >>> chunks = create_chunks(pages, chunk_size=500, overlap=100)
    """
    # Default values
    if chunk_size is None:
        chunk_size = 500
    if overlap is None:
        overlap = 100

    # Create splitter with semantic separators
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        separators=[
            "\n\n",  # Paragraph breaks
            "\n",  # Line breaks
            " ",  # Word breaks
            "",  # Character breaks
        ],
        keep_separator=True,
    )

    chunks = splitter.split_documents(documents)

    # Add chunk index to metadata
    for idx, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = idx
        chunk.metadata["chunk_size"] = len(chunk.page_content)

    return chunks


def estimate_chunk_count(
    text_length: int, chunk_size: int = 500, overlap: int = 100
) -> int:
    """
    Estimate number of chunks that will be created.

    Args:
        text_length: Total character count
        chunk_size: Chunk size in characters
        overlap: Overlap size in characters

    Returns:
        Estimated chunk count
    """
    if text_length <= chunk_size:
        return 1

    effective_chunk_size = chunk_size - overlap
    return max(1, (text_length - overlap) // effective_chunk_size)
