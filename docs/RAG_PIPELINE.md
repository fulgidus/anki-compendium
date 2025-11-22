# Anki Compendium - RAG Pipeline Architecture

## Overview

The RAG (Retrieval-Augmented Generation) pipeline transforms PDF documents into high-quality Anki flashcards through an 8-stage process powered by Google Gemini AI and **LangChain** (hybrid approach for accelerated development).

### LangChain Integration Strategy
- **Stages 1-2**: LangChain document loaders and text splitters
- **Stages 3-7**: LangChain prompt templates and chains with Gemini
- **Stage 8**: Custom logic with genanki (Anki-specific formatting)

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
│ Stage 1: Extraction & Recursion (🔗 LangChain)                  │
│ ─────────────────────────────────────────────────────────────── │
│ • LangChain PyMuPDFLoader for PDF text extraction               │
│ • Handle multi-column layouts automatically                      │
│ • Preserve structural hierarchy (headings, sections)             │
│ • Extract images and tables (optional, V2)                       │
│ • Code: loader = PyMuPDFLoader(pdf_path); pages = loader.load() │
│ ─────────────────────────────────────────────────────────────── │
│ Output: List of Document objects with text + metadata            │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 2: Chunking (🔗 LangChain)                                │
│ ─────────────────────────────────────────────────────────────── │
│ • LangChain RecursiveCharacterTextSplitter                       │
│ • Chunk size: 500 characters (configurable via admin settings)  │
│ • Overlap: 100 characters (20%, configurable)                    │
│ • Preserve sentence boundaries automatically                     │
│ • Code: splitter.split_documents(pages)                          │
│ ─────────────────────────────────────────────────────────────── │
│ Output: List of Document chunks with metadata                    │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 3: Topic & Subtopic Extraction (🔗 LangChain Chain)       │
│ ─────────────────────────────────────────────────────────────── │
│ • LangChain ChatPromptTemplate + Gemini 1.5 Flash                │
│ • Analyze chunks to identify main topics                         │
│ • Extract subtopics and hierarchical structure                   │
│ • Code: topic_chain = prompt | llm | output_parser              │
│ • Automatic retry logic and error handling                       │
│ ─────────────────────────────────────────────────────────────── │
│ Output: Topic hierarchy (JSON parsed automatically)              │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 4: Topic Refinement (🔗 LangChain Chain)                  │
│ ─────────────────────────────────────────────────────────────── │
│ • LangChain chain with Gemini 1.5 Flash                          │
│ • Consolidate duplicate or overlapping topics                    │
│ • Improve topic naming and hierarchy                             │
│ • Code: refinement_chain.invoke({"topics": topics})             │
│ ─────────────────────────────────────────────────────────────── │
│ Output: Refined topic hierarchy                                  │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 5: Tag Generation (🔗 LangChain Chain)                    │
│ ─────────────────────────────────────────────────────────────── │
│ • LangChain chain with Gemini 1.5 Flash                          │
│ • Generate relevant tags for each topic                          │
│ • Include domain-specific keywords                               │
│ • Code: tag_chain.invoke({"topics": refined_topics})            │
│ ─────────────────────────────────────────────────────────────── │
│ Output: Tags per topic (array, JSON parsed)                      │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 6: Question Generation (🔗 LangChain Chain)               │
│ ─────────────────────────────────────────────────────────────── │
│ • LangChain ChatPromptTemplate with Gemini 1.5 Flash             │
│ • Generate questions based on topics and chunks                  │
│ • Apply spaced repetition principles (via prompt)                │
│ • Focus on active recall (not recognition)                       │
│ • User-configurable density, language, custom instructions       │
│ • Code: question_chain.invoke({context, topics, settings})      │
│ ─────────────────────────────────────────────────────────────── │
│ Output: List of questions (JSON structured)                      │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 7: Question Answering (🔗 LangChain Chain)                │
│ ─────────────────────────────────────────────────────────────── │
│ • LangChain chain with Gemini 1.5 Flash                          │
│ • Generate answers for each question                             │
│ • Validate answers against source text (via retrieval)           │
│ • Ensure answer quality: 2-10 sentences (configurable)          │
│ • Code: answer_chain.invoke({question, context})                │
│ ─────────────────────────────────────────────────────────────── │
│ Output: Q&A pairs (question + answer, structured)                │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 8: Card Generation (⚙️ Custom Logic)                      │
│ ─────────────────────────────────────────────────────────────── │
│ • Custom Python logic (NOT LangChain)                            │
│ • Format Q&A pairs into Anki Basic cards                         │
│ • Apply final refinement (optional, Gemini 1.5 Pro via chain)   │
│ • Add metadata (tags, topics, source)                            │
│ • Generate .apkg file using genanki library                      │
│ • Validate card quality (minimum info principle)                 │
│ • Code: deck.add_note(note); package.write_to_file(path)        │
│ ─────────────────────────────────────────────────────────────── │
│ Output: .apkg file (Anki deck) - Full custom control            │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
Upload to MinIO → Update job status → Notify user

---

## LangChain Implementation Benefits

### Time Savings Breakdown
- **Stage 1 (Extraction)**: -70% dev time (LangChain loader vs custom PyMuPDF)
- **Stage 2 (Chunking)**: -80% dev time (battle-tested splitter)
- **Stages 3-7 (Chains)**: -40% dev time (prompt templates, retry logic, error handling)
- **Stage 8 (Cards)**: 0% (custom logic required)

**Total estimated time savings: 2-3 weeks** on 8-10 week MVP timeline
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

### API Usage Pattern (LangChain)

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import JsonOutputParser

# Initialize Gemini via LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.7,
    max_output_tokens=2048
)

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert educator."),
    ("user", "{input}")
])

# Create chain with output parsing
output_parser = JsonOutputParser()
chain = prompt | llm | output_parser

# Invoke chain (automatic retry on rate limit, error handling)
result = chain.invoke({"input": "Extract topics from this text..."})
```

**LangChain Benefits**:
- Automatic retry logic for rate limits
- Built-in error handling
- Structured output parsing
- Prompt template management
- Logging and observability

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

### Embedding Generation (LangChain)

```python
from langchain.embeddings import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import PGVector

# Initialize embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=settings.GEMINI_API_KEY,
    task_type="retrieval_document"
)

# Create vector store (automatic embedding generation)
vectorstore = PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    connection_string=DATABASE_URL,
    collection_name=f"job_{job_id}"
)
```

### Similarity Search (LangChain)

```python
# Semantic search (automatic query embedding + similarity)
similar_chunks = vectorstore.similarity_search(
    query="What is the main concept?",
    k=5  # Top 5 most relevant chunks
)

# With similarity scores
similar_chunks_with_scores = vectorstore.similarity_search_with_score(
    query="Explain the process",
    k=5
)

# For each chunk:
for doc, score in similar_chunks_with_scores:
    print(f"Similarity: {score}")
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}")
```

**LangChain Benefits**:
- Automatic embedding generation and storage
- Built-in similarity search with multiple algorithms
- Metadata filtering
- No manual SQL queries needed

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
