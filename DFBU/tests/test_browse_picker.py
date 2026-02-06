"""
Tests for unified browse picker in AddDotfileDialog.

Verifies that the browse button opens a unified file/directory picker
instead of showing a 'File or Directory?' type prompt.
"""

import pytest
from PySide6.QtWidgets import QFileDialog, QMessageBox


@pytest.mark.gui
def test_browse_does_not_show_type_prompt(qapp, qtbot, monkeypatch):
    """Browse should NOT show a 'File or Directory?' message box."""
    from gui.view import AddDotfileDialog

    dialog = AddDotfileDialog(None)

    # Track if the old QMessageBox type prompt is shown
    message_box_shown: list[bool] = []

    original_exec = QMessageBox.exec

    def tracking_exec(self_mb: QMessageBox) -> int:
        if self_mb.windowTitle() == "Select Type":
            message_box_shown.append(True)
        return original_exec(self_mb)

    monkeypatch.setattr(QMessageBox, "exec", tracking_exec)

    # Mock QFileDialog.exec to return Rejected (cancelled) so we don't block
    monkeypatch.setattr(
        QFileDialog, "exec", lambda self: QFileDialog.DialogCode.Rejected
    )

    dialog._on_browse_path()

    assert not message_box_shown, "Browse should not show File/Directory type prompt"
