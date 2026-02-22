"""MCP REST Server entry point."""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main() -> None:
    """Run the MCP REST Server via HTTP (streamable-http) transport."""
    from .config import Configuration
    from .server import mcp

    config = Configuration()
    mcp.settings.host = config.host
    mcp.settings.port = config.port
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
