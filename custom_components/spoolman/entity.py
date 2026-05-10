"""Unified base class for every Spoolman platform entity.

Replaces the duplicated ``__init__``, ``_handle_coordinator_update``, and
``async_update`` blocks across the legacy ``sensors/*.py`` tree. Every
Spoolman entity that lives on a per-spool device sits on top of this.
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
    """Human-readable spool name.

    Must produce the EXACT same string the legacy duplicated code in
    ``sensors/*.py`` produced. The characterization snapshot in
    ``tests/snapshots/test_characterization.ambr`` depends on this.
    """
    filament = spool.get("filament") or {}
    vendor_name = (filament.get("vendor") or {}).get("name")
    name = filament.get("name")
    material = filament.get("material")
    if name and material:
        if vendor_name:
            return f"{vendor_name} {name} {material}"
        return f"{name} {material}"
    return f"Spoolman Spool {spool['id']}"


class SpoolmanEntity(CoordinatorEntity["SpoolManCoordinator"]):
    """Base for every Spoolman platform entity tied to a single spool."""

    _attr_has_entity_name = False  # legacy entities use the long name format

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: SpoolManCoordinator,
        spool: SpoolData,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.hass = hass
        self._entry = config_entry
        self.spool_id: int = spool["id"]
        self._spool: SpoolData = spool
        self._spool_name = build_spool_display_name(spool)
        self._attr_available = True

    def _make_entity_id(self, platform: str, suffix: str) -> str:
        """Build the legacy entity_id slug for this spool + suffix."""
        return generate_entity_id(
            f"{platform}.{{}}",
            f"spoolman_spool_{self.spool_id}_{suffix}",
            hass=self.hass,
        )

    def _make_unique_id(self, suffix: str) -> str:
        """Build the legacy unique_id slug for this spool + suffix."""
        return f"spoolman_{self._entry.entry_id}_spool_{self.spool_id}_{suffix}"

    def _make_device_info(self) -> DeviceInfo:
        """Build the spool device identifier shared by every per-spool entity.

        Reads the URL from ``entry.runtime_data`` (Platinum rule
        ``runtime-data``) with a defensive fallback to the legacy
        ``hass.data[DOMAIN]`` while the legacy sensors are migrated.

        Note: identifiers carry a 3-tuple ``(DOMAIN, url, "spool_{id}")``
        rather than the strict 2-tuple HA expects. This legacy shape lets
        devices stay distinct across multiple Spoolman instances on the
        same HA host. Changing it would orphan every existing user's
        devices on upgrade, so the type is suppressed intentionally.
        """
        runtime_data = getattr(self._entry, "runtime_data", None)
        url = (
            runtime_data.url
            if runtime_data is not None
            else self.hass.data[DOMAIN][CONF_URL]
        )
        return DeviceInfo(
            identifiers={(DOMAIN, url, f"spool_{self.spool_id}")}  # type: ignore[arg-type]
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Refresh ``self._spool`` from the coordinator's latest snapshot."""
        spool = next(
            (
                s
                for s in self.coordinator.data.get("spools", [])
                if s["id"] == self.spool_id
            ),
            None,
        )
        if spool is None:
            self._attr_available = False
        else:
            self._attr_available = True
            self._spool = spool
        self.async_write_ha_state()
