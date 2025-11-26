"""Sensor class: Spool."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.const import UnitOfMass
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import (
    CONF_URL,
    DOMAIN,
    EVENT_THRESHOLD_EXCEEDED,
    NOTIFICATION_THRESHOLDS,
    SPOOLMAN_INFO_PROPERTY,
)

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:printer-3d-nozzle"

class Spool(CoordinatorEntity, SensorEntity):
    """Representation of a Spoolman Sensor."""

    def __init__(
        self, hass, coordinator, spool_data, idx, config_entry, image_url
    ) -> None:
        """Spoolman home assistant spool sensor init."""
        super().__init__(coordinator)

        self.config = hass.data[DOMAIN]

        self._spool = spool_data
        self.spool_id = spool_data['id']  # Store ID instead of index
        self.handled_threshold_events = []
        self._filament = self._spool["filament"]
        self._attr_entity_picture = image_url
        self._attr_available = True
        self._entry = config_entry

        # Set entity properties first
        self.entity_id = generate_entity_id("sensor.{}", f"spoolman_spool_{spool_data['id']}", hass=hass)
        self._attr_unique_id = f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}"
        self._attr_has_entity_name = False
        self._attr_device_class = SensorDeviceClass.WEIGHT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfMass.GRAMS
        self._attr_icon = ICON
        self.idx = idx  # Keep for backwards compatibility, but don't use for lookups

        # Now assign device info (requires entity_id to be set)
        self.assign_name_and_location()

    def assign_name_and_location(self):
        """Update sensor name and device (spool as device, location as via_device)."""

        vendor_name = self._filament.get("vendor", {}).get("name")

        if (
            self._filament.get("name") is None
            or self._filament.get("material") is None
        ):
            spool_name = f"Spoolman Spool {self._spool['id']}"
            _LOGGER.warning(
                "SpoolManCoordinator: Spool with ID '%s' has no 'name' or 'material' set in filament. Using default name.",
                self._spool["id"],
            )
        elif vendor_name is None:
            spool_name = f"{self._filament['name']} {self._filament.get('material')}"
            _LOGGER.warning(
                "SpoolManCoordinator: Spool with ID '%s' has no 'vendor' set in filament. Using default name.",
                self._spool["id"],
            )
        else:
            spool_name = f"{vendor_name} {self._filament['name']} {self._filament.get('material')}"
            _LOGGER.debug(
                "SpoolManCoordinator: Spool with ID '%s' has 'vendor' set in filament. Using vendor name.",
                self._spool["id"],
            )

        location_name = (
            self._spool.get("location", "Unknown")
            if self._spool["archived"] is False
            else "Archived"
        )

        # Create location hub device (via_device)
        spoolman_info = self.config[SPOOLMAN_INFO_PROPERTY]
        location_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config[CONF_URL], f"location_{location_name}")},
            name=f"Location: {location_name}",
            manufacturer="https://github.com/Donkie/Spoolman",
            model="Spoolman Location Hub",
            configuration_url=self.config[CONF_URL],
            suggested_area=location_name,
            sw_version=f"{spoolman_info.get('version', 'unknown')} ({spoolman_info.get('git_commit', 'unknown')})",
        )

        # Create spool device with location as via_device
        spool_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")},
            name=spool_name,
            manufacturer=vendor_name if vendor_name else "Unknown",
            model=f"{self._filament.get('material', 'Unknown')} - {self._filament.get('name', 'Unknown')}",
            via_device=(DOMAIN, self.config[CONF_URL], f"location_{location_name}"),
            configuration_url=self.config[CONF_URL],
            sw_version=f"Spool ID: {self._spool['id']}",
        )

        # Ensure location hub device exists first
        if self.coordinator.config_entry is not None:
            device_registry = dr.async_get(self.coordinator.hass)

            # Create or get location hub
            device_registry.async_get_or_create(
                config_entry_id=self.coordinator.config_entry.entry_id,
                **location_device_info
            )

            # Create or get spool device
            spool_device = device_registry.async_get_or_create(
                config_entry_id=self.coordinator.config_entry.entry_id,
                **spool_device_info
            )

            # Only update entity if it already exists, otherwise device_info will be used during entity creation
            entity_registry = er.async_get(self.coordinator.hass)
            existing_entity = entity_registry.async_get(self.entity_id)
            if existing_entity:
                self.registry_entry = entity_registry.async_update_entity(
                    self.entity_id,
                    device_id=spool_device.id
                )

        self._attr_device_info = spool_device_info
        self._attr_name = spool_name  # Use full name for now to avoid confusion

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Use ID-based lookup instead of index to prevent IndexError
        spool_data = next(
            (s for s in self.coordinator.data.get("spools", []) if s["id"] == self.spool_id),
            None
        )

        if spool_data is None:
            # Spool was deleted or filtered out (e.g., archived)
            _LOGGER.warning(
                "SpoolManCoordinator: Spool with ID '%s' not found in coordinator data. Marking as unavailable.",
                self.spool_id,
            )
            self._attr_available = False
            self.async_write_ha_state()
            return

        self._attr_available = True
        self._spool = spool_data
        self._filament = spool_data["filament"]

        _LOGGER.debug("SpoolManCoordinator: Spool %s", self._spool)
        _LOGGER.debug("SpoolManCoordinator: Filament %s", self._filament)

        self.assign_name_and_location()

        if self._filament.get("weight") is None:
            _LOGGER.warning(
                "SpoolManCoordinator: Spool with ID '%s' has no 'weight' set or property is missing in filament. Can't calculate usage. Skipping.",
                self._spool["id"],
            )
            return

        if self._spool.get("used_weight") is None:
            _LOGGER.warning(
                "SpoolManCoordinator: Spool with ID '%s' has no 'used_weight' set or property is missing in filament. Can't calculate usage. Skipping.",
                self._spool["id"],
            )
            return

        self._spool["used_percentage"] = (
            round(self._spool["used_weight"] / self._filament["weight"], 3) * 100
        )

        if self._spool["archived"] is False:
            self.check_for_threshold(self._spool, self._spool["used_percentage"])

        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        """Return all attributes for backward compatibility during migration.

        Users can migrate to dedicated sensors at their own pace.
        This maintains compatibility with existing automations and scripts.
        """
        # Return flattened dict of all spool and filament data for backward compatibility
        return self.flatten_dict(self._spool)

    def check_for_threshold(self, spool, used_percentage):
        """Check if the used percentage is above a threshold and fire an event if it is."""
        for key, _value in sorted(
            NOTIFICATION_THRESHOLDS.items(), key=lambda x: x[1], reverse=True
        ):
            threshold_name = key
            config_threshold = self.config[f"notification_threshold_{threshold_name}"]

            if threshold_name in self.handled_threshold_events:
                _LOGGER.debug(
                    "SpoolManCoordinator.check_for_threshold: '%s' already handled for spool '%s' in '%s' with '%s'",
                    threshold_name,
                    self._attr_name,
                    self._spool.get("location", "Unknown"),
                    used_percentage,
                )
                break

            if used_percentage >= config_threshold:
                _LOGGER.debug(
                    "SpoolManCoordinator.check_for_threshold: '%s' reached for spool '%s' in '%s' with '%s'",
                    threshold_name,
                    self._attr_name,
                    self._spool.get("location", "Unknown"),
                    used_percentage,
                )
                self.hass.bus.fire(
                    EVENT_THRESHOLD_EXCEEDED,
                    {
                        "entity_id": self.entity_id,
                        "spool": spool,
                        "threshold_name": threshold_name,
                        "threshold_value": config_threshold,
                        "used_percentage": used_percentage,
                    },
                )
                self.handled_threshold_events.append(threshold_name)
                break

    def flatten_dict(self, d, parent_key="", sep="_"):
        """Flattens a dictionary."""
        flat_dict = {}
        if isinstance(d, dict):
            for key, value in d.items():
                new_key = f"{parent_key}{sep}{key}" if parent_key else key
                if isinstance(value, dict):
                    # Wenn der Wert ein Dictionary ist, rufen Sie die Funktion rekursiv auf
                    flat_dict.update(self.flatten_dict(value, new_key, sep=sep))
                elif isinstance(value, str):
                    # Wenn der Wert ein String ist, trimmen Sie ihn
                    flat_dict[new_key] = value.strip()
                else:
                    flat_dict[new_key] = value
            return flat_dict

        else:
            return {}

    @property
    def state(self):
        """Return the state of the sensor."""

        return round(self._spool.get("remaining_weight", 0), 3)

    async def async_update(self):
        """Fetch the latest data from the coordinator."""
        await self.coordinator.async_request_refresh()
