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
