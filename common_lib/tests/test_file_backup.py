#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for file_backup module - Rotating Backup Functionality

Description:
    Comprehensive pytest tests for rotating file backup utility. Tests backup
    creation, rotation, and file discovery functionality with various scenarios.

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

# Add common_lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from file_backup import (
    create_rotating_backup,
    get_backup_files,
    rotate_old_backups,
)


class TestCreateRotatingBackup:
    """Test suite for create_rotating_backup function."""

    def test_creates_backup_in_default_directory(self, tmp_path: Path) -> None:
        """Test backup creation in default .backups directory."""
        # Arrange: Create source file
        source_file = tmp_path / "config.toml"
        source_file.write_text("test content")

        # Act: Create backup
        backup_path, success = create_rotating_backup(source_file, max_backups=10)

        # Assert: Backup created successfully
        assert success is True
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.read_text() == "test content"
        assert ".config.toml.backups" in str(backup_path)

    def test_creates_backup_in_specified_directory(self, tmp_path: Path) -> None:
        """Test backup creation in specified directory."""
        # Arrange: Create source file and backup directory
        source_file = tmp_path / "config.toml"
        source_file.write_text("test content")
        backup_dir = tmp_path / "backups"

        # Act: Create backup with specified directory
        backup_path, success = create_rotating_backup(
            source_file, backup_dir=backup_dir, max_backups=10
        )

        # Assert: Backup created in specified directory
        assert success is True
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.parent == backup_dir
        assert backup_path.read_text() == "test content"

    def test_creates_backup_directory_if_not_exists(self, tmp_path: Path) -> None:
        """Test automatic creation of backup directory."""
        # Arrange: Create source file without creating backup directory
        source_file = tmp_path / "config.toml"
        source_file.write_text("test content")
        backup_dir = tmp_path / "nonexistent" / "backups"

        # Act: Create backup (should create directory)
        backup_path, success = create_rotating_backup(
            source_file, backup_dir=backup_dir, max_backups=10
        )

        # Assert: Directory created and backup succeeded
        assert success is True
        assert backup_dir.exists()
        assert backup_path is not None
        assert backup_path.exists()

    def test_fails_when_source_file_does_not_exist(self, tmp_path: Path) -> None:
        """Test failure when source file doesn't exist."""
        # Arrange: Non-existent source file
        source_file = tmp_path / "nonexistent.toml"
        backup_dir = tmp_path / "backups"

        # Act: Attempt to create backup
        backup_path, success = create_rotating_backup(
            source_file, backup_dir=backup_dir, max_backups=10
        )

        # Assert: Backup failed
        assert success is False
        assert backup_path is None

    def test_backup_filename_contains_timestamp(self, tmp_path: Path) -> None:
        """Test that backup filename includes timestamp."""
        # Arrange: Create source file
        source_file = tmp_path / "config.toml"
        source_file.write_text("test content")
        backup_dir = tmp_path / "backups"

        # Act: Create backup
        backup_path, success = create_rotating_backup(
            source_file, backup_dir=backup_dir, max_backups=10
        )

        # Assert: Backup filename contains timestamp pattern
        assert success is True
        assert backup_path is not None
        # Filename format: config.YYYYMMDD_HHMMSS.toml
        assert backup_path.stem.startswith("config.")
        assert backup_path.suffix == ".toml"
        # Check that timestamp portion exists (8 digits for date + underscore + 6 digits for time)
        timestamp_part = backup_path.stem.split(".", 1)[1]
        assert len(timestamp_part) == 15  # YYYYMMDD_HHMMSS = 15 chars
        assert "_" in timestamp_part

    def test_preserves_file_content(self, tmp_path: Path) -> None:
        """Test that backup preserves file content exactly."""
        # Arrange: Create source file with specific content
        source_file = tmp_path / "config.toml"
        test_content = "title = 'Test Config'\n[section]\nkey = 'value'\n"
        source_file.write_text(test_content)
        backup_dir = tmp_path / "backups"

        # Act: Create backup
        backup_path, success = create_rotating_backup(
            source_file, backup_dir=backup_dir, max_backups=10
        )

        # Assert: Content preserved exactly
        assert success is True
        assert backup_path is not None
        assert backup_path.read_text() == test_content

    def test_custom_timestamp_format(self, tmp_path: Path) -> None:
        """Test backup creation with custom timestamp format."""
        # Arrange: Create source file
        source_file = tmp_path / "config.toml"
        source_file.write_text("test content")
        backup_dir = tmp_path / "backups"

        # Act: Create backup with custom timestamp format
        backup_path, success = create_rotating_backup(
            source_file,
            backup_dir=backup_dir,
            max_backups=10,
            timestamp_format="%Y-%m-%d",
        )

        # Assert: Backup uses custom timestamp format
        assert success is True
        assert backup_path is not None
        # Filename format: config.YYYY-MM-DD.toml
        timestamp_part = backup_path.stem.split(".", 1)[1]
        assert len(timestamp_part) == 10  # YYYY-MM-DD = 10 chars
        assert timestamp_part.count("-") == 2


class TestRotateOldBackups:
    """Test suite for rotate_old_backups function."""

    def test_deletes_oldest_backups_when_exceeding_max(self, tmp_path: Path) -> None:
        """Test deletion of oldest backups exceeding maximum count."""
        # Arrange: Create source file and multiple backups
        source_file = tmp_path / "config.toml"
        source_file.write_text("test content")
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create 5 backup files with different timestamps
        backup_files = []
        for i in range(5):
            backup_file = backup_dir / f"config.{i:08d}_000000.toml"
            backup_file.write_text(f"backup {i}")
            backup_files.append(backup_file)
            time.sleep(0.01)  # Ensure different mtimes

        # Act: Rotate to keep only 3 backups
        deleted = rotate_old_backups(source_file, backup_dir, max_backups=3)

        # Assert: 2 oldest backups deleted
        assert len(deleted) == 2
        assert backup_files[0] in deleted
        assert backup_files[1] in deleted
        assert backup_files[2].exists()
        assert backup_files[3].exists()
        assert backup_files[4].exists()
        assert not backup_files[0].exists()
        assert not backup_files[1].exists()

    def test_no_deletion_when_under_max(self, tmp_path: Path) -> None:
        """Test no deletion when backup count is under maximum."""
        # Arrange: Create source file and 3 backups
        source_file = tmp_path / "config.toml"
        source_file.write_text("test content")
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create 3 backup files
        backup_files = []
        for i in range(3):
            backup_file = backup_dir / f"config.{i:08d}_000000.toml"
            backup_file.write_text(f"backup {i}")
            backup_files.append(backup_file)

        # Act: Rotate with max of 5 backups
        deleted = rotate_old_backups(source_file, backup_dir, max_backups=5)

        # Assert: No backups deleted
        assert len(deleted) == 0
        for backup_file in backup_files:
            assert backup_file.exists()

    def test_handles_nonexistent_backup_directory(self, tmp_path: Path) -> None:
        """Test graceful handling when backup directory doesn't exist."""
        # Arrange: Source file without backup directory
        source_file = tmp_path / "config.toml"
        backup_dir = tmp_path / "nonexistent"

        # Act: Attempt rotation
        deleted = rotate_old_backups(source_file, backup_dir, max_backups=5)

        # Assert: No errors, empty deletion list
        assert len(deleted) == 0


class TestGetBackupFiles:
    """Test suite for get_backup_files function."""

    def test_finds_all_backup_files(self, tmp_path: Path) -> None:
        """Test finding all backup files for source file."""
        # Arrange: Create source file and multiple backups
        source_file = tmp_path / "config.toml"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create 3 backup files
        backup_files = []
        for i in range(3):
            backup_file = backup_dir / f"config.{i:08d}_000000.toml"
            backup_file.write_text(f"backup {i}")
            backup_files.append(backup_file)
            time.sleep(0.01)  # Ensure different mtimes

        # Act: Get backup files
        found_backups = get_backup_files(source_file, backup_dir)

        # Assert: All backups found
        assert len(found_backups) == 3
        for backup_file in backup_files:
            assert backup_file in found_backups

    def test_returns_backups_sorted_by_age(self, tmp_path: Path) -> None:
        """Test that backups are returned sorted by age (oldest first)."""
        # Arrange: Create backups with different ages
        source_file = tmp_path / "config.toml"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create backups in specific order with delays
        backup_files = []
        for i in range(3):
            backup_file = backup_dir / f"config.{i:08d}_000000.toml"
            backup_file.write_text(f"backup {i}")
            backup_files.append(backup_file)
            time.sleep(0.01)  # Ensure different mtimes

        # Act: Get backup files
        found_backups = get_backup_files(source_file, backup_dir)

        # Assert: Backups sorted oldest to newest
        assert len(found_backups) == 3
        assert found_backups[0] == backup_files[0]  # Oldest
        assert found_backups[1] == backup_files[1]
        assert found_backups[2] == backup_files[2]  # Newest

    def test_returns_empty_list_when_no_backups_exist(self, tmp_path: Path) -> None:
        """Test empty list when no backups exist."""
        # Arrange: Source file and empty backup directory
        source_file = tmp_path / "config.toml"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Act: Get backup files
        found_backups = get_backup_files(source_file, backup_dir)

        # Assert: Empty list returned
        assert len(found_backups) == 0

    def test_returns_empty_list_when_backup_dir_not_exists(
        self, tmp_path: Path
    ) -> None:
        """Test empty list when backup directory doesn't exist."""
        # Arrange: Source file without backup directory
        source_file = tmp_path / "config.toml"
        backup_dir = tmp_path / "nonexistent"

        # Act: Get backup files
        found_backups = get_backup_files(source_file, backup_dir)

        # Assert: Empty list returned
        assert len(found_backups) == 0

    def test_ignores_non_matching_files(self, tmp_path: Path) -> None:
        """Test that only matching backup files are returned."""
        # Arrange: Create backup directory with mixed files
        source_file = tmp_path / "config.toml"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create matching backups
        backup1 = backup_dir / "config.20250101_120000.toml"
        backup1.write_text("backup 1")
        backup2 = backup_dir / "config.20250102_120000.toml"
        backup2.write_text("backup 2")

        # Create non-matching files
        other1 = backup_dir / "other.20250101_120000.toml"
        other1.write_text("other backup")
        other2 = backup_dir / "config.txt"
        other2.write_text("different extension")

        # Act: Get backup files
        found_backups = get_backup_files(source_file, backup_dir)

        # Assert: Only matching backups returned
        assert len(found_backups) == 2
        assert backup1 in found_backups
        assert backup2 in found_backups
        assert other1 not in found_backups
        assert other2 not in found_backups


class TestIntegrationRotatingBackup:
    """Integration tests for full rotating backup workflow."""

    def test_full_rotation_workflow(self, tmp_path: Path) -> None:
        """Test complete workflow with multiple backup creations and rotation."""
        # Arrange: Create source file
        source_file = tmp_path / "config.toml"
        source_file.write_text("initial content")
        backup_dir = tmp_path / "backups"

        # Act: Create 12 backups (exceeding max of 10)
        for i in range(12):
            source_file.write_text(f"content version {i}")
            backup_path, success = create_rotating_backup(
                source_file, backup_dir=backup_dir, max_backups=10
            )
            assert success is True
            time.sleep(0.01)  # Ensure different timestamps

        # Assert: Only 10 backups remain (oldest 2 deleted)
        found_backups = get_backup_files(source_file, backup_dir)
        assert len(found_backups) == 10

    def test_handles_rapid_successive_backups(self, tmp_path: Path) -> None:
        """Test handling of rapid successive backup creation."""
        # Arrange: Create source file
        source_file = tmp_path / "config.toml"
        source_file.write_text("initial content")
        backup_dir = tmp_path / "backups"

        # Act: Create 5 backups in rapid succession
        for i in range(5):
            source_file.write_text(f"content {i}")
            backup_path, success = create_rotating_backup(
                source_file, backup_dir=backup_dir, max_backups=10
            )
            assert success is True

        # Assert: All backups created successfully
        found_backups = get_backup_files(source_file, backup_dir)
        assert len(found_backups) == 5

    def test_preserves_newest_backups_during_rotation(self, tmp_path: Path) -> None:
        """Test that newest backups are preserved during rotation."""
        # Arrange: Create source file
        source_file = tmp_path / "config.toml"
        backup_dir = tmp_path / "backups"

        # Act: Create 7 backups with max of 5, with delays to ensure different timestamps
        backup_paths = []
        for i in range(7):
            source_file.write_text(f"version {i}")
            backup_path, success = create_rotating_backup(
                source_file, backup_dir=backup_dir, max_backups=5
            )
            assert success is True
            backup_paths.append(backup_path)
            time.sleep(0.1)  # Longer delay to ensure different timestamps

        # Assert: Only 5 newest backups remain
        found_backups = get_backup_files(source_file, backup_dir)
        assert len(found_backups) == 5
        # Verify newest 5 backups exist
        for i in range(2, 7):  # Backups 2-6 should exist (0-1 deleted)
            assert backup_paths[i].exists()
        # Verify oldest 2 backups deleted
        assert not backup_paths[0].exists()
        assert not backup_paths[1].exists()
