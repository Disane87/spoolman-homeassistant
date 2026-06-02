"""Test the image-generation helpers in sensor.py.

These run in the executor thread in production; calling them directly is
sufficient for coverage.
"""

from __future__ import annotations

import os

from custom_components.spoolman.sensor import (
    _generate_entity_picture,
    _generate_filament_entity_picture,
)


def test_generate_entity_picture_single_color(tmp_path) -> None:
    """A spool with a single color writes a PNG and returns its local URL."""
    spool = {"id": 1, "filament": {"color_hex": "FF6600"}}
    url = _generate_entity_picture(spool, str(tmp_path))
    assert url is not None
    assert url.endswith("spool_1.png")
    assert os.path.exists(os.path.join(str(tmp_path), "spool_1.png"))


def test_generate_entity_picture_multi_color_coaxial(tmp_path) -> None:
    """Multi-color spools use the multi_color_hexes list, coaxial bands."""
    spool = {
        "id": 7,
        "filament": {
            "multi_color_hexes": "FF6600,00AA00,0000FF",
            "multi_color_direction": "coaxial",
        },
    }
    url = _generate_entity_picture(spool, str(tmp_path))
    assert url is not None
    assert os.path.exists(os.path.join(str(tmp_path), "spool_7.png"))


def test_generate_entity_picture_multi_color_longitudinal(tmp_path) -> None:
    """Multi-color spools also support longitudinal bands."""
    spool = {
        "id": 8,
        "filament": {
            "multi_color_hexes": "FF0000,00FF00",
            "multi_color_direction": "longitudinal",
        },
    }
    url = _generate_entity_picture(spool, str(tmp_path))
    assert url is not None


def test_generate_entity_picture_no_color_returns_none(tmp_path) -> None:
    """A filament with no color information returns None and logs a warning."""
    spool = {"id": 9, "filament": {"color_hex": "", "multi_color_hexes": ""}}
    url = _generate_entity_picture(spool, str(tmp_path))
    assert url is None


def test_generate_filament_entity_picture_single_color(tmp_path) -> None:
    """Same routine for the per-filament image."""
    fil = {"id": 10, "color_hex": "FF6600"}
    url = _generate_filament_entity_picture(fil, str(tmp_path))
    assert url is not None
    assert url.endswith("filament_10.png")


def test_generate_filament_entity_picture_no_color(tmp_path) -> None:
    """No-color filament returns None."""
    fil = {"id": 11, "color_hex": "", "multi_color_hexes": ""}
    url = _generate_filament_entity_picture(fil, str(tmp_path))
    assert url is None


def test_generate_filament_entity_picture_multi_longitudinal(tmp_path) -> None:
    """Filament longitudinal multi-color path."""
    fil = {
        "id": 12,
        "multi_color_hexes": "FF0000,00FF00",
        "multi_color_direction": "longitudinal",
    }
    url = _generate_filament_entity_picture(fil, str(tmp_path))
    assert url is not None
