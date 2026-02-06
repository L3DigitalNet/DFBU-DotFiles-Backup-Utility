"""
Tests for the verbose log mode feature.

Verifies that the log pane includes a 'Verbose' toggle button
that controls whether full destination paths are shown in log entries.
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QPushButton


@pytest.mark.gui
def test_verbose_button_exists(qapp, qtbot):
    """Log pane should have a 'Verbose' toggle button."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    btn = window.findChild(QPushButton, "logPaneVerboseButton")
    assert btn is not None
    assert btn.isCheckable()


@pytest.mark.gui
def test_verbose_mode_shows_full_path(qapp, qtbot):
    """In verbose mode, processed items should show full destination path."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    # Enable verbose mode
    verbose_btn = window.findChild(QPushButton, "logPaneVerboseButton")
    assert verbose_btn is not None
    verbose_btn.setChecked(True)

    # Simulate an item processed signal
    window._on_item_processed(
        "/home/user/.bashrc", "/home/user/backups/mirror/host/.bashrc"
    )

    log_text = window.operation_log.toPlainText()
    assert "/home/user/backups/mirror/host/.bashrc" in log_text


@pytest.mark.gui
def test_non_verbose_mode_shows_names_only(qapp, qtbot):
    """In non-verbose mode, processed items should show filenames only."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    # Ensure verbose is off
    verbose_btn = window.findChild(QPushButton, "logPaneVerboseButton")
    assert verbose_btn is not None
    verbose_btn.setChecked(False)

    # Simulate an item processed signal
    window._on_item_processed(
        "/home/user/.bashrc", "/home/user/backups/mirror/host/.bashrc"
    )

    log_text = window.operation_log.toPlainText()
    assert ".bashrc" in log_text
    # Full path should NOT appear in non-verbose mode
    assert "/home/user/backups/mirror/host/.bashrc" not in log_text
