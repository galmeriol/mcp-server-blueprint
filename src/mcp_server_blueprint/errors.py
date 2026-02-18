"""Custom error types for the MCP REST Server."""


class McpServerError(Exception):
    """Base error for all MCP REST Server errors."""


class ConfigurationError(McpServerError):
    """Invalid or missing configuration."""


class ApiClientError(McpServerError):
    """Error communicating with the upstream REST API."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(McpServerError):
    """Authentication or token exchange failure."""
