"""Tests for configuration validation."""

from mcp_server_blueprint.config import Configuration


def test_default_config():
    config = Configuration()
    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.auth_type == "none"
    assert config.base_url == "https://jsonplaceholder.typicode.com"
    assert config.timeout == 30


def test_token_passthrough_auth_type():
    config = Configuration(auth_type="token_passthrough")
    assert config.auth_type == "token_passthrough"
