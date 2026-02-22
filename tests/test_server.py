"""Tests for server wiring utilities."""

from unittest.mock import AsyncMock, MagicMock, patch

from mcp_server_blueprint.server import AppContext, app_lifespan, get_request_token


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


def test_get_request_token_returns_none_for_lowercase_bearer():
    # Scheme matching is case-sensitive per RFC 7235; "bearer" != "Bearer"
    ctx = MagicMock()
    ctx.request_context.request.headers.get.return_value = "bearer user-token"
    assert get_request_token(ctx) is None


def test_get_request_token_strips_extra_whitespace_from_token():
    # Double space after "Bearer" — strip() removes the leading space from the token slice
    ctx = MagicMock()
    ctx.request_context.request.headers.get.return_value = "Bearer  token-value"
    assert get_request_token(ctx) == "token-value"


def test_get_request_token_preserves_internal_spaces_in_token():
    # strip() only removes leading/trailing whitespace; internal spaces are preserved
    ctx = MagicMock()
    ctx.request_context.request.headers.get.return_value = "Bearer tok en"
    assert get_request_token(ctx) == "tok en"


def test_get_request_token_returns_none_for_tab_only_token():
    # A tab-only token collapses to empty string after strip(), returning None
    ctx = MagicMock()
    ctx.request_context.request.headers.get.return_value = "Bearer \t"
    assert get_request_token(ctx) is None


async def test_app_lifespan_yields_app_context():
    async with app_lifespan(object()) as ctx:
        assert isinstance(ctx, AppContext)
        assert ctx.http_client is not None
        assert ctx.config is not None


async def test_app_lifespan_closes_http_client_on_shutdown():
    target = "mcp_server_blueprint.server.HttpClient.close"
    with patch(target, new_callable=AsyncMock) as mock_close:
        async with app_lifespan(object()):
            pass
        mock_close.assert_awaited_once()
