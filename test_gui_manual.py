#!/usr/bin/env python3
"""
Minimal GUI test to verify log updates work
"""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent / "DFBU" / "gui"))

from model import DFBUModel
from PySide6.QtWidgets import QApplication
from view import MainWindow
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
    # Create the actual View
    window = MainWindow(viewmodel, "0.5.6-test")
    window.show()

    print("\nGUI is now running - click the backup button!")
    print("Watch the operation log for updates...")

    # Run the application
    sys.exit(app.exec())
