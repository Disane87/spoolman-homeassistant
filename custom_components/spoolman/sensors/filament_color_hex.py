"""Sensor class: FilamentColorHex."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import CONF_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class FilamentColorHex(CoordinatorEntity[Any], SensorEntity):
    """Sensor for filament color hex code, with the swatch as entity picture."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: Any,
        spool_data: dict[str, Any],
        config_entry: ConfigEntry,
        image_url: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.config = hass.data[DOMAIN]
        self._spool = spool_data
        self.spool_id = spool_data["id"]
        self._entry = config_entry
        self._attr_available = True
        self._attr_entity_picture = image_url

        filament = self._spool.get("filament", {})
        vendor_name = filament.get("vendor", {}).get("name")
        if filament.get("name") and filament.get("material"):
            spool_name = (
                f"{vendor_name} {filament['name']} {filament.get('material')}"
                if vendor_name
                else f"{filament['name']} {filament.get('material')}"
            )
        else:
            spool_name = f"Spoolman Spool {self._spool['id']}"

        self.entity_id = generate_entity_id(
            "sensor.{}", f"spoolman_spool_{spool_data['id']}_color_hex", hass=hass
        )
        self._attr_unique_id = (
            f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}_color_hex"
        )
        self._attr_has_entity_name = False
        self._attr_name = f"{spool_name} Color Hex"
        self._attr_icon = "mdi:palette"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")  # type: ignore[arg-type]
            }
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Refresh ``self._spool`` from the coordinator."""
        spool_data = next(
            (
                s
                for s in self.coordinator.data.get("spools", [])
                if s["id"] == self.spool_id
            ),
            None,
        )
        if spool_data is None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._spool = spool_data
        self.async_write_ha_state()

    @property  # type: ignore[misc]
    def state(self) -> str | None:
        """Return the filament color hex code.

        Overrides ``state`` rather than ``native_value`` so the legacy
        snapshot output (raw hex string) stays byte-stable.
        """
        filament = self._spool.get("filament", {})
        value: str | None = filament.get("color_hex")
        return value

    async def async_update(self) -> None:
        """Force a coordinator refresh."""
        await self.coordinator.async_request_refresh()
