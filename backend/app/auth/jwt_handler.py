"""
DocuMind AI — JWT Handler
Utility functions for creating and verifying JWT access tokens.

Phase 1: Structure is in place. Token creation/verification is functional.
Full user lookup from DB will be wired in Phase 2 (auth implementation phase).
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Args:
        subject: The user's ID (UUID string).
        extra_claims: Additional claims to embed (e.g., role, email).

    Returns:
        Encoded JWT string.
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expire,
    }
    if extra_claims:
        payload.update(extra_claims)

    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    logger.debug("Access token created for subject: %s", subject)
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT access token.

    Args:
        token: The JWT string to verify.

    Returns:
        The decoded payload dictionary.

    Raises:
        JWTError: If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as exc:
        logger.warning("JWT decode failed: %s", str(exc))
        raise


def get_subject_from_token(token: str) -> str | None:
    """
    Extract the subject (user ID) from a token without raising.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = decode_access_token(token)
        return payload.get("sub")
    except JWTError:
        return None
