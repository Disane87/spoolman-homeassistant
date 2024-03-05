"""Schema helper."""
from typing import Any
import voluptuous as vol
from .const import (
    CONF_NOTIFICATION_THRESHOLD_CRITICAL,
    CONF_NOTIFICATION_THRESHOLD_INFO,
    CONF_NOTIFICATION_THRESHOLD_WARNING,
    CONF_SHOW_ARCHIVED,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    NOTIFICATION_THRESHOLDS
)


class SchemaHelper:
    """Schema helper contains the config and options schema."""

    @staticmethod
    def get_config_schema(get_values=False, config_data=None):
        """Get the form for config and options flows."""
        # Definiere eine Hilfsfunktion, um Standardwerte zu ermitteln
        def get_default_value(key: str, default: Any):
            """Get saved or default values."""
            if get_values and config_data:
                return config_data.get(key, default)
            return default

        return vol.Schema({
            vol.Required(CONF_URL, default=get_default_value(CONF_URL, "")): str,
            vol.Optional(CONF_UPDATE_INTERVAL, default=get_default_value(CONF_UPDATE_INTERVAL, 15)): vol.All(
                vol.Coerce(int), vol.Range(min=1)
            ),
            vol.Required(
                CONF_NOTIFICATION_THRESHOLD_INFO,
                default=get_default_value(CONF_NOTIFICATION_THRESHOLD_INFO, NOTIFICATION_THRESHOLDS.get("info", 0)),
            ): vol.All(int, vol.Range(min=0, max=100)),
            vol.Required(
                CONF_NOTIFICATION_THRESHOLD_WARNING,
                default=get_default_value(CONF_NOTIFICATION_THRESHOLD_WARNING, NOTIFICATION_THRESHOLDS.get("warning", 0)),
            ): vol.All(int, vol.Range(min=0, max=100)),
            vol.Required(
                CONF_NOTIFICATION_THRESHOLD_CRITICAL,
                default=get_default_value(CONF_NOTIFICATION_THRESHOLD_CRITICAL, NOTIFICATION_THRESHOLDS.get("critical", 0)),
            ): vol.All(int, vol.Range(min=0, max=100)),
            vol.Required(CONF_SHOW_ARCHIVED, default=get_default_value(CONF_SHOW_ARCHIVED, False)): bool,
        })
