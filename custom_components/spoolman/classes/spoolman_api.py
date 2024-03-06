"""Class for interacting with the Spoolman API."""
import aiohttp
import logging
_LOGGER = logging.getLogger(__name__)


class SpoolmanAPI:
    """Class for interacting with the Spoolman API."""

    def __init__(self, base_url, api_version="v1"):
        """Initialize the Spoolman API."""
        _LOGGER.debug("SpoolmanAPI: __init__")
        self.base_url = f"{base_url}api/{api_version}"

    async def info(self):
        """Return information about the API."""
        _LOGGER.debug("SpoolmanAPI: info")
        url = f"{self.base_url}/info"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()
            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: info response %s", response)
            return response

    async def health(self):
        """Return the health status of the API."""
        _LOGGER.debug("SpoolmanAPI: health")
        url = f"{self.base_url}/health"
        async with aiohttp.ClientSession() as session, session.get(
            url, timeout=10
        ) as response:
            response.raise_for_status()
            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: health response %s", response)
            return response

    async def backup(self):
        """Initiate a backup of the API."""
        _LOGGER.debug("SpoolmanAPI: backup")
        url = f"{self.base_url}/backup"
        async with aiohttp.ClientSession() as session, session.post(url) as response:
            response.raise_for_status()

            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: backup response %s", response)
            return response

    async def get_spools(self, params):
        """Return a list of all spools."""
        _LOGGER.debug("SpoolmanAPI: get_spool")
        url = f"{self.base_url}/spool"
        if len(params) > 0:
            url = f"{url}?{self.string_from_dictionary(params)}"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()

            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: get_spool response %s", response)
            return response

    async def get_spool_by_id(self, spool_id):
        """Return the spool with the specified ID."""
        _LOGGER.debug("SpoolmanAPI: get_spool_by_id")
        url = f"{self.base_url}/spool/{spool_id}"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()
            response = await response.json()
            _LOGGER.debug("SpoolmanAPI: get_spool_by_id response %s", response)
            return response

    def string_from_dictionary(self, params_dict):
        """Initialize an empty string to hold the result."""
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
