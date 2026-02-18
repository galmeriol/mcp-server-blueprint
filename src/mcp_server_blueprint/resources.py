"""MCP resources — data exposed as readable context for AI assistants."""

import datetime
import json
import socket

from mcp.server.fastmcp import Context

from .errors import ApiClientError
from .server import AppContext, mcp


@mcp.resource("resource://host")
async def host_resource() -> str:
    """Hostname of the server process running this MCP instance.

    In containerised environments this reflects the container or pod name,
    not a stable network identifier.
    """
    hostname = socket.gethostname()
    return f"This is the host '{hostname}' serving the MCP resources."


@mcp.resource("health://status")
async def health_status(ctx: Context) -> str:
    """Server health and non-sensitive configuration for operational monitoring."""
    app: AppContext = ctx.request_context.lifespan_context
    return json.dumps(
        {
            "status": "ok",
            "checked_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "base_url": app.config.base_url,
            "auth_type": app.config.auth_type,
            "timeout": app.config.timeout,
        },
        indent=2,
    )


@mcp.resource("config://server")
async def server_config(ctx: Context) -> str:
    """Current server configuration (non-sensitive fields only)."""
    app: AppContext = ctx.request_context.lifespan_context
    return json.dumps(
        {
            "base_url": app.config.base_url,
            "timeout": app.config.timeout,
            "auth_type": app.config.auth_type,
        },
        indent=2,
    )


@mcp.resource("posts://{post_id}")
async def post_resource(post_id: int, ctx: Context) -> str:
    """A specific post as a readable resource.

    Args:
        post_id: The post ID to fetch
    """
    app: AppContext = ctx.request_context.lifespan_context
    try:
        response = await app.http(ctx).get(f"/posts/{post_id}")
        return json.dumps(response, indent=2, ensure_ascii=False)
    except ApiClientError as e:
        return json.dumps({"error": str(e)})
