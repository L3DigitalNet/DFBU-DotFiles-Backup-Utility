# Error Handling v0.9.0 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete v0.9.0 error handling by wiring the existing ErrorHandler infrastructure to the UI with recovery dialog and retry/skip/continue logic.

**Architecture:** The ErrorHandler component, TypedDicts, Protocol, and `.ui` file already exist. This plan completes the integration by creating the RecoveryDialog Python class, wiring it to the View, and implementing user-facing recovery actions.

**Tech Stack:** Python 3.14+, PySide6, QUiLoader, existing MVVM architecture

---

## Pre-Implementation Verification

Before starting, verify all tests pass:

```bash
pytest DFBU/tests/ -v --tb=short
```

Expected: All ~500+ tests pass.

---

## Task 1: Create RecoveryDialog Class

**Files:**
- Create: `DFBU/gui/recovery_dialog.py`
- Test: `DFBU/tests/test_recovery_dialog.py`

### Step 1: Write the failing test

Create test file `DFBU/tests/test_recovery_dialog.py`:

```python
"""Tests for the RecoveryDialog component."""

import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QDialog

sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))
from recovery_dialog import RecoveryDialog


@pytest.fixture
def sample_operation_result():
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
        result = {
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
```

### Step 2: Run test to verify it fails

```bash
pytest DFBU/tests/test_recovery_dialog.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'recovery_dialog'`

### Step 3: Write minimal implementation

Create `DFBU/gui/recovery_dialog.py`:

```python
"""Recovery dialog for handling backup/restore failures.

Displays operation results with options to retry, skip, or abort.
Loaded from Qt Designer .ui file.
"""

from pathlib import Path
from typing import Final

from PySide6.QtCore import Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from core.common_types import OperationResultDict


# Path to UI file relative to this module
UI_FILE: Final[Path] = Path(__file__).parent / "designer" / "recovery_dialog.ui"


class RecoveryDialog(QDialog):
    """Dialog for recovery options after backup/restore failures.

    Shows summary of completed/failed items and provides options to:
    - Retry failed items that might succeed
    - Skip failed items and continue
    - Abort the operation

    Attributes:
        action: User's chosen action ("retry", "continue", "abort")
        operation_result: The OperationResultDict being displayed

    Public methods:
        get_retryable_paths: Get list of paths that can be retried
    """

    def __init__(
        self,
        operation_result: OperationResultDict,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the recovery dialog.

        Args:
            operation_result: Structured operation result to display
            parent: Parent widget, typically the main window
        """
        super().__init__(parent)
        self.operation_result = operation_result
        self.action: str = ""

        self._load_ui()
        self._populate_data()
        self._connect_signals()

    def _load_ui(self) -> None:
        """Load UI from .ui file and find child widgets."""
        loader = QUiLoader()
        ui_file = UI_FILE.open("r")
        loaded = loader.load(ui_file, self)
        ui_file.close()

        if loaded is None:
            raise RuntimeError(f"Failed to load UI file: {UI_FILE}")

        # Set window properties from loaded UI
        self.setWindowTitle(loaded.windowTitle())
        self.setMinimumSize(loaded.minimumSize())
        self.resize(loaded.size())

        # Find widgets by object name
        self.success_count_label: QLabel = loaded.findChild(QLabel, "successCountLabel")
        self.failed_count_label: QLabel = loaded.findChild(QLabel, "failedCountLabel")
        self.failed_items_tree: QTreeWidget = loaded.findChild(
            QTreeWidget, "failedItemsTree"
        )
        self.retry_info_label: QLabel = loaded.findChild(QLabel, "retryInfoLabel")
        self.retry_failed_btn: QPushButton = loaded.findChild(
            QPushButton, "retryFailedBtn"
        )
        self.continue_btn: QPushButton = loaded.findChild(QPushButton, "continueBtn")
        self.abort_btn: QPushButton = loaded.findChild(QPushButton, "abortBtn")

        # Transfer layout from loaded widget to this dialog
        if loaded.layout():
            self.setLayout(loaded.layout())

    def _populate_data(self) -> None:
        """Populate dialog with operation result data."""
        result = self.operation_result

        # Update summary labels
        completed_count = len(result["completed"])
        failed_count = len(result["failed"])

        self.success_count_label.setText(f"{completed_count} files backed up successfully")
        self.failed_count_label.setText(f"{failed_count} files failed")

        # Populate failed items tree
        self.failed_items_tree.clear()
        for item in result["failed"]:
            tree_item = QTreeWidgetItem([
                item["path"],
                item["error_message"],
                "Yes" if item["can_retry"] else "No",
            ])
            self.failed_items_tree.addTopLevelItem(tree_item)

        # Enable/disable retry button based on retryable items
        retryable_count = len(result["can_retry"])
        self.retry_failed_btn.setEnabled(retryable_count > 0)

        if retryable_count == 0:
            self.retry_info_label.setText("No items can be retried.")
        else:
            self.retry_info_label.setText(
                f"{retryable_count} item(s) marked 'Yes' may succeed if retried."
            )

    def _connect_signals(self) -> None:
        """Connect button signals to handlers."""
        self.retry_failed_btn.clicked.connect(self._on_retry)
        self.continue_btn.clicked.connect(self._on_continue)
        self.abort_btn.clicked.connect(self._on_abort)

    def _on_retry(self) -> None:
        """Handle Retry Failed button click."""
        self.action = "retry"
        self.accept()

    def _on_continue(self) -> None:
        """Handle Skip & Continue button click."""
        self.action = "continue"
        self.accept()

    def _on_abort(self) -> None:
        """Handle Abort button click."""
        self.action = "abort"
        self.reject()

    def get_retryable_paths(self) -> list[str]:
        """Get list of paths that can be retried.

        Returns:
            List of path strings from failed items where can_retry is True
        """
        return self.operation_result["can_retry"].copy()
```

### Step 4: Run test to verify it passes

```bash
pytest DFBU/tests/test_recovery_dialog.py -v
```

Expected: All tests PASS

### Step 5: Commit

```bash
git add DFBU/gui/recovery_dialog.py DFBU/tests/test_recovery_dialog.py
git commit -m "feat: add RecoveryDialog class for error recovery UI (v0.9.0)"
```

---

## Task 2: Wire RecoveryDialog to View

**Files:**
- Modify: `DFBU/gui/view.py`
- Test: Verify via manual test (complex GUI integration)

### Step 1: Add import and dialog show method

Add to `DFBU/gui/view.py` imports section:

```python
from gui.recovery_dialog import RecoveryDialog
```

### Step 2: Add method to show recovery dialog

Add method to `MainWindow` class:

```python
def _show_recovery_dialog(self, result: OperationResultDict) -> str:
    """Show recovery dialog when operation has failures.

    Args:
        result: Operation result with failures

    Returns:
        User's chosen action: "retry", "continue", or "abort"
    """
    dialog = RecoveryDialog(result, parent=self)
    dialog.exec()
    return dialog.action
```

### Step 3: Commit

```bash
git add DFBU/gui/view.py
git commit -m "feat: add recovery dialog display method to MainWindow"
```

---

## Task 3: Wire ViewModel to Show Dialog on Failures

**Files:**
- Modify: `DFBU/gui/viewmodel.py`

### Step 1: Add signal for requesting recovery dialog

In `DFBUViewModel` class, add signal:

```python
# In signal definitions section
recovery_dialog_requested = Signal(object)  # OperationResultDict
```

### Step 2: Connect worker signal to handler

In the `command_start_backup` method, after connecting `backup_finished`, add:

```python
self._backup_worker.backup_finished_with_result.connect(
    self._on_backup_finished_with_result
)
```

### Step 3: Add handler method

Add method to `DFBUViewModel`:

```python
def _on_backup_finished_with_result(self, result: OperationResultDict) -> None:
    """Handle backup completion with structured result.

    Emits recovery_dialog_requested signal if there are failures.

    Args:
        result: Structured operation result
    """
    # Only show recovery dialog if there are failures that could be retried
    if result["status"] != "success" and result["can_retry"]:
        self.recovery_dialog_requested.emit(result)
```

### Step 4: Commit

```bash
git add DFBU/gui/viewmodel.py
git commit -m "feat: emit recovery dialog signal on backup failures"
```

---

## Task 4: Connect View to ViewModel Recovery Signal

**Files:**
- Modify: `DFBU/gui/view.py`

### Step 1: Connect signal in MainWindow._connect_viewmodel_signals

Add connection:

```python
self.viewmodel.recovery_dialog_requested.connect(self._show_recovery_dialog)
```

### Step 2: Update _show_recovery_dialog to handle user action

Modify the method to act on user's choice:

```python
def _show_recovery_dialog(self, result: OperationResultDict) -> None:
    """Show recovery dialog when operation has failures.

    Args:
        result: Operation result with failures
    """
    dialog = RecoveryDialog(result, parent=self)
    dialog.exec()

    if dialog.action == "retry":
        # Get retryable paths and trigger retry
        paths_to_retry = dialog.get_retryable_paths()
        self._log_message(f"Retrying {len(paths_to_retry)} failed items...")
        # TODO: Implement retry logic in v0.9.1
    elif dialog.action == "continue":
        self._log_message("Skipping failed items, operation complete.")
    else:  # abort
        self._log_message("Operation aborted by user.")
```

### Step 3: Commit

```bash
git add DFBU/gui/view.py
git commit -m "feat: connect recovery dialog to viewmodel signal"
```

---

## Task 5: Add Integration Test for Recovery Dialog Flow

**Files:**
- Create: `DFBU/tests/test_recovery_dialog_integration.py`

### Step 1: Write integration test

```python
"""Integration tests for recovery dialog flow."""

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
from PySide6.QtCore import QTimer

sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))
from core.common_types import OperationResultDict
from viewmodel import DFBUViewModel
from model import DFBUModel


@pytest.fixture
def partial_result() -> OperationResultDict:
    """Operation result with failures."""
    return {
        "status": "partial",
        "operation_type": "mirror_backup",
        "total_items": 3,
        "completed": [
            {"path": "/home/.bashrc", "dest_path": "/backup/.bashrc", "status": "success",
             "error_type": None, "error_message": "", "can_retry": False},
        ],
        "failed": [
            {"path": "/home/.vimrc", "dest_path": "/backup/.vimrc", "status": "failed",
             "error_type": "permission", "error_message": "Permission denied", "can_retry": True},
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
        self, qapp, temp_config_path, partial_result
    ):
        """ViewModel emits recovery_dialog_requested on partial status with retryable items."""
        # Arrange
        model = DFBUModel(temp_config_path)
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
    def test_viewmodel_no_signal_on_success(self, qapp, temp_config_path):
        """ViewModel does not emit signal on success status."""
        # Arrange
        model = DFBUModel(temp_config_path)
        vm = DFBUViewModel(model)
        signal_received = []
        vm.recovery_dialog_requested.connect(lambda r: signal_received.append(r))

        success_result: OperationResultDict = {
            "status": "success",
            "operation_type": "mirror_backup",
            "total_items": 1,
            "completed": [
                {"path": "/home/.bashrc", "dest_path": "/backup/.bashrc", "status": "success",
                 "error_type": None, "error_message": "", "can_retry": False},
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
    def test_viewmodel_no_signal_when_no_retryable(self, qapp, temp_config_path):
        """ViewModel does not emit signal when no items can be retried."""
        # Arrange
        model = DFBUModel(temp_config_path)
        vm = DFBUViewModel(model)
        signal_received = []
        vm.recovery_dialog_requested.connect(lambda r: signal_received.append(r))

        no_retry_result: OperationResultDict = {
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
            "can_retry": [],  # Empty - no retryable items
            "timestamp": "2026-02-01T10:00:00+00:00",
        }

        # Act
        vm._on_backup_finished_with_result(no_retry_result)

        # Assert
        assert len(signal_received) == 0
```

### Step 2: Run tests

```bash
pytest DFBU/tests/test_recovery_dialog_integration.py -v
```

Expected: All tests PASS

### Step 3: Commit

```bash
git add DFBU/tests/test_recovery_dialog_integration.py
git commit -m "test: add integration tests for recovery dialog flow"
```

---

## Task 6: Run Full Test Suite and Update Documentation

### Step 1: Run full test suite

```bash
pytest DFBU/tests/ -v --tb=short
```

Expected: All tests pass (500+)

### Step 2: Update production-readiness-design.md checklist

In `docs/plans/2026-01-31-production-readiness-design.md`, update the v0.9.0 checklist:

```markdown
### v0.9.0 - Error Handling & Recovery
- [x] `ErrorHandler` component
- [x] `ErrorHandlerProtocol` interface
- [x] `OperationResult` dataclass
- [x] Error categorization logic
- [x] User-friendly error messages
- [x] Recovery dialog UI
- [x] Retry/skip/continue logic (basic - retry deferred to v0.9.1)
- [x] Comprehensive tests
- [x] Documentation updates
```

### Step 3: Commit

```bash
git add docs/plans/2026-01-31-production-readiness-design.md
git commit -m "docs: update v0.9.0 checklist as complete"
```

---

## Task 7: Manual Verification

### Step 1: Run the application

```bash
python DFBU/dfbu-gui.py
```

### Step 2: Trigger a backup failure

1. Configure a path to a file you don't have read permission for
2. Start backup
3. Verify recovery dialog appears with correct counts
4. Test each button (Retry Failed, Skip & Continue, Abort)
5. Verify appropriate log messages appear

### Step 3: Document any issues found

If issues are found, create follow-up tasks.

---

## Summary

**Total Tasks:** 7
**Estimated Time:** 2-3 hours
**Key Files Created:**
- `DFBU/gui/recovery_dialog.py`
- `DFBU/tests/test_recovery_dialog.py`
- `DFBU/tests/test_recovery_dialog_integration.py`

**Key Files Modified:**
- `DFBU/gui/view.py`
- `DFBU/gui/viewmodel.py`
- `docs/plans/2026-01-31-production-readiness-design.md`

**Deferred to v0.9.1:**
- Actual retry execution (re-running backup for specific paths)
- RestoreWorker recovery dialog integration
