"""
DocuMind AI — Auth Dependencies
FastAPI dependencies for extracting and validating the current user.

Phase 1: Dependency structure is defined. Full DB user lookup will be
completed in Phase 2 when auth endpoints are fully implemented.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt_handler import decode_access_token
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# HTTPBearer extracts the token from "Authorization: Bearer <token>" header
bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser:
    """Represents the authenticated user extracted from a JWT token."""
    def __init__(self, user_id: str, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self) -> str:
        return f"<CurrentUser id={self.user_id} role={self.role}>"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    """
    FastAPI dependency: extract and validate the JWT, return the current user.

    Phase 1 Note: This validates the JWT structure and returns claims.
    In Phase 2, this will also query the database to confirm the user exists
    and is active.

    Raises:
        401 Unauthorized if no valid token is provided.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str | None = payload.get("sub")
        email: str | None = payload.get("email", "")
        role: str | None = payload.get("role", "faculty")

        if not user_id:
            raise ValueError("Token payload missing 'sub' claim.")

        return CurrentUser(user_id=user_id, email=email or "", role=role or "faculty")

    except Exception as exc:
        logger.warning("Authentication failed: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """
    FastAPI dependency: require the current user to have admin role.

    Raises:
        403 Forbidden if the user is not an admin.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required.",
        )
    return current_user
