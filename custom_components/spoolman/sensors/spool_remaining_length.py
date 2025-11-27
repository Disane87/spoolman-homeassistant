"""Sensor class: SpoolRemainingLength."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import (
    CONF_URL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:printer-3d-nozzle"

class SpoolRemainingLength(CoordinatorEntity, SensorEntity):
    """Sensor for spool remaining length - reduces state attributes on main sensor."""

    def __init__(
        self, hass, coordinator, spool_data, config_entry
    ) -> None:
        """Initialize the remaining length sensor."""
        super().__init__(coordinator)

        self.config = hass.data[DOMAIN]
        self._spool = spool_data
        self.spool_id = spool_data['id']
        self._entry = config_entry
        self._attr_available = True

        # Get spool name
        filament = self._spool.get("filament", {})
        vendor_name = filament.get("vendor", {}).get("name")

        if filament.get("name") and filament.get("material"):
            if vendor_name:
                spool_name = f"{vendor_name} {filament['name']} {filament.get('material')}"
            else:
                spool_name = f"{filament['name']} {filament.get('material')}"
        else:
            spool_name = f"Spoolman Spool {self._spool['id']}"

        self.entity_id = generate_entity_id(
            "sensor.{}",
            f"spoolman_spool_{spool_data['id']}_remaining_length",
            hass=hass
        )
        self._attr_unique_id = f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}_remaining_length"
        self._attr_has_entity_name = False
        self._attr_name = f"{spool_name} Remaining Length"
        self._attr_device_class = SensorDeviceClass.DISTANCE
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "mm"
        self._attr_icon = "mdi:tape-measure"

        # Set device info to match spool device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")},
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        spool_data = next(
            (s for s in self.coordinator.data.get("spools", []) if s["id"] == self.spool_id),
            None
        )

        if spool_data is None:
            _LOGGER.warning(
                "SpoolManCoordinator: Spool with ID '%s' not found in coordinator data. Marking as unavailable.",
                self.spool_id,
            )
            self._attr_available = False
            self.async_write_ha_state()
            return

        self._attr_available = True
        self._spool = spool_data
        self.async_write_ha_state()

    @property
    def state(self):
        """Return the remaining length in mm."""
        return round(self._spool.get("remaining_length", 0), 2)

    async def async_update(self):
        """Fetch the latest data from the coordinator."""
        await self.coordinator.async_request_refresh()
