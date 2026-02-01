# Remove Configuration Directory Choice Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove the UI elements and code that allow users to select a custom configuration directory. Configuration will always load from the fixed `DFBU/data/` directory.

**Architecture:** Remove the entire "Configuration File" section from the Backup tab UI, remove associated View/ViewModel code, and simplify startup to always use the default path. The model's `config_path` becomes read-only.

**Tech Stack:** PySide6, Qt Designer UI files (XML), Python

---

### Task 1: Remove Config Group from UI File

**Files:**
- Modify: `DFBU/gui/designer/main_window_complete.ui`

**Step 1: Remove the configGroup widget block**

In `main_window_complete.ui`, delete lines 79-205 (the entire `<item>` containing `configGroup`):

Find and delete the block starting with:
```xml
        <item>
         <widget class="QWidget" name="configGroup" native="true">
```

And ending with:
```xml
            </widget>
           </item>
          </layout>
         </widget>
        </item>
```

**Step 2: Remove actionLoadConfig from menu**

Find and delete the menu reference (around line 1779):
```xml
    <addaction name="actionLoadConfig"/>
```

**Step 3: Remove actionLoadConfig action definition**

Find and delete the action block (around line 1818-1824):
```xml
  <action name="actionLoadConfig">
   <property name="text">
    <string>&amp;Load Configuration...</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+O</string>
   </property>
  </action>
```

**Step 4: Verify UI file is valid XML**

Run: `python -c "import xml.etree.ElementTree as ET; ET.parse('DFBU/gui/designer/main_window_complete.ui'); print('Valid XML')"`
Expected: "Valid XML"

**Step 5: Commit**

```bash
git add DFBU/gui/designer/main_window_complete.ui
git commit -m "ui: remove config directory selection from Backup tab

Remove the Configuration File section (browse button, load button,
path field) since config always loads from DFBU/data/.
Also remove Load Configuration menu action (Ctrl+O)."
```

---

### Task 2: Remove View Widget References and Signal Connections

**Files:**
- Modify: `DFBU/gui/view.py`

**Step 1: Remove widget attribute declarations**

Find the docstring section listing widget attributes (around lines 422-423) and remove:
```python
        config_path_edit: Line edit for configuration file path
        load_config_btn: Button to load configuration
```

**Step 2: Remove widget finding code in _find_backup_tab_widgets**

Find and remove lines 580-586:
```python
        self.config_path_edit: QLineEdit = ui_widget.findChild(
            QLineEdit, "configGroupPathEdit"
        )  # type: ignore[assignment]
        self.load_config_btn: QPushButton = ui_widget.findChild(
            QPushButton, "configGroupLoadButton"
        )  # type: ignore[assignment]
```

**Step 3: Remove browse button connection**

Find and remove lines 734-737:
```python
        browse_config_btn: QPushButton = ui_widget.findChild(
            QPushButton, "configGroupBrowseButton"
        )  # type: ignore[assignment]
        browse_config_btn.clicked.connect(self._on_browse_config)
        self.load_config_btn.clicked.connect(self._on_load_config)
```

**Step 4: Remove menu action connection**

Find and remove lines 708 and 793:
```python
        self.action_load_config: QAction = ui_widget.findChild(
            QAction, "actionLoadConfig"
        )  # type: ignore[assignment]
```
and:
```python
        self.action_load_config.triggered.connect(self._on_browse_config)
```

**Step 5: Verify no syntax errors**

Run: `python -m py_compile DFBU/gui/view.py`
Expected: No output (success)

**Step 6: Commit**

```bash
git add DFBU/gui/view.py
git commit -m "view: remove config directory widget references and connections

Remove findChild calls and signal connections for:
- config_path_edit (QLineEdit)
- load_config_btn (QPushButton)
- browse_config_btn (QPushButton)
- action_load_config (QAction)"
```

---

### Task 3: Remove View Methods for Config Browsing/Loading

**Files:**
- Modify: `DFBU/gui/view.py`

**Step 1: Remove _on_browse_config method**

Find and delete the entire method (around lines 849-860):
```python
    def _on_browse_config(self) -> None:
        """Handle browse config directory selection."""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Configuration Directory",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly,
        )

        if dir_path:
            self.config_path_edit.setText(dir_path)
            self.viewmodel.model.config_path = Path(dir_path)
```

**Step 2: Remove _on_load_config method**

Find and delete the entire method (around lines 862-895). This is a larger method that handles the load config button click.

**Step 3: Remove config_path display in _apply_loaded_settings**

Find and remove the config path display block (around lines 840-842):
```python
        # Display config path if loaded
        if settings.get("config_path"):
            self.config_path_edit.setText(settings["config_path"])
```

**Step 4: Remove load_config_btn.setEnabled calls**

Search and remove all lines containing `self.load_config_btn.setEnabled`. There are approximately 4 occurrences at lines 909, 934, 1044, 1100.

**Step 5: Verify no syntax errors**

Run: `python -m py_compile DFBU/gui/view.py`
Expected: No output (success)

**Step 6: Commit**

```bash
git add DFBU/gui/view.py
git commit -m "view: remove config browsing and loading methods

Remove _on_browse_config() and _on_load_config() methods.
Remove config_path display logic and load_config_btn state management.
Config is now auto-loaded on startup from fixed location."
```

---

### Task 4: Remove Config Path from ViewModel Settings

**Files:**
- Modify: `DFBU/gui/viewmodel.py`

**Step 1: Remove configPath from load_settings**

In `load_settings()` method, remove lines related to config_path (around lines 1119-1137):
```python
        config_path_str: str = str(self.settings.value("configPath", ""))
```
and the validation block:
```python
        # Validate and apply loaded config path if exists
        if config_path_str:
            validation_result = InputValidator.validate_path(
                config_path_str, must_exist=True
            )
            if validation_result.success:
                config_path = Path(config_path_str)
                if config_path.exists():
                    self.model.config_path = config_path
            # Silently ignore invalid paths (settings may be from old session)
```
and remove from settings_dict:
```python
            "config_path": config_path_str,
```

**Step 2: Remove configPath from save_settings**

Remove line 1166:
```python
        self.settings.setValue("configPath", str(self.model.config_path))
```

**Step 3: Verify no syntax errors**

Run: `python -m py_compile DFBU/gui/viewmodel.py`
Expected: No output (success)

**Step 4: Commit**

```bash
git add DFBU/gui/viewmodel.py
git commit -m "viewmodel: remove config path from settings persistence

Config path is fixed to DFBU/data/, no need to save/restore it."
```

---

### Task 5: Make Model config_path Read-Only

**Files:**
- Modify: `DFBU/gui/model.py`
- Modify: `DFBU/gui/protocols.py`

**Step 1: Remove config_path setter from model.py**

Find and delete lines 152-155:
```python
    @config_path.setter
    def config_path(self, path: Path) -> None:
        """Set configuration file path."""
        self._config_manager.config_path = path
```

**Step 2: Remove config_path setter from protocols.py**

Find and delete lines 247-250:
```python
    @config_path.setter
    def config_path(self, path: Path) -> None:
        """Set configuration file path."""
        ...
```

**Step 3: Verify no syntax errors**

Run: `python -m py_compile DFBU/gui/model.py DFBU/gui/protocols.py`
Expected: No output (success)

**Step 4: Commit**

```bash
git add DFBU/gui/model.py DFBU/gui/protocols.py
git commit -m "model: make config_path read-only property

Remove setter since config directory is now fixed."
```

---

### Task 6: Simplify Application Startup

**Files:**
- Modify: `DFBU/dfbu-gui.py`

**Step 1: Simplify _load_config_if_available**

Replace the method (around lines 150-162) with simpler logic:

```python
    def _load_config_if_available(self) -> None:
        """Load configuration from default path on startup."""
        if DEFAULT_CONFIG_PATH.exists():
            self.viewmodel.command_load_config()
```

**Step 2: Verify no syntax errors**

Run: `python -m py_compile DFBU/dfbu-gui.py`
Expected: No output (success)

**Step 3: Commit**

```bash
git add DFBU/dfbu-gui.py
git commit -m "app: simplify startup config loading

Always load from DEFAULT_CONFIG_PATH, no saved path to check."
```

---

### Task 7: Update Tests

**Files:**
- Modify: `DFBU/tests/test_view_comprehensive.py`

**Step 1: Remove test_load_config_action_triggers_command test**

Find and delete the test method (around lines 361-376):
```python
    def test_load_config_action_triggers_command(self, qapp, viewmodel_with_config):
        """Test load config menu action triggers ViewModel command."""
        # ... entire test method
```

**Step 2: Run tests to verify nothing is broken**

Run: `cd /home/chris/projects/dfbu && source .venv/bin/activate && pytest DFBU/tests/ -v --tb=short 2>&1 | head -100`
Expected: All tests pass

**Step 3: Commit**

```bash
git add DFBU/tests/test_view_comprehensive.py
git commit -m "test: remove obsolete config loading test

The test tested UI elements that no longer exist."
```

---

### Task 8: Run Full Test Suite and GUI Verification

**Files:**
- None (verification only)

**Step 1: Run type checker**

Run: `cd /home/chris/projects/dfbu && source .venv/bin/activate && mypy DFBU/ --ignore-missing-imports 2>&1 | tail -20`
Expected: No errors

**Step 2: Run full test suite**

Run: `cd /home/chris/projects/dfbu && source .venv/bin/activate && pytest DFBU/tests/ -v --tb=short`
Expected: All tests pass

**Step 3: Manual GUI test**

Run: `cd /home/chris/projects/dfbu && source .venv/bin/activate && python DFBU/dfbu-gui.py`

Verify:
- Application launches
- Backup tab no longer shows "Configuration File" section
- File menu no longer has "Load Configuration..." option
- Config auto-loads on startup (check log or dotfiles table populates)

**Step 4: Final commit (if needed)**

If any fixes were needed, commit them. Otherwise, proceed.

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Remove configGroup from UI file | main_window_complete.ui |
| 2 | Remove widget references and connections | view.py |
| 3 | Remove browse/load methods | view.py |
| 4 | Remove config path from settings | viewmodel.py |
| 5 | Make config_path read-only | model.py, protocols.py |
| 6 | Simplify startup | dfbu-gui.py |
| 7 | Update tests | test_view_comprehensive.py |
| 8 | Full verification | (none) |

**Total: 8 tasks**
