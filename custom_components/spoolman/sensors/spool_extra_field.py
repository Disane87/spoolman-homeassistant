"""Sensor class: SpoolExtraField - Dynamic sensors for custom extra fields."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import CONF_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SpoolExtraField(CoordinatorEntity, SensorEntity):
    """Sensor for spool extra field - dynamically created for each extra field."""

    def __init__(
        self, hass, coordinator, spool_data, config_entry, field_key: str
    ) -> None:
        """Initialize the extra field sensor."""
        super().__init__(coordinator)
        self.config = hass.data[DOMAIN]
        self._spool = spool_data
        self.spool_id = spool_data["id"]
        self._entry = config_entry
        self._field_key = field_key
        self._attr_available = True

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

        # Create entity ID with the field key
        # e.g., sensor.spoolman_spool_1_extra_humidity
        safe_field_key = field_key.lower().replace(" ", "_").replace("-", "_")
        self.entity_id = generate_entity_id(
            "sensor.{}",
            f"spoolman_spool_{spool_data['id']}_extra_{safe_field_key}",
            hass=hass,
        )
        self._attr_unique_id = f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}_extra_{safe_field_key}"
        self._attr_has_entity_name = False
        self._attr_name = f"{spool_name} Extra {field_key.replace('_', ' ').title()}"
        self._attr_icon = "mdi:tag-outline"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")}  # type: ignore[arg-type]
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
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
            # Check if the extra field still exists
            extra_data = spool_data.get("extra", {})
            if self._field_key not in extra_data:
                # Field was removed, mark as unavailable
                self._attr_available = False
            else:
                self._attr_available = True
                self._spool = spool_data
        self.async_write_ha_state()

    @property
    def state(self) -> Any:
        """Return the state of the extra field."""
        extra_data = self._spool.get("extra", {})
        value = extra_data.get(self._field_key)

        # Convert value to string if it's a complex type
        if isinstance(value, dict | list):
            import json
            return json.dumps(value)

        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "field_key": self._field_key,
            "spool_id": self.spool_id,
        }

    async def async_update(self):
        """Fetch the latest data from the coordinator."""
        await self.coordinator.async_request_refresh()
