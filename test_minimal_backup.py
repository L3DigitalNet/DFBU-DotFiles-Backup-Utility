#!/usr/bin/env python3
"""Minimal backup test to trace file copy issue."""

import sys
from pathlib import Path


# Add DFBU directory to path
sys.path.insert(0, str(Path(__file__).parent / "DFBU"))
sys.path.insert(0, str(Path(__file__).parent / "DFBU" / "gui"))

from PySide6.QtCore import QCoreApplication

from gui.model import DFBUModel
from gui.viewmodel import BackupWorker


def test_minimal_backup():
    """Test minimal backup operation."""
    app = QCoreApplication(sys.argv)

    config_path = Path(__file__).parent / "DFBU" / "data" / "dfbu-config.toml"

    print("\n=== Loading Config ===")
    model = DFBUModel(config_path)
    success, error = model.load_config()
    print(f"Load result: success={success}")

    if not success:
        print(f"Failed to load config: {error}")
        return

    print(f"Dotfiles count: {model.get_dotfile_count()}")
    print(f"Mirror dir: {model.mirror_base_dir}")
    print(f"Mirror mode: {model.options['mirror']}")

    # Validate paths
    validation_results = model.validate_dotfile_paths()
    total_items = len([v for v in validation_results.values() if v[0]])
    print(f"Total items that exist: {total_items}")

    if total_items == 0:
        print("No items to backup!")
        return

    print("\n=== Creating Backup Worker ===")
    worker = BackupWorker()
    worker.set_model(model)
    worker.set_modes(mirror=True, archive=False)  # Only mirror mode

    # Connect signals for debugging
    worker.progress_updated.connect(lambda p: print(f"Progress: {p}%"))
    worker.item_processed.connect(lambda src, dst: print(f"Processed: {src} -> {dst}"))
    worker.item_skipped.connect(
        lambda path, reason: print(f"Skipped: {path} ({reason})")
    )
    worker.error_occurred.connect(lambda ctx, msg: print(f"Error [{ctx}]: {msg}"))
    worker.backup_finished.connect(lambda: print("Backup finished!"))

    print("\n=== Running Backup ===")
    worker.run()  # Run directly (not in thread) for synchronous debugging

    print("\n=== Backup Complete ===")
    print(f"Statistics: {model.statistics}")


if __name__ == "__main__":
    test_minimal_backup()
