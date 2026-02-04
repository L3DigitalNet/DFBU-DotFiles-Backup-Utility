"""Tests for the RecoveryDialog component."""

import pytest
from PySide6.QtWidgets import QApplication, QDialog

from core.common_types import OperationResultDict
from gui.recovery_dialog import RecoveryDialog


@pytest.fixture
def sample_operation_result() -> OperationResultDict:
    """Sample OperationResultDict with mixed results."""
    return {
        "status": "partial",
        "operation_type": "mirror_backup",
        "total_items": 5,
        "completed": [
            {"path": "/home/.bashrc", "dest_path": "/backup/.bashrc", "status": "success",
             "error_type": None, "error_message": "", "can_retry": False},
            {"path": "/home/.profile", "dest_path": "/backup/.profile", "status": "success",
             "error_type": None, "error_message": "", "can_retry": False},
        ],
        "failed": [
            {"path": "/home/.vimrc", "dest_path": "/backup/.vimrc", "status": "failed",
             "error_type": "permission", "error_message": "Permission denied", "can_retry": True},
            {"path": "/home/.ssh/config", "dest_path": "/backup/.ssh/config", "status": "failed",
             "error_type": "not_found", "error_message": "File not found", "can_retry": False},
        ],
        "skipped": [
            {"path": "/home/.gitconfig", "dest_path": None, "status": "skipped",
             "error_type": None, "error_message": "No changes detected", "can_retry": False},
        ],
        "warnings": [],
        "can_retry": ["/home/.vimrc"],
        "timestamp": "2026-02-01T10:00:00+00:00",
    }


class TestRecoveryDialogInit:
    """Tests for RecoveryDialog initialization."""

    @pytest.mark.gui
    def test_dialog_loads_ui(self, qapp, sample_operation_result):
        """Dialog loads UI file and finds widgets."""
        dialog = RecoveryDialog(sample_operation_result)
        assert dialog is not None
        assert dialog.windowTitle() == "Operation Interrupted"

    @pytest.mark.gui
    def test_dialog_displays_success_count(self, qapp, sample_operation_result):
        """Dialog shows correct success count."""
        dialog = RecoveryDialog(sample_operation_result)
        assert "2 files backed up successfully" in dialog.success_count_label.text()

    @pytest.mark.gui
    def test_dialog_displays_failed_count(self, qapp, sample_operation_result):
        """Dialog shows correct failed count."""
        dialog = RecoveryDialog(sample_operation_result)
        assert "2 files failed" in dialog.failed_count_label.text()

    @pytest.mark.gui
    def test_dialog_populates_failed_items_tree(self, qapp, sample_operation_result):
        """Dialog populates tree with failed items."""
        dialog = RecoveryDialog(sample_operation_result)
        tree = dialog.failed_items_tree
        assert tree.topLevelItemCount() == 2

    @pytest.mark.gui
    def test_retry_button_disabled_when_no_retryable(self, qapp):
        """Retry button disabled when no items can be retried."""
        result: OperationResultDict = {
            "status": "failed",
            "operation_type": "mirror_backup",
            "total_items": 1,
            "completed": [],
            "failed": [
                {"path": "/home/.vimrc", "dest_path": "/backup/.vimrc", "status": "failed",
                 "error_type": "not_found", "error_message": "File not found", "can_retry": False},
            ],
            "skipped": [],
            "warnings": [],
            "can_retry": [],
            "timestamp": "2026-02-01T10:00:00+00:00",
        }
        dialog = RecoveryDialog(result)
        assert not dialog.retry_failed_btn.isEnabled()


class TestRecoveryDialogActions:
    """Tests for RecoveryDialog button actions."""

    @pytest.mark.gui
    def test_retry_returns_retry_action(self, qapp, sample_operation_result):
        """Clicking Retry Failed returns 'retry' action."""
        dialog = RecoveryDialog(sample_operation_result)
        dialog.retry_failed_btn.click()
        assert dialog.action == "retry"
        assert dialog.result() == QDialog.DialogCode.Accepted

    @pytest.mark.gui
    def test_continue_returns_continue_action(self, qapp, sample_operation_result):
        """Clicking Skip & Continue returns 'continue' action."""
        dialog = RecoveryDialog(sample_operation_result)
        dialog.continue_btn.click()
        assert dialog.action == "continue"
        assert dialog.result() == QDialog.DialogCode.Accepted

    @pytest.mark.gui
    def test_abort_returns_abort_action(self, qapp, sample_operation_result):
        """Clicking Abort returns 'abort' action."""
        dialog = RecoveryDialog(sample_operation_result)
        dialog.abort_btn.click()
        assert dialog.action == "abort"
        assert dialog.result() == QDialog.DialogCode.Rejected

    @pytest.mark.gui
    def test_get_retryable_paths(self, qapp, sample_operation_result):
        """get_retryable_paths returns correct paths."""
        dialog = RecoveryDialog(sample_operation_result)
        paths = dialog.get_retryable_paths()
        assert paths == ["/home/.vimrc"]
