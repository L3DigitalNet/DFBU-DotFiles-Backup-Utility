# DFBU v1.1.0 Feature Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement Backup Profiles, Backup Preview, and Dashboard/Statistics features for DFBU v1.1.0

**Architecture:** Extends existing MVVM architecture with three new components: ProfileManager for profile CRUD, PreviewGenerator for dry-run previews, and BackupHistoryManager for dashboard metrics. Each follows the established Protocol-based dependency injection pattern.

**Tech Stack:** Python 3.14+, PySide6, ruamel.yaml, pytest/pytest-qt

---

## Phase 1: Backup Profiles

### Task 1.1: Add ProfileDict TypedDict

**Files:**

- Modify: `DFBU/core/common_types.py:317` (append after SizeReportDict)
- Test: `DFBU/tests/test_common_types.py` (create)

**Step 1: Write the failing test**

Create `DFBU/tests/test_common_types.py`:

```python
"""Tests for common_types module."""

import pytest
from core.common_types import ProfileDict


@pytest.mark.unit
def test_profile_dict_has_required_fields() -> None:
    """ProfileDict should have all required fields."""
    profile: ProfileDict = {
        "name": "Work Profile",
        "description": "Work-related dotfiles",
        "excluded": ["Steam", "Firefox"],
        "options_overrides": {"archive": True},
        "created_at": "2026-02-05T10:00:00Z",
        "modified_at": "2026-02-05T10:00:00Z",
    }
    assert profile["name"] == "Work Profile"
    assert profile["excluded"] == ["Steam", "Firefox"]
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_common_types.py::test_profile_dict_has_required_fields -v`
Expected: FAIL with "cannot import name 'ProfileDict'"

**Step 3: Write minimal implementation**

Add to `DFBU/core/common_types.py` after line 316:

```python
# =============================================================================
# Profile Types (v1.1.0)
# =============================================================================


class ProfileDict(TypedDict):
    """
    Type definition for backup profile configuration.

    Contains named preset for different backup configurations.

    Fields:
        name: Display name for the profile
        description: Human-readable description
        excluded: List of application names to exclude
        options_overrides: Partial OptionsDict with overridden settings
        created_at: ISO format timestamp of creation
        modified_at: ISO format timestamp of last modification
    """

    name: str
    description: str
    excluded: list[str]
    options_overrides: dict[str, bool | int | str]
    created_at: str
    modified_at: str
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_common_types.py::test_profile_dict_has_required_fields -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/core/common_types.py DFBU/tests/test_common_types.py
git commit -m "$(cat <<'EOF'
feat(types): add ProfileDict for backup profiles

Adds TypedDict for backup profile configuration supporting named
presets with exclusions and option overrides.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 1.2: Create ProfileManager class skeleton

**Files:**

- Create: `DFBU/gui/profile_manager.py`
- Test: `DFBU/tests/test_profile_manager.py` (create)

**Step 1: Write the failing test**

Create `DFBU/tests/test_profile_manager.py`:

```python
"""Tests for ProfileManager component."""

from pathlib import Path

import pytest

from gui.profile_manager import ProfileManager


@pytest.mark.unit
def test_profile_manager_initialization(tmp_path: Path) -> None:
    """ProfileManager should initialize with empty profiles."""
    manager = ProfileManager(config_path=tmp_path)
    assert manager.get_profile_count() == 0
    assert manager.get_active_profile_name() is None
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_profile_manager.py::test_profile_manager_initialization -v`
Expected: FAIL with "No module named 'gui.profile_manager'"

**Step 3: Write minimal implementation**

Create `DFBU/gui/profile_manager.py`:

```python
"""
DFBU ProfileManager - Backup Profile Management Component

Description:
    Handles named backup profiles allowing users to save and switch
    between different dotfile selection and option configurations.

Author: Chris Purcell
Date Created: 2026-02-05
License: MIT
"""

from pathlib import Path

from core.common_types import ProfileDict


class ProfileManager:
    """
    Manages backup profiles for different configurations.

    Profiles allow users to save named presets of excluded dotfiles
    and option overrides for quick switching between backup configurations.

    Attributes:
        config_path: Path to configuration directory
        _profiles: Dictionary of profile name -> ProfileDict
        _active_profile: Name of currently active profile (None = default)
    """

    def __init__(self, config_path: Path) -> None:
        """
        Initialize ProfileManager.

        Args:
            config_path: Path to configuration directory for profiles.yaml
        """
        self.config_path: Path = config_path
        self._profiles: dict[str, ProfileDict] = {}
        self._active_profile: str | None = None

    def get_profile_count(self) -> int:
        """
        Get number of saved profiles.

        Returns:
            Number of profiles in storage
        """
        return len(self._profiles)

    def get_active_profile_name(self) -> str | None:
        """
        Get name of currently active profile.

        Returns:
            Active profile name, or None if using default settings
        """
        return self._active_profile
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_profile_manager.py::test_profile_manager_initialization -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/gui/profile_manager.py DFBU/tests/test_profile_manager.py
git commit -m "$(cat <<'EOF'
feat(profiles): add ProfileManager skeleton

Creates ProfileManager class with initialization and basic accessors.
Foundation for backup profile management system.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 1.3: Implement profile YAML persistence

**Files:**

- Modify: `DFBU/gui/profile_manager.py`
- Test: `DFBU/tests/test_profile_manager.py`

**Step 1: Write the failing test**

Add to `DFBU/tests/test_profile_manager.py`:

```python
@pytest.mark.unit
def test_profile_manager_load_profiles(tmp_path: Path) -> None:
    """ProfileManager should load profiles from YAML file."""
    # Create profiles.yaml
    profiles_file = tmp_path / "profiles.yaml"
    profiles_file.write_text("""
Work:
  description: Work configuration
  excluded: [Steam, Firefox]
  options_overrides:
    archive: true
  created_at: "2026-02-05T10:00:00Z"
  modified_at: "2026-02-05T10:00:00Z"

active_profile: Work
""")

    manager = ProfileManager(config_path=tmp_path)
    success, error = manager.load_profiles()

    assert success is True
    assert error == ""
    assert manager.get_profile_count() == 1
    assert manager.get_active_profile_name() == "Work"
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_profile_manager.py::test_profile_manager_load_profiles -v`
Expected: FAIL with "ProfileManager has no attribute 'load_profiles'"

**Step 3: Write minimal implementation**

Add to `DFBU/gui/profile_manager.py`:

```python
from datetime import UTC, datetime

from ruamel.yaml import YAML


class ProfileManager:
    # ... existing __init__ and methods ...

    def load_profiles(self) -> tuple[bool, str]:
        """
        Load profiles from YAML configuration file.

        Returns:
            Tuple of (success, error_message)
        """
        profiles_file = self.config_path / "profiles.yaml"

        if not profiles_file.exists():
            # No profiles file is valid - just means no saved profiles
            return True, ""

        try:
            yaml = YAML()
            yaml.preserve_quotes = True

            with profiles_file.open("r", encoding="utf-8") as f:
                data = yaml.load(f)

            if data is None:
                return True, ""

            # Extract active profile setting
            self._active_profile = data.pop("active_profile", None)

            # Remaining keys are profile names
            for name, profile_data in data.items():
                if isinstance(profile_data, dict):
                    self._profiles[name] = ProfileDict(
                        name=name,
                        description=profile_data.get("description", ""),
                        excluded=profile_data.get("excluded", []),
                        options_overrides=profile_data.get("options_overrides", {}),
                        created_at=profile_data.get("created_at", ""),
                        modified_at=profile_data.get("modified_at", ""),
                    )

            return True, ""

        except Exception as e:
            return False, f"Failed to load profiles: {e}"

    def save_profiles(self) -> tuple[bool, str]:
        """
        Save profiles to YAML configuration file.

        Returns:
            Tuple of (success, error_message)
        """
        profiles_file = self.config_path / "profiles.yaml"

        try:
            yaml = YAML()
            yaml.preserve_quotes = True
            yaml.default_flow_style = False

            # Build data structure
            data: dict[str, Any] = {}

            for name, profile in self._profiles.items():
                data[name] = {
                    "description": profile["description"],
                    "excluded": profile["excluded"],
                    "options_overrides": profile["options_overrides"],
                    "created_at": profile["created_at"],
                    "modified_at": profile["modified_at"],
                }

            if self._active_profile:
                data["active_profile"] = self._active_profile

            with profiles_file.open("w", encoding="utf-8") as f:
                yaml.dump(data, f)

            return True, ""

        except Exception as e:
            return False, f"Failed to save profiles: {e}"
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_profile_manager.py::test_profile_manager_load_profiles -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/gui/profile_manager.py DFBU/tests/test_profile_manager.py
git commit -m "$(cat <<'EOF'
feat(profiles): implement profile YAML persistence

Adds load_profiles and save_profiles methods for reading/writing
profiles to profiles.yaml file using ruamel.yaml.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 1.4: Implement profile CRUD operations

**Files:**

- Modify: `DFBU/gui/profile_manager.py`
- Test: `DFBU/tests/test_profile_manager.py`

**Step 1: Write the failing tests**

Add to `DFBU/tests/test_profile_manager.py`:

```python
@pytest.mark.unit
def test_profile_manager_create_profile(tmp_path: Path) -> None:
    """ProfileManager should create new profiles."""
    manager = ProfileManager(config_path=tmp_path)

    success = manager.create_profile(
        name="Gaming",
        description="Gaming related configs",
        excluded=["Work Apps"],
    )

    assert success is True
    assert manager.get_profile_count() == 1
    profile = manager.get_profile("Gaming")
    assert profile is not None
    assert profile["description"] == "Gaming related configs"


@pytest.mark.unit
def test_profile_manager_delete_profile(tmp_path: Path) -> None:
    """ProfileManager should delete profiles."""
    manager = ProfileManager(config_path=tmp_path)
    manager.create_profile("ToDelete", "Test", [])

    success = manager.delete_profile("ToDelete")

    assert success is True
    assert manager.get_profile_count() == 0


@pytest.mark.unit
def test_profile_manager_switch_profile(tmp_path: Path) -> None:
    """ProfileManager should switch active profile."""
    manager = ProfileManager(config_path=tmp_path)
    manager.create_profile("Profile1", "First", [])
    manager.create_profile("Profile2", "Second", ["App1"])

    success = manager.switch_profile("Profile2")

    assert success is True
    assert manager.get_active_profile_name() == "Profile2"
    assert manager.get_active_exclusions() == ["App1"]
```

**Step 2: Run tests to verify they fail**

Run: `pytest DFBU/tests/test_profile_manager.py -k "create or delete or switch" -v`
Expected: FAIL with "ProfileManager has no attribute 'create_profile'"

**Step 3: Write minimal implementation**

Add to `DFBU/gui/profile_manager.py`:

```python
from typing import Any


class ProfileManager:
    # ... existing methods ...

    def create_profile(
        self,
        name: str,
        description: str,
        excluded: list[str],
        options_overrides: dict[str, bool | int | str] | None = None,
    ) -> bool:
        """
        Create a new backup profile.

        Args:
            name: Unique profile name
            description: Human-readable description
            excluded: List of application names to exclude
            options_overrides: Optional settings overrides

        Returns:
            True if profile was created successfully
        """
        if name in self._profiles:
            return False  # Profile already exists

        now = datetime.now(UTC).isoformat()
        self._profiles[name] = ProfileDict(
            name=name,
            description=description,
            excluded=excluded,
            options_overrides=options_overrides or {},
            created_at=now,
            modified_at=now,
        )
        return True

    def get_profile(self, name: str) -> ProfileDict | None:
        """
        Get profile by name.

        Args:
            name: Profile name to retrieve

        Returns:
            ProfileDict or None if not found
        """
        return self._profiles.get(name)

    def delete_profile(self, name: str) -> bool:
        """
        Delete a profile by name.

        Args:
            name: Profile name to delete

        Returns:
            True if profile was deleted
        """
        if name not in self._profiles:
            return False

        del self._profiles[name]

        # Clear active if deleted
        if self._active_profile == name:
            self._active_profile = None

        return True

    def switch_profile(self, name: str | None) -> bool:
        """
        Switch to a different profile.

        Args:
            name: Profile name to switch to, or None for default

        Returns:
            True if switch was successful
        """
        if name is not None and name not in self._profiles:
            return False

        self._active_profile = name
        return True

    def get_active_exclusions(self) -> list[str]:
        """
        Get exclusions from active profile.

        Returns:
            List of excluded application names, empty if no active profile
        """
        if self._active_profile is None:
            return []

        profile = self._profiles.get(self._active_profile)
        if profile is None:
            return []

        return profile["excluded"]

    def get_profile_names(self) -> list[str]:
        """
        Get list of all profile names.

        Returns:
            Sorted list of profile names
        """
        return sorted(self._profiles.keys())
```

**Step 4: Run tests to verify they pass**

Run: `pytest DFBU/tests/test_profile_manager.py -k "create or delete or switch" -v`
Expected: PASS (3 tests)

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/gui/profile_manager.py DFBU/tests/test_profile_manager.py
git commit -m "$(cat <<'EOF'
feat(profiles): implement profile CRUD operations

Adds create_profile, get_profile, delete_profile, switch_profile,
get_active_exclusions, and get_profile_names methods.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 1.5: Integrate ProfileManager with Model facade

**Files:**

- Modify: `DFBU/gui/model.py`
- Test: `DFBU/tests/test_model.py`

**Step 1: Write the failing test**

Add to `DFBU/tests/test_model.py` (or create if doesn't exist):

```python
"""Tests for DFBUModel facade."""

from pathlib import Path

import pytest

from gui.model import DFBUModel


@pytest.fixture
def model_with_profiles(yaml_config_dir: Path) -> DFBUModel:
    """Create DFBUModel with profiles support."""
    model = DFBUModel(yaml_config_dir)
    model.load_config()
    return model


@pytest.mark.unit
def test_model_exposes_profile_operations(model_with_profiles: DFBUModel) -> None:
    """DFBUModel should expose profile operations."""
    model = model_with_profiles

    # Create profile through facade
    success = model.create_profile("TestProfile", "Test", ["TestApp"])
    assert success is True

    # Get profile count
    assert model.get_profile_count() == 1

    # Switch profile
    success = model.switch_profile("TestProfile")
    assert success is True
    assert model.get_active_profile_name() == "TestProfile"
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_model.py::test_model_exposes_profile_operations -v`
Expected: FAIL with "DFBUModel has no attribute 'create_profile'"

**Step 3: Write minimal implementation**

Add to `DFBU/gui/model.py` imports:

```python
from gui.profile_manager import ProfileManager
```

Add to `DFBUModel.__init__`:

```python
        # Initialize ProfileManager (v1.1.0)
        self._profile_manager: ProfileManager = ProfileManager(config_path)
```

Add to `DFBUModel.load_config` after success check:

```python
            # Load profiles (v1.1.0)
            self._profile_manager.load_profiles()
```

Add new methods to `DFBUModel`:

```python
    # =========================================================================
    # Profile Management (v1.1.0)
    # =========================================================================

    def get_profile_count(self) -> int:
        """Get number of saved profiles."""
        return self._profile_manager.get_profile_count()

    def get_profile_names(self) -> list[str]:
        """Get list of all profile names."""
        return self._profile_manager.get_profile_names()

    def get_active_profile_name(self) -> str | None:
        """Get name of currently active profile."""
        return self._profile_manager.get_active_profile_name()

    def create_profile(
        self,
        name: str,
        description: str,
        excluded: list[str],
        options_overrides: dict[str, bool | int | str] | None = None,
    ) -> bool:
        """Create a new backup profile."""
        success = self._profile_manager.create_profile(
            name, description, excluded, options_overrides
        )
        if success:
            self._profile_manager.save_profiles()
        return success

    def delete_profile(self, name: str) -> bool:
        """Delete a profile by name."""
        success = self._profile_manager.delete_profile(name)
        if success:
            self._profile_manager.save_profiles()
        return success

    def switch_profile(self, name: str | None) -> bool:
        """Switch to a different profile."""
        success = self._profile_manager.switch_profile(name)
        if success:
            self._profile_manager.save_profiles()
        return success

    def get_profile_manager(self) -> ProfileManager:
        """Get ProfileManager instance for advanced operations."""
        return self._profile_manager
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_model.py::test_model_exposes_profile_operations -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/gui/model.py DFBU/tests/test_model.py
git commit -m "$(cat <<'EOF'
feat(model): integrate ProfileManager with facade

Exposes profile operations through DFBUModel facade:
create_profile, delete_profile, switch_profile, get_profile_count,
get_profile_names, get_active_profile_name.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 1.6: Add profile signals to ViewModel

**Files:**

- Modify: `DFBU/gui/viewmodel.py`
- Test: `DFBU/tests/test_viewmodel.py`

**Step 1: Write the failing test**

Add to `DFBU/tests/test_viewmodel.py`:

```python
@pytest.mark.gui
def test_viewmodel_profile_signals(
    qapp: QApplication, qtbot: Any, yaml_config_dir: Path
) -> None:
    """ViewModel should emit profile signals."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    model = DFBUModel(yaml_config_dir)
    model.load_config()
    vm = DFBUViewModel(model)

    # Test profile_switched signal
    with qtbot.waitSignal(vm.profile_switched, timeout=1000):
        vm.command_create_profile("TestProfile", "Test", [])
        vm.command_switch_profile("TestProfile")
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_viewmodel.py::test_viewmodel_profile_signals -v`
Expected: FAIL with "DFBUViewModel has no attribute 'profile_switched'"

**Step 3: Write minimal implementation**

Add signals to `DFBUViewModel` class:

```python
    # Profile signals (v1.1.0)
    profile_switched = Signal(str)  # profile_name (empty string for default)
    profiles_changed = Signal()  # emitted when profile list changes
```

Add commands to `DFBUViewModel`:

```python
    def command_create_profile(
        self,
        name: str,
        description: str,
        excluded: list[str],
        options_overrides: dict[str, bool | int | str] | None = None,
    ) -> bool:
        """
        Command to create a new backup profile.

        Args:
            name: Unique profile name
            description: Human-readable description
            excluded: List of application names to exclude
            options_overrides: Optional settings overrides

        Returns:
            True if profile was created successfully
        """
        success = self.model.create_profile(name, description, excluded, options_overrides)
        if success:
            self.profiles_changed.emit()
        return success

    def command_delete_profile(self, name: str) -> bool:
        """
        Command to delete a profile.

        Args:
            name: Profile name to delete

        Returns:
            True if profile was deleted
        """
        success = self.model.delete_profile(name)
        if success:
            self.profiles_changed.emit()
        return success

    def command_switch_profile(self, name: str | None) -> bool:
        """
        Command to switch active profile.

        Args:
            name: Profile name to switch to, or None for default

        Returns:
            True if switch was successful
        """
        success = self.model.switch_profile(name)
        if success:
            profile_name = name if name else ""
            self.profile_switched.emit(profile_name)
            self.exclusions_changed.emit()  # Profile switch changes exclusions
        return success

    def get_profile_names(self) -> list[str]:
        """Get list of all profile names."""
        return self.model.get_profile_names()

    def get_active_profile_name(self) -> str | None:
        """Get name of currently active profile."""
        return self.model.get_active_profile_name()
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_viewmodel.py::test_viewmodel_profile_signals -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/gui/viewmodel.py DFBU/tests/test_viewmodel.py
git commit -m "$(cat <<'EOF'
feat(viewmodel): add profile signals and commands

Adds profile_switched and profiles_changed signals.
Implements command_create_profile, command_delete_profile,
command_switch_profile commands.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 1.7: Create profile_dialog.ui in Qt Designer

**Files:**

- Create: `DFBU/gui/designer/profile_dialog.ui`

**Step 1: Create the UI file**

Create `DFBU/gui/designer/profile_dialog.ui`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>ProfileDialog</class>
 <widget class="QDialog" name="ProfileDialog">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>500</width>
    <height>400</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Manage Backup Profiles</string>
  </property>
  <layout class="QVBoxLayout" name="mainLayout">
   <item>
    <widget class="QListWidget" name="profileList">
     <property name="objectName">
      <string>profileList</string>
     </property>
    </widget>
   </item>
   <item>
    <layout class="QHBoxLayout" name="buttonLayout">
     <item>
      <widget class="QPushButton" name="btnNewProfile">
       <property name="objectName">
        <string>btnNewProfile</string>
       </property>
       <property name="text">
        <string>New Profile</string>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QPushButton" name="btnEditProfile">
       <property name="objectName">
        <string>btnEditProfile</string>
       </property>
       <property name="text">
        <string>Edit</string>
       </property>
       <property name="enabled">
        <bool>false</bool>
       </property>
      </widget>
     </item>
     <item>
      <widget class="QPushButton" name="btnDeleteProfile">
       <property name="objectName">
        <string>btnDeleteProfile</string>
       </property>
       <property name="text">
        <string>Delete</string>
       </property>
       <property name="enabled">
        <bool>false</bool>
       </property>
      </widget>
     </item>
     <item>
      <spacer name="horizontalSpacer">
       <property name="orientation">
        <enum>Qt::Horizontal</enum>
       </property>
      </spacer>
     </item>
    </layout>
   </item>
   <item>
    <widget class="QDialogButtonBox" name="buttonBox">
     <property name="objectName">
      <string>buttonBox</string>
     </property>
     <property name="standardButtons">
      <set>QDialogButtonBox::Close</set>
     </property>
    </widget>
   </item>
  </layout>
 </widget>
</ui>
```

**Step 2: Verify UI file loads**

Run: `python -c "from PySide6.QtUiTools import QUiLoader; from PySide6.QtWidgets import QApplication; app = QApplication([]); loader = QUiLoader(); f = open('DFBU/gui/designer/profile_dialog.ui'); loader.load(f); print('UI loads successfully')"`
Expected: "UI loads successfully"

**Step 3: Commit**

```bash
git add DFBU/gui/designer/profile_dialog.ui
git commit -m "$(cat <<'EOF'
feat(ui): create profile_dialog.ui for profile management

Adds Qt Designer UI file for profile management dialog with:
- Profile list widget
- New/Edit/Delete buttons
- Standard dialog button box

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 1.8: Implement ProfileDialog view class

**Files:**

- Create: `DFBU/gui/profile_dialog.py`
- Test: `DFBU/tests/test_profile_dialog.py`

**Step 1: Write the failing test**

Create `DFBU/tests/test_profile_dialog.py`:

```python
"""Tests for ProfileDialog view component."""

from pathlib import Path
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
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_profile_dialog.py::test_profile_dialog_displays_profiles -v`
Expected: FAIL with "No module named 'gui.profile_dialog'"

**Step 3: Write minimal implementation**

Create `DFBU/gui/profile_dialog.py`:

```python
"""
DFBU ProfileDialog - Profile Management Dialog

Description:
    Dialog for managing backup profiles including creating,
    editing, and deleting named backup configurations.

Author: Chris Purcell
Date Created: 2026-02-05
License: MIT
"""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QWidget,
)

from gui.viewmodel import DFBUViewModel


class ProfileDialog(QDialog):
    """
    Dialog for managing backup profiles.

    Allows users to create, edit, delete, and view backup profiles.
    Uses Qt Designer UI file for layout.
    """

    def __init__(
        self, viewmodel: DFBUViewModel, parent: QWidget | None = None
    ) -> None:
        """
        Initialize ProfileDialog.

        Args:
            viewmodel: DFBUViewModel instance
            parent: Parent widget
        """
        super().__init__(parent)
        self._viewmodel = viewmodel

        # Load UI from designer file
        self._load_ui()

        # Find widgets
        self._find_widgets()

        # Connect signals
        self._connect_signals()

        # Populate profile list
        self._refresh_profile_list()

    def _load_ui(self) -> None:
        """Load UI from Qt Designer file."""
        ui_path = Path(__file__).parent / "designer" / "profile_dialog.ui"
        loader = QUiLoader()

        with ui_path.open("r") as f:
            self._ui = loader.load(f, self)

        # Set dialog layout from loaded UI
        if self._ui:
            self.setWindowTitle(self._ui.windowTitle())
            self.setMinimumSize(self._ui.minimumSize())
            self.resize(self._ui.size())

    def _find_widgets(self) -> None:
        """Find and store references to UI widgets."""
        self.profile_list: QListWidget = self._ui.findChild(QListWidget, "profileList")
        self.btn_new: QPushButton = self._ui.findChild(QPushButton, "btnNewProfile")
        self.btn_edit: QPushButton = self._ui.findChild(QPushButton, "btnEditProfile")
        self.btn_delete: QPushButton = self._ui.findChild(QPushButton, "btnDeleteProfile")
        self.button_box: QDialogButtonBox = self._ui.findChild(
            QDialogButtonBox, "buttonBox"
        )

    def _connect_signals(self) -> None:
        """Connect widget signals to slots."""
        self.profile_list.currentItemChanged.connect(self._on_selection_changed)
        self.btn_new.clicked.connect(self._on_new_profile)
        self.btn_delete.clicked.connect(self._on_delete_profile)
        self.button_box.rejected.connect(self.reject)

    def _refresh_profile_list(self) -> None:
        """Refresh the profile list from ViewModel."""
        self.profile_list.clear()
        for name in self._viewmodel.get_profile_names():
            item = QListWidgetItem(name)
            self.profile_list.addItem(item)

    def _on_selection_changed(self, current: QListWidgetItem | None) -> None:
        """Handle profile selection change."""
        has_selection = current is not None
        self.btn_edit.setEnabled(has_selection)
        self.btn_delete.setEnabled(has_selection)

    def _on_new_profile(self) -> None:
        """Handle new profile button click."""
        # TODO: Show profile editor dialog
        pass

    def _on_delete_profile(self) -> None:
        """Handle delete profile button click."""
        current = self.profile_list.currentItem()
        if current:
            name = current.text()
            self._viewmodel.command_delete_profile(name)
            self._refresh_profile_list()
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_profile_dialog.py::test_profile_dialog_displays_profiles -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/gui/profile_dialog.py DFBU/tests/test_profile_dialog.py
git commit -m "$(cat <<'EOF'
feat(ui): implement ProfileDialog view class

Creates ProfileDialog with UI loading from designer file,
profile list display, and delete functionality.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Phase 2: Backup Preview/Dry Run

### Task 2.1: Add Preview TypedDicts

**Files:**

- Modify: `DFBU/core/common_types.py`
- Test: `DFBU/tests/test_common_types.py`

**Step 1: Write the failing test**

Add to `DFBU/tests/test_common_types.py`:

```python
from core.common_types import PreviewItemDict, BackupPreviewDict


@pytest.mark.unit
def test_preview_item_dict_structure() -> None:
    """PreviewItemDict should have all required fields."""
    item: PreviewItemDict = {
        "path": "/home/user/.bashrc",
        "dest_path": "/backups/mirror/.bashrc",
        "size_bytes": 1024,
        "status": "new",
        "application": "Bash",
    }
    assert item["status"] == "new"


@pytest.mark.unit
def test_backup_preview_dict_structure() -> None:
    """BackupPreviewDict should have all required fields."""
    preview: BackupPreviewDict = {
        "items": [],
        "total_size_bytes": 0,
        "new_count": 0,
        "changed_count": 0,
        "unchanged_count": 0,
        "error_count": 0,
    }
    assert preview["total_size_bytes"] == 0
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_common_types.py -k "preview" -v`
Expected: FAIL with "cannot import name 'PreviewItemDict'"

**Step 3: Write minimal implementation**

Add to `DFBU/core/common_types.py`:

```python
# =============================================================================
# Backup Preview Types (v1.1.0)
# =============================================================================


class PreviewItemDict(TypedDict):
    """
    Type definition for individual backup preview item.

    Contains information about a single file/directory in preview.

    Fields:
        path: Source path of the file
        dest_path: Destination path in backup
        size_bytes: Size in bytes
        status: Preview status ("new", "changed", "unchanged", "error")
        application: Name of the dotfile application
    """

    path: str
    dest_path: str
    size_bytes: int
    status: str  # "new", "changed", "unchanged", "error"
    application: str


class BackupPreviewDict(TypedDict):
    """
    Type definition for backup preview result.

    Contains summary and details of what would be backed up.

    Fields:
        items: List of individual preview items
        total_size_bytes: Total size of all items
        new_count: Number of new files
        changed_count: Number of changed files
        unchanged_count: Number of unchanged files
        error_count: Number of files with errors
    """

    items: list[PreviewItemDict]
    total_size_bytes: int
    new_count: int
    changed_count: int
    unchanged_count: int
    error_count: int
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_common_types.py -k "preview" -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/core/common_types.py DFBU/tests/test_common_types.py
git commit -m "$(cat <<'EOF'
feat(types): add PreviewItemDict and BackupPreviewDict

Adds TypedDicts for backup preview/dry-run feature showing
what files would be backed up with status indicators.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2.2: Create PreviewGenerator service

**Files:**

- Create: `DFBU/gui/preview_generator.py`
- Test: `DFBU/tests/test_preview_generator.py`

**Step 1: Write the failing test**

Create `DFBU/tests/test_preview_generator.py`:

```python
"""Tests for PreviewGenerator service."""

from pathlib import Path

import pytest

from gui.preview_generator import PreviewGenerator
from gui.file_operations import FileOperations


@pytest.fixture
def file_ops() -> FileOperations:
    """Create FileOperations instance."""
    return FileOperations(hostname="testhost")


@pytest.fixture
def preview_gen(file_ops: FileOperations, tmp_path: Path) -> PreviewGenerator:
    """Create PreviewGenerator instance."""
    return PreviewGenerator(
        file_ops=file_ops,
        mirror_base_dir=tmp_path / "mirror",
    )


@pytest.mark.unit
def test_preview_generator_detects_new_file(
    preview_gen: PreviewGenerator, tmp_path: Path
) -> None:
    """PreviewGenerator should detect new files."""
    # Create source file
    source = tmp_path / "source" / ".bashrc"
    source.parent.mkdir(parents=True)
    source.write_text("# Bash config")

    dotfiles = [
        {
            "application": "Bash",
            "paths": [str(source)],
            "enabled": True,
        }
    ]

    preview = preview_gen.generate_preview(
        dotfiles=dotfiles,
        hostname_subdir=True,
        date_subdir=False,
    )

    assert preview["new_count"] == 1
    assert preview["changed_count"] == 0
    assert len(preview["items"]) == 1
    assert preview["items"][0]["status"] == "new"
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_preview_generator.py::test_preview_generator_detects_new_file -v`
Expected: FAIL with "No module named 'gui.preview_generator'"

**Step 3: Write minimal implementation**

Create `DFBU/gui/preview_generator.py`:

```python
"""
DFBU PreviewGenerator - Backup Preview Service

Description:
    Generates preview of what would be backed up without actually
    performing the backup. Shows new, changed, and unchanged files.

Author: Chris Purcell
Date Created: 2026-02-05
License: MIT
"""

from pathlib import Path
from typing import Any

from core.common_types import BackupPreviewDict, PreviewItemDict
from gui.file_operations import FileOperations


class PreviewGenerator:
    """
    Generates backup preview without performing actual backup.

    Analyzes source files and compares with existing backup to
    determine what would be copied (new/changed) or skipped (unchanged).
    """

    def __init__(
        self,
        file_ops: FileOperations,
        mirror_base_dir: Path,
    ) -> None:
        """
        Initialize PreviewGenerator.

        Args:
            file_ops: FileOperations instance for file comparison
            mirror_base_dir: Base directory for mirror backups
        """
        self._file_ops = file_ops
        self._mirror_base_dir = mirror_base_dir

    def generate_preview(
        self,
        dotfiles: list[dict[str, Any]],
        hostname_subdir: bool,
        date_subdir: bool,
        progress_callback: Any | None = None,
    ) -> BackupPreviewDict:
        """
        Generate preview of backup operation.

        Args:
            dotfiles: List of dotfile configurations
            hostname_subdir: Whether to use hostname subdirectory
            date_subdir: Whether to use date subdirectory
            progress_callback: Optional callback for progress (0-100)

        Returns:
            BackupPreviewDict with preview results
        """
        items: list[PreviewItemDict] = []
        total_size = 0
        new_count = 0
        changed_count = 0
        unchanged_count = 0
        error_count = 0

        # Count total paths for progress
        total_paths = sum(
            len(df.get("paths", []))
            for df in dotfiles
            if df.get("enabled", True)
        )
        processed = 0

        for dotfile in dotfiles:
            if not dotfile.get("enabled", True):
                continue

            app_name = dotfile.get("application", "Unknown")

            for path_str in dotfile.get("paths", []):
                if not path_str:
                    continue

                src_path = self._file_ops.expand_path(path_str)

                # Check if source exists
                if not src_path.exists():
                    processed += 1
                    continue

                # Generate destination path
                dest_path = self._file_ops.assemble_dest_path(
                    self._mirror_base_dir,
                    src_path,
                    hostname_subdir,
                    date_subdir,
                )

                # Process files
                if src_path.is_file():
                    item = self._preview_file(src_path, dest_path, app_name)
                    items.append(item)
                    total_size += item["size_bytes"]

                    if item["status"] == "new":
                        new_count += 1
                    elif item["status"] == "changed":
                        changed_count += 1
                    elif item["status"] == "unchanged":
                        unchanged_count += 1
                    else:
                        error_count += 1

                elif src_path.is_dir():
                    # Process directory recursively
                    for file_path in src_path.rglob("*"):
                        if file_path.is_file():
                            rel_path = file_path.relative_to(src_path)
                            file_dest = dest_path / rel_path

                            item = self._preview_file(file_path, file_dest, app_name)
                            items.append(item)
                            total_size += item["size_bytes"]

                            if item["status"] == "new":
                                new_count += 1
                            elif item["status"] == "changed":
                                changed_count += 1
                            elif item["status"] == "unchanged":
                                unchanged_count += 1
                            else:
                                error_count += 1

                processed += 1
                if progress_callback and total_paths > 0:
                    progress_callback(int((processed / total_paths) * 100))

        return BackupPreviewDict(
            items=items,
            total_size_bytes=total_size,
            new_count=new_count,
            changed_count=changed_count,
            unchanged_count=unchanged_count,
            error_count=error_count,
        )

    def _preview_file(
        self, src_path: Path, dest_path: Path, app_name: str
    ) -> PreviewItemDict:
        """
        Preview a single file.

        Args:
            src_path: Source file path
            dest_path: Destination file path
            app_name: Application name for the dotfile

        Returns:
            PreviewItemDict with file preview info
        """
        try:
            size = src_path.stat().st_size

            if not dest_path.exists():
                status = "new"
            elif self._file_ops.files_are_identical(src_path, dest_path):
                status = "unchanged"
            else:
                status = "changed"

            return PreviewItemDict(
                path=str(src_path),
                dest_path=str(dest_path),
                size_bytes=size,
                status=status,
                application=app_name,
            )

        except (OSError, PermissionError) as e:
            return PreviewItemDict(
                path=str(src_path),
                dest_path=str(dest_path),
                size_bytes=0,
                status="error",
                application=app_name,
            )
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_preview_generator.py::test_preview_generator_detects_new_file -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/gui/preview_generator.py DFBU/tests/test_preview_generator.py
git commit -m "$(cat <<'EOF'
feat(preview): create PreviewGenerator service

Implements backup preview generation showing which files would be
backed up as new, changed, or unchanged without performing backup.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 2.3: Add preview to Model and ViewModel

**Files:**

- Modify: `DFBU/gui/model.py`
- Modify: `DFBU/gui/viewmodel.py`
- Test: `DFBU/tests/test_viewmodel.py`

**Step 1: Write the failing test**

Add to `DFBU/tests/test_viewmodel.py`:

```python
@pytest.mark.gui
def test_viewmodel_preview_signal(
    qapp: QApplication, qtbot: Any, yaml_config_dir: Path, tmp_path: Path
) -> None:
    """ViewModel should emit preview_ready signal."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    model = DFBUModel(yaml_config_dir)
    model.load_config()
    vm = DFBUViewModel(model)

    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Add dotfile pointing to test file
    model.add_dotfile("Test", "TestApp", "Test file", [str(test_file)], True)

    # Test preview_ready signal
    with qtbot.waitSignal(vm.preview_ready, timeout=5000):
        vm.command_generate_preview()
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_viewmodel.py::test_viewmodel_preview_signal -v`
Expected: FAIL with "DFBUViewModel has no attribute 'preview_ready'"

**Step 3: Write minimal implementation**

Add to `DFBU/gui/model.py`:

```python
from gui.preview_generator import PreviewGenerator
from core.common_types import BackupPreviewDict


class DFBUModel:
    def __init__(self, config_path: Path) -> None:
        # ... existing code ...

        # Initialize PreviewGenerator (v1.1.0)
        self._preview_generator: PreviewGenerator | None = None

    def _init_preview_generator(self) -> None:
        """Lazy initialize PreviewGenerator after config is loaded."""
        if self._preview_generator is None:
            self._preview_generator = PreviewGenerator(
                file_ops=self._file_ops,
                mirror_base_dir=self._config_manager.mirror_base_dir,
            )

    def generate_backup_preview(
        self,
        progress_callback: Callable[[int], None] | None = None,
    ) -> BackupPreviewDict:
        """
        Generate preview of what would be backed up.

        Args:
            progress_callback: Optional callback for progress (0-100)

        Returns:
            BackupPreviewDict with preview results
        """
        self._init_preview_generator()

        # Get enabled dotfiles
        dotfiles = [df for df in self.dotfiles if df.get("enabled", True)]

        return self._preview_generator.generate_preview(
            dotfiles=dotfiles,
            hostname_subdir=self.options["hostname_subdir"],
            date_subdir=self.options["date_subdir"],
            progress_callback=progress_callback,
        )
```

Add to `DFBU/gui/viewmodel.py`:

```python
from core.common_types import BackupPreviewDict


class PreviewWorker(QThread):
    """Worker thread for generating backup preview."""

    progress_updated = Signal(int)
    preview_finished = Signal(object)  # BackupPreviewDict
    error_occurred = Signal(str, str)

    def __init__(self) -> None:
        super().__init__()
        self.model: DFBUModel | None = None

    def set_model(self, model: DFBUModel) -> None:
        self.model = model

    def run(self) -> None:
        if not self.model:
            return

        try:
            preview = self.model.generate_backup_preview(
                progress_callback=lambda p: self.progress_updated.emit(p)
            )
            self.preview_finished.emit(preview)
        except Exception as e:
            self.error_occurred.emit("Preview", str(e))


class DFBUViewModel(QObject):
    # Add signals
    preview_ready = Signal(object)  # BackupPreviewDict
    preview_progress = Signal(int)

    def __init__(self, model: DFBUModel) -> None:
        # ... existing code ...
        self.preview_worker: PreviewWorker | None = None

    def command_generate_preview(self) -> bool:
        """
        Command to generate backup preview.

        Returns:
            True if preview generation started
        """
        if self.preview_worker is not None and self.preview_worker.isRunning():
            return False

        self.preview_worker = PreviewWorker()
        self.preview_worker.set_model(self.model)
        self.preview_worker.progress_updated.connect(self._on_preview_progress)
        self.preview_worker.preview_finished.connect(self._on_preview_finished)
        self.preview_worker.error_occurred.connect(self._on_worker_error)
        self.preview_worker.start()
        return True

    def _on_preview_progress(self, progress: int) -> None:
        """Handle preview progress updates."""
        self.preview_progress.emit(progress)

    def _on_preview_finished(self, preview: BackupPreviewDict) -> None:
        """Handle preview completion."""
        if self.preview_worker:
            self.preview_worker.wait()
            self.preview_worker.deleteLater()
            self.preview_worker = None
        self.preview_ready.emit(preview)
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_viewmodel.py::test_viewmodel_preview_signal -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/gui/model.py DFBU/gui/viewmodel.py DFBU/tests/test_viewmodel.py
git commit -m "$(cat <<'EOF'
feat(preview): integrate preview with Model and ViewModel

Adds generate_backup_preview to Model and command_generate_preview
to ViewModel with PreviewWorker for async generation.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Phase 3: Dashboard/Statistics View

### Task 3.1: Add Dashboard TypedDicts

**Files:**

- Modify: `DFBU/core/common_types.py`
- Test: `DFBU/tests/test_common_types.py`

**Step 1: Write the failing test**

Add to `DFBU/tests/test_common_types.py`:

```python
from core.common_types import BackupHistoryEntry, DashboardMetrics


@pytest.mark.unit
def test_backup_history_entry_structure() -> None:
    """BackupHistoryEntry should have all required fields."""
    entry: BackupHistoryEntry = {
        "timestamp": "2026-02-05T10:00:00Z",
        "profile": "Default",
        "items_backed": 42,
        "size_bytes": 1048576,
        "duration_seconds": 5.5,
        "success": True,
        "backup_type": "mirror",
    }
    assert entry["success"] is True


@pytest.mark.unit
def test_dashboard_metrics_structure() -> None:
    """DashboardMetrics should have all required fields."""
    metrics: DashboardMetrics = {
        "total_backups": 100,
        "successful_backups": 95,
        "failed_backups": 5,
        "success_rate": 0.95,
        "total_size_backed_bytes": 10737418240,
        "average_duration_seconds": 4.2,
        "last_backup_timestamp": "2026-02-05T10:00:00Z",
    }
    assert metrics["success_rate"] == 0.95
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_common_types.py -k "history or dashboard" -v`
Expected: FAIL with "cannot import name 'BackupHistoryEntry'"

**Step 3: Write minimal implementation**

Add to `DFBU/core/common_types.py`:

```python
# =============================================================================
# Dashboard/History Types (v1.1.0)
# =============================================================================


class BackupHistoryEntry(TypedDict):
    """
    Type definition for a single backup history entry.

    Fields:
        timestamp: ISO format timestamp of backup
        profile: Profile name used (or "Default")
        items_backed: Number of items backed up
        size_bytes: Total size backed up
        duration_seconds: Time taken for backup
        success: Whether backup completed successfully
        backup_type: Type of backup ("mirror" or "archive")
    """

    timestamp: str
    profile: str
    items_backed: int
    size_bytes: int
    duration_seconds: float
    success: bool
    backup_type: str


class DashboardMetrics(TypedDict):
    """
    Type definition for dashboard metrics summary.

    Fields:
        total_backups: Total number of backups recorded
        successful_backups: Number of successful backups
        failed_backups: Number of failed backups
        success_rate: Success rate (0.0 to 1.0)
        total_size_backed_bytes: Total size of all backups
        average_duration_seconds: Average backup duration
        last_backup_timestamp: Timestamp of most recent backup
    """

    total_backups: int
    successful_backups: int
    failed_backups: int
    success_rate: float
    total_size_backed_bytes: int
    average_duration_seconds: float
    last_backup_timestamp: str | None
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_common_types.py -k "history or dashboard" -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/core/common_types.py DFBU/tests/test_common_types.py
git commit -m "$(cat <<'EOF'
feat(types): add BackupHistoryEntry and DashboardMetrics

Adds TypedDicts for backup history tracking and dashboard
metrics display in v1.1.0 statistics feature.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3.2: Create BackupHistoryManager service

**Files:**

- Create: `DFBU/gui/backup_history.py`
- Test: `DFBU/tests/test_backup_history.py`

**Step 1: Write the failing test**

Create `DFBU/tests/test_backup_history.py`:

```python
"""Tests for BackupHistoryManager service."""

from pathlib import Path

import pytest

from gui.backup_history import BackupHistoryManager


@pytest.mark.unit
def test_backup_history_manager_initialization(tmp_path: Path) -> None:
    """BackupHistoryManager should initialize with empty history."""
    manager = BackupHistoryManager(config_path=tmp_path)
    assert manager.get_entry_count() == 0


@pytest.mark.unit
def test_backup_history_manager_record_backup(tmp_path: Path) -> None:
    """BackupHistoryManager should record backup entries."""
    manager = BackupHistoryManager(config_path=tmp_path)

    manager.record_backup(
        items_backed=10,
        size_bytes=1024,
        duration_seconds=2.5,
        success=True,
        backup_type="mirror",
        profile="Default",
    )

    assert manager.get_entry_count() == 1


@pytest.mark.unit
def test_backup_history_manager_calculates_metrics(tmp_path: Path) -> None:
    """BackupHistoryManager should calculate dashboard metrics."""
    manager = BackupHistoryManager(config_path=tmp_path)

    # Record some backups
    manager.record_backup(10, 1024, 2.0, True, "mirror", "Default")
    manager.record_backup(5, 512, 1.5, True, "archive", "Default")
    manager.record_backup(0, 0, 0.5, False, "mirror", "Default")

    metrics = manager.get_metrics()

    assert metrics["total_backups"] == 3
    assert metrics["successful_backups"] == 2
    assert metrics["failed_backups"] == 1
    assert metrics["success_rate"] == pytest.approx(0.667, rel=0.01)
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_backup_history.py -v`
Expected: FAIL with "No module named 'gui.backup_history'"

**Step 3: Write minimal implementation**

Create `DFBU/gui/backup_history.py`:

```python
"""
DFBU BackupHistoryManager - Backup History Service

Description:
    Tracks backup history for dashboard metrics and analytics.
    Persists history to YAML file.

Author: Chris Purcell
Date Created: 2026-02-05
License: MIT
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from core.common_types import BackupHistoryEntry, DashboardMetrics


class BackupHistoryManager:
    """
    Manages backup history for dashboard analytics.

    Records backup operations and calculates aggregate metrics
    for display in the dashboard view.
    """

    MAX_HISTORY_ENTRIES = 1000  # Limit history to prevent unbounded growth

    def __init__(self, config_path: Path) -> None:
        """
        Initialize BackupHistoryManager.

        Args:
            config_path: Path to configuration directory
        """
        self.config_path = config_path
        self._history: list[BackupHistoryEntry] = []
        self._load_history()

    def _load_history(self) -> None:
        """Load history from YAML file."""
        history_file = self.config_path / "backup_history.yaml"

        if not history_file.exists():
            return

        try:
            yaml = YAML()
            with history_file.open("r", encoding="utf-8") as f:
                data = yaml.load(f)

            if data and "entries" in data:
                self._history = data["entries"]
        except Exception:
            # Silently fail - start with empty history
            pass

    def _save_history(self) -> None:
        """Save history to YAML file."""
        history_file = self.config_path / "backup_history.yaml"

        try:
            yaml = YAML()
            yaml.default_flow_style = False

            data = {"entries": self._history[-self.MAX_HISTORY_ENTRIES:]}

            with history_file.open("w", encoding="utf-8") as f:
                yaml.dump(data, f)
        except Exception:
            # Silently fail - history is not critical
            pass

    def get_entry_count(self) -> int:
        """Get number of history entries."""
        return len(self._history)

    def record_backup(
        self,
        items_backed: int,
        size_bytes: int,
        duration_seconds: float,
        success: bool,
        backup_type: str,
        profile: str = "Default",
    ) -> None:
        """
        Record a backup operation.

        Args:
            items_backed: Number of items backed up
            size_bytes: Total size backed up
            duration_seconds: Duration of backup
            success: Whether backup succeeded
            backup_type: Type of backup ("mirror" or "archive")
            profile: Profile name used
        """
        entry = BackupHistoryEntry(
            timestamp=datetime.now(UTC).isoformat(),
            profile=profile,
            items_backed=items_backed,
            size_bytes=size_bytes,
            duration_seconds=duration_seconds,
            success=success,
            backup_type=backup_type,
        )
        self._history.append(entry)
        self._save_history()

    def get_metrics(self) -> DashboardMetrics:
        """
        Calculate dashboard metrics from history.

        Returns:
            DashboardMetrics with aggregate statistics
        """
        total = len(self._history)
        successful = sum(1 for e in self._history if e["success"])
        failed = total - successful

        success_rate = successful / total if total > 0 else 0.0
        total_size = sum(e["size_bytes"] for e in self._history if e["success"])

        durations = [e["duration_seconds"] for e in self._history if e["success"]]
        avg_duration = sum(durations) / len(durations) if durations else 0.0

        last_timestamp = self._history[-1]["timestamp"] if self._history else None

        return DashboardMetrics(
            total_backups=total,
            successful_backups=successful,
            failed_backups=failed,
            success_rate=success_rate,
            total_size_backed_bytes=total_size,
            average_duration_seconds=avg_duration,
            last_backup_timestamp=last_timestamp,
        )

    def get_recent_history(self, count: int = 10) -> list[BackupHistoryEntry]:
        """
        Get recent backup history entries.

        Args:
            count: Number of entries to return

        Returns:
            List of recent history entries (newest first)
        """
        return list(reversed(self._history[-count:]))
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_backup_history.py -v`
Expected: PASS (all 3 tests)

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/gui/backup_history.py DFBU/tests/test_backup_history.py
git commit -m "$(cat <<'EOF'
feat(dashboard): create BackupHistoryManager service

Implements backup history tracking with YAML persistence,
record_backup for logging operations, and get_metrics for
dashboard statistics calculation.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

### Task 3.3: Integrate history recording with BackupWorker

**Files:**

- Modify: `DFBU/gui/model.py`
- Modify: `DFBU/gui/viewmodel.py`
- Test: `DFBU/tests/test_viewmodel.py`

**Step 1: Write the failing test**

Add to `DFBU/tests/test_viewmodel.py`:

```python
@pytest.mark.gui
def test_viewmodel_records_backup_history(
    qapp: QApplication, qtbot: Any, yaml_config_dir: Path, tmp_path: Path
) -> None:
    """ViewModel should record backup to history after completion."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    model = DFBUModel(yaml_config_dir)
    model.load_config()
    vm = DFBUViewModel(model)

    # Create a test file
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    model.add_dotfile("Test", "TestApp", "Test file", [str(test_file)], True)

    # Run backup and wait for completion
    with qtbot.waitSignal(vm.operation_finished, timeout=10000):
        vm.command_start_backup()

    # Check history was recorded
    assert model.get_backup_history_count() >= 1
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_viewmodel.py::test_viewmodel_records_backup_history -v`
Expected: FAIL with "DFBUModel has no attribute 'get_backup_history_count'"

**Step 3: Write minimal implementation**

Add to `DFBU/gui/model.py`:

```python
from gui.backup_history import BackupHistoryManager
from core.common_types import DashboardMetrics


class DFBUModel:
    def __init__(self, config_path: Path) -> None:
        # ... existing code ...

        # Initialize BackupHistoryManager (v1.1.0)
        self._history_manager: BackupHistoryManager = BackupHistoryManager(config_path)

    def record_backup_history(
        self,
        items_backed: int,
        size_bytes: int,
        duration_seconds: float,
        success: bool,
        backup_type: str,
    ) -> None:
        """Record backup to history."""
        profile = self.get_active_profile_name() or "Default"
        self._history_manager.record_backup(
            items_backed=items_backed,
            size_bytes=size_bytes,
            duration_seconds=duration_seconds,
            success=success,
            backup_type=backup_type,
            profile=profile,
        )

    def get_backup_history_count(self) -> int:
        """Get number of backup history entries."""
        return self._history_manager.get_entry_count()

    def get_dashboard_metrics(self) -> DashboardMetrics:
        """Get dashboard metrics from history."""
        return self._history_manager.get_metrics()

    def get_recent_backup_history(self, count: int = 10) -> list:
        """Get recent backup history entries."""
        return self._history_manager.get_recent_history(count)
```

Add to `DFBU/gui/viewmodel.py` in `_on_backup_finished`:

```python
    def _on_backup_finished(self) -> None:
        """Handle backup completion and cleanup worker."""
        # Record to history (v1.1.0)
        stats = self.model.statistics
        total_items = stats.processed_items + stats.skipped_items
        success = stats.failed_items == 0

        self.model.record_backup_history(
            items_backed=stats.processed_items,
            size_bytes=0,  # Size tracking not implemented yet
            duration_seconds=stats.total_time,
            success=success,
            backup_type="mirror" if self.model.options["mirror"] else "archive",
        )

        summary = self.get_statistics_summary()
        self.operation_finished.emit(summary)

        # ... existing cleanup code ...
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_viewmodel.py::test_viewmodel_records_backup_history -v`
Expected: PASS

**Step 5: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 6: Commit**

```bash
git add DFBU/gui/model.py DFBU/gui/viewmodel.py DFBU/tests/test_viewmodel.py
git commit -m "$(cat <<'EOF'
feat(dashboard): integrate history recording with backup

Records backup operations to history after completion.
Adds get_backup_history_count, get_dashboard_metrics,
get_recent_backup_history to Model facade.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Final Integration Tasks

### Task F.1: Run full test suite

**Step 1: Run all tests**

Run: `pytest DFBU/tests/ -v --tb=short`
Expected: All tests pass

**Step 2: Run mypy**

Run: `mypy DFBU/`
Expected: Success: no issues found

**Step 3: Commit any fixes needed**

---

### Task F.2: Update version to 1.1.0

**Files:**

- Modify: `DFBU/dfbu_gui.py` (version constant if present)
- Modify: `packaging/dfbu.spec`

**Step 1: Update version strings**

Update version to "1.1.0" in relevant files.

**Step 2: Commit**

```bash
git add DFBU/dfbu_gui.py packaging/dfbu.spec
git commit -m "$(cat <<'EOF'
chore: bump version to 1.1.0

Releases Backup Profiles, Backup Preview, and Dashboard features.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Summary

This plan implements three major features:

| Phase | Feature | Tasks | Key Files |
|-------|---------|-------|-----------|
| 1 | Backup Profiles | 8 | profile_manager.py, profile_dialog.py |
| 2 | Backup Preview | 3 | preview_generator.py |
| 3 | Dashboard | 3 | backup_history.py |

**Total Tasks:** 14+ bite-sized TDD tasks

Each task follows the pattern:

1. Write failing test
2. Run test to verify failure
3. Write minimal implementation
4. Run test to verify pass
5. Run mypy
6. Commit

---

**Plan complete and saved to `docs/plans/2026-02-05-v110-features-tdd.md`. Two execution options:**

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

**Which approach?**
