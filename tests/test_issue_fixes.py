"""Regression tests for #850, #887, #888, #898 and #901."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.spoolman.const import CONF_CREATE_AREAS, DOMAIN

from .const import MOCK_CONFIG_DATA


def _push(hass: HomeAssistant, spools: list[dict], filaments, locations) -> None:
    hass.data[DOMAIN]["coordinator"].async_set_updated_data(
        {
            "spools": spools,
            "filaments": filaments,
            "locations": locations,
            "extra_fields": {"spool": []},
        }
    )


async def test_remaining_weight_updates_without_filament_weight(
    hass: HomeAssistant,
    setup_integration: MockConfigEntry,
    spools_data: list[dict],
    filaments_data: list[dict],
    locations_data: list[str],
) -> None:
    """#850: main spool sensor refreshes even if the filament has no weight."""
    spools = [
        {**s, "filament": {**s["filament"]}}
        for s in spools_data
        if not s.get("archived")
    ]
    spools[0]["filament"].pop("weight", None)
    spools[0]["remaining_weight"] = 123.0
    _push(hass, spools, filaments_data, locations_data)
    await hass.async_block_till_done()

    state = hass.states.get(f"sensor.spoolman_spool_{spools[0]['id']}")
    assert state is not None
    assert float(state.state) == 123.0


async def test_length_sensor_honours_unit_conversion(
    hass: HomeAssistant,
    setup_integration: MockConfigEntry,
    spools_data: list[dict],
) -> None:
    """#898: changing the display unit converts the value, not just the label."""
    spool = next(s for s in spools_data if not s.get("archived"))
    entity_id = f"sensor.spoolman_spool_{spool['id']}_remaining_length"
    raw_mm = float(hass.states.get(entity_id).state)

    er.async_get(hass).async_update_entity_options(
        entity_id, "sensor", {"unit_of_measurement": "m"}
    )
    await hass.async_block_till_done()

    state = hass.states.get(entity_id)
    assert state.attributes["unit_of_measurement"] == "m"
    assert abs(float(state.state) - raw_mm / 1000) < 0.01


async def test_spool_device_linked_via_device_id(
    hass: HomeAssistant,
    setup_integration: MockConfigEntry,
    spools_data: list[dict],
) -> None:
    """#887: spool devices hang off their location hub via via_device_id."""
    spool = next(s for s in spools_data if not s.get("archived"))
    registry = dr.async_get(hass)
    devices = dr.async_entries_for_config_entry(registry, setup_integration.entry_id)
    spool_device = next(
        d
        for d in devices
        if any(i[-1] == f"spool_{spool['id']}" for i in d.identifiers)
    )
    hub = registry.async_get(spool_device.via_device_id)
    assert hub is not None
    assert any(i[-1] == f"location_{spool['location']}" for i in hub.identifiers)


async def test_filament_spool_count(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """#888: filament sensors expose spool_count for the README card."""
    states = [
        s
        for s in hass.states.async_all("sensor")
        if s.entity_id.startswith("sensor.spoolman_filament_")
        and "spool_count" in s.attributes
    ]
    assert states
    assert all(isinstance(s.attributes["spool_count"], int) for s in states)


async def test_create_areas_disabled(
    hass: HomeAssistant,
    mock_spoolman_api,
) -> None:
    """#901: with create_areas off, no areas are created from locations."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={**MOCK_CONFIG_DATA, CONF_CREATE_AREAS: False},
        entry_id="no_areas",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert dr.async_entries_for_config_entry(dr.async_get(hass), entry.entry_id)
    assert not list(ar.async_get(hass).async_list_areas())
