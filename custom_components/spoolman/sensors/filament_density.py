"""Sensor class: FilamentDensity."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import CONF_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

class FilamentDensity(CoordinatorEntity, SensorEntity):
    """Sensor for filament density."""

    def __init__(self, hass, coordinator, spool_data, config_entry) -> None:
        super().__init__(coordinator)
        self.config = hass.data[DOMAIN]
        self._spool = spool_data
        self.spool_id = spool_data['id']
        self._entry = config_entry
        self._attr_available = True

        filament = self._spool.get("filament", {})
        vendor_name = filament.get("vendor", {}).get("name")
        if filament.get("name") and filament.get("material"):
            spool_name = f"{vendor_name} {filament['name']} {filament.get('material')}" if vendor_name else f"{filament['name']} {filament.get('material')}"
        else:
            spool_name = f"Spoolman Spool {self._spool['id']}"

        self.entity_id = generate_entity_id("sensor.{}", f"spoolman_spool_{spool_data['id']}_density", hass=hass)
        self._attr_unique_id = f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}_density"
        self._attr_has_entity_name = False
        self._attr_name = f"{spool_name} Density"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "g/cm³"
        self._attr_icon = "mdi:chart-bell-curve"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")})

    @callback
    def _handle_coordinator_update(self) -> None:
        spool_data = next((s for s in self.coordinator.data.get("spools", []) if s["id"] == self.spool_id), None)
        if spool_data is None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._spool = spool_data
        self.async_write_ha_state()

    @property
    def state(self):
        filament = self._spool.get("filament", {})
        return filament.get("density")

    async def async_update(self):
        await self.coordinator.async_request_refresh()
