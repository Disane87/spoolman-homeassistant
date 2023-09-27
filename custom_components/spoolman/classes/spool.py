from dataclasses import dataclass
from typing import Any

from .classes.filament import Filament


@dataclass
class Spool:
    id: int
    registered: str
    first_used: str
    last_used: str
    filament: Filament
    remaining_weight: float
    used_weight: float
    remaining_length: float
    used_length: float
    location: str
    archived: bool

    @staticmethod
    def from_dict(obj: Any) -> "Spool":
        _id = int(obj.get("id"))
        _registered = str(obj.get("registered"))
        _first_used = str(obj.get("first_used"))
        _last_used = str(obj.get("last_used"))
        _filament = Filament.from_dict(obj.get("filament"))
        _remaining_weight = float(obj.get("remaining_weight"))
        _used_weight = float(obj.get("used_weight"))
        _remaining_length = float(obj.get("remaining_length"))
        _used_length = float(obj.get("used_length"))
        _location = str(obj.get("location"))
        _archived = bool(obj.get("archived"))
        return Spool(
            _id,
            _registered,
            _first_used,
            _last_used,
            _filament,
            _remaining_weight,
            _used_weight,
            _remaining_length,
            _used_length,
            _location,
            _archived,
        )
