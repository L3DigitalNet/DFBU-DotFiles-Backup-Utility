#!/usr/bin/env python3
"""Debug script to test GUI dropdown and backup functionality."""

import sys
from pathlib import Path


# Add DFBU directory to path
sys.path.insert(0, str(Path(__file__).parent / "DFBU"))
sys.path.insert(0, str(Path(__file__).parent / "DFBU" / "gui"))

from PySide6.QtWidgets import QApplication

from gui.model import DFBUModel
from gui.viewmodel import DFBUViewModel


def test_dropdown_functionality():
    """Test if dropdowns work in the add dotfile dialog."""
    print("\n=== Testing Dropdown Functionality ===")

    config_path = Path(__file__).parent / "DFBU" / "data" / "dfbu-config.toml"

    # Create MVVM components
    model = DFBUModel(config_path)
    viewmodel = DFBUViewModel(model)

    # Load config
    print("[DEBUG] Loading configuration...")
    success, error = model.load_config()
    print(f"[DEBUG] Load result: success={success}, error='{error}'")

    if success:
        print(f"[DEBUG] Dotfiles loaded: {model.get_dotfile_count()} entries")

        # Get categories and subcategories for dropdown
        categories = set()
        subcategories = set()

        for i in range(model.get_dotfile_count()):
            dotfile = model.get_dotfile_by_index(i)
            if dotfile:
                cat = dotfile.get("category", "")
                subcat = dotfile.get("subcategory", "")
                print(f"[DEBUG] Dotfile {i}: category='{cat}', subcategory='{subcat}'")
                if cat:
                    categories.add(cat)
                if subcat:
                    subcategories.add(subcat)

        print(f"[DEBUG] Unique categories: {sorted(categories)}")
        print(f"[DEBUG] Unique subcategories: {sorted(subcategories)}")

    return success


def test_backup_execution():
    """Test if backup actually saves files."""
    print("\n=== Testing Backup Execution ===")

    config_path = Path(__file__).parent / "DFBU" / "data" / "dfbu-config.toml"

    # Create MVVM components
    model = DFBUModel(config_path)
    viewmodel = DFBUViewModel(model)

    # Load config
    print("[DEBUG] Loading configuration...")
    success, error = model.load_config()
    print(f"[DEBUG] Load result: success={success}, error='{error}'")

    if success:
        print(f"[DEBUG] Mirror dir: {model.mirror_base_dir}")
        print(f"[DEBUG] Archive dir: {model.archive_base_dir}")
        print(f"[DEBUG] Mirror mode: {model.options['mirror']}")
        print(f"[DEBUG] Archive mode: {model.options['archive']}")

        # Check if mirror directory exists or needs creation
        mirror_dir = model.expand_path(str(model.mirror_base_dir))
        print(f"[DEBUG] Expanded mirror dir: {mirror_dir}")
        print(f"[DEBUG] Mirror dir exists: {mirror_dir.exists()}")

        # Validate dotfile paths
        print("[DEBUG] Validating dotfile paths...")
        validation_results = model.validate_dotfile_paths()

        for idx, (exists, is_dir, type_str) in validation_results.items():
            dotfile = model.get_dotfile_by_index(idx)
            if dotfile:
                paths = dotfile.get("paths", [])
                enabled = dotfile.get("enabled", True)
                print(
                    f"[DEBUG] Dotfile {idx}: paths={paths}, exists={exists}, is_dir={is_dir}, enabled={enabled}"
                )

        # Count items that would be backed up
        total_items = len([v for v in validation_results.values() if v[0]])
        print(f"[DEBUG] Total items to backup: {total_items}")

        if total_items == 0:
            print("[ERROR] No items found to backup!")
        else:
            print("[DEBUG] Backup would process items - ready to execute")

    return success


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Test 1: Dropdown functionality
    test_dropdown_functionality()

    # Test 2: Backup execution
    test_backup_execution()

    print("\n=== Debug Testing Complete ===")
    sys.exit(0)
