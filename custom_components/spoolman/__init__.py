"""Spoolman home assistant integration."""
import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from custom_components.spoolman.schema_helper import SchemaHelper

from .const import (DOMAIN, SPOOLMAN_API_WRAPPER, SPOOLMAN_PATCH_SPOOL_SERVICENAME,
    SPOOLMAN_USE_SPOOL_FILAMENT_SERVICENAME)
from .coordinator import SpoolManCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


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

    coordinator = SpoolManCoordinator(hass, entry)
    await coordinator.async_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_spoolman_patch_spool(call):
        spool_id = call.data.get('id')
        data = {key: call.data[key] for key in call.data if key != 'id'}
        _LOGGER.info(f"Patch spool called with id: {spool_id} and data: {data}")

        try:
            await coordinator.spoolman_api.patch_spool(spool_id, data)
        except Exception as e:
            _LOGGER.error(f"Failed to patch spool: {e}")
            raise HomeAssistantError(f"Failed to patch spool: {e}")

    async def handle_spoolman_use_spool_filament(call):
        spool_id = call.data.get('id')
        data = {key: call.data[key] for key in call.data if key != 'id'}
        _LOGGER.info(f"Use spool filament called with id: {spool_id} and data: {data}")

        try:
            await coordinator.spoolman_api.use_spool_filament(spool_id, data)
        except Exception as e:
            _LOGGER.error(f"Failed to use filament: {e}")
            raise HomeAssistantError(f"Failed to use filament: {e}")


    hass.services.async_register(DOMAIN, SPOOLMAN_PATCH_SPOOL_SERVICENAME, handle_spoolman_patch_spool, schema=SchemaHelper.get_spoolman_patch_spool_schema())
    hass.services.async_register(DOMAIN, SPOOLMAN_USE_SPOOL_FILAMENT_SERVICENAME, handle_spoolman_use_spool_filament, schema=SchemaHelper.get_spoolman_use_spool_filament_schema())

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
    return await hass.data[DOMAIN][SPOOLMAN_API_WRAPPER].get_spools(
        {"allow_archived": False}
    )
