"""Test the entity-picture helpers in sensor.py and the legacy image cleanup."""

from __future__ import annotations

import base64
from pathlib import Path

from custom_components.spoolman import _remove_legacy_images
from custom_components.spoolman.sensor import (
    _generate_entity_picture,
    _generate_filament_entity_picture,
)

PREFIX = "data:image/svg+xml;base64,"


def _svg(url: str | None) -> str:
    """Decode a data URI returned by the helpers."""
    assert url is not None
    assert url.startswith(PREFIX)
    return base64.b64decode(url[len(PREFIX) :]).decode()


def test_generate_entity_picture_single_color() -> None:
    """A spool with a single color returns an inline SVG in that color."""
    spool = {"id": 1, "filament": {"color_hex": "FF6600"}}
    svg = _svg(_generate_entity_picture(spool))
    assert svg.startswith("<svg ")
    assert 'fill="#FF6600"' in svg


def test_generate_entity_picture_multi_color_coaxial() -> None:
    """Multi-color spools use the multi_color_hexes list, coaxial bands."""
    spool = {
        "id": 7,
        "filament": {
            "multi_color_hexes": "FF6600,00AA00,0000FF",
            "multi_color_direction": "coaxial",
        },
    }
    svg = _svg(_generate_entity_picture(spool))
    for color in ("FF6600", "00AA00", "0000FF"):
        assert f'fill="#{color}"' in svg
    assert 'x="0" y="0" width="33.3333" height="100"' in svg


def test_generate_entity_picture_multi_color_longitudinal() -> None:
    """Multi-color spools also support longitudinal bands."""
    spool = {
        "id": 8,
        "filament": {
            "multi_color_hexes": "FF0000,00FF00",
            "multi_color_direction": "longitudinal",
        },
    }
    svg = _svg(_generate_entity_picture(spool))
    assert 'x="0" y="50" width="100" height="50" fill="#00FF00"' in svg


def test_generate_entity_picture_no_color_returns_none() -> None:
    """A filament with no color information returns None and logs a warning."""
    spool = {"id": 9, "filament": {"color_hex": "", "multi_color_hexes": ""}}
    assert _generate_entity_picture(spool) is None


def test_generate_entity_picture_rejects_invalid_hex() -> None:
    """Values that are not hex colors never end up in the SVG."""
    spool = {"id": 13, "filament": {"color_hex": '"/><script>alert(1)</script>'}}
    assert _generate_entity_picture(spool) is None


def test_generate_entity_picture_invalid_multi_falls_back() -> None:
    """Invalid multi-color entries fall back to color_hex instead of crashing."""
    spool = {"id": 14, "filament": {"multi_color_hexes": "xyz", "color_hex": "123456"}}
    assert 'fill="#123456"' in _svg(_generate_entity_picture(spool))


def test_generate_filament_entity_picture_single_color() -> None:
    """Same routine for the per-filament image."""
    fil = {"id": 10, "color_hex": "FF6600"}
    assert 'fill="#FF6600"' in _svg(_generate_filament_entity_picture(fil))


def test_generate_filament_entity_picture_no_color() -> None:
    """No-color filament returns None."""
    fil = {"id": 11, "color_hex": "", "multi_color_hexes": ""}
    assert _generate_filament_entity_picture(fil) is None


def test_generate_filament_entity_picture_multi_longitudinal() -> None:
    """Filament longitudinal multi-color path."""
    fil = {
        "id": 12,
        "multi_color_hexes": "FF0000,00FF00",
        "multi_color_direction": "longitudinal",
    }
    assert 'fill="#FF0000"' in _svg(_generate_filament_entity_picture(fil))


def test_generate_filament_entity_picture_alpha_hexes() -> None:
    """Multi-color hexes with an alpha channel (RRGGBBAA) are accepted (#852)."""
    filament = {"id": 5, "multi_color_hexes": "FF6A13FF,00AA0080"}
    svg = _svg(_generate_filament_entity_picture(filament))
    assert 'fill="#FF6A13"' in svg
    assert 'fill="#00AA00"' in svg


def test_remove_legacy_images(tmp_path: Path) -> None:
    """Old PNGs are deleted and the folder goes away when it is empty."""
    image_dir = tmp_path / "spoolman_images"
    image_dir.mkdir()
    (image_dir / "spool_1.png").write_bytes(b"x")
    (image_dir / "filament_2.png").write_bytes(b"x")
    _remove_legacy_images(image_dir)
    assert not image_dir.exists()


def test_remove_legacy_images_keeps_foreign_files(tmp_path: Path) -> None:
    """Files the integration did not write are left alone."""
    image_dir = tmp_path / "spoolman_images"
    image_dir.mkdir()
    (image_dir / "spool_1.png").write_bytes(b"x")
    (image_dir / "mine.jpg").write_bytes(b"x")
    _remove_legacy_images(image_dir)
    assert not (image_dir / "spool_1.png").exists()
    assert (image_dir / "mine.jpg").exists()


def test_remove_legacy_images_missing_dir(tmp_path: Path) -> None:
    """A missing folder is not an error."""
    _remove_legacy_images(tmp_path / "does_not_exist")
