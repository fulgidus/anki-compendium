"""
Topic extraction chain (Stage 3).
Extracts key topics from document chunks using LangChain.
"""
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI

from app.rag.prompts.topic_extraction import get_topic_extraction_prompt


def create_topic_extraction_chain(
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.3,
) -> Runnable:
    """
    Create a topic extraction chain.

    Args:
        model_name: Google Gemini model name
        temperature: Model temperature (0.0-1.0)

    Returns:
        Runnable chain that extracts topics from text chunks
    """
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
    )

    prompt = get_topic_extraction_prompt()
    parser = JsonOutputParser()

    # Chain: prompt -> LLM -> JSON parser
    chain = prompt | llm | parser

    return chain


async def extract_topics_from_chunk(
    chunk_text: str,
    chunk_index: int = 0,
    total_chunks: int = 1,
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.3,
) -> dict:
    """
    Extract topics from a single document chunk.

    Args:
        chunk_text: Text content of the chunk
        chunk_index: Index of this chunk (for context)
        total_chunks: Total number of chunks in document
        model_name: Google Gemini model name
        temperature: Model temperature

    Returns:
        Dictionary with extracted topics:
        {
            "topics": ["topic1", "topic2", ...],
            "concepts": [{"name": "...", "importance": "..."}],
            "key_terms": ["term1", "term2", ...]
        }
    """
    chain = create_topic_extraction_chain(model_name, temperature)

    # Build metadata string
    metadata = f"Chunk {chunk_index + 1} of {total_chunks}"
    
    result = await chain.ainvoke(
        {
            "chunk_text": chunk_text,
            "metadata": metadata,
        }
    )

    return result
