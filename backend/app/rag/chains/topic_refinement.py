"""
Topic refinement chain (Stage 4).
Consolidates and organizes extracted topics using LangChain.
"""
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI

from app.rag.prompts.topic_refinement import get_topic_refinement_prompt


def create_topic_refinement_chain(
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.2,
) -> Runnable:
    """
    Create a topic refinement chain.

    Args:
        model_name: Google Gemini model name
        temperature: Model temperature (lower for more consistency)

    Returns:
        Runnable chain that refines and consolidates topics
    """
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
    )

    prompt = get_topic_refinement_prompt()
    parser = JsonOutputParser()

    # Chain: prompt -> LLM -> JSON parser
    chain = prompt | llm | parser

    return chain


async def refine_topics(
    extracted_topics: list[dict],
    document_title: str = "",
    subject: str = "",
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.2,
) -> dict:
    """
    Refine and consolidate topics from all chunks.

    Args:
        extracted_topics: List of topic dictionaries from all chunks
        document_title: Document title for context
        subject: Subject area (e.g., "biology", "computer_science")
        model_name: Google Gemini model name
        temperature: Model temperature

    Returns:
        Dictionary with refined topics:
        {
            "main_topics": ["topic1", "topic2", ...],
            "subtopics": {"topic1": ["sub1", "sub2"], ...},
            "topic_hierarchy": {...},
            "key_concepts": [...]
        }
    """
    chain = create_topic_refinement_chain(model_name, temperature)

    # Serialize extracted topics for the prompt
    topics_json = str(extracted_topics)

    result = await chain.ainvoke(
        {
            "extracted_topics": topics_json,
            "document_title": document_title,
            "subject": subject,
        }
    )

    return result
