"""Tests for the add_trailing_slash helper (contributed in #289)."""

from custom_components.spoolman.helpers.add_trailing_slash import add_trailing_slash


def test_adds_slash_when_missing() -> None:
    """It should add a trailing slash if the input does not end with '/'."""
    assert add_trailing_slash("http://example.com") == "http://example.com/"


def test_keeps_existing_slash() -> None:
    """It should not add another slash if one already exists."""
    assert add_trailing_slash("http://example.com/") == "http://example.com/"


def test_empty_string() -> None:
    """Edge case: empty string should become a single slash."""
    assert add_trailing_slash("") == "/"


def test_single_slash_input() -> None:
    """Input that is already '/' should remain unchanged."""
    assert add_trailing_slash("/") == "/"
