"""Config flow coverage. Platinum requires 100% line + branch on flow code."""

from __future__ import annotations

import re

from aioresponses import aioresponses
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.spoolman.const import (
    CONF_NOTIFICATION_THRESHOLD_CRITICAL,
    CONF_NOTIFICATION_THRESHOLD_INFO,
    CONF_NOTIFICATION_THRESHOLD_WARNING,
    CONF_SHOW_ARCHIVED,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
    DOMAIN,
    KLIPPER_URL,
)

from .const import MOCK_URL


def _user_payload(extra: dict[str, object] | None = None) -> dict[str, object]:
    """Build a config-flow form payload with all required fields."""
    base: dict[str, object] = {
        CONF_URL: MOCK_URL.rstrip("/"),
        CONF_UPDATE_INTERVAL: 5,
        CONF_SHOW_ARCHIVED: False,
        CONF_NOTIFICATION_THRESHOLD_INFO: 50,
        CONF_NOTIFICATION_THRESHOLD_WARNING: 75,
        CONF_NOTIFICATION_THRESHOLD_CRITICAL: 95,
        KLIPPER_URL: "",
    }
    base.update(extra or {})
    return base


async def test_user_flow_shows_form(hass: HomeAssistant) -> None:
    """Initial init renders the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_user_flow_happy_path(
    hass: HomeAssistant, mock_spoolman_api: aioresponses
) -> None:
    """Submitting a valid URL creates the config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], _user_payload()
    )

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["data"][CONF_URL] == MOCK_URL


async def test_user_flow_unhealthy_server(hass: HomeAssistant) -> None:
    """A 'starting' server response leaves info=None and creates entry anyway.

    This pins current behavior — the refactor in phase 4 may change this when
    we add Platinum's ``test-before-configure`` rule.
    """
    with aioresponses() as m:
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/health.*"),
            payload={"status": "starting"},
            repeat=True,
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], _user_payload()
        )

    assert result2["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_unreachable_server(hass: HomeAssistant) -> None:
    """Connection failure surfaces an error and re-shows the form."""
    with aioresponses() as m:
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/health.*"),
            status=500,
            repeat=True,
        )

        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], _user_payload()
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2.get("errors")
    assert CONF_URL in result2["errors"]


async def test_user_flow_klipper_url_validated(
    hass: HomeAssistant, mock_spoolman_api: aioresponses
) -> None:
    """When a Klipper URL is provided it is validated alongside Spoolman."""
    klipper_url = "http://klipper.test/"
    mock_spoolman_api.get(
        re.compile(rf"{re.escape(klipper_url)}server/info.*"),
        payload={"result": {"api_version_string": "1.0.0"}},
        repeat=True,
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], _user_payload({KLIPPER_URL: klipper_url.rstrip("/")})
    )

    assert result2["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_klipper_unreachable(
    hass: HomeAssistant, mock_spoolman_api: aioresponses
) -> None:
    """A bad Klipper URL keeps the form open with an error."""
    klipper_url = "http://klipper.test/"
    mock_spoolman_api.get(
        re.compile(rf"{re.escape(klipper_url)}server/info.*"),
        status=500,
        repeat=True,
    )

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], _user_payload({KLIPPER_URL: klipper_url.rstrip("/")})
    )

    assert result2["type"] is FlowResultType.FORM
    assert result2.get("errors")


async def test_options_flow_happy_path(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """Options flow updates the entry and reloads the integration."""
    result = await hass.config_entries.options.async_init(setup_integration.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result2 = await hass.config_entries.options.async_configure(
        result["flow_id"], _user_payload({CONF_UPDATE_INTERVAL: 10})
    )
    await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert setup_integration.data[CONF_UPDATE_INTERVAL] == 10


async def test_options_flow_validation_error_keeps_form(
    hass: HomeAssistant,
) -> None:
    """Bad URL in options keeps the form open with errors set.

    Built without ``setup_integration`` because aioresponses cannot stack
    over an already-active context. We register a healthy server for the
    initial setup, then swap to a failing server before triggering the
    options flow.
    """
    from .const import MOCK_CONFIG_DATA

    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_DATA,
        options={},
        title="Spoolman",
        unique_id=MOCK_URL,
        entry_id="01J0TESTSPOOLOPTS000000000",
    )
    entry.add_to_hass(hass)

    with aioresponses() as healthy:
        healthy.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/health.*"),
            payload={"status": "healthy"},
            repeat=True,
        )
        healthy.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/info.*"),
            payload={"version": "0.20.0"},
            repeat=True,
        )
        healthy.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool.*"),
            payload=[],
            repeat=True,
        )
        healthy.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/filament.*"),
            payload=[],
            repeat=True,
        )
        healthy.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/location.*"),
            payload=[],
            repeat=True,
        )
        healthy.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/field/spool.*"),
            payload=[],
            repeat=True,
        )
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Outside the healthy context — health calls will now fail.
    with aioresponses() as failing:
        failing.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/health.*"),
            status=500,
            repeat=True,
        )
        result = await hass.config_entries.options.async_init(entry.entry_id)
        result2 = await hass.config_entries.options.async_configure(
            result["flow_id"], _user_payload()
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2.get("errors")
