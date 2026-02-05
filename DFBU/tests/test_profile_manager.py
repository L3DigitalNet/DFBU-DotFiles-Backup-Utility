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


@pytest.mark.unit
def test_profile_manager_save_profiles(tmp_path: Path) -> None:
    """ProfileManager should save profiles to YAML file."""
    manager = ProfileManager(config_path=tmp_path)

    # Manually add a profile to the manager for saving
    from core.common_types import ProfileDict

    manager._profiles["Home"] = ProfileDict(
        name="Home",
        description="Home configuration",
        excluded=["Gaming"],
        options_overrides={"mirror": True},
        created_at="2026-02-05T11:00:00Z",
        modified_at="2026-02-05T11:00:00Z",
    )
    manager._active_profile = "Home"

    success, error = manager.save_profiles()

    assert success is True
    assert error == ""

    # Verify file was created
    profiles_file = tmp_path / "profiles.yaml"
    assert profiles_file.exists()

    # Verify content can be loaded back
    manager2 = ProfileManager(config_path=tmp_path)
    success2, _ = manager2.load_profiles()
    assert success2 is True
    assert manager2.get_profile_count() == 1
    assert manager2.get_active_profile_name() == "Home"


@pytest.mark.unit
def test_profile_manager_load_nonexistent_file(tmp_path: Path) -> None:
    """ProfileManager should succeed loading when no profiles.yaml exists."""
    manager = ProfileManager(config_path=tmp_path)
    success, error = manager.load_profiles()

    assert success is True
    assert error == ""
    assert manager.get_profile_count() == 0


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
def test_profile_manager_create_duplicate_profile(tmp_path: Path) -> None:
    """ProfileManager should return False for duplicate profile names."""
    manager = ProfileManager(config_path=tmp_path)
    manager.create_profile("Existing", "First profile", [])

    success = manager.create_profile("Existing", "Duplicate", [])

    assert success is False
    assert manager.get_profile_count() == 1


@pytest.mark.unit
def test_profile_manager_delete_profile(tmp_path: Path) -> None:
    """ProfileManager should delete profiles."""
    manager = ProfileManager(config_path=tmp_path)
    manager.create_profile("ToDelete", "Test", [])

    success = manager.delete_profile("ToDelete")

    assert success is True
    assert manager.get_profile_count() == 0


@pytest.mark.unit
def test_profile_manager_delete_nonexistent_profile(tmp_path: Path) -> None:
    """ProfileManager should return False when deleting non-existent profile."""
    manager = ProfileManager(config_path=tmp_path)

    success = manager.delete_profile("NonExistent")

    assert success is False


@pytest.mark.unit
def test_profile_manager_delete_clears_active(tmp_path: Path) -> None:
    """ProfileManager should clear active profile when deleted profile is active."""
    manager = ProfileManager(config_path=tmp_path)
    manager.create_profile("Active", "Test", [])
    manager.switch_profile("Active")
    assert manager.get_active_profile_name() == "Active"

    manager.delete_profile("Active")

    assert manager.get_active_profile_name() is None


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


@pytest.mark.unit
def test_profile_manager_switch_to_none(tmp_path: Path) -> None:
    """ProfileManager should allow switching to None (default)."""
    manager = ProfileManager(config_path=tmp_path)
    manager.create_profile("Profile1", "First", [])
    manager.switch_profile("Profile1")

    success = manager.switch_profile(None)

    assert success is True
    assert manager.get_active_profile_name() is None


@pytest.mark.unit
def test_profile_manager_switch_nonexistent(tmp_path: Path) -> None:
    """ProfileManager should return False when switching to non-existent profile."""
    manager = ProfileManager(config_path=tmp_path)

    success = manager.switch_profile("NonExistent")

    assert success is False


@pytest.mark.unit
def test_profile_manager_get_profile_names(tmp_path: Path) -> None:
    """ProfileManager should return sorted list of profile names."""
    manager = ProfileManager(config_path=tmp_path)
    manager.create_profile("Zebra", "Z profile", [])
    manager.create_profile("Alpha", "A profile", [])
    manager.create_profile("Middle", "M profile", [])

    names = manager.get_profile_names()

    assert names == ["Alpha", "Middle", "Zebra"]


@pytest.mark.unit
def test_profile_manager_get_active_exclusions_no_active(tmp_path: Path) -> None:
    """ProfileManager should return empty list when no active profile."""
    manager = ProfileManager(config_path=tmp_path)

    exclusions = manager.get_active_exclusions()

    assert exclusions == []
