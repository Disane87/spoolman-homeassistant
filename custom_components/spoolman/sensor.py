"""Spoolman home assistant sensor platform."""

import logging
import os
from typing import Any, cast

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from PIL import Image, ImageDraw

from .const import (
    DEFAULT_SPOOL_COLOR_HEX,
    DOMAIN,
    LOCAL_IMAGE_PATH,
    PUBLIC_IMAGE_PATH,
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

    @property  # type: ignore[misc]
    def state(self) -> Any:
        """Return the value extracted from the spool dict by ``value_fn``.

        Overrides ``state`` rather than ``native_value`` so timestamp-class
        sensors that store ISO strings (the legacy convention) keep their
        raw string state. Migrating to ``native_value`` would force a
        datetime parse and change the snapshotted state representation.
        """
        return self.entity_description.value_fn(self._spool)


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

    image_dir = hass.config.path(PUBLIC_IMAGE_PATH)

    async def _build_entities_for_spool(spool: dict[str, Any], idx: int) -> list[Any]:
        """Build the full sensor stack for a single spool.

        Complex sensors (Spool main entity, FlowRate, EstimatedRunOut,
        UsedPercentage, Location, ExtraField, ColorHex with image) keep
        their own classes in ``sensors/``. Trivial property sensors are
        instantiated from :data:`SENSOR_DESCRIPTIONS`.
        """
        entities: list[Any] = []
        image_url = await hass.async_add_executor_job(
            _generate_entity_picture, spool, image_dir
        )

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
            filament_image_url = await hass.async_add_executor_job(
                _generate_filament_entity_picture, filament, image_dir
            )
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
            filament_image_url = await hass.async_add_executor_job(
                _generate_filament_entity_picture, filament, image_dir
            )
            all_entities.append(
                Filament(
                    hass, coordinator, filament, idx, config_entry, filament_image_url
                )
            )

        async_add_entities(all_entities)

    # Register listener for coordinator updates so new spools (#327) and new
    # extra fields are added without requiring an integration reload.
    coordinator.async_add_listener(add_dynamic_entities)


def _generate_entity_picture(spool_data: dict[str, Any], image_dir: str) -> str | None:
    """Generate an entity picture with the specified color(s) and save it to the www directory."""
    filament = spool_data.get("filament", {})

    # Retrieve color(s)
    multi_color_hexes = filament.get("multi_color_hexes", "").split(",")
    color_hex = filament.get("color_hex", DEFAULT_SPOOL_COLOR_HEX)
    multi_color_direction = filament.get("multi_color_direction", "coaxial")

    # Determine colors: prioritize multi_color_hexes if available
    if multi_color_hexes and any(c.strip() for c in multi_color_hexes):
        colors = [c.strip() for c in multi_color_hexes if len(c.strip()) == 6]
    elif color_hex:
        colors = [color_hex]
    else:
        _LOGGER.warning(
            "SpoolManCoordinator: Spool with ID '%s' has no valid color information.",
            spool_data.get("id", "unknown"),
        )
        return None

    # Create image
    image_size = (100, 100)
    image = Image.new("RGB", image_size, int(DEFAULT_SPOOL_COLOR_HEX, 16))
    draw = ImageDraw.Draw(image)

    # Draw colors
    if len(colors) > 1:
        if multi_color_direction == "coaxial":
            step = image_size[0] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle(
                    [(i * step, 0), ((i + 1) * step - 1, image_size[1])],
                    fill=f"#{color}",
                )
        elif multi_color_direction == "longitudinal":
            step = image_size[1] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle(
                    [(0, i * step), (image_size[0], (i + 1) * step - 1)],
                    fill=f"#{color}",
                )
    else:
        # Single color fallback
        draw.rectangle([(0, 0), image_size], fill=f"#{colors[0]}")

    # Save the image
    image_name = f"spool_{spool_data.get('id', 'unknown')}.png"
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, image_name)
    image.save(image_path)

    # Return the URL for the saved image
    return f"{LOCAL_IMAGE_PATH}/{image_name}"


def _generate_filament_entity_picture(
    filament_data: dict[str, Any], image_dir: str
) -> str | None:
    """Generate a filament entity picture with the specified color(s) and save it to the www directory."""

    # Retrieve color(s)
    multi_color_hexes = filament_data.get("multi_color_hexes", "").split(",")
    color_hex = filament_data.get("color_hex", DEFAULT_SPOOL_COLOR_HEX)
    multi_color_direction = filament_data.get("multi_color_direction", "coaxial")

    # Determine colors: prioritize multi_color_hexes if available
    if multi_color_hexes and any(c.strip() for c in multi_color_hexes):
        colors = [c.strip() for c in multi_color_hexes if len(c.strip()) == 6]
    elif color_hex:
        colors = [color_hex]
    else:
        _LOGGER.warning(
            "SpoolManCoordinator: Filament with ID '%s' has no valid color information.",
            filament_data.get("id", "unknown"),
        )
        return None

    # Create image
    image_size = (100, 100)
    image = Image.new("RGB", image_size, int(DEFAULT_SPOOL_COLOR_HEX, 16))
    draw = ImageDraw.Draw(image)

    # Draw colors
    if len(colors) > 1:
        if multi_color_direction == "coaxial":
            step = image_size[0] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle(
                    [(i * step, 0), ((i + 1) * step - 1, image_size[1])],
                    fill=f"#{color}",
                )
        elif multi_color_direction == "longitudinal":
            step = image_size[1] // len(colors)
            for i, color in enumerate(colors):
                draw.rectangle(
                    [(0, i * step), (image_size[0], (i + 1) * step - 1)],
                    fill=f"#{color}",
                )
    else:
        # Single color fallback
        draw.rectangle([(0, 0), image_size], fill=f"#{colors[0]}")

    # Save the image
    image_name = f"filament_{filament_data.get('id', 'unknown')}.png"
    os.makedirs(image_dir, exist_ok=True)
    image_path = os.path.join(image_dir, image_name)
    image.save(image_path)

    # Return the URL for the saved image
    return f"{LOCAL_IMAGE_PATH}/{image_name}"
