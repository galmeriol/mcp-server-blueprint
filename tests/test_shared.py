"""Tests for the handle_errors decorator."""

import json
from unittest.mock import AsyncMock, MagicMock

from mcp_server_blueprint.errors import ApiClientError
from mcp_server_blueprint.shared import handle_errors


def make_ctx() -> MagicMock:
    ctx = MagicMock()
    ctx.error = AsyncMock()
    return ctx


async def test_returns_result_on_success():
    @handle_errors
    async def handler(ctx):
        return "ok"

    result = await handler(make_ctx())
    assert result == "ok"


async def test_catches_api_client_error_and_returns_json():
    @handle_errors
    async def handler(ctx):
        raise ApiClientError("upstream failed", status_code=503)

    result = json.loads(await handler(make_ctx()))
    assert result["error"] == "upstream failed"
    assert result["status_code"] == 503


async def test_logs_to_ctx_error_when_ctx_present():
    @handle_errors
    async def handler(ctx):
        raise ApiClientError("bad request", status_code=400)

    ctx = make_ctx()
    await handler(ctx)
    ctx.error.assert_awaited_once_with("bad request")


async def test_status_code_none_for_network_errors():
    @handle_errors
    async def handler(ctx):
        raise ApiClientError("connection refused")

    result = json.loads(await handler(make_ctx()))
    assert result["status_code"] is None


async def test_works_without_ctx_parameter():
    @handle_errors
    async def handler():
        raise ApiClientError("no ctx here")

    result = json.loads(await handler())
    assert "error" in result
    assert "status_code" in result


async def test_non_api_errors_are_caught_and_returned_as_json():
    @handle_errors
    async def handler(ctx):
        raise RuntimeError("unexpected")

    result = json.loads(await handler(make_ctx()))
    assert result["error"] == "unexpected"
    assert result["status_code"] is None
