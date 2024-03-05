"""Base flow for config and options flow."""
from custom_components.spoolman.classes.spoolman_api import SpoolmanAPI
from custom_components.spoolman.const import CONF_URL
from homeassistant import config_entries


class BaseFlow:
    """Shared Flow for Options and Config-Flows."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    @staticmethod
    def add_trailing_slash(input_string) -> str:
        """Add trailing slash if not present."""
        if not input_string.endswith("/"):
            input_string += "/"
        return input_string

    async def test_and_get_info(self, url: str) -> tuple[dict | None, dict, str]:
        """Tests the connection with the given url and returns health information about the Spoolman API."""
        errors = {}
        info = None  # Initialisiere info explizit als None
        cleaned_url: str = self.add_trailing_slash(url)
        spoolman_api = SpoolmanAPI(url)

        try:
            healthy = await spoolman_api.health()
            if healthy.get("status") == "healthy":
                info = await spoolman_api.info()
                return info, {}, cleaned_url  # Erfolg: Rückgabe von info und leeres error dict
        except Exception as error_message:
            errors[CONF_URL] = f"Error testing URL: {str(error_message)}"
        return None, errors, cleaned_url  # Fehler: Rückgabe von None für info und das errors dict
