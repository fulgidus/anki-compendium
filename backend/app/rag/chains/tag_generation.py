"""
Tag generation chain (Stage 5).
Generates Anki-compatible tags using LangChain.
"""
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI

from app.rag.prompts.tag_generation import get_tag_generation_prompt


def create_tag_generation_chain(
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.1,
) -> Runnable:
    """
    Create a tag generation chain.

    Args:
        model_name: Google Gemini model name
        temperature: Model temperature (very low for consistency)

    Returns:
        Runnable chain that generates Anki tags
    """
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
    )

    prompt = get_tag_generation_prompt()
    parser = JsonOutputParser()

    # Chain: prompt -> LLM -> JSON parser
    chain = prompt | llm | parser

    return chain


async def generate_tags(
    topics: dict,
    document_title: str = "",
    subject: str = "",
    chapter: str = "",
    custom_tags: list[str] | None = None,
    include_difficulty: bool = True,
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.1,
) -> dict:
    """
    Generate Anki-compatible tags from refined topics.

    Args:
        topics: Refined topics dictionary from topic refinement stage
        document_title: Document title
        subject: Subject area
        chapter: Chapter or section identifier
        custom_tags: User-provided custom tags
        include_difficulty: Whether to include difficulty tags
        model_name: Google Gemini model name
        temperature: Model temperature

    Returns:
        Dictionary with tags:
        {
            "tags": ["tag1", "tag2::subtag", ...],
            "tag_hierarchy": {"parent": ["child1", "child2"]}
        }
    """
    chain = create_tag_generation_chain(model_name, temperature)

    topics_str = str(topics)
    custom_tags_str = ", ".join(custom_tags) if custom_tags else ""

    result = await chain.ainvoke(
        {
            "topics": topics_str,
            "document_title": document_title,
            "subject": subject,
            "chapter": chapter,
            "custom_tags": custom_tags_str,
            "include_difficulty": str(include_difficulty),
        }
    )

    return result
