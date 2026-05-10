"""Base flow for config and options flow."""

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.spoolman.classes.klipper_api import KlipperAPI
from custom_components.spoolman.classes.spoolman_api import SpoolmanAPI
from custom_components.spoolman.const import CONF_URL

from .helpers.add_trailing_slash import add_trailing_slash


class BaseFlow:
    """Shared Flow for Options and Config-Flows."""

    async def get_spoolman_api_info(self, url: str) -> tuple[dict | None, dict, str]:
        """Test the Spoolman URL and return health/info plus normalized URL."""
        errors: dict[str, str] = {}
        info = None
        cleaned_url: str = add_trailing_slash(url)
        spoolman_api = SpoolmanAPI(
            cleaned_url, session=async_get_clientsession(self.hass)
        )

        try:
            healthy = await spoolman_api.health()
            if healthy.get("status") == "healthy":
                info = await spoolman_api.info()
                return info, {}, cleaned_url
        except Exception as error_message:
            errors[CONF_URL] = f"Error testing spoolman url: {error_message!s}"
        return None, errors, cleaned_url

    async def get_klipper_api_info(self, url: str) -> tuple[str | None, dict, str]:
        """Test the Klipper URL and return version info plus normalized URL."""
        errors: dict[str, str] = {}
        cleaned_url: str = add_trailing_slash(url)
        klipper_api = KlipperAPI(
            cleaned_url, session=async_get_clientsession(self.hass)
        )

        try:
            healthy = await klipper_api.api_version()
            if healthy is not None:
                return healthy, {}, cleaned_url
        except Exception as error_message:
            errors[CONF_URL] = f"Error testing klipper url: {error_message!s}"
        return None, errors, cleaned_url
