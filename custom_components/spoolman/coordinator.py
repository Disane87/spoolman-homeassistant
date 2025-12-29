"""Spoolman home assistant data coordinator."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .classes.klipper_api import KlipperAPI
from .classes.spoolman_api import SpoolmanAPI

from .const import (
    CONF_SHOW_ARCHIVED,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    DOMAIN,
    KLIPPER_URL,
    SPOOLMAN_API_WRAPPER,
)

_LOGGER = logging.getLogger(__name__)

class SpoolManCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Initialize my coordinator."""
        _LOGGER.debug("SpoolManCoordinator.__init__")

        url = entry.data[CONF_URL]
        update_interval = entry.data[CONF_UPDATE_INTERVAL]

        super().__init__(
            hass,
            _LOGGER,
            name="Spoolman data",
            update_interval=timedelta(minutes=update_interval),
        )
        self.hass = hass
        self.config_entry = entry
        self.spoolman_api = SpoolmanAPI(url)

        hass.data[DOMAIN] = {
            **entry.data,
            SPOOLMAN_API_WRAPPER: self.spoolman_api,
            "coordinator": self,
            "klipper_active_spool": None
        }

    async def _async_update_data(self):
        _LOGGER.debug("SpoolManCoordinator._async_update_data")
        config = self.hass.data[DOMAIN]

        show_archived = config.get(CONF_SHOW_ARCHIVED, False)

        try:
            spools = await self.spoolman_api.get_spools(
                {"allow_archived": show_archived}
            )
            filaments = await self.spoolman_api.get_filaments({})
        except asyncio.CancelledError:
            # Task was cancelled (e.g., during shutdown), re-raise to let coordinator handle it
            _LOGGER.debug("Data update was cancelled")
            raise
        except Exception as exception:
            raise UpdateFailed(
                f"Error fetching data from API: {exception}"
            ) from exception

        # Calculate total remaining weight for each filament from non-archived spools
        filament_remaining_weights = {}
        for spool in spools:
            if not spool.get("archived", False):  # Only count non-archived spools
                filament_id = spool.get("filament", {}).get("id")
                remaining_weight = spool.get("remaining_weight", 0)
                if filament_id is not None and remaining_weight is not None:
                    if filament_id not in filament_remaining_weights:
                        filament_remaining_weights[filament_id] = 0
                    filament_remaining_weights[filament_id] += remaining_weight

        # Add total remaining weight to each filament
        for filament in filaments:
            filament_id = filament.get("id")
            filament["total_remaining_weight"] = filament_remaining_weights.get(filament_id, 0)

        try:
            klipper_url = config.get(KLIPPER_URL, "")
            if klipper_url is not None and klipper_url != "":
                klipper_active_spool: int | None = await KlipperAPI(klipper_url).get_active_spool_id()
                if klipper_active_spool is not None:
                    for spool in spools:
                        if spool["id"] == klipper_active_spool:
                            spool["klipper_active_spool"] = True
                        else:
                            spool["klipper_active_spool"] = False
        except Exception as exception:
            _LOGGER.error(f"Error processing Klipper API data: {exception}")
            # Continue returning spools even if Klipper processing fails

        return {"spools": spools, "filaments": filaments}

    async def async_cleanup_extra_fields(self):
        """Cleanup orphaned extra field entities - can be called externally."""
        await self._async_cleanup_extra_fields_on_update()

    async def _async_cleanup_extra_fields_on_update(self):
        """Cleanup orphaned extra field entities after data update."""
        try:
            from homeassistant.helpers import entity_registry as er

            # Don't run cleanup if we don't have data yet
            if not self.data:
                _LOGGER.debug("Skipping extra field cleanup - no data available yet")
                return

            entity_reg = er.async_get(self.hass)
            entities = er.async_entries_for_config_entry(entity_reg, self.config_entry.entry_id)

            spools = self.data.get("spools", [])

            # Build a set of currently existing extra field unique_ids
            current_extra_field_unique_ids = set()
            for spool in spools:
                spool_id = spool.get("id")
                extra_data = spool.get("extra", {})
                for field_key in extra_data:
                    safe_field_key = field_key.lower().replace(" ", "_").replace("-", "_")
                    unique_id = f"spoolman_{self.config_entry.entry_id}_spool_{spool_id}_extra_{safe_field_key}"
                    current_extra_field_unique_ids.add(unique_id)

            removed_count = 0
            for entity in entities:
                # Check if this is an extra field entity (contains "_extra_" in unique_id)
                if entity.unique_id and "_extra_" in entity.unique_id:
                    # If it's not in the current set, it should be removed
                    if entity.unique_id not in current_extra_field_unique_ids:
                        _LOGGER.info(
                            f"Removing orphaned extra field entity during update: {entity.entity_id}"
                        )
                        entity_reg.async_remove(entity.entity_id)
                        removed_count += 1

            if removed_count > 0:
                _LOGGER.info(f"Update cleanup: Removed {removed_count} orphaned extra field entity/entities")
        except asyncio.CancelledError:
            # Task was cancelled, just return silently
            _LOGGER.debug("Extra field cleanup was cancelled")
        except Exception as e:
            _LOGGER.error(f"Error during extra field cleanup: {e}", exc_info=True)
