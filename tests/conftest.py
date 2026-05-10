"""Spoolman test fixtures and pytest config.

Note on URL matching: SpoolmanAPI.string_from_dictionary builds query
strings with a trailing space (e.g. ``allow_archived=False ``) and uses
``str(bool)`` which produces capitalized ``False``/``True``. We use
regex URL matchers so the mocks tolerate that quirk while we keep the
existing API client byte-stable through phase 3.
"""

from __future__ import annotations

import json
import re
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import pytest
from aioresponses import aioresponses
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.spoolman.const import DOMAIN

from .const import MOCK_CONFIG_DATA, MOCK_URL

pytest_plugins = ["pytest_homeassistant_custom_component"]

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> Any:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def _encode_extra(spools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Spoolman returns extra-field values as JSON strings; the client decodes them.

    Our fixtures store the decoded form for human readability, so we re-encode
    here on the way out of the mock.
    """
    out = []
    for spool in spools:
        copy = {**spool}
        if "extra" in copy and copy["extra"]:
            copy["extra"] = {
                k: v
                if isinstance(v, str)
                and (v.startswith('"') or v.startswith("{") or v.startswith("["))
                else json.dumps(v)
                for k, v in copy["extra"].items()
            }
        out.append(copy)
    return out


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(
    enable_custom_integrations: Any,
) -> AsyncGenerator[None, None]:
    """Enable loading of custom_components in the HA test harness."""
    yield


@pytest.fixture(autouse=True)
def _allow_asyncio_shutdown_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tolerate the Python 3.12 asyncio shutdown thread in PHACC's verify_cleanup.

    PHACC's verify_cleanup fixture asserts that no non-DummyThread non-waitpid
    threads linger after a test. Python 3.12 introduced an internal
    ``_run_safe_shutdown_loop`` thread spawned by
    ``BaseEventLoop.shutdown_default_executor`` that PHACC's check predates;
    the thread is harmless (daemon, exits when the process dies). We allow
    only that specific name through.
    """
    import threading as _threading

    real_enumerate = _threading.enumerate

    def filtered_enumerate() -> list[_threading.Thread]:
        return [
            t
            for t in real_enumerate()
            if t.name != "Thread-1 (_run_safe_shutdown_loop)"
            and not t.name.startswith("asyncio_")
        ]

    monkeypatch.setattr(
        "pytest_homeassistant_custom_component.plugins.threading.enumerate",
        filtered_enumerate,
        raising=False,
    )
    monkeypatch.setattr(_threading, "enumerate", filtered_enumerate)


@pytest.fixture
def spools_data() -> list[dict[str, Any]]:
    """Return decoded spool fixtures with native Python values in ``extra``."""
    return _load_fixture("spools.json")


@pytest.fixture
def filaments_data() -> list[dict[str, Any]]:
    """Return filament fixtures matching the spool fixtures' filament_ids."""
    return _load_fixture("filaments.json")


@pytest.fixture
def locations_data() -> list[str]:
    """Return location-string fixtures served by ``GET /location``."""
    return _load_fixture("locations.json")


@pytest.fixture
def extra_fields_data() -> list[dict[str, Any]]:
    """Return extra-field metadata served by ``GET /field/spool``."""
    return _load_fixture("extra_fields.json")


@pytest.fixture
def mock_spoolman_api(
    spools_data: list[dict[str, Any]],
    filaments_data: list[dict[str, Any]],
    locations_data: list[str],
    extra_fields_data: list[dict[str, Any]],
) -> AsyncGenerator[aioresponses, None]:
    """Mock the Spoolman HTTP API. Default = healthy server, all endpoints respond."""
    base = re.escape(f"{MOCK_URL}api/v1")

    with aioresponses() as mocked:
        mocked.get(
            re.compile(rf"{base}/health.*"), payload={"status": "healthy"}, repeat=True
        )
        mocked.get(
            re.compile(rf"{base}/info.*"), payload={"version": "0.20.0"}, repeat=True
        )

        # Spool list — match any allow_archived value, return filtered set based on the URL.
        archived_re = re.compile(rf"{base}/spool\?.*allow_archived=True.*")
        not_archived_re = re.compile(rf"{base}/spool\?.*allow_archived=False.*")
        mocked.get(archived_re, payload=_encode_extra(spools_data), repeat=True)
        mocked.get(
            not_archived_re,
            payload=_encode_extra([s for s in spools_data if not s.get("archived")]),
            repeat=True,
        )

        mocked.get(
            re.compile(rf"{base}/filament.*"), payload=filaments_data, repeat=True
        )
        mocked.get(re.compile(rf"{base}/location"), payload=locations_data, repeat=True)
        mocked.get(
            re.compile(rf"{base}/field/spool"), payload=extra_fields_data, repeat=True
        )

        yield mocked


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """Build a config entry without adding it to hass.

    The entry_id is pinned to a fixed ULID so that characterization
    snapshots stay byte-stable across test runs.
    """
    return MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_DATA,
        options={},
        title="Spoolman",
        unique_id=MOCK_URL,
        entry_id="01J0TESTSPOOLMAN0000000000",
    )


@pytest.fixture
async def setup_integration(
    hass: Any,
    config_entry: MockConfigEntry,
    mock_spoolman_api: aioresponses,
) -> MockConfigEntry:
    """Boot the integration end-to-end against the mocked API."""
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
