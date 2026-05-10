"""Class for interacting with the Spoolman API."""

import aiohttp
import logging
import json

_LOGGER = logging.getLogger(__name__)


class SpoolmanAPI:
    """Class for interacting with the Spoolman API.

    Accepts an optional pre-built ``aiohttp.ClientSession``. Inside Home
    Assistant, the coordinator passes ``async_get_clientsession(hass)`` so
    we share the HA-managed session (Platinum quality scale rule
    ``inject-websession``). Outside HA (e.g. raw scripts/tests), the class
    creates and manages its own session as a fallback.
    """

    def __init__(
        self, base_url, api_version="v1", session: aiohttp.ClientSession | None = None
    ):
        """Initialize the Spoolman API."""
        _LOGGER.debug("SpoolmanAPI: __init__")
        self.base_url = f"{base_url}api/{api_version}"
        self._session = session
        self._owns_session = session is None

    async def _get_session(self):
        """Get or create aiohttp ClientSession."""
        if self._session is None or self._session.closed:
            _LOGGER.debug("SpoolmanAPI: Creating new aiohttp ClientSession")
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    async def close(self):
        """Close the aiohttp ClientSession iff this instance owns it.

        When the caller (the HA coordinator) passes a shared session via
        ``async_get_clientsession``, that session's lifecycle is managed
        by Home Assistant — closing it here would break other integrations.
        """
        if self._session and not self._session.closed and self._owns_session:
            _LOGGER.debug("SpoolmanAPI: Closing aiohttp ClientSession")
            await self._session.close()

    async def info(self):
        """Return information about the API."""
        _LOGGER.debug("SpoolmanAPI: info")
        url = f"{self.base_url}/info"
        session = await self._get_session()
        async with session.get(url) as response:
            response.raise_for_status()
            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: info response %s", response)
            return response

    async def health(self):
        """Return the health status of the API."""
        _LOGGER.debug("SpoolmanAPI: health")
        url = f"{self.base_url}/health"
        session = await self._get_session()
        async with session.get(url) as response:
            response.raise_for_status()
            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: health response %s", response)
            return response

    async def backup(self):
        """Initiate a backup of the API."""
        _LOGGER.debug("SpoolmanAPI: backup")
        url = f"{self.base_url}/backup"
        session = await self._get_session()
        async with session.post(url) as response:
            response.raise_for_status()
            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: backup response %s", response)
            return response

    async def get_locations(self):
        """Return the list of configured spool locations from Spoolman.

        Uses ``GET /api/v1/location`` so that locations without any assigned
        spool (e.g. empty AMS trays) are still selectable in HA.
        """
        _LOGGER.debug("SpoolmanAPI: get_locations")
        url = f"{self.base_url}/location"
        session = await self._get_session()
        async with session.get(url) as response:
            response.raise_for_status()
            payload = await response.json()
            _LOGGER.debug("SpoolmanAPI: get_locations response %s", payload)
            return [str(loc) for loc in payload if loc]

    async def get_extra_fields(self, entity_type):
        """Return extra-field metadata for the given entity type (e.g. ``spool``).

        Returns a dict keyed by field key with ``name``, ``field_type``, ``unit``,
        ``choices`` and ``multi_choice`` so the integration can set proper HA
        device classes / units / state classes on dynamic extra-field sensors.
        """
        _LOGGER.debug("SpoolmanAPI: get_extra_fields(%s)", entity_type)
        url = f"{self.base_url}/field/{entity_type}"
        session = await self._get_session()
        async with session.get(url) as response:
            response.raise_for_status()
            payload = await response.json()
            _LOGGER.debug("SpoolmanAPI: get_extra_fields response %s", payload)
            return {
                item["key"]: {
                    "name": item.get("name"),
                    "field_type": item.get("field_type"),
                    "unit": item.get("unit"),
                    "choices": item.get("choices"),
                    "multi_choice": item.get("multi_choice"),
                }
                for item in payload
            }

    async def get_spools(self, params):
        """Return a list of all spools."""
        _LOGGER.debug("SpoolmanAPI: get_spools")
        url = f"{self.base_url}/spool"
        if len(params) > 0:
            url = f"{url}?{self.string_from_dictionary(params)}"
        session = await self._get_session()
        async with session.get(url) as response:
            response.raise_for_status()
            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: get_spools response %s", response)

            """Decode each item in extra from JSON."""
            for spool in response:
                if "extra" in spool:
                    for key, value in spool["extra"].items():
                        spool["extra"][key] = json.loads(value)

            return response

    async def get_filaments(self, params):
        """Return a list of all filaments."""
        _LOGGER.debug("SpoolmanAPI: get_filaments")
        url = f"{self.base_url}/filament"
        if len(params) > 0:
            url = f"{url}?{self.string_from_dictionary(params)}"
        session = await self._get_session()
        async with session.get(url) as response:
            response.raise_for_status()
            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: get_filaments response %s", response)

            """Decode each item in extra from JSON."""
            for filament in response:
                if "extra" in filament:
                    for key, value in filament["extra"].items():
                        filament["extra"][key] = json.loads(value)

            return response

    async def get_spool_by_id(self, spool_id):
        """Return the spool with the specified ID."""
        _LOGGER.debug("SpoolmanAPI: get_spool_by_id")
        url = f"{self.base_url}/spool/{spool_id}"
        session = await self._get_session()
        async with session.get(url) as response:
            response.raise_for_status()
            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: get_spool_by_id response %s", response)

            """Decode each item in extra from JSON."""
            if "extra" in response:
                for key, value in response["extra"].items():
                    response["extra"][key] = json.loads(value)

            return response

    def string_from_dictionary(self, params_dict):
        """Generate a query string from a dictionary of parameters."""
        _LOGGER.debug("SpoolmanAPI: string_from_dictionary")
        result_string = ""

        # Iterate through the dictionary and concatenate key-value pairs
        for key, value in params_dict.items():
            # Convert the value to a string if it's not already
            if not isinstance(value, str):
                value = str(value)

            # Concatenate the key and value in the desired format
            result_string += f"{key}={value} "

        # Remove the trailing space if needed
        result_string = result_string.strip()

        # Return the result string
        return result_string

    async def patch_spool(self, spool_id, data):
        """Update the spool with the specified ID."""
        _LOGGER.info(f"SpoolmanAPI: patch_spool {spool_id} with data {data}")

        if "remaining_weight" in data and "used_weight" in data:
            if data["remaining_weight"] > 0 and data["used_weight"] > 0:
                raise ValueError(
                    "remaining_weight and used_weight cannot be used together. Please use only one of them."
                )

        """Encode each item in extra as JSON."""
        if "extra" in data:
            for key, value in data["extra"].items():
                data["extra"][key] = json.dumps(value)

        url = f"{self.base_url}/spool/{spool_id}"
        try:
            session = await self._get_session()
            async with session.patch(url, json=data) as response:
                response.raise_for_status()
                response_data = await response.json()
                _LOGGER.debug("SpoolmanAPI: patch_spool response %s", response_data)
                return response_data
        except aiohttp.ClientResponseError as e:
            _LOGGER.error(f"HTTP error occurred: {e.status} {e.message}")
            raise
        except aiohttp.ClientConnectionError as e:
            _LOGGER.error(f"Connection error occurred: {e}")
            raise
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Client error occurred: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"An unexpected error occurred: {e}")
            raise

    async def use_spool_filament(self, spool_id, data):
        """Update the spool filament usage with the specified ID."""
        _LOGGER.info(f"SpoolmanAPI: patch_spool {spool_id} with data {data}")

        if "use_length" in data and "use_weight" in data:
            if data["use_length"] > 0 and data["use_weight"] > 0:
                raise ValueError(
                    "use_length and use_weight cannot be used together. Please use only one of them."
                )

        url = f"{self.base_url}/spool/{spool_id}/use"
        try:
            session = await self._get_session()
            async with session.put(url, json=data) as response:
                response.raise_for_status()
                response_data = await response.json()
                _LOGGER.debug(
                    "SpoolmanAPI: use_spool_filament response %s", response_data
                )
                return response_data
        except aiohttp.ClientResponseError as e:
            _LOGGER.error(f"HTTP error occurred: {e.status} {e.message}")
            raise
        except aiohttp.ClientConnectionError as e:
            _LOGGER.error(f"Connection error occurred: {e}")
            raise
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Client error occurred: {e}")
            raise
        except Exception as e:
            _LOGGER.error(f"An unexpected error occurred: {e}")
            raise
