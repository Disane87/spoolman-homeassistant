"""Typed shapes for Spoolman API and coordinator data.

Defined as TypedDict (not dataclass) because we receive plain dicts from
JSON; converting to dataclasses would mean a deep copy on every coordinator
refresh and would risk diverging from the existing characterization snapshot.
"""

from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class VendorData(TypedDict, total=False):
    """Vendor record nested in filament data."""

    id: int
    name: str


class FilamentData(TypedDict, total=False):
    """Filament record returned by Spoolman."""

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
    total_remaining_weight: float


class SpoolData(TypedDict):
    """Spool record returned by Spoolman, augmented by the coordinator."""

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
    extra: NotRequired[dict[str, Any]]
    klipper_active_spool: NotRequired[bool]


class ExtraFieldMetadata(TypedDict, total=False):
    """Extra-field metadata returned by ``GET /field/spool``."""

    name: str | None
    field_type: str | None
    unit: str | None
    choices: list[str] | None
    multi_choice: bool | None


class CoordinatorData(TypedDict):
    """Shape returned by SpoolManCoordinator._async_update_data."""

    spools: list[SpoolData]
    filaments: list[FilamentData]
    extra_fields: dict[str, dict[str, ExtraFieldMetadata]]
    locations: list[str]
