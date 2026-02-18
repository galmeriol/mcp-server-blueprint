"""MCP REST Server — FastMCP instance, lifespan, and wiring."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, ConfigDict

from .config import Configuration
from .infrastructure import BoundHttpClient, HttpClient

logger = logging.getLogger(__name__)


def get_request_token(ctx: Context) -> str | None:
    """
    Extract the bearer token from the incoming HTTP request's Authorization header.

    Returns the token value
    """
    request = ctx.request_context.request
    if not request:
        return None
    auth = request.headers.get("Authorization")
    # place to add additional controls, logic for token extraction, transformation if needed
    if auth and auth.startswith("Bearer "):
        token = auth[len("Bearer "):].strip()
        return token or None
    return None


class AppContext(BaseModel):
    """Lifespan context shared across all tools, resources, and prompts.

    Access from any handler via: ctx.request_context.lifespan_context
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    http_client: HttpClient
    config: Configuration

    def http(self, ctx: Context) -> BoundHttpClient:
        """Return an HTTP client with the request's bearer token pre-bound.

        Use this in every tool and resource handler instead of accessing
        http_client directly — it handles token passthrough transparently.

            http = app.http(ctx)
            response = await http.get("/posts")
        """
        return BoundHttpClient(self.http_client, get_request_token(ctx))


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle.

    Creates shared HTTP client on startup, tears it down on shutdown.
    """
    config = Configuration()
    logger.info("Starting server (base_url=%s, auth_type=%s)", config.base_url, config.auth_type)

    http_client = HttpClient(base_url=config.base_url, timeout=config.timeout)

    try:
        yield AppContext(http_client=http_client, config=config)
    finally:
        await http_client.close()
        logger.info("Server shutdown complete")


mcp = FastMCP("mcp-server-blueprint", lifespan=app_lifespan)

# Register MCP primitives — these modules use @mcp decorators on import
from . import prompts as _prompts  # noqa: E402, F401
from . import resources as _resources  # noqa: E402, F401
from . import tools as _tools  # noqa: E402, F401
