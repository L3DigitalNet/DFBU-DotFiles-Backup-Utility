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
