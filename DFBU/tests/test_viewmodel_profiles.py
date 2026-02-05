"""
Tests for ViewModel Profile Signals and Commands
=================================================

Description:
    Unit tests for the ViewModel's profile management methods including
    signals and commands for profile creation, deletion, and switching.

Author: Chris Purcell
Date Created: 2026-02-05
License: MIT

Test Coverage:
    - profile_switched signal emission
    - profiles_changed signal emission
    - command_create_profile
    - command_delete_profile
    - command_switch_profile
    - get_profile_names
    - get_active_profile_name
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from PySide6.QtWidgets import QApplication


# =============================================================================
# Tests for Profile Signals (v1.1.0)
# =============================================================================


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

    # Test profiles_changed signal on create
    with qtbot.waitSignal(vm.profiles_changed, timeout=1000):
        vm.command_create_profile("TestProfile", "Test", [])

    # Test profile_switched signal
    with qtbot.waitSignal(vm.profile_switched, timeout=1000):
        vm.command_switch_profile("TestProfile")

    assert vm.get_active_profile_name() == "TestProfile"


# =============================================================================
# Tests for command_create_profile
# =============================================================================


@pytest.mark.gui
class TestCommandCreateProfile:
    """Tests for command_create_profile method."""

    def test_create_profile_emits_profiles_changed(
        self, qapp: QApplication, qtbot: Any, yaml_config_dir: Path
    ) -> None:
        """Create profile should emit profiles_changed signal on success."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        with qtbot.waitSignal(vm.profiles_changed, timeout=1000):
            result = vm.command_create_profile("NewProfile", "Description", [])

        assert result is True

    def test_create_profile_with_exclusions(
        self, qapp: QApplication, qtbot: Any, yaml_config_dir: Path
    ) -> None:
        """Create profile should accept exclusion list."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        with qtbot.waitSignal(vm.profiles_changed, timeout=1000):
            result = vm.command_create_profile(
                "ExclusionProfile", "With exclusions", ["Firefox", "Steam"]
            )

        assert result is True

    def test_create_profile_with_options_overrides(
        self, qapp: QApplication, qtbot: Any, yaml_config_dir: Path
    ) -> None:
        """Create profile should accept options overrides."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        with qtbot.waitSignal(vm.profiles_changed, timeout=1000):
            result = vm.command_create_profile(
                "CustomProfile",
                "With overrides",
                [],
                {"mirror": False, "archive": True},
            )

        assert result is True


# =============================================================================
# Tests for command_delete_profile
# =============================================================================


@pytest.mark.gui
class TestCommandDeleteProfile:
    """Tests for command_delete_profile method."""

    def test_delete_profile_emits_profiles_changed(
        self, qapp: QApplication, qtbot: Any, yaml_config_dir: Path
    ) -> None:
        """Delete profile should emit profiles_changed signal on success."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        # First create a profile
        vm.command_create_profile("ToDelete", "Will be deleted", [])

        # Then delete it
        with qtbot.waitSignal(vm.profiles_changed, timeout=1000):
            result = vm.command_delete_profile("ToDelete")

        assert result is True

    def test_delete_nonexistent_profile_returns_false(
        self, qapp: QApplication, yaml_config_dir: Path
    ) -> None:
        """Delete nonexistent profile should return False."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        result = vm.command_delete_profile("NonexistentProfile")
        assert result is False


# =============================================================================
# Tests for command_switch_profile
# =============================================================================


@pytest.mark.gui
class TestCommandSwitchProfile:
    """Tests for command_switch_profile method."""

    def test_switch_profile_emits_profile_switched(
        self, qapp: QApplication, qtbot: Any, yaml_config_dir: Path
    ) -> None:
        """Switch profile should emit profile_switched signal."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        # Create a profile first
        vm.command_create_profile("SwitchTarget", "Target profile", [])

        # Switch to it
        with qtbot.waitSignal(vm.profile_switched, timeout=1000):
            result = vm.command_switch_profile("SwitchTarget")

        assert result is True

    def test_switch_profile_emits_exclusions_changed(
        self, qapp: QApplication, qtbot: Any, yaml_config_dir: Path
    ) -> None:
        """Switch profile should emit exclusions_changed signal."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        # Create a profile first
        vm.command_create_profile("ExclusionTarget", "Target profile", ["Firefox"])

        # Switch to it - should emit exclusions_changed
        with qtbot.waitSignal(vm.exclusions_changed, timeout=1000):
            vm.command_switch_profile("ExclusionTarget")

    def test_switch_to_default_profile(
        self, qapp: QApplication, qtbot: Any, yaml_config_dir: Path
    ) -> None:
        """Switch to None should switch to default profile."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        # Create and switch to a profile first
        vm.command_create_profile("TempProfile", "Temporary", [])
        vm.command_switch_profile("TempProfile")

        # Switch back to default
        with qtbot.waitSignal(vm.profile_switched, timeout=1000):
            result = vm.command_switch_profile(None)

        assert result is True


# =============================================================================
# Tests for get_profile_names
# =============================================================================


@pytest.mark.gui
class TestGetProfileNames:
    """Tests for get_profile_names method."""

    def test_get_profile_names_returns_list(
        self, qapp: QApplication, yaml_config_dir: Path
    ) -> None:
        """get_profile_names should return list of profile names."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        # Create some profiles
        vm.command_create_profile("Profile1", "First", [])
        vm.command_create_profile("Profile2", "Second", [])

        names = vm.get_profile_names()

        assert "Profile1" in names
        assert "Profile2" in names

    def test_get_profile_names_empty_initially(
        self, qapp: QApplication, yaml_config_dir: Path
    ) -> None:
        """get_profile_names should return empty list when no profiles."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        names = vm.get_profile_names()
        assert isinstance(names, list)


# =============================================================================
# Tests for get_active_profile_name
# =============================================================================


@pytest.mark.gui
class TestGetActiveProfileName:
    """Tests for get_active_profile_name method."""

    def test_get_active_profile_name_returns_none_initially(
        self, qapp: QApplication, yaml_config_dir: Path
    ) -> None:
        """get_active_profile_name should return None when no profile active."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        assert vm.get_active_profile_name() is None

    def test_get_active_profile_name_after_switch(
        self, qapp: QApplication, yaml_config_dir: Path
    ) -> None:
        """get_active_profile_name should return name after switch."""
        from gui.model import DFBUModel
        from gui.viewmodel import DFBUViewModel

        model = DFBUModel(yaml_config_dir)
        model.load_config()
        vm = DFBUViewModel(model)

        vm.command_create_profile("ActiveProfile", "Active", [])
        vm.command_switch_profile("ActiveProfile")

        assert vm.get_active_profile_name() == "ActiveProfile"
