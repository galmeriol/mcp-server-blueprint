"""Shared test fixtures."""

import pytest

from mcp_server_blueprint.config import Configuration
from mcp_server_blueprint.infrastructure.http_client import HttpClient


@pytest.fixture
def config():
    """Test configuration with no auth."""
    return Configuration(
        base_url="https://jsonplaceholder.typicode.com",
        auth_type="none",
    )


@pytest.fixture
def http_client(config):
    """HttpClient for testing (no auth)."""
    return HttpClient(
        base_url=config.base_url,
        timeout=config.timeout,
    )
