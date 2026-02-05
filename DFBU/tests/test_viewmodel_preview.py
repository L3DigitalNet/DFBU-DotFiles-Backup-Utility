"""Tests for ViewModel preview functionality."""

from pathlib import Path
from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from gui.model import DFBUModel
from gui.viewmodel import DFBUViewModel


@pytest.mark.gui
def test_viewmodel_preview_signal(
    qapp: QApplication, qtbot: Any, yaml_config_dir: Path, tmp_path: Path
) -> None:
    """ViewModel should emit preview_ready signal."""
    model = DFBUModel(yaml_config_dir)
    model.load_config()
    vm = DFBUViewModel(model)

    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Add dotfile pointing to test file
    model.add_dotfile("test", "TestApp", "Test file", [str(test_file)])

    # Test preview_ready signal
    with qtbot.waitSignal(vm.preview_ready, timeout=5000):
        vm.command_generate_preview()
