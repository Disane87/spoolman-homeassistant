"""Spoolman home assistant select entity."""

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

# Coordinator-driven; no concurrent per-entity updates. Platinum: parallel-updates.
PARALLEL_UPDATES = 0

_LOGGER = logging.getLogger(__name__)

ICON = "mdi:map-marker"


def _resolve_locations(coordinator_data, spools):
    """Pick the canonical location list, preferring Spoolman's /location feed.

    Falls back to the set of locations actually used by spools so older
    Spoolman servers (without /api/v1/location) still work.
    """
    locations = coordinator_data.get("locations") if coordinator_data else None
    if locations:
        return sorted(set(locations))
    derived = {spool["location"] for spool in spools if spool.get("location")}
    return sorted(derived)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up Spoolman select entities."""
    _LOGGER.info("Setting up Spoolman select platform")

    # Get the existing coordinator from hass.data
    coordinator = hass.data.get(DOMAIN, {}).get("coordinator")

    if (
        not coordinator
    ):  # pragma: no cover — defensive; setup ordering in __init__ prevents this
        _LOGGER.error("Coordinator not found in hass.data[%s]", DOMAIN)
        return

    _LOGGER.info("Coordinator found, checking for data")

    if not coordinator.data:
        _LOGGER.warning("No data in coordinator")
        return

    all_entities = []
    spool_data = coordinator.data.get("spools", [])
    _LOGGER.info("Found %d spools to create select entities for", len(spool_data))

    locations = _resolve_locations(coordinator.data, spool_data)
    _LOGGER.info("Found locations: %s", locations)

    existing_spool_ids: set = set()

    # Create a select entity for each spool
    for spool in spool_data:
        select_entity = SpoolLocationSelect(
            hass, coordinator, spool, locations, config_entry
        )
        all_entities.append(select_entity)
        existing_spool_ids.add(spool["id"])
        _LOGGER.debug("Created select entity for spool %s", spool["id"])

    _LOGGER.info("Adding %d select entities", len(all_entities))
    async_add_entities(all_entities)

    @callback
    def add_dynamic_selects():
        """Add a location select for spools that appeared after setup (#327)."""
        if not coordinator.data:
            return
        new_entities = []
        current_locations = _resolve_locations(
            coordinator.data, coordinator.data.get("spools", [])
        )
        for spool in coordinator.data.get("spools", []):
            spool_id = spool.get("id")
            if spool_id in existing_spool_ids:
                continue
            new_entities.append(
                SpoolLocationSelect(
                    hass, coordinator, spool, current_locations, config_entry
                )
            )
            existing_spool_ids.add(spool_id)
            _LOGGER.info("Dynamically adding location select for spool %s", spool_id)
        if new_entities:
            async_add_entities(new_entities)

    coordinator.async_add_listener(add_dynamic_selects)


class SpoolLocationSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Spoolman Spool Location Select."""

    def __init__(self, hass, coordinator, spool_data, locations, config_entry) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)

        self.config = hass.data[DOMAIN]
        self._spool = spool_data
        self.spool_id = spool_data["id"]
        self._locations = sorted(locations) if locations else ["Unknown"]
        self._entry = config_entry

        self.entity_id = generate_entity_id(
            "select.{}", f"spoolman_spool_{spool_data['id']}_location", hass=hass
        )
        self._attr_unique_id = (
            f"spoolman_{self._entry.entry_id}_spool_{spool_data['id']}_location"
        )
        self._attr_has_entity_name = False
        self._attr_icon = ICON
        self._attr_available = True

        # Set initial name
        filament = self._spool.get("filament", {})
        vendor_name = filament.get("vendor", {}).get("name")

        if filament.get("name") and filament.get("material"):
            if vendor_name:
                spool_name = (
                    f"{vendor_name} {filament['name']} {filament.get('material')}"
                )
            else:
                spool_name = f"{filament['name']} {filament.get('material')}"
        else:
            spool_name = f"Spoolman Spool {self._spool['id']}"

        self._attr_name = f"{spool_name} Location"

        # Set device info to match spool device
        from homeassistant.helpers.device_registry import DeviceInfo
        from .const import CONF_URL

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.config[CONF_URL], f"spool_{self._spool['id']}")},
        )

    @property
    def options(self) -> list[str]:
        """Return the list of available locations."""
        return self._locations

    @property
    def current_option(self) -> str | None:
        """Return the current location."""
        location = self._spool.get("location")
        return location if location in self._locations else None

    async def async_select_option(self, option: str) -> None:
        """Change the selected location."""
        _LOGGER.info(f"Changing spool {self.spool_id} location to: {option}")

        try:
            # Get the API wrapper from hass.data using the correct key
            from .const import SPOOLMAN_API_WRAPPER

            api = self.hass.data[DOMAIN][SPOOLMAN_API_WRAPPER]
            # Call the patch_spool service to update location
            await api.patch_spool(self.spool_id, {"location": option})
            # Immediately refresh coordinator data
            await self.coordinator.async_request_refresh()
        except Exception as e:  # pragma: no cover — defensive logging wrapper
            _LOGGER.error(f"Failed to update spool location: {e}")
            raise

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Use ID-based lookup
        spool_data = next(
            (
                s
                for s in self.coordinator.data.get("spools", [])
                if s["id"] == self.spool_id
            ),
            None,
        )

        if spool_data is None:
            _LOGGER.warning(
                "SpoolManCoordinator: Spool with ID '%s' not found in coordinator data. Marking as unavailable.",
                self.spool_id,
            )
            self._attr_available = False
            self.async_write_ha_state()
            return

        self._attr_available = True
        self._spool = spool_data

        # Refresh available locations from coordinator (Spoolman /location
        # feed) with fallback to spool-derived set.
        locations = _resolve_locations(
            self.coordinator.data,
            self.coordinator.data.get("spools", []),
        )
        self._locations = locations if locations else ["Unknown"]

        self.async_write_ha_state()
