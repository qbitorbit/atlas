"""File system tools for Android."""

from langchain.tools import tool
from typing import Optional
from ..device_manager import DeviceManager

_device_manager = DeviceManager()


@tool
def list_directory(path: str, device_id: Optional[str] = None) -> str:
    """List contents of a directory on device.

    Args:
        path: Directory path to list
        device_id: Device serial number (uses default if None)

    Returns:
        str: Directory contents
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"ls -la {path}")
    return output if success else f"Failed to list directory: {output}"


@tool
def read_file(path: str, device_id: Optional[str] = None, max_size: int = 102400) -> str:
    """Read text file contents from device.

    Args:
        path: File path to read
        device_id: Device serial number (uses default if None)
        max_size: Maximum file size in bytes (default: 100KB)

    Returns:
        str: File contents or error message
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Check file size first
    success, size_output = client.shell(f"stat -c%s {path}")
    if success and size_output.isdigit():
        if int(size_output) > max_size:
            return f"File too large ({size_output} bytes). Use pull_file for large files."

    success, output = client.shell(f"cat {path}")
    return output if success else f"Failed to read file: {output}"


@tool
def write_file(path: str, content: str, device_id: Optional[str] = None) -> str:
    """Write content to a file on device.

    Args:
        path: File path to write
        content: Content to write
        device_id: Device serial number (uses default if None)

    Returns:
        str: Write status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Escape content for shell
    escaped_content = content.replace("'", "'\\''")

    success, output = client.shell(f"echo '{escaped_content}' > {path}")
    return "File written successfully" if success else f"Failed to write file: {output}"


@tool
def push_file(local_path: str, device_path: str, device_id: Optional[str] = None) -> str:
    """Upload file from host to device.

    Args:
        local_path: Local file path on host
        device_path: Destination path on device
        device_id: Device serial number (uses default if None)

    Returns:
        str: Upload status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.execute(f"push {local_path} {device_path}")
    return output if success else f"Failed to push file: {output}"


@tool
def pull_file(device_path: str, local_path: Optional[str] = None, device_id: Optional[str] = None) -> str:
    """Download file from device to host.

    Args:
        device_path: File path on device
        local_path: Local destination path (optional, uses filename if None)
        device_id: Device serial number (uses default if None)

    Returns:
        str: Download status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    cmd = f"pull {device_path}"
    if local_path:
        cmd += f" {local_path}"

    success, output = client.execute(cmd)
    return output if success else f"Failed to pull file: {output}"


@tool
def create_directory(path: str, device_id: Optional[str] = None) -> str:
    """Create directory on device.

    Args:
        path: Directory path to create
        device_id: Device serial number (uses default if None)

    Returns:
        str: Creation status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"mkdir -p {path}")
    return "Directory created" if success else f"Failed to create directory: {output}"


@tool
def delete_file(path: str, device_id: Optional[str] = None, recursive: bool = False) -> str:
    """Delete file or directory on device.

    Args:
        path: Path to delete
        device_id: Device serial number (uses default if None)
        recursive: Delete recursively for directories (default: False)

    Returns:
        str: Deletion status
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    cmd = "rm -rf" if recursive else "rm"
    success, output = client.shell(f"{cmd} {path}")
    return "Deleted successfully" if success else f"Failed to delete: {output}"


@tool
def file_exists(path: str, device_id: Optional[str] = None) -> str:
    """Check if file or directory exists on device.

    Args:
        path: Path to check
        device_id: Device serial number (uses default if None)

    Returns:
        str: Existence status (exists/does not exist)
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"test -e {path} && echo exists || echo not_found")
    return output.strip() if success else "Error checking file"


@tool
def file_stats(path: str, device_id: Optional[str] = None) -> str:
    """Get file or directory metadata.

    Args:
        path: Path to check
        device_id: Device serial number (uses default if None)

    Returns:
        str: File metadata (size, permissions, dates)
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    success, output = client.shell(f"stat {path}")
    return output if success else f"Failed to get file stats: {output}"
