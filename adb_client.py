"""ADB client wrapper for Android device communication."""

import subprocess
from typing import Optional, List, Tuple


class ADBClient:
    """Wrapper for ADB command execution."""

    def __init__(self, device_id: Optional[str] = None):
        """
        Initialize ADB client.

        Args:
            device_id: Optional device serial number
        """
        self.device_id = device_id

    def execute(self, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """
        Execute ADB command.

        Args:
            command: ADB command to execute
            timeout: Command timeout in seconds

        Returns:
            Tuple[bool, str]: (success, output/error)
        """
        try:
            # Build full command
            if self.device_id:
                full_cmd = f"adb -s {self.device_id} {command}"
            else:
                full_cmd = f"adb {command}"

            # Execute command
            result = subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()

        except subprocess.TimeoutExpired:
            return False, f"Command timeout after {timeout}s"
        except Exception as e:
            return False, f"Error executing command: {str(e)}"

    def get_devices(self) -> List[str]:
        """
        Get list of connected devices.

        Returns:
            List[str]: Device serial numbers
        """
        success, output = self.execute("devices")
        if not success:
            return []

        devices = []
        for line in output.split('\n')[1:]:  # Skip header
            if line.strip() and '\tdevice' in line:
                device_id = line.split('\t')[0].strip()
                devices.append(device_id)

        return devices

    def is_device_connected(self, device_id: str) -> bool:
        """Check if specific device is connected."""
        devices = self.get_devices()
        return device_id in devices

    def shell(self, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """Execute shell command on device."""
        return self.execute(f"shell {command}", timeout)
