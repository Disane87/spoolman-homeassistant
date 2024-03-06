"""Class for interacting with Klipper API."""
import aiohttp
import logging

from ..helpers.add_trailing_slash import add_trailing_slash

_LOGGER = logging.getLogger(__name__)

class KlipperAPI:
    """Class for interacting with Klipper API."""

    def __init__(self, base_url):
        """Initialize the Klipper API."""
        self.base_url = add_trailing_slash(base_url)

    async def get_active_spool_id(self) -> int:
        """Get active spool from Klipper API."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}server/spoolman/spool_id"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return int(data.get('result').get("spool_id"))
                else:
                    return 0
    async def api_version(self) -> str | None:
        """Get api version from Klipper API."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}server/info"
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('result').get("api_version_string")
                else:
                    return None
