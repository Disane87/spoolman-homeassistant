"""Spoolman home assistant integration."""
import logging
import aiohttp

from homeassistant.const import Platform, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from .const import DOMAIN, CONF_URL, DEFAULT_NAME
from .coordinator import SpoolManCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_URL): cv.string,
    }
)


async def async_setup_platform(
    hass: HomeAssistant, config, add_devices, discovery_info=None
):
    """Set up Spoolman sensor."""
    _LOGGER.debug("__init__.async_setup_platform")


async def async_setup(hass: HomeAssistant, config):
    """Set up the Spoolman component."""
    _LOGGER.debug("__init__.async_setup")
    return True


async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up the Spoolman component from a config entry."""
    _LOGGER.debug("__init__.async_setup_entry")
    # session = async_create_clientsession(hass)
    coordinator = SpoolManCoordinator(hass, entry)
    await coordinator.async_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    _LOGGER.debug("__init__.async_unload_entry")
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data.pop(entry.domain)
    return unload_ok


async def async_get_data(hass: HomeAssistant):
    """Get the latest data from the Spoolman API."""
    _LOGGER.debug("__init__.async_get_data")
    url = hass.data[DOMAIN][CONF_URL]

    async with aiohttp.ClientSession() as session:
        try:
            headers = {}

            async with session.get(url, headers=headers) as response:
                data = await response.json()
                return data
        except Exception as e:
            _LOGGER.error(f"Error fetching data from Spoolman API: {e}")


# async def async_setup_websocket(hass, websocket_url, callback):
#     _LOGGER.debug("__init__.async_setup_websocket")
#     """Set up a WebSocket connection for real-time updates."""
#     while True:
#         try:
#             async with websockets.connect(websocket_url) as ws:
#                 while True:
#                     data = await ws.recv()
#                     data_json = json.loads(data)
#                     await callback()
#         except Exception as e:
#             _LOGGER.error(f"WebSocket error: {e}")


# async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
#     _LOGGER.debug("__init__.async_setup_platform")
#     """Set up the Spoolman sensor platform."""
#     coordinator = hass.data[DOMAIN]["coordinator"]
#     spool_data = coordinator.data
#     if spool_data:
#         sensors = [SpoolSensor(spool) for spool in spool_data]
#         async_add_entities(sensors)
