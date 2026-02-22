"""Description strings for MCP tools, resources, and prompts.

Centralising descriptions here keeps handler functions free of prose and ensures
the contract exposed to AI clients is easy to review and update in one place.
"""

# --- Tools ---

GET_POSTS = "Get posts from the REST API."
GET_POST = "Get a specific post by ID."
CREATE_POST = "Create a new post."
UPDATE_POST = "Update an existing post."
DELETE_POST = "Delete a post."

# --- Resources ---

HOST_RESOURCE = (
    "Hostname of the server process running this MCP instance.\n\n"
    "In containerised environments this reflects the container or pod name, "
    "not a stable network identifier."
)
HEALTH_STATUS = "Server health and non-sensitive configuration for operational monitoring."
SERVER_CONFIG = "Current server configuration (non-sensitive fields only)."
POST_RESOURCE = "A specific post as a readable resource."

# --- Prompts ---

SUMMARIZE_POST = "Create a prompt to summarize a specific post."
DRAFT_POST = "Create a prompt to draft a new blog post about a topic."
