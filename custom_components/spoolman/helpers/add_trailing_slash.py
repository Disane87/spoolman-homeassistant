"""Helpers."""

from __future__ import annotations


def add_trailing_slash(input_string: str) -> str:
    """Add a trailing slash to ``input_string`` if not already present."""
    if not input_string.endswith("/"):
        input_string += "/"
    return input_string
