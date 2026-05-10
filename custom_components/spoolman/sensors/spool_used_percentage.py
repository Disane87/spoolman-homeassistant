"""Sensor class: SpoolUsedPercentage."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import CONF_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:printer-3d-nozzle"


class SpoolUsedPercentage(CoordinatorEntity[Any], SensorEntity):
    """Sensor for spool used percentage."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: Any,
        spool_data: dict[str, Any],
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the used percentage sensor."""
        super().__init__(coordinator)

        self.config = hass.data[DOMAIN]
        self._spool = spool_data
        self.spool_id = spool_data["id"]
        self._entry = config_entry
        self._attr_available = True

        # Get spool name
        filament = self._spool.get("filament", {})
        vendor_name = filament.get("vendor", {}).get("name")

        if filament.get("name") and filament.get("material"):
            if vendor_name:
                spool_name = (
                    f"{vendor_name} {filament['name']} {filament.get('material')}"
                )
            else:
                spool_name = f"{filament['name']} {filament.get('material')}"
        else:
            spool_name = f"Spoolman Spool {self._spool['id']}"

        self.entity_id = generate_entity_id(
            "sensor.{}", f"spoolman_spool_{spool_data['id']}_used_percentage", hass=hass
        )
        self._attr_unique_id = (
            f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}_used_percentage"
        )
        self._attr_has_entity_name = False
        self._attr_name = f"{spool_name} Used Percentage"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "%"
        self._attr_icon = "mdi:percent"

        # Set device info to match spool device
        self._attr_device_info = DeviceInfo(
            identifiers={
                (DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")  # type: ignore[arg-type]
            },
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
            _LOGGER.warning(
                "SpoolManCoordinator: Spool with ID '%s' not found in coordinator data. Marking as unavailable.",
                self.spool_id,
            )
            self._attr_available = False
            self.async_write_ha_state()
            return

        self._attr_available = True
        self._spool = spool_data

        # Calculate used percentage
        filament = spool_data.get("filament", {})
        if filament.get("weight") and spool_data.get("used_weight") is not None:
            self._spool["used_percentage"] = round(
                (spool_data["used_weight"] / filament["weight"]) * 100, 1
            )
        else:
            self._spool["used_percentage"] = 0

        self.async_write_ha_state()

    @property  # type: ignore[misc]
    def state(self) -> float | int:
        """Return the used percentage.

        Type kept as ``float | int`` to preserve byte-stable snapshot
        output: integer 0 default vs. rounded float for the calculated
        percentage.
        """
        value = self._spool.get("used_percentage", 0)
        return value if isinstance(value, int | float) else 0

    async def async_update(self) -> None:
        """Fetch the latest data from the coordinator."""
        await self.coordinator.async_request_refresh()
