"""Class for interacting with Klipper API.

DEPRECATED. The integration's built-in Klipper bridge will be removed in
an upcoming release; new deployments should use Moonraker's native
Spoolman integration. See README banner for details.
"""

from __future__ import annotations

import logging
from typing import Any, cast

import aiohttp

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

    async def _get_json(self, endpoint: str) -> dict[str, Any]:
        """Fetch ``endpoint`` from Moonraker's HTTP API and decode JSON."""
        url = f"{self.base_url}server/{endpoint}"
        if self._session is not None:
            async with self._session.get(url) as response:
                response.raise_for_status()
                return cast("dict[str, Any]", await response.json())
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()
            return cast("dict[str, Any]", await response.json())

    async def get_active_spool_id(self) -> int | None:
        """Return the currently active spool ID reported by Moonraker."""
        data = await self._get_json("spoolman/spool_id")
        spool_id = data.get("result", {}).get("spool_id")

        if spool_id is not None:
            try:
                return int(spool_id)
            except ValueError as err:
                raise ValueError(f"Invalid spool_id: {spool_id}") from err

        return None

    async def api_version(self) -> str | None:
        """Return Moonraker's API version string."""
        data = await self._get_json("info")
        version = data.get("result", {}).get("api_version_string")
        return cast("str | None", version)
