"""System diagnostics and logging tools for Android."""

from langchain.tools import tool
from typing import Optional
from ..device_manager import DeviceManager

_device_manager = DeviceManager()


@tool
def device_logcat(device_id: Optional[str] = None, lines: int = 100, filter_expr: Optional[str] = None, buffer: str = "main", max_size: int = 10000) -> str:
    """Fetch system and application logs.

    Args:
        device_id: Device serial number (uses default if None)
        lines: Number of log lines to retrieve (default: 100)
        filter_expr: Log filter expression (e.g., "ActivityManager:I *:S")
        buffer: Log buffer (main, system, crash, events, radio, all)
        max_size: Maximum output size in characters (default: 10000)

    Returns:
        str: Log output
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    cmd = f"logcat -b {buffer} -t {lines}"
    if filter_expr:
        cmd += f" {filter_expr}"

    success, output = client.shell(cmd, timeout=60)
    if success:
        return output[:max_size] if len(output) > max_size else output
    else:
        return f"Failed to get logs: {output}"


@tool
def app_logs(package_name: str, device_id: Optional[str] = None, lines: int = 100) -> str:
    """Retrieve logs for specific application.

    Args:
        package_name: Package name to get logs for
        device_id: Device serial number (uses default if None)
        lines: Number of log lines (default: 100)

    Returns:
        str: Application logs
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Get PID for package
    success, pid_output = client.shell(f"pidof {package_name}")
    if not success or not pid_output:
        return f"App not running: {package_name}"

    pid = pid_output.strip()

    # Get logs for that PID
    success, output = client.shell(f"logcat -t {lines} --pid={pid}")
    return output if success else f"Failed to get app logs: {output}"


@tool
def device_anr_logs(device_id: Optional[str] = None) -> str:
    """Capture Application Not Responding (ANR) trace files.

    Args:
        device_id: Device serial number (uses default if None)

    Returns:
        str: ANR trace information
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Check for ANR traces
    success, output = client.shell("ls -la /data/anr/")
    if not success:
        return f"Failed to access ANR directory: {output}"

    if "No such file" in output or not output.strip():
        return "No ANR traces found"

    return output


@tool
def device_crash_logs(device_id: Optional[str] = None) -> str:
    """Retrieve application crash reports and tombstones.

    Args:
        device_id: Device serial number (uses default if None)

    Returns:
        str: Crash logs and tombstones
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Get recent crash logs from logcat
    success, output = client.shell("logcat -b crash -t 50")
    return output if success else f"Failed to get crash logs: {output}"


@tool
def device_battery_stats(device_id: Optional[str] = None) -> str:
    """Analyze device battery usage and status.

    Args:
        device_id: Device serial number (uses default if None)

    Returns:
        str: Battery status, level, temperature, health
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell("dumpsys battery")
    if not success:
        return f"Failed to get battery stats: {output}"

    # Extract key battery information
    lines = output.split("\n")
    result = []
    for line in lines:
        if any(key in line for key in ["level", "status", "health", "temperature", "voltage"]):
            result.append(line.strip())

    return "\n".join(result) if result else output


@tool
def capture_bugreport(device_id: Optional[str] = None, output_path: str = "bugreport.zip", timeout: int = 300) -> str:
    """Generate comprehensive diagnostic bugreport.

    Args:
        device_id: Device serial number (uses default if None)
        output_path: Output file path (default: bugreport.zip)
        timeout: Command timeout in seconds (default: 300)

    Returns:
        str: Bugreport generation status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.execute(f"bugreport {output_path}", timeout=timeout)
    return f"Bugreport saved to {output_path}" if success else f"Failed to generate bugreport: {output}"


@tool
def dump_heap(package_name: str, device_id: Optional[str] = None, output_path: str = "heap.hprof") -> str:
    """Capture Java or native heap dump for memory analysis.

    Args:
        package_name: Package name or process ID
        device_id: Device serial number (uses default if None)
        output_path: Output file path (default: heap.hprof)

    Returns:
        str: Heap dump status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Dump heap on device
    device_path = f"/sdcard/{output_path}"
    success, output = client.shell(f"am dumpheap {package_name} {device_path}")
    if not success:
        return f"Failed to dump heap: {output}"

    # Pull heap dump to host
    success, output = client.execute(f"pull {device_path} {output_path}")
    if success:
        # Cleanup device heap dump
        client.shell(f"rm {device_path}")
        return f"Heap dump saved to {output_path}"
    else:
        return f"Failed to download heap dump: {output}"
