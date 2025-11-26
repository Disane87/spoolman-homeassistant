"""Sensor class: SpoolEstimatedRunOut."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
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

class SpoolEstimatedRunOut(CoordinatorEntity, SensorEntity):
    """Representation of a Spoolman Spool Estimated Run Out Sensor."""

    def __init__(
        self, hass, coordinator, spool_data, config_entry
    ) -> None:
        """Initialize the estimated run out sensor."""
        super().__init__(coordinator)

        self.config = hass.data[DOMAIN]
        self._spool = spool_data
        self.spool_id = spool_data['id']
        self._entry = config_entry
        self._attr_available = True
        self._flow_rate_entity_id = f"sensor.spoolman_spool_{spool_data['id']}_flow_rate"

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
            f"spoolman_spool_{spool_data['id']}_estimated_runout",
            hass=hass
        )
        self._attr_unique_id = f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}_estimated_runout"
        self._attr_has_entity_name = False
        self._attr_name = f"{spool_name} Estimated Run Out"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-alert-outline"

        # Set device info to match spool device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")},
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

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

        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""

        remaining_weight = self._spool.get("remaining_weight", 0)

        # Get flow rate from the flow rate sensor entity
        flow_rate_state = self.hass.states.get(self._flow_rate_entity_id)
        flow_rate = 0.0

        if flow_rate_state and flow_rate_state.state not in ['unknown', 'unavailable', None]:
            try:
                flow_rate = float(flow_rate_state.state)
            except (ValueError, TypeError):
                flow_rate = 0.0

        hours_remaining = None
        days_remaining = None

        if flow_rate > 0 and remaining_weight > 0:
            hours_remaining = remaining_weight / flow_rate
            days_remaining = hours_remaining / 24

        return {
            "spool_id": self.spool_id,
            "remaining_weight": remaining_weight,
            "flow_rate": flow_rate,
            "hours_remaining": round(hours_remaining, 2) if hours_remaining is not None else None,
            "days_remaining": round(days_remaining, 2) if days_remaining is not None else None,
        }

    @property
    def state(self):
        """Return the estimated run out timestamp."""
        from datetime import datetime, timedelta

        remaining_weight = self._spool.get("remaining_weight", 0)

        # Get flow rate from the flow rate sensor entity
        flow_rate_state = self.hass.states.get(self._flow_rate_entity_id)
        flow_rate = 0.0

        if flow_rate_state and flow_rate_state.state not in ['unknown', 'unavailable', None]:
            try:
                flow_rate = float(flow_rate_state.state)
            except (ValueError, TypeError):
                flow_rate = 0.0

        # Calculate estimated run out time
        if flow_rate > 0 and remaining_weight > 0:
            hours_remaining = remaining_weight / flow_rate
            estimated_runout = datetime.now() + timedelta(hours=hours_remaining)
            return estimated_runout.isoformat()

        # Return None if we can't calculate (no flow rate or no material left)
        return None

    async def async_update(self):
        """Fetch the latest data from the coordinator."""
        await self.coordinator.async_request_refresh()
