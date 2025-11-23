# RAG Pipeline Bug Fix Guide

**Quick reference for fixing the critical issues found during E2E testing**

---

## ✅ FIXED: Stage 4 Prompt Template Fix

**File:** `backend/app/rag/prompts/topic_refinement.py`

**Status:** ✅ **FIXED** - JSON examples removed to prevent template variable confusion

**Problem:** LangChain interprets JSON examples as template variables

**Current (BROKEN):**
```python
"""
Output Format: JSON object with:
{
  "refined_topics": ["Topic 1", "Topic 2", ...],
  "topic_hierarchy": {"Parent Topic": ["Subtopic 1", "Subtopic 2"], ...}
}
"""
```

**Fix Option 1 - Escape Braces:**
```python
"""
Output Format: JSON object with:
{{
  "refined_topics": ["Topic 1", "Topic 2", ...],
  "topic_hierarchy": {{"Parent Topic": ["Subtopic 1", "Subtopic 2"], ...}}
}}
"""
```

**Fix Option 2 - Remove JSON Example:**
```python
"""
Output Format: Return a JSON object with two fields:
- refined_topics: array of refined topic strings
- topic_hierarchy: object mapping parent topics to child topics
"""
```

**Verification:**
```bash
cd backend
source venv/bin/activate
PYTHONPATH=/home/fulgidus/Documents/anki-compendium/backend python tests/test_rag_pipeline_e2e.py
```

---

## ✅ FIXED: Stage 1 Function Signature

**File:** `backend/app/rag/pipeline.py` line ~159

**Problem:** load_pdf() called with wrong parameters

**Fix Applied:**
```python
async def stage_1_load_pdf(
    self, pdf_path: str, page_start: int | None, page_end: int | None
) -> list:
    """Stage 1: Load PDF documents."""
    if page_start is not None and page_end is not None:
        return load_pdf(pdf_path, page_range=(page_start, page_end))
    return load_pdf(pdf_path)
```

---

## ✅ FIXED: Stage 3 Prompt Parameters

**File:** `backend/app/rag/chains/topic_extraction.py` line ~67

**Problem:** Prompt expected `metadata`, code passed `chunk_index` and `total_chunks`

**Fix Applied:**
```python
# Build metadata string
metadata = f"Chunk {chunk_index + 1} of {total_chunks}"

result = await chain.ainvoke(
    {
        "chunk_text": chunk_text,
        "metadata": metadata,  # Now matches template
    }
)
```

---

## ✅ COMPLETED: Prompt Template Audit

**Files Audited and Fixed:**

1. ✅ `backend/app/rag/prompts/topic_extraction.py` - FIXED (already working)
2. ✅ `backend/app/rag/prompts/topic_refinement.py` - FIXED (JSON examples removed)
3. ✅ `backend/app/rag/prompts/tag_generation.py` - **FIXED** (escaped braces in system message)
4. ✅ `backend/app/rag/prompts/question_generation.py` - VERIFIED (already properly escaped)
5. ✅ `backend/app/rag/prompts/question_answering.py` - **FIXED** (escaped braces in system message)

**Validation Pattern:**

For each prompt file:
1. Read the prompt template
2. List all `{variable}` placeholders
3. Find corresponding chain file
4. Verify `chain.ainvoke({...})` passes exactly those variables
5. Check for any `{` or `}` in prompt text that should be escaped as `{{` or `}}`

---

## ✅ FIXED: Stage 8 None-Value Handling

**File:** `backend/app/rag/anki/card_generator.py` lines 213-234

**Status:** ✅ **FIXED** - None values now handled gracefully, invalid cards skipped

**Problem:** LLM (Gemini) occasionally returns `null` values in JSON responses, causing `genanki` to crash

**Root Cause:**
```python
# BROKEN - .get() returns None if key exists with None value
question = qa.get("question", "")  # Returns None, not ""
```

**Fix Applied:**
```python
# FIXED - Use 'or' operator to convert None to empty string
question = qa.get("question") or ""
answer = qa.get("answer") or ""

# Skip cards with missing question or answer
if not question or not answer:
    logger.warning(f"Skipping card with missing data: question={question!r}, answer={answer!r}")
    continue
```

**Verification:**
```bash
cd backend
source venv/bin/activate
pytest tests/test_rag_pipeline_e2e.py::test_complete_rag_pipeline -v -s
```

**Expected Results:**
- ✅ Stage 8 completes successfully
- ✅ .apkg file created with >0 cards
- ⚠️ Warning logs for any skipped cards
- ✅ No TypeError or NoneType crashes

---

## 📋 Full Test Execution

```bash
# Terminal 1: Start services (if not running)
cd infra/docker-compose
docker compose -f docker-compose.dev.yml up -d

# Terminal 2: Run E2E test
cd backend
source venv/bin/activate
export PYTHONPATH=/home/fulgidus/Documents/anki-compendium/backend

# Run full pipeline test
python tests/test_rag_pipeline_e2e.py

# OR run with pytest (if installed)
pytest tests/test_rag_pipeline_e2e.py -v -s
```

---

## 🔍 Debugging Tips

### Check Gemini API Status
```bash
# Verify API key is set
cd backend
source venv/bin/activate
python validate_api_config.py
```

### Monitor Rate Limiting
- Watch for `ResourceExhausted` errors in output
- Gemini 2.0 Flash Experimental: 10 RPM
- Consider switching to gemini-1.5-flash (15 RPM)

### Check Stage-by-Stage
```python
# Run individual stage tests
pytest tests/test_rag_pipeline_e2e.py::test_stage_1_pdf_loading -v
pytest tests/test_rag_pipeline_e2e.py::test_stage_2_chunking -v
pytest tests/test_rag_pipeline_e2e.py::test_stage_3_topic_extraction -v
pytest tests/test_rag_pipeline_e2e.py::test_stage_8_anki_generation -v
```

---

## 🎯 Success Criteria

Pipeline is READY when:
- ✅ All 8 stages complete without errors
- ✅ Valid .apkg file generated (>1KB)
- ✅ At least 10 cards created from test PDF
- ✅ Processing time <5 minutes
- ✅ .apkg file imports correctly into Anki desktop

---

## 🚀 Performance Optimization

### Switch to Stable Model
```python
# In backend/app/rag/pipeline.py
# Change default model_name:
model_name: str = "gemini-1.5-flash"  # Was: gemini-2.0-flash-exp
```

### Benefits:
- 15 RPM instead of 10 RPM
- More stable (not experimental)
- Same quality for most tasks

---

## 📊 Test Artifacts

After successful run, check:
- `backend/RAG_PIPELINE_TEST_REPORT.md` - Full test report
- `backend/tests/test_rag_pipeline_e2e.py` - Test suite
- `/tmp/test_python_basics.pdf` - Test input
- `/tmp/output.apkg` - Generated deck (if successful)

---

## 🆘 If Still Failing

1. **Check logs:** Look for specific error messages
2. **Verify services:** Ensure PostgreSQL, MinIO, RabbitMQ are running
3. **Check API quota:** Verify Gemini API hasn't hit daily limit
4. **Test isolation:** Run stage tests individually to isolate failures
5. **Clear cache:** Python may cache old prompt templates - restart Python interpreter

---

**Last Updated:** 2025-11-23  
**Status:** ✅ **ALL 8 STAGES FUNCTIONAL** - Production Ready
