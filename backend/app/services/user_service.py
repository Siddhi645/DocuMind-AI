"""
DocuMind AI — User Service
Database operations for user management.

Handles:
- Creating users with bcrypt-hashed passwords
- Looking up users by email or ID
- Verifying credentials (email + password) for login

Security principles:
- Passwords are hashed with bcrypt (passlib) before storage.
- Plaintext passwords never reach the database.
- Password hashes are never returned to API callers.
- The user's role comes from the database, not from client input.
"""

import uuid

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger
from app.database.models import User, UserRole

logger = get_logger(__name__)

# bcrypt context — schemes list allows future algorithm migration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plaintext: str) -> str:
    """Return the bcrypt hash of a plaintext password."""
    return pwd_context.hash(plaintext)


def verify_password(plaintext: str, hashed: str) -> bool:
    """Return True if plaintext matches the stored bcrypt hash."""
    return pwd_context.verify(plaintext, hashed)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Fetch a user record by email address. Returns None if not found."""
    result = await db.execute(select(User).where(User.email == email.lower()))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Fetch a user record by UUID string. Returns None if not found."""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        return None
    result = await db.execute(select(User).where(User.id == uid))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    name: str,
    email: str,
    password: str,
    role: str = "faculty",
    department_id: int | None = None,
) -> User:
    """
    Create and persist a new user.

    Args:
        db: Active async database session.
        name: User's display name.
        email: Email address (stored lowercase, must be unique).
        password: Plaintext password — hashed before storage.
        role: User role string. Defaults to 'faculty'.
               Validated against UserRole enum.
        department_id: Optional FK to departments table.

    Returns:
        The newly created User ORM instance (with id populated).

    Raises:
        ValueError: If the role string is not a valid UserRole.
        sqlalchemy.exc.IntegrityError: If email already exists.
    """
    # Validate role against the enum
    try:
        user_role = UserRole(role)
    except ValueError:
        valid = [r.value for r in UserRole]
        raise ValueError(f"Invalid role '{role}'. Must be one of: {valid}")

    user = User(
        name=name,
        email=email.lower(),
        password_hash=hash_password(password),
        role=user_role,
        department_id=department_id,
        is_active=True,
    )
    db.add(user)
    await db.flush()   # assign id without committing — commit happens in get_db()
    await db.refresh(user)
    logger.info("Created user id=%s email=%s role=%s", user.id, user.email, user.role)
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """
    Verify email + password and return the User if valid.

    Returns None if:
    - No user exists with this email
    - The password does not match
    - The user account is inactive

    Never reveals which specific check failed (timing-safe).
    """
    user = await get_user_by_email(db, email)
    if user is None:
        # Run the hash anyway to prevent timing attacks that reveal email existence
        pwd_context.dummy_verify()
        logger.warning("Login attempt for unknown email: %s", email)
        return None

    if not verify_password(password, user.password_hash):
        logger.warning("Wrong password for user: %s", email)
        return None

    if not user.is_active:
        logger.warning("Login attempt for inactive user: %s", email)
        return None

    return user
