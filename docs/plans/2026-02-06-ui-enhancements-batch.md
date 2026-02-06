# UI Enhancements Batch Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement 7 UI/UX improvements: rename Update→Edit, hide missing dotfiles, external config editor with validation, smart browse picker, config export, verbose log mode, and unchanged file logging.

**Architecture:** All changes follow the existing MVVM pattern. UI additions go in `.ui` designer files (or programmatic additions to existing layouts for filtering controls). View handles UI events, ViewModel coordinates logic, Model handles file operations. Log changes modify signal handlers in view.py and the BackupWorker in viewmodel.py.

**Tech Stack:** Python 3.14+, PySide6, ruamel.yaml, subprocess (for xdg-open)

---

## Task 1: Rename "Update" Button to "Edit"

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui` (line ~462, the `fileGroupUpdateFileButton` label)

**Step 1: Write the failing test**

```python
# DFBU/tests/test_ui_labels.py
import pytest
from pathlib import Path
from PySide6.QtWidgets import QPushButton


@pytest.mark.gui
def test_update_button_labeled_edit(qapp, qtbot):
    """The backup tab's update button should be labeled 'Edit', not 'Update'."""
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm)

    btn = window.findChild(QPushButton, "fileGroupUpdateFileButton")
    assert btn is not None
    assert btn.text() == "Edit"
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_ui_labels.py::test_update_button_labeled_edit -v`
Expected: FAIL — button text is "Update"

**Step 3: Change the label in the .ui file**

In `DFBU/gui/designer/main_window_complete.ui`, find the `fileGroupUpdateFileButton` widget and change:
```xml
<!-- OLD -->
<property name="text">
 <string>Update</string>
</property>

<!-- NEW -->
<property name="text">
 <string>Edit</string>
</property>
```

No Python code changes needed — the object name stays `fileGroupUpdateFileButton`, and view.py references it by object name.

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_ui_labels.py::test_update_button_labeled_edit -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: 0 errors

**Step 6: Commit**

```bash
git add DFBU/gui/designer/main_window_complete.ui DFBU/tests/test_ui_labels.py
git commit -m "feat: rename Update button to Edit on backup tab"
```

---

## Task 2: Hide Missing/Not-Found Dotfiles Checkbox

**Context:** The backup tab's dotfile table shows all entries including ones where the file doesn't exist on disk (Status column = "✗"). Users want a checkbox to hide these irrelevant rows. The table already has a text filter (`_apply_filter` at view.py:1957) that hides rows by text match. We need a complementary filter.

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui` — add `hideMissingCheckbox` to the backup toolbar layout (`backupToolbarLayout`)
- Modify: `DFBU/gui/view.py` — wire up checkbox, modify filter logic
- Create: `DFBU/tests/test_hide_missing.py`

### Step 1: Write the failing test

```python
# DFBU/tests/test_hide_missing.py
import pytest
from pathlib import Path
from PySide6.QtWidgets import QCheckBox


@pytest.mark.gui
def test_hide_missing_checkbox_exists(qapp, qtbot):
    """Backup tab should have a 'Hide missing' checkbox."""
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm)

    checkbox = window.findChild(QCheckBox, "hideMissingCheckbox")
    assert checkbox is not None
    assert checkbox.text() == "Hide missing"
```

### Step 2: Run test to verify it fails

Run: `pytest DFBU/tests/test_hide_missing.py::test_hide_missing_checkbox_exists -v`
Expected: FAIL — widget not found

### Step 3: Add checkbox to .ui file

In `DFBU/gui/designer/main_window_complete.ui`, add a `QCheckBox` named `hideMissingCheckbox` to the `backupToolbarLayout` (between the filter input and the Add button):

```xml
<item>
 <widget class="QCheckBox" name="hideMissingCheckbox">
  <property name="text">
   <string>Hide missing</string>
  </property>
  <property name="toolTip">
   <string>Hide dotfiles whose paths don't exist on this system</string>
  </property>
 </widget>
</item>
```

### Step 4: Run test to verify checkbox exists

Run: `pytest DFBU/tests/test_hide_missing.py::test_hide_missing_checkbox_exists -v`
Expected: PASS

### Step 5: Write the filtering behavior test

```python
# Add to DFBU/tests/test_hide_missing.py

@pytest.mark.gui
def test_hide_missing_hides_nonexistent_rows(qapp, qtbot):
    """When 'Hide missing' is checked, rows with status '✗' should be hidden."""
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm)

    # Load config and wait for table to populate
    vm.command_load_config()
    qtbot.waitUntil(lambda: window.dotfile_table.rowCount() > 0, timeout=5000)

    total_rows = window.dotfile_table.rowCount()

    # Count rows with missing status (column 1 = "✗")
    missing_count = 0
    for row in range(total_rows):
        status_item = window.dotfile_table.item(row, 1)
        if status_item and status_item.text() == "✗":
            missing_count += 1

    # Check the hide missing checkbox
    checkbox = window.findChild(QCheckBox, "hideMissingCheckbox")
    checkbox.setChecked(True)

    # Count visible rows
    visible_count = sum(
        1 for row in range(total_rows)
        if not window.dotfile_table.isRowHidden(row)
    )

    assert visible_count == total_rows - missing_count
```

### Step 6: Run test to verify it fails

Run: `pytest DFBU/tests/test_hide_missing.py::test_hide_missing_hides_nonexistent_rows -v`
Expected: FAIL — checkbox doesn't filter yet

### Step 7: Implement the filtering logic in view.py

**In `_find_backup_tab_widgets()`** (view.py ~line 594), add widget reference:

```python
self._hide_missing_checkbox: QCheckBox | None = ui_widget.findChild(
    QCheckBox, "hideMissingCheckbox"
)
```

**In `_connect_ui_signals()`** (view.py ~line 800), add connection:

```python
# Hide missing checkbox
if self._hide_missing_checkbox:
    self._hide_missing_checkbox.stateChanged.connect(self._apply_combined_filters)
```

**Also update the existing filter input connection** to use `_apply_combined_filters`:

```python
# Change from:
if self._filter_input:
    self._filter_input.textChanged.connect(self._apply_filter)
# To:
if self._filter_input:
    self._filter_input.textChanged.connect(self._apply_combined_filters)
```

**Add new `_apply_combined_filters` method** that combines text filter + hide-missing filter:

```python
def _apply_combined_filters(self) -> None:
    """Apply all active filters (text search + hide missing) to the dotfile table."""
    text = ""
    if self._filter_input:
        text = self._filter_input.text().lower().strip()

    hide_missing = False
    if self._hide_missing_checkbox:
        hide_missing = self._hide_missing_checkbox.isChecked()

    for row in range(self.dotfile_table.rowCount()):
        # Text filter check
        text_matches = True
        if text:
            app_item = self.dotfile_table.item(row, 2)
            tags_item = self.dotfile_table.item(row, 3)
            path_item = self.dotfile_table.item(row, 5)
            app_text = app_item.text().lower() if app_item else ""
            tags_text = tags_item.text().lower() if tags_item else ""
            path_text = path_item.text().lower() if path_item else ""
            text_matches = text in app_text or text in tags_text or text in path_text

        # Missing status filter check
        status_matches = True
        if hide_missing:
            status_item = self.dotfile_table.item(row, 1)
            if status_item and status_item.text() == "✗":
                status_matches = False

        self.dotfile_table.setRowHidden(row, not (text_matches and status_matches))
```

**Remove the old `_apply_filter` method** (view.py:1957-1988) and replace with `_apply_combined_filters`.

### Step 8: Run tests

Run: `pytest DFBU/tests/test_hide_missing.py -v`
Expected: PASS (both tests)

### Step 9: Run mypy

Run: `mypy DFBU/`
Expected: 0 errors

### Step 10: Commit

```bash
git add DFBU/gui/designer/main_window_complete.ui DFBU/gui/view.py DFBU/tests/test_hide_missing.py
git commit -m "feat: add 'Hide missing' checkbox to filter out non-existent dotfiles"
```

---

## Task 3: External Config Editor + YAML Validation

**Context:** Users want to edit `dotfiles.yaml` directly in their preferred text editor and validate the YAML structure afterward. We need two buttons on the backup tab: "Edit Config" opens the file externally, "Validate Config" checks syntax/structure. After external editing, we offer to reload the config.

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui` — add `editConfigButton` and `validateConfigButton` to `backupActionBarLayout`
- Modify: `DFBU/gui/view.py` — implement handlers
- Modify: `DFBU/gui/viewmodel.py` — add `command_validate_config()` and `get_config_dir()` methods
- Create: `DFBU/tests/test_config_editor.py`

### Step 1: Write the failing test for UI buttons

```python
# DFBU/tests/test_config_editor.py
import pytest
from pathlib import Path
from PySide6.QtWidgets import QPushButton


@pytest.mark.gui
def test_edit_config_button_exists(qapp, qtbot):
    """Backup tab should have an 'Edit Config' button."""
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm)

    btn = window.findChild(QPushButton, "editConfigButton")
    assert btn is not None


@pytest.mark.gui
def test_validate_config_button_exists(qapp, qtbot):
    """Backup tab should have a 'Validate Config' button."""
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm)

    btn = window.findChild(QPushButton, "validateConfigButton")
    assert btn is not None
```

### Step 2: Run test to verify it fails

Run: `pytest DFBU/tests/test_config_editor.py -v`
Expected: FAIL — buttons not found

### Step 3: Add buttons to .ui file

In `DFBU/gui/designer/main_window_complete.ui`, add two buttons to `backupActionBarLayout` (after Save Config button):

```xml
<item>
 <widget class="QPushButton" name="editConfigButton">
  <property name="text">
   <string>Edit Config</string>
  </property>
  <property name="toolTip">
   <string>Open dotfiles.yaml in your system text editor</string>
  </property>
 </widget>
</item>
<item>
 <widget class="QPushButton" name="validateConfigButton">
  <property name="text">
   <string>Validate Config</string>
  </property>
  <property name="toolTip">
   <string>Check dotfiles.yaml for syntax and structure errors</string>
  </property>
 </widget>
</item>
```

### Step 4: Run test to verify buttons exist

Run: `pytest DFBU/tests/test_config_editor.py -v`
Expected: PASS

### Step 5: Write the validation logic test

```python
# Add to DFBU/tests/test_config_editor.py

@pytest.mark.unit
def test_validate_config_returns_success_for_valid_config():
    """Validation should return success for a well-formed dotfiles.yaml."""
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    vm.command_load_config()

    success, message = vm.command_validate_config()
    assert success is True
    assert "valid" in message.lower() or "ok" in message.lower()


@pytest.mark.unit
def test_validate_config_returns_error_for_bad_yaml(tmp_path):
    """Validation should return failure for malformed YAML."""
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

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
```

### Step 6: Run test to verify it fails

Run: `pytest DFBU/tests/test_config_editor.py::test_validate_config_returns_success_for_valid_config -v`
Expected: FAIL — `command_validate_config` doesn't exist

### Step 7: Implement `command_validate_config()` in viewmodel.py

Add to `DFBUViewModel` class (viewmodel.py):

```python
def command_validate_config(self) -> tuple[bool, str]:
    """
    Validate the dotfiles.yaml and settings.yaml configuration files.

    Returns:
        Tuple of (success, message). Message contains error details on failure.
    """
    config_dir = self.model.config_path
    errors: list[str] = []

    # Validate dotfiles.yaml
    dotfiles_path = config_dir / "dotfiles.yaml"
    if dotfiles_path.exists():
        try:
            from core.yaml_config import YAMLConfigLoader
            loader = YAMLConfigLoader(config_dir)
            loader.load_dotfiles()
        except (ValueError, Exception) as e:
            errors.append(f"dotfiles.yaml: {e}")
    else:
        errors.append("dotfiles.yaml: File not found")

    # Validate settings.yaml
    settings_path = config_dir / "settings.yaml"
    if settings_path.exists():
        try:
            from core.yaml_config import YAMLConfigLoader
            loader = YAMLConfigLoader(config_dir)
            loader.load_settings()
        except (ValueError, Exception) as e:
            errors.append(f"settings.yaml: {e}")
    else:
        errors.append("settings.yaml: File not found")

    if errors:
        return False, "Validation errors:\n" + "\n".join(errors)
    return True, "Configuration is valid. No errors found."

def get_config_dir(self) -> Path:
    """Return the path to the configuration directory."""
    return self.model.config_path
```

### Step 8: Run validation tests

Run: `pytest DFBU/tests/test_config_editor.py -v -k validate`
Expected: PASS

### Step 9: Wire up buttons in view.py

**In `_find_backup_tab_widgets()`**, add references:

```python
self.edit_config_btn: QPushButton = ui_widget.findChild(
    QPushButton, "editConfigButton"
)  # type: ignore[assignment]
self.validate_config_btn: QPushButton = ui_widget.findChild(
    QPushButton, "validateConfigButton"
)  # type: ignore[assignment]
```

**In `_connect_ui_signals()`**, add connections:

```python
self.edit_config_btn.clicked.connect(self._on_edit_config)
self.validate_config_btn.clicked.connect(self._on_validate_config)
```

**Add handler methods:**

```python
def _on_edit_config(self) -> None:
    """Open dotfiles.yaml in the user's default text editor."""
    import subprocess

    config_dir = self.viewmodel.get_config_dir()
    dotfiles_path = config_dir / "dotfiles.yaml"

    if not dotfiles_path.exists():
        QMessageBox.warning(
            self,
            "File Not Found",
            f"Configuration file not found:\n{dotfiles_path}",
        )
        return

    try:
        subprocess.Popen(["xdg-open", str(dotfiles_path)])
        self.status_bar.showMessage(
            "Opened dotfiles.yaml in external editor",
            STATUS_MESSAGE_TIMEOUT_MS,
        )
    except FileNotFoundError:
        QMessageBox.warning(
            self,
            "Editor Not Found",
            "Could not open file: xdg-open not found.\n"
            "Please open manually:\n" + str(dotfiles_path),
        )

def _on_validate_config(self) -> None:
    """Validate YAML configuration files and show results."""
    success, message = self.viewmodel.command_validate_config()

    if success:
        # Offer to reload config after validation (user may have edited externally)
        reply = QMessageBox.information(
            self,
            "Validation Passed",
            f"{message}\n\nReload configuration from disk?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.viewmodel.command_load_config()
    else:
        QMessageBox.warning(self, "Validation Failed", message)
```

### Step 10: Run all tests

Run: `pytest DFBU/tests/test_config_editor.py -v`
Expected: PASS

### Step 11: Run mypy

Run: `mypy DFBU/`
Expected: 0 errors

### Step 12: Commit

```bash
git add DFBU/gui/designer/main_window_complete.ui DFBU/gui/view.py DFBU/gui/viewmodel.py DFBU/tests/test_config_editor.py
git commit -m "feat: add Edit Config and Validate Config buttons to backup tab"
```

---

## Task 4: Smart Browse Picker (Unified File/Directory Selection)

**Context:** The `AddDotfileDialog._on_browse_path()` method (view.py:266-303) currently shows a `QMessageBox` asking "File or Directory?" before opening the appropriate picker. Users want a single picker that lets them select either. The approach: use a non-native `QFileDialog` in `ExistingFile` mode with a patched `accept()` that also accepts directory selections.

**Files:**
- Modify: `DFBU/gui/view.py` — rewrite `AddDotfileDialog._on_browse_path()`
- Modify: `DFBU/tests/test_config_editor.py` or create `DFBU/tests/test_browse_picker.py`

### Step 1: Write the failing test

```python
# DFBU/tests/test_browse_picker.py
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from PySide6.QtWidgets import QMessageBox


@pytest.mark.gui
def test_browse_does_not_show_type_prompt(qapp, qtbot, monkeypatch):
    """Browse should NOT show a 'File or Directory?' message box."""
    from gui.view import AddDotfileDialog

    dialog = AddDotfileDialog(None)

    # Track if QMessageBox is called (it should NOT be)
    message_box_called = False
    original_exec = QMessageBox.exec

    def mock_exec(self):
        nonlocal message_box_called
        if self.windowTitle() == "Select Type":
            message_box_called = True
        return original_exec(self)

    monkeypatch.setattr(QMessageBox, "exec", mock_exec)

    # Mock QFileDialog to auto-cancel so we don't block
    with patch("gui.view.QFileDialog") as mock_fd:
        mock_instance = MagicMock()
        mock_instance.exec.return_value = 0  # Cancelled
        mock_fd.return_value = mock_instance
        mock_fd.Option = MagicMock()
        mock_fd.FileMode = MagicMock()
        mock_fd.DialogLabel = MagicMock()

        dialog._on_browse_path()

    assert not message_box_called, "Browse should not show File/Directory type prompt"
```

### Step 2: Run test to verify it fails

Run: `pytest DFBU/tests/test_browse_picker.py -v`
Expected: FAIL — current code still shows the QMessageBox

### Step 3: Rewrite `_on_browse_path()` in AddDotfileDialog

Replace the entire method at view.py:266-303:

```python
def _on_browse_path(self) -> None:
    """Open a unified file/directory picker.

    Uses a non-native QFileDialog that allows selecting either files
    or directories from a single dialog, without a type prompt.
    """
    dialog = QFileDialog(self, "Select File or Directory", str(Path.home()))
    dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
    dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    dialog.setLabelText(QFileDialog.DialogLabel.Accept, "Select")
    dialog.setNameFilter("All Files (*)")

    # Override accept to also allow directory selection.
    # By default, clicking "Select" on a highlighted directory enters it.
    # This patch makes it accept the directory path instead.
    original_accept = dialog.accept

    def accept_with_dirs() -> None:
        line_edit = dialog.findChild(QLineEdit, "fileNameEdit")
        if line_edit:
            name = line_edit.text().strip()
            if name:
                candidate = Path(dialog.directory().absolutePath()) / name
                if candidate.is_dir():
                    dialog.done(QDialog.DialogCode.Accepted)
                    return
        original_accept()

    dialog.accept = accept_with_dirs  # type: ignore[method-assign]

    if dialog.exec() == QDialog.DialogCode.Accepted:
        selected = dialog.selectedFiles()
        if selected:
            chosen = selected[0]
            # Verify selection is a directory if no file was directly selected
            if not Path(chosen).exists():
                line_edit = dialog.findChild(QLineEdit, "fileNameEdit")
                if line_edit:
                    name = line_edit.text().strip()
                    candidate = Path(dialog.directory().absolutePath()) / name
                    if candidate.exists():
                        chosen = str(candidate)
            self.path_input_edit.setText(chosen)
```

Note: The imports `QFileDialog`, `QLineEdit`, and `QDialog` are already available in the file scope.

### Step 4: Run test

Run: `pytest DFBU/tests/test_browse_picker.py -v`
Expected: PASS

### Step 5: Run mypy

Run: `mypy DFBU/`
Expected: 0 errors

### Step 6: Commit

```bash
git add DFBU/gui/view.py DFBU/tests/test_browse_picker.py
git commit -m "feat: replace file/dir prompt with unified browse picker"
```

---

## Task 5: Config Export (Backup/Export dotfiles.yaml + settings.yaml)

**Context:** Users want to export their `dotfiles.yaml` and `settings.yaml` to an arbitrary location for safekeeping. This is a simple file copy operation. We'll add an "Export Config" button to the backup tab's action bar.

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui` — add `exportConfigButton`
- Modify: `DFBU/gui/view.py` — add widget ref + handler
- Modify: `DFBU/gui/viewmodel.py` — add `command_export_config(dest_dir)` method
- Create: `DFBU/tests/test_config_export.py`

### Step 1: Write the failing test

```python
# DFBU/tests/test_config_export.py
import pytest
from pathlib import Path


@pytest.mark.unit
def test_export_config_copies_files(tmp_path):
    """Export should copy dotfiles.yaml and settings.yaml to the target directory."""
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)

    dest_dir = tmp_path / "export"
    dest_dir.mkdir()

    success, message = vm.command_export_config(dest_dir)

    assert success is True
    assert (dest_dir / "dotfiles.yaml").exists()
    assert (dest_dir / "settings.yaml").exists()
```

### Step 2: Run test to verify it fails

Run: `pytest DFBU/tests/test_config_export.py -v`
Expected: FAIL — `command_export_config` doesn't exist

### Step 3: Implement `command_export_config()` in viewmodel.py

```python
def command_export_config(self, dest_dir: Path) -> tuple[bool, str]:
    """
    Export dotfiles.yaml and settings.yaml to the specified directory.

    Args:
        dest_dir: Destination directory for the exported files

    Returns:
        Tuple of (success, message)
    """
    import shutil

    config_dir = self.model.config_path
    files_to_export = ["dotfiles.yaml", "settings.yaml"]
    copied: list[str] = []
    errors: list[str] = []

    for filename in files_to_export:
        src = config_dir / filename
        dest = dest_dir / filename
        if src.exists():
            try:
                shutil.copy2(src, dest)
                copied.append(filename)
            except (OSError, PermissionError) as e:
                errors.append(f"{filename}: {e}")
        else:
            errors.append(f"{filename}: Source file not found")

    if errors:
        return False, f"Exported {len(copied)} file(s), errors:\n" + "\n".join(errors)
    return True, f"Exported {len(copied)} file(s) to {dest_dir}"
```

### Step 4: Run test

Run: `pytest DFBU/tests/test_config_export.py -v`
Expected: PASS

### Step 5: Add button to .ui file and wire up in view.py

In the `.ui` file, add to `backupActionBarLayout`:

```xml
<item>
 <widget class="QPushButton" name="exportConfigButton">
  <property name="text">
   <string>Export Config</string>
  </property>
  <property name="toolTip">
   <string>Export dotfiles.yaml and settings.yaml to a location of your choice</string>
  </property>
 </widget>
</item>
```

In `_find_backup_tab_widgets()`:

```python
self.export_config_btn: QPushButton = ui_widget.findChild(
    QPushButton, "exportConfigButton"
)  # type: ignore[assignment]
```

In `_connect_ui_signals()`:

```python
self.export_config_btn.clicked.connect(self._on_export_config)
```

Add handler:

```python
def _on_export_config(self) -> None:
    """Export configuration files to a user-chosen directory."""
    dest_dir = QFileDialog.getExistingDirectory(
        self, "Select Export Destination", str(Path.home())
    )

    if not dest_dir:
        return

    success, message = self.viewmodel.command_export_config(Path(dest_dir))

    if success:
        self.status_bar.showMessage(message, STATUS_MESSAGE_TIMEOUT_MS)
    else:
        QMessageBox.warning(self, "Export Failed", message)
```

### Step 6: Run all tests

Run: `pytest DFBU/tests/test_config_export.py -v && pytest DFBU/tests/ -m gui -v`
Expected: PASS

### Step 7: Run mypy

Run: `mypy DFBU/`
Expected: 0 errors

### Step 8: Commit

```bash
git add DFBU/gui/designer/main_window_complete.ui DFBU/gui/view.py DFBU/gui/viewmodel.py DFBU/tests/test_config_export.py
git commit -m "feat: add Export Config button to backup dotfiles.yaml and settings.yaml"
```

---

## Task 6: Verbose Log Mode (Show Destination Paths)

**Context:** Currently `_on_item_processed` (view.py:1103) logs just filenames: `✓ bashrc → bashrc`. Users want an option to also see the full destination path: `✓ bashrc → /home/user/backups/mirror/hostname/bashrc`. We add a "Verbose" toggle button to the log filter row.

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui` — add `logPaneVerboseButton` to log pane toolbar
- Modify: `DFBU/gui/view.py` — add widget ref, modify `_on_item_processed` to check verbose state
- Create: `DFBU/tests/test_verbose_log.py`

### Step 1: Write the failing test

```python
# DFBU/tests/test_verbose_log.py
import pytest
from pathlib import Path
from PySide6.QtWidgets import QPushButton


@pytest.mark.gui
def test_verbose_button_exists(qapp, qtbot):
    """Log pane should have a 'Verbose' toggle button."""
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm)

    btn = window.findChild(QPushButton, "logPaneVerboseButton")
    assert btn is not None
    assert btn.isCheckable()
```

### Step 2: Run test to verify it fails

Run: `pytest DFBU/tests/test_verbose_log.py -v`
Expected: FAIL

### Step 3: Add button to .ui file

Add to the log pane toolbar (near the existing filter buttons):

```xml
<item>
 <widget class="QPushButton" name="logPaneVerboseButton">
  <property name="text">
   <string>Verbose</string>
  </property>
  <property name="checkable">
   <bool>true</bool>
  </property>
  <property name="checked">
   <bool>false</bool>
  </property>
  <property name="toolTip">
   <string>Show full destination paths in log entries</string>
  </property>
 </widget>
</item>
```

### Step 4: Run test

Run: `pytest DFBU/tests/test_verbose_log.py::test_verbose_button_exists -v`
Expected: PASS

### Step 5: Write the log output behavior test

```python
# Add to DFBU/tests/test_verbose_log.py

@pytest.mark.gui
def test_verbose_mode_shows_full_path(qapp, qtbot):
    """In verbose mode, processed items should show full destination path."""
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm)

    # Enable verbose mode
    verbose_btn = window.findChild(QPushButton, "logPaneVerboseButton")
    verbose_btn.setChecked(True)

    # Simulate an item processed signal
    window._on_item_processed("/home/user/.bashrc", "/home/user/backups/mirror/host/.bashrc")

    log_text = window.operation_log.toPlainText()
    assert "/home/user/backups/mirror/host/.bashrc" in log_text


@pytest.mark.gui
def test_non_verbose_mode_shows_names_only(qapp, qtbot):
    """In non-verbose mode, processed items should show filenames only."""
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm)

    # Ensure verbose is off
    verbose_btn = window.findChild(QPushButton, "logPaneVerboseButton")
    verbose_btn.setChecked(False)

    # Simulate an item processed signal
    window._on_item_processed("/home/user/.bashrc", "/home/user/backups/mirror/host/.bashrc")

    log_text = window.operation_log.toPlainText()
    assert ".bashrc" in log_text
    assert "/home/user/backups/mirror/host/.bashrc" not in log_text
```

### Step 6: Run tests to verify they fail

Run: `pytest DFBU/tests/test_verbose_log.py -v`
Expected: button test PASS, behavior tests FAIL

### Step 7: Implement verbose mode in view.py

**In `_find_logs_tab_widgets()`**, add:

```python
self._log_verbose_btn: QPushButton = ui_widget.findChild(
    QPushButton, "logPaneVerboseButton"
)  # type: ignore[assignment]
```

**Modify `_on_item_processed()`** (view.py:1103):

```python
def _on_item_processed(self, source: str, destination: str) -> None:
    """Handle item processed signal."""
    if self._log_verbose_btn and self._log_verbose_btn.isChecked():
        log_message = f"✓ {Path(source).name} → {destination}"
    else:
        log_message = f"✓ {Path(source).name} → {Path(destination).name}"
    self._append_log(log_message, "success")
```

### Step 8: Run tests

Run: `pytest DFBU/tests/test_verbose_log.py -v`
Expected: PASS

### Step 9: Run mypy

Run: `mypy DFBU/`
Expected: 0 errors

### Step 10: Commit

```bash
git add DFBU/gui/designer/main_window_complete.ui DFBU/gui/view.py DFBU/tests/test_verbose_log.py
git commit -m "feat: add verbose log mode showing full destination paths"
```

---

## Task 7: Log Unchanged (Skipped) File Names

**Context:** Currently, `_on_item_skipped` (view.py:1108) batches skip messages: every 10 skips it logs `⊘ Skipped 10 unchanged files (total: 30)...`. Users want to see the name of each unchanged file individually. We'll make this the default behavior and remove the batch throttling. The `SKIP_LOG_INTERVAL` constant becomes unnecessary.

**Files:**
- Modify: `DFBU/gui/view.py` — rewrite `_on_item_skipped()`, remove `SKIP_LOG_INTERVAL`
- Create: `DFBU/tests/test_skip_logging.py`

### Step 1: Write the failing test

```python
# DFBU/tests/test_skip_logging.py
import pytest
from pathlib import Path
from PySide6.QtWidgets import QPushButton


@pytest.mark.gui
def test_skipped_file_name_appears_in_log(qapp, qtbot):
    """Each skipped file should have its name logged individually."""
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm)

    # Simulate skipping a single file
    window._on_item_skipped("/home/user/.bashrc", "File unchanged")

    log_text = window.operation_log.toPlainText()
    assert ".bashrc" in log_text
    assert "unchanged" in log_text.lower()


@pytest.mark.gui
def test_skipped_files_logged_individually(qapp, qtbot):
    """Multiple skipped files should each appear as separate log entries."""
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel
    from gui.model import DFBUModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm)

    # Simulate skipping 3 files
    window._on_item_skipped("/home/user/.bashrc", "File unchanged")
    window._on_item_skipped("/home/user/.vimrc", "File unchanged")
    window._on_item_skipped("/home/user/.gitconfig", "File unchanged")

    log_text = window.operation_log.toPlainText()
    assert ".bashrc" in log_text
    assert ".vimrc" in log_text
    assert ".gitconfig" in log_text
```

### Step 2: Run tests to verify they fail

Run: `pytest DFBU/tests/test_skip_logging.py -v`
Expected: FAIL — current code doesn't log individual names (batches them)

### Step 3: Rewrite `_on_item_skipped()` and clean up

**Remove** the `SKIP_LOG_INTERVAL` constant (view.py:94):

```python
# DELETE this line:
SKIP_LOG_INTERVAL: Final[int] = 10  # Log every N skipped files to avoid log spam
```

**Remove** the instance variables used for batch tracking. Find where `_skipped_count` and `_last_logged_skip_count` are initialized (likely in `__init__` or `_on_start_backup`) and remove them.

**Rewrite `_on_item_skipped()`** (view.py:1108):

```python
def _on_item_skipped(self, path: str, reason: str) -> None:
    """Handle item skipped signal — log each file individually."""
    self._skipped_count += 1
    name = Path(path).name

    if self._log_verbose_btn and self._log_verbose_btn.isChecked():
        log_message = f"⊘ {name} ({reason}) [{path}]"
    else:
        log_message = f"⊘ {name} ({reason})"
    self._append_log(log_message, "skip")
```

Note: Keep `_skipped_count` for the summary in `_on_operation_finished`. The verbose integration from Task 6 is included here too (showing full path when verbose is on).

**Update `_on_operation_finished()`** (view.py:1125): Remove the "remaining skipped files" logic since we no longer batch:

```python
# Remove these lines from _on_operation_finished:
if self._skipped_count > self._last_logged_skip_count:
    remaining = self._skipped_count - self._last_logged_skip_count
    self._append_log(
        f"⊘ Skipped {remaining} unchanged files (total: {self._skipped_count})...",
        "skip",
    )
```

Replace with just a summary line:

```python
if self._skipped_count > 0:
    self._append_log(
        f"⊘ Total unchanged files: {self._skipped_count}",
        "skip",
    )
```

**Also remove `_last_logged_skip_count`** wherever it's initialized/used — it's no longer needed.

### Step 4: Run tests

Run: `pytest DFBU/tests/test_skip_logging.py -v`
Expected: PASS

### Step 5: Run full test suite

Run: `pytest DFBU/tests/ -m unit -v`
Expected: PASS

### Step 6: Run mypy

Run: `mypy DFBU/`
Expected: 0 errors

### Step 7: Commit

```bash
git add DFBU/gui/view.py DFBU/tests/test_skip_logging.py
git commit -m "feat: log each unchanged file name individually instead of batch summaries"
```

---

## Post-Implementation Checklist

After all 7 tasks are complete:

1. **Run full test suite:** `pytest DFBU/tests/ -v`
2. **Run mypy:** `mypy DFBU/`
3. **Manual smoke test:** `python DFBU/dfbu_gui.py`
   - Verify "Edit" button label on backup tab
   - Check "Hide missing" checkbox filters the table
   - Click "Edit Config" — should open editor
   - Click "Validate Config" — should show success
   - Test browse button in Add/Edit dialog — single picker, no prompt
   - Click "Export Config" — should copy files
   - Toggle "Verbose" in log pane, run a backup, check paths
   - Run a backup and verify each unchanged file name appears in log
4. **Final commit:** squash or leave as feature commits per preference
