"""Tests for the SpoolmanAPI client error paths and edge cases."""

from __future__ import annotations

import re

import aiohttp
import pytest
from aioresponses import aioresponses
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.spoolman.classes.spoolman_api import SpoolmanAPI

from .const import MOCK_URL


async def test_get_spool_by_id_decodes_extra(hass: HomeAssistant) -> None:
    """``extra`` values are JSON-decoded on the way out."""
    with aioresponses() as m:
        m.get(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool/1"),
            payload={"id": 1, "extra": {"sticker_color": '"red"'}},
            repeat=True,
        )
        api = SpoolmanAPI(MOCK_URL, session=async_get_clientsession(hass))
        result = await api.get_spool_by_id(1)
    assert result["extra"]["sticker_color"] == "red"


async def test_patch_spool_rejects_conflicting_weights(hass: HomeAssistant) -> None:
    """remaining_weight + used_weight together is a client-side error."""
    api = SpoolmanAPI(MOCK_URL, session=async_get_clientsession(hass))
    with pytest.raises(ValueError):
        await api.patch_spool(1, {"remaining_weight": 100, "used_weight": 200})


async def test_use_spool_filament_rejects_conflicting_amounts(
    hass: HomeAssistant,
) -> None:
    """use_length + use_weight together is a client-side error."""
    api = SpoolmanAPI(MOCK_URL, session=async_get_clientsession(hass))
    with pytest.raises(ValueError):
        await api.use_spool_filament(1, {"use_length": 1, "use_weight": 2})


async def test_patch_spool_propagates_http_error(hass: HomeAssistant) -> None:
    """HTTP 4xx/5xx surfaces as a ClientResponseError."""
    with aioresponses() as m:
        m.patch(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool/1"),
            status=500,
            repeat=True,
        )
        api = SpoolmanAPI(MOCK_URL, session=async_get_clientsession(hass))
        with pytest.raises(aiohttp.ClientError):
            await api.patch_spool(1, {"comment": "x"})


async def test_patch_spool_encodes_extra_as_json(hass: HomeAssistant) -> None:
    """``extra`` values get JSON-encoded on the way in."""
    received_payload: dict = {}

    def _capture(url, **kwargs):  # noqa: ANN001 — aioresponses callback
        received_payload.update(kwargs.get("json", {}))
        return aiohttp.web.json_response({"id": 1})

    with aioresponses() as m:
        m.patch(
            re.compile(rf"{re.escape(MOCK_URL)}api/v1/spool/1"),
            payload={"id": 1},
            repeat=True,
        )
        api = SpoolmanAPI(MOCK_URL, session=async_get_clientsession(hass))
        await api.patch_spool(1, {"extra": {"sticker_color": "red"}})

        # Inspect the recorded request payload via aioresponses' history:
        sent = list(m.requests.values())[0][0].kwargs["json"]
        assert sent["extra"]["sticker_color"] == '"red"'


async def test_close_only_closes_owned_session() -> None:
    """A SpoolmanAPI given an external session must NOT close it."""
    session = aiohttp.ClientSession()
    api = SpoolmanAPI(MOCK_URL, session=session)
    await api.close()
    assert not session.closed
    await session.close()
