"""
DocuMind AI — Chunker Tests
Tests the TextChunker independently of the backend or any external services.
These are pure Python tests — no database, API keys, or embeddings needed.
"""

import pytest
from document_processor.chunker import TextChunker, TextChunk


@pytest.fixture
def chunker() -> TextChunker:
    """Standard chunker with small size for testing."""
    return TextChunker(max_chunk_size=200, overlap_size=50)


@pytest.fixture
def large_chunker() -> TextChunker:
    """Chunker with production-scale settings."""
    return TextChunker(max_chunk_size=1000, overlap_size=200)


def test_empty_text_returns_no_chunks(chunker: TextChunker) -> None:
    """Empty input must return an empty list."""
    result = chunker.chunk("", document_id="doc1", document_name="test.pdf")
    assert result == []


def test_whitespace_only_returns_no_chunks(chunker: TextChunker) -> None:
    """Whitespace-only input must return an empty list."""
    result = chunker.chunk("   \n\n   ", document_id="doc1", document_name="test.pdf")
    assert result == []


def test_short_text_produces_one_chunk(chunker: TextChunker) -> None:
    """Text shorter than max_chunk_size should be a single chunk."""
    text = "This is a short document about student mentoring activities."
    result = chunker.chunk(text, document_id="doc1", document_name="test.pdf")
    assert len(result) == 1
    assert result[0].text == text


def test_chunk_contains_document_metadata(chunker: TextChunker) -> None:
    """Each chunk must carry correct document identity metadata."""
    text = "Faculty development activities were conducted in 2025-26."
    result = chunker.chunk(
        text,
        document_id="abc-123",
        document_name="FDP_Report.pdf",
        page_number=5,
        section_heading="Faculty Activities",
    )
    assert len(result) >= 1
    chunk = result[0]
    assert chunk.document_id == "abc-123"
    assert chunk.document_name == "FDP_Report.pdf"
    assert chunk.page_number == 5
    assert chunk.section_heading == "Faculty Activities"


def test_chunk_id_format(chunker: TextChunker) -> None:
    """Chunk IDs must include document_id and page number for Pinecone delete support."""
    text = "The NBA accreditation report covers Criterion 2 outcomes."
    result = chunker.chunk(
        text,
        document_id="doc-xyz",
        document_name="NBA_Report.pdf",
        page_number=14,
    )
    assert len(result) >= 1
    assert "doc-xyz" in result[0].chunk_id
    assert "p14" in result[0].chunk_id


def test_long_text_produces_multiple_chunks(large_chunker: TextChunker) -> None:
    """Text longer than max_chunk_size must be split into multiple chunks."""
    # Build text longer than 1000 chars
    paragraph = "The institution conducts regular faculty development programs. " * 5
    long_text = "\n\n".join([paragraph] * 5)  # ~1500+ chars
    assert len(long_text) > 1000

    result = large_chunker.chunk(
        long_text,
        document_id="long-doc",
        document_name="Long_Document.pdf",
    )
    assert len(result) > 1, f"Expected multiple chunks, got {len(result)}"


def test_all_chunks_have_non_empty_text(large_chunker: TextChunker) -> None:
    """No chunk should have empty text."""
    text = "First paragraph about mentoring.\n\nSecond paragraph about FDP.\n\nThird about NBA."
    result = large_chunker.chunk(text, document_id="d1", document_name="report.pdf")
    for chunk in result:
        assert chunk.text.strip(), f"Chunk {chunk.chunk_id} has empty text"


def test_returns_list_of_text_chunk_objects(chunker: TextChunker) -> None:
    """Return type must be a list of TextChunk instances."""
    text = "NBA criterion 2 evidence from the department."
    result = chunker.chunk(text, document_id="d1", document_name="nba.pdf")
    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, TextChunk)
