#!/usr/bin/env python3
"""
Validate UI File Completeness

Description:
    Validates that the generated .ui file contains all widgets referenced
    in the view.py Python code. Ensures completeness and correctness of
    the Qt Designer UI file.

Author: Chris Purcell
Email: chris@l3digital.net
Date Created: 11-01-2025
License: MIT
"""

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def extract_widget_names_from_python(file_path: Path) -> set[str]:
    """
    Extract all widget names from Python view code.

    Args:
        file_path: Path to view.py file

    Returns:
        Set of widget names found in the code
    """
    widget_names = set()
    content = file_path.read_text()

    # Pattern 1: self.widget_name = QWidget...
    pattern1 = r"self\.(\w+)\s*=\s*Q\w+"
    widget_names.update(re.findall(pattern1, content))

    # Pattern 2: self.widget_name in assignments (without Q prefix)
    pattern2 = r"self\.(\w+)\s*=.*(?:QWidget|QLabel|QPushButton|QLineEdit|QTextEdit|QCheckBox|QSpinBox|QTableWidget|QTabWidget|QProgressBar|QStatusBar|QGroupBox)"
    widget_names.update(re.findall(pattern2, content))

    # Remove common non-widget attributes
    non_widgets = {
        "viewmodel",
        "version",
        "is_update_mode",
        "main_layout",
        "PROJECT_NAME",
        "STATUS_MESSAGE_TIMEOUT_MS",
    }
    widget_names -= non_widgets

    # Remove AddDotfileDialog widgets (separate dialog, not in main window UI)
    dialog_widgets = {
        "tags_edit",
        "application_edit",
        "description_edit",
        "paths_list",
        "path_input_edit",
        "enabled_checkbox",
    }
    widget_names -= dialog_widgets

    return widget_names


def extract_widget_names_from_ui(file_path: Path) -> set[str]:
    """
    Extract all widget object names from Qt Designer .ui XML file.

    Args:
        file_path: Path to .ui file

    Returns:
        Set of widget object names found in the UI file
    """
    widget_names = set()

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Find all widgets with name attributes
        for widget in root.iter("widget"):
            name = widget.get("name")
            if name:
                widget_names.add(name)

        # Find all actions with name attributes
        for action in root.iter("action"):
            name = action.get("name")
            if name:
                widget_names.add(name)

    except ET.ParseError as e:
        print(f"ERROR: Failed to parse UI file: {e}")
        return set()

    return widget_names


def validate_ui_completeness(view_file: Path, ui_file: Path) -> bool:
    """
    Validate that UI file contains all widgets from view code.

    Args:
        view_file: Path to view.py
        ui_file: Path to .ui file

    Returns:
        True if validation passes, False otherwise
    """
    print("=" * 70)
    print("UI File Validation Report")
    print("=" * 70)
    print()

    # Extract widget names from both sources
    code_widgets = extract_widget_names_from_python(view_file)
    ui_widgets = extract_widget_names_from_ui(ui_file)

    print(f"Widgets found in Python code: {len(code_widgets)}")
    print(f"Widgets found in UI file: {len(ui_widgets)}")
    print()

    # Find mismatches
    missing_in_ui = code_widgets - ui_widgets
    extra_in_ui = ui_widgets - code_widgets

    # Report results
    if missing_in_ui:
        print("❌ VALIDATION FAILED")
        print()
        print(f"Widgets in code but MISSING in .ui file ({len(missing_in_ui)}):")
        for widget in sorted(missing_in_ui):
            print(f"  - {widget}")
        print()
    else:
        print("✅ All code widgets are present in UI file")
        print()

    if extra_in_ui:
        print(
            f"INFO: Extra widgets in .ui file not referenced in code ({len(extra_in_ui)}):"
        )
        for widget in sorted(extra_in_ui):
            print(f"  - {widget}")
        print()

    # XML validation
    print("XML Structure Validation:")
    try:
        tree = ET.parse(ui_file)
        print("  ✅ Valid XML syntax")

        root = tree.getroot()
        if root.tag == "ui" and root.get("version") == "4.0":
            print("  ✅ Qt Designer 4.0 format")
        else:
            print("  ❌ Invalid Qt Designer format")
            return False

    except ET.ParseError as e:
        print(f"  ❌ XML parse error: {e}")
        return False

    print()
    print("=" * 70)

    # Overall result
    if missing_in_ui:
        print("RESULT: VALIDATION FAILED - Missing widgets in UI file")
        return False

    print("RESULT: VALIDATION PASSED - UI file is complete")
    return True


def main() -> int:
    """Main entry point."""
    # Define file paths
    current_dir = Path(__file__).parent
    view_file = current_dir.parent / "view.py"
    ui_file = current_dir / "main_window_complete.ui"

    # Check files exist
    if not view_file.exists():
        print(f"ERROR: view.py not found at {view_file}")
        return 1

    if not ui_file.exists():
        print(f"ERROR: .ui file not found at {ui_file}")
        return 1

    # Run validation
    success = validate_ui_completeness(view_file, ui_file)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
