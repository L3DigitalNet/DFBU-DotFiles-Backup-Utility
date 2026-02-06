from pathlib import Path

import pytest
from PySide6.QtWidgets import QPushButton


@pytest.mark.gui
def test_update_button_labeled_edit(qapp, qtbot):
    """The backup tab's update button should be labeled 'Edit', not 'Update'."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    btn = window.findChild(QPushButton, "fileGroupUpdateFileButton")
    assert btn is not None
    assert btn.text() == "Edit"
