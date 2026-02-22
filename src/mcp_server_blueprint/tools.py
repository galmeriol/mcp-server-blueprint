"""MCP tools — REST API operations exposed to AI assistants."""

import json
import uuid

from mcp.server.fastmcp import Context

from .descriptions import CREATE_POST, DELETE_POST, GET_POST, GET_POSTS, UPDATE_POST
from .params import PostBody, PostId, PostLimit, PostTitle, UserId
from .server import AppContext, mcp
from .shared import handle_errors


@mcp.tool(description=GET_POSTS)
@handle_errors
async def get_posts(ctx: Context, limit: PostLimit = 10) -> str:
    app: AppContext = ctx.request_context.lifespan_context
    request_id = str(uuid.uuid4())[:8]
    await ctx.info(f"[{request_id}] Fetching up to {limit} posts")

    response = await app.http(ctx).get("/posts", params={"_limit": limit})
    posts = response if isinstance(response, list) else [response]
    await ctx.info(f"[{request_id}] Retrieved {len(posts)} posts")
    return json.dumps(posts, indent=2, ensure_ascii=False)


@mcp.tool(description=GET_POST)
@handle_errors
async def get_post(ctx: Context, post_id: PostId) -> str:
    app: AppContext = ctx.request_context.lifespan_context
    request_id = str(uuid.uuid4())[:8]
    await ctx.info(f"[{request_id}] Fetching post {post_id}")

    response = await app.http(ctx).get(f"/posts/{post_id}")
    return json.dumps(response, indent=2, ensure_ascii=False)


@mcp.tool(description=CREATE_POST)
@handle_errors
async def create_post(ctx: Context, title: PostTitle, body: PostBody, user_id: UserId = 1) -> str:
    app: AppContext = ctx.request_context.lifespan_context
    request_id = str(uuid.uuid4())[:8]
    await ctx.info(f"[{request_id}] Creating post: {title}")

    response = await app.http(ctx).post(
        "/posts",
        {"title": title, "body": body, "userId": user_id},
    )
    await ctx.info(f"[{request_id}] Post created successfully")
    return json.dumps(response, indent=2, ensure_ascii=False)


@mcp.tool(description=UPDATE_POST)
@handle_errors
async def update_post(
    ctx: Context,
    post_id: PostId,
    title: PostTitle,
    body: PostBody,
    user_id: UserId = 1,
) -> str:
    app: AppContext = ctx.request_context.lifespan_context
    request_id = str(uuid.uuid4())[:8]
    await ctx.info(f"[{request_id}] Updating post {post_id}")

    response = await app.http(ctx).put(
        f"/posts/{post_id}",
        {"title": title, "body": body, "userId": user_id},
    )
    await ctx.info(f"[{request_id}] Post {post_id} updated successfully")
    return json.dumps(response, indent=2, ensure_ascii=False)


@mcp.tool(description=DELETE_POST)
@handle_errors
async def delete_post(ctx: Context, post_id: PostId) -> str:
    app: AppContext = ctx.request_context.lifespan_context
    request_id = str(uuid.uuid4())[:8]
    await ctx.info(f"[{request_id}] Deleting post {post_id}")

    await app.http(ctx).delete(f"/posts/{post_id}")
    await ctx.info(f"[{request_id}] Post {post_id} deleted")
    return f"Post {post_id} deleted successfully"
