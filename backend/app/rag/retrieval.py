"""
DocuMind AI — Retrieval Service
Semantic similarity search via Pinecone vector database.

Phase 2C: Real implementation replacing the Phase 1 stub.

Provider:        Pinecone
SDK version:     pinecone==6.0.2
Index metric:    cosine
Embedding dim:   1536 (must match EmbeddingService.EMBEDDING_DIMENSION)

Pinecone index configuration required (must be done once manually or via
admin tooling — NOT auto-created on every startup):
    dimension = 1536
    metric    = cosine

Chunk metadata structure (stored in Pinecone with every vector):
    {
        "document_id":   str   — UUID of the source document (PostgreSQL FK)
        "document_name": str   — human-readable filename
        "chunk_id":      str   — unique chunk identifier (e.g. "doc-uuid_page_idx")
        "page":          int   — source page number (0 if unknown)
        "section":       str   — heading/section if available
        "department":    str   — department tag for metadata filtering
        "academic_year": str   — e.g. "2025-26"
        "document_type": str   — e.g. "report", "notice", "policy"
        "access_level":  str   — "public" | "student" | "faculty" | "admin"
        "text":          str   — chunk text (stored in metadata for retrieval)
    }

Security note:
    Metadata filters are constructed by the backend from the authenticated
    user's role — NEVER from client request bodies.

Design principles:
    - Pinecone Index is constructed lazily on first use to avoid import-time
      failures when credentials are not configured (e.g. in unit tests).
    - Tests mock _get_index() to avoid live API calls.
    - All exceptions are caught and re-raised as RetrievalError.
    - Namespace support: vectors are stored in a namespace (default: "documents").
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.config import settings
from app.core.logging_config import get_logger
from app.rag.embeddings import EMBEDDING_DIMENSION

logger = get_logger(__name__)

# Namespace used for all document chunks in Pinecone.
# A single Pinecone index can hold multiple namespaces (e.g. "documents", "test").
DEFAULT_NAMESPACE = "documents"

# Maximum vectors per upsert batch (Pinecone hard limit is 100 vectors/batch)
UPSERT_BATCH_SIZE = 100


class RetrievalError(Exception):
    """Raised when the Pinecone retrieval service encounters an error."""


# ---------------------------------------------------------------------------
# RetrievedChunk — core data model flowing through the RAG pipeline
# ---------------------------------------------------------------------------

@dataclass
class RetrievedChunk:
    """
    A document chunk returned by Pinecone similarity search.

    This is the primary data structure passed between retrieval → context
    building → citation formatting in the RAG pipeline.

    Fields:
        chunk_id:      Unique vector ID in Pinecone (e.g. "abc123_4_02")
        text:          The actual chunk text (retrieved from Pinecone metadata)
        score:         Cosine similarity score [0.0, 1.0]
        document_id:   UUID of the source document in PostgreSQL
        document_name: Human-readable filename
        department:    Department tag for display and filtering
        academic_year: e.g. "2025-26"
        page:          Source page number (None if unknown)
        section:       Heading/section if available
        access_level:  "public" | "student" | "faculty" | "admin"
        metadata:      Full raw metadata dict from Pinecone for extensibility
    """
    chunk_id: str
    text: str
    score: float
    document_id: str = ""
    document_name: str = ""
    department: str = ""
    academic_year: str = ""
    page: int | None = None
    section: str | None = None
    access_level: str = "faculty"
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# RetrievalService
# ---------------------------------------------------------------------------

class RetrievalService:
    """
    Retrieves semantically relevant document chunks from Pinecone.

    Supports:
    - Query/search (retrieve)
    - Upsert vectors (upsert_chunks)
    - Delete vectors (delete_document_chunks)
    - Index validation (validate_connection)

    Configuration (from .env):
        PINECONE_API_KEY        — required for live calls
        PINECONE_INDEX_NAME     — target index name (default: documind-knowledge)
        PINECONE_ENVIRONMENT    — deprecated in SDK v6; kept for compatibility
    """

    def __init__(
        self,
        top_k: int = 5,
        namespace: str = DEFAULT_NAMESPACE,
    ):
        self.top_k = top_k
        self.namespace = namespace
        self._index = None       # lazy-initialised on first call
        logger.info(
            "RetrievalService initialised (top_k=%d, namespace=%r, index=%r)",
            top_k,
            namespace,
            settings.pinecone_index_name,
        )

    def _get_index(self):
        """
        Return the Pinecone Index object, constructing it on first call.

        Raises:
            RetrievalError: If PINECONE_API_KEY is not configured, or if the
                            pinecone package is not installed.
        """
        if self._index is not None:
            return self._index

        try:
            from pinecone import Pinecone  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RetrievalError(
                "pinecone package is not installed. "
                "Run: pip install pinecone==6.0.2"
            ) from exc

        if not settings.pinecone_api_key:
            raise RetrievalError(
                "PINECONE_API_KEY is not configured. "
                "Set it in .env before using the retrieval service."
            )

        pc = Pinecone(api_key=settings.pinecone_api_key)
        self._index = pc.Index(settings.pinecone_index_name)
        logger.info(
            "Pinecone index connected: %s", settings.pinecone_index_name
        )
        return self._index

    async def validate_connection(self) -> dict[str, Any]:
        """
        Validate connectivity to the Pinecone index and return index stats.

        Returns:
            Dict with index statistics (total_vector_count, namespaces, etc.)

        Raises:
            RetrievalError: If the connection or credentials are invalid.
        """
        try:
            index = self._get_index()
            stats = index.describe_index_stats()
            # Convert to plain dict for logging/returning
            stats_dict = {
                "total_vector_count": stats.total_vector_count,
                "namespaces": {
                    k: {"vector_count": v.vector_count}
                    for k, v in (stats.namespaces or {}).items()
                },
                "dimension": stats.dimension,
                "index_fullness": stats.index_fullness,
            }
            logger.info("Pinecone index stats: %s", stats_dict)
            return stats_dict
        except RetrievalError:
            raise
        except Exception as exc:
            logger.error("validate_connection failed: %s", str(exc))
            raise RetrievalError(f"Pinecone connection error: {exc}") from exc

    async def retrieve(
        self,
        query_embedding: list[float],
        metadata_filter: dict[str, Any] | None = None,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        """
        Query Pinecone for the most semantically similar document chunks.

        The query vector (from EmbeddingService.embed_query) is compared
        against all indexed document chunk vectors using cosine similarity.

        Args:
            query_embedding: 1536-dim float vector from EmbeddingService.
            metadata_filter: Pinecone filter dict, constructed by the backend
                             from the user's authenticated role/permissions.
                             Example: {"access_level": {"$in": ["public", "faculty"]}}
            top_k:           Number of chunks to retrieve. Defaults to self.top_k.

        Returns:
            List of RetrievedChunk objects sorted by score descending.
            Returns empty list if no relevant chunks are found.

        Raises:
            ValueError: If query_embedding is empty or has wrong dimension.
            RetrievalError: If the Pinecone query fails.
        """
        if not query_embedding:
            raise ValueError("retrieve: query_embedding must not be empty.")

        if len(query_embedding) != EMBEDDING_DIMENSION:
            raise ValueError(
                f"retrieve: expected embedding of dim {EMBEDDING_DIMENSION}, "
                f"got {len(query_embedding)}."
            )

        k = top_k or self.top_k

        logger.debug(
            "retrieve: top_k=%d, namespace=%r, filter=%s",
            k,
            self.namespace,
            metadata_filter,
        )

        try:
            index = self._get_index()
            response = index.query(
                vector=query_embedding,
                top_k=k,
                filter=metadata_filter,
                include_metadata=True,
                namespace=self.namespace,
            )

            chunks = []
            for match in response.matches:
                meta = match.metadata or {}
                chunk = RetrievedChunk(
                    chunk_id=match.id,
                    text=meta.get("text", ""),
                    score=float(match.score or 0.0),
                    document_id=meta.get("document_id", ""),
                    document_name=meta.get("document_name", ""),
                    department=meta.get("department", ""),
                    academic_year=meta.get("academic_year", ""),
                    page=int(meta["page"]) if meta.get("page") is not None else None,
                    section=meta.get("section"),
                    access_level=meta.get("access_level", "faculty"),
                    metadata=meta,
                )
                chunks.append(chunk)

            logger.info(
                "retrieve: returned %d chunks (top score=%.4f)",
                len(chunks),
                chunks[0].score if chunks else 0.0,
            )
            return chunks

        except RetrievalError:
            raise
        except Exception as exc:
            logger.error("retrieve failed: %s", str(exc), exc_info=True)
            raise RetrievalError(f"Pinecone query error: {exc}") from exc

    async def upsert_chunks(self, chunks: list[dict[str, Any]]) -> int:
        """
        Upsert document chunk vectors into Pinecone.

        Called by the ingestion pipeline after embedding document chunks.

        Each chunk dict must have:
            {
                "id":       str          — unique vector ID
                "values":   list[float]  — 1536-dim embedding vector
                "metadata": dict         — chunk metadata (see module docstring)
            }

        Args:
            chunks: List of vector dicts to upsert.

        Returns:
            Total number of vectors successfully upserted.

        Raises:
            ValueError: If chunks list is empty.
            RetrievalError: If the Pinecone upsert fails.
        """
        if not chunks:
            raise ValueError("upsert_chunks: chunks list must not be empty.")

        total_upserted = 0

        try:
            index = self._get_index()

            # Batch upsert to stay within Pinecone's per-request limit
            for batch_start in range(0, len(chunks), UPSERT_BATCH_SIZE):
                batch = chunks[batch_start : batch_start + UPSERT_BATCH_SIZE]
                response = index.upsert(
                    vectors=batch,
                    namespace=self.namespace,
                )
                total_upserted += response.upserted_count or len(batch)
                logger.debug(
                    "upsert_chunks: batch [%d:%d] upserted %d vectors",
                    batch_start,
                    batch_start + len(batch),
                    response.upserted_count or len(batch),
                )

            logger.info("upsert_chunks: total upserted = %d", total_upserted)
            return total_upserted

        except RetrievalError:
            raise
        except Exception as exc:
            logger.error("upsert_chunks failed: %s", str(exc), exc_info=True)
            raise RetrievalError(f"Pinecone upsert error: {exc}") from exc

    async def delete_document_chunks(self, document_id: str) -> int:
        """
        Delete all Pinecone vectors belonging to a specific document.

        Used when a document is updated or deleted from the knowledge base.
        Pinecone's metadata filter delete requires server-side filtering support
        (available on pods and serverless indexes).

        Args:
            document_id: UUID of the document whose chunks should be removed.

        Returns:
            0 — Pinecone delete by filter does not return a count.

        Raises:
            ValueError: If document_id is empty.
            RetrievalError: If the Pinecone delete fails.
        """
        if not document_id or not document_id.strip():
            raise ValueError("delete_document_chunks: document_id must not be empty.")

        logger.debug(
            "delete_document_chunks: document_id=%s, namespace=%r",
            document_id,
            self.namespace,
        )

        try:
            index = self._get_index()
            index.delete(
                filter={"document_id": {"$eq": document_id}},
                namespace=self.namespace,
            )
            logger.info(
                "delete_document_chunks: deleted chunks for document_id=%s", document_id
            )
            return 0  # Pinecone filter-delete does not return a count

        except RetrievalError:
            raise
        except Exception as exc:
            logger.error(
                "delete_document_chunks failed: %s", str(exc), exc_info=True
            )
            raise RetrievalError(f"Pinecone delete error: {exc}") from exc


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_retrieval_service: RetrievalService | None = None


def get_retrieval_service() -> RetrievalService:
    """
    Return the configured RetrievalService singleton.

    The singleton is created on first call. The Pinecone Index connection
    is established lazily on the first retrieve/upsert/delete call.
    Tests should inject a mock via RAGPipeline(retrieval_service=...).
    """
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
