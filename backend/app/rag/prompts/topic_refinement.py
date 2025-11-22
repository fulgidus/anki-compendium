"""
Prompt templates for topic refinement (Stage 4).
"""
from langchain_core.prompts import ChatPromptTemplate

TOPIC_REFINEMENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert at organizing and refining educational topics.

Your goal is to consolidate, deduplicate, and organize topics extracted from multiple text chunks.

Output Format: JSON object with:
{
  "refined_topics": ["Topic 1", "Topic 2", ...],
  "topic_hierarchy": {"Parent Topic": ["Subtopic 1", "Subtopic 2"], ...}
}

Guidelines:
1. Merge similar or duplicate topics
2. Create hierarchies where appropriate (parent-child relationships)
3. Remove overly generic or redundant topics
4. Ensure topics are specific and testable
5. Keep the total count reasonable (5-15 refined topics)""",
        ),
        (
            "user",
            """**Extracted Topics from Multiple Chunks:**
{raw_topics}

**Document Context:**
{document_title}
{page_range}

Refine these topics into a clean, organized structure. Return as JSON:
{{
  "refined_topics": [...],
  "topic_hierarchy": {{...}}
}}""",
        ),
    ]
)


def get_topic_refinement_prompt() -> ChatPromptTemplate:
    """Get the topic refinement prompt template."""
    return TOPIC_REFINEMENT_PROMPT
