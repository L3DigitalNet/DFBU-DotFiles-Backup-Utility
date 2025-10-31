#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DFBU Non-Dry-Run Test Script

Description:
    Test script to verify DFBU functionality with actual file operations.
    Uses a safe test configuration and limited file set to validate that
    the backup process works correctly without dry-run mode.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-28-2025
License: MIT
"""

import subprocess
import sys
from pathlib import Path


def test_dfbu_actual_operations():
    """
    Test DFBU with actual file operations enabled.

    Returns:
        bool: True if test successful, False otherwise
    """
    print("🧪 Testing DFBU with DRY_RUN=False...")
    print("=" * 50)

    # Verify test config exists
    test_config = Path(__file__).parent / "data" / "dfbu-config-test.toml"
    if not test_config.exists():
        print(f"❌ Test config not found: {test_config}")
        return False

    # Clear any existing test backup directory
    test_backup_dir = Path("/tmp/dfbu_test_backup")
    if test_backup_dir.exists():
        print(f"🧹 Cleaning existing test backup directory: {test_backup_dir}")
        import shutil

        shutil.rmtree(test_backup_dir)

    print(f"📁 Test backup destination: {test_backup_dir}")
    print("📋 Test configuration: Limited to 3 dotfiles")
    print("⚠️  WARNING: This will perform actual file operations!")

    # Run DFBU with automatic input
    try:
        # Create input for the program: choose backup mode (1), then confirm (y)
        input_data = "1\ny\n"

        result = subprocess.run(
            [sys.executable, "dfbu.py"],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=30,
        )

        print("\n" + "=" * 50)
        print("📤 DFBU OUTPUT:")
        print("-" * 50)
        print(result.stdout)

        if result.stderr:
            print("🚨 STDERR:")
            print(result.stderr)

        print("-" * 50)
        print(f"🔍 Exit code: {result.returncode}")

        # Check if backup directory was created and contains files
        if test_backup_dir.exists():
            print(f"✅ Backup directory created: {test_backup_dir}")

            # List contents
            backup_files = list(test_backup_dir.rglob("*"))
            print(f"📁 Backup contains {len(backup_files)} items:")
            for file in backup_files:
                if file.is_file():
                    print(f"   📄 {file.relative_to(test_backup_dir)}")
                elif file.is_dir():
                    print(f"   📁 {file.relative_to(test_backup_dir)}/")

            return len(backup_files) > 0
        else:
            print("❌ Backup directory was not created")
            return False

    except subprocess.TimeoutExpired:
        print("⏰ Test timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False


def cleanup_test_files():
    """Clean up test files and directories."""
    test_backup_dir = Path("/tmp/dfbu_test_backup")
    if test_backup_dir.exists():
        print(f"🧹 Cleaning up test backup directory: {test_backup_dir}")
        import shutil

        shutil.rmtree(test_backup_dir)

    test_archive_dir = Path("/tmp/dfbu_test_archive")
    if test_archive_dir.exists():
        print(f"🧹 Cleaning up test archive directory: {test_archive_dir}")
        import shutil

        shutil.rmtree(test_archive_dir)


if __name__ == "__main__":
    try:
        success = test_dfbu_actual_operations()

        print("\n" + "=" * 50)
        if success:
            print("✅ DFBU actual operation test PASSED!")
            print("🎉 File operations working correctly")
        else:
            print("❌ DFBU actual operation test FAILED!")
            print("🚨 File operations may have issues")

        print("\n🧹 Cleaning up test files...")
        cleanup_test_files()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        cleanup_test_files()
        sys.exit(1)
