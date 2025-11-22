"""UI automation tools for Android."""

from langchain.tools import tool
from typing import Optional
from ..device_manager import DeviceManager

_device_manager = DeviceManager()


@tool
def screenshot(device_id: Optional[str] = None, output_path: str = "screenshot.png", quality: int = 75) -> str:
    """Capture device screenshot.

    Args:
        device_id: Device serial number (uses default if None)
        output_path: Output file path (default: screenshot.png)
        quality: JPEG quality 1-100 (default: 75)

    Returns:
        str: Screenshot capture status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Capture screenshot on device
    device_path = "/sdcard/screenshot.png"
    success, output = client.shell(f"screencap -p {device_path}")
    if not success:
        return f"Failed to capture screenshot: {output}"

    # Pull screenshot to host
    success, output = client.execute(f"pull {device_path} {output_path}")
    if success:
        # Cleanup device screenshot
        client.shell(f"rm {device_path}")
        return f"Screenshot saved to {output_path}"
    else:
        return f"Failed to download screenshot: {output}"


@tool
def tap(x: int, y: int, device_id: Optional[str] = None) -> str:
    """Simulate tap at screen coordinates.

    Args:
        x: X coordinate
        y: Y coordinate
        device_id: Device serial number (uses default if None)

    Returns:
        str: Tap status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"input tap {x} {y}")
    return f"Tapped at ({x}, {y})" if success else f"Failed to tap: {output}"


@tool
def swipe(start_x: int, start_y: int, end_x: int, end_y: int, duration_ms: int = 300, device_id: Optional[str] = None) -> str:
    """Simulate swipe gesture.

    Args:
        start_x: Start X coordinate
        start_y: Start Y coordinate
        end_x: End X coordinate
        end_y: End Y coordinate
        duration_ms: Swipe duration in milliseconds (default: 300)
        device_id: Device serial number (uses default if None)

    Returns:
        str: Swipe status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}")
    return f"Swiped from ({start_x},{start_y}) to ({end_x},{end_y})" if success else f"Failed to swipe: {output}"


@tool
def input_text(text: str, device_id: Optional[str] = None) -> str:
    """Type text into focused input field.

    Args:
        text: Text to input
        device_id: Device serial number (uses default if None)

    Returns:
        str: Input status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Replace spaces with %s for ADB input
    formatted_text = text.replace(" ", "%s")

    success, output = client.shell(f"input text '{formatted_text}'")
    return f"Input text: {text}" if success else f"Failed to input text: {output}"


@tool
def press_key(keycode: int, device_id: Optional[str] = None) -> str:
    """Press hardware or software key.

    Args:
        keycode: Android keycode (e.g., 3=HOME, 4=BACK, 24=VOLUME_UP)
        device_id: Device serial number (uses default if None)

    Returns:
        str: Key press status

    Common keycodes:
    - HOME: 3
    - BACK: 4
    - MENU: 82
    - VOLUME_UP: 24
    - VOLUME_DOWN: 25
    - POWER: 26
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"input keyevent {keycode}")
    return f"Pressed key {keycode}" if success else f"Failed to press key: {output}"


@tool
def start_intent(package: str, activity: Optional[str] = None, extras: Optional[str] = None, device_id: Optional[str] = None) -> str:
    """Launch specific app activity or component.

    Args:
        package: Package name
        activity: Activity name (optional)
        extras: Intent extras in format "key=value,key2=value2" (optional)
        device_id: Device serial number (uses default if None)

    Returns:
        str: Intent start status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    cmd = "am start"

    if activity:
        cmd += f" -n {package}/{activity}"
    else:
        cmd += f" {package}"

    if extras:
        # Parse extras and add to command
        for extra in extras.split(","):
            if "=" in extra:
                key, value = extra.split("=", 1)
                cmd += f" --es {key} {value}"

    success, output = client.shell(cmd)
    return output if success else f"Failed to start intent: {output}"
