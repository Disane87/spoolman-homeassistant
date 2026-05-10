"""Tests for the Spoolman low-filament binary sensor."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry


async def test_low_filament_on_when_below_threshold(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """Spool 1 has 75% remaining, threshold is 75 → on (problem)."""
    state = hass.states.get("binary_sensor.spoolman_spool_1_low_filament")
    assert state is not None
    assert state.state == "on"
    assert state.attributes["remaining_percentage"] == 75.0
    assert state.attributes["threshold"] == 75


async def test_low_filament_off_when_no_weight_data(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """Spool 2 has no filament weight → off, error attribute set."""
    state = hass.states.get("binary_sensor.spoolman_spool_2_low_filament")
    assert state is not None
    assert state.state == "off"
    assert "error" in state.attributes
