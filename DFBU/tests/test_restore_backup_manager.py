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
