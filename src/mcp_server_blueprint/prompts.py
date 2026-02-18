"""MCP prompts — reusable prompt templates for AI assistants."""

from .server import mcp


@mcp.prompt()
def summarize_post(post_id: int) -> str:
    """Create a prompt to summarize a specific post.

    Args:
        post_id: ID of the post to summarize
    """
    return (
        f"Read the post with ID {post_id} using the get_post tool, "
        f"then provide a concise summary of its title and content."
    )


@mcp.prompt()
def draft_post(topic: str) -> str:
    """Create a prompt to draft a new blog post about a topic.

    Args:
        topic: The topic to write about
    """
    return (
        f"Draft a new blog post about '{topic}'. "
        f"First use get_posts to see existing posts for style reference, "
        f"then use create_post to publish the draft."
    )
