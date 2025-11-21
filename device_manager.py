"""Device manager for Android device connections."""

from typing import Dict, Optional, List
from .adb_client import ADBClient


class DeviceManager:
    """Manages Android device connections."""

    def __init__(self):
        """Initialize device manager."""
        self._devices: Dict[str, ADBClient] = {}
        self._default_device: Optional[str] = None

    def scan_devices(self) -> List[str]:
        """
        Scan for connected devices.

        Returns:
            List[str]: List of device IDs
        """
        client = ADBClient()
        devices = client.get_devices()

        # Update device pool
        for device_id in devices:
            if device_id not in self._devices:
                self._devices[device_id] = ADBClient(device_id)

        # Set default device if not set
        if devices and not self._default_device:
            self._default_device = devices[0]

        return devices

    def get_device(self, device_id: Optional[str] = None) -> Optional[ADBClient]:
        """
        Get ADB client for device.

        Args:
            device_id: Device ID (uses default if None)

        Returns:
            ADBClient or None
        """
        if device_id is None:
            device_id = self._default_device

        if device_id and device_id in self._devices:
            return self._devices[device_id]

        return None

    def set_default_device(self, device_id: str) -> bool:
        """
        Set default device.

        Args:
            device_id: Device ID to set as default

        Returns:
            bool: Success
        """
        if device_id in self._devices:
            self._default_device = device_id
            return True
        return False

    def get_default_device(self) -> Optional[str]:
        """Get default device ID."""
        return self._default_device

    def remove_device(self, device_id: str):
        """Remove device from pool."""
        if device_id in self._devices:
            del self._devices[device_id]
            if self._default_device == device_id:
                self._default_device = None
