"""Diagnostics support for the Spoolman integration.

Implements the Home Assistant ``diagnostics`` platform so users can attach a
sanitized snapshot of their integration state to bug reports without leaking
URLs, API keys, or other sensitive information.

Platinum quality scale rule: ``diagnostics``.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import CONF_URL, KLIPPER_URL, SPOOLMAN_INFO_PROPERTY
from .coordinator import SpoolmanConfigEntry

# Keys removed from the diagnostics dump to avoid leaking sensitive info
# in shared bug reports.
TO_REDACT = {CONF_URL, KLIPPER_URL, SPOOLMAN_INFO_PROPERTY}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: SpoolmanConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a Spoolman config entry.

    Reads the coordinator from ``entry.runtime_data`` (Platinum rule
    ``runtime-data``).
    """
    coordinator = entry.runtime_data.coordinator

    return {
        "config_entry": {
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": dict(entry.options),
            "title": entry.title,
            "version": entry.version,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": (
                coordinator.update_interval.total_seconds()
                if coordinator.update_interval
                else None
            ),
            "data": coordinator.data,
        },
    }
