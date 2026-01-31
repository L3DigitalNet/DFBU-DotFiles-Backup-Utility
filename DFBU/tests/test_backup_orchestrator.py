#!/usr/bin/env python3
"""
Tests for BackupOrchestrator - Backup and Restore Coordination

Description:
    Comprehensive test suite for the BackupOrchestrator class, validating
    backup coordination, restore operations, progress tracking, and statistics
    integration.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 11-01-2025
License: MIT
"""

import sys
from pathlib import Path
from unittest.mock import Mock


# Add gui directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))

from backup_orchestrator import BackupOrchestrator
from file_operations import FileOperations
from statistics_tracker import StatisticsTracker


class TestBackupOrchestratorInitialization:
    """Test BackupOrchestrator initialization."""

    def test_orchestrator_initialization(self, tmp_path: Path) -> None:
        """Test BackupOrchestrator initializes with required components."""
        # Arrange
        file_ops = Mock(spec=FileOperations)
        stats_tracker = Mock(spec=StatisticsTracker)
        mirror_base = tmp_path / "mirror"
        archive_base = tmp_path / "archive"

        # Act
        orchestrator = BackupOrchestrator(
            file_ops, stats_tracker, mirror_base, archive_base
        )

        # Assert
        assert orchestrator.file_ops is file_ops
        assert orchestrator.stats_tracker is stats_tracker
        assert orchestrator.mirror_base_dir == mirror_base
        assert orchestrator.archive_base_dir == archive_base


class TestValidateDotfilePaths:
    """Test dotfile path validation."""

    def test_validate_paths_all_exist(self, tmp_path: Path) -> None:
        """Test validation when all paths exist."""
        # Arrange
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.side_effect = lambda p: Path(p.replace("~", str(tmp_path)))
        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        dotfiles = [
            {"paths": [str(test_file)]},
            {"paths": [str(test_dir)]},
        ]

        # Act
        results = orchestrator.validate_dotfile_paths(dotfiles)

        # Assert
        assert len(results) == 2
        assert results[0] == (True, False, "File")
        assert results[1] == (True, True, "Directory")

    def test_validate_paths_nonexistent(self, tmp_path: Path) -> None:
        """Test validation when paths don't exist."""
        # Arrange
        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.return_value = tmp_path / "nonexistent"
        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        dotfiles = [{"paths": ["/nonexistent/path"]}]

        # Act
        results = orchestrator.validate_dotfile_paths(dotfiles)

        # Assert
        assert results[0] == (False, False, "Not Found")

    def test_validate_paths_empty_path_string(self, tmp_path: Path) -> None:
        """Test validation skips empty path strings."""
        # Arrange
        file_ops = Mock(spec=FileOperations)
        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        dotfiles = [{"paths": [""]}]

        # Act
        results = orchestrator.validate_dotfile_paths(dotfiles)

        # Assert
        assert results[0] == (False, False, "Not Found")

    def test_validate_paths_multiple_paths_per_dotfile(self, tmp_path: Path) -> None:
        """Test validation with multiple paths in single dotfile."""
        # Arrange
        file1 = tmp_path / "file1.txt"
        file1.write_text("content")
        dir1 = tmp_path / "dir1"
        dir1.mkdir()

        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.side_effect = lambda p: Path(p.replace("~", str(tmp_path)))
        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        dotfiles = [{"paths": [str(file1), str(dir1)]}]

        # Act
        results = orchestrator.validate_dotfile_paths(dotfiles)

        # Assert
        assert results[0] == (True, True, "Directory")  # Directory detected in paths


class TestExecuteMirrorBackup:
    """Test mirror backup execution."""

    def test_mirror_backup_no_valid_dotfiles(self, tmp_path: Path) -> None:
        """Test mirror backup returns early when no valid dotfiles exist."""
        # Arrange
        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.return_value = tmp_path / "nonexistent"
        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        dotfiles = [{"paths": ["/nonexistent"], "enabled": True}]
        options = {"hostname_subdir": True, "date_subdir": False}

        # Act
        processed, total = orchestrator.execute_mirror_backup(dotfiles, options)

        # Assert
        assert processed == 0
        assert total == 0

    def test_mirror_backup_skips_disabled_dotfiles(self, tmp_path: Path) -> None:
        """Test mirror backup skips disabled dotfiles."""
        # Arrange
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.return_value = test_file
        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        dotfiles = [{"paths": [str(test_file)], "enabled": False}]
        options = {"hostname_subdir": True, "date_subdir": False}

        # Act
        processed, total = orchestrator.execute_mirror_backup(dotfiles, options)

        # Assert
        assert processed == 0
        # Total might still count the dotfile even if disabled in validation

    def test_mirror_backup_processes_file(self, tmp_path: Path) -> None:
        """Test mirror backup processes a single file."""
        # Arrange
        src_file = tmp_path / "source" / "test.txt"
        src_file.parent.mkdir()
        src_file.write_text("content")

        dest_dir = tmp_path / "dest"

        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.return_value = src_file
        file_ops.assemble_dest_path.return_value = dest_dir / "test.txt"
        file_ops.check_readable.return_value = True
        file_ops.files_are_identical.return_value = False
        file_ops.copy_file.return_value = True

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(
            file_ops, stats_tracker, tmp_path / "mirror", tmp_path / "archive"
        )

        dotfiles = [{"paths": [str(src_file)], "enabled": True}]
        options = {"hostname_subdir": False, "date_subdir": False}

        # Act
        processed, total = orchestrator.execute_mirror_backup(dotfiles, options)

        # Assert
        assert processed == 1
        assert total == 1
        file_ops.copy_file.assert_called_once()
        stats_tracker.record_item_processed.assert_called_once()

    def test_mirror_backup_processes_directory(self, tmp_path: Path) -> None:
        """Test mirror backup processes a directory."""
        # Arrange
        src_dir = tmp_path / "source" / "mydir"
        src_dir.mkdir(parents=True)
        (src_dir / "file1.txt").write_text("content1")
        (src_dir / "file2.txt").write_text("content2")

        dest_dir = tmp_path / "dest"

        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.return_value = src_dir
        file_ops.assemble_dest_path.return_value = dest_dir / "mydir"
        file_ops.check_readable.return_value = True
        # Simulate copy_directory returning 2 successful files
        file_ops.copy_directory.return_value = [
            (src_dir / "file1.txt", dest_dir / "file1.txt", True, False),
            (src_dir / "file2.txt", dest_dir / "file2.txt", True, False),
        ]

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(
            file_ops, stats_tracker, tmp_path / "mirror", tmp_path / "archive"
        )

        dotfiles = [{"paths": [str(src_dir)], "enabled": True}]
        options = {"hostname_subdir": False, "date_subdir": False}

        # Act
        processed, total = orchestrator.execute_mirror_backup(dotfiles, options)

        # Assert
        assert processed == 2  # Two files processed
        assert total == 1  # One dotfile entry
        file_ops.copy_directory.assert_called_once()

    def test_mirror_backup_with_progress_callback(self, tmp_path: Path) -> None:
        """Test mirror backup calls progress callback."""
        # Arrange
        src_file = tmp_path / "test.txt"
        src_file.write_text("content")

        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.return_value = src_file
        file_ops.assemble_dest_path.return_value = tmp_path / "dest" / "test.txt"
        file_ops.check_readable.return_value = True
        file_ops.files_are_identical.return_value = False
        file_ops.copy_file.return_value = True

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        dotfiles = [{"paths": [str(src_file)], "enabled": True}]
        options = {"hostname_subdir": False, "date_subdir": False}

        progress_callback = Mock()

        # Act
        orchestrator.execute_mirror_backup(
            dotfiles, options, progress_callback=progress_callback
        )

        # Assert
        progress_callback.assert_called_with(100)  # Called with 100% at end

    def test_mirror_backup_with_item_callbacks(self, tmp_path: Path) -> None:
        """Test mirror backup calls item processed and skipped callbacks."""
        # Arrange
        src_file = tmp_path / "test.txt"
        src_file.write_text("content")

        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.return_value = src_file
        file_ops.assemble_dest_path.return_value = tmp_path / "dest" / "test.txt"
        file_ops.check_readable.return_value = True
        file_ops.files_are_identical.return_value = False
        file_ops.copy_file.return_value = True

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        dotfiles = [{"paths": [str(src_file)], "enabled": True}]
        options = {"hostname_subdir": False, "date_subdir": False}

        processed_callback = Mock()
        skipped_callback = Mock()

        # Act
        orchestrator.execute_mirror_backup(
            dotfiles,
            options,
            item_processed_callback=processed_callback,
            item_skipped_callback=skipped_callback,
        )

        # Assert
        processed_callback.assert_called_once()


class TestExecuteArchiveBackup:
    """Test archive backup execution."""

    def test_archive_backup_no_enabled_dotfiles(self, tmp_path: Path) -> None:
        """Test archive backup returns None when no enabled dotfiles."""
        # Arrange
        file_ops = Mock(spec=FileOperations)
        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        dotfiles = [{"paths": ["/nonexistent"], "enabled": False}]
        options = {
            "hostname_subdir": False,
            "rotate_archives": False,
            "max_archives": 10,
        }

        # Act
        result = orchestrator.execute_archive_backup(dotfiles, options)

        # Assert
        assert result is None

    def test_archive_backup_creates_archive(self, tmp_path: Path) -> None:
        """Test archive backup creates archive for enabled dotfiles."""
        # Arrange
        src_file = tmp_path / "test.txt"
        src_file.write_text("content")

        archive_path = tmp_path / "archive" / "backup.tar.gz"

        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.return_value = src_file
        file_ops.create_archive.return_value = archive_path

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(
            file_ops, stats_tracker, tmp_path / "mirror", tmp_path / "archive"
        )

        dotfiles = [{"paths": [str(src_file)], "enabled": True}]
        options = {
            "hostname_subdir": False,
            "rotate_archives": False,
            "max_archives": 10,
        }

        # Act
        result = orchestrator.execute_archive_backup(dotfiles, options)

        # Assert
        assert result == archive_path
        file_ops.create_archive.assert_called_once()

    def test_archive_backup_with_rotation(self, tmp_path: Path) -> None:
        """Test archive backup rotates old archives when enabled."""
        # Arrange
        src_file = tmp_path / "test.txt"
        src_file.write_text("content")

        archive_path = tmp_path / "archive" / "backup.tar.gz"

        file_ops = Mock(spec=FileOperations)
        file_ops.expand_path.return_value = src_file
        file_ops.create_archive.return_value = archive_path
        file_ops.rotate_archives.return_value = None

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(
            file_ops, stats_tracker, tmp_path / "mirror", tmp_path / "archive"
        )

        dotfiles = [{"paths": [str(src_file)], "enabled": True}]
        options = {
            "hostname_subdir": True,
            "rotate_archives": True,
            "max_archives": 5,
        }

        # Act
        result = orchestrator.execute_archive_backup(dotfiles, options)

        # Assert
        assert result == archive_path
        file_ops.rotate_archives.assert_called_once_with(tmp_path / "archive", True, 5)

    def test_archive_backup_skips_empty_paths(self, tmp_path: Path) -> None:
        """Test archive backup skips empty path strings."""
        # Arrange
        file_ops = Mock(spec=FileOperations)
        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        dotfiles = [{"paths": [""], "enabled": True}]
        options = {
            "hostname_subdir": False,
            "rotate_archives": False,
            "max_archives": 10,
        }

        # Act
        result = orchestrator.execute_archive_backup(dotfiles, options)

        # Assert
        assert result is None  # No valid items to archive


class TestExecuteRestore:
    """Test restore operation execution."""

    def test_restore_no_files_in_backup(self, tmp_path: Path) -> None:
        """Test restore returns early when no files in backup."""
        # Arrange
        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()

        file_ops = Mock(spec=FileOperations)
        file_ops.discover_restore_files.return_value = []

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        # Act
        processed, total = orchestrator.execute_restore(backup_dir)

        # Assert
        assert processed == 0
        assert total == 0

    def test_restore_processes_files(self, tmp_path: Path) -> None:
        """Test restore processes files from backup."""
        # Arrange
        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()

        src_file1 = backup_dir / "file1.txt"
        src_file2 = backup_dir / "file2.txt"
        dest_file1 = tmp_path / "restored" / "file1.txt"
        dest_file2 = tmp_path / "restored" / "file2.txt"

        file_ops = Mock(spec=FileOperations)
        file_ops.discover_restore_files.return_value = [src_file1, src_file2]
        file_ops.reconstruct_restore_paths.return_value = [
            (src_file1, dest_file1),
            (src_file2, dest_file2),
        ]
        file_ops.copy_file.return_value = True

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        # Act
        processed, total = orchestrator.execute_restore(backup_dir)

        # Assert
        assert processed == 2
        assert total == 2
        assert file_ops.copy_file.call_count == 2

    def test_restore_with_progress_callback(self, tmp_path: Path) -> None:
        """Test restore calls progress callback."""
        # Arrange
        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()

        src_file = backup_dir / "file.txt"
        dest_file = tmp_path / "restored" / "file.txt"

        file_ops = Mock(spec=FileOperations)
        file_ops.discover_restore_files.return_value = [src_file]
        file_ops.reconstruct_restore_paths.return_value = [(src_file, dest_file)]
        file_ops.copy_file.return_value = True

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        progress_callback = Mock()

        # Act
        orchestrator.execute_restore(backup_dir, progress_callback=progress_callback)

        # Assert
        progress_callback.assert_called_with(100)

    def test_restore_with_item_processed_callback(self, tmp_path: Path) -> None:
        """Test restore calls item processed callback."""
        # Arrange
        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()

        src_file = backup_dir / "file.txt"
        dest_file = tmp_path / "restored" / "file.txt"

        file_ops = Mock(spec=FileOperations)
        file_ops.discover_restore_files.return_value = [src_file]
        file_ops.reconstruct_restore_paths.return_value = [(src_file, dest_file)]
        file_ops.copy_file.return_value = True

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        item_callback = Mock()

        # Act
        orchestrator.execute_restore(backup_dir, item_processed_callback=item_callback)

        # Assert
        item_callback.assert_called_once()

    def test_restore_skips_none_dest_paths(self, tmp_path: Path) -> None:
        """Test restore skips files with None destination paths."""
        # Arrange
        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()

        src_file = backup_dir / "file.txt"

        file_ops = Mock(spec=FileOperations)
        file_ops.discover_restore_files.return_value = [src_file]
        file_ops.reconstruct_restore_paths.return_value = [(src_file, None)]

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        # Act
        processed, total = orchestrator.execute_restore(backup_dir)

        # Assert
        assert processed == 0
        assert total == 1
        file_ops.copy_file.assert_not_called()

    def test_restore_handles_copy_failures(self, tmp_path: Path) -> None:
        """Test restore handles copy failures gracefully."""
        # Arrange
        backup_dir = tmp_path / "backup"
        backup_dir.mkdir()

        src_file = backup_dir / "file.txt"
        dest_file = tmp_path / "restored" / "file.txt"

        file_ops = Mock(spec=FileOperations)
        file_ops.discover_restore_files.return_value = [src_file]
        file_ops.reconstruct_restore_paths.return_value = [(src_file, dest_file)]
        file_ops.copy_file.return_value = False  # Simulate failure

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        # Act
        processed, total = orchestrator.execute_restore(backup_dir)

        # Assert
        assert processed == 0  # No successful copies
        assert total == 1
        stats_tracker.record_item_failed.assert_called_once()


class TestProcessFileBackup:
    """Test private file backup processing."""

    def test_process_file_backup_permission_denied(self, tmp_path: Path) -> None:
        """Test file backup handles permission denied."""
        # Arrange
        src_file = tmp_path / "test.txt"
        dest_file = tmp_path / "dest" / "test.txt"

        file_ops = Mock(spec=FileOperations)
        file_ops.check_readable.return_value = False

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        skipped_callback = Mock()

        # Act
        result = orchestrator._process_file_backup(
            src_file, dest_file, True, item_skipped_callback=skipped_callback
        )

        # Assert
        assert result is False
        skipped_callback.assert_called_once_with(str(src_file), "Permission denied")
        stats_tracker.record_item_skipped.assert_called_once()

    def test_process_file_backup_identical_file_skipped(self, tmp_path: Path) -> None:
        """Test file backup skips identical files when enabled."""
        # Arrange
        src_file = tmp_path / "test.txt"
        dest_file = tmp_path / "dest" / "test.txt"

        file_ops = Mock(spec=FileOperations)
        file_ops.check_readable.return_value = True
        file_ops.files_are_identical.return_value = True

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        skipped_callback = Mock()

        # Act
        result = orchestrator._process_file_backup(
            src_file, dest_file, True, item_skipped_callback=skipped_callback
        )

        # Assert
        assert result is True  # Returns True for skipped identical files
        skipped_callback.assert_called_once_with(str(src_file), "File unchanged")
        stats_tracker.record_item_skipped.assert_called_once()


class TestProcessDirectoryBackup:
    """Test private directory backup processing."""

    def test_process_directory_backup_permission_denied(self, tmp_path: Path) -> None:
        """Test directory backup handles permission denied."""
        # Arrange
        src_dir = tmp_path / "mydir"
        dest_dir = tmp_path / "dest" / "mydir"

        file_ops = Mock(spec=FileOperations)
        file_ops.check_readable.return_value = False

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        skipped_callback = Mock()

        # Act
        count = orchestrator._process_directory_backup(
            src_dir, dest_dir, True, item_skipped_callback=skipped_callback
        )

        # Assert
        assert count == 0
        skipped_callback.assert_called_once_with(str(src_dir), "Permission denied")
        stats_tracker.record_item_skipped.assert_called_once()

    def test_process_directory_backup_processes_results(self, tmp_path: Path) -> None:
        """Test directory backup processes copy_directory results."""
        # Arrange
        src_dir = tmp_path / "mydir"
        dest_dir = tmp_path / "dest" / "mydir"

        file1 = src_dir / "file1.txt"
        file2 = src_dir / "file2.txt"
        dest1 = dest_dir / "file1.txt"
        dest2 = dest_dir / "file2.txt"

        file_ops = Mock(spec=FileOperations)
        file_ops.check_readable.return_value = True
        file_ops.copy_directory.return_value = [
            (file1, dest1, True, False),  # Success, not skipped
            (file2, dest2, True, True),  # Success, skipped (identical)
        ]

        stats_tracker = Mock(spec=StatisticsTracker)

        orchestrator = BackupOrchestrator(file_ops, stats_tracker, tmp_path, tmp_path)

        processed_callback = Mock()
        skipped_callback = Mock()

        # Act
        count = orchestrator._process_directory_backup(
            src_dir,
            dest_dir,
            True,
            item_processed_callback=processed_callback,
            item_skipped_callback=skipped_callback,
        )

        # Assert
        assert count == 1  # Only one file actually copied
        processed_callback.assert_called_once()
        skipped_callback.assert_called_once()


class TestRestoreWithPreBackup:
    """Test restore operation with pre-restore backup."""

    def test_restore_calls_pre_backup(self, tmp_path: Path) -> None:
        """Test restore calls RestoreBackupManager before restoring."""
        # Arrange
        file_ops = Mock(spec=FileOperations)
        stats_tracker = Mock(spec=StatisticsTracker)
        restore_backup_mgr = Mock()
        restore_backup_mgr.backup_before_restore.return_value = (True, "", tmp_path / "backup")

        # Setup source files
        src_dir = tmp_path / "backup"
        src_dir.mkdir()
        (src_dir / "test.txt").write_text("content")

        file_ops.discover_restore_files.return_value = [src_dir / "test.txt"]
        file_ops.reconstruct_restore_paths.return_value = [
            (src_dir / "test.txt", Path.home() / ".test.txt")
        ]
        file_ops.copy_file.return_value = True

        orchestrator = BackupOrchestrator(
            file_ops, stats_tracker, tmp_path, tmp_path,
            restore_backup_manager=restore_backup_mgr,
        )

        # Act
        orchestrator.execute_restore(src_dir)

        # Assert
        restore_backup_mgr.backup_before_restore.assert_called_once()

    def test_restore_aborts_if_pre_backup_fails(self, tmp_path: Path) -> None:
        """Test restore aborts if pre-backup fails."""
        # Arrange
        file_ops = Mock(spec=FileOperations)
        stats_tracker = Mock(spec=StatisticsTracker)
        restore_backup_mgr = Mock()
        restore_backup_mgr.backup_before_restore.return_value = (
            False, "Disk full", None
        )

        src_dir = tmp_path / "backup"
        src_dir.mkdir()
        (src_dir / "test.txt").write_text("content")

        file_ops.discover_restore_files.return_value = [src_dir / "test.txt"]
        file_ops.reconstruct_restore_paths.return_value = [
            (src_dir / "test.txt", Path.home() / ".test.txt")
        ]

        orchestrator = BackupOrchestrator(
            file_ops, stats_tracker, tmp_path, tmp_path,
            restore_backup_manager=restore_backup_mgr,
        )

        # Act
        processed, total = orchestrator.execute_restore(src_dir)

        # Assert
        assert processed == 0
        file_ops.copy_file.assert_not_called()

    def test_restore_works_without_backup_manager(self, tmp_path: Path) -> None:
        """Test restore still works when no backup manager provided."""
        # Arrange
        file_ops = Mock(spec=FileOperations)
        stats_tracker = Mock(spec=StatisticsTracker)

        src_dir = tmp_path / "backup"
        src_dir.mkdir()
        (src_dir / "test.txt").write_text("content")

        file_ops.discover_restore_files.return_value = [src_dir / "test.txt"]
        file_ops.reconstruct_restore_paths.return_value = [
            (src_dir / "test.txt", tmp_path / ".test.txt")
        ]
        file_ops.copy_file.return_value = True

        # No restore_backup_manager provided
        orchestrator = BackupOrchestrator(
            file_ops, stats_tracker, tmp_path, tmp_path
        )

        # Act
        processed, total = orchestrator.execute_restore(src_dir)

        # Assert
        assert processed == 1
        file_ops.copy_file.assert_called_once()
