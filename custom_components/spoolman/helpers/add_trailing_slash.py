"""Helpers."""
def add_trailing_slash(input_string) -> str:
    """Add trailing slash if not present."""
    if not input_string.endswith("/"):
        input_string += "/"
    return input_string
