import importlib.util
from pathlib import Path

HELPER_PATH = (
    Path(__file__).parent.parent
    / "custom_components"
    / "spoolman"
    / "helpers"
    / "add_trailing_slash.py"
)

spec = importlib.util.spec_from_file_location("add_trailing_slash", HELPER_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
add_trailing_slash = module.add_trailing_slash

def test_adds_slash_when_missing():
    """It should add a trailing slash if the input does not end with '/'."""
    assert add_trailing_slash("http://example.com") == "http://example.com/"

def test_keeps_existing_slash():
    """It should not add another slash if one already exists."""
    assert add_trailing_slash("http://example.com/") == "http://example.com/"

def test_empty_string():
    """Edge case: empty string should become a single slash."""
    assert add_trailing_slash("") == "/"

def test_single_slash_input():
    """Input that is already '/' should remain unchanged."""
    assert add_trailing_slash("/") == "/"