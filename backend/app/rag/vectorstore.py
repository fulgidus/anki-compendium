"""
Vector store using PostgreSQL with pgvector extension.
"""
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector as PGVectorStore
from app.rag.embeddings import create_embeddings
from app.config import settings
from typing import Optional


def create_vectorstore(
    documents: list, collection_name: str, pre_delete: bool = False
) -> PGVectorStore:
    """
    Create PGVector store with Gemini embeddings.

    Args:
        documents: List of Document chunks
        collection_name: Name for the vector collection (e.g., "job_123")
        pre_delete: Whether to delete existing collection

    Returns:
        PGVector instance

    Example:
        >>> from app.rag.loaders import load_pdf
        >>> from app.rag.chunking import create_chunks
        >>> pages = load_pdf("doc.pdf")
        >>> chunks = create_chunks(pages)
        >>> vs = create_vectorstore(chunks, "job_123")
    """
    embeddings = create_embeddings("retrieval_document")

    # Convert asyncpg URL to psycopg format for PGVector
    connection_string = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://", "postgresql+psycopg://"
    )

    vectorstore = PGVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        connection=connection_string,
        collection_name=collection_name,
        pre_delete_collection=pre_delete,
        use_jsonb=True,
    )

    return vectorstore


def load_vectorstore(collection_name: str) -> PGVectorStore:
    """
    Load existing vector store.

    Args:
        collection_name: Name of existing collection

    Returns:
        PGVector instance
    """
    embeddings = create_embeddings("retrieval_document")
    connection_string = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://", "postgresql+psycopg://"
    )

    vectorstore = PGVectorStore(
        connection=connection_string,
        embeddings=embeddings,
        collection_name=collection_name,
        use_jsonb=True,
    )

    return vectorstore


def search_similar(
    vectorstore: PGVectorStore, query: str, k: int = 5, score_threshold: Optional[float] = None
) -> list[tuple[str, float]]:
    """
    Semantic search with similarity scores.

    Args:
        vectorstore: PGVector instance
        query: Search query
        k: Number of results to return
        score_threshold: Minimum similarity score (0.0 to 1.0)

    Returns:
        List of (text, score) tuples
    """
    if score_threshold:
        results = vectorstore.similarity_search_with_relevance_scores(
            query, k=k, score_threshold=score_threshold
        )
    else:
        results = vectorstore.similarity_search_with_score(query, k=k)

    return [(doc.page_content, score) for doc, score in results]


async def asearch_similar(
    vectorstore: PGVectorStore, query: str, k: int = 5
) -> list[tuple[str, float]]:
    """
    Async semantic search with similarity scores.

    Args:
        vectorstore: PGVector instance
        query: Search query
        k: Number of results to return

    Returns:
        List of (text, score) tuples
    """
    results = await vectorstore.asimilarity_search_with_score(query, k=k)
    return [(doc.page_content, score) for doc, score in results]
