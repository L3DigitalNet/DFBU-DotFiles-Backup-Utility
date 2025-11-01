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

import sys
from pathlib import Path
from typing import TYPE_CHECKING


# Local imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_types import DotFileDict, OptionsDict


# Type checking imports to avoid circular dependencies
if TYPE_CHECKING:
    from file_operations import FileOperations
    from statistics_tracker import StatisticsTracker


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
    ) -> None:
        """
        Initialize BackupOrchestrator.

        Args:
            file_ops: FileOperations instance
            stats_tracker: StatisticsTracker instance
            mirror_base_dir: Base directory for mirror backups
            archive_base_dir: Base directory for archive backups
        """
        self.file_ops = file_ops
        self.stats_tracker = stats_tracker
        self.mirror_base_dir = mirror_base_dir
        self.archive_base_dir = archive_base_dir

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
        validation_results: dict[int, tuple[bool, bool, str]] = {}

        for i, dotfile in enumerate(dotfiles):
            # Check all paths in this dotfile entry
            any_exists = False
            any_is_dir = False

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
        progress_callback: callable | None = None,
        item_processed_callback: callable | None = None,
        item_skipped_callback: callable | None = None,
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
        # Validate which dotfiles exist
        validation_results = self.validate_dotfile_paths(dotfiles)

        # Count total items that exist
        total_items = len([v for v in validation_results.values() if v[0]])

        if total_items == 0:
            return 0, 0

        processed_count = 0

        # Process each dotfile
        for i, dotfile in enumerate(dotfiles):
            # Skip disabled dotfiles
            if not dotfile.get("enabled", True):
                continue

            # Process each path
            for path_str in dotfile["paths"]:
                if not path_str:
                    continue

                src_path = self.file_ops.expand_path(path_str)

                if not src_path.exists():
                    continue

                is_dir = src_path.is_dir()

                # Assemble destination path
                dest_path = self.file_ops.assemble_dest_path(
                    self.mirror_base_dir,
                    src_path,
                    options["hostname_subdir"],
                    options["date_subdir"],
                )

                # Process based on type
                if is_dir:
                    file_count = self._process_directory_backup(
                        src_path,
                        dest_path,
                        skip_identical=True,
                        item_processed_callback=item_processed_callback,
                        item_skipped_callback=item_skipped_callback,
                    )
                    if file_count > 0:
                        processed_count += 1
                elif self._process_file_backup(
                    src_path,
                    dest_path,
                    skip_identical=True,
                    item_processed_callback=item_processed_callback,
                    item_skipped_callback=item_skipped_callback,
                ):
                    processed_count += 1

                # Update progress
                if progress_callback and total_items > 0:
                    progress = int((processed_count / total_items) * 100)
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
        # Build list of items to archive
        items_to_archive: list[tuple[Path, bool, bool]] = []

        for dotfile in dotfiles:
            # Skip disabled dotfiles
            if not dotfile.get("enabled", True):
                continue

            # Process each path
            for path_str in dotfile["paths"]:
                if not path_str:
                    continue

                src_path = self.file_ops.expand_path(path_str)

                if src_path.exists():
                    is_dir = src_path.is_dir()
                    items_to_archive.append((src_path, True, is_dir))

        if not items_to_archive:
            return None

        # Create archive
        archive_path = self.file_ops.create_archive(
            items_to_archive, self.archive_base_dir, options["hostname_subdir"]
        )

        # Rotate old archives if configured
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
        progress_callback: callable | None = None,
        item_processed_callback: callable | None = None,
    ) -> tuple[int, int]:
        """
        Execute restore operation from backup directory.

        Args:
            src_dir: Source backup directory
            progress_callback: Optional callback for progress updates (percent)
            item_processed_callback: Optional callback for processed items (src, dest)

        Returns:
            Tuple of (successful_items, total_items)
        """
        # Discover all files in backup
        src_files = self.file_ops.discover_restore_files(src_dir)
        total_items = len(src_files)

        if total_items == 0:
            return 0, 0

        # Reconstruct original paths
        restore_paths = self.file_ops.reconstruct_restore_paths(src_files)

        processed_count = 0

        # Copy files to restored locations
        for src_path, dest_path in restore_paths:
            if dest_path is None:
                continue

            # Copy file
            success = self.file_ops.copy_file(
                src_path, dest_path, create_parent=True, skip_identical=False
            )

            if success:
                processed_count += 1
                self.stats_tracker.record_item_processed(0.0)
                if item_processed_callback:
                    item_processed_callback(str(src_path), str(dest_path))
            else:
                self.stats_tracker.record_item_failed()

            # Update progress
            if progress_callback and total_items > 0:
                progress = int((processed_count / total_items) * 100)
                progress_callback(progress)

        return processed_count, total_items

    def _process_file_backup(
        self,
        src_path: Path,
        dest_path: Path,
        skip_identical: bool,
        item_processed_callback: callable | None = None,
        item_skipped_callback: callable | None = None,
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
        import time

        start_time = time.perf_counter()

        # Check readability
        if not self.file_ops.check_readable(src_path):
            if item_skipped_callback:
                item_skipped_callback(str(src_path), "Permission denied")
            self.stats_tracker.record_item_skipped()
            return False

        # Check if identical
        if skip_identical and self.file_ops.files_are_identical(src_path, dest_path):
            if item_skipped_callback:
                item_skipped_callback(str(src_path), "File unchanged")
            self.stats_tracker.record_item_skipped()
            return True

        # Copy file
        success = self.file_ops.copy_file(
            src_path, dest_path, create_parent=True, skip_identical=skip_identical
        )

        if success:
            elapsed = time.perf_counter() - start_time
            self.stats_tracker.record_item_processed(elapsed)
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
        item_processed_callback: callable | None = None,
        item_skipped_callback: callable | None = None,
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
        # Check readability
        if not self.file_ops.check_readable(src_path):
            if item_skipped_callback:
                item_skipped_callback(str(src_path), "Permission denied")
            self.stats_tracker.record_item_skipped()
            return 0

        # Copy directory
        results = self.file_ops.copy_directory(
            src_path, dest_path, skip_identical=skip_identical
        )

        # Process results
        success_count = 0
        for src_file, dest_file, success, skipped in results:
            if success:
                if skipped:
                    if item_skipped_callback:
                        item_skipped_callback(str(src_file), "File unchanged")
                    self.stats_tracker.record_item_skipped()
                else:
                    success_count += 1
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
