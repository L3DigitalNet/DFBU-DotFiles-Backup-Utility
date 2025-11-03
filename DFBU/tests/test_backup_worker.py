#!/usr/bin/env python3
"""
Test the backup worker to see what happens
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "DFBU" / "gui"))

from model import DFBUModel
from PySide6.QtCore import QCoreApplication
from viewmodel import BackupWorker


# Create Qt application
app = QCoreApplication(sys.argv)

# Test with default config
config_path = Path(__file__).parent / "DFBU" / "data" / "dfbu-config.toml"
print(f"Testing with config: {config_path}")

model = DFBUModel(config_path)

# Load config
success, error = model.load_config()
print(f"Load config result: success={success}")

if success:
    print(f"Mirror mode: {model.options['mirror']}")
    print(f"Archive mode: {model.options['archive']}")
    print(f"Dotfile count: {model.get_dotfile_count()}")

    # Create backup worker
    worker = BackupWorker()
    worker.set_model(model)
    worker.set_modes(model.options["mirror"], model.options["archive"])

    # Connect signals
    def on_progress(value):
        print(f"Progress: {value}%")

    def on_item_processed(src, dest):
        print(f"Processed: {src} -> {dest}")

    def on_item_skipped(path, reason):
        print(f"Skipped: {path} (reason: {reason})")

    def on_backup_finished():
        print("Backup finished!")
        print(f"Statistics: {model.statistics}")
        app.quit()

    def on_error(context, message):
        print(f"Error in {context}: {message}")
        app.quit()

    worker.progress_updated.connect(on_progress)
    worker.item_processed.connect(on_item_processed)
    worker.item_skipped.connect(on_item_skipped)
    worker.backup_finished.connect(on_backup_finished)
    worker.error_occurred.connect(on_error)

    print("\nStarting backup worker...")
    worker.start()

    # Set a timeout to quit if nothing happens
    from PySide6.QtCore import QTimer

    timeout = QTimer()
    timeout.setSingleShot(True)
    timeout.timeout.connect(lambda: (print("\nTimeout - quitting"), app.quit()))
    timeout.start(10000)  # 10 second timeout

    # Run Qt event loop
    sys.exit(app.exec())
