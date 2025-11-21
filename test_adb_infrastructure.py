"""Test Android Infrastructure - Checkpoint 2.2"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from domains.android.adb_client import ADBClient
from domains.android.security import SecurityValidator, RiskLevel
from domains.android.device_manager import DeviceManager


def test_adb_infrastructure():
    """Test Android ADB infrastructure."""
    print("Testing Android ADB Infrastructure...")
    print("=" * 60)

    # Test 1: ADB Client
    print("\n1. Testing ADB client creation...")
    client = ADBClient()
    print(f"   ✓ ADB client created")

    # Test 2: Get devices
    print("\n2. Testing device detection...")
    devices = client.get_devices()
    print(f"   ✓ Found {len(devices)} device(s)")
    if devices:
        print(f"   Devices: {devices}")
    else:
        print(f"   ⚠ No devices connected (this is OK for testing)")

    # Test 3: Security validation - Safe command
    print("\n3. Testing security validation (safe command)...")
    allowed, risk, reason = SecurityValidator.validate_command("ls -la")
    print(f"   Command: 'ls -la'")
    print(f"   Allowed: {allowed}")
    print(f"   Risk: {risk.value}")
    print(f"   Reason: {reason}")
    assert allowed, "Safe command should be allowed"
    assert risk == RiskLevel.SAFE, "ls should be safe"

    # Test 4: Security validation - Critical risk command
    print("\n4. Testing security validation (critical risk command)...")
    allowed, risk, reason = SecurityValidator.validate_command("rm -rf /")
    print(f"   Command: 'rm -rf /'")
    print(f"   Allowed: {allowed}")
    print(f"   Risk: {risk.value}")
    print(f"   Reason: {reason}")
    assert allowed, "Commands should be allowed (with warning)"
    assert risk == RiskLevel.CRITICAL, "Should be critical risk"

    # Test 5: Security validation - High risk
    print("\n5. Testing security validation (high risk)...")
    allowed, risk, reason = SecurityValidator.validate_command("pm uninstall com.example.app")
    print(f"   Command: 'pm uninstall com.example.app'")
    print(f"   Allowed: {allowed}")
    print(f"   Risk: {risk.value}")
    print(f"   Reason: {reason}")
    assert allowed, "Uninstall should be allowed"
    assert risk == RiskLevel.HIGH, "Should be high risk"

    # Test 6: Security validation - Medium risk
    print("\n6. Testing security validation (medium risk)...")
    allowed, risk, reason = SecurityValidator.validate_command("pm install app.apk")
    print(f"   Command: 'pm install app.apk'")
    print(f"   Allowed: {allowed}")
    print(f"   Risk: {risk.value}")
    print(f"   Reason: {reason}")
    assert allowed, "Install should be allowed"
    assert risk == RiskLevel.MEDIUM, "Should be medium risk"

    # Test 7: Path validation - Safe path
    print("\n7. Testing path validation (safe path)...")
    allowed, risk, reason = SecurityValidator.validate_path("/sdcard/Download/file.txt")
    print(f"   Path: '/sdcard/Download/file.txt'")
    print(f"   Allowed: {allowed}")
    print(f"   Risk: {risk.value}")
    print(f"   Reason: {reason}")
    assert allowed, "Safe path should be allowed"
    assert risk == RiskLevel.SAFE, "Should be safe risk"

    # Test 8: Path validation - System path (high risk)
    print("\n8. Testing path validation (system path)...")
    allowed, risk, reason = SecurityValidator.validate_path("/system/bin/su")
    print(f"   Path: '/system/bin/su'")
    print(f"   Allowed: {allowed}")
    print(f"   Risk: {risk.value}")
    print(f"   Reason: {reason}")
    assert allowed, "System path should be allowed (with warning)"
    assert risk == RiskLevel.HIGH, "Should be high risk"

    # Test 9: Device Manager
    print("\n9. Testing device manager...")
    manager = DeviceManager()
    print(f"   ✓ Device manager created")

    # Test 10: Scan devices
    print("\n10. Testing device scanning...")
    found_devices = manager.scan_devices()
    print(f"   ✓ Scanned devices: {len(found_devices)}")
    if found_devices:
        print(f"   Devices: {found_devices}")
        default = manager.get_default_device()
        print(f"   Default device: {default}")
    else:
        print(f"   ⚠ No devices connected")

    # Test 11: Get device client
    print("\n11. Testing device client retrieval...")
    if found_devices:
        device_client = manager.get_device(found_devices[0])
        assert device_client is not None, "Should get device client"
        print(f"   ✓ Got client for device: {found_devices[0]}")
    else:
        print(f"   ⚠ Skipped (no devices)")

    print("\n" + "=" * 60)
    print("\n✅ Checkpoint 2.2 PASSED - Android infrastructure working!")
    print("\nInfrastructure components:")
    print(f"  ✓ ADB client wrapper")
    print(f"  ✓ Command security validation")
    print(f"  ✓ Path security validation")
    print(f"  ✓ Device connection manager")
    print(f"  ✓ Risk level assessment")
    return True


if __name__ == "__main__":
    try:
        test_adb_infrastructure()
    except Exception as e:
        print(f"\n❌ Checkpoint 2.2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
