"""
Prompt templates for question generation (Stage 6).
"""
from langchain_core.prompts import ChatPromptTemplate

QUESTION_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert educator creating high-quality Anki flashcards for university students.

Your goal is to generate questions that promote active recall and spaced repetition learning.

Output Format: JSON array of objects:
[
  {{
    "question": "Clear, specific question",
    "context": "Minimal context needed to answer",
    "difficulty": "easy|medium|hard"
  }},
  ...
]

Flashcard Best Practices:
1. **Atomic Facts**: One concept per question
2. **Active Recall**: Test retrieval, not recognition
3. **Clarity**: Unambiguous wording
4. **Conciseness**: No unnecessary verbosity
5. **Cloze-Friendly**: Can be converted to cloze deletions
6. **Avoid**: "List all..." or "Describe everything about..."

Question Types to Use:
- Definition questions ("What is X?")
- Cause-effect ("What causes X?")
- Comparison ("How does X differ from Y?")
- Application ("When would you use X?")
- Conceptual ("Why is X important?")""",
        ),
        (
            "user",
            """**Source Text:**
{chunk_text}

**Topics:**
{topics}

**Settings:**
- Card Density: {density} (low=2, medium=5, high=10 questions per chunk)
- Language: {language}
- Difficulty Mix: {difficulty_mix}
- Custom Instructions: {custom_instructions}

Generate {num_questions} flashcard questions. Return as JSON array:
[
  {{"question": "...", "context": "...", "difficulty": "..."}},
  ...
]""",
        ),
    ]
)


def get_question_generation_prompt() -> ChatPromptTemplate:
    """Get the question generation prompt template."""
    return QUESTION_GENERATION_PROMPT
