"""Sensor class: Filament."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import CONF_URL, DOMAIN, SPOOLMAN_INFO_PROPERTY

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:printer-3d-nozzle"


class Filament(CoordinatorEntity[Any], SensorEntity):
    """Representation of a Spoolman Filament Sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: Any,
        filament_data: dict[str, Any],
        idx: int,
        config_entry: ConfigEntry,
        image_url: str | None,
    ) -> None:
        """Spoolman home assistant filament sensor init."""
        super().__init__(coordinator)

        self.config = hass.data[DOMAIN]

        self._filament = filament_data
        self.filament_id = filament_data["id"]  # Store ID instead of index
        self._attr_entity_picture = image_url
        self._attr_available = True

        self.assign_name_and_location()

        self._entry = config_entry
        self.entity_id = generate_entity_id(
            "sensor.{}", f"spoolman_filament_{filament_data['id']}", hass=hass
        )
        self._attr_unique_id = (
            f"spoolman_{self._entry.entry_id}_filament_{filament_data['id']}"
        )
        self._attr_has_entity_name = False
        self._attr_device_class = SensorDeviceClass.WEIGHT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfMass.GRAMS
        self._attr_icon = ICON
        self.idx = idx  # Keep for backwards compatibility, but don't use for lookups

    def assign_name_and_location(self) -> None:
        """Update sensor name and device (location)."""

        vendor_name = self._filament.get("vendor", {}).get("name")

        if self._filament.get("name") is None or self._filament.get("material") is None:
            filament_name = f"Spoolman Filament {self._filament['id']}"
            _LOGGER.warning(
                "SpoolManCoordinator: Filament with ID '%s' has no 'name' or 'material' set. Using default name.",
                self._filament["id"],
            )
        elif vendor_name is None:
            filament_name = f"{self._filament['name']} {self._filament.get('material')}"
            _LOGGER.warning(
                "SpoolManCoordinator: Filament with ID '%s' has no 'vendor' set. Using default name.",
                self._filament["id"],
            )
        else:
            filament_name = f"{vendor_name} {self._filament['name']} {self._filament.get('material')}"
            _LOGGER.debug(
                "SpoolManCoordinator: Filament with ID '%s' has 'vendor' set. Using vendor name.",
                self._filament["id"],
            )

        location_name = "Filaments"
        spoolman_info = self.config[SPOOLMAN_INFO_PROPERTY]
        device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config[CONF_URL], location_name)},  # type: ignore
            name=location_name,
            manufacturer="https://github.com/Donkie/Spoolman",
            model="Spoolman",
            configuration_url=self.config[CONF_URL],
            suggested_area=location_name,
            sw_version=f"{spoolman_info.get('version', 'unknown')} ({spoolman_info.get('git_commit', 'unknown')})",
        )
        if self._attr_device_info is None:
            self._attr_device_info = device_info
        elif self._attr_device_info.get("name") != location_name:
            # Must update entry since async_write_ha_state does not update device
            if self.coordinator.config_entry is not None:
                device = dr.async_get(self.coordinator.hass).async_get_or_create(
                    config_entry_id=self.coordinator.config_entry.entry_id,
                    **device_info,
                )
            self.registry_entry = er.async_get(
                self.coordinator.hass
            ).async_update_entity(self.entity_id, device_id=device.id)

        self._attr_name = filament_name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Use ID-based lookup instead of index to prevent IndexError
        filament_data = next(
            (
                f
                for f in self.coordinator.data.get("filaments", [])
                if f["id"] == self.filament_id
            ),
            None,
        )

        if filament_data is None:
            # Filament was deleted
            _LOGGER.warning(
                "SpoolManCoordinator: Filament with ID '%s' not found in coordinator data. Marking as unavailable.",
                self.filament_id,
            )
            self._attr_available = False
            self.async_write_ha_state()
            return

        self._attr_available = True
        self._filament = filament_data

        _LOGGER.debug("SpoolManCoordinator: Filament %s", self._filament)

        self.assign_name_and_location()
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the attributes of the sensor."""
        return self.flatten_dict(self._filament)

    def flatten_dict(
        self, d: Any, parent_key: str = "", sep: str = "_"
    ) -> dict[str, Any]:
        """Flatten a nested dictionary into single-level keys."""
        flat_dict: dict[str, Any] = {}
        if isinstance(d, dict):
            for key, value in d.items():
                new_key = f"{parent_key}{sep}{key}" if parent_key else key
                if isinstance(value, dict):
                    flat_dict.update(self.flatten_dict(value, new_key, sep=sep))
                elif isinstance(value, str):
                    flat_dict[new_key] = value.strip()
                else:
                    flat_dict[new_key] = value
            return flat_dict
        return {}

    @property  # type: ignore[misc]
    def state(self) -> float | int:
        """Return the total remaining weight across all spools (g)."""
        value = round(self._filament.get("total_remaining_weight", 0), 3)
        return value if isinstance(value, int | float) else 0

    async def async_update(self) -> None:
        """Fetch the latest data from the coordinator."""
        await self.coordinator.async_request_refresh()
