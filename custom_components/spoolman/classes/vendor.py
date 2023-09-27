from typing import Any
from dataclasses import dataclass


@dataclass
class Vendor:
    id: int
    registered: str
    name: str

    @staticmethod
    def from_dict(obj: Any) -> "Vendor":
        _id = int(obj.get("id"))
        _registered = str(obj.get("registered"))
        _name = str(obj.get("name"))
        return Vendor(_id, _registered, _name)
