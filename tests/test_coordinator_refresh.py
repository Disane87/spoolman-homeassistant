"""End-to-end test: coordinator refresh propagates state changes to entities.

This single test exercises ``_handle_coordinator_update`` on every entity
type (sensors, binary sensors, select), the description-driven
``SpoolmanSensor.state`` recompute, and the dynamic-add path.
"""

from __future__ import annotations

import re

from aioresponses import aioresponses
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_URL


async def test_coordinator_refresh_propagates(
    hass: HomeAssistant,
    setup_integration: MockConfigEntry,
    mock_spoolman_api: aioresponses,
    spools_data: list[dict],
    filaments_data: list[dict],
    locations_data: list[str],
    extra_fields_data: list[dict],
) -> None:
    """After a refresh with mutated spool data, sensor states reflect the change."""
    # Bump used_weight on spool 1 from 250 → 500.
    mutated = [{**s} for s in spools_data]
    mutated[0]["used_weight"] = 500
    mutated[0]["remaining_weight"] = 500

    coordinator = hass.data["spoolman"]["coordinator"]
    coordinator.async_set_updated_data(
        {
            "spools": [s for s in mutated if not s.get("archived")],
            "filaments": filaments_data,
            "locations": locations_data,
            "extra_fields": {"spool": []},
        }
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.spoolman_spool_1_used_weight")
    assert state is not None
    assert float(state.state) == 500


async def test_dynamic_new_spool_added(
    hass: HomeAssistant,
    setup_integration: MockConfigEntry,
    spools_data: list[dict],
    filaments_data: list[dict],
    locations_data: list[str],
) -> None:
    """A spool that appears mid-session spawns its full sensor stack (#327)."""
    coordinator = hass.data["spoolman"]["coordinator"]
    new_spool = {
        "id": 99,
        "filament": {
            "id": 99,
            "name": "New PLA",
            "material": "PLA",
            "color_hex": "AABBCC",
            "vendor": {"name": "TestCo"},
        },
        "remaining_weight": 800,
        "used_weight": 200,
        "remaining_length": 250,
        "used_length": 50,
        "location": "Shelf A",
        "archived": False,
        "extra": {},
    }
    coordinator.async_set_updated_data(
        {
            "spools": [
                *(s for s in spools_data if not s.get("archived")),
                new_spool,
            ],
            "filaments": filaments_data,
            "locations": locations_data,
            "extra_fields": {"spool": []},
        }
    )
    await hass.async_block_till_done()

    state = hass.states.get("sensor.spoolman_spool_99_used_weight")
    assert state is not None


async def test_use_spool_filament_propagates_http_error(
    hass: HomeAssistant,
    setup_integration: MockConfigEntry,
    mock_spoolman_api: aioresponses,
) -> None:
    """API 500 surfaces as HomeAssistantError to automations."""
    from homeassistant.exceptions import HomeAssistantError

    import pytest

    mock_spoolman_api.put(
        re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool/1/use.*"),
        status=500,
        repeat=True,
    )

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            "spoolman",
            "use_spool_filament",
            {"id": 1, "use_length": 50},
            blocking=True,
        )
