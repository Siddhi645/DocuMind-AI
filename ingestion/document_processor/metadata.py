"""
DocuMind AI — Metadata Builder
Constructs Pinecone-compatible metadata for each document chunk.

Phase 1 Status: FUNCTIONAL — metadata structure is production-ready.
Phase 2: Extend with Google Drive metadata (modified_at, drive_url, etc.)

Integration point:
    Input:  document info + chunk info
    Output: dict compatible with Pinecone metadata schema
    Used by: ingestion pipeline (before upsert to Pinecone)

The metadata dict matches the schema defined in context.md Section 13.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger("documind.ingestion.metadata")

# Pinecone metadata string values have a max length limit
MAX_METADATA_STRING_LENGTH = 500


@dataclass
class DocumentInfo:
    """Information about the source document (from PostgreSQL or Drive)."""
    document_id: str
    document_name: str
    department: str = ""
    academic_year: str = ""
    document_type: str = ""
    access_level: str = "faculty"
    drive_file_id: str = ""


class MetadataBuilder:
    """
    Builds Pinecone vector metadata for each document chunk.

    The metadata stored with each Pinecone vector enables:
    - Permission filtering (access_level, department)
    - Source citation (document_name, page, section)
    - Incremental indexing (document_id for delete/replace)
    - Search filters (academic_year, document_type)
    """

    def build(
        self,
        doc_info: DocumentInfo,
        chunk_id: str,
        chunk_text: str,
        page_number: int | None = None,
        section_heading: str | None = None,
        chunk_index: int = 0,
    ) -> dict:
        """
        Build a Pinecone metadata dictionary for a single chunk.

        Args:
            doc_info: Source document information.
            chunk_id: Unique chunk identifier (e.g., "abc123_p14_c003").
            chunk_text: The chunk's text content (stored for snippet display).
            page_number: Page number in the original document.
            section_heading: Section heading if detected.
            chunk_index: Zero-based index of this chunk within the document.

        Returns:
            Dictionary compatible with Pinecone metadata storage.
        """
        # Pinecone metadata values must be str, int, float, bool, or list of these
        metadata = {
            # Document identity (used for incremental delete/replace)
            "document_id": str(doc_info.document_id),
            "document_name": self._truncate(doc_info.document_name),
            "drive_file_id": self._truncate(doc_info.drive_file_id),

            # Access control (used for permission filtering in retrieval)
            "access_level": doc_info.access_level or "faculty",
            "department": self._truncate(doc_info.department),

            # Institutional metadata (used for search filters)
            "academic_year": self._truncate(doc_info.academic_year),
            "document_type": self._truncate(doc_info.document_type),

            # Chunk location (used for source citation)
            "chunk_id": chunk_id,
            "chunk_index": chunk_index,
            "page": page_number if page_number is not None else -1,
            "section": self._truncate(section_heading or ""),

            # Text snippet (used for citation display in UI)
            # Truncated to avoid exceeding Pinecone metadata size limits
            "text_snippet": self._truncate(chunk_text, max_length=300),
        }

        logger.debug("Built metadata for chunk_id=%s page=%s", chunk_id, page_number)
        return metadata

    def _truncate(self, value: str, max_length: int = MAX_METADATA_STRING_LENGTH) -> str:
        """Truncate a string to fit Pinecone metadata limits."""
        if not value:
            return ""
        return value[:max_length]
