"""
DocuMind AI — Auth Dependencies
FastAPI dependencies for extracting and validating the current user.

Phase 2: get_current_user now queries PostgreSQL to:
  - Confirm the user still exists
  - Confirm is_active = True
  - Return the full User ORM object (not just JWT claims)

The role returned to callers comes from the DATABASE, not from the JWT payload.
This prevents a revoked/changed role from remaining valid until token expiry.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt_handler import decode_access_token
from app.core.logging_config import get_logger
from app.database.base import get_db
from app.database.models import User

logger = get_logger(__name__)

# HTTPBearer extracts the token from "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency: validate the JWT and load the authenticated user from DB.

    Steps:
    1. Extract Bearer token from Authorization header.
    2. Decode and verify JWT signature + expiry.
    3. Extract user_id ('sub' claim) from payload.
    4. Load User from PostgreSQL by ID.
    5. Verify user exists and is_active = True.

    Returns:
        The authenticated User ORM object.

    Raises:
        401 Unauthorized: No token, invalid token, expired token.
        401 Unauthorized: User not found in database.
        401 Unauthorized: User account is inactive/disabled.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Decode JWT — raises JWTError on invalid/expired
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise ValueError("Token payload missing 'sub' claim.")
    except Exception as exc:
        logger.warning("JWT decode failed: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Load user from database
    from app.services.user_service import get_user_by_id  # local import avoids circular
    user = await get_user_by_id(db, user_id)

    if user is None:
        logger.warning("Token references non-existent user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning("Token references inactive user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your account has been deactivated. Please contact an administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency: require the current user to have admin role.

    Raises:
        403 Forbidden if the user's role (from database) is not 'admin'.
    """
    from app.database.models import UserRole
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_user
