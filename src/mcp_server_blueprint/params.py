"""Parameter type annotations for MCP tools, resources, and prompts.

Each alias pairs a Python type with validation constraints and a human-readable
description. FastMCP builds the JSON schema from these annotations, so
constraints are enforced before the handler is called and are visible to AI clients.
"""

from typing import Annotated

from pydantic import Field
from pydantic.types import StringConstraints

PostLimit = Annotated[
    int,
    Field(ge=1, le=100, description="Maximum number of posts to return (1-100, default: 10)"),
]
PostId = Annotated[int, Field(ge=1, description="Post ID (must be positive)")]
PostTitle = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
    Field(description="Post title"),
]
PostBody = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
    Field(description="Post content"),
]
UserId = Annotated[int, Field(description="Author user ID (default: 1)")]
PromptTopic = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
    Field(description="Topic to write about"),
]
