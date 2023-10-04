"""Config flow for spoolman integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .classes.spoolman_api import SpoolmanAPI
from .const import (
    CONF_NOTIFICATION_THRESHOLD_CRITICAL,
    CONF_NOTIFICATION_THRESHOLD_INFO,
    CONF_NOTIFICATION_THRESHOLD_WARNING,
    CONF_SHOW_ARCHIVED,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    DOMAIN,
    NOTIFICATION_THRESHOLDS,
    SPOOLMAN_INFO_PROPERTY,
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
            if not errors:
                spoolman_api = SpoolmanAPI(url)
                try:
                    healty = await spoolman_api.health()
                    if healty.get("status", None) == "healthy":
                        info = await spoolman_api.info()

                        return self.async_create_entry(
                            title=DOMAIN,
                            data={
                                **user_input,
                                CONF_URL: url,
                                SPOOLMAN_INFO_PROPERTY: info,
                            },
                        )

                except Exception as error_message:
                    errors[CONF_URL] = f"Error testing URL: {str(error_message)}"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL): str,
                    vol.Optional(CONF_UPDATE_INTERVAL, default=15): vol.All(  # type: ignore
                        vol.Coerce(int), vol.Range(min=1)
                    ),
                    vol.Required(
                        CONF_NOTIFICATION_THRESHOLD_INFO,
                        default=NOTIFICATION_THRESHOLDS.get("info", 0),  # type: ignore
                    ): vol.All(int, vol.Range(min=0, max=100)),
                    vol.Required(
                        CONF_NOTIFICATION_THRESHOLD_WARNING,
                        default=NOTIFICATION_THRESHOLDS.get("warning", 0),  # type: ignore
                    ): vol.All(int, vol.Range(min=0, max=100)),
                    vol.Required(
                        CONF_NOTIFICATION_THRESHOLD_CRITICAL,
                        default=NOTIFICATION_THRESHOLDS.get("critical", 0),  # type: ignore
                    ): vol.All(int, vol.Range(min=0, max=100)),
                    vol.Required(CONF_SHOW_ARCHIVED): bool,
                }
            ),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
