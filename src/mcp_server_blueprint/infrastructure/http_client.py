"""Async HTTP client for REST API communication."""

import logging
from typing import Any

import httpx

from ..errors import ApiClientError

logger = logging.getLogger(__name__)


class HttpClient:
    """Async HTTP client managed via server lifespan.

    Auth-agnostic — receives pre-resolved auth headers from the server.
    Created once at startup, shared across all tool/resource invocations,
    closed at shutdown.

    For token_passthrough auth, pass the client's token via the `token`
    parameter on each method call. It overrides any static auth header.
    """

    def __init__(self, base_url: str, timeout: int = 30):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        logger.info("HTTP client initialized (base_url=%s)", base_url)

    async def close(self) -> None:
        """Close the underlying connection pool."""
        await self._client.aclose()
        logger.info("HTTP client closed")

    async def get(
        self, endpoint: str, params: dict[str, Any] | None = None, token: str | None = None
    ) -> Any:
        """Perform GET request."""
        return await self._request("GET", endpoint, params=params, token=token)

    async def post(
        self, endpoint: str, data: dict[str, Any], token: str | None = None
    ) -> Any:
        """Perform POST request."""
        return await self._request("POST", endpoint, json=data, token=token)

    async def put(
        self, endpoint: str, data: dict[str, Any], token: str | None = None
    ) -> Any:
        """Perform PUT request."""
        return await self._request("PUT", endpoint, json=data, token=token)

    async def patch(
        self, endpoint: str, data: dict[str, Any], token: str | None = None
    ) -> Any:
        """Perform PATCH request for partial resource updates."""
        return await self._request("PATCH", endpoint, json=data, token=token)

    async def delete(self, endpoint: str, token: str | None = None) -> Any:
        """Perform DELETE request."""
        return await self._request("DELETE", endpoint, token=token)

    async def _request(
        self, method: str, endpoint: str, token: str | None = None, **kwargs: Any
    ) -> Any:
        """Execute HTTP request with error wrapping.

        If `token` is provided it is sent as the Authorization header for this
        request only, overriding any static header set at initialisation time.
        """
        if token is not None:
            kwargs.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise ApiClientError(
                f"{method} {endpoint} failed: HTTP {e.response.status_code}",
                status_code=e.response.status_code,
            ) from e
        except httpx.RequestError as e:
            raise ApiClientError(f"{method} {endpoint} failed: {e}") from e


class BoundHttpClient:
    """HttpClient wrapper with a per-request bearer token pre-bound.

    Obtained via AppContext.http(ctx) — eliminates token threading through
    every tool and resource handler. The same underlying connection pool is
    reused; only the per-request Authorization header changes.
    """

    def __init__(self, client: HttpClient, token: str | None) -> None:
        self._client = client
        self._token = token

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        return await self._client.get(endpoint, params=params, token=self._token)

    async def post(self, endpoint: str, data: dict[str, Any]) -> Any:
        return await self._client.post(endpoint, data, token=self._token)

    async def put(self, endpoint: str, data: dict[str, Any]) -> Any:
        return await self._client.put(endpoint, data, token=self._token)

    async def patch(self, endpoint: str, data: dict[str, Any]) -> Any:
        return await self._client.patch(endpoint, data, token=self._token)

    async def delete(self, endpoint: str) -> Any:
        return await self._client.delete(endpoint, token=self._token)
