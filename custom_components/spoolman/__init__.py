"""Spoolman home assistant integration."""
import logging

import homeassistant.helpers.config_validation as cv
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr, entity_registry as er

from custom_components.spoolman.schema_helper import SchemaHelper

from .const import (DOMAIN, SPOOLMAN_API_WRAPPER, SPOOLMAN_PATCH_SPOOL_SERVICENAME,
    SPOOLMAN_USE_SPOOL_FILAMENT_SERVICENAME)
from .coordinator import SpoolManCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.SELECT, Platform.BINARY_SENSOR]

# Integration can only be set up from config entries
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


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

    # Clean up old location devices from previous versions
    await _async_remove_old_location_devices(hass, entry)

    # Clean up orphaned extra field entities (after initial data load)
    if coordinator.data:
        await _async_cleanup_extra_field_entities(hass, entry, coordinator)

    # Register a one-time listener to cleanup extra fields after coordinator updates
    async def _async_cleanup_on_update():
        """Cleanup extra fields on coordinator update."""
        await coordinator.async_cleanup_extra_fields()

    # Add listener that runs cleanup on every update
    entry.async_on_unload(
        coordinator.async_add_listener(_async_cleanup_on_update)
    )

    # Register shutdown event to close aiohttp session
    async def _async_close_session(event):
        """Close the API session on shutdown."""
        if DOMAIN in hass.data and SPOOLMAN_API_WRAPPER in hass.data[DOMAIN]:
            api = hass.data[DOMAIN][SPOOLMAN_API_WRAPPER]
            await api.close()

    entry.async_on_unload(
        hass.bus.async_listen_once("homeassistant_stop", _async_close_session)
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_spoolman_patch_spool(call):
        spool_id = call.data.get('id')
        data = {key: call.data[key] for key in call.data if key != 'id'}
        _LOGGER.info(f"Patch spool called with id: {spool_id} and data: {data}")

        try:
            await coordinator.spoolman_api.patch_spool(spool_id, data)
            # Immediately refresh coordinator data to reflect changes
            _LOGGER.debug(f"Requesting coordinator refresh after patching spool {spool_id}")
            await coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Failed to patch spool: {e}")
            raise HomeAssistantError(f"Failed to patch spool: {e}")

    async def handle_spoolman_use_spool_filament(call):
        spool_id = call.data.get('id')
        data = {key: call.data[key] for key in call.data if key != 'id'}
        _LOGGER.info(f"Use spool filament called with id: {spool_id} and data: {data}")

        try:
            await coordinator.spoolman_api.use_spool_filament(spool_id, data)
            # Immediately refresh coordinator data to reflect changes
            _LOGGER.debug(f"Requesting coordinator refresh after using filament from spool {spool_id}")
            await coordinator.async_request_refresh()
        except Exception as e:
            _LOGGER.error(f"Failed to use filament: {e}")
            raise HomeAssistantError(f"Failed to use filament: {e}")


    hass.services.async_register(DOMAIN, SPOOLMAN_PATCH_SPOOL_SERVICENAME, handle_spoolman_patch_spool, schema=SchemaHelper.get_spoolman_patch_spool_schema())
    hass.services.async_register(DOMAIN, SPOOLMAN_USE_SPOOL_FILAMENT_SERVICENAME, handle_spoolman_use_spool_filament, schema=SchemaHelper.get_spoolman_use_spool_filament_schema())

    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    _LOGGER.debug("__init__.async_unload_entry")
    # Unload all platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        # Close API session before removing data
        if DOMAIN in hass.data and SPOOLMAN_API_WRAPPER in hass.data[DOMAIN]:
            api = hass.data[DOMAIN][SPOOLMAN_API_WRAPPER]
            await api.close()
        hass.data.pop(DOMAIN, None)
    return unload_ok


async def async_get_data(hass: HomeAssistant):
    """Get the latest data from the Spoolman API."""
    _LOGGER.debug("__init__.async_get_data")
    return await hass.data[DOMAIN][SPOOLMAN_API_WRAPPER].get_spools(
        {"allow_archived": False}
    )


async def _async_remove_old_location_devices(hass: HomeAssistant, entry):
    """Remove old location devices from previous integration versions.

    In earlier versions, this integration created devices for locations.
    These are now replaced with spool-based devices. This migration
    removes any orphaned location devices.
    """
    device_reg = dr.async_get(hass)
    devices = dr.async_entries_for_config_entry(device_reg, entry.entry_id)

    removed_count = 0
    for device in devices:
        # Location devices had identifiers like: (DOMAIN, url, "location_X")
        # Spool devices have identifiers like: (DOMAIN, url, "spool_X")
        for identifier in device.identifiers:
            if len(identifier) >= 3 and isinstance(identifier[2], str):
                if identifier[2].startswith("location_"):
                    _LOGGER.info(f"Removing old location device: {device.name} ({identifier[2]})")
                    device_reg.async_remove_device(device.id)
                    removed_count += 1
                    break

    if removed_count > 0:
        _LOGGER.info(f"Migration complete: Removed {removed_count} old location device(s)")


async def _async_cleanup_extra_field_entities(hass: HomeAssistant, entry, coordinator):
    """Remove orphaned extra field entities when fields are deleted from Spoolman.

    When extra fields are removed from a spool in Spoolman, the corresponding
    sensor entities should be automatically removed from Home Assistant.
    """
    entity_reg = er.async_get(hass)
    entities = er.async_entries_for_config_entry(entity_reg, entry.entry_id)

    if not coordinator.data:
        return

    spools = coordinator.data.get("spools", [])

    # Build a set of currently existing extra field unique_ids
    current_extra_field_unique_ids = set()
    for spool in spools:
        spool_id = spool.get("id")
        extra_data = spool.get("extra", {})
        for field_key in extra_data:
            safe_field_key = field_key.lower().replace(" ", "_").replace("-", "_")
            unique_id = f"spoolman_{entry.entry_id}_spool_{spool_id}_extra_{safe_field_key}"
            current_extra_field_unique_ids.add(unique_id)

    removed_count = 0
    for entity in entities:
        # Check if this is an extra field entity (contains "_extra_" in unique_id)
        if entity.unique_id and "_extra_" in entity.unique_id:
            # If it's not in the current set, it should be removed
            if entity.unique_id not in current_extra_field_unique_ids:
                _LOGGER.info(
                    f"Removing orphaned extra field entity: {entity.entity_id} (unique_id: {entity.unique_id})"
                )
                entity_reg.async_remove(entity.entity_id)
                removed_count += 1

    if removed_count > 0:
        _LOGGER.info(f"Cleanup complete: Removed {removed_count} orphaned extra field entity/entities")
