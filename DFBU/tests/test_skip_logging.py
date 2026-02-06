"""
Tests for Skip Logging Behavior

Description:
    Verifies that skipped (unchanged) files are logged individually by name
    rather than in batch summaries. Each skipped file should appear as its
    own log entry showing the filename and reason.

Author: Chris Purcell
Date Created: 02-06-2026
License: MIT
"""

from pathlib import Path

import pytest


@pytest.mark.gui
def test_skipped_file_name_appears_in_log(qapp, qtbot):
    """Each skipped file should have its name logged individually."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    # Simulate skipping a single file
    window._on_item_skipped("/home/user/.bashrc", "File unchanged")

    log_text = window.operation_log.toPlainText()
    assert ".bashrc" in log_text
    assert "unchanged" in log_text.lower()


@pytest.mark.gui
def test_skipped_files_logged_individually(qapp, qtbot):
    """Multiple skipped files should each appear as separate log entries."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    # Simulate skipping 3 files
    window._on_item_skipped("/home/user/.bashrc", "File unchanged")
    window._on_item_skipped("/home/user/.vimrc", "File unchanged")
    window._on_item_skipped("/home/user/.gitconfig", "File unchanged")

    log_text = window.operation_log.toPlainText()
    assert ".bashrc" in log_text
    assert ".vimrc" in log_text
    assert ".gitconfig" in log_text


@pytest.mark.gui
def test_skipped_count_increments(qapp, qtbot):
    """The _skipped_count attribute should increment for each skipped file."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    assert window._skipped_count == 0

    window._on_item_skipped("/home/user/.bashrc", "File unchanged")
    assert window._skipped_count == 1

    window._on_item_skipped("/home/user/.vimrc", "File unchanged")
    assert window._skipped_count == 2


@pytest.mark.gui
def test_verbose_mode_shows_full_path(qapp, qtbot):
    """When verbose mode is on, skipped file log should include the full path."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    # Enable verbose mode
    if window._log_verbose_btn:
        window._log_verbose_btn.setChecked(True)

    window._on_item_skipped("/home/user/.bashrc", "File unchanged")

    log_text = window.operation_log.toPlainText()
    assert "/home/user/.bashrc" in log_text
