#!/usr/bin/env python3
"""Test GUI issues: dropdown and backup functionality."""

import sys
from pathlib import Path


# Add DFBU directory to path
sys.path.insert(0, str(Path(__file__).parent / "DFBU"))
sys.path.insert(0, str(Path(__file__).parent / "DFBU" / "gui"))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from gui.model import DFBUModel
from gui.view import MainWindow
from gui.viewmodel import DFBUViewModel


def test_gui_issues():
    """Test GUI dropdown and backup issues."""
    app = QApplication(sys.argv)

    config_path = Path(__file__).parent / "DFBU" / "data" / "dfbu-config.toml"

    print("\n=== Creating MVVM Components ===")
    model = DFBUModel(config_path)
    viewmodel = DFBUViewModel(model)
    view = MainWindow(viewmodel, "0.5.6")

    print("[DEBUG] Loading configuration...")
    success, error = model.load_config()
    print(f"[DEBUG] Load result: success={success}, error='{error}'")
    print(f"[DEBUG] Dotfiles count: {model.get_dotfile_count()}")

    # Test dropdown data
    print("\n=== Testing Dropdown Data ===")
    categories = viewmodel.get_unique_categories()
    subcategories = viewmodel.get_unique_subcategories()
    print(f"[DEBUG] Categories available: {len(categories)}")
    print(f"[DEBUG] Subcategories available: {len(subcategories)}")
    if categories:
        print(f"[DEBUG] First 5 categories: {categories[:5]}")
    if subcategories:
        print(f"[DEBUG] First 5 subcategories: {subcategories[:5]}")

    # Test backup preparation
    print("\n=== Testing Backup Preparation ===")
    validation_results = model.validate_dotfile_paths()
    total_items = len([v for v in validation_results.values() if v[0]])
    print(f"[DEBUG] Total items that exist: {total_items}")

    if total_items > 0:
        print(f"[DEBUG] Mirror dir: {model.mirror_base_dir}")
        print(f"[DEBUG] Mirror mode: {model.options['mirror']}")
        print(f"[DEBUG] Archive mode: {model.options['archive']}")

    # Show window briefly
    print("\n=== Showing Window ===")
    view.show()

    # Close after 2 seconds
    QTimer.singleShot(2000, app.quit)

    app.exec()
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_gui_issues()
