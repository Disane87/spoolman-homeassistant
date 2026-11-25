"""DeviceInfo helpers."""

from typing import Any


def device_info_dict(info: Any) -> dict[str, Any]:
    """Return a DeviceInfo as a plain dict.

    DeviceInfo is a dataclass from HA 2026.12 (unpacking it is deprecated, #912)
    and a TypedDict on older versions, which have no as_dict().
    """
    return dict(info.as_dict() if hasattr(info, "as_dict") else info)
