# Spoolman HA Platinum Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the 27-file sensor zoo into a single EntityDescription-driven class, build a real test suite from scratch (currently 0% real coverage — existing tests are copy-paste leftovers from `mail_and_packages`), enforce a hard 90% coverage gate in CI and pre-commit, and reach Home Assistant's **Platinum** Integration Quality Scale as a custom component.

**Architecture:**
- Phase 1 builds the test foundation so phase 2 can refactor without regressions.
- Phase 2 captures characterization snapshots of *current* output (all entity_ids, unique_ids, states, attributes, device structure) — the snapshot is the regression contract.
- Phase 3 collapses 27 sensor files into one `SpoolmanSensor` class + a list of `SpoolmanSensorEntityDescription`s with `value_fn`/`exists_fn`. Snapshot must stay byte-identical.
- Phase 4 hits each Platinum rule: strict typing, `entry.runtime_data`, `parallel_updates`, `ConfigEntryNotReady`, full strings/translations, 100% config-flow coverage, `quality_scale.yaml`.
- Phase 5 finalizes docs, hassfest, HACS, and self-assessment.

**Tech Stack:** Python 3.13, Home Assistant Core (latest stable), `pytest-homeassistant-custom-component`, `pytest-cov`, `aioresponses`, `syrupy` (snapshot testing), `mypy --strict`, `ruff`, `pre-commit`.

**Hard Constraints (read every task with these in mind):**
1. **Zero regressions.** Every existing entity_id, unique_id, attribute, and service signature must survive byte-identically through phase 3. Phase 4 may rename internals but never user-visible IDs.
2. **TDD always.** Write the failing test → run it → implement → run it green → commit. No exceptions.
3. **Coverage gate is 90% global, hard fail.** Local pre-commit + CI both enforce.
4. **Klipper code stays deprecated** but functional until a separately-tracked removal release. Don't delete it in this plan.

---

## File Structure (post-refactor)

```
custom_components/spoolman/
├── __init__.py                  # async_setup_entry, runtime_data wiring, services
├── api.py                       # (renamed from classes/spoolman_api.py)
├── api_klipper.py               # (renamed from classes/klipper_api.py) - deprecated
├── binary_sensor.py             # uses EntityDescription pattern
├── config_flow.py
├── const.py
├── coordinator.py               # SpoolManCoordinator with typed `_async_update_data`
├── diagnostics.py               # NEW (Platinum requirement)
├── entity.py                    # NEW: SpoolmanEntity base class (replaces sensors/base.py)
├── manifest.json
├── models.py                    # NEW: TypedDicts for SpoolData/FilamentData/CoordinatorData
├── options_flow.py
├── quality_scale.yaml           # NEW (Platinum self-assessment)
├── schema_helper.py
├── select.py                    # uses EntityDescription pattern
├── sensor.py                    # SpoolmanSensor class + SENSOR_DESCRIPTIONS registry
├── sensor_descriptions.py       # NEW: all SpoolmanSensorEntityDescription instances
├── sensor_complex.py            # NEW: 5 complex sensors (RunOut, FlowRate, UsedPct, ExtraField, ColorHex w/ image)
├── services.yaml
├── strings.json                 # NEW (or expanded — Platinum needs full coverage)
├── translations/
└── helpers/                     # unchanged

tests/
├── __init__.py
├── conftest.py                  # REPLACED — Spoolman fixtures
├── const.py                     # REPLACED — Spoolman fixture data
├── fixtures/
│   ├── spools.json              # NEW
│   ├── filaments.json           # NEW
│   ├── extra_fields.json        # NEW
│   └── locations.json           # NEW
├── snapshots/                   # NEW (syrupy)
├── test_init.py                 # REPLACED
├── test_config_flow.py          # REPLACED — 100% coverage of all paths
├── test_options_flow.py         # NEW
├── test_coordinator.py          # NEW
├── test_sensor.py               # REPLACED — characterization + per-description tests
├── test_binary_sensor.py        # NEW
├── test_select.py               # NEW
├── test_services.py             # NEW
├── test_diagnostics.py          # REPLACED
├── test_api.py                  # NEW
└── test_models.py               # NEW

.github/workflows/
├── pr_tests.yml                 # MODIFIED — runs tests + coverage gate
├── tests.yml                    # NEW — reusable test workflow
└── lint.yml                     # MODIFIED — add mypy

.pre-commit-config.yaml          # MODIFIED — modern ruff, mypy, pytest-cov
pyproject.toml                   # MODIFIED — pytest, coverage, mypy config
requirements_test.txt            # NEW
```

---

# PHASE 1 — Test Foundation

Goal: a runnable, fixture-driven test suite that boots the integration end-to-end against a mocked Spoolman API. No refactor yet. By the end of phase 1, `pytest --cov` runs green and reports a baseline coverage number.

---

### Task 1.1: Wipe stale `mail_and_packages` tests

**Files:**
- Delete: `tests/conftest.py`, `tests/const.py`, `tests/test_camera.py`, `tests/test_config_flow.py`, `tests/test_diagnostics.py`, `tests/test_helpers.py`, `tests/test_init.py`, `tests/test_sensor.py`, `tests/test_emails/`
- Keep: `tests/__init__.py`

- [ ] **Step 1: Verify the stale tests reference `mail_and_packages`**

```bash
grep -l mail_and_packages tests/
```
Expected: lists every test file plus conftest.py and const.py.

- [ ] **Step 2: Delete the stale files**

```bash
rm tests/conftest.py tests/const.py tests/test_camera.py tests/test_config_flow.py tests/test_diagnostics.py tests/test_helpers.py tests/test_init.py tests/test_sensor.py
rm -r tests/test_emails
```

- [ ] **Step 3: Confirm only `__init__.py` remains**

```bash
ls tests/
```
Expected: `__init__.py` only.

- [ ] **Step 4: Commit**

```bash
git add -A tests/
git commit -m "test: remove stale mail_and_packages copy-paste leftovers

These tests were never adapted to Spoolman and have been failing/ignored
since the integration was forked. Removing them so phase 1 of the
platinum refactor can build a real test suite from scratch."
```

---

### Task 1.2: Add test dependencies

**Files:**
- Create: `requirements_test.txt`
- Modify: `pyproject.toml`

- [ ] **Step 1: Create `requirements_test.txt`**

```text
# Test dependencies — pin majors, allow patches.
pytest>=8.3,<9
pytest-homeassistant-custom-component>=0.13.180
pytest-cov>=5.0
pytest-asyncio>=0.24
aioresponses>=0.7.6
syrupy>=4.7
mypy>=1.13
freezegun>=1.5
```

- [ ] **Step 2: Append pytest + coverage config to `pyproject.toml`**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = [
    "-ra",
    "--strict-markers",
    "--cov=custom_components.spoolman",
    "--cov-report=term-missing",
    "--cov-report=xml",
    "--cov-fail-under=90",
]

[tool.coverage.run]
source = ["custom_components/spoolman"]
branch = true
omit = [
    "custom_components/spoolman/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
show_missing = true
skip_covered = false

[tool.mypy]
python_version = "3.13"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_any_generics = true
disallow_untyped_defs = true
no_implicit_optional = true
plugins = []

[[tool.mypy.overrides]]
module = ["homeassistant.*", "pytest_homeassistant_custom_component.*", "aioresponses.*"]
ignore_missing_imports = true
```

- [ ] **Step 3: Install and verify**

```bash
pip install -r requirements_test.txt
pytest --collect-only
```
Expected: pytest collects 0 tests (we deleted them) but does not error on configuration.

- [ ] **Step 4: Commit**

```bash
git add requirements_test.txt pyproject.toml
git commit -m "test: add pytest, coverage, mypy tooling configuration

Sets up the 90% coverage gate, mypy --strict, and pytest-homeassistant-custom-component.
The gate fails CI immediately; tests will be written in subsequent commits."
```

---

### Task 1.3: Create fixture data

**Files:**
- Create: `tests/fixtures/spools.json`
- Create: `tests/fixtures/filaments.json`
- Create: `tests/fixtures/locations.json`
- Create: `tests/fixtures/extra_fields.json`

- [ ] **Step 1: Create `tests/fixtures/spools.json`** — three spools covering the variation matrix: complete data, sparse data (most optional fields missing), archived.

```json
[
  {
    "id": 1,
    "registered": "2024-01-15T10:00:00Z",
    "first_used": "2024-02-01T12:00:00Z",
    "last_used": "2024-05-01T14:30:00Z",
    "filament": {
      "id": 10,
      "name": "PLA Basic",
      "material": "PLA",
      "density": 1.24,
      "diameter": 1.75,
      "weight": 1000,
      "color_hex": "FF6600",
      "settings_extruder_temp": 210,
      "settings_bed_temp": 60,
      "article_number": "BL-PLA-001",
      "vendor": {"id": 1, "name": "Bambu Lab"}
    },
    "remaining_weight": 750,
    "used_weight": 250,
    "remaining_length": 248.5,
    "used_length": 82.8,
    "price": 24.99,
    "spool_weight": 200,
    "lot_nr": "LOT-A-2024",
    "comment": "Used for benchies",
    "location": "Shelf A",
    "archived": false,
    "extra": {"sticker_color": "\"red\"", "internal_id": "42"}
  },
  {
    "id": 2,
    "registered": "2024-03-01T09:00:00Z",
    "filament": {
      "id": 11,
      "name": null,
      "material": "PETG",
      "color_hex": "00AA00",
      "vendor": {}
    },
    "remaining_weight": 1000,
    "used_weight": 0,
    "remaining_length": 330,
    "used_length": 0,
    "location": "Shelf B",
    "archived": false,
    "extra": {}
  },
  {
    "id": 3,
    "registered": "2023-06-01T08:00:00Z",
    "filament": {"id": 12, "name": "Old PLA", "material": "PLA", "vendor": {"name": "Generic"}},
    "remaining_weight": 0,
    "used_weight": 1000,
    "archived": true,
    "extra": {}
  }
]
```

- [ ] **Step 2: Create `tests/fixtures/filaments.json`**

```json
[
  {"id": 10, "name": "PLA Basic", "material": "PLA", "color_hex": "FF6600", "vendor": {"id": 1, "name": "Bambu Lab"}},
  {"id": 11, "name": null, "material": "PETG", "color_hex": "00AA00", "vendor": {}},
  {"id": 12, "name": "Old PLA", "material": "PLA", "vendor": {"name": "Generic"}}
]
```

- [ ] **Step 3: Create `tests/fixtures/locations.json`**

```json
["Shelf A", "Shelf B", "Drawer 1"]
```

- [ ] **Step 4: Create `tests/fixtures/extra_fields.json`**

```json
[
  {"key": "sticker_color", "name": "Sticker color", "field_type": "text"},
  {"key": "internal_id", "name": "Internal ID", "field_type": "integer"}
]
```

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/
git commit -m "test: add Spoolman API fixture data covering the spool variation matrix

Three spools: full-data, sparse-data, archived. Plus filaments,
locations, and extra-field metadata. Used by every integration test."
```

---

### Task 1.4: Build `conftest.py` — Spoolman API mock

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/const.py`

- [ ] **Step 1: Write `tests/const.py`**

```python
"""Shared constants for Spoolman tests."""
from __future__ import annotations

from custom_components.spoolman.const import (
    CONF_NOTIFICATION_THRESHOLD_CRITICAL,
    CONF_NOTIFICATION_THRESHOLD_INFO,
    CONF_NOTIFICATION_THRESHOLD_WARNING,
    CONF_SHOW_ARCHIVED,
    CONF_UPDATE_INTERVAL,
    CONF_URL,
)

MOCK_URL = "http://spoolman.test:7912/"

MOCK_CONFIG_DATA = {
    CONF_URL: MOCK_URL,
    CONF_UPDATE_INTERVAL: 5,
    CONF_SHOW_ARCHIVED: False,
    CONF_NOTIFICATION_THRESHOLD_INFO: 50,
    CONF_NOTIFICATION_THRESHOLD_WARNING: 75,
    CONF_NOTIFICATION_THRESHOLD_CRITICAL: 95,
}
```

- [ ] **Step 2: Write `tests/conftest.py`**

```python
"""Spoolman test fixtures and pytest config."""
from __future__ import annotations

import json
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


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of custom_components in HA test harness."""
    yield


@pytest.fixture
def spools_data() -> list[dict[str, Any]]:
    return _load_fixture("spools.json")


@pytest.fixture
def filaments_data() -> list[dict[str, Any]]:
    return _load_fixture("filaments.json")


@pytest.fixture
def locations_data() -> list[str]:
    return _load_fixture("locations.json")


@pytest.fixture
def extra_fields_data() -> list[dict[str, Any]]:
    return _load_fixture("extra_fields.json")


@pytest.fixture
def mock_spoolman_api(spools_data, filaments_data, locations_data, extra_fields_data):
    """Mock the Spoolman HTTP API. Default = healthy server, all endpoints respond."""
    with aioresponses() as mocked:
        # Match BOTH archived=true and archived=false param combinations.
        mocked.get(
            f"{MOCK_URL}api/v1/spool?allow_archived=false",
            payload=[s for s in spools_data if not s.get("archived")],
            repeat=True,
        )
        mocked.get(
            f"{MOCK_URL}api/v1/spool?allow_archived=true",
            payload=spools_data,
            repeat=True,
        )
        mocked.get(f"{MOCK_URL}api/v1/filament", payload=filaments_data, repeat=True)
        mocked.get(f"{MOCK_URL}api/v1/location", payload=locations_data, repeat=True)
        mocked.get(
            f"{MOCK_URL}api/v1/field/spool", payload=extra_fields_data, repeat=True
        )
        yield mocked


@pytest.fixture
async def config_entry(hass) -> MockConfigEntry:
    """Add a config entry to hass without setting it up."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_CONFIG_DATA,
        options={},
        title="Spoolman",
        unique_id=MOCK_URL,
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def setup_integration(hass, config_entry, mock_spoolman_api):
    """Boot the integration end-to-end against the mocked API."""
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
```

- [ ] **Step 3: Run pytest collection to confirm fixtures load**

```bash
pytest --collect-only -q
```
Expected: collects 0 tests, no fixture errors.

- [ ] **Step 4: Commit**

```bash
git add tests/conftest.py tests/const.py
git commit -m "test: add Spoolman conftest with API mock and end-to-end fixtures

Provides mock_spoolman_api (aioresponses-based) and setup_integration
fixtures so tests can exercise the integration end-to-end without
hitting a real Spoolman server."
```

---

### Task 1.5: First sanity test — integration boots

**Files:**
- Create: `tests/test_init.py`

- [ ] **Step 1: Write the failing test**

```python
"""Test setup/unload of the Spoolman integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant


async def test_setup_and_unload(hass: HomeAssistant, setup_integration) -> None:
    """The integration sets up cleanly and unloads cleanly."""
    entry = setup_integration
    assert entry.state is ConfigEntryState.LOADED

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_creates_entities(hass: HomeAssistant, setup_integration) -> None:
    """At least the two non-archived spools produce entities."""
    states = hass.states.async_all()
    assert any(s.entity_id.startswith("sensor.spoolman_spool_1") for s in states)
    assert any(s.entity_id.startswith("sensor.spoolman_spool_2") for s in states)
```

- [ ] **Step 2: Run it**

```bash
pytest tests/test_init.py -v
```
Expected: PASS (existing code already supports this — we're verifying the harness, not new behavior). If it fails on coverage gate, that's expected at this point.

- [ ] **Step 3: Confirm coverage report appears**

```bash
pytest tests/test_init.py --cov-report=term --no-cov-on-fail
```
Expected: a coverage table prints. Number will be low (~15-25%); coverage gate fail is fine for this task.

- [ ] **Step 4: Commit**

```bash
git add tests/test_init.py
git commit -m "test: add integration setup/unload sanity test

First real test for this codebase. Verifies the integration boots
against the mocked Spoolman API and produces sensor entities."
```

---

### Task 1.6: Wire CI to run tests + coverage gate

**Files:**
- Create: `.github/workflows/tests.yml`
- Modify: `.github/workflows/pr_tests.yml`

- [ ] **Step 1: Create reusable test workflow**

```yaml
# .github/workflows/tests.yml
name: "Tests"

on:
  workflow_call:

jobs:
  pytest:
    name: "Pytest + 90% coverage gate"
    runs-on: "ubuntu-latest"
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6.2.0
        with:
          python-version: "3.13"
          cache: "pip"
      - name: Install runtime requirements
        run: pip install -r requirements.txt
      - name: Install test requirements
        run: pip install -r requirements_test.txt
      - name: Run pytest
        run: pytest
      - name: Upload coverage XML
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-xml
          path: coverage.xml

  mypy:
    name: "Mypy --strict"
    runs-on: "ubuntu-latest"
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6.2.0
        with:
          python-version: "3.13"
          cache: "pip"
      - run: pip install -r requirements.txt -r requirements_test.txt
      - run: mypy custom_components/spoolman
```

- [ ] **Step 2: Modify `pr_tests.yml` to call it**

```yaml
name: PR Tests

on:
  pull_request:
    branches: ['dev', 'main']
    paths: ['custom_components/**', 'tests/**', 'pyproject.toml', 'requirements*.txt']

jobs:
  lint:
    uses: ./.github/workflows/lint.yml
  tests:
    uses: ./.github/workflows/tests.yml
```

- [ ] **Step 3: Commit and push to verify on CI**

```bash
git add .github/workflows/tests.yml .github/workflows/pr_tests.yml
git commit -m "ci: run pytest with 90% coverage gate and mypy --strict on every PR

The coverage gate is hard-fail. Until enough tests are written in the
remaining tasks, CI on this branch will be red — that is intentional and
the signal driving the rest of phase 1+2."
git push
```

Expected: PR CI shows test job running, coverage failing under 90%, mypy reporting many errors. That is the baseline; subsequent phases close it.

---

### Task 1.7: Modernize pre-commit and wire git hooks

**Files:**
- Modify: `.pre-commit-config.yaml`
- Create: `scripts/install-hooks.sh`

- [ ] **Step 1: Replace `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: debug-statements
      - id: detect-private-key

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        files: ^custom_components/spoolman/
        additional_dependencies:
          - homeassistant
          - aiohttp
          - voluptuous

  - repo: local
    hooks:
      - id: pytest-fast
        name: pytest (fast unit tests, no coverage)
        entry: pytest -x -q --no-cov tests/
        language: system
        pass_filenames: false
        stages: [pre-push]
      - id: pytest-coverage
        name: pytest with 90% coverage gate
        entry: pytest
        language: system
        pass_filenames: false
        stages: [pre-push]
        # only runs on `git push`, not every commit, to keep commits fast
```

- [ ] **Step 2: Create installer script**

```bash
# scripts/install-hooks.sh
#!/usr/bin/env bash
set -euo pipefail
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
echo "Git hooks installed: pre-commit (lint+type) and pre-push (tests+coverage)."
```

```bash
chmod +x scripts/install-hooks.sh
```

- [ ] **Step 3: Run it locally and confirm hooks fire**

```bash
bash scripts/install-hooks.sh
pre-commit run --all-files
```
Expected: ruff, mypy, etc. run. Errors are OK at this point — we just verify the wiring.

- [ ] **Step 4: Document in CONTRIBUTING.md** (append a "Local development" section if missing — show the install command and what each hook does).

- [ ] **Step 5: Commit**

```bash
git add .pre-commit-config.yaml scripts/install-hooks.sh CONTRIBUTING.md
git commit -m "tooling: modernize pre-commit, add pre-push test hook, hook installer

- pre-commit on every commit: ruff (lint+format), mypy, basic checks
- pre-push: pytest + 90% coverage gate (mirrors CI)
- scripts/install-hooks.sh wires both stages with one command"
```

---

# PHASE 2 — Characterization Snapshot (Regression Net)

Goal: capture the *exact* current entity_id, unique_id, state, and attribute output for the fixture data. This snapshot becomes the contract that phase 3 must not break.

---

### Task 2.1: Snapshot every entity from the fixture data

**Files:**
- Create: `tests/test_characterization.py`
- Generated: `tests/snapshots/test_characterization.ambr`

- [ ] **Step 1: Write the characterization test**

```python
"""Characterization test: pins down the current sensor output as a regression contract.

This test must keep passing through the EntityDescription refactor in phase 3.
Any byte-level change to entity_id, unique_id, state, or attribute set
indicates a user-visible regression.
"""
from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from syrupy.assertion import SnapshotAssertion


async def test_all_entities_snapshot(
    hass: HomeAssistant,
    setup_integration,
    snapshot: SnapshotAssertion,
) -> None:
    """Every entity's full registry+state shape, sorted, is the regression contract."""
    entity_reg = er.async_get(hass)
    entries = sorted(
        er.async_entries_for_config_entry(entity_reg, setup_integration.entry_id),
        key=lambda e: e.entity_id,
    )

    captured = []
    for entry in entries:
        state = hass.states.get(entry.entity_id)
        captured.append(
            {
                "entity_id": entry.entity_id,
                "unique_id": entry.unique_id,
                "platform": entry.platform,
                "device_class": entry.device_class or entry.original_device_class,
                "unit": entry.unit_of_measurement,
                "state": state.state if state else None,
                "attributes": (
                    {k: v for k, v in state.attributes.items() if k != "entity_picture"}
                    if state
                    else None
                ),
            }
        )

    assert captured == snapshot


async def test_device_registry_snapshot(
    hass: HomeAssistant,
    setup_integration,
    snapshot: SnapshotAssertion,
) -> None:
    """Device structure (which spool gets which device, identifiers) is contract."""
    from homeassistant.helpers import device_registry as dr

    dev_reg = dr.async_get(hass)
    devices = sorted(
        dr.async_entries_for_config_entry(dev_reg, setup_integration.entry_id),
        key=lambda d: sorted(str(i) for i in d.identifiers)[0],
    )
    captured = [
        {
            "name": d.name,
            "model": d.model,
            "manufacturer": d.manufacturer,
            "identifiers": sorted(str(i) for i in d.identifiers),
            "via": d.via_device_id,
        }
        for d in devices
    ]
    assert captured == snapshot
```

- [ ] **Step 2: Run it once to generate the snapshot**

```bash
pytest tests/test_characterization.py --snapshot-update -v
```
Expected: PASS. Inspect the generated `.ambr` file — it should show every spool_1 and spool_2 entity with its current ID and state.

- [ ] **Step 3: Run again to confirm stability**

```bash
pytest tests/test_characterization.py -v
```
Expected: PASS without `--snapshot-update`.

- [ ] **Step 4: Eyeball the snapshot for sanity**

Open `tests/snapshots/test_characterization.ambr`. Confirm:
- `sensor.spoolman_spool_1` (the main sensor) is present with all attributes
- `sensor.spoolman_spool_1_used_weight` etc. are present
- `binary_sensor.spoolman_spool_1_low_filament` is present
- Spool 3 (archived) entities are NOT present (config has show_archived=false)
- Extra-field sensors for spool 1 are present

If any of these look wrong, fix the fixture data BEFORE proceeding — the snapshot is your contract.

- [ ] **Step 5: Commit**

```bash
git add tests/test_characterization.py tests/snapshots/
git commit -m "test: characterization snapshot of all entities (regression contract)

This snapshot pins every entity_id, unique_id, state, attribute, and
device identifier produced by the integration on the fixture data. It
must remain green through the EntityDescription refactor in phase 3 —
any failure means a user-visible regression."
```

---

### Task 2.2: Service contract tests

**Files:**
- Create: `tests/test_services.py`

- [ ] **Step 1: Write tests for both services**

```python
"""Test that registered services keep their contract."""
from __future__ import annotations

from homeassistant.core import HomeAssistant

from custom_components.spoolman.const import (
    DOMAIN,
    SPOOLMAN_PATCH_SPOOL_SERVICENAME,
    SPOOLMAN_USE_SPOOL_FILAMENT_SERVICENAME,
)
from tests.const import MOCK_URL


async def test_services_registered(hass: HomeAssistant, setup_integration) -> None:
    assert hass.services.has_service(DOMAIN, SPOOLMAN_PATCH_SPOOL_SERVICENAME)
    assert hass.services.has_service(DOMAIN, SPOOLMAN_USE_SPOOL_FILAMENT_SERVICENAME)


async def test_patch_spool_service(hass: HomeAssistant, setup_integration, mock_spoolman_api) -> None:
    """patch_spool calls the API and triggers a refresh."""
    mock_spoolman_api.patch(f"{MOCK_URL}api/v1/spool/1", payload={"id": 1, "comment": "updated"})

    await hass.services.async_call(
        DOMAIN,
        SPOOLMAN_PATCH_SPOOL_SERVICENAME,
        {"id": 1, "comment": "updated"},
        blocking=True,
    )
    # The mock recorded the PATCH call:
    assert any("api/v1/spool/1" in str(k) for k in mock_spoolman_api.requests)


async def test_use_spool_filament_service(hass: HomeAssistant, setup_integration, mock_spoolman_api) -> None:
    mock_spoolman_api.put(f"{MOCK_URL}api/v1/spool/1/use", payload={"id": 1})

    await hass.services.async_call(
        DOMAIN,
        SPOOLMAN_USE_SPOOL_FILAMENT_SERVICENAME,
        {"id": 1, "use_length": 100},
        blocking=True,
    )
    assert any("/use" in str(k) for k in mock_spoolman_api.requests)
```

- [ ] **Step 2: Run**

```bash
pytest tests/test_services.py -v
```
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add tests/test_services.py
git commit -m "test: pin patch_spool and use_spool_filament service contracts"
```

---

### Task 2.3: Config flow + options flow tests (also phase-2 contract)

**Files:**
- Create: `tests/test_config_flow.py`
- Create: `tests/test_options_flow.py`

Read the current `config_flow.py` and `options_flow.py` to enumerate every code path. For each path (happy, validation error, duplicate entry, abort, reauth if any) write one test.

- [ ] **Step 1: Inspect the flows**

```bash
cat custom_components/spoolman/config_flow.py custom_components/spoolman/options_flow.py
```
Note every `errors=`, every `async_abort`, every branch. List them.

- [ ] **Step 2: Write `tests/test_config_flow.py`** — one test per branch enumerated. Template:

```python
"""Test the Spoolman config flow — must reach 100% line + branch coverage."""
from __future__ import annotations

from unittest.mock import patch

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.spoolman.const import DOMAIN
from tests.const import MOCK_CONFIG_DATA, MOCK_URL


async def test_user_flow_happy_path(hass: HomeAssistant, mock_spoolman_api) -> None:
    """User submits valid URL → entry is created."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], MOCK_CONFIG_DATA
    )
    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["data"][next(iter(MOCK_CONFIG_DATA))]  # smoke-check


async def test_user_flow_unreachable(hass: HomeAssistant) -> None:
    """Connection failure → form re-shown with cannot_connect error."""
    # use aioresponses-less context: server returns 500 / unreachable
    from aioresponses import aioresponses

    with aioresponses() as m:
        m.get(f"{MOCK_URL}api/v1/info", status=500, repeat=True)
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"], MOCK_CONFIG_DATA
        )
        assert result2["type"] is FlowResultType.FORM
        assert "cannot_connect" in (result2.get("errors") or {}).values() or \
               "cannot_connect" in str(result2.get("errors"))


async def test_duplicate_entry_aborts(hass: HomeAssistant, setup_integration, mock_spoolman_api) -> None:
    """Same URL twice → abort with already_configured."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"], MOCK_CONFIG_DATA
    )
    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "already_configured"
```

Add tests for every other branch you enumerated in step 1. **Do not skip branches** — Platinum requires 100% config flow coverage.

- [ ] **Step 3: Write `tests/test_options_flow.py`** following the same enumerate-then-test pattern.

- [ ] **Step 4: Run with branch coverage on the flow files**

```bash
pytest tests/test_config_flow.py tests/test_options_flow.py \
  --cov=custom_components.spoolman.config_flow \
  --cov=custom_components.spoolman.options_flow \
  --cov-report=term-missing
```
Expected: 100% on both files. If lines are uncovered, write the missing test. Don't move on until 100%.

- [ ] **Step 5: Commit**

```bash
git add tests/test_config_flow.py tests/test_options_flow.py
git commit -m "test: 100% line+branch coverage of config_flow and options_flow

Platinum quality scale requires 100% config-flow coverage; this commit
enumerates and tests every form, error path, and abort branch."
```

---

### Task 2.4: Coordinator + API tests

**Files:**
- Create: `tests/test_coordinator.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Coordinator tests** — happy update, API failure → `UpdateFailed`, partial endpoint failure (extra_fields 404 should degrade gracefully), location fallback when `/location` not available, archived filter.

```python
"""Test SpoolManCoordinator data update logic."""
from __future__ import annotations

import pytest
from aioresponses import aioresponses
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.spoolman.coordinator import SpoolManCoordinator
from tests.const import MOCK_URL


async def test_update_happy_path(hass, config_entry, mock_spoolman_api):
    coord = SpoolManCoordinator(hass, config_entry)
    await coord.async_refresh()
    assert coord.last_update_success
    assert len(coord.data["spools"]) == 2  # archived filtered
    assert "filaments" in coord.data
    assert "locations" in coord.data


async def test_update_failure_marks_unsuccessful(hass, config_entry):
    with aioresponses() as m:
        m.get(f"{MOCK_URL}api/v1/spool?allow_archived=false", status=500, repeat=True)
        coord = SpoolManCoordinator(hass, config_entry)
        await coord.async_refresh()
    assert not coord.last_update_success


async def test_extra_fields_endpoint_404_degrades(hass, config_entry, spools_data, filaments_data, locations_data):
    """Older Spoolman without /field/spool: integration still works."""
    with aioresponses() as m:
        m.get(f"{MOCK_URL}api/v1/spool?allow_archived=false",
              payload=[s for s in spools_data if not s.get("archived")], repeat=True)
        m.get(f"{MOCK_URL}api/v1/filament", payload=filaments_data, repeat=True)
        m.get(f"{MOCK_URL}api/v1/location", payload=locations_data, repeat=True)
        m.get(f"{MOCK_URL}api/v1/field/spool", status=404, repeat=True)
        coord = SpoolManCoordinator(hass, config_entry)
        await coord.async_refresh()
    assert coord.last_update_success
    assert coord.data["extra_fields"]["spool"] == {}


async def test_locations_fallback_to_derived(hass, config_entry, spools_data, filaments_data):
    """No /location endpoint → derive from spool.location values."""
    with aioresponses() as m:
        m.get(f"{MOCK_URL}api/v1/spool?allow_archived=false",
              payload=[s for s in spools_data if not s.get("archived")], repeat=True)
        m.get(f"{MOCK_URL}api/v1/filament", payload=filaments_data, repeat=True)
        m.get(f"{MOCK_URL}api/v1/location", status=404, repeat=True)
        m.get(f"{MOCK_URL}api/v1/field/spool", payload=[], repeat=True)
        coord = SpoolManCoordinator(hass, config_entry)
        await coord.async_refresh()
    # derived from spool fixture: "Shelf A" + "Shelf B"
    assert set(coord.data["locations"]) == {"Shelf A", "Shelf B"}
```

- [ ] **Step 2: API client tests** — `tests/test_api.py` — for each method on `SpoolmanAPI`: success, HTTP 4xx/5xx, network error, malformed JSON. Use `aioresponses`.

- [ ] **Step 3: Run and verify both files have 100% coverage on their target modules**

```bash
pytest tests/test_coordinator.py tests/test_api.py \
  --cov=custom_components.spoolman.coordinator \
  --cov=custom_components.spoolman.classes.spoolman_api \
  --cov-report=term-missing
```
Expected: 100% (or as close as possible — every uncovered line must have a justification).

- [ ] **Step 4: Commit**

```bash
git add tests/test_coordinator.py tests/test_api.py
git commit -m "test: cover SpoolManCoordinator and SpoolmanAPI happy + failure paths"
```

---

### Task 2.5: Verify coverage gate is now passing

- [ ] **Step 1: Run the full suite**

```bash
pytest
```
Expected: ≥90% coverage. If under, identify which modules are pulling it down (sensor.py, binary_sensor.py, sensors/*.py likely) and add focused tests until the gate passes.

- [ ] **Step 2: Push and confirm green CI**

```bash
git push
```
Expected: PR CI green for tests + coverage. Mypy will likely still be red — that's phase 4's problem.

---

# PHASE 3 — EntityDescription Refactor

Goal: collapse 27 sensor files to one generic class + a description registry, while phase-2 snapshots stay green.

---

### Task 3.1: Introduce `models.py` with TypedDicts

**Files:**
- Create: `custom_components/spoolman/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write a tiny test** that round-trips a fixture spool through the TypedDict at runtime (using `cast` — TypedDicts don't validate, so the test really just locks in the structural contract).

```python
"""Lock the TypedDict shape we depend on."""
from custom_components.spoolman.models import CoordinatorData, SpoolData


def test_spool_typeddict_accepts_fixture(spools_data):
    spool: SpoolData = spools_data[0]  # type: ignore[assignment]
    assert spool["id"] == 1
    assert spool["filament"]["material"] == "PLA"


def test_coordinator_typeddict_accepts_full_payload(spools_data, filaments_data):
    payload: CoordinatorData = {  # type: ignore[typeddict-item]
        "spools": spools_data,
        "filaments": filaments_data,
        "extra_fields": {"spool": []},
        "locations": ["Shelf A"],
    }
    assert "spools" in payload
```

- [ ] **Step 2: Run — fails (no models module)**

```bash
pytest tests/test_models.py -v
```

- [ ] **Step 3: Implement `models.py`**

```python
"""Typed shapes for Spoolman API and coordinator data.

Defined as TypedDict (not dataclass) because we receive plain dicts from
JSON; converting would mean a deep-copy on every coordinator refresh and
would break the existing characterization snapshot.
"""
from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class VendorData(TypedDict, total=False):
    id: int
    name: str


class FilamentData(TypedDict, total=False):
    id: int
    name: str | None
    material: str
    density: float
    diameter: float
    weight: float
    color_hex: str
    multi_color_hexes: str
    multi_color_direction: str
    settings_extruder_temp: int
    settings_bed_temp: int
    article_number: str
    vendor: VendorData


class SpoolData(TypedDict):
    id: int
    filament: FilamentData
    archived: NotRequired[bool]
    registered: NotRequired[str]
    first_used: NotRequired[str | None]
    last_used: NotRequired[str | None]
    remaining_weight: NotRequired[float | None]
    used_weight: NotRequired[float | None]
    remaining_length: NotRequired[float | None]
    used_length: NotRequired[float | None]
    price: NotRequired[float | None]
    spool_weight: NotRequired[float | None]
    lot_nr: NotRequired[str | None]
    comment: NotRequired[str | None]
    location: NotRequired[str | None]
    extra: NotRequired[dict[str, str]]
    klipper_active_spool: NotRequired[bool]


class ExtraFieldData(TypedDict):
    key: str
    name: str
    field_type: str


class CoordinatorData(TypedDict):
    spools: list[SpoolData]
    filaments: list[FilamentData]
    extra_fields: dict[str, list[ExtraFieldData]]
    locations: list[str]
```

- [ ] **Step 4: Run, expect green**

```bash
pytest tests/test_models.py -v
```

- [ ] **Step 5: Commit**

```bash
git add custom_components/spoolman/models.py tests/test_models.py
git commit -m "refactor: add TypedDict models for Spoolman data

These types replace untyped dicts in coordinator/sensor signatures over
the next tasks. Pure addition — no behavior change."
```

---

### Task 3.2: Build `entity.py` — the unified base

**Files:**
- Create: `custom_components/spoolman/entity.py`

- [ ] **Step 1: Write a unit test in `tests/test_entity.py`**

```python
"""Test the SpoolmanEntity base class behavior in isolation."""
from custom_components.spoolman.entity import build_spool_display_name


def test_display_name_full():
    s = {"id": 1, "filament": {"name": "PLA Basic", "material": "PLA",
                               "vendor": {"name": "Bambu Lab"}}}
    assert build_spool_display_name(s) == "Bambu Lab PLA Basic PLA"


def test_display_name_no_vendor():
    s = {"id": 1, "filament": {"name": "PLA Basic", "material": "PLA", "vendor": {}}}
    assert build_spool_display_name(s) == "PLA Basic PLA"


def test_display_name_fallback():
    s = {"id": 7, "filament": {"vendor": {}}}
    assert build_spool_display_name(s) == "Spoolman Spool 7"
```

- [ ] **Step 2: Run — fails**

- [ ] **Step 3: Implement `entity.py`**

```python
"""Unified base class for all Spoolman platform entities.

Replaces the duplicated __init__ + _handle_coordinator_update across the
old sensors/*.py tree. Every Spoolman entity sits on top of this.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_URL, DOMAIN
from .models import SpoolData

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

    from .coordinator import SpoolManCoordinator


def build_spool_display_name(spool: SpoolData) -> str:
    """Human-readable spool name. Must produce the EXACT same string the old
    duplicated code produced — phase-2 snapshot depends on this.
    """
    filament = spool.get("filament", {}) or {}
    vendor_name = (filament.get("vendor") or {}).get("name")
    name = filament.get("name")
    material = filament.get("material")
    if name and material:
        if vendor_name:
            return f"{vendor_name} {name} {material}"
        return f"{name} {material}"
    return f"Spoolman Spool {spool['id']}"


class SpoolmanEntity(CoordinatorEntity["SpoolManCoordinator"]):
    """Base for every Spoolman platform entity."""

    _attr_has_entity_name = False  # legacy: existing entities use the long name format

    def __init__(
        self,
        hass: "HomeAssistant",
        coordinator: "SpoolManCoordinator",
        spool: SpoolData,
        config_entry: "ConfigEntry",
    ) -> None:
        super().__init__(coordinator)
        self.hass = hass
        self._entry = config_entry
        self.spool_id: int = spool["id"]
        self._spool: SpoolData = spool
        self._spool_name = build_spool_display_name(spool)
        self._attr_available = True

    def _make_entity_id(self, platform: str, suffix: str) -> str:
        return generate_entity_id(
            f"{platform}.{{}}", f"spoolman_spool_{self.spool_id}_{suffix}", hass=self.hass
        )

    def _make_unique_id(self, suffix: str) -> str:
        return f"spoolman_{self._entry.entry_id}_spool_{self.spool_id}_{suffix}"

    def _make_device_info(self) -> DeviceInfo:
        url = self.hass.data[DOMAIN][CONF_URL]  # phase 4 will move this to runtime_data
        return DeviceInfo(identifiers={(DOMAIN, url, f"spool_{self.spool_id}")})

    @callback
    def _handle_coordinator_update(self) -> None:
        spool = next(
            (s for s in self.coordinator.data.get("spools", []) if s["id"] == self.spool_id),
            None,
        )
        if spool is None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._spool = spool
        self.async_write_ha_state()
```

- [ ] **Step 4: Run unit test green, commit**

```bash
pytest tests/test_entity.py -v
git add custom_components/spoolman/entity.py tests/test_entity.py
git commit -m "refactor: add SpoolmanEntity base class with shared name/id/device logic

Pure addition — nothing uses it yet. The display-name function exactly
reproduces the duplicated logic from sensors/*.py so the characterization
snapshot stays green when migration starts in the next task."
```

---

### Task 3.3: Build `sensor_descriptions.py` — describe every trivial sensor

**Files:**
- Create: `custom_components/spoolman/sensor_descriptions.py`

The 22 trivial property sensors (everything except Spool main sensor, SpoolFlowRate, SpoolEstimatedRunOut, SpoolUsedPercentage, SpoolExtraField, SpoolLocation, FilamentColorHex with image, and the per-filament Filament device) are pure `value_fn = lambda spool: spool[...]` shapes.

- [ ] **Step 1: Define the description dataclass + the registry**

```python
"""All Spoolman sensor descriptions — one row per trivial property sensor."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CURRENCY_EURO, UnitOfLength, UnitOfMass, UnitOfTemperature

from .models import SpoolData


@dataclass(frozen=True, kw_only=True)
class SpoolmanSensorEntityDescription(SensorEntityDescription):
    """Description for a Spoolman sensor.

    value_fn  — extracts the state from a spool dict.
    exists_fn — decides whether to instantiate this sensor for a given spool.
                Mirrors the if-checks in the old async_setup_entry so dynamic
                presence (sensor only exists when the field is non-null) is
                preserved EXACTLY.
    name_suffix — string appended to the spool display name to form _attr_name.
    entity_id_suffix — used for both entity_id and unique_id.
    """

    value_fn: Callable[[SpoolData], Any]
    exists_fn: Callable[[SpoolData], bool] = lambda _spool: True
    name_suffix: str
    entity_id_suffix: str


def _filament(spool: SpoolData, key: str) -> Any:
    return (spool.get("filament") or {}).get(key)


def _parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


SENSOR_DESCRIPTIONS: tuple[SpoolmanSensorEntityDescription, ...] = (
    # ---- always-present spool sensors ----
    SpoolmanSensorEntityDescription(
        key="used_weight",
        name_suffix="Used Weight",
        entity_id_suffix="used_weight",
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfMass.GRAMS,
        icon="mdi:weight",
        value_fn=lambda s: round(s.get("used_weight") or 0, 3),
    ),
    SpoolmanSensorEntityDescription(
        key="remaining_length",
        name_suffix="Remaining Length",
        entity_id_suffix="remaining_length",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.METERS,
        icon="mdi:tape-measure",
        value_fn=lambda s: round((s.get("remaining_length") or 0) / 1000, 3)
            if s.get("remaining_length") and s["remaining_length"] > 100 else s.get("remaining_length"),
        # ^ verify against old SpoolRemainingLength implementation; if it's
        #   raw mm -> just return s.get("remaining_length"). The snapshot will tell.
    ),
    # ... (entries for: used_length, location, registered, first_used, last_used,
    #      price, spool_weight, lot_number, comment, filament_density,
    #      filament_diameter, filament_extruder_temp, filament_bed_temp,
    #      filament_article_number, spool_id, filament_name, filament_material,
    #      vendor_name, filament_weight)
    # Each row is ~6 lines. The full list is generated mechanically by
    # mirroring the old per-file _attr_* values.
)
```

**Important:** for each old sensor file, copy its `_attr_*` values verbatim into the matching description. Use the snapshot from phase 2 to verify every device_class, unit, and icon. Do NOT guess.

- [ ] **Step 2: For each old sensor file, append a description row.** Read the file, identify the constant-shape values, write the row. Tracking checklist (tick each as you migrate it):

  - [ ] used_weight
  - [ ] remaining_length
  - [ ] used_length
  - [ ] location (text variant — note: `select.py` provides the writable selector; the sensor is read-only display)
  - [ ] registered (timestamp, with exists_fn)
  - [ ] first_used (timestamp, with exists_fn)
  - [ ] last_used (timestamp, with exists_fn)
  - [ ] price (with exists_fn `price is not None`)
  - [ ] spool_weight (with exists_fn)
  - [ ] lot_number (with exists_fn)
  - [ ] comment (with exists_fn)
  - [ ] filament_density (with exists_fn)
  - [ ] filament_diameter (with exists_fn)
  - [ ] filament_extruder_temp (with exists_fn)
  - [ ] filament_bed_temp (with exists_fn)
  - [ ] filament_article_number (with exists_fn)
  - [ ] spool_id (always)
  - [ ] filament_name (with exists_fn)
  - [ ] filament_material (with exists_fn)
  - [ ] vendor_name (with exists_fn)
  - [ ] filament_weight (with exists_fn)

- [ ] **Step 3: Commit just the descriptions module (nothing wired yet)**

```bash
git add custom_components/spoolman/sensor_descriptions.py
git commit -m "refactor: declare SpoolmanSensorEntityDescription registry

22 descriptions covering every trivial property sensor. Not yet wired
into sensor.py — that swap happens atomically in the next commit so the
phase-2 snapshot can verify it byte-for-byte."
```

---

### Task 3.4: Implement `SpoolmanSensor` and switch sensor.py over

**Files:**
- Modify: `custom_components/spoolman/sensor.py`
- Create: `custom_components/spoolman/sensor_complex.py`

This is the big one. Done atomically: one commit, snapshot must stay green.

- [ ] **Step 1: Move complex sensors as-is into `sensor_complex.py`**

Copy the 5 complex sensors (`Spool` main sensor with image, `SpoolFlowRate`, `SpoolEstimatedRunOut`, `SpoolUsedPercentage`, `SpoolLocation`, `SpoolExtraField`, `FilamentColorHex` with image, `Filament` device sensor) from `sensors/spool.py` etc. into `sensor_complex.py`. Update their imports to use `from .entity import SpoolmanEntity` where it cleanly fits (it may not for the ones that have non-spool device info — leave them alone if they don't fit).

Run snapshot:
```bash
pytest tests/test_characterization.py -v
```
Expected: still green (we only moved code, not its behavior).

- [ ] **Step 2: Write the generic `SpoolmanSensor`**

In `sensor.py`, add at the top (before async_setup_entry):

```python
from homeassistant.components.sensor import SensorEntity
from .entity import SpoolmanEntity
from .sensor_descriptions import SENSOR_DESCRIPTIONS, SpoolmanSensorEntityDescription


class SpoolmanSensor(SpoolmanEntity, SensorEntity):
    """Generic sensor driven entirely by a SpoolmanSensorEntityDescription."""

    entity_description: SpoolmanSensorEntityDescription

    def __init__(self, hass, coordinator, spool, config_entry, description):
        super().__init__(hass, coordinator, spool, config_entry)
        self.entity_description = description
        self._attr_name = f"{self._spool_name} {description.name_suffix}"
        self._attr_unique_id = self._make_unique_id(description.entity_id_suffix)
        self.entity_id = self._make_entity_id("sensor", description.entity_id_suffix)
        self._attr_device_info = self._make_device_info()

    @property
    def native_value(self):
        return self.entity_description.value_fn(self._spool)
```

- [ ] **Step 3: Replace `_build_entities_for_spool`**

Rewrite the function. The new version:

```python
async def _build_entities_for_spool(spool, idx):
    entities: list = []
    image_url = await hass.async_add_executor_job(
        _generate_entity_picture, spool, image_dir
    )
    # complex sensors first (preserve order from old code so snapshot stays stable)
    entities.append(Spool(hass, coordinator, spool, idx, config_entry, image_url))
    entities.append(SpoolFlowRate(hass, coordinator, spool, config_entry))
    entities.append(SpoolEstimatedRunOut(hass, coordinator, spool, config_entry))

    # description-driven trivial sensors
    for desc in SENSOR_DESCRIPTIONS:
        if desc.exists_fn(spool):
            entities.append(SpoolmanSensor(hass, coordinator, spool, config_entry, desc))

    entities.append(SpoolUsedPercentage(hass, coordinator, spool, config_entry))
    entities.append(SpoolLocation(hass, coordinator, spool, config_entry))

    # filament_color_hex stays special (image generation)
    filament = spool.get("filament", {})
    if filament.get("color_hex"):
        filament_image_url = await hass.async_add_executor_job(
            _generate_filament_entity_picture, filament, image_dir
        )
        entities.append(FilamentColorHex(hass, coordinator, spool, config_entry, filament_image_url))

    # extra fields stay special (per-field iteration)
    for field_key in spool.get("extra", {}):
        entity = SpoolExtraField(hass, coordinator, spool, config_entry, field_key)
        entities.append(entity)
        existing_extra_fields[(spool["id"], field_key)] = entity

    existing_spool_ids.add(spool["id"])
    return entities
```

Drop the entire 200-line `if coordinator.data:` duplicated block from the bottom of `async_setup_entry` and have it call `_build_entities_for_spool` for each initial spool too. Same logic, no duplication.

- [ ] **Step 4: Run the snapshot test — must stay green**

```bash
pytest tests/test_characterization.py -v
```

If it fails: read the diff carefully. Each diff is a regression. Common causes and fixes:
- **Order of entities differs** → re-order the description list to match old insertion order
- **`_attr_name` differs** → check for trailing space or different casing in `name_suffix`
- **`unique_id` differs** → check `entity_id_suffix` exactly matches the old per-file `f"..._{suffix}"` strings
- **State value differs** → your `value_fn` doesn't match the old `state` property; recheck rounding, defaults, type

Iterate until green. **Do not update the snapshot to make it pass** — that defeats the contract.

- [ ] **Step 5: Run the full suite**

```bash
pytest
```
Expected: all green, coverage still ≥90%.

- [ ] **Step 6: Commit**

```bash
git add custom_components/spoolman/sensor.py custom_components/spoolman/sensor_complex.py
git commit -m "refactor: collapse 22 trivial sensor classes into description-driven SpoolmanSensor

The SpoolmanSensorEntityDescription registry replaces 22 ~60-line files
with one ~200-line table. Behavior is byte-identical to the old code;
the characterization snapshot in tests/snapshots stays green."
```

---

### Task 3.5: Delete the old `sensors/` tree

- [ ] **Step 1: Check nothing imports from `sensors/`**

```bash
grep -rn "from .sensors" custom_components/spoolman/ || echo none
grep -rn "from custom_components.spoolman.sensors" tests/ || echo none
```
Expected: `sensor_complex.py` may import `Spool, SpoolFlowRate, ...` from `.sensors` after moving — fix those imports to point at `sensor_complex` itself, then re-run.

- [ ] **Step 2: Delete the directory**

```bash
rm -r custom_components/spoolman/sensors/
```

- [ ] **Step 3: Run full suite + characterization**

```bash
pytest
```
Expected: green.

- [ ] **Step 4: Commit**

```bash
git add -A custom_components/spoolman/
git commit -m "refactor: delete legacy sensors/ tree (replaced by description registry)

Removes 27 files / ~1500 lines. All functionality is now in
sensor.py + sensor_descriptions.py + sensor_complex.py. The
phase-2 characterization snapshot remains byte-identical."
```

---

### Task 3.6: Same treatment for binary_sensor.py and select.py

The user-visible payoff is smaller (1 binary sensor, 1 select), but Platinum demands consistent patterns.

- [ ] **Step 1: Refactor `binary_sensor.py`** to use `SpoolmanEntity` as base. Snapshot test stays green.
- [ ] **Step 2: Refactor `select.py`** to use `SpoolmanEntity` as base. Snapshot test stays green.
- [ ] **Step 3: Add `tests/test_binary_sensor.py` and `tests/test_select.py`** with focused unit tests for low-filament threshold behavior and location selection respectively.
- [ ] **Step 4: Commit both refactors and tests in two commits.**

---

# PHASE 4 — Platinum Quality Scale Compliance

Reference: <https://www.home-assistant.io/docs/quality_scale/> — go through every rule. Below: the rules that need work in this codebase, mapped to tasks.

---

### Task 4.1: Move from `hass.data[DOMAIN]` to `entry.runtime_data`

**Why:** Platinum rule `runtime-data`. Avoids the global `hass.data` bag.

**Files:**
- Modify: `custom_components/spoolman/__init__.py`
- Modify: `custom_components/spoolman/coordinator.py`
- Modify: `custom_components/spoolman/entity.py`
- Modify: `custom_components/spoolman/sensor_complex.py`
- Modify: every other module reading `hass.data[DOMAIN]`

- [ ] **Step 1: Define the runtime container**

In `coordinator.py`, add at top:

```python
from dataclasses import dataclass

@dataclass
class SpoolmanRuntimeData:
    coordinator: "SpoolManCoordinator"
    api: "SpoolmanAPI"
    klipper_active_spool: int | None = None
```

And the typed alias:

```python
from homeassistant.config_entries import ConfigEntry
type SpoolmanConfigEntry = ConfigEntry[SpoolmanRuntimeData]
```

- [ ] **Step 2: Wire it in `__init__.py`**

```python
async def async_setup_entry(hass: HomeAssistant, entry: SpoolmanConfigEntry) -> bool:
    api = SpoolmanAPI(entry.data[CONF_URL])
    coordinator = SpoolManCoordinator(hass, entry, api)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = SpoolmanRuntimeData(coordinator=coordinator, api=api)
    ...
```

Replace `hass.data[DOMAIN] = {...}` setup with the runtime_data assignment. Replace every `hass.data[DOMAIN]["coordinator"]` read with `entry.runtime_data.coordinator`. Same for `SPOOLMAN_API_WRAPPER`.

- [ ] **Step 3: Update entity base** to read URL from runtime_data instead of `hass.data[DOMAIN][CONF_URL]`. The entity already has `self._entry`; thread `entry.runtime_data.api.url` through.

- [ ] **Step 4: Run the suite — snapshot must stay green**

```bash
pytest
```
Any change in entity_id/unique_id is a bug; the URL-derived device identifier must remain identical.

- [ ] **Step 5: Commit**

```bash
git commit -am "refactor: use ConfigEntry.runtime_data instead of hass.data[DOMAIN]

Platinum rule 'runtime-data'. Removes the implicit global state bag and
gives us a typed handle on per-entry runtime objects."
```

---

### Task 4.2: Replace first refresh with `async_config_entry_first_refresh`

**Why:** Platinum rule `entity-unavailable`. Coordinator's first refresh should raise `ConfigEntryNotReady` automatically on failure, so HA retries.

- [ ] **Step 1: In `__init__.py`, replace**

```python
await coordinator.async_refresh()
```

with

```python
await coordinator.async_config_entry_first_refresh()
```

- [ ] **Step 2: Add a test** in `tests/test_init.py`:

```python
async def test_setup_retries_on_api_failure(hass, config_entry):
    """If Spoolman is unreachable on first refresh, HA gets ConfigEntryNotReady."""
    from homeassistant.config_entries import ConfigEntryState

    with aioresponses() as m:
        m.get(f"{MOCK_URL}api/v1/spool?allow_archived=false", status=500, repeat=True)
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
```

- [ ] **Step 3: Run, commit**

---

### Task 4.3: Add `parallel_updates`

**Why:** Platinum rule `parallel-updates`. Each platform must declare it.

- [ ] **Step 1: At top of `sensor.py`, `binary_sensor.py`, `select.py`:**

```python
PARALLEL_UPDATES = 0  # data comes from a single coordinator
```

- [ ] **Step 2: Commit**

---

### Task 4.4: Strict typing pass — get mypy green

This is the largest single task. Allocate a full session.

- [ ] **Step 1: Run mypy and capture the error count baseline**

```bash
mypy custom_components/spoolman 2>&1 | tail -3
```

- [ ] **Step 2: Fix files in dependency order**: `models.py` (already typed) → `const.py` → `api.py` → `coordinator.py` → `entity.py` → `sensor_descriptions.py` → `sensor.py` → `sensor_complex.py` → `binary_sensor.py` → `select.py` → `config_flow.py` → `options_flow.py` → `__init__.py` → `helpers/*.py`.

For each file:
- Add return type annotations to every function.
- Replace `dict` with `SpoolData` / `CoordinatorData` where applicable.
- Eliminate `Any` (the mypy `disallow_any_generics` will catch most).
- Fix `Optional` imports.
- Use `NotRequired` for optional TypedDict fields.

- [ ] **Step 3: After each file, run mypy and pytest**

```bash
mypy custom_components/spoolman/<file>.py
pytest -x
```

- [ ] **Step 4: When mypy is green, commit**

```bash
git commit -am "refactor: full mypy --strict compliance

Platinum rule 'strict-typing'. Every function has explicit type
annotations; coordinator and sensor data uses SpoolData/CoordinatorData
TypedDicts instead of bare dicts."
```

---

### Task 4.5: Translations + strings.json

**Why:** Platinum rule `docs-installation-parameters`, `common-modules`. All user-facing strings must be in `strings.json`, with at least English translation. Service descriptions must be in `services.yaml` referenced from translations.

- [ ] **Step 1: Audit every user-facing string** — config flow titles, error keys, options flow, exception messages raised to user. Make a checklist.

- [ ] **Step 2: Build `custom_components/spoolman/strings.json`** with full coverage. Update `translations/en.json` to mirror.

- [ ] **Step 3: Add a hassfest run to CI** (it already exists but isn't called from `pr_tests.yml` — wire it).

- [ ] **Step 4: Run hassfest locally**

```bash
python -m homeassistant_hassfest --integration-path custom_components/spoolman
```

- [ ] **Step 5: Commit**

---

### Task 4.6: Diagnostics platform

**Why:** Platinum rule `diagnostics`.

- [ ] **Step 1: Write `tests/test_diagnostics.py`** with a snapshot of the diagnostics dump (using syrupy). Test must redact URLs/keys.

- [ ] **Step 2: Implement `custom_components/spoolman/diagnostics.py`**:

```python
"""Diagnostics support for Spoolman."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .coordinator import SpoolmanConfigEntry

TO_REDACT = {"spoolman_url", "klipper_url"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: SpoolmanConfigEntry
) -> dict[str, Any]:
    coord = entry.runtime_data.coordinator
    return {
        "config": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
        "coordinator": {
            "last_update_success": coord.last_update_success,
            "data": coord.data,
        },
    }
```

- [ ] **Step 3: Run tests, commit.**

---

### Task 4.7: Reload-on-options-change

**Why:** Platinum rule `reauthentication-flow` and options flow update.

- [ ] **Step 1: Add an update listener in `__init__.py`**

```python
entry.async_on_unload(entry.add_update_listener(_async_update_listener))

async def _async_update_listener(hass: HomeAssistant, entry: SpoolmanConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
```

- [ ] **Step 2: Test in `test_options_flow.py`** — change update_interval, assert coordinator restarts with new value.

- [ ] **Step 3: Commit.**

---

### Task 4.8: Manifest updates

**Files:**
- Modify: `manifest.json`

- [ ] **Step 1: Update**:

```json
{
  "domain": "spoolman",
  "name": "Spoolman",
  "codeowners": ["@disane87"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/Disane87/spoolman-homeassistant",
  "integration_type": "service",
  "iot_class": "local_polling",
  "issue_tracker": "https://github.com/Disane87/spoolman-homeassistant/issues",
  "loggers": ["custom_components.spoolman"],
  "quality_scale": "platinum",
  "requirements": [],
  "version": "0.0.0"
}
```

- [ ] **Step 2: Run hassfest, fix any complaints, commit.**

---

### Task 4.9: `quality_scale.yaml` self-assessment

**Files:**
- Create: `custom_components/spoolman/quality_scale.yaml`

- [ ] **Step 1:** For each rule on <https://www.home-assistant.io/docs/quality_scale/> tier list (Bronze + Silver + Gold + Platinum), add a status entry:

```yaml
rules:
  config-flow: done
  test-before-configure: done
  unique-config-entry: done
  config-flow-test-coverage: done
  runtime-data: done
  test-before-setup: done
  appropriate-polling: done
  entity-unique-id: done
  has-entity-name: done
  entity-event-setup: done
  parallel-updates: done
  reauthentication-flow:
    status: exempt
    comment: integration does not require authentication
  action-setup: done
  log-when-unavailable: done
  exception-translations: done
  config-entry-unloading: done
  reconfiguration-flow: done
  dynamic-devices: done
  devices: done
  entity-category: done
  diagnostics: done
  stale-devices: done
  icon-translations: done
  entity-translations: done
  repair-issues:
    status: exempt
    comment: no known repair scenarios in this integration
  docs-installation-parameters: done
  docs-configuration-parameters: done
  strict-typing: done
  test-coverage: done
  inject-websession:
    status: exempt
    comment: aiohttp session injected via async_get_clientsession in api.py
```

- [ ] **Step 2:** Cross-check each `done` against actual code; if not actually done, mark `todo` and add a follow-up task. **Do not lie in this file** — the HA review process checks every claim.

- [ ] **Step 3: Commit.**

---

# PHASE 5 — Final Verification & Documentation

---

### Task 5.1: Full quality gauntlet

- [ ] **Step 1:** `ruff check . && ruff format --check .`
- [ ] **Step 2:** `mypy custom_components/spoolman` — 0 errors.
- [ ] **Step 3:** `pytest` — all green, coverage ≥ 90%.
- [ ] **Step 4:** Run hassfest as the CI job does.
- [ ] **Step 5:** Run HACS validation locally if possible.
- [ ] **Step 6:** Spin up a real HA instance with the integration loaded; click through every config + options flow path; verify entities appear; trigger both services.

If any step fails: open an issue, fix, re-run.

---

### Task 5.2: Document the result

- [ ] **Step 1:** Update `README.md`:
  - "Quality Scale: Platinum" badge near the top.
  - Reference `quality_scale.yaml`.
  - Update the migration section with a note that all sensors are now description-driven (no behavior change for users).

- [ ] **Step 2:** Update `CONTRIBUTING.md`:
  - "Run `bash scripts/install-hooks.sh` once to wire pre-commit + pre-push hooks."
  - "Tests: `pytest` (90% gate). Strict typing: `mypy custom_components/spoolman`."

- [ ] **Step 3: Commit and push.**

---

### Task 5.3: Open the consolidating PR

- [ ] **Step 1:** Push the branch.
- [ ] **Step 2:** Open a PR against `dev` titled `refactor: platinum quality scale + sensor description registry`.
- [ ] **Step 3:** PR body: link to this plan, summarize phase-by-phase, link the snapshot file as the regression contract, and explicitly call out: "User-visible behavior is unchanged — verified by `tests/snapshots/test_characterization.ambr`."

---

## Self-Review Checklist (engineer runs before declaring done)

- [ ] Every old per-file sensor has a matching description in `sensor_descriptions.py` OR a class in `sensor_complex.py`. No orphans.
- [ ] `tests/snapshots/test_characterization.ambr` was never updated with `--snapshot-update` after the initial baseline in Task 2.1. (`git log -p tests/snapshots/` should show one creation commit and zero modifications.)
- [ ] `pytest` reports ≥ 90% coverage globally AND on every individual module.
- [ ] `mypy --strict custom_components/spoolman` reports 0 errors.
- [ ] `ruff check .` reports 0 issues.
- [ ] `pre-commit run --all-files` is green.
- [ ] `quality_scale.yaml` claims are each backed by real code/tests, not aspirational.
- [ ] Klipper code still works for users who haven't migrated to Moonraker (tested manually).
- [ ] No `hass.data[DOMAIN]` reads remain in the codebase.

If any item is unchecked, fix it before opening the PR.
