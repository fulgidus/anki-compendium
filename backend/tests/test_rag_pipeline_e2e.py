"""
End-to-End RAG Pipeline Test

Tests the complete pipeline from PDF upload through Anki deck generation.
This is a comprehensive white-box test that validates all 8 stages.
"""
import asyncio
import os
import tempfile
import time
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.rag.pipeline import generate_anki_deck_from_pdf


def create_test_pdf(output_path: str) -> None:
    """
    Create a simple test PDF with Python programming content.
    
    Uses PyMuPDF to create a multi-page PDF with structured content.
    """
    import pymupdf
    
    doc = pymupdf.open()
    
    # Page 1: Title and Variables
    page1 = doc.new_page()
    page1.insert_text((72, 72), "Python Programming Basics", fontsize=20, fontname="helv")
    page1.insert_text((72, 120), "1. Variables and Data Types", fontsize=16, fontname="helv")
    page1.insert_text((72, 150), 
        "Variables in Python are used to store data. Python has several built-in\n"
        "data types including integers, floats, strings, and booleans. You don't\n"
        "need to declare the type explicitly - Python infers it automatically.\n\n"
        "Example: x = 10 (integer), y = 3.14 (float), name = 'Alice' (string),\n"
        "is_valid = True (boolean)\n\n"
        "Key Points:\n"
        "- Variables are dynamically typed\n"
        "- No declaration needed\n"
        "- Case-sensitive naming\n"
        "- Can be reassigned to different types",
        fontsize=11, fontname="helv"
    )
    
    # Page 2: Functions
    page2 = doc.new_page()
    page2.insert_text((72, 72), "2. Functions", fontsize=16, fontname="helv")
    page2.insert_text((72, 100),
        "Functions are reusable blocks of code that perform specific tasks.\n"
        "They are defined using the 'def' keyword followed by the function name\n"
        "and parameters in parentheses.\n\n"
        "Functions can accept parameters and return values. They help organize\n"
        "code and make it more modular and maintainable.\n\n"
        "Example:\n"
        "def greet(name):\n"
        "    return f'Hello, {name}!'\n\n"
        "Benefits of functions:\n"
        "- Code reusability\n"
        "- Better organization\n"
        "- Easier testing and debugging\n"
        "- Modularity",
        fontsize=11, fontname="helv"
    )
    
    # Page 3: Loops
    page3 = doc.new_page()
    page3.insert_text((72, 72), "3. Loops", fontsize=16, fontname="helv")
    page3.insert_text((72, 100),
        "Python has two main types of loops: for loops and while loops.\n"
        "For loops iterate over a sequence (like a list or range), while\n"
        "while loops continue until a condition becomes false.\n\n"
        "Example:\n"
        "- for i in range(5) will iterate 5 times\n"
        "- while x < 10 will continue until x is no longer less than 10\n\n"
        "Loop Control:\n"
        "- break: Exit the loop early\n"
        "- continue: Skip to next iteration\n"
        "- else clause: Executes when loop completes normally\n\n"
        "Best Practices:\n"
        "- Use for loops for known iterations\n"
        "- Use while loops for conditional iterations\n"
        "- Avoid infinite loops with proper exit conditions",
        fontsize=11, fontname="helv"
    )
    
    doc.save(output_path)
    doc.close()


@pytest.mark.asyncio
async def test_complete_rag_pipeline():
    """
    Test the complete RAG pipeline from PDF to Anki deck.
    
    This test validates:
    1. PDF loading and text extraction
    2. Text chunking
    3. Topic extraction via Gemini
    4. Topic refinement
    5. Tag generation
    6. Question generation
    7. Answer generation
    8. Anki .apkg file creation
    """
    print("\n" + "="*80)
    print("STARTING COMPLETE RAG PIPELINE END-TO-END TEST")
    print("="*80)
    
    # Validate API key
    if not settings.GEMINI_API_KEY:
        pytest.skip("GEMINI_API_KEY not configured")
    
    # Create temp directories
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "test_python_basics.pdf"
        output_path = Path(tmpdir) / "output.apkg"
        
        # Stage 0: Create test PDF
        print("\n[STAGE 0] Creating test PDF...")
        start_time = time.time()
        create_test_pdf(str(pdf_path))
        creation_time = time.time() - start_time
        
        assert pdf_path.exists(), "Test PDF creation failed"
        pdf_size = pdf_path.stat().st_size
        print(f"✓ PDF created: {pdf_size:,} bytes ({creation_time:.2f}s)")
        
        # Run complete pipeline
        print("\n[PIPELINE] Starting RAG pipeline execution...")
        pipeline_start = time.time()
        
        try:
            result = await generate_anki_deck_from_pdf(
                pdf_path=str(pdf_path),
                output_path=str(output_path),
                gemini_api_key=settings.GEMINI_API_KEY,
                database_url=settings.DATABASE_URL,
                deck_name="Python Basics Test Deck",
                subject="Programming",
                chapter="Python Fundamentals",
                card_density="medium",
                custom_tags=["python", "programming", "basics"],
                model_name="gemini-2.0-flash-exp",
                chunk_size=500,
                chunk_overlap=100,
            )
            
            pipeline_time = time.time() - pipeline_start
            
            # Validate results
            print("\n" + "="*80)
            print("PIPELINE EXECUTION RESULTS")
            print("="*80)
            print(f"Total processing time: {pipeline_time:.2f}s")
            print(f"Pages processed: {result['num_pages']}")
            print(f"Chunks created: {result['num_chunks']}")
            print(f"Topics extracted: {result['num_topics']}")
            print(f"Tags generated: {result['num_tags']}")
            print(f"Flashcards generated: {result['num_cards']}")
            print(f"Output file: {result['output_path']}")
            
            # Assertions
            assert result['num_pages'] == 3, f"Expected 3 pages, got {result['num_pages']}"
            assert result['num_chunks'] > 0, "No chunks created"
            assert result['num_topics'] > 0, "No topics extracted"
            assert result['num_cards'] > 0, "No flashcards generated"
            assert output_path.exists(), "Output .apkg file not created"
            
            # Validate output file
            output_size = output_path.stat().st_size
            print(f"\n✓ Output .apkg file: {output_size:,} bytes")
            assert output_size > 1000, "Output file suspiciously small"
            
            # Quality checks
            cards_per_page = result['num_cards'] / result['num_pages']
            print(f"✓ Card density: {cards_per_page:.1f} cards/page")
            assert cards_per_page >= 2, "Card generation density too low"
            
            chunks_per_page = result['num_chunks'] / result['num_pages']
            print(f"✓ Chunk density: {chunks_per_page:.1f} chunks/page")
            
            # Performance check
            time_per_card = pipeline_time / result['num_cards']
            print(f"✓ Performance: {time_per_card:.2f}s per card")
            
            print("\n" + "="*80)
            print("✓ ALL TESTS PASSED")
            print("="*80)
            
        except Exception as e:
            print(f"\n✗ PIPELINE FAILED: {e}")
            import traceback
            traceback.print_exc()
            raise


@pytest.mark.asyncio
async def test_stage_1_pdf_loading():
    """Test Stage 1: PDF loading and text extraction."""
    from app.rag.loaders import load_pdf
    
    print("\n[STAGE 1 TEST] PDF Loading")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "test.pdf"
        create_test_pdf(str(pdf_path))
        
        # Load PDF
        documents = load_pdf(str(pdf_path), page_range=None)
        
        print(f"Loaded {len(documents)} pages")
        assert len(documents) == 3, f"Expected 3 pages, got {len(documents)}"
        
        # Check content
        for i, doc in enumerate(documents):
            print(f"Page {i+1}: {len(doc.page_content)} chars")
            assert len(doc.page_content) > 50, f"Page {i+1} has too little content"
            assert "metadata" in dir(doc), "Document missing metadata"
        
        print("✓ Stage 1 passed")


@pytest.mark.asyncio
async def test_stage_2_chunking():
    """Test Stage 2: Text chunking."""
    from app.rag.loaders import load_pdf
    from app.rag.chunking import create_chunks
    
    print("\n[STAGE 2 TEST] Text Chunking")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "test.pdf"
        create_test_pdf(str(pdf_path))
        
        documents = load_pdf(str(pdf_path))
        chunks = create_chunks(documents, chunk_size=500, overlap=100)
        
        print(f"Created {len(chunks)} chunks from {len(documents)} pages")
        assert len(chunks) >= len(documents), "Should have at least one chunk per page"
        
        # Validate chunk properties
        for i, chunk in enumerate(chunks):
            assert hasattr(chunk, 'page_content'), "Chunk missing page_content"
            assert hasattr(chunk, 'metadata'), "Chunk missing metadata"
            assert 'chunk_index' in chunk.metadata, "Missing chunk_index"
            print(f"Chunk {i}: {chunk.metadata.get('chunk_size')} chars")
        
        print("✓ Stage 2 passed")


@pytest.mark.asyncio
async def test_stage_3_topic_extraction():
    """Test Stage 3: Topic extraction using Gemini."""
    from app.rag.chains.topic_extraction import extract_topics_from_chunk
    
    print("\n[STAGE 3 TEST] Topic Extraction")
    
    if not settings.GEMINI_API_KEY:
        pytest.skip("GEMINI_API_KEY not configured")
    
    test_text = """
    Variables in Python are used to store data. Python has several built-in
    data types including integers, floats, strings, and booleans. You don't
    need to declare the type explicitly - Python infers it automatically.
    """
    
    result = await extract_topics_from_chunk(
        chunk_text=test_text,
        chunk_index=0,
        total_chunks=1,
        model_name="gemini-2.0-flash-exp"
    )
    
    print(f"Extracted: {result}")
    assert isinstance(result, dict), "Result should be a dictionary"
    assert len(result) > 0, "No topics extracted"
    
    print("✓ Stage 3 passed")


@pytest.mark.asyncio
async def test_stage_8_anki_generation():
    """Test Stage 8: Anki deck generation."""
    from app.rag.anki.card_generator import create_anki_deck
    
    print("\n[STAGE 8 TEST] Anki Deck Generation")
    
    test_qa_pairs = [
        {
            "question": "What are the main data types in Python?",
            "answer": "Integers, floats, strings, and booleans",
            "context": "Python variables",
            "explanation": "Python has dynamic typing",
            "difficulty": "easy"
        },
        {
            "question": "How do you define a function in Python?",
            "answer": "Use the 'def' keyword followed by function name and parameters",
            "context": "Python functions",
            "explanation": "Functions are defined using def keyword",
            "difficulty": "easy"
        }
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.apkg"
        
        result_path = create_anki_deck(
            qa_pairs=test_qa_pairs,
            deck_name="Test Deck",
            tags=["test", "python"],
            source="test_source",
            output_path=str(output_path)
        )
        
        assert Path(result_path).exists(), "Anki deck not created"
        size = Path(result_path).stat().st_size
        print(f"Created .apkg file: {size:,} bytes")
        assert size > 500, "Anki deck file too small"
        
        print("✓ Stage 8 passed")


@pytest.mark.asyncio
async def test_pipeline_error_handling():
    """Test pipeline error handling with invalid inputs."""
    print("\n[ERROR HANDLING TEST]")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "output.apkg"
        
        # Test with non-existent PDF
        with pytest.raises(FileNotFoundError):
            await generate_anki_deck_from_pdf(
                pdf_path="/nonexistent/file.pdf",
                output_path=str(output_path),
                gemini_api_key=settings.GEMINI_API_KEY or "fake_key",
                database_url=settings.DATABASE_URL,
            )
        
        print("✓ Error handling works correctly")


if __name__ == "__main__":
    # Run tests directly
    print("Running RAG Pipeline E2E Tests...")
    asyncio.run(test_complete_rag_pipeline())
