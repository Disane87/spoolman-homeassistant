"""Tests for the device_info_dict helper (#912)."""

from homeassistant.helpers.device_registry import DeviceInfo

from custom_components.spoolman.helpers.device_info import device_info_dict


def test_typed_dict_device_info() -> None:
    """Pre-2026.12 DeviceInfo is a TypedDict and is returned as a dict."""
    info = DeviceInfo(name="Spool", model="PLA")
    assert device_info_dict(info) == {"name": "Spool", "model": "PLA"}


def test_dataclass_device_info_uses_as_dict() -> None:
    """HA 2026.12+ DeviceInfo is a dataclass; as_dict() must be used, not unpacking."""

    class DataclassInfo:
        def as_dict(self) -> dict:
            return {"name": "Spool"}

        def keys(self):  # unpacking would hit this deprecated path
            raise AssertionError("DeviceInfo must not be unpacked")

    assert device_info_dict(DataclassInfo()) == {"name": "Spool"}
