"""Tests for server wiring utilities."""

from unittest.mock import MagicMock

from mcp_server_blueprint.server import get_request_token


def test_get_request_token_returns_authorization_from_request():
    ctx = MagicMock()
    ctx.request_context.request.headers.get.return_value = "Bearer user-token"
    assert get_request_token(ctx) == "user-token"


def test_get_request_token_returns_none_when_request_is_none():
    ctx = MagicMock()
    ctx.request_context.request = None
    assert get_request_token(ctx) is None


def test_get_request_token_returns_none_when_header_absent():
    ctx = MagicMock()
    ctx.request_context.request.headers.get.return_value = None
    assert get_request_token(ctx) is None


def test_get_request_token_returns_none_when_token_is_blank():
    ctx = MagicMock()
    ctx.request_context.request.headers.get.return_value = "Bearer "
    assert get_request_token(ctx) is None


def test_get_request_token_returns_none_for_non_bearer_scheme():
    ctx = MagicMock()
    ctx.request_context.request.headers.get.return_value = "Basic dXNlcjpwYXNz"
    assert get_request_token(ctx) is None
