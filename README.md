# MCP Server Blueprint

A blueprint for building FastMCP-based MCP servers.

## Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

```bash
uv sync
```

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `MCP_SERVER_HOST` | `127.0.0.1` | Interface to bind the HTTP server to |
| `MCP_SERVER_PORT` | `8000` | Port to listen on |
| `MCP_SERVER_BASE_URL` | `https://jsonplaceholder.typicode.com` | Base URL of the upstream REST API |
| `MCP_SERVER_TIMEOUT` | `30` | Request timeout in seconds |
| `MCP_SERVER_AUTH_TYPE` | `none` | `none` or `token_passthrough` |

With `token_passthrough`, the server has no credentials of its own — each MCP client provides its bearer token via the HTTP `Authorization` header, and the server forwards it to the upstream API.

## Running the Server

```bash
uv run mcp-server-blueprint
```

The server starts on `http://127.0.0.1:8000` by default. The MCP endpoint is at `/mcp` (streamable HTTP transport).

To bind to all interfaces (e.g. inside Docker):

```bash
MCP_SERVER_HOST=0.0.0.0 uv run mcp-server-blueprint
```

## Running Tests

```bash
uv run pytest
```

## Project Structure

```text
src/mcp_server_blueprint/
├── main.py                # Entry point (logging + mcp run)
├── server.py              # FastMCP instance, lifespan, AppContext
├── config.py              # Configuration with validation
├── errors.py              # Custom error types
├── tools.py               # MCP tools
├── resources.py           # MCP resources (static + dynamic)
├── prompts.py             # MCP prompt templates
└── infrastructure/
    └── http_client.py     # Async HTTP client
```

## Extending

### Adding a Tool

```python
from .server import AppContext, mcp
from .errors import ApiClientError

@mcp.tool()
async def your_tool(ctx: Context, param: str) -> str:
    """Tool description."""
    app: AppContext = ctx.request_context.lifespan_context
    try:
        response = await app.http(ctx).get(f"/endpoint/{param}")
        return json.dumps(response, indent=2)
    except ApiClientError as e:
        await ctx.error(str(e))
        return f"Error: {e}"
```

`app.http(ctx)` returns an `HttpClient` with the request's bearer token pre-bound —
token passthrough works automatically without any extra wiring in your tool.

### Adding a Resource

```python
@mcp.resource("scheme://{param}")
async def your_resource(param: str, ctx: Context) -> str:
    """Resource description."""
    app: AppContext = ctx.request_context.lifespan_context
    response = await app.http(ctx).get(f"/endpoint/{param}")
    return json.dumps(response, indent=2)
```

### Adding a Prompt

```python
@mcp.prompt()
def your_prompt(param: str) -> str:
    """Prompt description."""
    return f"Use the your_tool tool with param '{param}' and summarize the result."
```

## License

MIT
