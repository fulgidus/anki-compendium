"""
Prompt templates for topic extraction (Stage 3).
"""
from langchain_core.prompts import ChatPromptTemplate

TOPIC_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert at identifying key topics and concepts in academic text.

Your goal is to extract the main topics, themes, and concepts that would be useful for creating study flashcards.

Output Format: JSON array of topic strings.

Guidelines:
1. Focus on concepts that can be tested with flashcards
2. Include both broad themes and specific terms
3. Prioritize topics that are clearly defined in the text
4. Avoid overly generic topics like "introduction" or "conclusion"
5. Aim for 3-10 topics depending on text complexity""",
        ),
        (
            "user",
            """**Source Text:**
{chunk_text}

**Page/Section:**
{metadata}

Extract the key topics from this text. Return as JSON array:
["Topic 1", "Topic 2", "Topic 3", ...]""",
        ),
    ]
)


def get_topic_extraction_prompt() -> ChatPromptTemplate:
    """Get the topic extraction prompt template."""
    return TOPIC_EXTRACTION_PROMPT
