# MCP Server Blueprint

A blueprint for building production-ready MCP servers with [FastMCP](https://github.com/jlowin/fastmcp).

## Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

```bash
uv sync
```

## Configuration

```bash
cp .env.example .env
```

## Running the Server

```bash
make serve
# or: uv run mcp-server-blueprint
```

The server starts on `http://127.0.0.1:8000` by default. The MCP endpoint is at `/mcp` (streamable HTTP transport).

To bind to all interfaces (e.g. inside Docker):

```bash
MCP_SERVER_HOST=0.0.0.0 make serve
```

## Development

```bash
make check      # lint + typecheck + tests + security audit (full quality gate)
make test       # tests with coverage report only
make lint       # ruff check
make format     # ruff check --fix + ruff format
make typecheck  # ty check
make audit      # pip-audit vulnerability scan
```

## Project Structure

```text
src/mcp_server_blueprint/
├── main.py            # Entry point (logging + mcp.run)
├── server.py          # FastMCP instance, lifespan, AppContext
├── config.py          # Pydantic-settings configuration with validators
├── errors.py          # Custom error types
├── descriptions.py    # Description strings for all tools, resources, and prompts
├── params.py          # Annotated type aliases with validation constraints
├── shared.py          # handle_errors decorator
├── tools.py           # MCP tools
├── resources.py       # MCP resources (static + template)
├── prompts.py         # MCP prompt templates
└── infrastructure/
    └── http_client.py # Async HTTP client with timeout and auth
```

## Extending

The three shared modules keep handlers focused purely on business logic:

- **`descriptions.py`** — human-readable descriptions passed to `@mcp.tool(description=...)`, visible to AI clients
- **`params.py`** — `Annotated` type aliases that carry both validation constraints (Pydantic `Field`, `StringConstraints`) and field descriptions for the JSON schema
- **`shared.py`** — `@handle_errors` catches any unhandled exception and returns a structured `{"error": ..., "status_code": ...}` JSON response, logging via `ctx.error` when a context is available

### Adding a Tool

**`descriptions.py`**

```python
YOUR_TOOL = "What the tool does, as seen by the AI client."
```

**`params.py`**

```python
YourParam = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1), Field(description="...")]
```

**`tools.py`**

```python
from .descriptions import YOUR_TOOL
from .params import YourParam
from .server import AppContext, mcp
from .shared import handle_errors

@mcp.tool(description=YOUR_TOOL)
@handle_errors
async def your_tool(ctx: Context, param: YourParam) -> str:
    app: AppContext = ctx.request_context.lifespan_context
    response = await app.http(ctx).get(f"/endpoint/{param}")
    return json.dumps(response, indent=2)
```

`app.http(ctx)` returns an `HttpClient` with the request's bearer token pre-bound — token passthrough works automatically without any extra wiring.

### Adding a Resource

```python
# descriptions.py
YOUR_RESOURCE = "What the resource exposes."

# resources.py
@mcp.resource("scheme://{param}", description=YOUR_RESOURCE)
@handle_errors
async def your_resource(param: YourParam, ctx: Context) -> str:
    app: AppContext = ctx.request_context.lifespan_context
    response = await app.http(ctx).get(f"/endpoint/{param}")
    return json.dumps(response, indent=2)
```

### Adding a Prompt

```python
# descriptions.py
YOUR_PROMPT = "What the prompt template does."

# prompts.py
@mcp.prompt(description=YOUR_PROMPT)
def your_prompt(param: YourParam) -> str:
    return f"Use the your_tool tool with param '{param}' and summarize the result."
```

## License

MIT
