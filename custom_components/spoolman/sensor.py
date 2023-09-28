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
        # spool_entities.append(MyCustomSensor(CONF_NAME, DOMAIN))
        for idx, spool_data in enumerate(coordinator.data):
            spool_device = Spool(hass, coordinator, spool_data, idx, config_entry)
            spool_entities.append(spool_device)
            # spool_entities.extend(spool_device.create_child_sensors())
        async_add_entities(spool_entities)


class Spool(CoordinatorEntity, SensorEntity):
    """Representation of a Spoolman Sensor."""

    def __init__(self, hass, coordinator, spool_data, idx, config_entry) -> None:
        """Spoolman home assistant spool sensor init."""
        super().__init__(coordinator)
        self._spool = spool_data
        self._filament = self._spool["filament"]
        self._entry = config_entry
        self._attr_unique_id = self._filament["name"]
        self._attr_has_entity_name = False
        self._attr_name = self._filament["name"]
        # self._firne
        self._attr_device_class = SensorDeviceClass.WEIGHT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfMass.GRAMS
        self._attr_icon = ICON
        self._attr_device_info = DeviceInfo(
            # , "spool", self.name
            identifiers={(DOMAIN, CONF_URL)},
            # manufacturer=self._filament["vendor"]["name"],
            # model=self._filament["material"],
            name=DOMAIN,
            # suggested_area=self._spool["location"],
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

    # def _get_sensor_properties(self, key):
    #     device_class = None
    #     unit_of_measurement = None

    #     if key.endswith("_temp"):
    #         device_class = SensorDeviceClass.TEMPERATURE
    #         unit_of_measurement = UnitOfTemperature.CELSIUS
    #     elif key.endswith("_weight"):
    #         device_class = SensorDeviceClass.WEIGHT
    #         unit_of_measurement = UnitOfMass.GRAMS
    #     elif key.endswith("_length"):
    #         device_class = SensorDeviceClass.DISTANCE
    #         unit_of_measurement = UnitOfLength.MILLIMETERS
    #     elif key in ["registered", "first_used", "last_used"]:
    #         device_class = SensorDeviceClass.DATE

    #     return device_class, unit_of_measurement

    # def create_child_sensors(self):
    #     def _create_child_sensors_recursive(parent_key, data):
    #         sensors = []
    #         for key, value in data.items():
    #             if isinstance(value, dict):
    #                 sensors.extend(_create_child_sensors_recursive(f"{parent_key}_{key}", value))
    #             else:
    #                 device_class, unit_of_measurement = self._get_sensor_properties(key)
    #                 sensor_key = f"{parent_key}_{key}".strip("_")
    #                 sensor_name = f"{sensor_key}".replace("_", " ").title()
    #                 sensors.append(self.create_sensor(sensor_key, sensor_name, value, unit_of_measurement, device_class, self._attr_name))

    #         return sensors

    #     sensors = []
    #     for key, value in self._spool.items():
    #         if isinstance(value, dict):
    #             sensors.extend(_create_child_sensors_recursive(key, value))
    #         else:
    #             device_class, unit_of_measurement = self._get_sensor_properties(key)
    #             sensor_key = f"{self.name}_{key}".replace("_", " ").title()
    #             sensors.append(self.create_sensor(sensor_key, sensor_key, value, unit_of_measurement, device_class, self._attr_name))

    #     return sensors

    # def create_sensor(self, key, name, value, unit_of_measurement, device_class, device_name):
    #     _LOGGER.info(f"Creating child sensor for '{self._attr_name}' '{key}' and name '{name}'")
    #     return SpoolSensor(
    #         self._entry.entry_id,
    #         f"sensor.{self._attr_name}_{self._entry.entry_id}_{self.idx}_{key}",
    #         name,
    #         value,
    #         ICON,
    #         device_class,
    #         unit_of_measurement,
    #         self._spool['filament']['vendor']['name'],
    #         self._spool['filament']['material'],
    #         self._spool['location'],
    #         device_name
    #     )

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


# class SpoolSensor(SensorEntity):
#     def __init__(self, entry_id, entity_id, name, state, icon, device_class, unit_of_measurement, manufacturer, model, suggested_area, device_name):
#         self._entry_id = entry_id
#         self._entity_id = entity_id
#         self._attr_has_entity_name = True
#         self._name = name
#         self._state = state
#         self._icon = icon
#         self._device_class = device_class
#         self._unit_of_measurement = unit_of_measurement
#         self._manufacturer = manufacturer
#         self._model = model
#         self._suggested_area = suggested_area
#         self._device_name = device_name

#     @property
#     def unique_id(self):
#         return f"{self._entry_id}_{self._entity_id}"

#     @property
#     def name(self):
#         return self._name

#     @property
#     def state(self):
#         return self._state

#     @property
#     def icon(self):
#         return self._icon

#     @property
#     def device_info(self):
#         return DeviceInfo(
#             identifiers={(DOMAIN, self._entry_id, "spool", self._device_name)},
#             manufacturer=self._manufacturer,
#             model=self._model,
#             suggested_area=self._suggested_area,
#             name=self._name,
#         )
