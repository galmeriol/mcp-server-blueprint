"""Tests for configuration validation."""

import pytest
from pydantic import ValidationError

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


def test_invalid_auth_type_raises_validation_error():
    with pytest.raises(ValidationError):
        Configuration(auth_type="oauth2")  # type: ignore[arg-type]


def test_negative_port_raises_validation_error():
    with pytest.raises(ValidationError):
        Configuration(port=-1)


def test_env_var_override(monkeypatch):
    monkeypatch.setenv("MCP_SERVER_BASE_URL", "https://api.example.com")
    monkeypatch.setenv("MCP_SERVER_PORT", "9090")
    config = Configuration()
    assert config.base_url == "https://api.example.com"
    assert config.port == 9090
