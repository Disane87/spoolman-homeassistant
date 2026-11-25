"""Complex Spoolman sensor classes that don't fit the description registry.

The simple property sensors that previously lived here were collapsed
into ``custom_components.spoolman.sensor_descriptions.SENSOR_DESCRIPTIONS``
in phase 3 of the platinum refactor. Only sensors with custom logic
(image generation, computed state, deeply spool-specific behavior)
remain as their own classes.
"""

from .filament import Filament
from .filament_color_hex import FilamentColorHex
from .spool import Spool
from .spool_estimated_run_out import SpoolEstimatedRunOut
from .spool_extra_field import SpoolExtraField
from .spool_flow_rate import SpoolFlowRate
from .spool_location import SpoolLocation
from .spool_used_percentage import SpoolUsedPercentage

__all__ = [
    "Filament",
    "FilamentColorHex",
    "Spool",
    "SpoolEstimatedRunOut",
    "SpoolExtraField",
    "SpoolFlowRate",
    "SpoolLocation",
    "SpoolUsedPercentage",
]
