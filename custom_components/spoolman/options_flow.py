"""Options flow."""
from homeassistant import config_entries
from typing import Any
from homeassistant.data_entry_flow import FlowResult

from .base_flow import BaseFlow
from .schema_helper import SchemaHelper
from .const import (
    CONF_URL,
    SPOOLMAN_INFO_PROPERTY,
)

class OptionsFlowHandler(config_entries.OptionsFlow, BaseFlow):
    """Implementation of the OptionWorkflow."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            info, errors, cleaned_url = await self.test_and_get_info(user_input.get(CONF_URL, ""))

            if not errors:
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        **user_input,
                        CONF_URL: cleaned_url,
                        SPOOLMAN_INFO_PROPERTY: info,
                    }
                )
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)

                return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=SchemaHelper().get_config_schema(True, self.config_entry.data),
            errors=errors,
        )
