"""Characterization test: pins down the current sensor output as a regression contract.

This test must keep passing through the EntityDescription refactor in phase 3.
Any byte-level change to entity_id, unique_id, state, attributes, or device
identifier indicates a user-visible regression.
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from syrupy.assertion import SnapshotAssertion


async def test_all_entities_snapshot(
    hass: HomeAssistant,
    setup_integration: Any,
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
                    {
                        k: v
                        for k, v in state.attributes.items()
                        # Filter wall-clock and image-cache attributes that are
                        # non-deterministic between runs but represent no
                        # user-visible behavior we want to pin.
                        if k not in {"entity_picture", "last_update"}
                    }
                    if state
                    else None
                ),
            }
        )

    assert captured == snapshot


async def test_device_registry_snapshot(
    hass: HomeAssistant,
    setup_integration: Any,
    snapshot: SnapshotAssertion,
) -> None:
    """Device structure (which spool gets which device, identifiers) is contract."""
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
        }
        for d in devices
    ]
    assert captured == snapshot
