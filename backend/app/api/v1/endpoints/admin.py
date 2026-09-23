"""
DocuMind AI — Admin Endpoints
POST /api/admin/sync
GET  /api/admin/indexing-status

Phase 1 Status: ADMIN-PROTECTED STUBS
Phase 2: Connect to n8n webhook trigger and indexing status from PostgreSQL.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import CurrentUser, require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post(
    "/sync",
    summary="Trigger document synchronization (admin only)",
    description=(
        "Triggers n8n to scan Google Drive for new/updated documents and index them. "
        "Admin role required."
    ),
)
async def trigger_sync(
    admin: CurrentUser = Depends(require_admin),
) -> dict:
    """
    Phase 1 stub.

    Phase 2 implementation:
    1. POST to n8n webhook URL with auth header.
    2. n8n scans Google Drive, downloads new/updated files.
    3. Sends files to the ingestion pipeline.
    4. Returns job ID for status tracking.
    """
    # TODO Phase 2: POST to settings.n8n_webhook_url to trigger sync workflow
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "NOT_IMPLEMENTED",
            "message": "Google Drive sync will be available after n8n integration.",
        },
    )


@router.get(
    "/indexing-status",
    summary="Get document indexing status (admin only)",
    description="Returns the indexing status of all documents in the system.",
)
async def get_indexing_status(
    admin: CurrentUser = Depends(require_admin),
) -> dict:
    """
    Phase 1 stub.
    Phase 2: Query documents table for status counts (indexed, pending, failed).
    """
    # TODO Phase 2: Aggregate document status from PostgreSQL
    return {
        "total": 0,
        "indexed": 0,
        "pending": 0,
        "processing": 0,
        "failed": 0,
        "message": "[Phase 1] Indexing status will be available after database integration.",
    }
