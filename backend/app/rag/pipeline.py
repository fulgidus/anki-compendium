"""
RAG Pipeline Orchestrator - Coordinates all 8 stages.

PDF → Chunks → Topics → Refinement → Tags → Questions → Answers → Anki Deck

Stages:
1. Document Loading (PyMuPDFLoader)
2. Text Chunking (RecursiveCharacterTextSplitter)
3. Topic Extraction (LangChain)
4. Topic Refinement (LangChain)
5. Tag Generation (LangChain)
6. Question Generation (LangChain)
7. Question Answering (LangChain + RAG)
8. Anki Card Generation (genanki - NO LangChain)
"""

import logging
from pathlib import Path
from typing import Any

from app.rag.anki.card_generator import create_anki_deck
from app.rag.chains.question_answering import generate_answers_batch
from app.rag.chains.question_generation import generate_questions
from app.rag.chains.tag_generation import generate_tags
from app.rag.chains.topic_extraction import extract_topics_from_chunk
from app.rag.chains.topic_refinement import refine_topics
from app.rag.chunking import create_chunks
from app.rag.embeddings import create_embeddings
from app.rag.loaders import load_pdf
# from app.rag.vectorstore import create_vectorstore  # Not used in current pipeline

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Orchestrates the complete RAG pipeline from PDF to Anki deck.
    """

    def __init__(
        self,
        gemini_api_key: str,
        database_url: str,
        model_name: str = "gemini-2.0-flash-exp",
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):
        """
        Initialize RAG pipeline.

        Args:
            gemini_api_key: Google Gemini API key
            database_url: PostgreSQL connection string for vector store
            model_name: Gemini model to use for LLM chains
            chunk_size: Text chunk size for splitting
            chunk_overlap: Overlap between chunks
        """
        self.gemini_api_key = gemini_api_key
        self.database_url = database_url
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Pipeline state
        self.documents = []
        self.chunks = []
        self.extracted_topics = []
        self.refined_topics = {}
        self.tags = {}
        self.qa_pairs = []

    async def run(
        self,
        pdf_path: str,
        output_path: str,
        deck_name: str = "Generated Deck",
        subject: str = "",
        chapter: str = "",
        card_density: str = "medium",
        custom_tags: list[str] | None = None,
        page_start: int | None = None,
        page_end: int | None = None,
    ) -> dict[str, Any]:
        """
        Run the complete RAG pipeline.

        Args:
            pdf_path: Path to input PDF file
            output_path: Path to output .apkg file
            deck_name: Name of the Anki deck
            subject: Subject area (e.g., "biology")
            chapter: Chapter or section identifier
            card_density: Number of cards per chunk (low, medium, high)
            custom_tags: User-provided tags
            page_start: Starting page number (optional)
            page_end: Ending page number (optional)

        Returns:
            Dictionary with pipeline results and statistics
        """
        logger.info(f"Starting RAG pipeline for {pdf_path}")

        # Stage 1: Document Loading
        logger.info("Stage 1: Loading PDF...")
        self.documents = await self.stage_1_load_pdf(pdf_path, page_start, page_end)
        logger.info(f"Loaded {len(self.documents)} pages")

        # Stage 2: Text Chunking
        logger.info("Stage 2: Chunking documents...")
        self.chunks = await self.stage_2_chunk_documents(self.documents)
        logger.info(f"Created {len(self.chunks)} chunks")

        # Stage 3: Topic Extraction
        logger.info("Stage 3: Extracting topics from chunks...")
        self.extracted_topics = await self.stage_3_extract_topics(self.chunks)
        logger.info(f"Extracted topics from {len(self.extracted_topics)} chunks")

        # Stage 4: Topic Refinement
        logger.info("Stage 4: Refining topics...")
        self.refined_topics = await self.stage_4_refine_topics(
            self.extracted_topics, Path(pdf_path).stem, subject
        )
        logger.info(f"Refined to {len(self.refined_topics.get('main_topics', []))} main topics")

        # Stage 5: Tag Generation
        logger.info("Stage 5: Generating tags...")
        self.tags = await self.stage_5_generate_tags(
            self.refined_topics, Path(pdf_path).stem, subject, chapter, custom_tags
        )
        logger.info(f"Generated {len(self.tags.get('tags', []))} tags")

        # Stage 6 & 7: Question Generation and Answering
        logger.info("Stage 6 & 7: Generating questions and answers...")
        self.qa_pairs = await self.stage_6_7_generate_qa_pairs(
            self.chunks, self.refined_topics, card_density
        )
        logger.info(f"Generated {len(self.qa_pairs)} Q&A pairs")

        # Stage 8: Anki Card Generation
        logger.info("Stage 8: Creating Anki deck...")
        result_path = await self.stage_8_create_anki_deck(
            self.qa_pairs, deck_name, self.tags.get("tags", []), output_path
        )
        logger.info(f"Anki deck created: {result_path}")

        return {
            "output_path": result_path,
            "num_pages": len(self.documents),
            "num_chunks": len(self.chunks),
            "num_topics": len(self.refined_topics.get("main_topics", [])),
            "num_tags": len(self.tags.get("tags", [])),
            "num_cards": len(self.qa_pairs),
        }

    async def stage_1_load_pdf(
        self, pdf_path: str, page_start: int | None, page_end: int | None
    ) -> list:
        """Stage 1: Load PDF documents."""
        return await load_pdf(pdf_path, page_start, page_end)

    async def stage_2_chunk_documents(self, documents: list) -> list:
        """Stage 2: Chunk documents into smaller pieces."""
        return create_chunks(
            documents, chunk_size=self.chunk_size, overlap=self.chunk_overlap
        )

    async def stage_3_extract_topics(self, chunks: list) -> list[dict]:
        """Stage 3: Extract topics from each chunk."""
        topics = []
        for i, chunk in enumerate(chunks):
            topic_data = await extract_topics_from_chunk(
                chunk_text=chunk.page_content,
                chunk_index=i,
                total_chunks=len(chunks),
                model_name=self.model_name,
            )
            topics.append(topic_data)
        return topics

    async def stage_4_refine_topics(
        self, extracted_topics: list[dict], document_title: str, subject: str
    ) -> dict:
        """Stage 4: Refine and consolidate topics."""
        return await refine_topics(
            extracted_topics=extracted_topics,
            document_title=document_title,
            subject=subject,
            model_name=self.model_name,
        )

    async def stage_5_generate_tags(
        self,
        topics: dict,
        document_title: str,
        subject: str,
        chapter: str,
        custom_tags: list[str] | None,
    ) -> dict:
        """Stage 5: Generate Anki tags."""
        return await generate_tags(
            topics=topics,
            document_title=document_title,
            subject=subject,
            chapter=chapter,
            custom_tags=custom_tags,
            model_name=self.model_name,
        )

    async def stage_6_7_generate_qa_pairs(
        self, chunks: list, topics: dict, density: str
    ) -> list[dict]:
        """Stages 6 & 7: Generate questions and answers for each chunk."""
        all_qa_pairs = []

        for chunk in chunks:
            # Stage 6: Generate questions
            questions = await generate_questions(
                chunk_text=chunk.page_content,
                topics=topics,
                density=density,
                model_name=self.model_name,
            )

            # Stage 7: Generate answers for the questions
            qa_pairs = await generate_answers_batch(
                questions=questions,
                chunk_text=chunk.page_content,
                model_name=self.model_name,
            )

            all_qa_pairs.extend(qa_pairs)

        return all_qa_pairs

    async def stage_8_create_anki_deck(
        self, qa_pairs: list[dict], deck_name: str, tags: list[str], output_path: str
    ) -> str:
        """Stage 8: Create Anki deck (custom genanki - NO LangChain)."""
        return create_anki_deck(
            qa_pairs=qa_pairs, deck_name=deck_name, tags=tags, output_path=output_path
        )


async def generate_anki_deck_from_pdf(
    pdf_path: str,
    output_path: str,
    gemini_api_key: str,
    database_url: str,
    deck_name: str = "Generated Deck",
    subject: str = "",
    chapter: str = "",
    card_density: str = "medium",
    custom_tags: list[str] | None = None,
    page_start: int | None = None,
    page_end: int | None = None,
    model_name: str = "gemini-2.0-flash-exp",
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> dict[str, Any]:
    """
    High-level function to generate an Anki deck from a PDF.

    Args:
        pdf_path: Path to input PDF
        output_path: Path to output .apkg file
        gemini_api_key: Google Gemini API key
        database_url: PostgreSQL connection string
        deck_name: Name of the Anki deck
        subject: Subject area
        chapter: Chapter identifier
        card_density: Card density (low, medium, high)
        custom_tags: User-provided tags
        page_start: Starting page (optional)
        page_end: Ending page (optional)
        model_name: Gemini model name
        chunk_size: Text chunk size
        chunk_overlap: Chunk overlap

    Returns:
        Dictionary with pipeline results
    """
    pipeline = RAGPipeline(
        gemini_api_key=gemini_api_key,
        database_url=database_url,
        model_name=model_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return await pipeline.run(
        pdf_path=pdf_path,
        output_path=output_path,
        deck_name=deck_name,
        subject=subject,
        chapter=chapter,
        card_density=card_density,
        custom_tags=custom_tags,
        page_start=page_start,
        page_end=page_end,
    )
