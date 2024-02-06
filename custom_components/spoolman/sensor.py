"""Spoolman home assistant sensor."""
import logging
import os

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfMass,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from PIL import Image

from .const import (
    CONF_URL,
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
        spool_entities = []
        for idx, spool_data in enumerate(coordinator.data):
            if spool_data['filament'].get('name') is None or spool_data['filament'].get('material') is None:
                _LOGGER.warning("SpoolManCoordinator: Spool with ID '%s' has no name or material set. Can't create sensor. Skipping.", spool_data['filament'].get('id'))
                return
            spool_device = Spool(hass, coordinator, spool_data, idx, config_entry)
            spool_entities.append(spool_device)
        async_add_entities(spool_entities)


class Spool(CoordinatorEntity, SensorEntity):
    """Representation of a Spoolman Sensor."""

    def __init__(self, hass, coordinator, spool_data, idx, config_entry) -> None:
        """Spoolman home assistant spool sensor init."""
        super().__init__(coordinator)

        self.config = hass.data[DOMAIN]
        conf_url = self.config[CONF_URL]
        spoolman_info = self.config[SPOOLMAN_INFO_PROPERTY]

        self._spool = spool_data
        self.handled_threshold_events = []
        self._filament = self._spool["filament"]

        vendor_name = self._filament.get('vendor', {}).get('name')

        if vendor_name is None:
            spool_name = f"{self._filament['name']} {self._filament.get('material')}"
        else:
            spool_name = f"{vendor_name} {self._filament['name']} {self._filament.get('material')}"

        location_name = (
            "Unknown" if not self._spool.get("location") else self._spool["location"]
        ) if spool_data["archived"] is False else "Archived"


        self._entry = config_entry
        self._attr_name = spool_name
        self._attr_unique_id = f"{self._attr_name}_{spool_data['id']}"
        self._attr_has_entity_name = False
        self._attr_device_class = SensorDeviceClass.WEIGHT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfMass.GRAMS
        self._attr_icon = ICON

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, conf_url, location_name)},  # type: ignore
            name=location_name,
            manufacturer="https://github.com/Donkie/Spoolman",
            model="Spoolman",
            configuration_url=conf_url,
            suggested_area=location_name,
            sw_version=f"{spoolman_info.get('version', 'unknown')} ({spoolman_info.get('git_commit', 'unknown')})",
        )
        self.idx = idx

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._spool = self.coordinator.data[self.idx]
        self._filament = self._spool["filament"]

        _LOGGER.debug("SpoolManCoordinator: Spool %s", self._spool)
        _LOGGER.debug("SpoolManCoordinator: Spool %s", self._filament)

        if self._filament.get("weight") is None:
            _LOGGER.warning("SpoolManCoordinator: Spool with ID '%s' has no 'weight' set or property is missing in filament. Can't calculate usage. Skipping.", self._spool['id'])
            return

        if self._filament.get("used_weight") is None:
            _LOGGER.warning("SpoolManCoordinator: Spool with ID '%s' has no 'used_weight' set or property is missing in filament. Can't calculate usage. Skipping.", self._spool['id'])
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
                    self._spool["location"],
                    used_percentage,
                )
                break

            if used_percentage >= config_threshold:
                _LOGGER.debug(
                    "SpoolManCoordinator.check_for_threshold: '%s' reached for spool '%s' in '%s' with '%s'",
                    threshold_name,
                    self._attr_name,
                    self._spool["location"],
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

        return round(self._spool.get('remaining_weight',0), 3)

    @property
    def entity_picture(self):
        """Return the entity picture."""
        filament = self._spool["filament"]

        if filament.get("color_hex") is None:
            _LOGGER.warning("SpoolManCoordinator: Spool with ID '%s' has no color_hex set. Can't create entity picture.", self._spool['id'])
            # color_hex = 'FFFFFF'
        else:
            color_hex = filament.get("color_hex", 'FFFFFF')
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
