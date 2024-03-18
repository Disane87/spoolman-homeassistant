"""Options flow."""
from homeassistant import config_entries
from typing import Any
from homeassistant.data_entry_flow import FlowResult

from .base_flow import BaseFlow
from .schema_helper import SchemaHelper
from .const import (
    CONF_URL,
    KLIPPER_URL,
    SPOOLMAN_INFO_PROPERTY,
)

class OptionsFlowHandler(config_entries.OptionsFlow, BaseFlow):
    """Implementation of the OptionWorkflow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        spoolman_errors: dict[str, str] = {}
        klipper_errors: dict[str, str] = {}

        if user_input is not None:
            spoolman_info, spoolman_errors, spoolman_url = await self.get_spoolman_api_info(user_input.get(CONF_URL, ""))

            klipper_url = user_input.get(KLIPPER_URL, None)
            if klipper_url is not None and klipper_url != "":
                klipper_info, klipper_errors, klipper_url = await self.get_klipper_api_info(user_input.get(KLIPPER_URL, None))

            if not spoolman_errors and not klipper_errors:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        **user_input,
                        CONF_URL: spoolman_url,
                        SPOOLMAN_INFO_PROPERTY: spoolman_info,
                    }
                )
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)

                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=SchemaHelper().get_config_schema(True, self.config_entry.data),
            errors={**spoolman_errors, **klipper_errors}
        )
