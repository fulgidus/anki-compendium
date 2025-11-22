# LangChain Hybrid Integration - Decision Summary

**Date**: 2025-11-22  
**Decision**: ✅ Approved  
**Impact**: -2 to -3 weeks on MVP timeline

---

## Overview

Anki Compendium now uses a **hybrid LangChain approach** to accelerate RAG pipeline development while maintaining precise control over Anki-specific card generation.

---

## What Changed

### Architecture Updates

#### Before (Full Custom)
- Custom PDF extraction with PyMuPDF
- Custom text chunking and tokenization
- Manual embedding generation and storage
- Custom prompt management
- Direct Gemini API calls with manual retry logic
- Custom genanki card generation

**Estimated Development**: 8-10 weeks

#### After (Hybrid LangChain)
- **Stages 1-2**: LangChain document loaders + text splitters
- **Vector Store**: LangChain PGVector integration
- **Stages 3-7**: LangChain chains + prompt templates
- **Stage 8**: Custom genanki (unchanged)

**Estimated Development**: 6-7 weeks (-2 to -3 weeks)

---

## LangChain Components Used

### ✅ Where We Use LangChain

| Component | Purpose | Benefit |
|-----------|---------|---------|
| `PyMuPDFLoader` | PDF text extraction | Battle-tested, handles edge cases |
| `RecursiveCharacterTextSplitter` | Intelligent chunking | Preserves semantic boundaries |
| `GoogleGenerativeAIEmbeddings` | Gemini embeddings | Automatic generation and caching |
| `PGVector` | Vector store integration | No manual SQL for similarity search |
| `ChatGoogleGenerativeAI` | Gemini LLM wrapper | Auto-retry, error handling, logging |
| `ChatPromptTemplate` | Prompt management | Clean templates, easy testing |
| `JsonOutputParser` | Structured outputs | Automatic parsing and validation |
| Chains (LCEL) | Pipeline orchestration | Composable, traceable, debuggable |

### ❌ Where We DON'T Use LangChain

| Component | Reason | Implementation |
|-----------|--------|----------------|
| Anki Card Generation | LangChain has no Anki support | Custom `genanki` logic |
| Card Formatting | Need precise control over front/back/tags | Python dictionaries + genanki |
| .apkg File Creation | Anki-specific binary format | genanki.Package API |

---

## Code Examples

### Stage 1-2: Loading & Chunking

```python
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load PDF (replaces ~50 lines of custom PyMuPDF code)
loader = PyMuPDFLoader("document.pdf")
pages = loader.load()

# Chunk intelligently (replaces ~100 lines of tokenization logic)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
chunks = splitter.split_documents(pages)
```

**Time Saved**: ~1-2 weeks

### Vector Store Setup

```python
from langchain.vectorstores import PGVector
from langchain.embeddings import GoogleGenerativeAIEmbeddings

# Automatic embedding + storage (replaces ~200 lines of SQL + embedding code)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vectorstore = PGVector.from_documents(
    documents=chunks,
    embedding=embeddings,
    connection_string=DATABASE_URL
)

# Semantic search (replaces manual SQL queries)
results = vectorstore.similarity_search("What is the main concept?", k=5)
```

**Time Saved**: ~1 week

### Stages 3-7: Chains & Prompts

```python
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import JsonOutputParser

# Clean prompt template (replaces string concatenation)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert educator."),
    ("user", "Extract topics from: {text}")
])

# LLM with auto-retry (replaces manual retry loops)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    max_retries=3
)

# Chain with automatic JSON parsing
chain = prompt | llm | JsonOutputParser()
result = chain.invoke({"text": chunk})  # Returns dict, not string
```

**Time Saved**: ~1-2 weeks (across all 5 stages)

### Stage 8: Custom Anki Generation (NO LangChain)

```python
import genanki

# Full control over Anki format
deck = genanki.Deck(deck_id, "My Deck")
note = genanki.Note(
    model=basic_model,
    fields=[question, answer],
    tags=["chemistry", "organic"]
)
deck.add_note(note)
genanki.Package(deck).write_to_file("output.apkg")
```

**Why Custom**: LangChain has no Anki support, we need precise control

---

## Time Savings Breakdown

| Stage | Task | Without LangChain | With LangChain | Savings |
|-------|------|-------------------|----------------|---------|
| 1 | PDF Extraction | 3 days | 0.5 days | -70% |
| 2 | Chunking | 5 days | 1 day | -80% |
| 2.5 | Vector Store | 5 days | 1 day | -80% |
| 3-7 | Chains & Prompts | 10 days | 6 days | -40% |
| 8 | Card Generation | 3 days | 3 days | 0% |
| **Total** | | **26 days** | **11.5 days** | **-56%** |

**Net Savings**: ~14.5 days (2-3 weeks)

---

## Trade-offs

### ✅ Pros
1. **Faster Development**: -2 to -3 weeks on MVP
2. **Battle-Tested**: LangChain components used by thousands of projects
3. **Better Error Handling**: Automatic retries, structured logging
4. **Cleaner Code**: Less boilerplate, more maintainable
5. **Future-Proof**: Easy to swap models/providers
6. **Testing**: Each component independently testable

### ⚠️ Cons
1. **Dependencies**: +50 packages (acceptable for time savings)
2. **Abstraction**: Slightly less control (mitigated by hybrid approach)
3. **Learning Curve**: Team needs to learn LangChain patterns
4. **Updates**: LangChain APIs change frequently (pin versions)

### Mitigation
- Pin LangChain versions in requirements.txt
- Document our usage patterns clearly
- Keep Stage 8 custom (most critical for our use case)
- Easy migration path if needed (component-by-component replacement)

---

## Migration Path (If Needed)

If we ever need to move away from LangChain:

1. **Stage 1**: Replace PyMuPDFLoader → Direct PyMuPDF calls (~1 day)
2. **Stage 2**: Replace splitter → Custom tokenization (~2 days)
3. **Vector Store**: Replace PGVector → Direct SQL + embeddings (~3 days)
4. **Stages 3-7**: Replace chains → Direct Gemini API calls (~5 days)

**Total Migration Effort**: ~2 weeks (if ever needed)

**Likelihood**: Low (LangChain is stable and widely adopted)

---

## Updated Tech Stack

### Backend (Python 3.11+)
- **Framework**: FastAPI
- **Task Queue**: Celery + RabbitMQ
- **ORM**: SQLAlchemy + Alembic
- **RAG Framework**: **LangChain (hybrid)**
  - Document loaders
  - Text splitters
  - Vector store (PGVector)
  - Prompt templates
  - Chains + LCEL
- **PDF Extraction**: LangChain PyMuPDFLoader
- **Embeddings**: GoogleGenerativeAIEmbeddings
- **LLM**: ChatGoogleGenerativeAI (Gemini 1.5 Flash/Pro)
- **Anki Export**: genanki (custom)

### New Dependencies
```txt
langchain>=0.1.0
langchain-core>=0.1.0
langchain-community>=0.0.20
langchain-google-genai>=0.0.6
langchain-postgres>=0.0.3
genanki>=0.13.0
```

---

## Next Steps

### Immediate Actions
1. ✅ Update ARCHITECTURE.md with LangChain details
2. ✅ Update RAG_PIPELINE.md with code examples
3. ✅ Create TASK-004-LANGCHAIN for implementation
4. ⏳ Execute TASK-001 (Docker Compose setup)
5. ⏳ Execute TASK-004 (LangChain integration)

### Implementation Priority
1. **Phase 1**: Docker Compose environment (TASK-001)
2. **Phase 2**: LangChain setup (TASK-004)
3. **Phase 2**: Backend API + Celery workers
4. **Phase 3**: Frontend UI
5. **Phase 4**: Deployment to K8s

---

## Success Metrics

### Before LangChain (Projected)
- MVP completion: 8-10 weeks
- RAG pipeline dev: 26 days
- Custom code: ~1500 lines

### After LangChain (Projected)
- MVP completion: 6-7 weeks ✅
- RAG pipeline dev: 11.5 days ✅
- LangChain + custom: ~800 lines ✅

**Result**: Faster, cleaner, more maintainable codebase

---

## Conclusion

The LangChain hybrid approach is **approved and documented**.

We gain:
- ✅ 2-3 weeks faster MVP delivery
- ✅ Battle-tested components
- ✅ Cleaner, more maintainable code
- ✅ Full control over Anki formatting

We keep:
- ✅ Custom Anki card generation
- ✅ Precise control over Stage 8
- ✅ Easy migration path if needed

**Status**: Ready to implement (TASK-004)

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-22  
**Author**: Project Manager Agent  
**Approved By**: Project Owner
