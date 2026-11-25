"""Test the Spoolman diagnostics platform — Platinum requirement."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.spoolman.diagnostics import (
    async_get_config_entry_diagnostics,
)

from .const import MOCK_URL


async def test_diagnostics_redacts_sensitive_keys(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """URL and Spoolman info must be redacted from diagnostics output."""
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)

    data = diag["config_entry"]["data"]
    # The MOCK_URL must NOT appear anywhere in the redacted dump:
    assert MOCK_URL not in str(data)
    # Redacted keys are replaced with "**REDACTED**":
    assert data["spoolman_url"] == "**REDACTED**"


async def test_diagnostics_includes_coordinator_state(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """Coordinator state (success flag, data) is exposed for debugging."""
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)

    coord = diag["coordinator"]
    assert coord["last_update_success"] is True
    assert "spools" in coord["data"]
    assert "filaments" in coord["data"]


async def test_diagnostics_options_passthrough(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """Options (currently empty) are present and not redacted."""
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    assert isinstance(diag["config_entry"]["options"], dict)


async def test_diagnostics_handles_no_update_interval(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """update_interval is exposed as seconds (or None when not set)."""
    diag = await async_get_config_entry_diagnostics(hass, setup_integration)
    interval: Any = diag["coordinator"]["update_interval"]
    # Default config sets 5 minutes → 300 seconds:
    assert interval == 300
