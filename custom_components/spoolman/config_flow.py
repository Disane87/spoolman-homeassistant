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
    KLIPPER_URL,
    SPOOLMAN_INFO_PROPERTY,
)


class ConfigFlow(BaseFlow, config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for spoolman."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        spoolman_errors: dict[str, str] = {}
        klipper_errors: dict[str, str] = {}

        if user_input is not None:
            spoolman_info, spoolman_errors, spoolman_url = await self.get_spoolman_api_info(user_input.get(CONF_URL, ""))

            klipper_url = user_input.get(KLIPPER_URL, None)
            if klipper_url is not None and klipper_url != "":
                klipper_info, klipper_errors, klipper_url = await self.get_klipper_api_info(user_input.get(KLIPPER_URL, None))

            if not spoolman_errors and not klipper_errors:
                return self.async_create_entry(
                    title=DOMAIN,
                    data={
                        **user_input,
                        CONF_URL: spoolman_url,
                        SPOOLMAN_INFO_PROPERTY: spoolman_info,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=SchemaHelper().get_config_schema(),
            errors={**spoolman_errors, **klipper_errors},
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
