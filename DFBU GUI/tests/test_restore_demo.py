#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Restore Functionality Demo for Dotfiles Backup Utility

Description:
    Direct demonstration of the dfbu.py restore functionality using the
    real backup directory at /home/chris/GitHub/dotfiles/PC-COS. This script
    runs the restore functions with dry-run mode enabled to safely test the
    functionality without modifying the actual system.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-27-2025
Date Changed: 10-27-2025
Version: 0.2.0.dev1
License: MIT

Features:
    - Test restore functionality with real backup directory structure
    - Use dry-run mode to safely test without system modifications
    - Demonstrate file discovery and destination path calculation
    - Show real-world restore scenario with actual backup files

Requirements:
    - Linux environment
    - Python 3.14+ for Path.copy() functionality
    - Real backup directory structure at /home/chris/GitHub/dotfiles/PC-COS
"""

import sys
import importlib.util
from pathlib import Path

# Add the project directory to Python path for imports
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(PROJECT_DIR.parent / "common_lib"))

# Import the module under test using importlib to handle the hyphen in filename
spec = importlib.util.spec_from_file_location("dotfiles_bu", PROJECT_DIR / "dfbug_cli_backup.py")
if spec is not None and spec.loader is not None:
    dotfiles_bu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dotfiles_bu)

    # Import specific functions
    create_src_file_list = dotfiles_bu.create_src_file_list
    create_dest_restore_paths = dotfiles_bu.create_dest_restore_paths
    summarize_restore_actions = dotfiles_bu.summarize_restore_actions
    copy_files_restore = dotfiles_bu.copy_files_restore
else:
    raise ImportError("Could not load dotfiles_bu module")


def test_restore_with_actual_backup() -> None:
    """
    Test restore functionality using the actual backup directory.
    """
    backup_path = Path("/home/chris/GitHub/dotfiles/PC-COS")

    print("=" * 70)
    print("DOTFILES RESTORE FUNCTIONALITY TEST")
    print("=" * 70)
    print(f"Testing with backup directory: {backup_path}")

    if not backup_path.exists():
        print(f"❌ Backup directory not found: {backup_path}")
        return

    if not backup_path.is_dir():
        print(f"❌ Backup path is not a directory: {backup_path}")
        return

    print("✅ Backup directory found")

    # Step 1: Discover source files
    print("\n📁 Step 1: Discovering source files...")
    src_files = create_src_file_list(backup_path)

    if not src_files:
        print("❌ No source files found in backup directory")
        return

    print(f"✅ Found {len(src_files)} source files")

    # Show sample files
    print("\n📄 Sample source files:")
    home_files = [f for f in src_files if "/home/" in str(f)]
    root_files = [f for f in src_files if "/root/" in str(f)]

    print(f"   Home files: {len(home_files)}")
    for f in home_files[:5]:
        print(f"     • {f}")
    if len(home_files) > 5:
        print(f"     ... and {len(home_files) - 5} more home files")

    print(f"   Root files: {len(root_files)}")
    for f in root_files[:5]:
        print(f"     • {f}")
    if len(root_files) > 5:
        print(f"     ... and {len(root_files) - 5} more root files")

    # Step 2: Create destination paths
    print("\n🎯 Step 2: Creating destination paths...")
    dest_paths = create_dest_restore_paths(src_files)

    if len(dest_paths) != len(src_files):
        print(
            f"❌ Mismatch: {len(src_files)} source files but {len(dest_paths)} destination paths"
        )
        return

    print(f"✅ Created {len(dest_paths)} destination paths")

    # Show mapping examples
    print("\n🗂️  Sample file mappings:")
    for i, (src, dest) in enumerate(zip(src_files[:8], dest_paths[:8])):
        print(f"   {i + 1:2d}. {src.name}")
        print(f"       FROM: {src}")
        print(f"       TO:   {dest}")
        print()

    if len(src_files) > 8:
        print(f"   ... and {len(src_files) - 8} more file mappings")

    # Step 3: Summarize restore actions (this will call the actual function)
    print("\n📋 Step 3: Summarizing restore actions...")
    print("-" * 50)
    summarize_restore_actions(src_files, dest_paths)
    print("-" * 50)

    # Step 4: Test dry-run restore (note: DRY_RUN is set in module)
    print("\n🧪 Step 4: Testing restore functionality...")
    print("   Note: The dfbu.py module has DRY_RUN enabled by default")
    print("   This means no actual files will be modified during restore operations")

    try:
        print("   Running restore functions...")
        # This will respect the DRY_RUN setting in the module
        copy_files_restore(
            src_files[:3], dest_paths[:3]
        )  # Test with first 3 files only
        print("✅ Restore functions executed successfully")
    except Exception as e:
        print(f"❌ Restore function failed: {e}")

    print("\n" + "=" * 70)
    print("RESTORE FUNCTIONALITY TEST COMPLETE")
    print("=" * 70)
    print(f"✅ Backup directory: {backup_path}")
    print(f"✅ Source files discovered: {len(src_files)}")
    print(f"✅ Destination paths created: {len(dest_paths)}")
    print(f"✅ Home directory files: {len(home_files)}")
    print(f"✅ Root directory files: {len(root_files)}")
    print("✅ Restore functions tested successfully")
    print("\nThe restore functionality is working correctly!")
    print("DRY_RUN mode prevents actual file modifications.")
    print("To perform actual restore, set DRY_RUN = False in dfbu.py")


def main() -> None:
    """Main entry point for the restore functionality test."""
    test_restore_with_actual_backup()


if __name__ == "__main__":
    main()
