#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for DFBU GUI config backup functionality

Description:
    Tests to validate that dfbu-config.toml is automatically backed up with
    rotation when saved through the model's save_config() method.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 10-30-2025
License: MIT
"""

import sys
import time
from pathlib import Path

import pytest

# Add src and common_lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "common_lib"))

from model import DFBUModel


class TestConfigBackupIntegration:
    """Test suite for automatic config file backup during save operations."""

    def test_saves_config_without_backup_on_first_save(self, tmp_path: Path) -> None:
        """Test that first save doesn't create backup (no previous config exists)."""
        # Arrange: Create new config file path
        config_path = tmp_path / "dfbu-config.toml"
        model = DFBUModel(config_path)
        model.options["mirror"] = True
        model.add_dotfile(
            category="Shell",
            subcategory="Bash",
            application="Bash",
            description="Bash config",
            path="~/.bashrc",
            enabled=True,
        )

        # Act: Save config for first time
        success, error = model.save_config()

        # Assert: Config saved successfully, no backup created (file didn't exist before)
        assert success is True
        assert error == ""
        assert config_path.exists()
        backup_dir = config_path.parent / f".{config_path.name}.backups"
        assert not backup_dir.exists()  # No backup on first save

    def test_creates_backup_on_subsequent_saves(self, tmp_path: Path) -> None:
        """Test that backup is created on subsequent saves."""
        # Arrange: Create and save initial config
        config_path = tmp_path / "dfbu-config.toml"
        model = DFBUModel(config_path)
        model.add_dotfile(
            category="Shell",
            subcategory="Bash",
            application="Bash",
            description="Bash config",
            path="~/.bashrc",
            enabled=True,
        )
        success, _ = model.save_config()
        assert success is True

        # Act: Save config again (should create backup)
        time.sleep(0.1)  # Ensure different timestamp
        model.add_dotfile(
            category="Editor",
            subcategory="Vim",
            application="Vim",
            description="Vim config",
            path="~/.vimrc",
            enabled=True,
        )
        success, error = model.save_config()

        # Assert: Backup created
        assert success is True
        assert error == ""
        backup_dir = config_path.parent / f".{config_path.name}.backups"
        assert backup_dir.exists()
        backup_files = list(backup_dir.glob("dfbu-config.*.toml"))
        assert len(backup_files) == 1

    def test_rotates_backups_after_multiple_saves(self, tmp_path: Path) -> None:
        """Test that backups are rotated after exceeding max count."""
        # Arrange: Create initial config
        config_path = tmp_path / "dfbu-config.toml"
        model = DFBUModel(config_path)
        model.add_dotfile(
            category="Shell",
            subcategory="Bash",
            application="Bash",
            description="Bash config",
            path="~/.bashrc",
            enabled=True,
        )
        success, _ = model.save_config()
        assert success is True

        # Act: Save config 12 more times (total 13 saves = 12 backups)
        for i in range(12):
            time.sleep(0.05)  # Ensure different timestamps
            model.add_dotfile(
                category=f"Category{i}",
                subcategory=f"Sub{i}",
                application=f"App{i}",
                description=f"Desc {i}",
                path=f"~/file{i}",
                enabled=True,
            )
            success, _ = model.save_config()
            assert success is True

        # Assert: Only 10 backups remain (max rotation limit)
        backup_dir = config_path.parent / f".{config_path.name}.backups"
        backup_files = list(backup_dir.glob("dfbu-config.*.toml"))
        assert len(backup_files) == 10

    def test_backup_preserves_config_content(self, tmp_path: Path) -> None:
        """Test that backup contains exact copy of previous config."""
        # Arrange: Create and save initial config
        config_path = tmp_path / "dfbu-config.toml"
        model = DFBUModel(config_path)
        model.add_dotfile(
            category="Shell",
            subcategory="Bash",
            application="Bash",
            description="Bash config",
            path="~/.bashrc",
            enabled=True,
        )
        success, _ = model.save_config()
        assert success is True
        original_content = config_path.read_text()

        # Act: Modify and save again
        time.sleep(0.1)
        model.add_dotfile(
            category="Editor",
            subcategory="Vim",
            application="Vim",
            description="Vim config",
            path="~/.vimrc",
            enabled=True,
        )
        success, _ = model.save_config()

        # Assert: Backup contains original content
        assert success is True
        backup_dir = config_path.parent / f".{config_path.name}.backups"
        backup_files = list(backup_dir.glob("dfbu-config.*.toml"))
        assert len(backup_files) == 1
        backup_content = backup_files[0].read_text()
        assert backup_content == original_content

    def test_backup_directory_naming_convention(self, tmp_path: Path) -> None:
        """Test that backup directory follows naming convention."""
        # Arrange: Create config with specific name
        config_path = tmp_path / "my-config.toml"
        model = DFBUModel(config_path)
        model.add_dotfile(
            category="Shell",
            subcategory="Bash",
            application="Bash",
            description="Bash config",
            path="~/.bashrc",
            enabled=True,
        )
        success, _ = model.save_config()
        assert success is True

        # Act: Save again to create backup
        time.sleep(0.1)
        model.update_option("mirror", False)
        success, _ = model.save_config()

        # Assert: Backup directory follows naming convention
        assert success is True
        expected_backup_dir = config_path.parent / ".my-config.toml.backups"
        assert expected_backup_dir.exists()

    def test_handles_rapid_successive_saves(self, tmp_path: Path) -> None:
        """Test handling of rapid successive saves within same second."""
        # Arrange: Create initial config
        config_path = tmp_path / "dfbu-config.toml"
        model = DFBUModel(config_path)
        model.add_dotfile(
            category="Shell",
            subcategory="Bash",
            application="Bash",
            description="Bash config",
            path="~/.bashrc",
            enabled=True,
        )
        success, _ = model.save_config()
        assert success is True

        # Act: Save multiple times rapidly
        for i in range(5):
            model.update_option("mirror", i % 2 == 0)
            success, _ = model.save_config()
            assert success is True

        # Assert: All backups created (collision handling works)
        backup_dir = config_path.parent / f".{config_path.name}.backups"
        backup_files = list(backup_dir.glob("dfbu-config.*.toml"))
        assert len(backup_files) == 5

    def test_continues_on_backup_failure(self, tmp_path: Path) -> None:
        """Test that save continues even if backup fails."""
        # Arrange: Create initial config
        config_path = tmp_path / "dfbu-config.toml"
        model = DFBUModel(config_path)
        model.add_dotfile(
            category="Shell",
            subcategory="Bash",
            application="Bash",
            description="Bash config",
            path="~/.bashrc",
            enabled=True,
        )
        success, _ = model.save_config()
        assert success is True

        # Act: Make backup directory read-only to force backup failure
        backup_dir = config_path.parent / f".{config_path.name}.backups"
        backup_dir.mkdir(exist_ok=True)
        backup_dir.chmod(0o444)  # Read-only

        try:
            time.sleep(0.1)
            model.update_option("mirror", False)
            success, error = model.save_config()

            # Assert: Save still succeeds despite backup failure
            assert success is True
            assert error == ""
            assert config_path.exists()

        finally:
            # Cleanup: Restore permissions
            backup_dir.chmod(0o755)
