"""Spoolman home assistant sensor platform."""

import base64
import logging
import re
from typing import Any, cast

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEFAULT_SPOOL_COLOR_HEX,
    DOMAIN,
)
from .entity import SpoolmanEntity
from .models import SpoolData
from .sensor_descriptions import (
    SENSOR_DESCRIPTIONS,
    SpoolmanSensorEntityDescription,
)
from .sensors import (
    Filament,
    FilamentColorHex,
    Spool,
    SpoolEstimatedRunOut,
    SpoolExtraField,
    SpoolFlowRate,
    SpoolLocation,
    SpoolUsedPercentage,
)

# All updates fan out from a single DataUpdateCoordinator, so per-entity
# parallelism would only multiply HA-internal locking. Platinum rule
# ``parallel-updates``.
PARALLEL_UPDATES = 0


class SpoolmanSensor(SpoolmanEntity, SensorEntity):
    """Generic Spoolman sensor driven by a SpoolmanSensorEntityDescription.

    Replaces the bulk of the legacy ``sensors/`` tree. The 20 trivial
    property sensors are now rows in :data:`SENSOR_DESCRIPTIONS` and a
    single instance of this class per row.
    """

    entity_description: SpoolmanSensorEntityDescription

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: Any,
        spool: dict[str, Any],
        config_entry: ConfigEntry,
        description: SpoolmanSensorEntityDescription,
    ) -> None:
        """Initialize a description-driven Spoolman sensor."""
        super().__init__(hass, coordinator, cast("SpoolData", spool), config_entry)
        self.entity_description = description
        self._attr_name = f"{self._spool_name} {description.name_suffix}"
        self._attr_unique_id = self._make_unique_id(description.entity_id_suffix)
        self.entity_id = self._make_entity_id("sensor", description.entity_id_suffix)
        self._attr_device_info = self._make_device_info()

    @property
    def native_value(self) -> Any:
        """Return the value extracted from the spool dict by ``value_fn``."""
        return self.entity_description.value_fn(self._spool)

    @property  # type: ignore[misc]
    def state(self) -> Any:
        """Return the state; numeric sensors go through HA unit conversion (#898).

        Timestamp sensors keep their raw ISO string (legacy convention);
        ``native_value`` would force a datetime parse and change the state.
        """
        if self.device_class == SensorDeviceClass.TIMESTAMP:
            return self.native_value
        return super().state


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(  # noqa: C901
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Spoolman sensors from a config entry."""
    # Use the coordinator from hass.data that was created in __init__.py
    coordinator = hass.data[DOMAIN]["coordinator"]

    # Track which spools / extra fields we've already materialised so we can
    # add brand-new spools and extras when the coordinator notices them
    # (#327: previously only extra fields were added dynamically; new spools
    # required a full integration reload).
    existing_spool_ids: set[int] = set()
    existing_extra_fields: dict[tuple[int, str], Any] = {}

    async def _build_entities_for_spool(spool: dict[str, Any], idx: int) -> list[Any]:
        """Build the full sensor stack for a single spool.

        Complex sensors (Spool main entity, FlowRate, EstimatedRunOut,
        UsedPercentage, Location, ExtraField, ColorHex with image) keep
        their own classes in ``sensors/``. Trivial property sensors are
        instantiated from :data:`SENSOR_DESCRIPTIONS`.
        """
        entities: list[Any] = []
        image_url = _generate_entity_picture(spool)

        # Complex sensors first — these have custom logic that doesn't
        # fit the description pattern (image generation, computed state,
        # custom name handling, dynamic per-key sensors).
        entities.append(Spool(hass, coordinator, spool, idx, config_entry, image_url))
        entities.append(SpoolFlowRate(hass, coordinator, spool, config_entry))
        entities.append(SpoolEstimatedRunOut(hass, coordinator, spool, config_entry))
        entities.append(SpoolLocation(hass, coordinator, spool, config_entry))
        entities.append(SpoolUsedPercentage(hass, coordinator, spool, config_entry))

        # Description-driven sensors. Each row's ``exists_fn`` mirrors the
        # legacy if-checks and the resulting entity_id/unique_id/name/icon/
        # device_class/unit values mirror the legacy classes byte-for-byte.
        spool_typed = cast("SpoolData", spool)
        for desc in SENSOR_DESCRIPTIONS:
            if desc.exists_fn(spool_typed):
                entities.append(
                    SpoolmanSensor(hass, coordinator, spool, config_entry, desc)
                )

        # FilamentColorHex needs image generation, so it stays out of the
        # description registry.
        filament = spool.get("filament", {})
        if filament.get("color_hex"):
            filament_image_url = _generate_filament_entity_picture(filament)
            entities.append(
                FilamentColorHex(
                    hass, coordinator, spool, config_entry, filament_image_url
                )
            )

        # Extra fields are dynamic per spool, one entity per key.
        for field_key in spool.get("extra", {}):
            extra_sensor = SpoolExtraField(
                hass, coordinator, spool, config_entry, field_key
            )
            entities.append(extra_sensor)
            existing_extra_fields[(spool["id"], field_key)] = extra_sensor

        existing_spool_ids.add(spool["id"])
        return entities

    async def _async_add_new_spools(new_spools: list[dict[str, Any]]) -> None:
        """Build & register sensors for spools the coordinator just discovered."""
        new_entities: list[Any] = []
        # Use a stable index continuation for the picture filename.
        base_idx = len(existing_spool_ids)
        for offset, spool in enumerate(new_spools):
            _LOGGER.info("Dynamically adding sensors for new spool %s", spool.get("id"))
            new_entities.extend(
                await _build_entities_for_spool(spool, base_idx + offset)
            )
        if new_entities:
            async_add_entities(new_entities)

    @callback
    def add_dynamic_entities() -> None:
        """Add new spools and new extra-field sensors as they appear."""
        if not coordinator.data:
            return

        spools = coordinator.data.get("spools", [])

        # New spools (#327): full sensor stack, async because of image gen.
        new_spools = [s for s in spools if s.get("id") not in existing_spool_ids]
        if new_spools:
            hass.async_create_task(_async_add_new_spools(new_spools))

        # New extra fields on already-known spools.
        new_entities = []
        for spool in spools:
            spool_id = spool.get("id")
            if spool_id not in existing_spool_ids:
                # Will be handled by _async_add_new_spools above.
                continue
            for field_key in spool.get("extra", {}):
                entity_key = (spool_id, field_key)
                if entity_key not in existing_extra_fields:
                    extra_field_sensor = SpoolExtraField(
                        hass, coordinator, spool, config_entry, field_key
                    )
                    new_entities.append(extra_field_sensor)
                    existing_extra_fields[entity_key] = extra_field_sensor
                    _LOGGER.info(
                        "Dynamically adding new extra field sensor for spool %s: %s",
                        spool_id,
                        field_key,
                    )

        if new_entities:
            async_add_entities(new_entities)

    if coordinator.data:
        all_entities: list[Any] = []

        # Per-spool sensors via _build_entities_for_spool (single source of
        # truth — same path used for dynamically-added spools later).
        spool_data = coordinator.data.get("spools", [])
        for idx, spool in enumerate(spool_data):
            all_entities.extend(await _build_entities_for_spool(spool, idx))

        # Per-filament Filament device sensor (separate from per-spool stack).
        filament_data = coordinator.data.get("filaments", [])
        for idx, filament in enumerate(filament_data):
            filament_image_url = _generate_filament_entity_picture(filament)
            all_entities.append(
                Filament(
                    hass, coordinator, filament, idx, config_entry, filament_image_url
                )
            )

        async_add_entities(all_entities)

    # Register listener for coordinator updates so new spools (#327) and new
    # extra fields are added without requiring an integration reload.
    coordinator.async_add_listener(add_dynamic_entities)


_HEX_COLOR_RE = re.compile(r"^[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?$")
_IMAGE_SIZE = 100


def _build_color_svg_data_uri(colors: list[str], direction: str) -> str:
    """Return a color swatch as an inline SVG data URI.

    The swatch is embedded in the entity_picture attribute instead of being
    written to ``www/``, which Home Assistant serves under ``/local/`` without
    authentication. Colors are expected as validated RRGGBB[AA] hex strings;
    only the RGB part is used, like the previous PNG images.
    """
    size = _IMAGE_SIZE
    rects: list[str] = []
    if len(colors) > 1 and direction in ("coaxial", "longitudinal"):
        step = size / len(colors)
        for i, color in enumerate(colors):
            if direction == "coaxial":
                x, y, w, h = i * step, 0, step, size
            else:
                x, y, w, h = 0, i * step, size, step
            rects.append(
                f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
                f'fill="#{color[:6]}"/>'
            )
    else:
        rects.append(f'<rect width="{size}" height="{size}" fill="#{colors[0][:6]}"/>')

    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
        'shape-rendering="crispEdges">'
        f'<rect width="{size}" height="{size}" fill="#{DEFAULT_SPOOL_COLOR_HEX}"/>'
        f"{''.join(rects)}</svg>"
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _filament_colors(filament: dict[str, Any]) -> list[str]:
    """Return the valid hex colors of a filament, multi-color first."""
    multi_color_hexes = (filament.get("multi_color_hexes") or "").split(",")
    colors = [c.strip() for c in multi_color_hexes if _HEX_COLOR_RE.match(c.strip())]
    if colors:
        return colors
    color_hex = (filament.get("color_hex") or "").strip()
    if _HEX_COLOR_RE.match(color_hex):
        return [color_hex]
    return []


def _generate_entity_picture(spool_data: dict[str, Any]) -> str | None:
    """Return an entity picture showing the color(s) of a spool's filament."""
    filament = spool_data.get("filament", {})
    colors = _filament_colors(filament)
    if not colors:
        _LOGGER.warning(
            "SpoolManCoordinator: Spool with ID '%s' has no valid color information.",
            spool_data.get("id", "unknown"),
        )
        return None
    return _build_color_svg_data_uri(
        colors, filament.get("multi_color_direction", "coaxial")
    )


def _generate_filament_entity_picture(filament_data: dict[str, Any]) -> str | None:
    """Return an entity picture showing the color(s) of a filament."""
    colors = _filament_colors(filament_data)
    if not colors:
        _LOGGER.warning(
            "SpoolManCoordinator: Filament with ID '%s' has no valid color information.",
            filament_data.get("id", "unknown"),
        )
        return None
    return _build_color_svg_data_uri(
        colors, filament_data.get("multi_color_direction", "coaxial")
    )
