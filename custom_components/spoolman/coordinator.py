"""Spoolman home assistant data coordinator."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .classes.spoolman_api import SpoolmanAPI
from .const import (
    CONF_SHOW_ARCHIVED,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    DOMAIN,
    SPOOLMAN_API_WRAPPER,
)

_LOGGER = logging.getLogger(__name__)


class SpoolManCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        """Initialize my coordinator."""
        _LOGGER.info("SpoolManCoordinator.__init__")
        url = entry.data[CONF_URL]
        update_interval = entry.data[CONF_UPDATE_INTERVAL]

        super().__init__(
            hass,
            _LOGGER,
            name="Spoolman data",
            update_interval=timedelta(minutes=update_interval),
        )
        self.my_api = url
        self.hass = hass
        self.spoolman_api = SpoolmanAPI(entry.data[CONF_URL])

        hass.data[DOMAIN] = {
            **entry.data,
            SPOOLMAN_API_WRAPPER: self.spoolman_api,
            "coordinator": self,
        }

    async def _async_update_data(self):
        _LOGGER.info("SpoolManCoordinator._async_update_data")
        config = self.hass.data[DOMAIN]

        show_archived = config.get(CONF_SHOW_ARCHIVED, False)

        try:
            spools = await self.spoolman_api.get_spool(
                {"allow_archived": show_archived}
            )
            return spools

        except Exception as exception:
            raise UpdateFailed(
                f"Error fetching data from Spoolman API: {exception}"
            ) from exception
