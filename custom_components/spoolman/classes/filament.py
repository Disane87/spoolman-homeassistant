from dataclasses import dataclass
from typing import Any

from .classes.vendor import Vendor


@dataclass
class Filament:
    id: int
    registered: str
    name: str
    vendor: Vendor
    material: str
    price: float
    density: float
    diameter: float
    weight: int
    article_number: str
    comment: str
    settings_extruder_temp: int
    settings_bed_temp: int
    color_hex: str

    @staticmethod
    def from_dict(obj: Any) -> "Filament":
        _id = int(obj.get("id"))
        _registered = str(obj.get("registered"))
        _name = str(obj.get("name"))
        _vendor = Vendor.from_dict(obj.get("vendor"))
        _material = str(obj.get("material"))
        _price = float(obj.get("price"))
        _density = float(obj.get("density"))
        _diameter = float(obj.get("diameter"))
        _weight = int(obj.get("weight"))
        _article_number = str(obj.get("article_number"))
        _comment = str(obj.get("comment"))
        _settings_extruder_temp = int(obj.get("settings_extruder_temp"))
        _settings_bed_temp = int(obj.get("settings_bed_temp"))
        _color_hex = str(obj.get("color_hex"))
        return Filament(
            _id,
            _registered,
            _name,
            _vendor,
            _material,
            _price,
            _density,
            _diameter,
            _weight,
            _article_number,
            _comment,
            _settings_extruder_temp,
            _settings_bed_temp,
            _color_hex,
        )
