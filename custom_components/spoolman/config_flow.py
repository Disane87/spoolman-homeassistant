"""Config flow for spoolman integration."""
from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    API_HEALTH_ENDPOINT,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    DOMAIN,
    CONF_SHOW_ARCHIVED,
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for spoolman."""

    VERSION = 1

    def add_trailing_slash(self, input_string):
        """Add traling slashed when not present."""
        if not input_string.endswith("/"):
            input_string += "/"
        return input_string

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            url = self.add_trailing_slash(user_input.get(CONF_URL))

            # Test the API key and URLs here if necessary
            # If valid, create an entry
            # If invalid, set errors
            test_url = f"{url}{API_HEALTH_ENDPOINT}"
            if not errors:
                try:
                    async with aiohttp.ClientSession() as session, session.get(
                        test_url
                    ) as response:
                        if response.status == 200:
                            if "application/json" in response.headers.get(
                                "content-type", ""
                            ):
                                try:
                                    data = await response.json()
                                    if (
                                        isinstance(data, dict)
                                        and data.get("status") == "healthy"
                                    ):
                                        return self.async_create_entry(
                                            title=DOMAIN,
                                            data={**user_input, CONF_URL: url},
                                        )
                                    else:
                                        errors[
                                            CONF_URL
                                        ] = "URL does not return a JSON object with a 'status' property set to 'healthy'"
                                except ValueError:
                                    errors[
                                        CONF_URL
                                    ] = "URL does not return valid JSON data"
                            else:
                                errors[CONF_URL] = "URL does not return JSON content"
                        else:
                            errors[
                                CONF_URL
                            ] = f"Failed to connect to the URL. Status code: {response.status}"
                except Exception as e:
                    errors[CONF_URL] = f"Error testing URL: {str(e)}"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL): str,
                    vol.Optional(CONF_UPDATE_INTERVAL, default=15): vol.All(
                        vol.Coerce(int), vol.Range(min=1)
                    ),
                    vol.Required(CONF_SHOW_ARCHIVED): bool,
                }
            ),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
