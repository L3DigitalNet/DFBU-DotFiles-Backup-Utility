#!/usr/bin/env python3
"""
Test to verify signals are being emitted correctly
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "DFBU" / "gui"))

from model import DFBUModel
from PySide6.QtWidgets import QApplication
from viewmodel import DFBUViewModel


# Create Qt application
app = QApplication(sys.argv)

# Test with default config
config_path = Path(__file__).parent / "DFBU" / "data" / "dfbu-config.toml"
print(f"Testing with config: {config_path}")

model = DFBUModel(config_path)
viewmodel = DFBUViewModel(model)

# Load config
success, error = model.load_config()
print(f"Load config result: success={success}")

if success:
    print(f"Dotfile count: {model.get_dotfile_count()}")

    # Connect signals
    signal_count = {
        "progress": 0,
        "processed": 0,
        "skipped": 0,
        "finished": 0,
        "error": 0,
    }

    def on_progress(value):
        signal_count["progress"] += 1
        if signal_count["progress"] <= 5 or signal_count["progress"] % 10 == 0:
            print(f"Progress signal #{signal_count['progress']}: {value}%")

    def on_item_processed(src, dest):
        signal_count["processed"] += 1
        if signal_count["processed"] <= 5:
            print(f"Processed signal #{signal_count['processed']}: {src[:50]}...")

    def on_item_skipped(path, reason):
        signal_count["skipped"] += 1
        if signal_count["skipped"] <= 5:
            print(
                f"Skipped signal #{signal_count['skipped']}: {path[:50]}... ({reason})"
            )

    def on_finished(summary):
        signal_count["finished"] += 1
        print(f"\nFinished signal #{signal_count['finished']}")
        print(f"Summary: {summary[:200]}...")
        print("\nTotal signals emitted:")
        print(f"  Progress: {signal_count['progress']}")
        print(f"  Processed: {signal_count['processed']}")
        print(f"  Skipped: {signal_count['skipped']}")
        print(f"  Finished: {signal_count['finished']}")
        print(f"  Errors: {signal_count['error']}")
        app.quit()

    def on_error(context, message):
        signal_count["error"] += 1
        print(f"Error signal #{signal_count['error']}: {context} - {message}")

    # Connect ViewModel signals (NOT worker signals)
    viewmodel.progress_updated.connect(on_progress)
    viewmodel.item_processed.connect(on_item_processed)
    viewmodel.item_skipped.connect(on_item_skipped)
    viewmodel.operation_finished.connect(on_finished)
    viewmodel.error_occurred.connect(on_error)

    print("\nStarting backup via ViewModel command...")
    success = viewmodel.command_start_backup()
    print(f"Command returned: {success}")

    if success:
        # Set a timeout
        from PySide6.QtCore import QTimer

        timeout = QTimer()
        timeout.setSingleShot(True)
        timeout.timeout.connect(lambda: (print("\nTimeout - quitting"), app.quit()))
        timeout.start(15000)  # 15 second timeout

        # Run Qt event loop
        sys.exit(app.exec())
    else:
        print("Failed to start backup!")
