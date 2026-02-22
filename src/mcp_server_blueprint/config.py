"""Configuration management for MCP REST Server."""

from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuration(BaseSettings):
    """Application configuration loaded from environment variables.

    All variables are prefixed with MCP_SERVER_ and can be set via .env file.
    """

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # API
    base_url: str = "https://jsonplaceholder.typicode.com"
    timeout: int = 30

    # Authentication
    auth_type: Literal["none", "token_passthrough"] = "none"

    model_config = SettingsConfigDict(
        env_prefix="MCP_SERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @field_validator("port", "timeout")
    @classmethod
    def must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("must be a positive integer")
        return v
