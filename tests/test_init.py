"""Test setup/unload of the Spoolman integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_setup_and_unload(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """The integration sets up cleanly and unloads cleanly."""
    entry = setup_integration
    assert entry.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_creates_entities(
    hass: HomeAssistant, setup_integration: Any
) -> None:
    """At least the two non-archived spools produce entities."""
    states = hass.states.async_all()
    spool_1_states = [s for s in states if "spoolman_spool_1" in s.entity_id]
    spool_2_states = [s for s in states if "spoolman_spool_2" in s.entity_id]
    assert spool_1_states, "expected entities for spool 1 to be present"
    assert spool_2_states, "expected entities for spool 2 to be present"
