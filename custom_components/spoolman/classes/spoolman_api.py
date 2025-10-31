"""Class for interacting with the Spoolman API."""
import aiohttp
import logging
import json
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
        async with aiohttp.ClientSession() as session, session.get(url) as response:
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
        _LOGGER.debug("SpoolmanAPI: get_spools")
        url = f"{self.base_url}/spool"
        if len(params) > 0:
            url = f"{url}?{self.string_from_dictionary(params)}"
        async with aiohttp.ClientSession() as session, session.get(url) as response:
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
        async with aiohttp.ClientSession() as session, session.get(url) as response:
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
        async with aiohttp.ClientSession() as session, session.get(url) as response:
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
                raise ValueError("remaining_weight and used_weight cannot be used together. Please use only one of them.")

        """Encode each item in extra as JSON."""
        if "extra" in data:
            for key, value in data["extra"].items():
                data["extra"][key] = json.dumps(value)

        url = f"{self.base_url}/spool/{spool_id}"
        try:
            async with aiohttp.ClientSession() as session, session.patch(url, json=data) as response:
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
                raise ValueError("use_length and use_weight cannot be used together. Please use only one of them.")

        url = f"{self.base_url}/spool/{spool_id}/use"
        try:
            async with aiohttp.ClientSession() as session, session.put(url, json=data) as response:
                response.raise_for_status()
                response_data = await response.json()
                _LOGGER.debug("SpoolmanAPI: use_spool_filament response %s", response_data)
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
