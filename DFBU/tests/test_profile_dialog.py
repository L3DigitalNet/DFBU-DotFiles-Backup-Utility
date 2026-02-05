"""Tests for ProfileDialog view component."""

import sys
from pathlib import Path

# Add DFBU directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from gui.model import DFBUModel
from gui.viewmodel import DFBUViewModel
from gui.profile_dialog import ProfileDialog


@pytest.mark.gui
def test_profile_dialog_displays_profiles(
    qapp: QApplication, qtbot: Any, yaml_config_dir: Path
) -> None:
    """ProfileDialog should display existing profiles."""
    model = DFBUModel(yaml_config_dir)
    model.load_config()
    model.create_profile("TestProfile", "Test description", [])
    vm = DFBUViewModel(model)

    dialog = ProfileDialog(vm)
    qtbot.addWidget(dialog)

    # Check profile appears in list
    assert dialog.profile_list.count() == 1
    assert dialog.profile_list.item(0).text() == "TestProfile"
