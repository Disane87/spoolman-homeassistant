"""Base flow for config and options flow."""
from custom_components.spoolman.classes.klipper_api import KlipperAPI
from custom_components.spoolman.classes.spoolman_api import SpoolmanAPI
from custom_components.spoolman.const import CONF_URL

from .helpers.add_trailing_slash import add_trailing_slash

class BaseFlow:
    """Shared Flow for Options and Config-Flows."""

    @staticmethod
    async def get_spoolman_api_info(url: str) -> tuple[dict | None, dict, str]:
        """Test the connection with the given url and return health information about the Spoolman API."""
        errors = {}
        info = None  # Initialisiere info explizit als None
        cleaned_url: str = add_trailing_slash(url)
        spoolman_api = SpoolmanAPI(cleaned_url)

        try:
            healthy = await spoolman_api.health()
            if healthy.get("status") == "healthy":
                info = await spoolman_api.info()
                return info, {}, cleaned_url  # Erfolg: Rückgabe von info und leeres error dict
        except Exception as error_message:
            errors[CONF_URL] = f"Error testing spoolman url: {str(error_message)}"
        return None, errors, cleaned_url  # Fehler: Rückgabe von None für info und das errors dict

    @staticmethod
    async def get_klipper_api_info(url: str) -> tuple[str | None, dict, str]:
        """Test the connection with the given url and return health information about the Klipper API."""
        errors = {}
        cleaned_url: str = add_trailing_slash(url)
        klipper_api = KlipperAPI(cleaned_url)

        try:
            healthy = await klipper_api.api_version()
            if healthy is not None:
                return healthy, {}, cleaned_url  # Erfolg: Rückgabe von info und leeres error dict
        except Exception as error_message:
            errors[CONF_URL] = f"Error testing klipper url: {str(error_message)}"
        return None, errors, cleaned_url  # Fehler: Rückgabe von None für info und das errors dict
