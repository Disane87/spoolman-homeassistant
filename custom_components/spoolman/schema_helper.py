"""Schema helper."""
from typing import Any
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .const import (
    CONF_NOTIFICATION_THRESHOLD_CRITICAL,
    CONF_NOTIFICATION_THRESHOLD_INFO,
    CONF_NOTIFICATION_THRESHOLD_WARNING,
    CONF_SHOW_ARCHIVED,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    KLIPPER_URL,
    KLIPPER_URL_DESC,
    NOTIFICATION_THRESHOLDS
)


class SchemaHelper:
    """Schema helper contains the config and options schema."""

    @staticmethod
    def get_spoolman_patch_spool_schema():
        """Get the schema for the spoolman_patch_spool service."""
        return vol.Schema({
            vol.Required('id'): cv.string,
            vol.Optional('first_used'): cv.string,
            vol.Optional('last_used'): cv.string,
            vol.Optional('filament_id'): cv.positive_int,
            vol.Optional('price'): vol.Coerce(float),
            vol.Optional('initial_weight'): vol.Coerce(float),
            vol.Optional('spool_weight'): vol.Coerce(float),
            vol.Optional('remaining_weight'): vol.Coerce(float),
            vol.Optional('used_weight'): vol.Coerce(float),
            vol.Optional('location'): cv.string,
            vol.Optional('lot_nr'): cv.string,
            vol.Optional('comment'): cv.string,
            vol.Optional('archived'): cv.boolean,
            vol.Optional('extra'): vol.Schema({}, extra=vol.ALLOW_EXTRA),
        })

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
            vol.Optional(KLIPPER_URL, msg=KLIPPER_URL_DESC, default=get_default_value(KLIPPER_URL, "")): str,
            vol.Optional(CONF_UPDATE_INTERVAL, default=get_default_value(CONF_UPDATE_INTERVAL, 15)): vol.All(
                vol.Coerce(int), vol.Range(min=1)
            )
        })
