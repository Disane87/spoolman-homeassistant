"""Diagnostics support for the Spoolman integration.

Implements the Home Assistant ``diagnostics`` platform so users can attach a
sanitized snapshot of their integration state to bug reports without leaking
URLs, API keys, or other sensitive information.

Platinum quality scale rule: ``diagnostics``.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_URL,
    DOMAIN,
    KLIPPER_URL,
    SPOOLMAN_INFO_PROPERTY,
)

# Keys removed from the diagnostics dump to avoid leaking sensitive info
# in shared bug reports.
TO_REDACT = {CONF_URL, KLIPPER_URL, SPOOLMAN_INFO_PROPERTY}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a Spoolman config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]

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
