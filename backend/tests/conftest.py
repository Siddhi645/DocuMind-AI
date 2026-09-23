"""
DocuMind AI — pytest configuration and shared fixtures.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client() -> AsyncClient:
    """
    Async test client for the FastAPI app.
    Does NOT hit a real database or any external service.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac
