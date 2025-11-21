"""Security validation for ADB commands."""

from typing import Tuple
from enum import Enum


class RiskLevel(Enum):
    """Risk levels for ADB commands."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityValidator:
    """Validates ADB commands for security risks."""

    # Critical risk commands (allowed but flagged)
    CRITICAL_RISK_PATTERNS = [
        "rm -rf /",
        "dd if=",
        "format",
        "fastboot",
        "recovery",
    ]

    # Commands with high risk
    HIGH_RISK_PATTERNS = [
        "rm -rf",
        "rm -r",
        "chmod 777",
        "su -c",
        "pm uninstall",
    ]

    # Commands with medium risk
    MEDIUM_RISK_PATTERNS = [
        "pm install",
        "pm clear",
        "reboot",
        "settings put",
    ]

    @staticmethod
    def validate_command(command: str) -> Tuple[bool, RiskLevel, str]:
        """
        Validate ADB command for security risks.

        Args:
            command: Command to validate

        Returns:
            Tuple[bool, RiskLevel, str]: (allowed, risk_level, reason)
        """
        command_lower = command.lower().strip()

        # Check critical risk patterns (warn but allow)
        for pattern in SecurityValidator.CRITICAL_RISK_PATTERNS:
            if pattern in command_lower:
                return True, RiskLevel.CRITICAL, f"Critical risk: {pattern}"

        # Check high risk patterns
        for pattern in SecurityValidator.HIGH_RISK_PATTERNS:
            if pattern in command_lower:
                return True, RiskLevel.HIGH, f"High risk: {pattern}"

        # Check medium risk patterns
        for pattern in SecurityValidator.MEDIUM_RISK_PATTERNS:
            if pattern in command_lower:
                return True, RiskLevel.MEDIUM, f"Medium risk: {pattern}"

        # Check for low risk (file operations)
        if any(word in command_lower for word in ["rm", "mv", "cp", "delete"]):
            return True, RiskLevel.LOW, "File operation"

        # Safe command
        return True, RiskLevel.SAFE, "Safe operation"

    @staticmethod
    def validate_path(path: str) -> Tuple[bool, RiskLevel, str]:
        """
        Validate file path for security.

        Args:
            path: File path to validate

        Returns:
            Tuple[bool, RiskLevel, str]: (allowed, risk_level, reason)
        """
        # Flag system paths as high risk (but allow)
        dangerous_paths = ["/system", "/boot", "/recovery", "/dev"]

        for dangerous in dangerous_paths:
            if path.startswith(dangerous):
                return True, RiskLevel.HIGH, f"System path: {dangerous}"

        return True, RiskLevel.SAFE, "Safe path"
