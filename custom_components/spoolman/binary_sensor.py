"""Spoolman home assistant binary sensor platform.

This module provides a binary sensor that indicates when a spool is running low
on filament based on the configured warning threshold.

The binary sensor uses the existing notification threshold configuration to
determine when to alert users about low filament levels.
"""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_NOTIFICATION_THRESHOLD_WARNING,
    CONF_URL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Spoolman binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    if coordinator.data:
        binary_sensors = []
        spool_data = coordinator.data.get("spools", [])

        for spool in spool_data:
            binary_sensor = SpoolLowFilament(
                hass, coordinator, spool, config_entry
            )
            binary_sensors.append(binary_sensor)

        async_add_entities(binary_sensors, True)


class SpoolLowFilament(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor that indicates when a spool is running low on filament."""

    def __init__(
        self, hass: HomeAssistant, coordinator, spool_data: dict, config_entry: ConfigEntry
    ) -> None:
        """Initialize the low filament binary sensor."""
        super().__init__(coordinator)

        self.config = hass.data[DOMAIN]
        self._spool = spool_data
        self.spool_id = spool_data['id']
        self._entry = config_entry
        self._attr_available = True

        # Get threshold from config (use notification_threshold_warning)
        self._threshold = config_entry.options.get(
            CONF_NOTIFICATION_THRESHOLD_WARNING,
            config_entry.data.get(CONF_NOTIFICATION_THRESHOLD_WARNING, 75)
        )

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
            "binary_sensor.{}",
            f"spoolman_spool_{spool_data['id']}_low_filament",
            hass=hass
        )
        self._attr_unique_id = f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}_low_filament"
        self._attr_has_entity_name = False
        self._attr_name = f"{spool_name} Low Filament"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM
        self._attr_icon = "mdi:alert-circle"

        # Set device info to match spool device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")},
        )

        # Initial state calculation
        self._calculate_state(self._spool)

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

        self._spool = spool_data
        self._attr_available = True
        self._calculate_state(spool_data)
        self.async_write_ha_state()

    def _calculate_state(self, spool_data) -> None:
        """Calculate the binary sensor state based on remaining filament."""
        # Calculate remaining percentage
        used_weight = spool_data.get("used_weight", 0)
        filament = spool_data.get("filament", {})
        filament_weight = filament.get("weight")

        if filament_weight and filament_weight > 0:
            remaining_percentage = ((filament_weight - used_weight) / filament_weight) * 100

            # Sensor is ON (problem) when remaining percentage is below threshold
            self._attr_is_on = remaining_percentage <= self._threshold

            # Add extra attributes for debugging/display
            self._attr_extra_state_attributes = {
                "remaining_percentage": round(remaining_percentage, 1),
                "threshold": self._threshold,
                "used_weight": used_weight,
                "total_weight": filament_weight,
            }
        else:
            # If we don't have weight data, sensor is off (no problem detected)
            self._attr_is_on = False
            self._attr_extra_state_attributes = {
                "error": "No filament weight data available"
            }

    @property
    def icon(self) -> str:
        """Return appropriate icon based on current sensor state.

        Returns mdi:alert-circle when low, mdi:check-circle when sufficient.
        """
        if self.is_on:
            return "mdi:alert-circle"
        return "mdi:check-circle"
