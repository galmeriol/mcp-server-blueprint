"""MCP resources — data exposed as readable context for AI assistants."""

import datetime
import json
import socket

from mcp.server.fastmcp import Context

from .descriptions import HEALTH_STATUS, HOST_RESOURCE, POST_RESOURCE, SERVER_CONFIG
from .params import PostId
from .server import AppContext, mcp
from .shared import handle_errors


@mcp.resource("resource://host", description=HOST_RESOURCE)
async def host_resource() -> str:
    hostname = socket.gethostname()
    return f"This is the host '{hostname}' serving the MCP resources."


@mcp.resource("health://status", description=HEALTH_STATUS)
async def health_status(ctx: Context) -> str:
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


@mcp.resource("config://server", description=SERVER_CONFIG)
async def server_config(ctx: Context) -> str:
    app: AppContext = ctx.request_context.lifespan_context
    return json.dumps(
        {
            "base_url": app.config.base_url,
            "timeout": app.config.timeout,
            "auth_type": app.config.auth_type,
        },
        indent=2,
    )


@mcp.resource("posts://{post_id}", description=POST_RESOURCE)
@handle_errors
async def post_resource(post_id: PostId, ctx: Context) -> str:
    app: AppContext = ctx.request_context.lifespan_context
    response = await app.http(ctx).get(f"/posts/{post_id}")
    return json.dumps(response, indent=2, ensure_ascii=False)
