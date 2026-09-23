"""
DocuMind AI — ORM Models
Initial database schema matching the context.md design.
All models inherit from Base defined in database/base.py.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


# ---- Enumerations ----

class UserRole(str, PyEnum):
    ADMIN = "admin"
    FACULTY = "faculty"
    STAFF = "staff"
    STUDENT = "student"


class DocumentStatus(str, PyEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    ARCHIVED = "archived"


class AccessLevel(str, PyEnum):
    PUBLIC = "public"
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"


class MessageRole(str, PyEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ---- Models ----

class Department(Base):
    """
    Academic department or administrative unit.
    Documents and users are associated with a department.
    """
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    code: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)

    # Relationships
    users: Mapped[list["User"]] = relationship("User", back_populates="department")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="department")

    def __repr__(self) -> str:
        return f"<Department id={self.id} name={self.name!r}>"


class User(Base):
    """
    Authenticated system user (faculty, staff, admin, student).
    Role determines what documents they can access.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), nullable=False, default=UserRole.FACULTY
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    department: Mapped["Department | None"] = relationship("Department", back_populates="users")
    chat_sessions: Mapped[list["ChatSession"]] = relationship("ChatSession", back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"


class Document(Base):
    """
    Institutional document record.
    Tracks metadata, indexing status, and Google Drive identity.
    The actual content lives in Pinecone (as vector chunks).
    """
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    # Google Drive file ID — used for incremental indexing
    drive_file_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    department_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=True
    )
    academic_year: Mapped[str | None] = mapped_column(String(20), nullable=True)
    document_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    access_level: Mapped[AccessLevel] = mapped_column(
        Enum(AccessLevel), nullable=False, default=AccessLevel.FACULTY
    )
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), nullable=False, default=DocumentStatus.PENDING
    )
    # Error message if indexing failed
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Number of chunks indexed in Pinecone
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    department: Mapped["Department | None"] = relationship("Department", back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document id={self.id} name={self.name!r} status={self.status}>"


class ChatSession(Base):
    """
    A conversation session between a user and the AI assistant.
    Groups related messages together.
    """
    __tablename__ = "chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="session", order_by="Message.created_at"
    )

    def __repr__(self) -> str:
        return f"<ChatSession id={self.id} user_id={self.user_id}>"


class Message(Base):
    """
    Individual message within a chat session.
    Stores both user questions and AI answers (with sources).
    """
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id"), nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # JSON-serialized list of source citations for assistant messages
    sources_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message id={self.id} role={self.role} session_id={self.session_id}>"
