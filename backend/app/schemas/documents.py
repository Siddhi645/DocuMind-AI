"""
DocuMind AI — Document schemas
Request/response models for document metadata endpoints.
"""

from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """Document metadata returned by GET /api/documents."""
    id: str
    name: str
    department: str | None = None
    academic_year: str | None = None
    document_type: str | None = None
    access_level: str
    status: str
    chunk_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Paginated list of documents."""
    documents: list[DocumentResponse]
    total: int
    page: int = 1
    page_size: int = 20
