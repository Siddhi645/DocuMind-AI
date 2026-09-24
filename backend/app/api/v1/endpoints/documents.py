"""
DocuMind AI — Documents Endpoints
GET /api/documents
GET /api/documents/{document_id}

Phase 1 Status: STRUCTURED STUBS
Phase 2: Query PostgreSQL documents table with permission filtering.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.database.models import User

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get(
    "",
    summary="List documents",
    description="Returns a paginated list of documents accessible to the authenticated user.",
)
async def list_documents(
    current_user: User = Depends(get_current_user),
    page: int = 1,
    page_size: int = 20,
    department: str | None = None,
    academic_year: str | None = None,
    status: str | None = None,
) -> dict:
    """
    Phase 1 stub: Returns empty list.

    Phase 2 implementation:
    1. Build query filtered by user's access_level and optional params.
    2. Paginate results.
    3. Return DocumentListResponse.
    """
    # TODO Phase 2: Query documents from PostgreSQL with access control
    return {
        "documents": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "message": "[Phase 1] Document listing will be available after database integration.",
    }


@router.get(
    "/{document_id}",
    summary="Get document details",
    description="Returns metadata for a specific document.",
)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Phase 1 stub.
    Phase 2: Fetch from DB and verify access_level allows current_user's role.
    """
    # TODO Phase 2: Fetch document and check access_level against user role
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "NOT_IMPLEMENTED",
            "message": "Document detail retrieval will be available in Phase 2.",
        },
    )
