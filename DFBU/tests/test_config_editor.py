"""
Tests for Edit Config and Validate Config buttons on the backup tab.

Tests verify button existence in the UI and config validation logic
in the ViewModel layer.
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QPushButton


@pytest.mark.gui
def test_edit_config_button_exists(qapp, qtbot):
    """Backup tab should have an 'Edit Config' button."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    btn = window.findChild(QPushButton, "editConfigButton")
    assert btn is not None


@pytest.mark.gui
def test_validate_config_button_exists(qapp, qtbot):
    """Backup tab should have a 'Validate Config' button."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    btn = window.findChild(QPushButton, "validateConfigButton")
    assert btn is not None


@pytest.mark.unit
def test_validate_config_returns_success_for_valid_config():
    """Validation should return success for a well-formed config."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)

    success, message = vm.command_validate_config()
    assert success is True
    assert "valid" in message.lower() or "no errors" in message.lower()


@pytest.mark.unit
def test_validate_config_returns_error_for_bad_yaml(tmp_path):
    """Validation should return failure for malformed YAML."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    # Create a bad dotfiles.yaml
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "dotfiles.yaml").write_text("{{invalid yaml: [", encoding="utf-8")
    (config_dir / "settings.yaml").write_text(
        "paths:\n  mirror_dir: ~/m\n  archive_dir: ~/a\n  restore_backup_dir: ~/r\n"
        "options:\n  mirror: true\n  archive: false\n  hostname_subdir: true\n"
        "  date_subdir: false\n  archive_format: tar.gz\n  archive_compression_level: 9\n"
        "  rotate_archives: false\n  max_archives: 5\n  pre_restore_backup: true\n"
        "  max_restore_backups: 5\n",
        encoding="utf-8",
    )
    (config_dir / "session.yaml").write_text("excluded: []\n", encoding="utf-8")

    model = DFBUModel(config_dir)
    vm = DFBUViewModel(model)

    success, message = vm.command_validate_config()
    assert success is False
