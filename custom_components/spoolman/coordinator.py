"""Spoolman home assistant data coordinator."""
import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_SPOOL_ENDPOINT,
    CONF_SHOW_ARCHIVED,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    DOMAIN,
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
            # Name of the data. For logging purposes.
            name="Spoolman data",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(minutes=update_interval),
        )
        self.my_api = url
        self.hass = hass

        hass.data[DOMAIN] = {
            **entry.data,
            "coordinator": self,
        }

    async def _async_update_data(self):
        _LOGGER.info("SpoolManCoordinator._async_update_data")
        config = self.hass.data[DOMAIN]

        show_archived = config.get(CONF_SHOW_ARCHIVED, False)

        url = f"{config[CONF_URL]}{API_SPOOL_ENDPOINT}?allow_archived={show_archived}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    data = await response.json()
                    return data
            except Exception as e:
                raise UpdateFailed(f"Error fetching data from Spoolman API: {e}")
