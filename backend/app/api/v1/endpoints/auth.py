"""
DocuMind AI — Auth Endpoints
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me

Security principles:
- Passwords are hashed by UserService before storage.
- JWT tokens embed user_id + email + role claims.
- get_current_user reloads the user from PostgreSQL on every request.
- Role comes from the database — never from client-supplied fields.
- Duplicate email returns 409 Conflict (not 500).
- Invalid credentials return a generic 401 (does not reveal which field failed).
- Password hashes are never returned in any response.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.jwt_handler import create_access_token
from app.core.config import settings
from app.core.logging_config import get_logger
from app.database.base import get_db
from app.database.models import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.user_service import authenticate_user, create_user

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])


def _user_to_response(user: User) -> UserResponse:
    """Convert a User ORM instance to a UserResponse schema object."""
    return UserResponse(
        id=str(user.id),
        name=user.name,
        email=user.email,
        role=user.role.value,
        department_id=user.department_id,
        is_active=user.is_active,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Create a new user account. "
        "The password is hashed with bcrypt before storage. "
        "Duplicate email addresses return 409 Conflict."
    ),
)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Register a new user account.

    Validation:
    - Email must be unique (409 if duplicate).
    - Password >= 8 characters (validated by schema).
    - Role must be admin/faculty/staff/student (validated by schema).

    Note: In production, admin self-registration should be restricted.
    For the academic project, admin accounts can be seeded or the first
    registered user can be promoted via direct DB access.
    """
    try:
        user = await create_user(
            db,
            name=user_data.name,
            email=str(user_data.email),
            password=user_data.password,
            role=user_data.role,
            department_id=user_data.department_id,
        )
    except IntegrityError:
        # Email uniqueness constraint violated
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "EMAIL_ALREADY_EXISTS",
                "message": f"An account with email '{user_data.email}' already exists.",
            },
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "VALIDATION_ERROR", "message": str(exc)},
        )

    return _user_to_response(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate with email and password. Returns a signed JWT access token.",
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate and return a JWT access token.

    - Looks up user by email (case-insensitive).
    - Verifies bcrypt password hash.
    - Checks user is_active.
    - Returns a signed JWT with user_id, email, role claims.
    - Returns a generic 401 on any failure (does not reveal which check failed).
    """
    user = await authenticate_user(db, str(credentials.email), credentials.password)
    if user is None:
        # Generic message — do not reveal whether email or password was wrong
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_CREDENTIALS",
                "message": "Invalid email or password.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Issue JWT with key claims embedded
    token = create_access_token(
        subject=str(user.id),
        extra_claims={
            "email": user.email,
            "role": user.role.value,
            "name": user.name,
        },
    )

    logger.info("Login successful for user_id=%s role=%s", user.id, user.role)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    description="Returns the authenticated user's profile loaded from the database.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Return the current authenticated user's profile.

    The user object is loaded from PostgreSQL by get_current_user.
    This replaces the Phase 1 workaround of decoding the JWT client-side.
    """
    return _user_to_response(current_user)
