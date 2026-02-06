"""
Integration tests for recovery dialog flow.

Tests verify that the ViewModel correctly emits the recovery_dialog_requested
signal when backup operations complete with recoverable failures.
"""

import pytest
from core.common_types import OperationResultDict

from gui.model import DFBUModel
from gui.viewmodel import DFBUViewModel


@pytest.fixture
def partial_result() -> OperationResultDict:
    """Operation result with failures."""
    return {
        "status": "partial",
        "operation_type": "mirror_backup",
        "total_items": 3,
        "completed": [
            {
                "path": "/home/.bashrc",
                "dest_path": "/backup/.bashrc",
                "status": "success",
                "error_type": None,
                "error_message": "",
                "can_retry": False,
            },
        ],
        "failed": [
            {
                "path": "/home/.vimrc",
                "dest_path": "/backup/.vimrc",
                "status": "failed",
                "error_type": "permission",
                "error_message": "Permission denied",
                "can_retry": True,
            },
        ],
        "skipped": [],
        "warnings": [],
        "can_retry": ["/home/.vimrc"],
        "timestamp": "2026-02-01T10:00:00+00:00",
    }


class TestRecoveryDialogIntegration:
    """Integration tests for recovery dialog triggering."""

    @pytest.mark.integration
    @pytest.mark.gui
    def test_viewmodel_emits_recovery_signal_on_partial(
        self, qapp, yaml_config_dir, partial_result
    ):
        """ViewModel emits recovery_dialog_requested on partial status with retryable items."""
        # Arrange
        model = DFBUModel(yaml_config_dir)
        vm = DFBUViewModel(model)
        signal_received = []
        vm.recovery_dialog_requested.connect(lambda r: signal_received.append(r))

        # Act
        vm._on_backup_finished_with_result(partial_result)

        # Assert
        assert len(signal_received) == 1
        assert signal_received[0]["status"] == "partial"

    @pytest.mark.integration
    @pytest.mark.gui
    def test_viewmodel_no_signal_on_success(self, qapp, yaml_config_dir):
        """ViewModel does not emit signal on success status."""
        # Arrange
        model = DFBUModel(yaml_config_dir)
        vm = DFBUViewModel(model)
        signal_received = []
        vm.recovery_dialog_requested.connect(lambda r: signal_received.append(r))

        success_result: OperationResultDict = {
            "status": "success",
            "operation_type": "mirror_backup",
            "total_items": 1,
            "completed": [
                {
                    "path": "/home/.bashrc",
                    "dest_path": "/backup/.bashrc",
                    "status": "success",
                    "error_type": None,
                    "error_message": "",
                    "can_retry": False,
                },
            ],
            "failed": [],
            "skipped": [],
            "warnings": [],
            "can_retry": [],
            "timestamp": "2026-02-01T10:00:00+00:00",
        }

        # Act
        vm._on_backup_finished_with_result(success_result)

        # Assert
        assert len(signal_received) == 0

    @pytest.mark.integration
    @pytest.mark.gui
    def test_viewmodel_no_signal_when_no_retryable(self, qapp, yaml_config_dir):
        """ViewModel does not emit signal when no items can be retried."""
        # Arrange
        model = DFBUModel(yaml_config_dir)
        vm = DFBUViewModel(model)
        signal_received = []
        vm.recovery_dialog_requested.connect(lambda r: signal_received.append(r))

        no_retry_result: OperationResultDict = {
            "status": "failed",
            "operation_type": "mirror_backup",
            "total_items": 1,
            "completed": [],
            "failed": [
                {
                    "path": "/home/.vimrc",
                    "dest_path": "/backup/.vimrc",
                    "status": "failed",
                    "error_type": "not_found",
                    "error_message": "File not found",
                    "can_retry": False,
                },
            ],
            "skipped": [],
            "warnings": [],
            "can_retry": [],  # Empty - no retryable items
            "timestamp": "2026-02-01T10:00:00+00:00",
        }

        # Act
        vm._on_backup_finished_with_result(no_retry_result)

        # Assert
        assert len(signal_received) == 0
