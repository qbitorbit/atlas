"""Shell command execution tools for Android."""

from langchain.tools import tool
from typing import Optional
from ..device_manager import DeviceManager
from ..security import SecurityValidator

_device_manager = DeviceManager()


@tool
def execute_shell(command: str, device_id: Optional[str] = None, max_lines: Optional[int] = None, max_size: int = 10000) -> str:
    """Execute ADB shell command on device with risk assessment.

    Args:
        command: Shell command to execute
        device_id: Device serial number (uses default if None)
        max_lines: Limit output lines (optional)
        max_size: Maximum output size in characters (default: 10000)

    Returns:
        str: Command output with risk assessment

    Common safe commands:
    - ls: List files
    - cat: Read files
    - ps: List processes
    - dumpsys: System diagnostics
    - getprop: Get properties
    """
    client = _device_manager.get_device(device_id)
    if not client:
        return f"Device not found: {device_id or 'default'}"

    # Validate command security
    allowed, risk, reason = SecurityValidator.validate_command(command)

    # Add risk warning to output
    risk_msg = f"[Risk: {risk.value.upper()}] {reason}\n\n"

    # Execute command
    success, output = client.shell(command)
    if not success:
        return f"{risk_msg}Failed to execute: {output}"

    # Limit output
    if max_lines:
        lines = output.split("\n")
        output = "\n".join(lines[:max_lines])
        if len(lines) > max_lines:
            output += f"\n... (truncated {len(lines) - max_lines} lines)"

    if len(output) > max_size:
        output = output[:max_size] + f"\n... (truncated {len(output) - max_size} characters)"

    return f"{risk_msg}{output}"
