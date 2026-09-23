"""
DocuMind AI — Users Endpoints
GET  /api/users
POST /api/users
PUT  /api/users/{user_id}

Phase 1 Status: ADMIN-PROTECTED STUBS
Phase 2: Full CRUD with PostgreSQL and password hashing.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import CurrentUser, require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    summary="List all users (admin only)",
    description="Returns all registered users. Requires admin role.",
)
async def list_users(
    admin: CurrentUser = Depends(require_admin),
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Phase 1 stub. Phase 2: Query users from PostgreSQL."""
    # TODO Phase 2: Query users table with pagination
    return {
        "users": [],
        "total": 0,
        "page": page,
        "page_size": page_size,
        "message": "[Phase 1] User management will be available after database integration.",
    }


@router.put(
    "/{user_id}",
    summary="Update user (admin only)",
)
async def update_user(
    user_id: str,
    admin: CurrentUser = Depends(require_admin),
) -> dict:
    """Phase 1 stub. Phase 2: Update user fields in PostgreSQL."""
    # TODO Phase 2: Validate and update user record
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"error": "NOT_IMPLEMENTED", "message": "User update available in Phase 2."},
    )
