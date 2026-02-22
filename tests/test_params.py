"""Tests for parameter type constraints."""

import pytest
from pydantic import TypeAdapter, ValidationError

from mcp_server_blueprint.params import (
    PostBody,
    PostId,
    PostLimit,
    PostTitle,
    PromptTopic,
)

# --- PostLimit (ge=1, le=100) ---


def test_post_limit_accepts_boundaries():
    ta = TypeAdapter(PostLimit)
    assert ta.validate_python(1) == 1
    assert ta.validate_python(100) == 100


def test_post_limit_rejects_zero():
    with pytest.raises(ValidationError):
        TypeAdapter(PostLimit).validate_python(0)


def test_post_limit_rejects_above_max():
    with pytest.raises(ValidationError):
        TypeAdapter(PostLimit).validate_python(101)


# --- PostId (ge=1) ---


def test_post_id_accepts_positive():
    assert TypeAdapter(PostId).validate_python(1) == 1


def test_post_id_rejects_zero():
    with pytest.raises(ValidationError):
        TypeAdapter(PostId).validate_python(0)


def test_post_id_rejects_negative():
    with pytest.raises(ValidationError):
        TypeAdapter(PostId).validate_python(-5)


# --- PostTitle / PostBody (strip_whitespace=True, min_length=1) ---


def test_post_title_accepts_valid():
    assert TypeAdapter(PostTitle).validate_python("Hello") == "Hello"


def test_post_title_strips_whitespace():
    assert TypeAdapter(PostTitle).validate_python("  Hello  ") == "Hello"


def test_post_title_rejects_empty():
    with pytest.raises(ValidationError):
        TypeAdapter(PostTitle).validate_python("")


def test_post_title_rejects_blank():
    with pytest.raises(ValidationError):
        TypeAdapter(PostTitle).validate_python("   ")


def test_post_body_rejects_empty():
    with pytest.raises(ValidationError):
        TypeAdapter(PostBody).validate_python("")


def test_post_body_rejects_blank():
    with pytest.raises(ValidationError):
        TypeAdapter(PostBody).validate_python("   ")


# --- PromptTopic (strip_whitespace=True, min_length=1) ---


def test_prompt_topic_accepts_valid():
    assert TypeAdapter(PromptTopic).validate_python("AI ethics") == "AI ethics"


def test_prompt_topic_strips_whitespace():
    assert TypeAdapter(PromptTopic).validate_python("  AI ethics  ") == "AI ethics"


def test_prompt_topic_rejects_empty():
    with pytest.raises(ValidationError):
        TypeAdapter(PromptTopic).validate_python("")


def test_prompt_topic_rejects_blank():
    with pytest.raises(ValidationError):
        TypeAdapter(PromptTopic).validate_python("   ")
