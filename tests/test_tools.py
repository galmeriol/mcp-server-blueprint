"""Tests for MCP tools using mocked HTTP responses."""

import httpx
import pytest
import respx

from mcp_server_blueprint.errors import ApiClientError
from mcp_server_blueprint.infrastructure.http_client import HttpClient

BASE_URL = "https://jsonplaceholder.typicode.com"


@pytest.fixture
def mock_client():
    return HttpClient(base_url=BASE_URL, timeout=5)


@respx.mock
async def test_get_success(mock_client):
    respx.get(f"{BASE_URL}/posts/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "title": "Test"})
    )
    result = await mock_client.get("/posts/1")
    assert result["id"] == 1


@respx.mock
async def test_get_not_found(mock_client):
    respx.get(f"{BASE_URL}/posts/999").mock(
        return_value=httpx.Response(404, json={"error": "Not found"})
    )
    with pytest.raises(ApiClientError) as exc_info:
        await mock_client.get("/posts/999")
    assert exc_info.value.status_code == 404


@respx.mock
async def test_post_success(mock_client):
    respx.post(f"{BASE_URL}/posts").mock(
        return_value=httpx.Response(201, json={"id": 101, "title": "New"})
    )
    result = await mock_client.post("/posts", {"title": "New", "body": "Content"})
    assert result["id"] == 101


@respx.mock
async def test_put_success(mock_client):
    respx.put(f"{BASE_URL}/posts/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "title": "Updated"})
    )
    result = await mock_client.put("/posts/1", {"title": "Updated"})
    assert result["title"] == "Updated"


@respx.mock
async def test_patch_success(mock_client):
    respx.patch(f"{BASE_URL}/posts/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "title": "Patched"})
    )
    result = await mock_client.patch("/posts/1", {"title": "Patched"})
    assert result["title"] == "Patched"


@respx.mock
async def test_delete_success(mock_client):
    respx.delete(f"{BASE_URL}/posts/1").mock(return_value=httpx.Response(200, json={}))
    result = await mock_client.delete("/posts/1")
    assert result == {}


@respx.mock
async def test_token_passthrough_sets_authorization_header(mock_client):
    """A per-request token overrides the Authorization header for that call."""

    def check_auth(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer user-token"
        return httpx.Response(200, json={"id": 1})

    respx.get(f"{BASE_URL}/posts/1").mock(side_effect=check_auth)
    result = await mock_client.get("/posts/1", token="user-token")
    assert result["id"] == 1


@respx.mock
async def test_connection_error(mock_client):
    respx.get(f"{BASE_URL}/posts").mock(side_effect=httpx.ConnectError("Connection refused"))
    with pytest.raises(ApiClientError, match="Connection refused"):
        await mock_client.get("/posts")


@respx.mock
async def test_timeout_raises_api_client_error(mock_client):
    respx.get(f"{BASE_URL}/posts").mock(side_effect=httpx.TimeoutException("timed out"))
    with pytest.raises(ApiClientError, match="timed out"):
        await mock_client.get("/posts")
