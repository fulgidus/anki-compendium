"""
Question generation chain (Stage 6).
Generates flashcard questions using LangChain.
"""
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI

from app.rag.prompts.question_generation import get_question_generation_prompt


def create_question_generation_chain(
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.4,
) -> Runnable:
    """
    Create a question generation chain.

    Args:
        model_name: Google Gemini model name
        temperature: Model temperature (moderate for creativity)

    Returns:
        Runnable chain that generates flashcard questions
    """
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
    )

    prompt = get_question_generation_prompt()
    parser = JsonOutputParser()

    # Chain: prompt -> LLM -> JSON parser
    chain = prompt | llm | parser

    return chain


async def generate_questions(
    chunk_text: str,
    topics: dict,
    density: str = "medium",
    language: str = "English",
    difficulty_mix: str = "balanced",
    custom_instructions: str = "",
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.4,
) -> list[dict]:
    """
    Generate flashcard questions from a chunk.

    Args:
        chunk_text: Source text chunk
        topics: Topics dictionary (from refinement stage)
        density: Card density (low=2, medium=5, high=10 questions per chunk)
        language: Target language for questions
        difficulty_mix: Difficulty distribution (balanced, easy_heavy, hard_heavy)
        custom_instructions: Additional user instructions
        model_name: Google Gemini model name
        temperature: Model temperature

    Returns:
        List of question dictionaries:
        [
            {
                "question": "...",
                "context": "...",
                "difficulty": "easy|medium|hard"
            },
            ...
        ]
    """
    chain = create_question_generation_chain(model_name, temperature)

    # Determine number of questions based on density
    density_map = {"low": 2, "medium": 5, "high": 10}
    num_questions = density_map.get(density, 5)

    topics_str = str(topics)

    result = await chain.ainvoke(
        {
            "chunk_text": chunk_text,
            "topics": topics_str,
            "density": density,
            "num_questions": num_questions,
            "language": language,
            "difficulty_mix": difficulty_mix,
            "custom_instructions": custom_instructions,
        }
    )

    # Ensure result is a list
    if isinstance(result, dict) and "questions" in result:
        return result["questions"]
    elif isinstance(result, list):
        return result
    else:
        return []
