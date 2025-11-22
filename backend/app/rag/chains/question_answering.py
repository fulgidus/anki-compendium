"""
Question answering chain (Stage 7).
Generates answers for flashcard questions using LangChain + RAG.
"""
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI

from app.rag.prompts.question_answering import get_question_answering_prompt


def create_question_answering_chain(
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.2,
) -> Runnable:
    """
    Create a question answering chain.

    Args:
        model_name: Google Gemini model name
        temperature: Model temperature (low for accuracy)

    Returns:
        Runnable chain that generates answers
    """
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
    )

    prompt = get_question_answering_prompt()
    parser = JsonOutputParser()

    # Chain: prompt -> LLM -> JSON parser
    chain = prompt | llm | parser

    return chain


async def generate_answer(
    question: str,
    context: str,
    chunk_text: str,
    language: str = "English",
    answer_style: str = "brief",
    include_explanation: bool = False,
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.2,
) -> dict:
    """
    Generate an answer for a flashcard question using RAG context.

    Args:
        question: The flashcard question
        context: Minimal context from question generation
        chunk_text: Full source chunk text
        language: Target language
        answer_style: Answer style (brief, detailed, bullet_points)
        include_explanation: Whether to include explanation
        model_name: Google Gemini model name
        temperature: Model temperature

    Returns:
        Dictionary with answer:
        {
            "answer": "...",
            "explanation": "...",
            "difficulty_rating": "easy|medium|hard"
        }
    """
    chain = create_question_answering_chain(model_name, temperature)

    result = await chain.ainvoke(
        {
            "question": question,
            "context": context,
            "chunk_text": chunk_text,
            "language": language,
            "answer_style": answer_style,
            "include_explanation": str(include_explanation),
        }
    )

    return result


async def generate_answers_batch(
    questions: list[dict],
    chunk_text: str,
    language: str = "English",
    answer_style: str = "brief",
    include_explanation: bool = False,
    model_name: str = "gemini-2.0-flash-exp",
    temperature: float = 0.2,
) -> list[dict]:
    """
    Generate answers for multiple questions from the same chunk.

    Args:
        questions: List of question dictionaries with "question" and "context" keys
        chunk_text: Source chunk text
        language: Target language
        answer_style: Answer style
        include_explanation: Whether to include explanations
        model_name: Google Gemini model name
        temperature: Model temperature

    Returns:
        List of complete Q&A pairs with answers added
    """
    results = []

    for q in questions:
        answer_dict = await generate_answer(
            question=q["question"],
            context=q.get("context", ""),
            chunk_text=chunk_text,
            language=language,
            answer_style=answer_style,
            include_explanation=include_explanation,
            model_name=model_name,
            temperature=temperature,
        )

        # Merge question and answer data
        qa_pair = {
            **q,  # Original question data
            **answer_dict,  # Add answer, explanation, difficulty_rating
        }
        results.append(qa_pair)

    return results
