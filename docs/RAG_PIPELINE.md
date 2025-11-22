# Anki Compendium - RAG Pipeline Architecture

## Overview

The RAG (Retrieval-Augmented Generation) pipeline transforms PDF documents into high-quality Anki flashcards through an 8-stage process powered by Google Gemini AI.

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG Pipeline Flow                         │
└─────────────────────────────────────────────────────────────────┘

PDF Input (Selected Pages)
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 1: Extraction & Recursion                                  │
│ ─────────────────────────────────────────────────────────────── │
│ • Extract text from PDF pages (PyMuPDF/pdfplumber)              │
│ • Handle multi-column layouts                                    │
│ • Preserve structural hierarchy (headings, sections)             │
│ • Extract images and tables (optional, V2)                       │
│ ─────────────────────────────────────────────────────────────── │
│ Output: Raw text with structure metadata                         │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 2: Chunking                                                │
│ ─────────────────────────────────────────────────────────────── │
│ • Split text into semantic chunks                                │
│ • Chunk size: 500 tokens (configurable via admin settings)      │
│ • Overlap: 20% (configurable)                                    │
│ • Preserve sentence boundaries                                   │
│ • Token counting: tiktoken (cl100k_base)                         │
│ ─────────────────────────────────────────────────────────────── │
│ Output: List of text chunks with metadata                        │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 3: Topic & Subtopic Extraction                             │
│ ─────────────────────────────────────────────────────────────── │
│ • Analyze chunks to identify main topics                         │
│ • Extract subtopics and hierarchical structure                   │
│ • Use Gemini 1.5 Flash for extraction                            │
│ • Prompt: "Extract main topics and subtopics from this text"    │
│ ─────────────────────────────────────────────────────────────── │
│ Output: Topic hierarchy (JSON)                                   │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 4: Topic Refinement                                        │
│ ─────────────────────────────────────────────────────────────── │
│ • Consolidate duplicate or overlapping topics                    │
│ • Improve topic naming and hierarchy                             │
│ • Use Gemini 1.5 Flash for refinement                            │
│ • Prompt: "Refine and consolidate this topic structure"         │
│ ─────────────────────────────────────────────────────────────── │
│ Output: Refined topic hierarchy                                  │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 5: Tag Generation                                          │
│ ─────────────────────────────────────────────────────────────── │
│ • Generate relevant tags for each topic                          │
│ • Include domain-specific keywords                               │
│ • Use Gemini 1.5 Flash for tag generation                        │
│ • Prompt: "Generate relevant tags for these topics"             │
│ ─────────────────────────────────────────────────────────────── │
│ Output: Tags per topic (array)                                   │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 6: Question Generation                                     │
│ ─────────────────────────────────────────────────────────────── │
│ • Generate questions based on topics and chunks                  │
│ • Apply spaced repetition principles                             │
│ • Focus on active recall (not recognition)                       │
│ • Use Gemini 1.5 Flash for Q generation                          │
│ • User-configurable density (cards per page)                     │
│ • Custom instructions support                                    │
│ • Language specification (via user settings)                     │
│ • Prompt template with density/language/custom instructions      │
│ ─────────────────────────────────────────────────────────────── │
│ Output: List of questions (front card content)                   │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 7: Question Answering                                      │
│ ─────────────────────────────────────────────────────────────── │
│ • Generate answers for each question                             │
│ • Validate answers against source text                           │
│ • Ensure answer quality: 2-10 sentences (configurable)          │
│ • Use Gemini 1.5 Flash for answer generation                     │
│ • Prompt: "Answer this question based on the context"           │
│ ─────────────────────────────────────────────────────────────── │
│ Output: Q&A pairs (question + answer)                            │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 8: Card Generation                                         │
│ ─────────────────────────────────────────────────────────────── │
│ • Format Q&A pairs into Anki Basic cards                         │
│ • Apply final refinement (optional, Gemini 1.5 Pro)             │
│ • Add metadata (tags, topics, source)                            │
│ • Generate .apkg file using genanki                              │
│ • Validate card quality (minimum info principle)                 │
│ ─────────────────────────────────────────────────────────────── │
│ Output: .apkg file (Anki deck)                                   │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
Upload to MinIO → Update job status → Notify user
```

---

## Gemini Integration

### Model Selection Strategy

| Stage | Default Model | Purpose | Rationale |
|-------|--------------|---------|-----------|
| Extraction | Gemini 1.5 Flash | Text extraction | Fast, cost-effective |
| Chunking | Gemini 1.5 Flash | Semantic splitting | Lightweight task |
| Topic Extraction | Gemini 1.5 Flash | Topic identification | High volume, low complexity |
| Topic Refinement | Gemini 1.5 Flash | Consolidation | Medium complexity |
| Tag Generation | Gemini 1.5 Flash | Keyword extraction | Simple pattern recognition |
| Q Generation | Gemini 1.5 Flash | Question creation | Core task, high volume |
| Q Answering | Gemini 1.5 Flash | Answer generation | Core task, high volume |
| Final Refinement | Gemini 1.5 Pro | Polish & validation | Optional, quality-focused |

**Admin Configuration**: All model selections are configurable via the `settings` table.

### API Usage Pattern

```python
import google.generativeai as genai

# Configure API key
genai.configure(api_key=settings.GEMINI_API_KEY)

# Get model from admin settings
model_name = get_setting('gemini_model_qa_generation')  # e.g., "gemini-1.5-flash"
model = genai.GenerativeModel(model_name)

# Generate content
response = model.generate_content(
    prompt,
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 2048,
    }
)
```

### Rate Limiting & Cost Control

- **User Tracking**: Track API calls per user in `users.cards_generated_month`
- **Free Tier**: 30 cards/month (configurable)
- **Retry Logic**: Exponential backoff for rate limit errors
- **Batch Processing**: Group similar requests when possible
- **Caching**: Cache embeddings and topic extractions (future optimization)

---

## Vector Database Integration

### Database Choice

**Option A (V1)**: **pgvector** (PostgreSQL extension)
- Pros: No additional service, simple deployment
- Cons: Less optimized for large-scale vector operations

**Option B (Future)**: **ChromaDB** self-hosted
- Pros: Purpose-built for embeddings, better performance
- Cons: Additional service to maintain

### Vector Store Schema (pgvector)

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE chunk_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(768),  -- Gemini embedding dimension
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chunk_embeddings_job_id ON chunk_embeddings(job_id);
CREATE INDEX idx_chunk_embeddings_embedding ON chunk_embeddings 
    USING ivfflat (embedding vector_cosine_ops);
```

### Embedding Generation

```python
import google.generativeai as genai

# Generate embedding for chunk
embedding_model = "models/embedding-001"
result = genai.embed_content(
    model=embedding_model,
    content=chunk_text,
    task_type="retrieval_document"
)
embedding_vector = result['embedding']
```

### Similarity Search

```python
# Find similar chunks (semantic search)
query_embedding = genai.embed_content(
    model="models/embedding-001",
    content=user_query,
    task_type="retrieval_query"
)['embedding']

similar_chunks = db.execute(
    """
    SELECT chunk_text, 1 - (embedding <=> %s::vector) AS similarity
    FROM chunk_embeddings
    WHERE job_id = %s
    ORDER BY embedding <=> %s::vector
    LIMIT 5
    """,
    (query_embedding, job_id, query_embedding)
)
```

---

## Prompt Engineering

### Stage 6: Question Generation Prompt Template

```python
QUESTION_GENERATION_PROMPT = """
You are an expert educator creating Anki flashcards for university students.

**Source Material:**
{chunk_text}

**Topics:**
{topics}

**Tags:**
{tags}

**Instructions:**
- Generate {card_density} high-quality flashcard questions from this content
- Focus on {user_custom_instructions}
- Language: {language}
- Apply spaced repetition principles (atomic facts, active recall)
- Avoid ambiguous or overly broad questions
- Each question should test a single concept

**Output Format:**
Return a JSON array of questions:
[
  {{"question": "What is...?", "context": "brief context"}},
  ...
]
"""
```

### Stage 7: Answer Generation Prompt Template

```python
ANSWER_GENERATION_PROMPT = """
You are an expert educator creating Anki flashcard answers.

**Question:**
{question}

**Source Context:**
{context}

**Requirements:**
- Answer length: {min_sentences} to {max_sentences} sentences
- Language: {language}
- Be concise but complete
- Use clear, student-friendly language
- Include relevant examples if helpful
- Ensure factual accuracy based on source context

**Output Format:**
Return only the answer text, no additional formatting.
"""
```

### Stage 8: Final Refinement Prompt (Optional)

```python
REFINEMENT_PROMPT = """
You are a quality control expert for educational flashcards.

**Card to Review:**
Front: {front}
Back: {back}

**Review Criteria:**
1. Clarity: Is the question unambiguous?
2. Accuracy: Is the answer factually correct?
3. Completeness: Does the answer fully address the question?
4. Conciseness: Is the answer appropriately brief ({min_sentences}-{max_sentences} sentences)?
5. Educational Value: Does this card promote effective learning?

**Instructions:**
- If the card meets all criteria, return it unchanged
- If improvements are needed, refine the question and/or answer
- Maintain the original intent and factual content

**Output Format:**
Return a JSON object:
{{"front": "refined question", "back": "refined answer", "changes": "description of changes or 'none'"}}
"""
```

---

## Card Quality Assurance

### Validation Rules

1. **Atomic Facts**: One testable fact per card
2. **Answer Length**: 2-10 sentences (configurable)
3. **Question Clarity**: No ambiguous phrasing
4. **Context Sufficiency**: Enough context to answer without source
5. **No Duplicates**: Detect and merge similar cards
6. **Spaced Repetition Friendly**: Optimized for active recall

### Quality Metrics

Track per deck:
- Average answer length
- Question clarity score (future: user feedback)
- Duplicate detection rate
- User rating (future: star ratings)

---

## Configuration Management

### Admin Settings Interface

```python
# Backend API endpoint
GET /api/admin/settings
PUT /api/admin/settings/{key}

# Settings categories
{
  "rag": {
    "chunk_size_tokens": 500,
    "chunk_overlap_percent": 20,
    "card_answer_min_sentences": 2,
    "card_answer_max_sentences": 10
  },
  "gemini": {
    "model_extraction": "gemini-1.5-flash",
    "model_chunking": "gemini-1.5-flash",
    "model_topic_extraction": "gemini-1.5-flash",
    "model_topic_refinement": "gemini-1.5-flash",
    "model_tag_generation": "gemini-1.5-flash",
    "model_qa_generation": "gemini-1.5-flash",
    "model_qa_answering": "gemini-1.5-flash",
    "model_refinement": "gemini-1.5-pro",
    "enable_final_refinement": false
  },
  "limits": {
    "free_tier_card_limit": 30,
    "max_pdf_size_mb": 100
  }
}
```

### User Settings (Per Job)

Users can customize per-job:
- **Card Density**: Low / Medium / High (affects cards per page)
- **Language**: ISO 639-1 code (en, it, es, fr, de, etc.)
- **Custom Instructions**: Free-text guidance for question generation

---

## Error Handling

### Pipeline Failure Recovery

```python
# Celery task with retry logic
@celery_app.task(bind=True, max_retries=3)
def process_pdf_pipeline(self, job_id):
    try:
        # Execute pipeline stages
        for stage in PIPELINE_STAGES:
            result = stage.execute(job_id)
            update_job_progress(job_id, stage.progress_percent)
        
        # Success
        finalize_job(job_id, status='completed')
        send_notification(job_id, type='job_completed')
        
    except RateLimitError as e:
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
        
    except ValidationError as e:
        # Non-retryable error
        finalize_job(job_id, status='failed', error=str(e))
        send_notification(job_id, type='job_failed')
        
    except Exception as e:
        # Log and retry
        logger.error(f"Pipeline failed for job {job_id}: {e}")
        raise self.retry(exc=e, countdown=60)
```

### Partial Success Handling

- Save intermediate results (chunks, topics, Q&A pairs)
- Allow manual retry from last successful stage
- Provide detailed error logs to admin

---

## Performance Optimization

### Parallel Processing

```python
# Process chunks in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=10) as executor:
    chunk_embeddings = list(executor.map(
        generate_embedding,
        chunks
    ))
```

### Caching Strategy (Future)

- **Chunk Embeddings**: Cache for 24 hours
- **Topic Extractions**: Cache similar PDFs
- **Model Responses**: Cache with hash of (prompt + model + params)

---

## Testing Strategy

### Unit Tests

```python
# Test each pipeline stage independently
def test_extraction_stage():
    pdf_path = "test_data/sample.pdf"
    result = ExtractionStage().execute(pdf_path, pages=[1, 2, 3])
    assert len(result.text) > 0
    assert result.metadata['page_count'] == 3

def test_chunking_stage():
    text = load_test_text()
    chunks = ChunkingStage(chunk_size=500, overlap=0.2).execute(text)
    assert all(len(c.tokens) <= 500 for c in chunks)
```

### Integration Tests

```python
# Test full pipeline end-to-end
def test_full_pipeline():
    job = create_test_job(pdf_path="test.pdf", pages=[1, 2])
    result = execute_pipeline(job.id)
    
    assert result.status == 'completed'
    assert result.deck_path.endswith('.apkg')
    assert result.card_count > 0
```

### Smoke Tests

```bash
# Quick validation of key functionality
pytest tests/smoke/ -v
```

---

## Monitoring & Observability

### Key Metrics

- **Pipeline Success Rate**: % of jobs completed successfully
- **Average Processing Time**: Per stage and overall
- **Gemini API Usage**: Tokens consumed per user/day
- **Card Quality Score**: User feedback ratings (future)
- **Error Rate by Stage**: Identify bottlenecks

### Logging

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "pipeline.stage.completed",
    job_id=job_id,
    stage="question_generation",
    duration_seconds=12.5,
    cards_generated=42,
    model="gemini-1.5-flash"
)
```

---

## Future Enhancements

### V2 Pipeline Features

- **Image Extraction**: Extract diagrams and tables from PDFs
- **Image Occlusion**: Generate image occlusion cards
- **Cloze Deletions**: Support for fill-in-the-blank cards
- **Multi-Document RAG**: Combine multiple sources
- **Incremental Updates**: Add cards to existing decks
- **User Feedback Loop**: Refine prompts based on ratings

### Advanced RAG

- **Hybrid Search**: Combine vector similarity with keyword search
- **Re-ranking**: Use cross-encoder for better retrieval
- **Query Expansion**: Improve question generation with expanded context
- **Multi-Modal**: Support images and equations in cards

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-22  
**Author**: Project Manager Agent
