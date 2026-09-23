"""
DocuMind AI — Text Chunker
Splits cleaned text into overlapping chunks for embedding and retrieval.

Phase 1 Status: FUNCTIONAL — sentence-aware chunking is implemented.
Phase 2: Add heading-aware, section-aware, and semantic chunking strategies.

Design principle (from context.md):
    Do not blindly split at arbitrary character boundaries.
    Prefer preserving paragraphs, headings, and logical document boundaries.

Integration point:
    Input:  cleaned text string + page/section metadata
    Output: list[TextChunk]
    Used by: ingestion pipeline → EmbeddingService → Pinecone
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger("documind.ingestion.chunker")


@dataclass
class TextChunk:
    """
    A single chunk of text ready for embedding and indexing.

    chunk_id is derived from document_id + page + chunk index,
    enabling incremental update and deletion in Pinecone.
    """
    chunk_id: str
    text: str
    document_id: str
    document_name: str
    page_number: int | None = None
    section_heading: str | None = None
    chunk_index: int = 0
    metadata: dict = field(default_factory=dict)


class TextChunker:
    """
    Splits document text into overlapping chunks for RAG indexing.

    Strategy: Paragraph-aware chunking with overlap.
    - Splits on paragraph boundaries (double newlines) first.
    - If a paragraph exceeds max_chunk_size, splits on sentences.
    - Adds overlap between chunks to preserve context at boundaries.

    Parameters:
        max_chunk_size: Maximum characters per chunk (default 1000).
        overlap_size:   Characters of overlap between consecutive chunks (default 200).

    These values should be tuned experimentally (see context.md).
    """

    def __init__(self, max_chunk_size: int = 1000, overlap_size: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        logger.info(
            "TextChunker initialized (max=%d, overlap=%d)", max_chunk_size, overlap_size
        )

    def chunk(
        self,
        text: str,
        document_id: str,
        document_name: str,
        page_number: int | None = None,
        section_heading: str | None = None,
        extra_metadata: dict | None = None,
    ) -> list[TextChunk]:
        """
        Split text into chunks with metadata.

        Args:
            text: Cleaned document text.
            document_id: UUID of the parent document (for Pinecone upsert + deletion).
            document_name: Human-readable document name for citation.
            page_number: Page number in the source document.
            section_heading: Section heading if available.
            extra_metadata: Any additional metadata to attach to each chunk.

        Returns:
            List of TextChunk objects ready for embedding.
        """
        if not text or not text.strip():
            return []

        raw_chunks = self._split_into_raw_chunks(text)
        result: list[TextChunk] = []

        for idx, chunk_text in enumerate(raw_chunks):
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue

            chunk_id = f"{document_id}_p{page_number or 0}_c{idx:03d}"
            metadata = extra_metadata.copy() if extra_metadata else {}

            result.append(TextChunk(
                chunk_id=chunk_id,
                text=chunk_text,
                document_id=document_id,
                document_name=document_name,
                page_number=page_number,
                section_heading=section_heading,
                chunk_index=idx,
                metadata=metadata,
            ))

        logger.debug(
            "Chunked document '%s' page %s: %d chunks from %d chars",
            document_name, page_number, len(result), len(text)
        )
        return result

    def _split_into_raw_chunks(self, text: str) -> list[str]:
        """
        Split text into raw chunks using paragraph-aware strategy.

        Algorithm:
        1. Split on paragraph breaks (double newlines).
        2. Accumulate paragraphs until max_chunk_size is reached.
        3. When limit reached, save current chunk and start a new one
           with overlap from the end of the previous chunk.
        """
        paragraphs = re.split(r"\n\s*\n", text)
        chunks: list[str] = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # If a single paragraph exceeds max_chunk_size, split it by sentences
            if len(para) > self.max_chunk_size:
                sentence_chunks = self._split_by_sentences(para)
                for sentence_chunk in sentence_chunks:
                    if len(current_chunk) + len(sentence_chunk) + 1 > self.max_chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk)
                            # Overlap: keep last N chars
                            current_chunk = current_chunk[-self.overlap_size:] + "\n" + sentence_chunk
                        else:
                            chunks.append(sentence_chunk)
                            current_chunk = sentence_chunk[-self.overlap_size:]
                    else:
                        current_chunk = (current_chunk + "\n" + sentence_chunk).strip()
            else:
                if len(current_chunk) + len(para) + 2 > self.max_chunk_size:
                    if current_chunk:
                        chunks.append(current_chunk)
                        current_chunk = current_chunk[-self.overlap_size:] + "\n\n" + para
                    else:
                        chunks.append(para)
                        current_chunk = ""
                else:
                    current_chunk = (current_chunk + "\n\n" + para).strip()

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _split_by_sentences(self, text: str) -> list[str]:
        """Split text into sentence-sized pieces as a fallback."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks: list[str] = []
        current = ""

        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= self.max_chunk_size:
                current = (current + " " + sentence).strip()
            else:
                if current:
                    chunks.append(current)
                current = sentence

        if current:
            chunks.append(current)

        return chunks
