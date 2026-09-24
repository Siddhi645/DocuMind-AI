"""
DocuMind AI — Auth schemas
Request/response models for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    """Credentials submitted on the login form."""
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Password must not be empty.")
        return v


class RegisterRequest(BaseModel):
    """Data required to create a new user account."""
    name: str
    email: EmailStr
    password: str
    role: str = "faculty"
    department_id: int | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name must not be empty.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v

    @field_validator("role")
    @classmethod
    def role_valid(cls, v: str) -> str:
        valid = {"admin", "faculty", "staff", "student"}
        if v not in valid:
            raise ValueError(f"Role must be one of: {sorted(valid)}")
        return v


class TokenResponse(BaseModel):
    """JWT token returned after successful login."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """
    Public user information returned by the API.
    Never includes password_hash.
    """
    id: str          # serialised from uuid.UUID
    name: str
    email: str
    role: str
    department_id: int | None = None
    is_active: bool = True

    model_config = {"from_attributes": True}
