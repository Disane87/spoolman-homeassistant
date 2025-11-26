"""Base sensor classes for Spoolman integration."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import CONF_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SpoolBaseSensor(CoordinatorEntity):
    """Base class for spool sensors."""

    def __init__(self, hass: HomeAssistant, coordinator, spool_data: dict, config_entry) -> None:
        """Initialize the base sensor."""
        super().__init__(coordinator)
        self.config = hass.data[DOMAIN]
        self._spool = spool_data
        self.spool_id = spool_data['id']
        self._entry = config_entry
        self._attr_available = True

        # Generate spool name
        filament = self._spool.get("filament", {})
        vendor_name = filament.get("vendor", {}).get("name")
        if filament.get("name") and filament.get("material"):
            spool_name = f"{vendor_name} {filament['name']} {filament.get('material')}" if vendor_name else f"{filament['name']} {filament.get('material')}"
        else:
            spool_name = f"Spoolman Spool {self._spool['id']}"

        self._spool_name = spool_name

    def _generate_entity_id(self, hass: HomeAssistant, sensor_suffix: str) -> str:
        """Generate entity ID for the sensor."""
        return generate_entity_id("sensor.{}", f"spoolman_spool_{self.spool_id}_{sensor_suffix}", hass=hass)

    def _get_device_info(self) -> DeviceInfo:
        """Get device info for the spool."""
        return DeviceInfo(identifiers={(DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")})

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        spool_data = next((s for s in self.coordinator.data.get("spools", []) if s["id"] == self.spool_id), None)
        if spool_data is None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._spool = spool_data
        self.async_write_ha_state()

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()
