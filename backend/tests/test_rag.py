"""
DocuMind AI — Phase 2C: Embedding + Retrieval tests.

All tests use mocked external calls. No live Pinecone or OpenAI API keys
are required to run this suite.

Coverage:
    EmbeddingService:
        - embed_query: valid input, empty input, whitespace-only input
        - embed_query: multiple queries return correct dimension
        - embed_documents: valid batch, empty list, list with empty string
        - embed_documents: batching for large inputs
        - embed_query: provider error surfaced as EmbeddingError
        - embed_documents: provider error surfaced as EmbeddingError
        - no API key → EmbeddingError on first call (not at import)

    RetrievalService:
        - retrieve: valid query, correct RetrievedChunk fields
        - retrieve: empty results (no matches above threshold)
        - retrieve: metadata filter forwarded to Pinecone
        - retrieve: wrong embedding dimension → ValueError
        - retrieve: empty embedding → ValueError
        - retrieve: Pinecone error → RetrievalError
        - upsert_chunks: single batch, multiple batches
        - upsert_chunks: empty list → ValueError
        - upsert_chunks: Pinecone error → RetrievalError
        - delete_document_chunks: calls delete with correct filter
        - delete_document_chunks: empty document_id → ValueError
        - delete_document_chunks: Pinecone error → RetrievalError
        - validate_connection: success, failure

    RetrievedChunk:
        - dataclass field defaults are correct

    Integration:
        - retrieve returns chunks in score-descending order
        - metadata fields are mapped correctly to RetrievedChunk fields
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.rag.embeddings import (
    EMBEDDING_DIMENSION,
    EmbeddingError,
    EmbeddingService,
)
from app.rag.retrieval import (
    RetrievalError,
    RetrievalService,
    RetrievedChunk,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_valid_embedding(dim: int = EMBEDDING_DIMENSION) -> list[float]:
    """Return a unit vector of the correct dimension."""
    return [1.0 / dim] * dim


def make_mock_openai_response(vectors: list[list[float]]):
    """
    Construct a mock that mimics the shape of openai.types.CreateEmbeddingResponse.
    """
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(embedding=v) for v in vectors
    ]
    return mock_response


def make_mock_pinecone_match(
    chunk_id: str,
    score: float,
    meta: dict,
):
    """Construct a mock Pinecone query match object."""
    match = MagicMock()
    match.id = chunk_id
    match.score = score
    match.metadata = meta
    return match


def make_mock_pinecone_response(matches: list):
    response = MagicMock()
    response.matches = matches
    return response


# ---------------------------------------------------------------------------
# EmbeddingService tests
# ---------------------------------------------------------------------------

class TestEmbeddingService:

    # ---- embed_query -------------------------------------------------------

    async def test_embed_query_valid_returns_correct_dimension(self):
        """embed_query with valid text returns a vector of EMBEDDING_DIMENSION."""
        service = EmbeddingService()
        expected = make_valid_embedding()
        mock_response = make_mock_openai_response([expected])

        with patch.object(service, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.embeddings.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await service.embed_query("What is student mentoring?")

        assert len(result) == EMBEDDING_DIMENSION
        assert result == expected

    async def test_embed_query_strips_whitespace(self):
        """embed_query trims leading/trailing whitespace before sending to API."""
        service = EmbeddingService()
        expected = make_valid_embedding()
        mock_response = make_mock_openai_response([expected])

        with patch.object(service, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.embeddings.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await service.embed_query("  hello world  ")

        assert result == expected
        # Verify the API was called with stripped text
        call_args = mock_client.embeddings.create.call_args
        assert call_args.kwargs["input"] == "hello world"

    async def test_embed_query_empty_string_raises_value_error(self):
        """embed_query raises ValueError for empty string — no API call made."""
        service = EmbeddingService()
        with pytest.raises(ValueError, match="must not be empty"):
            await service.embed_query("")

    async def test_embed_query_whitespace_only_raises_value_error(self):
        """embed_query raises ValueError for whitespace-only string."""
        service = EmbeddingService()
        with pytest.raises(ValueError, match="must not be empty"):
            await service.embed_query("   \t\n  ")

    async def test_embed_query_api_error_raises_embedding_error(self):
        """embed_query wraps API exceptions in EmbeddingError."""
        service = EmbeddingService()
        with patch.object(service, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.embeddings.create = AsyncMock(
                side_effect=Exception("connection timeout")
            )
            mock_get_client.return_value = mock_client

            with pytest.raises(EmbeddingError, match="connection timeout"):
                await service.embed_query("some question")

    # ---- embed_documents ---------------------------------------------------

    async def test_embed_documents_valid_batch(self):
        """embed_documents returns one vector per input text."""
        service = EmbeddingService()
        texts = ["chunk one text", "chunk two text", "chunk three text"]
        expected = [make_valid_embedding() for _ in texts]
        mock_response = make_mock_openai_response(expected)

        with patch.object(service, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.embeddings.create = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await service.embed_documents(texts)

        assert len(result) == 3
        for vec in result:
            assert len(vec) == EMBEDDING_DIMENSION

    async def test_embed_documents_empty_list_raises_value_error(self):
        """embed_documents raises ValueError for empty list."""
        service = EmbeddingService()
        with pytest.raises(ValueError, match="must not be empty"):
            await service.embed_documents([])

    async def test_embed_documents_list_with_empty_string_raises_value_error(self):
        """embed_documents raises ValueError if any text in the batch is empty."""
        service = EmbeddingService()
        with pytest.raises(ValueError, match="indices"):
            await service.embed_documents(["valid text", "", "another valid"])

    async def test_embed_documents_batches_large_input(self):
        """embed_documents makes multiple API calls for large inputs."""
        from app.rag.embeddings import MAX_BATCH_SIZE

        service = EmbeddingService()
        # Create 2.5 batches worth of texts
        count = int(MAX_BATCH_SIZE * 2.5)
        texts = [f"chunk {i} text content" for i in range(count)]
        single_vec = make_valid_embedding()

        def make_batch_response(batch_texts):
            return make_mock_openai_response(
                [single_vec for _ in batch_texts]
            )

        call_count = 0

        async def mock_create(**kwargs):
            nonlocal call_count
            call_count += 1
            return make_batch_response(kwargs["input"])

        with patch.object(service, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.embeddings.create = mock_create
            mock_get_client.return_value = mock_client

            result = await service.embed_documents(texts)

        assert len(result) == count
        # Should have made 3 API calls (ceil(2.5 batches) = 3)
        assert call_count == 3

    async def test_embed_documents_api_error_raises_embedding_error(self):
        """embed_documents wraps API exceptions in EmbeddingError."""
        service = EmbeddingService()
        with patch.object(service, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.embeddings.create = AsyncMock(
                side_effect=Exception("rate limit exceeded")
            )
            mock_get_client.return_value = mock_client

            with pytest.raises(EmbeddingError, match="rate limit exceeded"):
                await service.embed_documents(["text one", "text two"])

    def test_get_client_no_api_key_raises_embedding_error(self):
        """_get_client raises EmbeddingError when OPENAI_API_KEY is not set."""
        service = EmbeddingService()
        service._client = None  # force fresh init

        with patch("app.rag.embeddings.settings") as mock_settings:
            mock_settings.openai_api_key = ""
            mock_settings.openai_embedding_model = "text-embedding-3-small"
            with pytest.raises(EmbeddingError, match="OPENAI_API_KEY"):
                service._get_client()


# ---------------------------------------------------------------------------
# RetrievedChunk tests
# ---------------------------------------------------------------------------

class TestRetrievedChunk:

    def test_default_values(self):
        """RetrievedChunk has correct defaults for optional fields."""
        chunk = RetrievedChunk(
            chunk_id="test-id",
            text="sample text",
            score=0.87,
        )
        assert chunk.document_id == ""
        assert chunk.document_name == ""
        assert chunk.department == ""
        assert chunk.academic_year == ""
        assert chunk.page is None
        assert chunk.section is None
        assert chunk.access_level == "faculty"
        assert chunk.metadata == {}

    def test_full_construction(self):
        """RetrievedChunk can be constructed with all fields."""
        meta = {"extra_field": "value"}
        chunk = RetrievedChunk(
            chunk_id="abc123_4_02",
            text="Student mentoring records show...",
            score=0.9234,
            document_id="abc123",
            document_name="Mentoring_Report_2025-26.pdf",
            department="CSE",
            academic_year="2025-26",
            page=4,
            section="Criterion 2",
            access_level="faculty",
            metadata=meta,
        )
        assert chunk.chunk_id == "abc123_4_02"
        assert chunk.score == 0.9234
        assert chunk.page == 4
        assert chunk.section == "Criterion 2"
        assert chunk.metadata == meta


# ---------------------------------------------------------------------------
# RetrievalService tests
# ---------------------------------------------------------------------------

class TestRetrievalService:

    def _make_service(self) -> RetrievalService:
        """Create a RetrievalService with a mocked Pinecone index."""
        service = RetrievalService(top_k=5, namespace="documents")
        service._index = MagicMock()  # inject mock index, skip lazy init
        return service

    # ---- retrieve ----------------------------------------------------------

    async def test_retrieve_returns_correct_chunks(self):
        """retrieve maps Pinecone matches to RetrievedChunk objects correctly."""
        service = self._make_service()

        meta = {
            "text": "Student mentoring is conducted...",
            "document_id": "doc-uuid-001",
            "document_name": "Mentoring_Report.pdf",
            "department": "CSE",
            "academic_year": "2025-26",
            "page": 4,
            "section": "Criterion 2",
            "access_level": "faculty",
        }
        matches = [make_mock_pinecone_match("doc-uuid-001_4_01", 0.92, meta)]
        service._index.query.return_value = make_mock_pinecone_response(matches)

        result = await service.retrieve(make_valid_embedding())

        assert len(result) == 1
        chunk = result[0]
        assert chunk.chunk_id == "doc-uuid-001_4_01"
        assert chunk.score == 0.92
        assert chunk.text == "Student mentoring is conducted..."
        assert chunk.document_id == "doc-uuid-001"
        assert chunk.document_name == "Mentoring_Report.pdf"
        assert chunk.department == "CSE"
        assert chunk.academic_year == "2025-26"
        assert chunk.page == 4
        assert chunk.section == "Criterion 2"
        assert chunk.access_level == "faculty"

    async def test_retrieve_empty_results(self):
        """retrieve returns empty list when Pinecone finds no matches."""
        service = self._make_service()
        service._index.query.return_value = make_mock_pinecone_response([])

        result = await service.retrieve(make_valid_embedding())
        assert result == []

    async def test_retrieve_passes_metadata_filter_to_pinecone(self):
        """retrieve forwards the metadata_filter to the Pinecone query call."""
        service = self._make_service()
        service._index.query.return_value = make_mock_pinecone_response([])

        my_filter = {"access_level": {"$in": ["public", "faculty"]}}
        await service.retrieve(make_valid_embedding(), metadata_filter=my_filter)

        call_kwargs = service._index.query.call_args.kwargs
        assert call_kwargs["filter"] == my_filter
        assert call_kwargs["include_metadata"] is True
        assert call_kwargs["namespace"] == "documents"

    async def test_retrieve_uses_custom_top_k(self):
        """retrieve respects the top_k override parameter."""
        service = self._make_service()
        service._index.query.return_value = make_mock_pinecone_response([])

        await service.retrieve(make_valid_embedding(), top_k=10)
        call_kwargs = service._index.query.call_args.kwargs
        assert call_kwargs["top_k"] == 10

    async def test_retrieve_empty_embedding_raises_value_error(self):
        """retrieve raises ValueError for empty embedding vector."""
        service = self._make_service()
        with pytest.raises(ValueError, match="must not be empty"):
            await service.retrieve([])

    async def test_retrieve_wrong_dimension_raises_value_error(self):
        """retrieve raises ValueError for embedding of wrong dimension."""
        service = self._make_service()
        wrong_dim_vec = [0.1] * 768  # wrong dimension (e.g. BERT-base)
        with pytest.raises(ValueError, match="dim"):
            await service.retrieve(wrong_dim_vec)

    async def test_retrieve_pinecone_error_raises_retrieval_error(self):
        """retrieve wraps Pinecone exceptions in RetrievalError."""
        service = self._make_service()
        service._index.query.side_effect = Exception("index not found")

        with pytest.raises(RetrievalError, match="index not found"):
            await service.retrieve(make_valid_embedding())

    async def test_retrieve_results_sorted_by_score_descending(self):
        """retrieve preserves Pinecone's score-descending order."""
        service = self._make_service()

        # Pinecone returns results pre-sorted by score descending
        matches = [
            make_mock_pinecone_match("id1", 0.95, {"text": "best", "page": 1}),
            make_mock_pinecone_match("id2", 0.82, {"text": "good", "page": 2}),
            make_mock_pinecone_match("id3", 0.71, {"text": "ok", "page": 3}),
        ]
        service._index.query.return_value = make_mock_pinecone_response(matches)

        result = await service.retrieve(make_valid_embedding())
        scores = [c.score for c in result]
        assert scores == sorted(scores, reverse=True)

    # ---- upsert_chunks -----------------------------------------------------

    async def test_upsert_chunks_single_batch(self):
        """upsert_chunks calls index.upsert and returns upserted count."""
        service = self._make_service()
        mock_upsert_response = MagicMock()
        mock_upsert_response.upserted_count = 3
        service._index.upsert.return_value = mock_upsert_response

        chunks = [
            {"id": "c1", "values": make_valid_embedding(), "metadata": {"text": "text1"}},
            {"id": "c2", "values": make_valid_embedding(), "metadata": {"text": "text2"}},
            {"id": "c3", "values": make_valid_embedding(), "metadata": {"text": "text3"}},
        ]
        result = await service.upsert_chunks(chunks)
        assert result == 3
        service._index.upsert.assert_called_once()

    async def test_upsert_chunks_multiple_batches(self):
        """upsert_chunks splits into multiple batches for large inputs."""
        from app.rag.retrieval import UPSERT_BATCH_SIZE

        service = self._make_service()
        mock_upsert_response = MagicMock()
        mock_upsert_response.upserted_count = UPSERT_BATCH_SIZE
        service._index.upsert.return_value = mock_upsert_response

        count = UPSERT_BATCH_SIZE + 5  # 105 chunks → 2 batches
        chunks = [
            {"id": f"c{i}", "values": make_valid_embedding(), "metadata": {}}
            for i in range(count)
        ]
        result = await service.upsert_chunks(chunks)
        assert service._index.upsert.call_count == 2

    async def test_upsert_chunks_empty_list_raises_value_error(self):
        """upsert_chunks raises ValueError for empty list."""
        service = self._make_service()
        with pytest.raises(ValueError, match="must not be empty"):
            await service.upsert_chunks([])

    async def test_upsert_chunks_pinecone_error_raises_retrieval_error(self):
        """upsert_chunks wraps Pinecone exceptions in RetrievalError."""
        service = self._make_service()
        service._index.upsert.side_effect = Exception("quota exceeded")

        with pytest.raises(RetrievalError, match="quota exceeded"):
            await service.upsert_chunks([
                {"id": "c1", "values": make_valid_embedding(), "metadata": {}}
            ])

    # ---- delete_document_chunks --------------------------------------------

    async def test_delete_document_chunks_calls_correct_filter(self):
        """delete_document_chunks calls index.delete with the correct filter."""
        service = self._make_service()
        service._index.delete.return_value = None

        result = await service.delete_document_chunks("doc-uuid-001")
        assert result == 0
        service._index.delete.assert_called_once_with(
            filter={"document_id": {"$eq": "doc-uuid-001"}},
            namespace="documents",
        )

    async def test_delete_document_chunks_empty_id_raises_value_error(self):
        """delete_document_chunks raises ValueError for empty document_id."""
        service = self._make_service()
        with pytest.raises(ValueError, match="must not be empty"):
            await service.delete_document_chunks("")

    async def test_delete_document_chunks_pinecone_error_raises_retrieval_error(self):
        """delete_document_chunks wraps Pinecone exceptions in RetrievalError."""
        service = self._make_service()
        service._index.delete.side_effect = Exception("index unavailable")

        with pytest.raises(RetrievalError, match="index unavailable"):
            await service.delete_document_chunks("doc-uuid-001")

    # ---- validate_connection -----------------------------------------------

    async def test_validate_connection_returns_stats(self):
        """validate_connection returns index statistics dict."""
        service = self._make_service()
        mock_stats = MagicMock()
        mock_stats.total_vector_count = 1000
        mock_stats.namespaces = {}
        mock_stats.dimension = EMBEDDING_DIMENSION
        mock_stats.index_fullness = 0.02
        service._index.describe_index_stats.return_value = mock_stats

        result = await service.validate_connection()
        assert result["total_vector_count"] == 1000
        assert result["dimension"] == EMBEDDING_DIMENSION

    async def test_validate_connection_error_raises_retrieval_error(self):
        """validate_connection wraps errors in RetrievalError."""
        service = self._make_service()
        service._index.describe_index_stats.side_effect = Exception("auth failed")

        with pytest.raises(RetrievalError, match="auth failed"):
            await service.validate_connection()

    def test_get_index_no_api_key_raises_retrieval_error(self):
        """_get_index raises RetrievalError when PINECONE_API_KEY is not set."""
        service = RetrievalService()
        service._index = None  # ensure lazy init runs

        with patch("app.rag.retrieval.settings") as mock_settings:
            mock_settings.pinecone_api_key = ""
            mock_settings.pinecone_index_name = "documind-knowledge"
            with pytest.raises(RetrievalError, match="PINECONE_API_KEY"):
                service._get_index()
