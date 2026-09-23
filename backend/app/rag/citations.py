"""
DocuMind AI — Citation Formatter
Converts retrieved chunks into structured source citations for the API response.

Phase 1 Status: FUNCTIONAL — extracts citation data from RetrievedChunk objects.

Integration point:
    Input:  list[RetrievedChunk]
    Output: list[SourceCitation] (Pydantic schema)
    Used by: RAGPipeline
"""

from app.core.logging_config import get_logger
from app.rag.retrieval import RetrievedChunk
from app.schemas.chat import SourceCitation

logger = get_logger(__name__)

# Maximum snippet length shown in the response
SNIPPET_MAX_CHARS = 300


class CitationFormatter:
    """
    Converts retrieved document chunks into SourceCitation objects.

    Each citation contains enough information for the frontend to:
    - Show the document name
    - Show the page/section
    - Show a relevant snippet
    - Link to the document (future)
    - Verify the AI's answer against the source
    """

    def format(self, chunks: list[RetrievedChunk]) -> list[SourceCitation]:
        """
        Convert retrieved chunks to citation objects.

        Args:
            chunks: List of RetrievedChunk from RetrievalService.

        Returns:
            List of SourceCitation (deduplicated by document + page).
        """
        citations: list[SourceCitation] = []
        seen: set[str] = set()

        for chunk in chunks:
            # Deduplicate by document + page combination
            dedup_key = f"{chunk.document_id}_{chunk.page}"
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            snippet = chunk.text[:SNIPPET_MAX_CHARS].strip()
            if len(chunk.text) > SNIPPET_MAX_CHARS:
                snippet += "..."

            citation = SourceCitation(
                document_name=chunk.document_name,
                document_id=chunk.document_id or None,
                page=chunk.page,
                section=chunk.section,
                snippet=snippet if snippet else None,
                academic_year=chunk.academic_year or None,
                department=chunk.department or None,
                score=round(chunk.score, 4),
            )
            citations.append(citation)

        logger.debug("Formatted %d citations from %d chunks.", len(citations), len(chunks))
        return citations
