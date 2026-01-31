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
