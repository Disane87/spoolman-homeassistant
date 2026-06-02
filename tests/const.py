"""Shared constants for Spoolman tests."""

from __future__ import annotations

from custom_components.spoolman.const import (
    CONF_NOTIFICATION_THRESHOLD_CRITICAL,
    CONF_NOTIFICATION_THRESHOLD_INFO,
    CONF_NOTIFICATION_THRESHOLD_WARNING,
    CONF_SHOW_ARCHIVED,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    SPOOLMAN_INFO_PROPERTY,
)

MOCK_URL = "http://spoolman.test:7912/"

MOCK_CONFIG_DATA = {
    CONF_URL: MOCK_URL,
    CONF_UPDATE_INTERVAL: 5,
    CONF_SHOW_ARCHIVED: False,
    CONF_NOTIFICATION_THRESHOLD_INFO: 50,
    CONF_NOTIFICATION_THRESHOLD_WARNING: 75,
    CONF_NOTIFICATION_THRESHOLD_CRITICAL: 95,
    # Populated by the config flow in real life — provide stable test values:
    SPOOLMAN_INFO_PROPERTY: {
        "version": "0.20.0",
        "git_commit": "test-commit",
        "build_date": "2024-01-01T00:00:00Z",
    },
}
