"""
Embedding generation using Google Gemini.
"""
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings


def create_embeddings(task_type: str = "retrieval_document") -> GoogleGenerativeAIEmbeddings:
    """
    Create Gemini embeddings instance.

    Args:
        task_type: Type of embedding task
            - "retrieval_document": For document indexing
            - "retrieval_query": For search queries
            - "semantic_similarity": For similarity comparisons
            - "classification": For text classification

    Returns:
        GoogleGenerativeAIEmbeddings instance

    Example:
        >>> embeddings = create_embeddings("retrieval_document")
        >>> vector = embeddings.embed_query("What is LangChain?")
    """
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.GEMINI_API_KEY,
        task_type=task_type,
    )


async def embed_documents(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple documents asynchronously.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors
    """
    embeddings = create_embeddings("retrieval_document")
    vectors = await embeddings.aembed_documents(texts)
    return vectors


async def embed_query(text: str) -> list[float]:
    """
    Generate embedding for a single query asynchronously.

    Args:
        text: Query text to embed

    Returns:
        Embedding vector
    """
    embeddings = create_embeddings("retrieval_query")
    vector = await embeddings.aembed_query(text)
    return vector
