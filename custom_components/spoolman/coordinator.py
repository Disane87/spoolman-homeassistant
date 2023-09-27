import logging
from datetime import timedelta
from typing import Any, Dict, List

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (DataUpdateCoordinator,
                                                      UpdateFailed)

from .const import (API_SPOOL_ENDPOINT, CONF_API_KEY, CONF_UPDATE_INTERVAL,
                    CONF_URL, DOMAIN)

_LOGGER = logging.getLogger(__name__)


class SpoolManCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        _LOGGER.info("SpoolManCoordinator.__init__")
        api_key = entry.data[CONF_API_KEY]
        url = f"{entry.data[CONF_URL]}{API_SPOOL_ENDPOINT}"
        update_interval = entry.data[CONF_UPDATE_INTERVAL]
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Spoolman data",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=update_interval),
        )
        self.my_api = url
        self.hass = hass

        hass.data[DOMAIN] = {
            CONF_API_KEY: api_key,
            CONF_URL: url,
            CONF_UPDATE_INTERVAL: update_interval,
            'coordinator': self
        }

    async def _async_update_data(self):
        _LOGGER.info("SpoolManCoordinator._async_update_data")
        api_key = self.hass.data[DOMAIN][CONF_API_KEY]
        url = self.hass.data[DOMAIN][CONF_URL]

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url, headers={"Authorization": f"Bearer {api_key}"}
                ) as response:
                    data = await response.json()
                    # _LOGGER.info(f"SpoolManCoordinator._async_update_data: {data}")
                    return data
            except Exception as e:
                raise UpdateFailed(f"Error fetching data from Spoolman API: {e}")

    # def parse_spool_data(data: list[dict[str, Any]]) -> list[Spool]:
    #     spool_objects = []
    #     for item in data:
    #         spool = Spool.from_dict(item)
    #         spool_objects.append(spool)
    #     return spool_objects

    # async def async_setup_websocket(hass, websocket_url, callback):
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
    #             await asyncio.sleep(10)
