"""App management tools for Android."""

from langchain.tools import tool
from typing import Optional
from ..device_manager import DeviceManager

_device_manager = DeviceManager()


@tool
def list_packages(device_id: Optional[str] = None, include_system: bool = False) -> str:
    """List installed applications on device.

    Args:
        device_id: Device serial number (uses default if None)
        include_system: Include system apps (default: False)

    Returns:
        str: List of installed packages
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    cmd = "pm list packages"
    if not include_system:
        cmd += " -3"  # Third-party apps only

    success, output = client.shell(cmd)
    if not success:
        return f"Failed to list packages: {output}"

    packages = [line.replace("package:", "") for line in output.split("\n") if line.startswith("package:")]
    return f"Found {len(packages)} package(s):\n" + "\n".join(packages)


@tool
def install_app(apk_path: str, device_id: Optional[str] = None, reinstall: bool = False, grant_permissions: bool = False) -> str:
    """Install APK on device.

    Args:
        apk_path: Local path to APK file
        device_id: Device serial number (uses default if None)
        reinstall: Allow reinstall (default: False)
        grant_permissions: Grant all permissions (default: False)

    Returns:
        str: Installation status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    cmd = f"install"
    if reinstall:
        cmd += " -r"
    if grant_permissions:
        cmd += " -g"
    cmd += f" {apk_path}"

    success, output = client.execute(cmd)
    return output if success else f"Installation failed: {output}"


@tool
def uninstall_app(package_name: str, device_id: Optional[str] = None, keep_data: bool = False) -> str:
    """Uninstall application from device.

    Args:
        package_name: Package name to uninstall
        device_id: Device serial number (uses default if None)
        keep_data: Keep app data and cache (default: False)

    Returns:
        str: Uninstallation status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    cmd = f"uninstall"
    if keep_data:
        cmd += " -k"
    cmd += f" {package_name}"

    success, output = client.execute(cmd)
    return output if success else f"Uninstallation failed: {output}"


@tool
def start_app(package_name: str, device_id: Optional[str] = None, activity: Optional[str] = None) -> str:
    """Launch application on device.

    Args:
        package_name: Package name to launch
        device_id: Device serial number (uses default if None)
        activity: Specific activity to start (optional)

    Returns:
        str: Launch status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    if activity:
        component = f"{package_name}/{activity}"
    else:
        component = package_name

    success, output = client.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
    return "App started" if success else f"Failed to start app: {output}"


@tool
def stop_app(package_name: str, device_id: Optional[str] = None) -> str:
    """Force stop running application.

    Args:
        package_name: Package name to stop
        device_id: Device serial number (uses default if None)

    Returns:
        str: Stop status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"am force-stop {package_name}")
    return "App stopped" if success else f"Failed to stop app: {output}"


@tool
def clear_app_data(package_name: str, device_id: Optional[str] = None) -> str:
    """Clear application data and cache.

    Args:
        package_name: Package name to clear
        device_id: Device serial number (uses default if None)

    Returns:
        str: Clear status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"pm clear {package_name}")
    return output if success else f"Failed to clear data: {output}"


@tool
def get_app_info(package_name: str, device_id: Optional[str] = None) -> str:
    """Get detailed application information.

    Args:
        package_name: Package name
        device_id: Device serial number (uses default if None)

    Returns:
        str: App information including version, permissions, status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"dumpsys package {package_name}")
    if not success:
        return f"Failed to get app info: {output}"

    # Extract key information
    lines = output.split("\n")
    info = []
    for line in lines[:50]:  # First 50 lines usually have key info
        if "versionName" in line or "versionCode" in line or "targetSdk" in line:
            info.append(line.strip())

    return "\n".join(info) if info else output[:500]


@tool
def get_app_manifest(package_name: str, device_id: Optional[str] = None) -> str:
    """Extract AndroidManifest.xml details.

    Args:
        package_name: Package name
        device_id: Device serial number (uses default if None)

    Returns:
        str: Manifest information
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Get APK path first
    success, path_output = client.shell(f"pm path {package_name}")
    if not success or not path_output:
        return f"Package not found: {package_name}"

    apk_path = path_output.replace("package:", "").strip()

    # Dump manifest
    success, output = client.shell(f"aapt dump badging {apk_path}")
    return output[:1000] if success else f"Failed to get manifest: {output}"


@tool
def get_app_permissions(package_name: str, device_id: Optional[str] = None) -> str:
    """List application permissions and their status.

    Args:
        package_name: Package name
        device_id: Device serial number (uses default if None)

    Returns:
        str: List of permissions
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"dumpsys package {package_name} | grep permission")
    return output if success else f"Failed to get permissions: {output}"


@tool
def get_app_activities(package_name: str, device_id: Optional[str] = None) -> str:
    """List all activities in an application.

    Args:
        package_name: Package name
        device_id: Device serial number (uses default if None)

    Returns:
        str: List of activities
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"dumpsys package {package_name} | grep Activity")
    return output[:1000] if success else f"Failed to get activities: {output}"
