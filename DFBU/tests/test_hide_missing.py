"""
Tests for the 'Hide missing' checkbox feature.

Verifies that the backup tab includes a 'Hide missing' checkbox
that filters out dotfiles whose paths don't exist on the system.
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QCheckBox


@pytest.mark.gui
def test_hide_missing_checkbox_exists(qapp, qtbot):
    """Backup tab should have a 'Hide missing' checkbox."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    checkbox = window.findChild(QCheckBox, "hideMissingCheckbox")
    assert checkbox is not None
    assert checkbox.text() == "Hide missing"


@pytest.mark.gui
def test_hide_missing_hides_nonexistent_rows(qapp, qtbot):
    """When 'Hide missing' is checked, rows with status '✗' should be hidden."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    # Load config and wait for table to populate
    vm.command_load_config()
    qtbot.waitUntil(lambda: window.dotfile_table.rowCount() > 0, timeout=5000)

    total_rows = window.dotfile_table.rowCount()

    # Count rows with missing status (column 1 = "✗")
    missing_count = 0
    for row in range(total_rows):
        status_item = window.dotfile_table.item(row, 1)
        if status_item and status_item.text() == "\u2717":
            missing_count += 1

    # Check the hide missing checkbox
    checkbox = window.findChild(QCheckBox, "hideMissingCheckbox")
    assert checkbox is not None, "hideMissingCheckbox not found"
    checkbox.setChecked(True)

    # Count visible rows
    visible_count = sum(
        1 for row in range(total_rows) if not window.dotfile_table.isRowHidden(row)
    )

    assert visible_count == total_rows - missing_count
