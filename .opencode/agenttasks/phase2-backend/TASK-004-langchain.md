---
task_id: "TASK-004-LANGCHAIN"
title: "Setup LangChain Hybrid Integration for RAG Pipeline"
phase: "Phase 2: Backend Core"
complexity: "medium"
estimated_duration: "3-4 hours"
assigned_to: "developer"
dependencies: ["TASK-001-DOCKERCOMPOSE"]
status: "pending"
priority: "high"
created_at: "2025-11-22"
---

# Task: Setup LangChain Hybrid Integration

## Objective
Integrate LangChain selectively into the RAG pipeline to accelerate development while maintaining custom control for Anki-specific logic.

## Context
LangChain provides battle-tested components for document loading, chunking, embeddings, and chain orchestration. We use it for stages 1-7 of our RAG pipeline, while maintaining custom logic for stage 8 (Anki card generation).

**Time Savings**: Estimated 2-3 weeks reduction in MVP timeline.

---

## Requirements

### Functional Requirements

#### Stage 1-2: Document Loading & Chunking
1. Use `PyMuPDFLoader` for PDF text extraction
2. Use `RecursiveCharacterTextSplitter` for intelligent chunking
3. Preserve document metadata (page numbers, sections)
4. Support configurable chunk size and overlap (from admin settings)

#### Vector Store Integration
1. Setup `PGVector` with PostgreSQL + pgvector extension
2. Automatic embedding generation with Gemini
3. Similarity search capabilities
4. Metadata filtering support

#### Stages 3-7: Chains & Prompt Templates
1. Create reusable prompt templates for each stage
2. Implement chains with automatic retry logic
3. Structured output parsing (JSON)
4. Error handling and logging

#### Stage 8: Custom Card Generation
1. Keep custom logic with `genanki`
2. Do NOT use LangChain for Anki-specific formatting

### Non-Functional Requirements
- Clean separation between LangChain and custom code
- Easy to test each stage independently
- Configurable model selection per stage
- Comprehensive logging for debugging

---

## File Structure

```
backend/app/
├── rag/
│   ├── __init__.py
│   ├── loaders.py               # LangChain document loaders
│   ├── chunking.py              # LangChain text splitters
│   ├── embeddings.py            # LangChain embeddings setup
│   ├── vectorstore.py           # PGVector integration
│   ├── chains/
│   │   ├── __init__.py
│   │   ├── topic_extraction.py  # Chain for stage 3
│   │   ├── topic_refinement.py  # Chain for stage 4
│   │   ├── tag_generation.py    # Chain for stage 5
│   │   ├── question_generation.py  # Chain for stage 6
│   │   └── question_answering.py   # Chain for stage 7
│   ├── prompts/
│   │   ├── __init__.py
│   │   ├── topic_extraction.py  # Prompt templates
│   │   ├── topic_refinement.py
│   │   ├── tag_generation.py
│   │   ├── question_generation.py
│   │   └── question_answering.py
│   ├── anki/
│   │   ├── __init__.py
│   │   └── card_generator.py    # Custom genanki logic (NO LangChain)
│   └── pipeline.py              # Main RAG pipeline orchestrator
├── tests/
│   └── rag/
│       ├── test_loaders.py
│       ├── test_chunking.py
│       ├── test_chains.py
│       └── test_pipeline.py
```

---

## Acceptance Criteria

### Must Have
- [ ] LangChain PyMuPDFLoader successfully extracts text from PDFs
- [ ] RecursiveCharacterTextSplitter creates chunks with configurable size/overlap
- [ ] PGVector vectorstore stores and retrieves embeddings correctly
- [ ] All 5 chains (stages 3-7) execute successfully
- [ ] Prompt templates are clean, reusable, and well-documented
- [ ] Custom genanki card generation works independently
- [ ] Unit tests cover each component
- [ ] Integration test runs full pipeline PDF → .apkg

### Nice to Have
- [ ] LangSmith tracing integration for debugging
- [ ] Caching layer for embeddings (Redis)
- [ ] Batch processing for multiple chunks
- [ ] Async execution for chains (parallel processing)

---

## Technical Specifications

### Dependencies (requirements.txt)

```txt
# LangChain Core
langchain>=0.1.0
langchain-core>=0.1.0
langchain-community>=0.0.20

# LangChain Integrations
langchain-google-genai>=0.0.6    # Gemini integration
langchain-postgres>=0.0.3         # PGVector integration

# Document Processing
pymupdf>=1.23.0                   # PDF extraction (used by LangChain)

# Anki Export (Custom)
genanki>=0.13.0

# Utilities
pydantic>=2.0.0                   # For structured outputs
tiktoken>=0.5.0                   # Token counting
```

### Stage 1-2: Loader & Chunker Implementation

```python
# backend/app/rag/loaders.py
from langchain.document_loaders import PyMuPDFLoader
from pathlib import Path

def load_pdf(pdf_path: str, page_range: tuple[int, int] = None) -> list:
    """
    Load PDF and extract text with metadata.
    
    Args:
        pdf_path: Path to PDF file
        page_range: Optional (start_page, end_page) tuple (0-indexed)
    
    Returns:
        List of Document objects with text and metadata
    """
    loader = PyMuPDFLoader(pdf_path)
    pages = loader.load()
    
    # Filter by page range if specified
    if page_range:
        start, end = page_range
        pages = [p for p in pages if start <= p.metadata['page'] <= end]
    
    return pages
```

```python
# backend/app/rag/chunking.py
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.core.settings import get_setting

def create_chunks(documents: list, chunk_size: int = None, overlap: int = None):
    """
    Split documents into semantic chunks.
    
    Args:
        documents: List of Document objects from loader
        chunk_size: Override default chunk size (from settings if None)
        overlap: Override default overlap (from settings if None)
    
    Returns:
        List of Document chunks with preserved metadata
    """
    # Get config from admin settings if not provided
    if chunk_size is None:
        chunk_size = int(get_setting('chunk_size_tokens', default=500))
    if overlap is None:
        overlap_pct = int(get_setting('chunk_overlap_percent', default=20))
        overlap = int(chunk_size * overlap_pct / 100)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = splitter.split_documents(documents)
    return chunks
```

### Vector Store Setup

```python
# backend/app/rag/vectorstore.py
from langchain.vectorstores import PGVector
from langchain.embeddings import GoogleGenerativeAIEmbeddings
from app.core.config import settings

def create_vectorstore(documents: list, job_id: str):
    """
    Create PGVector store with Gemini embeddings.
    
    Args:
        documents: List of Document chunks
        job_id: Job ID for collection naming
    
    Returns:
        PGVector instance
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.GEMINI_API_KEY,
        task_type="retrieval_document"
    )
    
    vectorstore = PGVector.from_documents(
        documents=documents,
        embedding=embeddings,
        connection_string=settings.DATABASE_URL,
        collection_name=f"job_{job_id}",
        pre_delete_collection=False  # Keep embeddings for retry
    )
    
    return vectorstore

def search_similar(vectorstore: PGVector, query: str, k: int = 5):
    """Semantic search with similarity scores."""
    results = vectorstore.similarity_search_with_score(query, k=k)
    return [(doc.page_content, score) for doc, score in results]
```

### Prompt Template Example (Stage 6: Question Generation)

```python
# backend/app/rag/prompts/question_generation.py
from langchain.prompts import ChatPromptTemplate

QUESTION_GENERATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert educator creating Anki flashcards for university students.

Your goal is to generate high-quality questions that:
1. Test a single concept (atomic facts)
2. Promote active recall (not recognition)
3. Are unambiguous and clear
4. Match the specified language and density

Output Format: JSON array of objects with "question" and "context" fields."""),
    
    ("user", """**Source Text:**
{chunk_text}

**Topics:**
{topics}

**Settings:**
- Card Density: {density}
- Language: {language}
- Custom Instructions: {custom_instructions}

Generate {num_questions} flashcard questions based on the above. Return as JSON array:
[
  {{"question": "...", "context": "..."}},
  ...
]""")
])

def get_question_prompt():
    """Factory function to get prompt template."""
    return QUESTION_GENERATION_PROMPT
```

### Chain Implementation (Stage 6: Question Generation)

```python
# backend/app/rag/chains/question_generation.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import JsonOutputParser
from app.rag.prompts.question_generation import get_question_prompt
from app.core.config import settings

def create_question_generation_chain():
    """Create LangChain chain for question generation."""
    # Get model from settings
    model_name = get_setting('gemini_model_qa_generation', 'gemini-1.5-flash')
    
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.7,
        max_retries=3  # Automatic retry on failures
    )
    
    prompt = get_question_prompt()
    output_parser = JsonOutputParser()
    
    # Chain: prompt -> LLM -> JSON parser
    chain = prompt | llm | output_parser
    
    return chain

async def generate_questions(
    chunk_text: str,
    topics: list,
    density: str = "medium",
    language: str = "en",
    custom_instructions: str = ""
) -> list:
    """
    Generate questions from a text chunk.
    
    Returns:
        List of dict with 'question' and 'context' keys
    """
    chain = create_question_generation_chain()
    
    # Calculate number of questions based on density
    num_questions = {"low": 2, "medium": 5, "high": 10}.get(density, 5)
    
    result = await chain.ainvoke({
        "chunk_text": chunk_text,
        "topics": ", ".join(topics),
        "density": density,
        "language": language,
        "custom_instructions": custom_instructions or "None",
        "num_questions": num_questions
    })
    
    return result
```

### Custom Anki Card Generation (Stage 8)

```python
# backend/app/rag/anki/card_generator.py
import genanki
import random
from pathlib import Path

def generate_anki_deck(
    qa_pairs: list[dict],
    deck_name: str,
    tags: list[str] = None,
    output_path: str = None
) -> str:
    """
    Generate .apkg file from Q&A pairs.
    
    Args:
        qa_pairs: List of {"question": str, "answer": str, "tags": list}
        deck_name: Name of the deck
        tags: Global tags to apply to all cards
        output_path: Where to save .apkg file
    
    Returns:
        Path to generated .apkg file
    """
    # Create deck with random ID
    deck_id = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(deck_id, deck_name)
    
    # Define Basic note type
    model_id = random.randrange(1 << 30, 1 << 31)
    basic_model = genanki.Model(
        model_id,
        'Anki Compendium Basic',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Back}}',
            },
        ],
        css="""
        .card {
            font-family: Arial, sans-serif;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        """
    )
    
    # Add cards
    for qa in qa_pairs:
        card_tags = tags or []
        if 'tags' in qa:
            card_tags.extend(qa['tags'])
        
        note = genanki.Note(
            model=basic_model,
            fields=[qa['question'], qa['answer']],
            tags=card_tags
        )
        deck.add_note(note)
    
    # Generate .apkg file
    if output_path is None:
        output_path = f"/tmp/{deck_name.replace(' ', '_')}.apkg"
    
    package = genanki.Package(deck)
    package.write_to_file(output_path)
    
    return output_path
```

---

## Testing Requirements

### Unit Tests

```python
# backend/tests/rag/test_loaders.py
import pytest
from app.rag.loaders import load_pdf

def test_load_pdf():
    """Test PDF loading with PyMuPDFLoader."""
    pages = load_pdf("tests/fixtures/sample.pdf")
    assert len(pages) > 0
    assert pages[0].page_content
    assert 'page' in pages[0].metadata

def test_load_pdf_with_page_range():
    """Test page filtering."""
    pages = load_pdf("tests/fixtures/sample.pdf", page_range=(0, 2))
    assert len(pages) == 3  # Pages 0, 1, 2
    assert all(p.metadata['page'] <= 2 for p in pages)
```

```python
# backend/tests/rag/test_chunking.py
import pytest
from app.rag.chunking import create_chunks
from app.rag.loaders import load_pdf

def test_create_chunks():
    """Test text chunking with RecursiveCharacterTextSplitter."""
    pages = load_pdf("tests/fixtures/sample.pdf")
    chunks = create_chunks(pages, chunk_size=500, overlap=100)
    
    assert len(chunks) > len(pages)  # More chunks than pages
    assert all(len(c.page_content) <= 600 for c in chunks)  # Approx limit

def test_chunks_preserve_metadata():
    """Test that chunks retain source metadata."""
    pages = load_pdf("tests/fixtures/sample.pdf")
    chunks = create_chunks(pages)
    
    assert all('page' in c.metadata for c in chunks)
```

### Integration Test

```python
# backend/tests/rag/test_pipeline.py
import pytest
from app.rag.pipeline import execute_rag_pipeline

@pytest.mark.asyncio
async def test_full_pipeline():
    """Test complete RAG pipeline PDF -> .apkg."""
    result = await execute_rag_pipeline(
        pdf_path="tests/fixtures/sample.pdf",
        page_range=(0, 5),
        settings={
            "density": "medium",
            "language": "en"
        }
    )
    
    assert result['status'] == 'completed'
    assert result['apkg_path'].endswith('.apkg')
    assert result['card_count'] > 0
    
    # Verify .apkg file exists
    import os
    assert os.path.exists(result['apkg_path'])
```

---

## Success Criteria
- All LangChain components integrated and functional
- RAG pipeline executes successfully end-to-end
- Custom Anki generation works with genanki
- Unit tests pass with >80% coverage
- Integration test creates valid .apkg file
- Documentation clear for maintenance

## Deliverables
1. LangChain loaders, chunkers, embeddings, chains
2. Custom Anki card generator (genanki)
3. Unit tests for each component
4. Integration test for full pipeline
5. Updated requirements.txt with LangChain deps
6. Documentation in code and README

## Notes
- LangChain version pinning important for stability
- Use async chains (`ainvoke`) for better concurrency
- Consider LangSmith for debugging (optional)
- Monitor Gemini API costs during development

## References
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [LangChain Google GenAI](https://python.langchain.com/docs/integrations/platforms/google)
- [PGVector Integration](https://python.langchain.com/docs/integrations/vectorstores/pgvector)
- [genanki Documentation](https://github.com/kerrickstaley/genanki)
