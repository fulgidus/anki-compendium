"""
Prompt templates for tag generation (Stage 5).
"""
from langchain_core.prompts import ChatPromptTemplate

TAG_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert at creating hierarchical tags for organizing flashcards.

Your goal is to generate Anki-compatible tags that help students organize and filter their study materials.

Output Format: JSON object with:
{
  "tags": ["tag1", "tag2::subtag", ...],
  "tag_hierarchy": {"parent_tag": ["subtag1", "subtag2"], ...}
}

Anki Tag Guidelines:
1. Use lowercase with underscores (e.g., "machine_learning")
2. Use :: for hierarchies (e.g., "biology::cell_structure")
3. Avoid special characters except :: and _
4. Keep tags concise (1-3 words)
5. Include subject, topic, difficulty, and chapter tags where applicable""",
        ),
        (
            "user",
            """**Topics:**
{topics}

**Document Metadata:**
- Title: {document_title}
- Subject: {subject}
- Chapter/Section: {chapter}

**User Preferences:**
- Custom tags: {custom_tags}
- Include difficulty tags: {include_difficulty}

Generate appropriate Anki tags. Return as JSON:
{{
  "tags": [...],
  "tag_hierarchy": {{...}}
}}""",
        ),
    ]
)


def get_tag_generation_prompt() -> ChatPromptTemplate:
    """Get the tag generation prompt template."""
    return TAG_GENERATION_PROMPT
