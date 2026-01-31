#!/usr/bin/env python3
"""
Tests for RestoreBackupManager - Pre-Restore Safety Component

Description:
    Test suite for RestoreBackupManager validating pre-restore backups,
    manifest creation, and retention policy.

Author: Chris Purcell
"""

import sys
from pathlib import Path
from typing import Protocol, runtime_checkable

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))

from protocols import RestoreBackupManagerProtocol


class TestRestoreBackupManagerProtocol:
    """Test RestoreBackupManagerProtocol interface definition."""

    def test_protocol_exists(self) -> None:
        """Test that RestoreBackupManagerProtocol is defined."""
        # Assert
        assert hasattr(RestoreBackupManagerProtocol, "backup_before_restore")
        assert hasattr(RestoreBackupManagerProtocol, "get_backup_count")
        assert hasattr(RestoreBackupManagerProtocol, "cleanup_old_backups")


# =============================================================================
# RestoreBackupManager Initialization Tests
# =============================================================================


class TestRestoreBackupManagerInitialization:
    """Test RestoreBackupManager initialization."""

    def test_initialization_default_path(self) -> None:
        """Test RestoreBackupManager initializes with default backup path."""
        # Arrange & Act
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager()

        # Assert
        expected_path = Path.home() / ".local" / "share" / "dfbu" / "restore-backups"
        assert manager.backup_base_dir == expected_path
        assert manager.max_backups == 5

    def test_initialization_custom_path(self, tmp_path: Path) -> None:
        """Test RestoreBackupManager with custom backup path."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        custom_path = tmp_path / "custom-backups"

        # Act
        manager = RestoreBackupManager(backup_base_dir=custom_path, max_backups=10)

        # Assert
        assert manager.backup_base_dir == custom_path
        assert manager.max_backups == 10

    def test_max_backups_setter(self, tmp_path: Path) -> None:
        """Test max_backups can be updated."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path)

        # Act
        manager.max_backups = 3

        # Assert
        assert manager.max_backups == 3


# =============================================================================
# Backup Listing Tests
# =============================================================================


class TestBackupListing:
    """Test backup listing and counting."""

    def test_get_backup_count_empty(self, tmp_path: Path) -> None:
        """Test count is 0 when no backups exist."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path)

        # Act
        count = manager.get_backup_count()

        # Assert
        assert count == 0

    def test_get_backup_count_with_backups(self, tmp_path: Path) -> None:
        """Test count matches number of backup directories."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path)
        (tmp_path / "2026-01-31_100000").mkdir()
        (tmp_path / "2026-01-31_110000").mkdir()
        (tmp_path / "2026-01-31_120000").mkdir()

        # Act
        count = manager.get_backup_count()

        # Assert
        assert count == 3

    def test_get_backup_count_ignores_files(self, tmp_path: Path) -> None:
        """Test count ignores regular files, only counts directories."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path)
        (tmp_path / "2026-01-31_100000").mkdir()
        (tmp_path / "random_file.txt").write_text("ignore me")

        # Act
        count = manager.get_backup_count()

        # Assert
        assert count == 1

    def test_get_backup_count_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test count is 0 when backup directory doesn't exist."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        nonexistent = tmp_path / "does_not_exist"
        manager = RestoreBackupManager(backup_base_dir=nonexistent)

        # Act
        count = manager.get_backup_count()

        # Assert
        assert count == 0

    def test_list_backups_empty(self, tmp_path: Path) -> None:
        """Test list returns empty when no backups exist."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path)

        # Act
        backups = manager.list_backups()

        # Assert
        assert backups == []

    def test_list_backups_sorted_newest_first(self, tmp_path: Path) -> None:
        """Test list returns backups sorted by timestamp, newest first."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path)
        (tmp_path / "2026-01-30_100000").mkdir()
        (tmp_path / "2026-01-31_120000").mkdir()
        (tmp_path / "2026-01-31_100000").mkdir()

        # Act
        backups = manager.list_backups()

        # Assert
        assert len(backups) == 3
        assert backups[0][0].name == "2026-01-31_120000"
        assert backups[1][0].name == "2026-01-31_100000"
        assert backups[2][0].name == "2026-01-30_100000"

    def test_list_backups_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test list returns empty when backup directory doesn't exist."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        nonexistent = tmp_path / "does_not_exist"
        manager = RestoreBackupManager(backup_base_dir=nonexistent)

        # Act
        backups = manager.list_backups()

        # Assert
        assert backups == []

    def test_list_backups_ignores_files(self, tmp_path: Path) -> None:
        """Test list ignores regular files, only lists directories."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path)
        (tmp_path / "2026-01-31_100000").mkdir()
        (tmp_path / "random_file.txt").write_text("ignore me")

        # Act
        backups = manager.list_backups()

        # Assert
        assert len(backups) == 1
        assert backups[0][0].name == "2026-01-31_100000"
        assert backups[0][1] == "2026-01-31_100000"


# =============================================================================
# Cleanup Old Backups Tests
# =============================================================================


class TestCleanupOldBackups:
    """Test backup cleanup and retention policy."""

    def test_cleanup_no_action_under_limit(self, tmp_path: Path) -> None:
        """Test cleanup does nothing when under max_backups limit."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path, max_backups=5)
        (tmp_path / "2026-01-31_100000").mkdir()
        (tmp_path / "2026-01-31_110000").mkdir()

        # Act
        removed = manager.cleanup_old_backups()

        # Assert
        assert removed == []
        assert manager.get_backup_count() == 2

    def test_cleanup_removes_oldest_over_limit(self, tmp_path: Path) -> None:
        """Test cleanup removes oldest backups when over limit."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path, max_backups=2)
        dir1 = tmp_path / "2026-01-29_100000"
        dir2 = tmp_path / "2026-01-30_100000"
        dir3 = tmp_path / "2026-01-31_100000"
        dir1.mkdir()
        dir2.mkdir()
        dir3.mkdir()

        # Act
        removed = manager.cleanup_old_backups()

        # Assert
        assert len(removed) == 1
        assert removed[0] == dir1
        assert not dir1.exists()
        assert dir2.exists()
        assert dir3.exists()

    def test_cleanup_removes_multiple_oldest(self, tmp_path: Path) -> None:
        """Test cleanup removes multiple backups when far over limit."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path, max_backups=1)
        for i in range(5):
            (tmp_path / f"2026-01-{25+i:02d}_100000").mkdir()

        # Act
        removed = manager.cleanup_old_backups()

        # Assert
        assert len(removed) == 4
        assert manager.get_backup_count() == 1
        # Newest should remain
        assert (tmp_path / "2026-01-29_100000").exists()

    def test_cleanup_handles_nonexistent_dir(self, tmp_path: Path) -> None:
        """Test cleanup handles nonexistent backup directory gracefully."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        nonexistent = tmp_path / "does_not_exist"
        manager = RestoreBackupManager(backup_base_dir=nonexistent)

        # Act
        removed = manager.cleanup_old_backups()

        # Assert
        assert removed == []


# =============================================================================
# Backup Before Restore Tests
# =============================================================================


class TestBackupBeforeRestore:
    """Test backup_before_restore functionality."""

    def test_backup_creates_timestamped_directory(self, tmp_path: Path) -> None:
        """Test backup creates directory with timestamp name."""
        # Arrange
        import re

        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path)
        file_to_backup = tmp_path / "original" / "test.txt"
        file_to_backup.parent.mkdir()
        file_to_backup.write_text("original content")

        # Act
        success, error, backup_dir = manager.backup_before_restore(
            files_to_overwrite=[file_to_backup],
            source_backup_path="/backups/mirror/2026-01-28",
        )

        # Assert
        assert success is True
        assert error == ""
        assert backup_dir is not None
        assert backup_dir.exists()
        # Verify timestamp format: YYYY-MM-DD_HHMMSS
        assert re.match(r"\d{4}-\d{2}-\d{2}_\d{6}", backup_dir.name)

    def test_backup_creates_base_directory_if_missing(self, tmp_path: Path) -> None:
        """Test backup creates base directory if it doesn't exist."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        backup_base = tmp_path / "new" / "nested" / "backup"
        manager = RestoreBackupManager(backup_base_dir=backup_base)
        file_to_backup = tmp_path / "test.txt"
        file_to_backup.write_text("content")

        # Act
        success, error, backup_dir = manager.backup_before_restore(
            files_to_overwrite=[file_to_backup],
            source_backup_path="/backups/mirror/test",
        )

        # Assert
        assert success is True
        assert backup_base.exists()

    def test_backup_empty_list_succeeds(self, tmp_path: Path) -> None:
        """Test backup with empty file list succeeds with no backup created."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path)

        # Act
        success, error, backup_dir = manager.backup_before_restore(
            files_to_overwrite=[],
            source_backup_path="/backups/mirror/test",
        )

        # Assert
        assert success is True
        assert error == ""
        assert backup_dir is None
        assert manager.get_backup_count() == 0

    def test_backup_copies_files_preserving_structure(self, tmp_path: Path) -> None:
        """Test backup copies files preserving relative directory structure."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        mock_home = tmp_path / "home"
        mock_home.mkdir()
        manager = RestoreBackupManager(
            backup_base_dir=tmp_path / "backups",
            home_dir=mock_home,
        )

        # Create source files with nested structure
        config_dir = mock_home / ".config" / "app"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "settings.toml"
        config_file.write_text("key = 'value'")

        bashrc = mock_home / ".bashrc"
        bashrc.write_text("export PATH=$PATH")

        # Act
        success, error, backup_dir = manager.backup_before_restore(
            files_to_overwrite=[config_file, bashrc],
            source_backup_path="/backups/mirror/test",
        )

        # Assert
        assert success is True
        assert backup_dir is not None

        # Verify files were copied (structure relative to home)
        backed_up_config = backup_dir / ".config" / "app" / "settings.toml"
        backed_up_bashrc = backup_dir / ".bashrc"
        assert backed_up_config.exists()
        assert backed_up_bashrc.exists()
        assert backed_up_config.read_text() == "key = 'value'"
        assert backed_up_bashrc.read_text() == "export PATH=$PATH"

    def test_backup_skips_nonexistent_files(self, tmp_path: Path) -> None:
        """Test backup skips files that don't exist."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        manager = RestoreBackupManager(backup_base_dir=tmp_path / "backups")

        existing = tmp_path / "exists.txt"
        existing.write_text("I exist")
        nonexistent = tmp_path / "missing.txt"

        # Act
        success, error, backup_dir = manager.backup_before_restore(
            files_to_overwrite=[existing, nonexistent],
            source_backup_path="/backups/mirror/test",
        )

        # Assert
        assert success is True
        # Only the existing file should be backed up
        backed_up = backup_dir / "exists.txt"
        assert backed_up.exists()
        assert not (backup_dir / "missing.txt").exists()

    def test_backup_handles_directories(self, tmp_path: Path) -> None:
        """Test backup handles directories by copying all contents."""
        # Arrange
        from restore_backup_manager import RestoreBackupManager

        mock_home = tmp_path / "home"
        mock_home.mkdir()
        manager = RestoreBackupManager(
            backup_base_dir=tmp_path / "backups",
            home_dir=mock_home,
        )

        source_dir = mock_home / ".config" / "nvim"
        source_dir.mkdir(parents=True)
        (source_dir / "init.lua").write_text("vim.opt.number = true")
        (source_dir / "lua").mkdir()
        (source_dir / "lua" / "plugins.lua").write_text("return {}")

        # Act
        success, error, backup_dir = manager.backup_before_restore(
            files_to_overwrite=[source_dir],
            source_backup_path="/backups/mirror/test",
        )

        # Assert
        assert success is True
        backed_up_dir = backup_dir / ".config" / "nvim"
        assert backed_up_dir.is_dir()
        assert (backed_up_dir / "init.lua").read_text() == "vim.opt.number = true"
        assert (backed_up_dir / "lua" / "plugins.lua").read_text() == "return {}"
