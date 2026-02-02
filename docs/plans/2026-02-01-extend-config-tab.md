# Extend Configuration Tab Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add missing settings from `settings.yaml` to the existing Configuration tab in the GUI.

**Architecture:** Extend the existing Configuration tab's QFormLayout in the `.ui` file with new sections for Verification Options and Size Thresholds. Wire up the new widgets in `view.py` following the established pattern.

**Tech Stack:** PySide6 (Qt Designer `.ui` files), Python 3.14+

---

## Missing Settings

These 7 settings exist in `settings.yaml` but have no GUI controls:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `archive_format` | string | "tar.gz" | Archive format (tar.gz only currently) |
| `verify_after_backup` | bool | false | Automatic verification after backup |
| `hash_verification` | bool | false | Use SHA-256 for verification (slower) |
| `size_check_enabled` | bool | true | Enable pre-backup size analysis |
| `size_warning_threshold_mb` | int | 10 | Warning level threshold (yellow) |
| `size_alert_threshold_mb` | int | 100 | Alert level threshold (orange) |
| `size_critical_threshold_mb` | int | 1024 | Critical level threshold (red) |

---

## Tasks

### Task 1: Update Qt Designer UI File

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui`

**Step 1: Open UI file in Qt Designer**

```bash
cd /home/chris/projects/dfbu
designer DFBU/gui/designer/main_window_complete.ui
```

**Step 2: Add Verification Options section**

In the Configuration tab, after "Pre-Restore Safety" section (row 16), add:

1. Section header label (`verificationLabel`):
   - Text: "Verification Options"
   - styleSheet: `font-weight: bold; margin-top: 10px;`
   - Span both columns (row 17, column 0-1)

2. Verify After Backup checkbox (`config_verify_checkbox`):
   - Label: "Verify After Backup:" (row 18, column 0)
   - Checkbox text: "Automatically verify backup integrity" (row 18, column 1)
   - toolTip: "Run verification after each backup operation"

3. Hash Verification checkbox (`config_hash_checkbox`):
   - Label: "Hash Verification:" (row 19, column 0)
   - Checkbox text: "Use SHA-256 hash comparison (slower)" (row 19, column 1)
   - toolTip: "Compare file contents using cryptographic hash instead of size only"

**Step 3: Add Size Management section**

1. Section header label (`sizeManagementLabel`):
   - Text: "Size Management"
   - styleSheet: `font-weight: bold; margin-top: 10px;`
   - Span both columns (row 20, column 0-1)

2. Size Check Enabled checkbox (`config_size_check_checkbox`):
   - Label: "Enable Size Check:" (row 21, column 0)
   - Checkbox text: "Analyze file sizes before backup" (row 21, column 1)
   - toolTip: "Show warnings for large files before starting backup"

3. Warning Threshold spinbox (`config_size_warning_spinbox`):
   - Label: "Warning Threshold (MB):" (row 22, column 0)
   - SpinBox: minimum=1, maximum=10000, value=10 (row 22, column 1)
   - toolTip: "Files larger than this show a warning (yellow)"

4. Alert Threshold spinbox (`config_size_alert_spinbox`):
   - Label: "Alert Threshold (MB):" (row 23, column 0)
   - SpinBox: minimum=1, maximum=10000, value=100 (row 23, column 1)
   - toolTip: "Files larger than this show an alert (orange)"

5. Critical Threshold spinbox (`config_size_critical_spinbox`):
   - Label: "Critical Threshold (MB):" (row 24, column 0)
   - SpinBox: minimum=1, maximum=100000, value=1024 (row 24, column 1)
   - toolTip: "Files larger than this show critical warning (red)"

**Step 4: Save the UI file**

Save and close Qt Designer.

**Step 5: Commit UI changes**

```bash
git add DFBU/gui/designer/main_window_complete.ui
git commit -m "feat(ui): add verification and size management sections to config tab"
```

---

### Task 2: Add Widget References in View

**Files:**
- Modify: `DFBU/gui/view.py:639-683` (in `_find_config_tab_widgets` method)

**Step 1: Add widget reference declarations**

After line 683 (after `self.save_config_btn`), add the following widget lookups:

```python
        # Verification options widgets (v1.1.0)
        self.config_verify_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_verify_checkbox"
        )  # type: ignore[assignment]
        self.config_hash_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_hash_checkbox"
        )  # type: ignore[assignment]
        # Size management widgets (v1.1.0)
        self.config_size_check_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_size_check_checkbox"
        )  # type: ignore[assignment]
        self.config_size_warning_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_size_warning_spinbox"
        )  # type: ignore[assignment]
        self.config_size_alert_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_size_alert_spinbox"
        )  # type: ignore[assignment]
        self.config_size_critical_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_size_critical_spinbox"
        )  # type: ignore[assignment]
```

**Step 2: Run the application to verify widgets load**

```bash
cd /home/chris/projects/dfbu
source .venv/bin/activate
python DFBU/dfbu-gui.py
```

Expected: Application launches without errors, new widgets visible in Configuration tab.

**Step 3: Commit**

```bash
git add DFBU/gui/view.py
git commit -m "feat(view): add widget references for verification and size options"
```

---

### Task 3: Connect Widget Signals

**Files:**
- Modify: `DFBU/gui/view.py:729-794` (in `_connect_ui_signals` method)

**Step 1: Add signal connections for new widgets**

After line 781 (after `self.save_config_btn.clicked.connect(self._on_save_config)`), add:

```python
        # Verification options signal connections (v1.1.0)
        self.config_verify_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_hash_checkbox.stateChanged.connect(self._on_config_changed)
        # Size management signal connections (v1.1.0)
        self.config_size_check_checkbox.stateChanged.connect(
            self._on_size_check_checkbox_changed
        )
        self.config_size_check_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_size_warning_spinbox.valueChanged.connect(self._on_config_changed)
        self.config_size_alert_spinbox.valueChanged.connect(self._on_config_changed)
        self.config_size_critical_spinbox.valueChanged.connect(self._on_config_changed)
```

**Step 2: Add the size check checkbox handler method**

After `_on_pre_restore_checkbox_changed` method (around line 1430), add:

```python
    def _on_size_check_checkbox_changed(self, state: int) -> None:
        """Handle size check enabled checkbox state change."""
        # Enable/disable threshold spinboxes based on size check checkbox
        enabled = bool(state)
        self.config_size_warning_spinbox.setEnabled(enabled)
        self.config_size_alert_spinbox.setEnabled(enabled)
        self.config_size_critical_spinbox.setEnabled(enabled)
```

**Step 3: Commit**

```bash
git add DFBU/gui/view.py
git commit -m "feat(view): connect signals for verification and size management widgets"
```

---

### Task 4: Update Options Display

**Files:**
- Modify: `DFBU/gui/view.py:1269-1305` (in `_update_options_display` method)

**Step 1: Add loading of new options from model**

After line 1297 (after enabling max restore backups spinbox), add:

```python
        # Verification options (v1.1.0)
        self.config_verify_checkbox.setChecked(options.get("verify_after_backup", False))
        self.config_hash_checkbox.setChecked(options.get("hash_verification", False))

        # Size management options (v1.1.0)
        size_check_enabled = options.get("size_check_enabled", True)
        self.config_size_check_checkbox.setChecked(size_check_enabled)
        self.config_size_warning_spinbox.setValue(
            options.get("size_warning_threshold_mb", 10)
        )
        self.config_size_alert_spinbox.setValue(
            options.get("size_alert_threshold_mb", 100)
        )
        self.config_size_critical_spinbox.setValue(
            options.get("size_critical_threshold_mb", 1024)
        )
        # Enable threshold spinboxes only if size check is enabled
        self.config_size_warning_spinbox.setEnabled(size_check_enabled)
        self.config_size_alert_spinbox.setEnabled(size_check_enabled)
        self.config_size_critical_spinbox.setEnabled(size_check_enabled)
```

**Step 2: Run the application and verify options load**

```bash
python DFBU/dfbu-gui.py
```

Expected: Configuration tab shows current values from settings.yaml for all new options.

**Step 3: Commit**

```bash
git add DFBU/gui/view.py
git commit -m "feat(view): load verification and size options into config tab widgets"
```

---

### Task 5: Update Save Config Handler

**Files:**
- Modify: `DFBU/gui/view.py:1441-1510` (in `_on_save_config` method)

**Step 1: Add saving of new options to model**

After line 1479 (after saving `max_restore_backups`), add:

```python
            # Verification options (v1.1.0)
            self.viewmodel.command_update_option(
                "verify_after_backup", self.config_verify_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "hash_verification", self.config_hash_checkbox.isChecked()
            )
            # Size management options (v1.1.0)
            self.viewmodel.command_update_option(
                "size_check_enabled", self.config_size_check_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "size_warning_threshold_mb", self.config_size_warning_spinbox.value()
            )
            self.viewmodel.command_update_option(
                "size_alert_threshold_mb", self.config_size_alert_spinbox.value()
            )
            self.viewmodel.command_update_option(
                "size_critical_threshold_mb", self.config_size_critical_spinbox.value()
            )
```

**Step 2: Test saving configuration**

1. Launch application: `python DFBU/dfbu-gui.py`
2. Go to Configuration tab
3. Change a new option (e.g., enable "Verify After Backup")
4. Click "Save Config"
5. Check `DFBU/data/settings.yaml` - verify the option was saved

**Step 3: Commit**

```bash
git add DFBU/gui/view.py
git commit -m "feat(view): save verification and size options from config tab"
```

---

### Task 6: Write Integration Test

**Files:**
- Create: `DFBU/tests/test_config_tab_options.py`

**Step 1: Write the test file**

```python
"""
Integration tests for Configuration tab options.

Tests that new verification and size management options
are properly loaded and saved through the UI.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication

from gui.viewmodel import DFBUViewModel
from gui.model import DFBUModel


@pytest.mark.integration
class TestConfigTabVerificationOptions:
    """Test verification options in Configuration tab."""

    def test_verify_after_backup_option_saved(
        self, qapp: QApplication, temp_config_path: Path, mocker
    ) -> None:
        """Verify after backup option saves correctly."""
        # Arrange
        model = DFBUModel(temp_config_path)
        model.options["verify_after_backup"] = False

        # Act
        model.options["verify_after_backup"] = True
        success, _ = model.save_config()

        # Assert
        assert success
        assert model.options["verify_after_backup"] is True

    def test_hash_verification_option_saved(
        self, qapp: QApplication, temp_config_path: Path, mocker
    ) -> None:
        """Hash verification option saves correctly."""
        # Arrange
        model = DFBUModel(temp_config_path)
        model.options["hash_verification"] = False

        # Act
        model.options["hash_verification"] = True
        success, _ = model.save_config()

        # Assert
        assert success
        assert model.options["hash_verification"] is True


@pytest.mark.integration
class TestConfigTabSizeOptions:
    """Test size management options in Configuration tab."""

    def test_size_check_enabled_option_saved(
        self, qapp: QApplication, temp_config_path: Path
    ) -> None:
        """Size check enabled option saves correctly."""
        # Arrange
        model = DFBUModel(temp_config_path)

        # Act
        model.options["size_check_enabled"] = False
        success, _ = model.save_config()

        # Assert
        assert success
        assert model.options["size_check_enabled"] is False

    def test_size_thresholds_saved(
        self, qapp: QApplication, temp_config_path: Path
    ) -> None:
        """Size threshold options save correctly."""
        # Arrange
        model = DFBUModel(temp_config_path)

        # Act
        model.options["size_warning_threshold_mb"] = 25
        model.options["size_alert_threshold_mb"] = 250
        model.options["size_critical_threshold_mb"] = 2048
        success, _ = model.save_config()

        # Assert
        assert success
        assert model.options["size_warning_threshold_mb"] == 25
        assert model.options["size_alert_threshold_mb"] == 250
        assert model.options["size_critical_threshold_mb"] == 2048
```

**Step 2: Run the test**

```bash
pytest DFBU/tests/test_config_tab_options.py -v
```

Expected: All tests pass.

**Step 3: Commit**

```bash
git add DFBU/tests/test_config_tab_options.py
git commit -m "test: add integration tests for config tab verification and size options"
```

---

### Task 7: Update Documentation

**Files:**
- Modify: `DFBU/docs/CHANGELOG.md`

**Step 1: Add changelog entry**

Add to the top of the changelog (after the header):

```markdown
## [1.1.0] - 2026-02-XX

### Added

- **Configuration Tab Extensions**: Added GUI controls for all settings in `settings.yaml`:
  - Verification Options section: "Verify After Backup" and "Hash Verification" checkboxes
  - Size Management section: "Enable Size Check" checkbox and threshold spinboxes (Warning/Alert/Critical MB)
- Integration tests for new configuration options

### Changed

- Configuration tab now exposes all available backup settings
```

**Step 2: Commit**

```bash
git add DFBU/docs/CHANGELOG.md
git commit -m "docs: add changelog entry for config tab extensions"
```

---

### Task 8: Final Verification

**Step 1: Run full test suite**

```bash
pytest DFBU/tests/ -v --tb=short
```

Expected: All tests pass.

**Step 2: Run type checker**

```bash
mypy DFBU/
```

Expected: No type errors.

**Step 3: Manual verification**

1. Launch application
2. Go to Configuration tab
3. Verify all new sections are visible:
   - "Verification Options" with 2 checkboxes
   - "Size Management" with 1 checkbox and 3 spinboxes
4. Change settings and save
5. Close and reopen - verify settings persisted

**Step 4: Final commit**

```bash
git add -A
git commit -m "feat: complete config tab extension with verification and size options"
```

---

## Summary

This plan adds 6 new UI controls to the Configuration tab:

| Widget | Type | Setting Key |
|--------|------|-------------|
| `config_verify_checkbox` | QCheckBox | `verify_after_backup` |
| `config_hash_checkbox` | QCheckBox | `hash_verification` |
| `config_size_check_checkbox` | QCheckBox | `size_check_enabled` |
| `config_size_warning_spinbox` | QSpinBox | `size_warning_threshold_mb` |
| `config_size_alert_spinbox` | QSpinBox | `size_alert_threshold_mb` |
| `config_size_critical_spinbox` | QSpinBox | `size_critical_threshold_mb` |

Note: `archive_format` is intentionally not added as it's currently hardcoded to "tar.gz" and there's no alternative format support in the codebase.
