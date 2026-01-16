import pathlib
from utils.load_module import load_module

HELPER_PATH = (
    pathlib.Path(__file__).parent.parent
    / "custom_components"
    / "spoolman"
    / "helpers"
    / "add_trailing_slash.py"
)
module = load_module(HELPER_PATH)
add_trailing_slash = module.add_trailing_slash

#==================== Testing starts bellow =====================
import pytest
#from custom_components.spoolman.helpers.add_trailing_slash import add_trailing_slash

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

