"""Config flow for spoolman integration."""
from __future__ import annotations

from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.core import callback
from .base_flow import BaseFlow

from .options_flow import OptionsFlowHandler
from .schema_helper import SchemaHelper
from .const import (
    CONF_URL,
    DOMAIN,
    SPOOLMAN_INFO_PROPERTY,
)


class ConfigFlow(config_entries.ConfigFlow, BaseFlow, domain=DOMAIN):
    """Handle a config flow for spoolman."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

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
            info, errors, cleaned_url = await self.test_and_get_info(user_input.get(CONF_URL, ""))

            if not errors:
                return self.async_create_entry(
                    title=DOMAIN,
                    data={
                        **user_input,
                        CONF_URL: cleaned_url,
                        SPOOLMAN_INFO_PROPERTY: info,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=SchemaHelper().get_config_schema(),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
