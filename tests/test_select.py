"""Tests for the Spoolman location select platform."""

from __future__ import annotations

import re

from aioresponses import aioresponses
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_URL


async def test_select_options_listed(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """The select entity exposes the locations from the coordinator."""
    state = hass.states.get("select.spoolman_spool_1_location")
    assert state is not None
    assert state.state == "Shelf A"
    assert "Drawer 1" in state.attributes["options"]


async def test_select_change_dispatches_patch(
    hass: HomeAssistant,
    setup_integration: MockConfigEntry,
    mock_spoolman_api: aioresponses,
) -> None:
    """Selecting a different location calls patch_spool with location=<new>."""
    mock_spoolman_api.patch(
        re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool/1.*"),
        payload={"id": 1, "location": "Drawer 1"},
        repeat=True,
    )

    await hass.services.async_call(
        "select",
        "select_option",
        {ATTR_ENTITY_ID: "select.spoolman_spool_1_location", "option": "Drawer 1"},
        blocking=True,
    )
    await hass.async_block_till_done()

    matched = [k for k in mock_spoolman_api.requests if "api/v1/spool/1" in str(k[1])]
    assert matched
