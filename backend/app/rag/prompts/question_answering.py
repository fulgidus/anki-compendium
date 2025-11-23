"""
Prompt templates for question answering (Stage 7).
"""
from langchain_core.prompts import ChatPromptTemplate

QUESTION_ANSWERING_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert educator creating clear, accurate answers for university-level flashcards.

Your goal is to provide concise, factually correct answers that facilitate effective learning.

Output Format: JSON object:
{{
  "answer": "Clear, complete answer",
  "explanation": "Brief supporting explanation (optional)",
  "difficulty_rating": "easy|medium|hard"
}}

Answer Guidelines:
1. **Accuracy**: Provide factually correct information
2. **Conciseness**: Brief but complete (2-4 sentences max)
3. **Clarity**: Use simple, direct language
4. **Context-Aware**: Reference the source material
5. **Self-Contained**: Answer should make sense without the question
6. **Active Recall Support**: Don't give away too much; encourage thinking
7. **No Speculation**: Only use information from the provided context""",
        ),
        (
            "user",
            """**Question:**
{question}

**Source Context:**
{context}

**Additional Context:**
{chunk_text}

**Settings:**
- Language: {language}
- Answer Style: {answer_style} (brief|detailed|bullet_points)
- Include Explanation: {include_explanation}

Generate the answer. Return as JSON:
{{
  "answer": "...",
  "explanation": "...",
  "difficulty_rating": "..."
}}""",
        ),
    ]
)


def get_question_answering_prompt() -> ChatPromptTemplate:
    """Get the question answering prompt template."""
    return QUESTION_ANSWERING_PROMPT
