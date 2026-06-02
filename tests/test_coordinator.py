"""SpoolManCoordinator behavior — happy path, failures, graceful degradation."""

from __future__ import annotations

import re
from typing import Any

from aioresponses import aioresponses
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.spoolman.coordinator import SpoolManCoordinator

from .const import MOCK_URL


async def test_update_happy_path(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_spoolman_api: aioresponses,
) -> None:
    """Happy path returns the expected shape — archived spools filtered."""
    config_entry.add_to_hass(hass)
    coord = SpoolManCoordinator(hass, config_entry)
    await coord.async_refresh()

    assert coord.last_update_success
    assert coord.data is not None
    # Archived spool 3 is filtered when CONF_SHOW_ARCHIVED is False:
    assert {s["id"] for s in coord.data["spools"]} == {1, 2}
    assert coord.data["filaments"]
    assert coord.data["locations"]


async def test_update_failure_marks_unsuccessful(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    """If the spool endpoint 500s, the coordinator marks the update failed."""
    config_entry.add_to_hass(hass)
    with aioresponses() as m:
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool.*"),
            status=500,
            repeat=True,
        )
        coord = SpoolManCoordinator(hass, config_entry)
        await coord.async_refresh()

    assert not coord.last_update_success


async def test_extra_fields_endpoint_404_degrades(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    spools_data: list[dict[str, Any]],
    filaments_data: list[dict[str, Any]],
    locations_data: list[str],
) -> None:
    """Older Spoolman without /field/spool: integration still works."""
    config_entry.add_to_hass(hass)
    with aioresponses() as m:
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool.*"),
            payload=[s for s in spools_data if not s.get("archived")],
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/filament.*"),
            payload=filaments_data,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/setting/locations.*"),
            status=404,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/location.*"),
            payload=locations_data,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/field/spool.*"),
            status=404,
            repeat=True,
        )
        coord = SpoolManCoordinator(hass, config_entry)
        await coord.async_refresh()

    assert coord.last_update_success
    assert coord.data["extra_fields"]["spool"] == {}


async def test_locations_fallback_to_derived(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    spools_data: list[dict[str, Any]],
    filaments_data: list[dict[str, Any]],
) -> None:
    """Neither /setting/locations nor /location → derive from spool.location."""
    config_entry.add_to_hass(hass)
    with aioresponses() as m:
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool.*"),
            payload=[s for s in spools_data if not s.get("archived")],
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/filament.*"),
            payload=filaments_data,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/setting/locations.*"),
            status=404,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/location.*"),
            status=404,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/field/spool.*"),
            payload=[],
            repeat=True,
        )
        coord = SpoolManCoordinator(hass, config_entry)
        await coord.async_refresh()

    assert coord.last_update_success
    # Derived from spool fixture: "Shelf A" + "Shelf B" (alphabetical):
    assert set(coord.data["locations"]) == {"Shelf A", "Shelf B"}


async def test_locations_merge_setting_and_spool(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_spoolman_api: aioresponses,
) -> None:
    """#854: empty Locations-page entries are merged with spool-referenced ones."""
    config_entry.add_to_hass(hass)
    coord = SpoolManCoordinator(hass, config_entry)
    await coord.async_refresh()

    assert coord.last_update_success
    locations = set(coord.data["locations"])
    # Empty locations only present in /setting/locations (the bug in #854):
    assert {"External Spool Holder", "Ordered"} <= locations
    # ...merged with the /location feed ("Drawer 1") and spool-derived ones:
    assert {"Shelf A", "Shelf B", "Drawer 1"} <= locations


async def test_setting_locations_404_falls_back_to_location(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    spools_data: list[dict[str, Any]],
    filaments_data: list[dict[str, Any]],
    locations_data: list[str],
) -> None:
    """Older Spoolman without /setting/locations still uses the /location feed."""
    config_entry.add_to_hass(hass)
    with aioresponses() as m:
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool.*"),
            payload=[s for s in spools_data if not s.get("archived")],
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/filament.*"),
            payload=filaments_data,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/setting/locations.*"),
            status=404,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/location.*"),
            payload=locations_data,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/field/spool.*"),
            payload=[],
            repeat=True,
        )
        coord = SpoolManCoordinator(hass, config_entry)
        await coord.async_refresh()

    assert coord.last_update_success
    assert set(coord.data["locations"]) == {"Shelf A", "Shelf B", "Drawer 1"}


async def test_setting_locations_malformed_value_degrades(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    spools_data: list[dict[str, Any]],
    filaments_data: list[dict[str, Any]],
    locations_data: list[str],
) -> None:
    """A malformed Setting value doesn't crash; /location still contributes."""
    config_entry.add_to_hass(hass)
    with aioresponses() as m:
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool.*"),
            payload=[s for s in spools_data if not s.get("archived")],
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/filament.*"),
            payload=filaments_data,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/setting/locations.*"),
            payload={"value": "{not valid json", "is_set": True},
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/location.*"),
            payload=locations_data,
            repeat=True,
        )
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/field/spool.*"),
            payload=[],
            repeat=True,
        )
        coord = SpoolManCoordinator(hass, config_entry)
        await coord.async_refresh()

    assert coord.last_update_success
    assert set(coord.data["locations"]) == {"Shelf A", "Shelf B", "Drawer 1"}


async def test_total_remaining_weight_calculated(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_spoolman_api: aioresponses,
) -> None:
    """Filaments get a total_remaining_weight aggregated across non-archived spools."""
    config_entry.add_to_hass(hass)
    coord = SpoolManCoordinator(hass, config_entry)
    await coord.async_refresh()

    by_id = {f["id"]: f for f in coord.data["filaments"]}
    # Filament 10 used by spool 1 (remaining_weight=750):
    assert by_id[10]["total_remaining_weight"] == 750
    # Filament 11 used by spool 2 (remaining_weight=1000):
    assert by_id[11]["total_remaining_weight"] == 1000
    # Filament 12 only on archived spool 3 — should be 0:
    assert by_id[12]["total_remaining_weight"] == 0
