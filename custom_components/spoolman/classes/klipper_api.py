"""Class for interacting with Klipper API.

DEPRECATED. The integration's built-in Klipper bridge will be removed in
an upcoming release; new deployments should use Moonraker's native
Spoolman integration. See README banner for details.
"""

import aiohttp
import logging

from ..helpers.add_trailing_slash import add_trailing_slash

_LOGGER = logging.getLogger(__name__)


class KlipperAPI:
    """Class for interacting with Klipper API."""

    def __init__(
        self, base_url: str, session: aiohttp.ClientSession | None = None
    ) -> None:
        """Initialize the Klipper API."""
        self.base_url = add_trailing_slash(base_url)
        self._session = session

    async def _get_json(self, endpoint: str) -> dict:
        """Convert the response to JSON."""
        url = f"{self.base_url}server/{endpoint}"
        if self._session is not None:
            async with self._session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def get_active_spool_id(self) -> int | None:
        """Get active spool from Klipper API."""
        data = await self._get_json("spoolman/spool_id")
        spool_id = data.get("result", {}).get("spool_id")

        if spool_id is not None:
            try:
                return int(spool_id)
            except ValueError:
                raise ValueError(f"Invalid spool_id: {spool_id}")

        return None

    async def api_version(self) -> str | None:
        """Get api version from Klipper API."""
        data = await self._get_json("info")
        return data.get("result", {}).get("api_version_string")
