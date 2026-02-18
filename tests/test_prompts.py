"""Tests for MCP prompt templates."""

from mcp_server_blueprint.prompts import draft_post, summarize_post


def test_summarize_post_includes_post_id():
    result = summarize_post(42)
    assert "42" in result
    assert "get_post" in result


def test_draft_post_includes_topic():
    result = draft_post("machine learning")
    assert "machine learning" in result
    assert "create_post" in result
