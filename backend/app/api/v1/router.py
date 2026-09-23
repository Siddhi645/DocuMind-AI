"""
DocuMind AI — API v1 Router
Aggregates all endpoint routers under the /api prefix.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import admin, auth, chat, documents, health, users

api_router = APIRouter()

# Health check — no auth, always available
api_router.include_router(health.router)

# Authentication
api_router.include_router(auth.router)

# Core application endpoints (auth-protected)
api_router.include_router(chat.router)
api_router.include_router(documents.router)
api_router.include_router(users.router)
api_router.include_router(admin.router)
