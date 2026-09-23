"""
DocuMind AI — Health endpoint tests.
Tests that /api/health works without a database or any API keys.
All async tests are handled automatically by pytest-asyncio (asyncio_mode=auto).
"""

from httpx import AsyncClient


async def test_health_returns_200(client: AsyncClient) -> None:
    """Health endpoint must return HTTP 200."""
    response = await client.get("/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


async def test_health_response_schema(client: AsyncClient) -> None:
    """Health endpoint must return the correct JSON schema."""
    response = await client.get("/api/health")
    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "documind-backend"
    assert "version" in data
    assert "environment" in data


async def test_health_no_auth_required(client: AsyncClient) -> None:
    """Health endpoint must be accessible without an Authorization header."""
    response = await client.get("/api/health")
    # Must not return 401 or 403
    assert response.status_code not in (401, 403), (
        f"Health endpoint should not require auth, got {response.status_code}"
    )


async def test_chat_requires_auth(client: AsyncClient) -> None:
    """
    POST /api/chat must require authentication.
    An unauthenticated request should return 401 or 403.
    """
    response = await client.post(
        "/api/chat",
        json={"question": "What evidence exists for student mentoring?"},
    )
    assert response.status_code in (401, 403), (
        f"Expected 401/403 for unauthenticated chat, got {response.status_code}"
    )


async def test_unknown_route_returns_404(client: AsyncClient) -> None:
    """Unknown routes must return 404."""
    response = await client.get("/api/nonexistent-endpoint-xyz")
    assert response.status_code == 404
