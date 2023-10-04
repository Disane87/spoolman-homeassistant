"""Class for interacting with the Spoolman API."""
import aiohttp


class SpoolmanAPI:
    """Class for interacting with the Spoolman API."""

    def __init__(self, base_url, api_version="v1"):
        """Initialize the Spoolman API."""
        self.base_url = f"{base_url}api/{api_version}"

    async def info(self):
        """Return information about the API."""
        url = f"{self.base_url}/info"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def health(self):
        """Return the health status of the API."""
        url = f"{self.base_url}/health"
        async with aiohttp.ClientSession() as session, session.get(
            url, timeout=10
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def backup(self):
        """Initiate a backup of the API."""
        url = f"{self.base_url}/backup"
        async with aiohttp.ClientSession() as session, session.post(url) as response:
            response.raise_for_status()
            return await response.json()

    async def get_spool(self, params):
        """Return a list of all spools."""
        url = f"{self.base_url}/spool"
        if len(params) > 0:
            url = f"{url}?{self.string_from_dictionary(params)}"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def get_spool_by_id(self, spool_id):
        """Return the spool with the specified ID."""
        url = f"{self.base_url}/spool/{spool_id}"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    def string_from_dictionary(self, params_dict):
        """Initialize an empty string to hold the result."""
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
