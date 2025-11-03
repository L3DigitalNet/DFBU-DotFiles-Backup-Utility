#!/usr/bin/env python3
"""
Final integration test: Verify Force Full Backup actually copies all files.

This test creates temporary test files and verifies that:
1. Smart backup (default) skips unchanged files
2. Force full backup copies all files regardless of changes
"""

import sys
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "DFBU"))
sys.path.insert(0, str(Path(__file__).parent / "DFBU" / "gui"))

from PySide6.QtCore import QCoreApplication

from gui.model import DFBUModel
from gui.viewmodel import BackupWorker


def test_force_full_backup_behavior():
    """Test that force full backup actually copies all files."""
    print("\n" + "=" * 70)
    print("FINAL INTEGRATION TEST: Force Full Backup Behavior")
    print("=" * 70)

    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create source files
        source_dir = temp_path / "source"
        source_dir.mkdir()

        test_files = [
            source_dir / "file1.txt",
            source_dir / "file2.txt",
            source_dir / "file3.txt",
        ]

        for f in test_files:
            f.write_text("test content")

        # Create mirror directory
        mirror_dir = temp_path / "mirror"
        mirror_dir.mkdir()

        # Create config directory structure
        config_dir = temp_path / "config"
        config_dir.mkdir()
        data_dir = config_dir / "data"
        data_dir.mkdir()

        # Create temporary config file
        config_file = data_dir / "test-config.toml"
        config_content = f"""
[paths]
mirror_dir = "{mirror_dir}"
archive_dir = "{temp_path / "archive"}"

[options]
mirror = true
archive = false
hostname_subdir = false
date_subdir = false

[[dotfile]]
category = "Test"
subcategory = "Test"
application = "Test"
description = "Test files"
paths = ["{source_dir / "file1.txt"}", "{source_dir / "file2.txt"}", "{source_dir / "file3.txt"}"]
enabled = true
"""
        config_file.write_text(config_content)

        print("\n📁 Created test environment:")
        print(f"  Source: {source_dir}")
        print(f"  Mirror: {mirror_dir}")
        print(f"  Config: {config_file}")

        # Load model and do first backup
        model = DFBUModel(config_file)
        success, error = model.load_config()
        assert success, f"Failed to load config: {error}"

        print("\n🔧 Test 1: First Backup (Smart Mode)")
        print("-" * 70)

        worker1 = BackupWorker()
        worker1.set_model(model)
        worker1.set_modes(mirror=True, archive=False)
        worker1.set_force_full_backup(False)

        processed1 = []
        skipped1 = []

        worker1.item_processed.connect(lambda src, dst: processed1.append(src))
        worker1.item_skipped.connect(lambda path, reason: skipped1.append(path))

        worker1.run()

        print("✓ First backup completed:")
        print(f"  - Files copied: {len(processed1)}")
        print(f"  - Files skipped: {len(skipped1)}")

        assert len(processed1) == 3, f"Expected 3 files copied, got {len(processed1)}"
        assert len(skipped1) == 0, f"Expected 0 files skipped, got {len(skipped1)}"

        print("\n🔧 Test 2: Second Backup (Smart Mode - should skip all)")
        print("-" * 70)

        # Reset statistics
        model.reset_statistics()

        worker2 = BackupWorker()
        worker2.set_model(model)
        worker2.set_modes(mirror=True, archive=False)
        worker2.set_force_full_backup(False)

        processed2 = []
        skipped2 = []

        worker2.item_processed.connect(lambda src, dst: processed2.append(src))
        worker2.item_skipped.connect(lambda path, reason: skipped2.append(path))

        worker2.run()

        print("✓ Second backup completed:")
        print(f"  - Files copied: {len(processed2)}")
        print(f"  - Files skipped: {len(skipped2)}")

        assert len(processed2) == 0, (
            f"Expected 0 files copied (all unchanged), got {len(processed2)}"
        )
        assert len(skipped2) == 3, f"Expected 3 files skipped, got {len(skipped2)}"

        print("\n🔧 Test 3: Third Backup (Force Full - should copy all)")
        print("-" * 70)

        # Reset statistics
        model.reset_statistics()

        worker3 = BackupWorker()
        worker3.set_model(model)
        worker3.set_modes(mirror=True, archive=False)
        worker3.set_force_full_backup(True)  # FORCE FULL BACKUP

        processed3 = []
        skipped3 = []

        worker3.item_processed.connect(lambda src, dst: processed3.append(src))
        worker3.item_skipped.connect(lambda path, reason: skipped3.append(path))

        worker3.run()

        print("✓ Third backup (force full) completed:")
        print(f"  - Files copied: {len(processed3)}")
        print(f"  - Files skipped: {len(skipped3)}")

        assert len(processed3) == 3, (
            f"Expected 3 files copied (force full), got {len(processed3)}"
        )
        assert len(skipped3) == 0, (
            f"Expected 0 files skipped (force full), got {len(skipped3)}"
        )

        print("\n" + "=" * 70)
        print("✅ FORCE FULL BACKUP WORKS CORRECTLY!")
        print("=" * 70)
        print("\nVerified behavior:")
        print("✓ Smart backup (default): Skips unchanged files after first backup")
        print("✓ Force full backup: Copies all files even if unchanged")
        print("✓ User has complete control over backup thoroughness")

        return 0


if __name__ == "__main__":
    app = QCoreApplication(sys.argv)
    try:
        exit_code = test_force_full_backup_behavior()
        sys.exit(exit_code)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
