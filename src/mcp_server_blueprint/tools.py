"""MCP tools — REST API operations exposed to AI assistants."""

import json

from mcp.server.fastmcp import Context

from .errors import ApiClientError
from .server import AppContext, mcp


@mcp.tool()
async def get_posts(ctx: Context, limit: int = 10) -> str:
    """Get posts from the REST API.

    Args:
        limit: Maximum number of posts to return (1-100, default: 10)
    """
    if limit < 1 or limit > 100:
        return "Error: limit must be between 1 and 100"

    app: AppContext = ctx.request_context.lifespan_context
    await ctx.info(f"Fetching up to {limit} posts")

    try:
        response = await app.http(ctx).get("/posts", params={"_limit": limit})
        posts = response if isinstance(response, list) else [response]
        await ctx.info(f"Retrieved {len(posts)} posts")
        return json.dumps(posts, indent=2, ensure_ascii=False)
    except ApiClientError as e:
        await ctx.error(str(e))
        return f"Error fetching posts: {e}"


@mcp.tool()
async def get_post(ctx: Context, post_id: int) -> str:
    """Get a specific post by ID.

    Args:
        post_id: The post ID to retrieve (must be positive)
    """
    if post_id < 1:
        return "Error: post_id must be a positive integer"

    app: AppContext = ctx.request_context.lifespan_context
    await ctx.info(f"Fetching post {post_id}")

    try:
        response = await app.http(ctx).get(f"/posts/{post_id}")
        return json.dumps(response, indent=2, ensure_ascii=False)
    except ApiClientError as e:
        await ctx.error(str(e))
        return f"Error fetching post {post_id}: {e}"


@mcp.tool()
async def create_post(ctx: Context, title: str, body: str, user_id: int = 1) -> str:
    """Create a new post.

    Args:
        title: Post title
        body: Post content
        user_id: Author user ID (default: 1)
    """
    app: AppContext = ctx.request_context.lifespan_context
    await ctx.info(f"Creating post: {title}")

    try:
        response = await app.http(ctx).post(
            "/posts",
            {"title": title, "body": body, "userId": user_id},
        )
        await ctx.info("Post created successfully")
        return json.dumps(response, indent=2, ensure_ascii=False)
    except ApiClientError as e:
        await ctx.error(str(e))
        return f"Error creating post: {e}"


@mcp.tool()
async def update_post(ctx: Context, post_id: int, title: str, body: str, user_id: int = 1) -> str:
    """Update an existing post.

    Args:
        post_id: ID of the post to update (must be positive)
        title: New post title
        body: New post content
        user_id: Author user ID (default: 1)
    """
    if post_id < 1:
        return "Error: post_id must be a positive integer"

    app: AppContext = ctx.request_context.lifespan_context
    await ctx.info(f"Updating post {post_id}")

    try:
        response = await app.http(ctx).put(
            f"/posts/{post_id}",
            {"title": title, "body": body, "userId": user_id},
        )
        await ctx.info(f"Post {post_id} updated successfully")
        return json.dumps(response, indent=2, ensure_ascii=False)
    except ApiClientError as e:
        await ctx.error(str(e))
        return f"Error updating post {post_id}: {e}"


@mcp.tool()
async def delete_post(ctx: Context, post_id: int) -> str:
    """Delete a post.

    Args:
        post_id: ID of the post to delete (must be positive)
    """
    if post_id < 1:
        return "Error: post_id must be a positive integer"

    app: AppContext = ctx.request_context.lifespan_context
    await ctx.info(f"Deleting post {post_id}")

    try:
        await app.http(ctx).delete(f"/posts/{post_id}")
        await ctx.info(f"Post {post_id} deleted")
        return f"Post {post_id} deleted successfully"
    except ApiClientError as e:
        await ctx.error(str(e))
        return f"Error deleting post {post_id}: {e}"
