"""Device management tools for Android."""

from langchain.tools import tool
from typing import Optional, List
from ..adb_client import ADBClient
from ..device_manager import DeviceManager

# Global device manager instance
_device_manager = DeviceManager()


@tool
def list_devices() -> str:
    """List all connected Android devices.

    Returns:
        str: List of connected device serial numbers
    """
    devices = _device_manager.scan_devices()

    if not devices:
        return "No devices connected"

    result = f"Found {len(devices)} device(s):\n"
    for i, device_id in enumerate(devices, 1):
        result += f"{i}. {device_id}"
        if device_id == _device_manager.get_default_device():
            result += " (default)"
        result += "\n"

    return result.strip()


@tool
def connect_device(address: str, port: int = 5555) -> str:
    """Connect to Android device via TCP/IP.

    Args:
        address: IP address of the device
        port: Port number (default: 5555)

    Returns:
        str: Connection status
    """
    client = ADBClient()
    success, output = client.execute(f"connect {address}:{port}")

    if success:
        _device_manager.scan_devices()
        return f"Connected to {address}:{port}"
    else:
        return f"Failed to connect: {output}"


@tool
def disconnect_device(address: str, port: int = 5555) -> str:
    """Disconnect from Android device (TCP/IP connection).

    Args:
        address: IP address of the device
        port: Port number (default: 5555)

    Returns:
        str: Disconnection status
    """
    device_id = f"{address}:{port}"
    client = ADBClient()
    success, output = client.execute(f"disconnect {device_id}")

    if success:
        _device_manager.remove_device(device_id)
        return f"Disconnected from {device_id}"
    else:
        return f"Failed to disconnect: {output}"


@tool
def reboot_device(device_id: Optional[str] = None, mode: str = "normal") -> str:
    """Reboot Android device.

    Args:
        device_id: Device serial number (uses default if None)
        mode: Reboot mode - 'normal', 'recovery', or 'bootloader'

    Returns:
        str: Reboot status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Build reboot command
    if mode == "recovery":
        cmd = "reboot recovery"
    elif mode == "bootloader":
        cmd = "reboot bootloader"
    else:
        cmd = "reboot"

    success, output = client.execute(cmd)

    if success:
        return f"Device rebooting to {mode} mode"
    else:
        return f"Failed to reboot: {output}"


@tool
def device_properties(device_id: Optional[str] = None) -> str:
    """Get detailed device properties and information.

    Args:
        device_id: Device serial number (uses default if None)

    Returns:
        str: Device properties including model, brand, Android version, etc.
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    properties = {
        "Model": "ro.product.model",
        "Brand": "ro.product.brand",
        "Device": "ro.product.device",
        "Android Version": "ro.build.version.release",
        "SDK Level": "ro.build.version.sdk",
        "Build Number": "ro.build.display.id",
        "Serial": "ro.serialno",
        "Manufacturer": "ro.product.manufacturer"
    }

    result = []
    for name, prop in properties.items():
        success, value = client.shell(f"getprop {prop}")
        if success and value:
            result.append(f"{name}: {value}")

    return "\n".join(result) if result else "Unable to retrieve device properties"
