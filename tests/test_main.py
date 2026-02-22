"""Tests for the main() entry point."""

from unittest.mock import patch

from mcp_server_blueprint.main import main
from mcp_server_blueprint.server import mcp


def test_main_runs_with_streamable_http():
    with patch.object(mcp, "run") as mock_run:
        main()
        mock_run.assert_called_once_with(transport="streamable-http")


def test_main_sets_host_and_port_from_config():
    with patch.object(mcp, "run"):
        main()
        assert mcp.settings.host == "127.0.0.1"
        assert mcp.settings.port == 8000
