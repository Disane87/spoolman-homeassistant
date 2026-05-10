"""Sensor description registry for Spoolman.

Each ``SpoolmanSensorEntityDescription`` row replaces a ~60-line legacy
file in ``sensors/*.py``. Trivial sensors (no special
``_handle_coordinator_update`` logic, no per-entity image generation)
live here; complex sensors (Spool main entity, FlowRate, EstimatedRunOut,
UsedPercentage, Location, ExtraField, ColorHex with image, the per-
filament Filament device sensor) keep their own classes in
``sensor_complex.py``.

The values in each row mirror the ``_attr_*`` block from the legacy file
EXACTLY. The characterization snapshot in
``tests/snapshots/test_characterization.ambr`` locks each row's behavior;
do not change ``key``, ``name_suffix``, ``entity_id_suffix``, ``icon``,
``device_class``, ``state_class``, or ``native_unit_of_measurement``
without re-recording the snapshot — those are user-visible identifiers.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import UnitOfLength, UnitOfMass, UnitOfTemperature

from .models import SpoolData


@dataclass(frozen=True, kw_only=True)
class SpoolmanSensorEntityDescription(SensorEntityDescription):
    """Description for a Spoolman per-spool sensor.

    ``value_fn`` extracts the state from a spool dict.
    ``exists_fn`` decides whether to instantiate this sensor for a given
    spool — mirrors the if-checks that lived in the legacy
    ``async_setup_entry`` so dynamic presence is preserved exactly.
    ``name_suffix`` is appended to the spool display name to form
    ``_attr_name``.
    ``entity_id_suffix`` drives both the entity_id and unique_id.
    """

    value_fn: Callable[[SpoolData], Any]
    exists_fn: Callable[[SpoolData], bool] = lambda _spool: True
    name_suffix: str = ""
    entity_id_suffix: str = ""


def _filament(spool: SpoolData, key: str) -> Any:
    """Read a key from the nested filament dict, returning None if missing."""
    return (spool.get("filament") or {}).get(key)


def _vendor_name(spool: SpoolData) -> Any:
    """Return the vendor name from the deeply nested vendor dict, or None."""
    return ((spool.get("filament") or {}).get("vendor") or {}).get("name")


# Each row mirrors the legacy file's _attr_* block. Naming/icon/units must
# match the existing snapshot byte-for-byte.

SENSOR_DESCRIPTIONS: tuple[SpoolmanSensorEntityDescription, ...] = (
    # ---- Always-present basic info ----
    SpoolmanSensorEntityDescription(
        key="id",
        name_suffix="ID",
        entity_id_suffix="id",
        icon="mdi:identifier",
        value_fn=lambda s: s.get("id"),
    ),
    # ---- Filament properties ----
    SpoolmanSensorEntityDescription(
        key="filament_name",
        name_suffix="Filament Name",
        entity_id_suffix="filament_name",
        icon="mdi:label",
        exists_fn=lambda s: bool(_filament(s, "name")),
        value_fn=lambda s: _filament(s, "name"),
    ),
    SpoolmanSensorEntityDescription(
        key="filament_material",
        name_suffix="Material",  # legacy: "{spool_name} Material"
        entity_id_suffix="material",
        icon="mdi:material-design",
        exists_fn=lambda s: bool(_filament(s, "material")),
        value_fn=lambda s: _filament(s, "material"),
    ),
    SpoolmanSensorEntityDescription(
        key="vendor_name",
        name_suffix="Vendor",
        entity_id_suffix="vendor_name",
        icon="mdi:factory",
        exists_fn=lambda s: bool(_vendor_name(s)),
        value_fn=_vendor_name,
    ),
    # ---- Filament print settings ----
    SpoolmanSensorEntityDescription(
        key="filament_extruder_temp",
        name_suffix="Extruder Temp",  # legacy: "{spool_name} Extruder Temp"
        entity_id_suffix="extruder_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        exists_fn=lambda s: _filament(s, "settings_extruder_temp") is not None,
        value_fn=lambda s: _filament(s, "settings_extruder_temp"),
    ),
    SpoolmanSensorEntityDescription(
        key="filament_bed_temp",
        name_suffix="Bed Temp",
        entity_id_suffix="bed_temp",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        exists_fn=lambda s: _filament(s, "settings_bed_temp") is not None,
        value_fn=lambda s: _filament(s, "settings_bed_temp"),
    ),
    SpoolmanSensorEntityDescription(
        key="filament_density",
        name_suffix="Density",
        entity_id_suffix="density",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="g/cm³",
        icon="mdi:chart-bell-curve",
        exists_fn=lambda s: _filament(s, "density") is not None,
        value_fn=lambda s: _filament(s, "density"),
    ),
    SpoolmanSensorEntityDescription(
        key="filament_diameter",
        name_suffix="Diameter",
        entity_id_suffix="diameter",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="mm",
        icon="mdi:diameter-outline",
        exists_fn=lambda s: _filament(s, "diameter") is not None,
        value_fn=lambda s: _filament(s, "diameter"),
    ),
    SpoolmanSensorEntityDescription(
        key="filament_weight",
        name_suffix="Filament Weight",
        entity_id_suffix="filament_weight",
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfMass.GRAMS,
        icon="mdi:weight",
        exists_fn=lambda s: _filament(s, "weight") is not None,
        value_fn=lambda s: _filament(s, "weight"),
    ),
    SpoolmanSensorEntityDescription(
        key="filament_article_number",
        name_suffix="Article Number",
        entity_id_suffix="article_number",
        icon="mdi:identifier",
        exists_fn=lambda s: bool(_filament(s, "article_number")),
        value_fn=lambda s: _filament(s, "article_number"),
    ),
    # ---- Optional spool metadata ----
    SpoolmanSensorEntityDescription(
        key="lot_number",
        name_suffix="Lot Number",
        entity_id_suffix="lot_number",
        icon="mdi:barcode",
        exists_fn=lambda s: bool(s.get("lot_nr")),
        value_fn=lambda s: s.get("lot_nr"),
    ),
    SpoolmanSensorEntityDescription(
        key="comment",
        name_suffix="Comment",
        entity_id_suffix="comment",
        icon="mdi:comment-text",
        exists_fn=lambda s: bool(s.get("comment")),
        value_fn=lambda s: s.get("comment"),
    ),
    SpoolmanSensorEntityDescription(
        key="price",
        name_suffix="Price",
        entity_id_suffix="price",
        icon="mdi:currency-eur",
        exists_fn=lambda s: s.get("price") is not None,
        value_fn=lambda s: s.get("price"),
    ),
    SpoolmanSensorEntityDescription(
        key="spool_weight",
        name_suffix="Spool Weight",
        entity_id_suffix="spool_weight",
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfMass.GRAMS,
        icon="mdi:weight",
        exists_fn=lambda s: s.get("spool_weight") is not None,
        value_fn=lambda s: s.get("spool_weight"),
    ),
    # ---- Measurements ----
    SpoolmanSensorEntityDescription(
        key="used_weight",
        name_suffix="Used Weight",
        entity_id_suffix="used_weight",
        device_class=SensorDeviceClass.WEIGHT,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfMass.GRAMS,
        icon="mdi:weight",
        value_fn=lambda s: round(s.get("used_weight", 0), 3),
    ),
    SpoolmanSensorEntityDescription(
        key="used_length",
        name_suffix="Used Length",
        entity_id_suffix="used_length",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfLength.METERS,
        icon="mdi:tape-measure",
        value_fn=lambda s: round(s.get("used_length", 0), 3),
    ),
    SpoolmanSensorEntityDescription(
        key="remaining_length",
        name_suffix="Remaining Length",
        entity_id_suffix="remaining_length",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfLength.METERS,
        icon="mdi:tape-measure",
        value_fn=lambda s: round(s.get("remaining_length") or 0, 3),
    ),
    # ---- Timestamps ----
    SpoolmanSensorEntityDescription(
        key="registered",
        name_suffix="Registered",
        entity_id_suffix="registered",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-plus-outline",
        exists_fn=lambda s: bool(s.get("registered")),
        value_fn=lambda s: s.get("registered"),
    ),
    SpoolmanSensorEntityDescription(
        key="first_used",
        name_suffix="First Used",
        entity_id_suffix="first_used",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-start",
        exists_fn=lambda s: bool(s.get("first_used")),
        value_fn=lambda s: s.get("first_used"),
    ),
    SpoolmanSensorEntityDescription(
        key="last_used",
        name_suffix="Last Used",
        entity_id_suffix="last_used",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-end",
        exists_fn=lambda s: bool(s.get("last_used")),
        value_fn=lambda s: s.get("last_used"),
    ),
)
