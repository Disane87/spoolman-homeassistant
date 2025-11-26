"""Sensor class: SpoolFlowRate."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
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

class SpoolFlowRate(CoordinatorEntity, SensorEntity):
    """Representation of a Spoolman Spool Flow Rate Sensor."""

    def __init__(
        self, hass, coordinator, spool_data, config_entry
    ) -> None:
        """Initialize the flow rate sensor."""
        super().__init__(coordinator)

        self.config = hass.data[DOMAIN]
        self._spool = spool_data
        self.spool_id = spool_data['id']
        self._entry = config_entry
        self._attr_available = True
        self._previous_weight = None
        self._previous_timestamp = None
        self._flow_rate = 0.0

        # Set initial name
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
            f"spoolman_spool_{spool_data['id']}_flow_rate",
            hass=hass
        )
        self._attr_unique_id = f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}_flow_rate"
        self._attr_has_entity_name = False
        self._attr_name = f"{spool_name} Flow Rate"
        self._attr_device_class = None
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "g/h"
        self._attr_icon = "mdi:speedometer"

        # Set device info to match spool device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")},
        )

        # Initialize with current weight and timestamp
        self._previous_weight = self._spool.get("remaining_weight", 0)
        from datetime import datetime
        self._previous_timestamp = datetime.now()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        from datetime import datetime

        # Use ID-based lookup
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

        # Calculate flow rate
        current_weight = self._spool.get("remaining_weight", 0)
        current_timestamp = datetime.now()

        if self._previous_weight is not None and self._previous_timestamp is not None and current_weight != self._previous_weight:
            # Calculate time difference in hours
            time_diff = (current_timestamp - self._previous_timestamp).total_seconds() / 3600

            if time_diff > 0:
                # Calculate weight difference (positive means material used)
                weight_diff = self._previous_weight - current_weight

                # Calculate flow rate (g/h)
                self._flow_rate = weight_diff / time_diff

                _LOGGER.debug(
                    "Spool %s: Flow rate calculated: %.2f g/h (weight change: %.2f g over %.2f hours)",
                    self.spool_id,
                    self._flow_rate,
                    weight_diff,
                    time_diff
                )

                # Update previous values only when weight changed
                self._previous_weight = current_weight
                self._previous_timestamp = current_timestamp
        elif self._previous_weight is None:
            # First run, initialize
            self._previous_weight = current_weight
            self._previous_timestamp = current_timestamp

        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "spool_id": self.spool_id,
            "previous_weight": self._previous_weight,
            "current_weight": self._spool.get("remaining_weight", 0),
            "last_update": self._previous_timestamp.isoformat() if self._previous_timestamp else None,
        }

    @property
    def state(self):
        """Return the flow rate."""
        # Return 0 if flow rate is negative (weight increased - shouldn't happen normally)
        return round(max(0, self._flow_rate), 2)

    async def async_update(self):
        """Fetch the latest data from the coordinator."""
        await self.coordinator.async_request_refresh()
