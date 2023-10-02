"""Spoolman home assistant sensor."""
import os
from PIL import Image

from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.const import (
    UnitOfMass,
)
from .const import CONF_URL, DOMAIN, PUBLIC_IMAGE_PATH, LOCAL_IMAGE_PATH
from .coordinator import SpoolManCoordinator

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
        spool_entities = []
        for idx, spool_data in enumerate(coordinator.data):
            spool_device = Spool(hass, coordinator, spool_data, idx, config_entry)
            spool_entities.append(spool_device)
        async_add_entities(spool_entities)


class Spool(CoordinatorEntity, SensorEntity):
    """Representation of a Spoolman Sensor."""

    def __init__(self, hass, coordinator, spool_data, idx, config_entry) -> None:
        """Spoolman home assistant spool sensor init."""
        super().__init__(coordinator)

        conf_url = hass.data[DOMAIN][CONF_URL]

        self._spool = spool_data
        self._filament = self._spool["filament"]
        self._entry = config_entry
        self._attr_name = f"{self._filament['vendor']['name']} {self._filament['name']} {self._filament['material']}"
        self._attr_unique_id = f"{self._attr_name}_{spool_data['id']}"
        self._attr_has_entity_name = False
        self._attr_device_class = SensorDeviceClass.WEIGHT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfMass.GRAMS
        self._attr_icon = ICON
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, conf_url)},
            name=DOMAIN,
            manufacturer="https://github.com/Donkie/Spoolman",
            model="Spoolman",
            configuration_url=conf_url,
        )
        self.idx = idx

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._spool = self.coordinator.data[self.idx]

        self._filament = self._spool["filament"]
        self.async_write_ha_state()

    @property
    def extra_state_attributes(self):
        """Return the attributes of the sensor."""
        spool = self._spool
        spool["used_percentage"] = (
            round(self._spool["used_weight"] / self._filament["weight"], 3) * 100
        )
        return self.flatten_dict(spool)

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

        return round(self._spool["remaining_weight"], 3)

    @property
    def entity_picture(self):
        """Return the entity picture."""
        filament = self._spool["filament"]
        color_hex = filament["color_hex"]
        return self.generate_entity_picture(color_hex)

    def generate_entity_picture(self, color_hex):
        """Generate an entity picture with the specified color and save it to the www directory."""
        image = Image.new("RGB", (100, 100), f"#{color_hex}")
        image_name = f"spool_{self._spool['id']}.png"

        # Define the directory path
        image_dir = self.hass.config.path(PUBLIC_IMAGE_PATH)

        # Check if the directory exists, and create it if it doesn't
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        image_path = os.path.join(image_dir, image_name)
        image.save(image_path)

        # Get the URL for the saved image
        image_url = f"{LOCAL_IMAGE_PATH}/{image_name}"

        return image_url

    async def async_update(self):
        """Fetch the latest data from the coordinator."""
        await self.coordinator.async_request_refresh()
