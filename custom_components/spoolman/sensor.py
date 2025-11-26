"""Spoolman home assistant sensor."""

import logging
import os

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from PIL import Image, ImageDraw

from .const import (
    CONF_URL,
    DEFAULT_SPOOL_COLOR_HEX,
    DOMAIN,
    EVENT_THRESHOLD_EXCEEDED,
    LOCAL_IMAGE_PATH,
    NOTIFICATION_THRESHOLDS,
    PUBLIC_IMAGE_PATH,
    SPOOLMAN_INFO_PROPERTY,
)
from .coordinator import SpoolManCoordinator

_LOGGER = logging.getLogger(__name__)


ICON = "mdi:printer-3d-nozzle"


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Spoolman home assistant sensor init."""
    coordinator = SpoolManCoordinator(hass, config_entry)
    await coordinator.async_config_entry_first_refresh()

    if coordinator.data:
        all_entities = []
        image_dir = hass.config.path(PUBLIC_IMAGE_PATH)

        # Create spool entities
        spool_data = coordinator.data.get("spools", [])
        for idx, spool in enumerate(spool_data):
            image_url = await hass.async_add_executor_job(
                _generate_entity_picture, spool, image_dir
            )
            spool_device = Spool(
                hass, coordinator, spool, idx, config_entry, image_url
            )
            all_entities.append(spool_device)

        # Create filament entities
        filament_data = coordinator.data.get("filaments", [])
        for idx, filament in enumerate(filament_data):
            image_url = await hass.async_add_executor_job(
                _generate_filament_entity_picture, filament, image_dir
            )
            filament_device = Filament(
                hass, coordinator, filament, idx, config_entry, image_url
            )
            all_entities.append(filament_device)

        async_add_entities(all_entities)


def _generate_entity_picture(spool_data, image_dir):
    """Generate an entity picture with the specified color(s) and save it to the www directory."""
    filament = spool_data.get("filament", {})

    # Retrieve color(s)
    multi_color_hexes = filament.get("multi_color_hexes", "").split(",")
    color_hex = filament.get("color_hex", DEFAULT_SPOOL_COLOR_HEX)
    multi_color_direction = filament.get("multi_color_direction", "coaxial")

    # Determine colors: prioritize multi_color_hexes if available
    if multi_color_hexes and any(c.strip() for c in multi_color_hexes):
        colors = [c.strip() for c in multi_color_hexes if len(c.strip()) == 6]
    elif color_hex:
        colors = [color_hex]
    else:
        _LOGGER.warning(
            "SpoolManCoordinator: Spool with ID '%s' has no valid color information.",
            spool_data.get("id", "unknown"),
        )
        return None

    # Create image
    image_size = (100, 100)
    image = Image.new("RGB", image_size, int(DEFAULT_SPOOL_COLOR_HEX, 16))  # Use integer for default white color
    draw = ImageDraw.Draw(image)

    # Draw colors
    if len(colors) > 1:
        if multi_color_direction == "coaxial":
            step = image_size[0] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([
                    (i * step, 0),
                    ((i + 1) * step - 1, image_size[1])
                ], fill=f"#{color}")
        elif multi_color_direction == "longitudinal":
            step = image_size[1] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([
                    (0, i * step),
                    (image_size[0], (i + 1) * step - 1)
                ], fill=f"#{color}")
    else:
        # Single color fallback
        draw.rectangle([(0, 0), image_size], fill=f"#{colors[0]}")

    # Save the image
    image_name = f"spool_{spool_data.get('id', 'unknown')}.png"
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, image_name)
    image.save(image_path)

    # Return the URL for the saved image
    return f"{LOCAL_IMAGE_PATH}/{image_name}"


def _generate_filament_entity_picture(filament_data, image_dir):
    """Generate a filament entity picture with the specified color(s) and save it to the www directory."""

    # Retrieve color(s)
    multi_color_hexes = filament_data.get("multi_color_hexes", "").split(",")
    color_hex = filament_data.get("color_hex", DEFAULT_SPOOL_COLOR_HEX)
    multi_color_direction = filament_data.get("multi_color_direction", "coaxial")

    # Determine colors: prioritize multi_color_hexes if available
    if multi_color_hexes and any(c.strip() for c in multi_color_hexes):
        colors = [c.strip() for c in multi_color_hexes if len(c.strip()) == 6]
    elif color_hex:
        colors = [color_hex]
    else:
        _LOGGER.warning(
            "SpoolManCoordinator: Filament with ID '%s' has no valid color information.",
            filament_data.get("id", "unknown"),
        )
        return None

    # Create image
    image_size = (100, 100)
    image = Image.new("RGB", image_size, int(DEFAULT_SPOOL_COLOR_HEX, 16))  # Use integer for default white color
    draw = ImageDraw.Draw(image)

    # Draw colors
    if len(colors) > 1:
        if multi_color_direction == "coaxial":
            step = image_size[0] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([
                    (i * step, 0),
                    ((i + 1) * step - 1, image_size[1])
                ], fill=f"#{color}")
        elif multi_color_direction == "longitudinal":
            step = image_size[1] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle([
                    (0, i * step),
                    (image_size[0], (i + 1) * step - 1)
                ], fill=f"#{color}")
    else:
        # Single color fallback
        draw.rectangle([(0, 0), image_size], fill=f"#{colors[0]}")

    # Save the image
    image_name = f"filament_{filament_data.get('id', 'unknown')}.png"
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, image_name)
    image.save(image_path)

    # Return the URL for the saved image
    return f"{LOCAL_IMAGE_PATH}/{image_name}"


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

        self.assign_name_and_location()

        self._entry = config_entry
        self.entity_id = generate_entity_id("sensor.{}", f"spoolman_spool_{spool_data['id']}", hass=hass)
        self._attr_unique_id = f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}"
        self._attr_has_entity_name = False
        self._attr_device_class = SensorDeviceClass.WEIGHT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfMass.GRAMS
        self._attr_icon = ICON
        self.idx = idx  # Keep for backwards compatibility, but don't use for lookups

    def assign_name_and_location(self):
        """Update sensor name and device (location)."""

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
            spool_name = f"{vendor_name} {self._filament['name']} { self._filament.get('material')}"
            _LOGGER.debug(
                "SpoolManCoordinator: Spool with ID '%s' has 'vendor' set in filament. Using vendor name.",
                self._spool["id"],
            )

        location_name = (
            self._spool.get("location", "Unknown")
            if self._spool["archived"] is False
            else "Archived"
        )

        # Only update device info if location changed or not set yet
        current_location = self._attr_device_info.get("name") if self._attr_device_info else None

        if current_location != location_name:
            spoolman_info = self.config[SPOOLMAN_INFO_PROPERTY]
            device_info = DeviceInfo(
                identifiers={(DOMAIN, self.config[CONF_URL], location_name)},  # type: ignore
                name=location_name,
                manufacturer="https://github.com/Donkie/Spoolman",
                model="Spoolman",
                configuration_url=self.config[CONF_URL],
                suggested_area=location_name,
                sw_version=f"{spoolman_info.get('version', 'unknown')} ({ spoolman_info.get('git_commit', 'unknown')})",
            )

            if self._attr_device_info is None:
                self._attr_device_info = device_info
            else:
                # Must update entry since async_write_ha_state does not update device
                if self.coordinator.config_entry is not None:
                    _LOGGER.debug(
                        "SpoolManCoordinator: Updating device location for spool %s from '%s' to '%s'",
                        self._spool["id"],
                        current_location,
                        location_name,
                    )
                    device = dr.async_get(self.coordinator.hass).async_get_or_create(config_entry_id=self.coordinator.config_entry.entry_id, **device_info)
                    self.registry_entry = er.async_get(self.coordinator.hass).async_update_entity(self.entity_id, device_id = device.id)

        self._attr_name = spool_name

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
        """Return the attributes of the sensor."""
        spool = self._spool

        return self.flatten_dict(spool)

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


class Filament(CoordinatorEntity, SensorEntity):
    """Representation of a Spoolman Filament Sensor."""

    def __init__(
        self, hass, coordinator, filament_data, idx, config_entry, image_url
    ) -> None:
        """Spoolman home assistant filament sensor init."""
        super().__init__(coordinator)

        self.config = hass.data[DOMAIN]

        self._filament = filament_data
        self.filament_id = filament_data['id']  # Store ID instead of index
        self._attr_entity_picture = image_url
        self._attr_available = True

        self.assign_name_and_location()

        self._entry = config_entry
        self.entity_id = generate_entity_id("sensor.{}", f"spoolman_filament_{filament_data['id']}", hass=hass)
        self._attr_unique_id = f"spoolman_{self._entry.entry_id}_filament_{filament_data['id']}"
        self._attr_has_entity_name = False
        self._attr_device_class = SensorDeviceClass.WEIGHT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfMass.GRAMS
        self._attr_icon = ICON
        self.idx = idx  # Keep for backwards compatibility, but don't use for lookups

    def assign_name_and_location(self):
        """Update sensor name and device (location)."""

        vendor_name = self._filament.get("vendor", {}).get("name")

        if (
            self._filament.get("name") is None
            or self._filament.get("material") is None
        ):
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
                device = dr.async_get(self.coordinator.hass).async_get_or_create(config_entry_id=self.coordinator.config_entry.entry_id, **device_info)
            self.registry_entry = er.async_get(self.coordinator.hass).async_update_entity(self.entity_id, device_id = device.id)

        self._attr_name = filament_name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Use ID-based lookup instead of index to prevent IndexError
        filament_data = next(
            (f for f in self.coordinator.data.get("filaments", []) if f["id"] == self.filament_id),
            None
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
    def extra_state_attributes(self):
        """Return the attributes of the sensor."""
        filament = self._filament

        return self.flatten_dict(filament)

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
        """Return the state of the sensor (total remaining weight)."""
        return round(self._filament.get("total_remaining_weight", 0), 3)

    async def async_update(self):
        """Fetch the latest data from the coordinator."""
        await self.coordinator.async_request_refresh()
