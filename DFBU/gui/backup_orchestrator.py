#!/usr/bin/env python3
"""
DFBU BackupOrchestrator - Backup and Restore Coordination Component

Description:
    Coordinates backup and restore operations for DFBU GUI, orchestrating
    interactions between FileOperations, ConfigManager, and StatisticsTracker.
    Part of the refactored MVVM architecture following Single Responsibility
    Principle.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 11-01-2025
License: MIT

Features:
    - Mirror backup orchestration with identical file skipping
    - Archive backup creation with compression
    - Restore operation coordination with path reconstruction
    - Progress tracking and statistics collection
    - Clean separation between orchestration and file operations

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - Requires: FileOperations, ConfigManager, StatisticsTracker components
    - Requires: common_types for TypedDict definitions

Classes:
    - BackupOrchestrator: Orchestrates backup and restore operations

Functions:
    None
"""

import logging
import sys
import time
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING


# Setup logger for this module
logger = logging.getLogger(__name__)


# Local imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import DotFileDict, OptionsDict, VerificationReportDict


# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from file_operations import FileOperations
    from statistics_tracker import StatisticsTracker
    from restore_backup_manager import RestoreBackupManager
    from verification_manager import VerificationManager


# =============================================================================
# BackupOrchestrator Class
# =============================================================================


class BackupOrchestrator:
    """
    Orchestrates backup and restore operations.

    Coordinates interactions between FileOperations, configuration data, and
    statistics tracking. Handles the business logic of backup and restore
    workflows without direct file I/O.

    Attributes:
        file_ops: FileOperations instance for file I/O
        stats_tracker: StatisticsTracker instance for metrics
        mirror_base_dir: Base directory for mirror backups
        archive_base_dir: Base directory for archive backups

    Public methods:
        execute_mirror_backup: Execute mirror backup for all enabled dotfiles
        execute_archive_backup: Create compressed archive of dotfiles
        execute_restore: Restore files from backup directory
        validate_dotfile_paths: Validate all dotfile paths exist

    Private methods:
        _process_file_backup: Process single file mirror backup
        _process_directory_backup: Process directory mirror backup recursively
    """

    def __init__(
        self,
        file_ops: FileOperations,
        stats_tracker: StatisticsTracker,
        mirror_base_dir: Path,
        archive_base_dir: Path,
        restore_backup_manager: RestoreBackupManager | None = None,
        verification_manager: VerificationManager | None = None,
    ) -> None:
        """
        Initialize BackupOrchestrator.

        Args:
            file_ops: FileOperations instance
            stats_tracker: StatisticsTracker instance
            mirror_base_dir: Base directory for mirror backups
            archive_base_dir: Base directory for archive backups
            restore_backup_manager: Optional RestoreBackupManager for pre-restore backups
            verification_manager: Optional VerificationManager for post-backup verification
        """
        self.file_ops = file_ops
        self.stats_tracker = stats_tracker
        self.mirror_base_dir = mirror_base_dir
        self.archive_base_dir = archive_base_dir
        self._restore_backup_manager = restore_backup_manager
        self._verification_manager = verification_manager
        self._last_backup_files: list[tuple[Path, Path]] = []  # (source, backup) pairs

    def validate_dotfile_paths(
        self, dotfiles: list[DotFileDict]
    ) -> dict[int, tuple[bool, bool, str]]:
        """
        Validate all dotfile paths exist and determine their types.

        Args:
            dotfiles: List of dotfile configurations

        Returns:
            Dict mapping dotfile index to (exists, is_dir, type_str) tuple
        """
        # Initialize validation results dictionary
        validation_results: dict[int, tuple[bool, bool, str]] = {}

        # Iterate through all dotfile entries
        for i, dotfile in enumerate(dotfiles):
            # Initialize flags for path existence and type checking
            any_exists = False
            any_is_dir = False

            # Check all paths in this dotfile entry
            for path_str in dotfile["paths"]:
                if not path_str:
                    continue

                path = self.file_ops.expand_path(path_str)
                if path.exists():
                    any_exists = True
                    if path.is_dir():
                        any_is_dir = True

            # Determine type string for display
            if any_exists:
                type_str = "Directory" if any_is_dir else "File"
            else:
                type_str = "Not Found"

            validation_results[i] = (any_exists, any_is_dir, type_str)

        return validation_results

    def execute_mirror_backup(
        self,
        dotfiles: list[DotFileDict],
        options: OptionsDict,
        progress_callback: Callable[[int], None] | None = None,
        item_processed_callback: Callable[[str, str], None] | None = None,
        item_skipped_callback: Callable[[str, str], None] | None = None,
    ) -> tuple[int, int]:
        """
        Execute mirror backup for all enabled dotfiles.

        Args:
            dotfiles: List of dotfile configurations
            options: Options configuration
            progress_callback: Optional callback for progress updates (percent)
            item_processed_callback: Optional callback for processed items (src, dest)
            item_skipped_callback: Optional callback for skipped items (src, reason)

        Returns:
            Tuple of (successful_items, total_items)
        """
        # Clear tracked files for fresh verification tracking
        self._last_backup_files.clear()

        # Validate which dotfiles exist in filesystem
        validation_results = self.validate_dotfile_paths(dotfiles)

        # Count total items that exist (for accurate progress calculation)
        total_items = len([v for v in validation_results.values() if v[0]])

        # Return early if no valid dotfiles found
        if total_items == 0:
            return 0, 0

        # Initialize counters for tracking backup progress
        processed_count = 0  # Tracks individual files processed
        completed_items = 0  # Tracks dotfile entries completed

        # Process each dotfile entry in configuration
        for dotfile in dotfiles:
            # Skip disabled dotfiles
            if not dotfile.get("enabled", True):
                continue

            # Process each path in dotfile entry
            for path_str in dotfile["paths"]:
                # Skip empty path strings
                if not path_str:
                    continue

                # Expand path with environment variables and user home directory
                src_path = self.file_ops.expand_path(path_str)

                # Skip non-existent paths
                if not src_path.exists():
                    continue

                # Determine if path is directory or file
                is_dir = src_path.is_dir()

                # Build destination path with hostname and date subdirectories
                dest_path = self.file_ops.assemble_dest_path(
                    self.mirror_base_dir,
                    src_path,
                    options["hostname_subdir"],
                    options["date_subdir"],
                )

                # Process based on file type (directory vs file)
                if is_dir:
                    file_count = self._process_directory_backup(
                        src_path,
                        dest_path,
                        skip_identical=True,
                        item_processed_callback=item_processed_callback,
                        item_skipped_callback=item_skipped_callback,
                    )
                    if file_count > 0:
                        processed_count += file_count
                elif self._process_file_backup(
                    src_path,
                    dest_path,
                    skip_identical=True,
                    item_processed_callback=item_processed_callback,
                    item_skipped_callback=item_skipped_callback,
                ):
                    processed_count += 1

                # Increment completed items counter for progress tracking
                completed_items += 1

                # Update progress based on completed items (not files processed)
                if progress_callback and total_items > 0:
                    progress = int((completed_items / total_items) * 100)
                    progress_callback(progress)

        return processed_count, total_items

    def execute_archive_backup(
        self, dotfiles: list[DotFileDict], options: OptionsDict
    ) -> Path | None:
        """
        Create compressed archive of all enabled dotfiles.

        Args:
            dotfiles: List of dotfile configurations
            options: Options configuration

        Returns:
            Path to created archive, or None if failed
        """
        # Build list of items to include in archive (tuples of path, enabled, is_dir)
        items_to_archive: list[tuple[Path, bool, bool]] = []

        # Collect all enabled dotfile paths that exist
        for dotfile in dotfiles:
            # Skip disabled dotfiles
            if not dotfile.get("enabled", True):
                continue

            # Process each path in dotfile entry
            for path_str in dotfile["paths"]:
                # Skip empty path strings
                if not path_str:
                    continue

                # Expand path with environment variables and user home directory
                src_path = self.file_ops.expand_path(path_str)

                # Add existing paths to archive list
                if src_path.exists():
                    is_dir = src_path.is_dir()
                    items_to_archive.append((src_path, True, is_dir))

        # Return None if no items found to archive
        if not items_to_archive:
            return None

        # Create compressed archive with timestamp
        archive_path = self.file_ops.create_archive(
            items_to_archive, self.archive_base_dir, options["hostname_subdir"]
        )

        # Rotate old archives if enabled and archive created successfully
        if archive_path and options["rotate_archives"]:
            self.file_ops.rotate_archives(
                self.archive_base_dir,
                options["hostname_subdir"],
                options["max_archives"],
            )

        return archive_path

    def execute_restore(
        self,
        src_dir: Path,
        pre_restore_enabled: bool = True,
        progress_callback: Callable[[int], None] | None = None,
        item_processed_callback: Callable[[str, str], None] | None = None,
    ) -> tuple[int, int]:
        """
        Execute restore operation from backup directory.

        Args:
            src_dir: Source backup directory
            pre_restore_enabled: Whether to create pre-restore backup (default: True)
            progress_callback: Optional callback for progress updates (percent)
            item_processed_callback: Optional callback for processed items (src, dest)

        Returns:
            Tuple of (successful_items, total_items)
        """
        # Discover all files in backup directory recursively
        src_files = self.file_ops.discover_restore_files(src_dir)
        total_items = len(src_files)

        # Return early if no files found in backup
        if total_items == 0:
            return 0, 0

        # Reconstruct original filesystem paths from backup structure
        restore_paths = self.file_ops.reconstruct_restore_paths(src_files)

        # Pre-restore backup: backup files that will be overwritten
        if pre_restore_enabled and self._restore_backup_manager is not None:
            dest_paths = [dest for _, dest in restore_paths if dest is not None]
            success, error, _ = self._restore_backup_manager.backup_before_restore(
                files_to_overwrite=dest_paths,
                source_backup_path=str(src_dir),
            )
            if not success:
                logger.error(f"Pre-restore backup failed: {error}")
                return 0, total_items

            # Cleanup old backups to enforce retention policy
            self._restore_backup_manager.cleanup_old_backups()

        # Initialize counter for successful restore operations
        processed_count = 0

        # Copy each file from backup to original location
        for src_path, dest_path in restore_paths:
            # Skip if path reconstruction failed
            if dest_path is None:
                continue

            # Copy file with metadata preservation
            success = self.file_ops.copy_file(
                src_path, dest_path, create_parent=True, skip_identical=False
            )

            # Track restore statistics and notify callbacks
            if success:
                processed_count += 1
                self.stats_tracker.record_item_processed(0.0)
                if item_processed_callback:
                    item_processed_callback(str(src_path), str(dest_path))
            else:
                self.stats_tracker.record_item_failed()

            # Update progress callback with percentage completed
            if progress_callback and total_items > 0:
                progress = int((processed_count / total_items) * 100)
                progress_callback(progress)

        return processed_count, total_items

    def verify_last_backup(self) -> VerificationReportDict | None:
        """
        Verify the integrity of the last mirror backup operation.

        Uses the tracked source/backup file pairs from the most recent
        execute_mirror_backup call to verify all files were backed up correctly.

        Returns:
            VerificationReportDict with results, or None if:
            - No verification manager is configured
            - No backup has been performed yet
            - No files were tracked during backup
        """
        if self._verification_manager is None:
            logger.warning("Verification requested but no VerificationManager configured")
            return None

        if not self._last_backup_files:
            logger.warning("No backup files to verify - run a backup first")
            return None

        logger.info(f"Starting verification of {len(self._last_backup_files)} files")

        report = self._verification_manager.verify_backup(
            backup_path=self.mirror_base_dir,
            source_paths=self._last_backup_files,
            backup_type="mirror",
        )

        return report

    def get_last_backup_file_count(self) -> int:
        """
        Get the number of files tracked from the last backup operation.

        Returns:
            Number of source/backup file pairs tracked
        """
        return len(self._last_backup_files)

    def _process_file_backup(
        self,
        src_path: Path,
        dest_path: Path,
        skip_identical: bool,
        item_processed_callback: Callable[[str, str], None] | None = None,
        item_skipped_callback: Callable[[str, str], None] | None = None,
    ) -> bool:
        """
        Process single file mirror backup.

        Args:
            src_path: Source file path
            dest_path: Destination file path
            skip_identical: Whether to skip copying if identical
            item_processed_callback: Optional callback for processed items
            item_skipped_callback: Optional callback for skipped items

        Returns:
            True if successful or skipped, False otherwise
        """
        # Record operation start time for statistics
        start_time = time.perf_counter()

        # Verify source file is readable
        if not self.file_ops.check_readable(src_path):
            if item_skipped_callback:
                item_skipped_callback(str(src_path), "Permission denied")
            self.stats_tracker.record_item_skipped()
            return False

        # Skip copying if files are identical (optimization)
        if skip_identical and self.file_ops.files_are_identical(src_path, dest_path):
            if item_skipped_callback:
                item_skipped_callback(str(src_path), "File unchanged")
            self.stats_tracker.record_item_skipped()
            # Track skipped files too - they should still verify
            self._last_backup_files.append((src_path, dest_path))
            return True

        # Perform file copy operation with metadata preservation
        success = self.file_ops.copy_file(
            src_path, dest_path, create_parent=True, skip_identical=skip_identical
        )

        # Record statistics and notify callbacks based on operation result
        if success:
            elapsed = time.perf_counter() - start_time
            self.stats_tracker.record_item_processed(elapsed)
            # Track successfully backed up files for verification
            self._last_backup_files.append((src_path, dest_path))
            if item_processed_callback:
                item_processed_callback(str(src_path), str(dest_path))
        else:
            self.stats_tracker.record_item_failed()

        return success

    def _process_directory_backup(
        self,
        src_path: Path,
        dest_path: Path,
        skip_identical: bool,
        item_processed_callback: Callable[[str, str], None] | None = None,
        item_skipped_callback: Callable[[str, str], None] | None = None,
    ) -> int:
        """
        Process directory mirror backup recursively.

        Args:
            src_path: Source directory path
            dest_path: Destination directory path
            skip_identical: Whether to skip copying if identical
            item_processed_callback: Optional callback for processed items
            item_skipped_callback: Optional callback for skipped items

        Returns:
            Number of successfully copied files
        """
        # Verify source directory is readable
        if not self.file_ops.check_readable(src_path):
            if item_skipped_callback:
                item_skipped_callback(str(src_path), "Permission denied")
            self.stats_tracker.record_item_skipped()
            return 0

        # Recursively copy directory contents with metadata preservation
        results = self.file_ops.copy_directory(
            src_path, dest_path, skip_identical=skip_identical
        )

        # Process results and track statistics for each file
        success_count = 0
        for src_file, dest_file, success, skipped in results:
            if success:
                if skipped:
                    if item_skipped_callback:
                        item_skipped_callback(str(src_file), "File unchanged")
                    self.stats_tracker.record_item_skipped()
                    # Track skipped files for verification
                    if dest_file is not None:
                        self._last_backup_files.append((src_file, dest_file))
                else:
                    success_count += 1
                    # Track successfully backed up files for verification
                    if dest_file is not None:
                        self._last_backup_files.append((src_file, dest_file))
                    if item_processed_callback:
                        item_processed_callback(str(src_file), str(dest_file))
                    self.stats_tracker.record_item_processed(0.0)
            elif dest_file is None:
                if item_skipped_callback:
                    item_skipped_callback(
                        str(src_file), "Permission denied or read error"
                    )
                self.stats_tracker.record_item_skipped()
            else:
                self.stats_tracker.record_item_failed()

        return success_count
