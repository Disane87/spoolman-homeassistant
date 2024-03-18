"""Spoolman home assistant data coordinator."""
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

            klipper_url = config.get(KLIPPER_URL, "")
            if klipper_url is not None and klipper_url != "":
                klipper_active_spool: int = await KlipperAPI(klipper_url).get_active_spool_id()
                for spool in spools:
                    if spool["id"] == klipper_active_spool:
                        spool["klipper_active_spool"] = True
                    else:
                        spool["klipper_active_spool"] = False

            return spools

        except Exception as exception:
            raise UpdateFailed(
                f"Error fetching data from API: {exception}"
            ) from exception
