"""
DocuMind AI — Auth Endpoints
POST /api/auth/login
POST /api/auth/register

Phase 1 Status: STRUCTURED STUBS
- Endpoint structure is defined.
- Schemas are validated.
- Responses are clearly marked as Phase 1 stubs.
Phase 2: Wire to database, password hashing, and JWT token creation.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate with email and password. Returns a JWT access token.",
)
async def login(credentials: LoginRequest) -> TokenResponse:
    """
    Phase 1 stub: Validates schema but does not check a real database.

    Phase 2 implementation:
    1. Look up user by email in PostgreSQL.
    2. Verify password hash using passlib.
    3. Check user.is_active.
    4. Create JWT token with user ID, email, and role claims.
    5. Return TokenResponse.
    """
    # TODO Phase 2: Replace stub with real authentication
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "NOT_IMPLEMENTED",
            "message": "Authentication will be implemented in Phase 2.",
            "received_email": credentials.email,
        },
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. Admin accounts must be created by an existing admin.",
)
async def register(user_data: RegisterRequest) -> UserResponse:
    """
    Phase 1 stub: Validates schema but does not write to the database.

    Phase 2 implementation:
    1. Check if email already exists.
    2. Hash the password using passlib bcrypt.
    3. Create user record in PostgreSQL.
    4. Return the created user (without password).
    """
    # TODO Phase 2: Replace stub with real user creation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error": "NOT_IMPLEMENTED",
            "message": "User registration will be implemented in Phase 2.",
        },
    )
