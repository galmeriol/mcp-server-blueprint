"""MCP prompts — reusable prompt templates for AI assistants."""

from .descriptions import DRAFT_POST, SUMMARIZE_POST
from .params import PostId, PromptTopic
from .server import mcp


@mcp.prompt(description=SUMMARIZE_POST)
def summarize_post(post_id: PostId) -> str:
    return (
        f"Read the post with ID {post_id} using the get_post tool, "
        f"then provide a concise summary of its title and content."
    )


@mcp.prompt(description=DRAFT_POST)
def draft_post(topic: PromptTopic) -> str:
    return (
        f"Draft a new blog post about '{topic}'. "
        f"First use get_posts to see existing posts for style reference, "
        f"then use create_post to publish the draft."
    )
