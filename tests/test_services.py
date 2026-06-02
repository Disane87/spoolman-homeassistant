"""Test that registered Spoolman services keep their contract."""

from __future__ import annotations

import re
from typing import Any

import pytest
from aioresponses import aioresponses
from homeassistant.core import HomeAssistant

from custom_components.spoolman.const import (
    DOMAIN,
    SPOOLMAN_PATCH_SPOOL_SERVICENAME,
    SPOOLMAN_USE_SPOOL_FILAMENT_SERVICENAME,
)

from .const import MOCK_URL


async def test_services_registered(hass: HomeAssistant, setup_integration: Any) -> None:
    """Both services must be registered after integration setup."""
    assert hass.services.has_service(DOMAIN, SPOOLMAN_PATCH_SPOOL_SERVICENAME)
    assert hass.services.has_service(DOMAIN, SPOOLMAN_USE_SPOOL_FILAMENT_SERVICENAME)


async def test_patch_spool_service_calls_api(
    hass: HomeAssistant,
    setup_integration: Any,
    mock_spoolman_api: aioresponses,
) -> None:
    """patch_spool dispatches PATCH /api/v1/spool/<id> with the payload."""
    mock_spoolman_api.patch(
        re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool/1.*"),
        payload={"id": 1, "comment": "updated"},
        repeat=True,
    )

    await hass.services.async_call(
        DOMAIN,
        SPOOLMAN_PATCH_SPOOL_SERVICENAME,
        {"id": 1, "comment": "updated"},
        blocking=True,
    )
    await hass.async_block_till_done()

    matched = [k for k in mock_spoolman_api.requests if "api/v1/spool/1" in str(k[1])]
    assert matched, "expected at least one PATCH to /api/v1/spool/1"


async def test_use_spool_filament_service_calls_api(
    hass: HomeAssistant,
    setup_integration: Any,
    mock_spoolman_api: aioresponses,
) -> None:
    """use_spool_filament dispatches PUT /api/v1/spool/<id>/use with the payload."""
    mock_spoolman_api.put(
        re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool/1/use.*"),
        payload={"id": 1, "remaining_weight": 700},
        repeat=True,
    )

    await hass.services.async_call(
        DOMAIN,
        SPOOLMAN_USE_SPOOL_FILAMENT_SERVICENAME,
        {"id": 1, "use_length": 100},
        blocking=True,
    )
    await hass.async_block_till_done()

    matched = [k for k in mock_spoolman_api.requests if "/use" in str(k[1])]
    assert matched, "expected at least one PUT to /spool/1/use"


async def test_patch_spool_service_propagates_api_error(
    hass: HomeAssistant,
    setup_integration: Any,
    mock_spoolman_api: aioresponses,
) -> None:
    """API failures surface as HomeAssistantError so automations can react."""
    from homeassistant.exceptions import HomeAssistantError

    mock_spoolman_api.patch(
        re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool/1.*"),
        status=500,
        repeat=True,
    )

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(
            DOMAIN,
            SPOOLMAN_PATCH_SPOOL_SERVICENAME,
            {"id": 1, "comment": "x"},
            blocking=True,
        )
