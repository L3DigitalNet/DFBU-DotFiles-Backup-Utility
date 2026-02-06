"""
Tests for the Export Config feature.

Tests cover:
    - Export button exists in the backup tab UI
    - Successful export of dotfiles.yaml and settings.yaml
    - Error reporting for missing source files
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QPushButton


@pytest.mark.gui
def test_export_config_button_exists(qapp, qtbot):
    """Backup tab should have an 'Export Config' button."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    btn = window.findChild(QPushButton, "exportConfigButton")
    assert btn is not None


@pytest.mark.unit
def test_export_config_copies_files(tmp_path):
    """Export should copy dotfiles.yaml and settings.yaml to the target directory."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)

    dest_dir = tmp_path / "export"
    dest_dir.mkdir()

    success, message = vm.command_export_config(dest_dir)

    assert success is True
    assert (dest_dir / "dotfiles.yaml").exists()
    assert (dest_dir / "settings.yaml").exists()


@pytest.mark.unit
def test_export_config_reports_missing_files(tmp_path):
    """Export should report errors for missing source files."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    # Create a config dir with only one file
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "dotfiles.yaml").write_text(
        "Bash:\n  description: test\n  path: ~/.bashrc\n", encoding="utf-8"
    )
    # settings.yaml is missing
    (config_dir / "session.yaml").write_text("excluded: []\n", encoding="utf-8")

    model = DFBUModel(config_dir)
    vm = DFBUViewModel(model)

    dest_dir = tmp_path / "export"
    dest_dir.mkdir()

    success, message = vm.command_export_config(dest_dir)

    assert success is False
    assert "settings.yaml" in message
