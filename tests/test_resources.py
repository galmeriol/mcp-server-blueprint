"""Tests for MCP resource functions."""

import json
import socket
from unittest.mock import AsyncMock, MagicMock

import httpx
import respx

from mcp_server_blueprint.config import Configuration
from mcp_server_blueprint.infrastructure.http_client import HttpClient
from mcp_server_blueprint.resources import (
    health_status,
    host_resource,
    post_resource,
    server_config,
)
from mcp_server_blueprint.server import AppContext

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


def make_client() -> HttpClient:
    return HttpClient(base_url=BASE_URL, timeout=5)


async def test_host_resource_returns_hostname():
    result = await host_resource()
    assert socket.gethostname() in result


async def test_server_config_returns_expected_fields():
    ctx = make_ctx(make_client())
    result = json.loads(await server_config(ctx))
    assert result["base_url"] == BASE_URL
    assert result["auth_type"] == "none"
    assert "timeout" in result
    assert "api_key" not in result


async def test_health_status_returns_ok():
    ctx = make_ctx(make_client())
    result = json.loads(await health_status(ctx))
    assert result["status"] == "ok"
    assert "checked_at" in result
    assert result["base_url"] == BASE_URL


@respx.mock
async def test_post_resource_success():
    respx.get(f"{BASE_URL}/posts/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "title": "Hello"})
    )
    ctx = make_ctx(make_client())
    result = json.loads(await post_resource(1, ctx))
    assert result["id"] == 1


@respx.mock
async def test_post_resource_error_returns_json():
    respx.get(f"{BASE_URL}/posts/999").mock(return_value=httpx.Response(404, json={}))
    ctx = make_ctx(make_client())
    result = json.loads(await post_resource(999, ctx))
    assert "error" in result
    assert "status_code" in result
