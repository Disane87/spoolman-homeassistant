"""Spoolman home assistant data coordinator."""
import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_SPOOL_ENDPOINT,
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
            CONF_URL: url,
            CONF_UPDATE_INTERVAL: update_interval,
            "coordinator": self,
        }

    async def _async_update_data(self):
        _LOGGER.info("SpoolManCoordinator._async_update_data")
        url = f"{self.hass.data[DOMAIN][CONF_URL]}{API_SPOOL_ENDPOINT}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    data = await response.json()
                    # _LOGGER.info(f"SpoolManCoordinator._async_update_data: {data}")
                    return data
            except Exception as e:
                raise UpdateFailed(f"Error fetching data from Spoolman API: {e}")
