"""Sensor entities for Spoolman integration.

Each sensor class is in its own file following Python best practices.
"""

from .filament import Filament
from .filament_article_number import FilamentArticleNumber
from .filament_bed_temp import FilamentBedTemp
from .filament_color_hex import FilamentColorHex
from .filament_density import FilamentDensity
from .filament_diameter import FilamentDiameter
from .filament_extruder_temp import FilamentExtruderTemp
from .filament_material import FilamentMaterial
from .filament_name import FilamentName
from .filament_weight import FilamentWeight
from .spool import Spool
from .spool_comment import SpoolComment
from .spool_estimated_run_out import SpoolEstimatedRunOut
from .spool_extra_field import SpoolExtraField
from .spool_first_used import SpoolFirstUsed
from .spool_flow_rate import SpoolFlowRate
from .spool_id import SpoolId
from .spool_last_used import SpoolLastUsed
from .spool_location import SpoolLocation
from .spool_lot_number import SpoolLotNumber
from .spool_price import SpoolPrice
from .spool_registered import SpoolRegistered
from .spool_remaining_length import SpoolRemainingLength
from .spool_used_length import SpoolUsedLength
from .spool_used_percentage import SpoolUsedPercentage
from .spool_used_weight import SpoolUsedWeight
from .spool_weight import SpoolWeight
from .vendor_name import VendorName

__all__ = [
    "Filament",
    "FilamentArticleNumber",
    "FilamentBedTemp",
    "FilamentColorHex",
    "FilamentDensity",
    "FilamentDiameter",
    "FilamentExtruderTemp",
    "FilamentMaterial",
    "FilamentName",
    "FilamentWeight",
    "Spool",
    "SpoolComment",
    "SpoolEstimatedRunOut",
    "SpoolExtraField",
    "SpoolFirstUsed",
    "SpoolFlowRate",
    "SpoolId",
    "SpoolLastUsed",
    "SpoolLocation",
    "SpoolLotNumber",
    "SpoolPrice",
    "SpoolRegistered",
    "SpoolRemainingLength",
    "SpoolUsedLength",
    "SpoolUsedPercentage",
    "SpoolUsedWeight",
    "SpoolWeight",
    "VendorName",
]
