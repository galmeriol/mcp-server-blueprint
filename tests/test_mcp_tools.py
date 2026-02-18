"""Tests for MCP tool functions."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
import respx

from mcp_server_blueprint.config import Configuration
from mcp_server_blueprint.infrastructure.http_client import HttpClient
from mcp_server_blueprint.server import AppContext
from mcp_server_blueprint.tools import (
    create_post,
    delete_post,
    get_post,
    get_posts,
    update_post,
)

BASE_URL = "https://jsonplaceholder.typicode.com"


def make_ctx(http_client: HttpClient) -> MagicMock:
    """Build a minimal mock MCP Context with AppContext wired in."""
    config = Configuration(base_url=BASE_URL)
    ctx = MagicMock()
    ctx.request_context.lifespan_context = AppContext(http_client=http_client, config=config)
    ctx.request_context.request = None  # no token passthrough in default tests
    ctx.info = AsyncMock()
    ctx.error = AsyncMock()
    return ctx


@pytest.fixture
def client():
    return HttpClient(base_url=BASE_URL, timeout=5)


# --- get_posts ---


async def test_get_posts_invalid_limit(client):
    ctx = make_ctx(client)
    result = await get_posts(ctx, limit=0)
    assert result.startswith("Error")


@respx.mock
async def test_get_posts_success(client):
    respx.get(f"{BASE_URL}/posts").mock(
        return_value=httpx.Response(200, json=[{"id": 1}, {"id": 2}])
    )
    ctx = make_ctx(client)
    result = await get_posts(ctx, limit=2)
    assert '"id": 1' in result


@respx.mock
async def test_get_posts_api_error(client):
    respx.get(f"{BASE_URL}/posts").mock(return_value=httpx.Response(500, json={}))
    ctx = make_ctx(client)
    result = await get_posts(ctx, limit=5)
    assert result.startswith("Error fetching posts")
    ctx.error.assert_awaited_once()


# --- get_post ---


async def test_get_post_invalid_id(client):
    ctx = make_ctx(client)
    result = await get_post(ctx, post_id=0)
    assert result.startswith("Error")


@respx.mock
async def test_get_post_success(client):
    respx.get(f"{BASE_URL}/posts/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "title": "Hello"})
    )
    ctx = make_ctx(client)
    result = await get_post(ctx, post_id=1)
    assert '"id": 1' in result


@respx.mock
async def test_get_post_not_found(client):
    respx.get(f"{BASE_URL}/posts/999").mock(return_value=httpx.Response(404, json={}))
    ctx = make_ctx(client)
    result = await get_post(ctx, post_id=999)
    assert result.startswith("Error fetching post")


# --- create_post ---


@respx.mock
async def test_create_post_success(client):
    respx.post(f"{BASE_URL}/posts").mock(
        return_value=httpx.Response(201, json={"id": 101, "title": "New"})
    )
    ctx = make_ctx(client)
    result = await create_post(ctx, title="New", body="Content")
    assert '"id": 101' in result


# --- update_post ---


async def test_update_post_invalid_id(client):
    ctx = make_ctx(client)
    result = await update_post(ctx, post_id=0, title="x", body="y")
    assert result.startswith("Error")


@respx.mock
async def test_update_post_success(client):
    respx.put(f"{BASE_URL}/posts/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "title": "Updated"})
    )
    ctx = make_ctx(client)
    result = await update_post(ctx, post_id=1, title="Updated", body="Body")
    assert '"id": 1' in result


# --- delete_post ---


async def test_delete_post_invalid_id(client):
    ctx = make_ctx(client)
    result = await delete_post(ctx, post_id=0)
    assert result.startswith("Error")


@respx.mock
async def test_delete_post_success(client):
    respx.delete(f"{BASE_URL}/posts/1").mock(return_value=httpx.Response(200, json={}))
    ctx = make_ctx(client)
    result = await delete_post(ctx, post_id=1)
    assert "deleted" in result.lower()


# --- token passthrough ---


@respx.mock
async def test_token_passthrough_forwarded_to_upstream(client):
    """Token from _meta.authorization is sent as Authorization header to upstream."""

    def check_auth(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer user-abc"
        return httpx.Response(200, json={"id": 1, "title": "Hello"})

    respx.get(f"{BASE_URL}/posts/1").mock(side_effect=check_auth)

    ctx = make_ctx(client)
    ctx.request_context.request = MagicMock()
    ctx.request_context.request.headers.get.return_value = "Bearer user-abc"

    result = await get_post(ctx, post_id=1)
    assert '"id": 1' in result
