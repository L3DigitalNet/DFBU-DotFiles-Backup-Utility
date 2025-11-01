#!/usr/bin/env python3
"""
DFBU Model - Data and Business Logic Layer

Description:
    Model layer for DFBU GUI implementing MVVM pattern. Manages application
    state, configuration loading, file operations, and backup/restore business
    logic. Independent of UI presentation concerns.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 10-31-2025
License: MIT

Features:
    - MVVM Model layer with clean separation from View and ViewModel
    - Centralized backup/restore state management
    - TOML configuration loading and validation
    - Dynamic dotfile entry management (add/update/remove)
    - File discovery and validation for backup operations
    - Business logic for mirror and archive backup operations
    - Archive rotation based on retention policies
    - Restore path reconstruction and validation
    - Python standard library first approach with minimal dependencies
    - Clean architecture with confident design patterns

Requirements:
    - Linux environment
    - Python 3.14+ for latest Path.copy() with metadata preservation
    - Standard library only: pathlib, tomllib, tomli_w, tarfile, socket, time, datetime, os, sys, shutil
    - Rotating backup utilities included inline (no external dependencies)

Classes:
    - DotFileDict: TypedDict for dotfile configuration
    - OptionsDict: TypedDict for options configuration
    - BackupStatistics: Data class for backup operation metrics
    - DFBUModel: Main model class managing application state

Functions:
    None
"""

import os
import shutil
import tarfile
import time
import tomllib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from socket import gethostname
from typing import Any, Final, TypedDict

import tomli_w


# =============================================================================
# Constants
# =============================================================================


# File modification time comparison tolerance in seconds
# Accounts for filesystem timestamp precision differences across systems
FILE_MTIME_TOLERANCE_SECONDS: Final[float] = 1.0


# =============================================================================
# Utility Functions (formerly from common_lib/file_backup.py)
# =============================================================================


def create_rotating_backup(
    source_path: Path,
    backup_dir: Path | None = None,
    max_backups: int = 10,
    timestamp_format: str = "%Y%m%d_%H%M%S",
) -> tuple[Path | None, bool]:
    """
    Create a timestamped backup of a file and rotate old backups.

    Creates a backup copy of the source file in the backup directory with a
    timestamp. Automatically rotates old backups to maintain the maximum count.
    If backup_dir is None, backups are created in the same directory as the
    source file with a '.backups' suffix.

    Args:
        source_path: Path to file to backup
        backup_dir: Directory for backup storage (default: source_path.parent / '.backups')
        max_backups: Maximum number of backups to retain (default: 10)
        timestamp_format: strftime format for timestamp (default: ISO 8601 compatible)

    Returns:
        Tuple of (backup_path, success). backup_path is None if operation failed.
    """
    # Source file must exist
    if not source_path.exists() or not source_path.is_file():
        return None, False

    # Determine backup directory location
    if backup_dir is None:
        backup_dir = source_path.parent / f".{source_path.name}.backups"

    # Create backup directory if needed
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError):
        return None, False

    # Generate timestamped backup filename with collision handling
    timestamp = datetime.now().strftime(timestamp_format)
    backup_name = f"{source_path.stem}.{timestamp}{source_path.suffix}"
    backup_path = backup_dir / backup_name

    # Handle filename collision by adding counter suffix
    counter = 0
    while backup_path.exists():
        counter += 1
        backup_name = f"{source_path.stem}.{timestamp}.{counter}{source_path.suffix}"
        backup_path = backup_dir / backup_name

    # Copy file to backup location
    try:
        shutil.copy2(source_path, backup_path)
    except (OSError, PermissionError, shutil.Error):
        return backup_path, False

    # Rotate old backups to maintain maximum count
    rotate_old_backups(source_path, backup_dir, max_backups)

    return backup_path, True


def rotate_old_backups(
    source_path: Path,
    backup_dir: Path,
    max_backups: int,
) -> list[Path]:
    """
    Delete oldest backups exceeding maximum retention limit.

    Finds all backup files for the source file and deletes the oldest ones
    to maintain the maximum backup count. Backups are identified by matching
    the source file's stem and suffix with timestamp in between.

    Args:
        source_path: Original file that was backed up
        backup_dir: Directory containing backup files
        max_backups: Maximum number of backups to retain

    Returns:
        List of deleted backup file paths
    """
    deleted_backups: list[Path] = []

    # Get all backup files for this source file
    backup_files = get_backup_files(source_path, backup_dir)

    # Calculate number to delete
    num_to_delete = len(backup_files) - max_backups

    # Delete oldest backups if we exceed the limit
    if num_to_delete > 0:
        for i in range(num_to_delete):
            try:
                backup_files[i].unlink()
                deleted_backups.append(backup_files[i])
            except OSError:
                # Skip files that can't be deleted
                continue

    return deleted_backups


def get_backup_files(
    source_path: Path,
    backup_dir: Path,
) -> list[Path]:
    """
    Find all backup files for a specific source file.

    Searches the backup directory for files matching the source file's naming
    pattern. Returns files sorted by modification time (oldest first).

    Args:
        source_path: Original file that was backed up
        backup_dir: Directory containing backup files

    Returns:
        List of backup file paths sorted by age (oldest first)
    """
    # Backup directory must exist
    if not backup_dir.exists():
        return []

    # Build glob pattern to match backup files
    # Pattern: {stem}.{timestamp}{suffix}
    pattern = f"{source_path.stem}.*{source_path.suffix}"

    # Find all matching backup files with error handling
    backup_list: list[tuple[Path, float]] = []
    try:
        for backup_path in backup_dir.glob(pattern):
            try:
                mtime = backup_path.stat().st_mtime
                backup_list.append((backup_path, mtime))
            except OSError:
                # Skip files that can't be stat'd
                continue
    except OSError:
        return []

    # Sort by modification time (oldest first)
    backup_files = [path for path, mtime in sorted(backup_list, key=lambda x: x[1])]

    return backup_files


# =============================================================================
# Type Definitions
# =============================================================================


class DotFileDict(TypedDict):
    """
    Type definition for dotfile configuration dictionary.

    Contains all metadata and path information for individual dotfile entries
    from TOML configuration file. Supports multiple paths per dotfile entry.
    """

    category: str
    subcategory: str
    application: str
    description: str
    paths: list[str]
    mirror_dir: str
    archive_dir: str
    enabled: bool


class OptionsDict(TypedDict):
    """
    Type definition for options configuration dictionary.

    Contains all backup operation settings and preferences from TOML
    configuration file.
    """

    mirror: bool
    archive: bool
    hostname_subdir: bool
    date_subdir: bool
    archive_format: str
    archive_compression_level: int
    rotate_archives: bool
    max_archives: int


@dataclass
class BackupStatistics:
    """
    Data class for tracking backup operation statistics.

    Attributes:
        total_items: Total number of items to process
        processed_items: Number of successfully processed items
        skipped_items: Number of items skipped (not exist or no permission)
        failed_items: Number of items that failed processing
        total_time: Total elapsed time for operation
        processing_times: Individual processing times for each item
        average_time: Average processing time per item
        min_time: Minimum processing time
        max_time: Maximum processing time
    """

    total_items: int = 0
    processed_items: int = 0
    skipped_items: int = 0
    failed_items: int = 0
    total_time: float = 0.0
    processing_times: list[float] = field(default_factory=list)

    @property
    def average_time(self) -> float:
        """Calculate average processing time per item."""
        if not self.processing_times:
            return 0.0
        return sum(self.processing_times) / len(self.processing_times)

    @property
    def min_time(self) -> float:
        """Get minimum processing time."""
        return min(self.processing_times) if self.processing_times else 0.0

    @property
    def max_time(self) -> float:
        """Get maximum processing time."""
        return max(self.processing_times) if self.processing_times else 0.0

    def reset(self) -> None:
        """Reset statistics to initial state."""
        self.total_items = 0
        self.processed_items = 0
        self.skipped_items = 0
        self.failed_items = 0
        self.total_time = 0.0
        self.processing_times = []


class DFBUModel:
    """
    Model class managing DFBU application state and business logic.

    Attributes:
        config_path: Path to TOML configuration file
        options: Backup operation options from configuration
        dotfiles: List of dotfile metadata from configuration
        statistics: Backup/restore operation statistics
        hostname: Current system hostname
        mirror_base_dir: Base directory for mirror backups
        archive_base_dir: Base directory for archive backups

    Public methods:
        load_config: Load and validate TOML configuration
        save_config: Save configuration changes back to TOML file
        add_dotfile: Add a new dotfile entry to configuration
        update_dotfile: Update an existing dotfile entry in configuration
        remove_dotfile: Remove a dotfile entry from configuration by index
        validate_dotfile_paths: Check which dotfiles exist on system
        get_dotfile_by_index: Get dotfile metadata by index
        get_dotfile_count: Get number of configured dotfiles
        assemble_dest_path: Build destination path for backup
        expand_path: Expand user home directory in path
        check_readable: Check if path has read permissions
        create_directory: Create directory with permissions
        copy_file: Copy file with metadata preservation
        copy_directory: Copy directory recursively
        create_archive: Create compressed TAR.GZ archive
        rotate_archives: Delete oldest archives exceeding limit
        discover_restore_files: Find all files in restore source
        reconstruct_restore_paths: Build original paths from backup structure
        record_item_processed: Record successful item processing
        record_item_skipped: Record skipped item
        record_item_failed: Record failed item
        reset_statistics: Reset operation statistics
        update_option: Update a single configuration option
        update_path: Update mirror_dir or archive_dir path

    Private methods:
        _validate_config: Validate complete configuration structure
        _validate_options: Validate options with type checking
        _validate_dotfile: Validate individual dotfile entry
        _is_relative_to_home: Check if path is under home directory
    """

    def __init__(self, config_path: Path) -> None:
        """
        Initialize the DFBUModel.

        Args:
            config_path: Path to TOML configuration file
        """
        self.config_path: Path = config_path
        self.options: OptionsDict = self._get_default_options()
        self.dotfiles: list[DotFileDict] = []
        self.statistics: BackupStatistics = BackupStatistics()
        self.hostname: str = gethostname()

        # Base directories (set from first dotfile paths after config load)
        self.mirror_base_dir: Path = Path.home()
        self.archive_base_dir: Path = Path.home()

    def load_config(self) -> tuple[bool, str]:
        """
        Load and validate TOML configuration file.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        try:
            # Read TOML configuration file
            with open(self.config_path, "rb") as toml_file:
                config_data: dict[str, Any] = tomllib.load(toml_file)

            # Validate and extract configuration
            self.options, self.dotfiles = self._validate_config(config_data)

            # Set base directories from first dotfile
            if self.dotfiles:
                self.mirror_base_dir = self.expand_path(
                    self.dotfiles[0].get("mirror_dir", "~/DFBU_Mirror")
                )
                self.archive_base_dir = self.expand_path(
                    self.dotfiles[0].get("archive_dir", "~/DFBU_Archives")
                )

            return True, ""

        except FileNotFoundError:
            return False, f"Configuration file not found: {self.config_path}"
        except tomllib.TOMLDecodeError as e:
            return False, f"Invalid TOML format: {e!s}"
        except KeyError as e:
            return False, f"Missing required configuration key: {e!s}"
        except Exception as e:
            return False, f"Unexpected error loading config: {e!s}"

    def save_config(self) -> tuple[bool, str]:
        """
        Save current configuration back to TOML file with automatic rotating backups.

        Creates a timestamped backup of the config file before saving, maintaining
        up to 10 backup copies with automatic rotation of oldest backups.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        try:
            # Create rotating backup before saving (if config file exists)
            if self.config_path.exists():
                backup_dir = (
                    self.config_path.parent / f".{self.config_path.name}.backups"
                )
                backup_path, backup_success = create_rotating_backup(
                    source_path=self.config_path,
                    backup_dir=backup_dir,
                    max_backups=10,
                    timestamp_format="%Y%m%d_%H%M%S",
                )
                # Continue with save even if backup fails (log could be added here)

            # Build configuration dictionary matching TOML structure
            config_data: dict[str, Any] = {
                "title": "Dotfiles Backup Config",
                "description": "Configuration file for dotfiles backup.",
                "paths": {
                    "mirror_dir": self._path_to_tilde_notation(self.mirror_base_dir),
                    "archive_dir": self._path_to_tilde_notation(self.archive_base_dir),
                },
                "options": dict(self.options),
                "dotfile": [],
            }

            # Add dotfiles - save as single 'path' or 'paths' list
            for dotfile in self.dotfiles:
                dotfile_entry: dict[str, Any] = {
                    "category": dotfile["category"],
                    "subcategory": dotfile["subcategory"],
                    "application": dotfile["application"],
                    "description": dotfile["description"],
                    "enabled": dotfile["enabled"],
                }

                # Save as single 'path' for backward compatibility if only one path
                # Otherwise save as 'paths' list
                paths_list = dotfile["paths"]
                if len(paths_list) == 1:
                    dotfile_entry["path"] = paths_list[0]
                else:
                    dotfile_entry["paths"] = paths_list

                config_data["dotfile"].append(dotfile_entry)

            # Write TOML file using tomli_w
            with open(self.config_path, "wb") as toml_file:
                tomli_w.dump(config_data, toml_file)

            return True, ""

        except (OSError, PermissionError) as e:
            return False, f"Failed to write configuration file: {e!s}"
        except Exception as e:
            return False, f"Unexpected error saving config: {e!s}"

    def update_option(self, key: str, value: Any) -> bool:
        """
        Update a single configuration option.

        Note: Type validation should be performed by caller (ViewModel layer).
        This method trusts that the value type matches the key's expected type.

        Args:
            key: Option key to update
            value: New value for the option

        Returns:
            True if option was updated successfully
        """
        if key in self.options:
            # Type validation performed at ViewModel layer before reaching here
            if key == "mirror":
                self.options["mirror"] = bool(value)
            elif key == "archive":
                self.options["archive"] = bool(value)
            elif key == "hostname_subdir":
                self.options["hostname_subdir"] = bool(value)
            elif key == "date_subdir":
                self.options["date_subdir"] = bool(value)
            elif key == "archive_format":
                self.options["archive_format"] = str(value)
            elif key == "archive_compression_level":
                self.options["archive_compression_level"] = int(value)
            elif key == "rotate_archives":
                self.options["rotate_archives"] = bool(value)
            elif key == "max_archives":
                self.options["max_archives"] = int(value)
            return True
        return False

    def update_path(self, path_type: str, value: str) -> bool:
        """
        Update mirror_dir or archive_dir path.

        Args:
            path_type: Either "mirror_dir" or "archive_dir"
            value: New path value

        Returns:
            True if path was updated successfully
        """
        expanded_path = self.expand_path(value)

        if path_type == "mirror_dir":
            self.mirror_base_dir = expanded_path
            return True
        if path_type == "archive_dir":
            self.archive_base_dir = expanded_path
            return True

        return False

    def validate_dotfile_paths(self) -> dict[int, tuple[bool, bool, str]]:
        """
        Check which configured dotfiles exist on the system.

        For dotfiles with multiple paths, validates the first path only for display purposes.
        Individual path validation occurs during backup operations.

        Returns:
            Dict mapping index to (exists, is_dir, type_str) tuple
        """
        validation_results: dict[int, tuple[bool, bool, str]] = {}

        for i, dotfile in enumerate(self.dotfiles):
            # Get first path for validation (for display purposes)
            paths = dotfile["paths"]
            if not paths or not paths[0]:
                validation_results[i] = (False, False, "File")
                continue

            path = self.expand_path(paths[0])
            exists = path.exists()
            is_dir = path.is_dir() if exists else False
            type_str = "Directory" if is_dir else "File"

            validation_results[i] = (exists, is_dir, type_str)

        return validation_results

    def calculate_path_size(self, path: Path) -> int:
        """
        Calculate total size of a file or directory in bytes.

        Args:
            path: Path to file or directory

        Returns:
            Total size in bytes, 0 if path doesn't exist or permission denied
        """
        # Path doesn't exist
        if not path.exists():
            return 0

        # Check read permissions
        if not self.check_readable(path):
            return 0

        try:
            # For files, return file size
            if path.is_file():
                return path.stat().st_size

            # For directories, sum all file sizes recursively
            if path.is_dir():
                total_size = 0
                try:
                    for item in path.rglob("*"):
                        if item.is_file():
                            try:
                                total_size += item.stat().st_size
                            except (OSError, PermissionError):
                                # Skip files we can't access
                                continue
                except (OSError, PermissionError):
                    # Error during directory traversal
                    return 0

                return total_size

        except (OSError, PermissionError):
            return 0

        return 0

    def get_dotfile_sizes(self) -> dict[int, int]:
        """
        Calculate sizes for all configured dotfiles.

        For dotfiles with multiple paths, returns the sum of all path sizes.

        Returns:
            Dict mapping dotfile index to total size in bytes
        """
        size_results: dict[int, int] = {}

        for i, dotfile in enumerate(self.dotfiles):
            total_size = 0
            for path_str in dotfile["paths"]:
                if path_str:
                    path = self.expand_path(path_str)
                    total_size += self.calculate_path_size(path)
            size_results[i] = total_size

        return size_results

    def get_dotfile_by_index(self, index: int) -> DotFileDict | None:
        """
        Get dotfile metadata by index.

        Args:
            index: Index in dotfiles list

        Returns:
            Dotfile dictionary or None if invalid index
        """
        if 0 <= index < len(self.dotfiles):
            return self.dotfiles[index]
        return None

    def get_dotfile_count(self) -> int:
        """
        Get number of configured dotfiles.

        Returns:
            Number of dotfiles in configuration
        """
        return len(self.dotfiles)

    def assemble_dest_path(
        self,
        base_path: Path,
        src_path: Path,
        hostname_subdir: bool,
        date_subdir: bool,
    ) -> Path:
        """
        Assemble destination path based on source and options.

        Args:
            base_path: Base destination directory
            src_path: Source file/directory path
            hostname_subdir: Include hostname subdirectory
            date_subdir: Include date subdirectory

        Returns:
            Assembled destination path
        """
        # Determine if path is relative to home or root
        is_relative_to_home = self._is_relative_to_home(src_path)
        src_relative = (
            src_path.relative_to(Path.home())
            if is_relative_to_home
            else src_path.relative_to(Path("/"))
        )
        prefix = "home" if is_relative_to_home else "root"

        # Build destination path components
        dest_parts: list[Path] = [base_path]
        if hostname_subdir:
            dest_parts.append(Path(self.hostname))
        if date_subdir:
            dest_parts.append(Path(time.strftime("%Y-%m-%d")))
        dest_parts.extend([Path(prefix), src_relative])

        # Combine all path components
        final_path = dest_parts[0]
        for part in dest_parts[1:]:
            final_path = final_path / part

        return final_path

    def expand_path(self, path_str: str) -> Path:
        """
        Expand user home directory in path string.

        Args:
            path_str: Path string potentially containing ~

        Returns:
            Expanded Path object
        """
        return Path(path_str).expanduser() if "~" in path_str else Path(path_str)

    def check_readable(self, path: Path) -> bool:
        """
        Check if path has read permissions.

        Args:
            path: Path to check

        Returns:
            True if readable, False otherwise
        """
        return os.access(path, os.R_OK)

    def create_directory(self, path: Path, mode: int = 0o755) -> bool:
        """
        Create directory with proper permissions.

        Args:
            path: Directory path to create
            mode: Directory permissions mode

        Returns:
            True if created successfully, False otherwise
        """
        try:
            path.mkdir(mode=mode, parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False

    def files_are_identical(self, src_path: Path, dest_path: Path) -> bool:
        """
        Compare two files to determine if they are identical.

        Compares file size and modification time to efficiently determine if files
        are the same without reading entire file contents.

        Args:
            src_path: Source file path
            dest_path: Destination file path

        Returns:
            True if files are identical (same size and mtime), False otherwise
        """
        # Destination doesn't exist, files are not identical
        if not dest_path.exists():
            return False

        try:
            src_stat = src_path.stat()
            dest_stat = dest_path.stat()

            # Compare file size first (fast check)
            if src_stat.st_size != dest_stat.st_size:
                return False

            # Compare modification time with tolerance for filesystem precision
            time_diff = abs(src_stat.st_mtime - dest_stat.st_mtime)
            if time_diff > FILE_MTIME_TOLERANCE_SECONDS:
                return False

            # Files appear identical
            return True

        except (OSError, PermissionError):
            return False

    def copy_file(
        self,
        src_path: Path,
        dest_path: Path,
        create_parent: bool = True,
        skip_identical: bool = False,
    ) -> bool:
        """
        Copy file with metadata preservation using Python 3.14 Path.copy() or fallback.

        Note: Performs readability check as this is a public method that may be called
        with non-validated paths. For validated configuration files, this provides
        additional safety against permission changes between validation and copy.

        Args:
            src_path: Source file path (must exist and be readable)
            dest_path: Destination file path
            create_parent: Whether to create parent directories
            skip_identical: Whether to skip copying if files are identical (mirror optimization)

        Returns:
            True if copied successfully or skipped due to identical files, False otherwise
        """
        try:
            # Check readability - protects against permission changes after validation
            if not self.check_readable(src_path):
                return False

            # Check if files are identical when optimization enabled
            if skip_identical and self.files_are_identical(src_path, dest_path):
                return True

            # Create parent directory if needed
            if create_parent and not dest_path.parent.exists():
                if not self.create_directory(dest_path.parent):
                    return False

            # Use Path.copy() with metadata preservation (Python 3.14+ required)
            src_path.copy(dest_path, follow_symlinks=True, preserve_metadata=True)
            return True

        except (OSError, PermissionError):
            return False

    def copy_directory(
        self, src_path: Path, dest_base: Path, skip_identical: bool = False
    ) -> list[tuple[Path, Path | None, bool, bool]]:
        """
        Copy directory recursively with all files.

        Args:
            src_path: Source directory path
            dest_base: Destination base path
            skip_identical: Whether to skip copying if files are identical

        Returns:
            List of (src_file, dest_file, success, skipped) tuples for each file
            dest_file is None if destination path is not applicable
        """
        results: list[tuple[Path, Path | None, bool, bool]] = []

        # Check directory readability
        if not self.check_readable(src_path):
            return results

        # Gather all files recursively
        try:
            files = [f for f in src_path.rglob("*") if f.is_file()]
        except (OSError, PermissionError):
            return results

        # Process each file
        for file_path in files:
            # Skip files without read permissions
            if not self.check_readable(file_path):
                results.append((file_path, None, False, False))
                continue

            # Calculate destination path maintaining structure
            try:
                file_relative = file_path.relative_to(src_path)
                file_dest = dest_base / file_relative

                # Check if file is identical and can be skipped
                was_skipped = False
                if skip_identical and self.files_are_identical(file_path, file_dest):
                    was_skipped = True
                    results.append((file_path, file_dest, True, True))
                else:
                    # Copy file
                    success = self.copy_file(
                        file_path, file_dest, create_parent=True, skip_identical=False
                    )
                    results.append((file_path, file_dest, success, False))

            except (ValueError, OSError):
                results.append((file_path, None, False, False))

        return results

    def create_archive(
        self, dotfiles_to_archive: list[tuple[Path, bool, bool]]
    ) -> tuple[Path | None, bool]:
        """
        Create compressed TAR.GZ archive of existing dotfiles.

        Args:
            dotfiles_to_archive: List of (path, exists, is_dir) tuples

        Returns:
            Tuple of (archive_path, success)
        """
        # Determine archive path with hostname subdirectory if configured
        archive_base = self.archive_base_dir
        if self.options["hostname_subdir"]:
            archive_base = archive_base / self.hostname

        # Create archive directory
        if not self.create_directory(archive_base):
            return None, False

        # Generate timestamped archive filename with microseconds for uniqueness
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        archive_name = f"dotfiles-{timestamp}.tar.gz"
        archive_path = archive_base / archive_name

        try:
            # Create compressed TAR.GZ archive
            with tarfile.open(archive_path, "w:gz") as tar:
                for path, exists, is_dir in dotfiles_to_archive:
                    if exists:
                        tar.add(path)

            return archive_path, True

        except (OSError, tarfile.TarError):
            return archive_path, False

    def perform_mirror_backup(self) -> bool:
        """
        Perform mirror backup of all enabled dotfiles.

        Copies files and directories to mirror destination, maintaining directory
        structure and preserving metadata. Uses copy_file and copy_directory
        methods for actual file operations.

        Returns:
            True if backup completed successfully, False if any errors occurred
        """
        # Reset statistics for new backup operation
        self.reset_statistics()

        # Check if mirror backup is enabled
        if not self.options.get("mirror_enabled", True):
            return False

        success = True

        # Process each dotfile entry
        for index, dotfile in enumerate(self.dotfiles):
            # Skip disabled dotfiles
            if not dotfile.get("enabled", True):
                continue

            # Process each path in the dotfile
            paths = dotfile.get("paths", [dotfile.get("path", "")])
            if isinstance(paths, str):
                paths = [paths]

            for path_str in paths:
                if not path_str:
                    continue

                # Expand and validate source path
                src_path = self.expand_path(path_str)
                if not src_path.exists():
                    self.record_item_skipped()
                    continue

                # Assemble destination path for mirror backup
                dest_path = self._assemble_dest_path(
                    self.mirror_base_dir, src_path, dotfile
                )

                # Copy file or directory
                if src_path.is_file():
                    copy_success = self.copy_file(
                        src_path, dest_path, create_parent=True, skip_identical=True
                    )
                elif src_path.is_dir():
                    results = self.copy_directory(
                        src_path, dest_path, skip_identical=True
                    )
                    copy_success = len(results) > 0 and all(
                        result[2] for result in results
                    )
                    # Update statistics for each file in directory
                    for _, _, file_success, skipped in results:
                        if file_success:
                            if skipped:
                                self.record_item_skipped()
                            else:
                                self.record_item_processed(
                                    0.0
                                )  # Time will be set by actual copy
                        else:
                            self.record_item_failed()
                else:
                    copy_success = False

                if not copy_success:
                    success = False
                    self.record_item_failed()
                elif src_path.is_file():
                    self.record_item_processed(0.0)  # Time will be set by actual copy

        return success

    def _assemble_dest_path(
        self, base_dir: Path, src_path: Path, dotfile: DotFileDict
    ) -> Path:
        """
        Assemble destination path for backup operations.

        Args:
            base_dir: Base destination directory (mirror or archive)
            src_path: Source file/directory path
            dotfile: Dotfile configuration dictionary

        Returns:
            Assembled destination path
        """
        # Determine if path is relative to home directory
        is_relative_to_home = self._is_relative_to_home(src_path)

        # Calculate relative path from home or root
        if is_relative_to_home:
            src_relative = src_path.relative_to(Path.home())
            prefix = "home"
        else:
            src_relative = src_path.relative_to(Path("/"))
            prefix = "root"

        # Build destination path components
        dest_parts = [base_dir]

        # Add hostname subdirectory if configured
        if self.options.get("hostname_subdir", True):
            dest_parts.append(Path(self.hostname))

        # Add date subdirectory if configured
        if self.options.get("date_subdir", False):
            dest_parts.append(Path(time.strftime("%Y-%m-%d")))

        # Add prefix and relative path
        dest_parts.extend([Path(prefix), src_relative])

        # Use efficient path construction
        return Path(*dest_parts)

    def rotate_archives(self) -> list[Path]:
        """
        Delete oldest archives exceeding maximum retention limit.

        Returns:
            List of deleted archive paths
        """
        # Determine archive base directory
        archive_base = self.archive_base_dir
        if self.options["hostname_subdir"]:
            archive_base = archive_base / self.hostname

        deleted_archives: list[Path] = []

        # Find all existing archives sorted by modification time with error handling
        try:
            # Build list of (path, mtime) tuples, skipping files that fail stat()
            archive_list: list[tuple[Path, float]] = []
            for archive_path in archive_base.glob("dotfiles-*.tar.gz"):
                try:
                    mtime = archive_path.stat().st_mtime
                    archive_list.append((archive_path, mtime))
                except OSError:
                    # Skip files that can't be stat'd (deleted or permission error)
                    continue

            # Sort by modification time
            archives = [
                path for path, mtime in sorted(archive_list, key=lambda x: x[1])
            ]
        except OSError:
            return deleted_archives

        # Calculate number to delete
        num_to_delete = len(archives) - self.options["max_archives"]

        # Delete oldest archives
        if num_to_delete > 0:
            for i in range(num_to_delete):
                try:
                    archives[i].unlink()
                    deleted_archives.append(archives[i])
                except OSError:
                    continue

        return deleted_archives

    def discover_restore_files(self, src_dir: Path) -> list[Path]:
        """
        Find all files in restore source directory recursively.

        Args:
            src_dir: Source directory containing backup files

        Returns:
            List of all file paths found
        """
        try:
            return [f for f in src_dir.rglob("*") if f.is_file()]
        except (OSError, PermissionError):
            return []

    def reconstruct_restore_paths(
        self, src_files: list[Path]
    ) -> list[tuple[Path, Path | None]]:
        """
        Build original destination paths from backup structure.

        Args:
            src_files: List of source files from backup

        Returns:
            List of (src_path, dest_path) tuples, dest_path is None if reconstruction fails
        """
        restore_paths: list[tuple[Path, Path | None]] = []

        for src_path in src_files:
            try:
                # Find hostname in path
                hostname_index = src_path.parts.index(self.hostname)
                r_host = Path(*src_path.parts[hostname_index + 1 :])

                # Reconstruct based on home or root
                if "home" in r_host.parts:
                    home_index = r_host.parts.index("home")
                    r_home = Path(*r_host.parts[home_index + 1 :])
                    dest_path = Path.home() / r_home
                    restore_paths.append((src_path, dest_path))
                elif "root" in r_host.parts:
                    root_index = r_host.parts.index("root")
                    r_root = Path(*r_host.parts[root_index + 1 :])
                    dest_path = Path("/") / r_root
                    restore_paths.append((src_path, dest_path))
                else:
                    # Cannot determine original location
                    restore_paths.append((src_path, None))

            except (ValueError, IndexError):
                # Reconstruction failed
                restore_paths.append((src_path, None))

        return restore_paths

    def record_item_processed(self, processing_time: float) -> None:
        """
        Record successfully processed item.

        Args:
            processing_time: Time taken to process item
        """
        self.statistics.processed_items += 1
        self.statistics.processing_times.append(processing_time)

    def record_item_skipped(self) -> None:
        """Record skipped item (not exist or no permission)."""
        self.statistics.skipped_items += 1

    def record_item_failed(self) -> None:
        """Record failed item."""
        self.statistics.failed_items += 1

    def reset_statistics(self) -> None:
        """Reset operation statistics for new run."""
        self.statistics.reset()

    def add_dotfile(
        self,
        category: str,
        subcategory: str,
        application: str,
        description: str,
        paths: list[str],
        enabled: bool = True,
    ) -> bool:
        """
        Add a new dotfile entry to the configuration.

        Args:
            category: Category for the dotfile
            subcategory: Subcategory for the dotfile
            application: Application name
            description: Description of the dotfile
            paths: List of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was added successfully
        """
        # Create new dotfile entry with paths from existing configuration
        new_dotfile: DotFileDict = {
            "category": category,
            "subcategory": subcategory,
            "application": application,
            "description": description,
            "paths": paths,
            "mirror_dir": self._path_to_tilde_notation(self.mirror_base_dir),
            "archive_dir": self._path_to_tilde_notation(self.archive_base_dir),
            "enabled": enabled,
        }

        # Add to dotfiles list
        self.dotfiles.append(new_dotfile)
        return True

    def update_dotfile(
        self,
        index: int,
        category: str,
        subcategory: str,
        application: str,
        description: str,
        paths: list[str],
        enabled: bool = True,
    ) -> bool:
        """
        Update an existing dotfile entry in the configuration.

        Args:
            index: Index of dotfile to update
            category: Updated category
            subcategory: Updated subcategory
            application: Updated application name
            description: Updated description
            paths: Updated list of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was updated successfully
        """
        if 0 <= index < len(self.dotfiles):
            # Update the dotfile entry while preserving mirror_dir and archive_dir
            self.dotfiles[index]["category"] = category
            self.dotfiles[index]["subcategory"] = subcategory
            self.dotfiles[index]["application"] = application
            self.dotfiles[index]["description"] = description
            self.dotfiles[index]["paths"] = paths
            self.dotfiles[index]["enabled"] = enabled
            return True
        return False

    def remove_dotfile(self, index: int) -> bool:
        """
        Remove a dotfile entry from the configuration by index.

        Args:
            index: Index of dotfile to remove

        Returns:
            True if dotfile was removed successfully
        """
        if 0 <= index < len(self.dotfiles):
            self.dotfiles.pop(index)
            return True
        return False

    def toggle_dotfile_enabled(self, index: int) -> bool:
        """
        Toggle the enabled status of a dotfile entry.

        Args:
            index: Index of dotfile to toggle

        Returns:
            New enabled status if successful, current status otherwise
        """
        if 0 <= index < len(self.dotfiles):
            self.dotfiles[index]["enabled"] = not self.dotfiles[index]["enabled"]
            return self.dotfiles[index]["enabled"]
        return False

    def _get_default_options(self) -> OptionsDict:
        """
        Get default options configuration.

        Returns:
            Default OptionsDict
        """
        return {
            "mirror": True,
            "archive": False,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": False,
            "max_archives": 5,
        }

    def _validate_config(
        self, config_data: dict[str, Any]
    ) -> tuple[OptionsDict, list[DotFileDict]]:
        """
        Validate complete configuration structure.

        Args:
            config_data: Raw configuration from TOML

        Returns:
            Tuple of validated options and dotfiles list
        """
        # Extract sections
        raw_paths = config_data.get("paths", {})
        raw_options = config_data.get("options", {})
        raw_dotfiles = config_data.get("dotfile", [])

        # Validate options
        validated_options = self._validate_options(raw_options)

        # Validate and merge dotfiles
        validated_dotfiles: list[DotFileDict] = []
        for dotfile in raw_dotfiles:
            merged_dotfile = {**raw_paths, **dotfile}
            validated_dotfiles.append(self._validate_dotfile(merged_dotfile))

        return validated_options, validated_dotfiles

    def _validate_options(self, raw_options: dict[str, Any]) -> OptionsDict:
        """
        Validate options with type checking and defaults.

        Args:
            raw_options: Raw options from configuration

        Returns:
            Validated OptionsDict
        """
        # Validate compression level
        compression_level = raw_options.get("archive_compression_level", 9)
        if not isinstance(compression_level, int) or not (0 <= compression_level <= 9):
            compression_level = 9

        # Validate max archives
        max_archives = raw_options.get("max_archives", 5)
        if not isinstance(max_archives, int) or max_archives < 1:
            max_archives = 5

        # Build validated options dictionary with proper types
        return {
            "mirror": raw_options.get("mirror", True),
            "archive": raw_options.get("archive", False),
            "hostname_subdir": raw_options.get("hostname_subdir", True),
            "date_subdir": raw_options.get("date_subdir", False),
            "archive_format": str(raw_options.get("archive_format", "tar.gz")),
            "archive_compression_level": compression_level,
            "rotate_archives": raw_options.get("rotate_archives", False),
            "max_archives": max_archives,
        }

    def _validate_dotfile(self, raw_dotfile: dict[str, Any]) -> DotFileDict:
        """
        Validate individual dotfile entry.

        Supports both legacy single 'path' (str) and new 'paths' (list[str]) format.
        Automatically converts single path to list for internal consistency.

        Args:
            raw_dotfile: Raw dotfile metadata

        Returns:
            Validated DotFileDict with paths as list[str]
        """
        # Convert enabled field to bool with proper type handling
        enabled_value = raw_dotfile.get("enabled", "true")
        if isinstance(enabled_value, bool):
            enabled = enabled_value
        else:
            # Handle string representations
            enabled = str(enabled_value).lower() in ("true", "1", "yes")

        # Handle both legacy 'path' (str) and new 'paths' (list[str]) format
        paths: list[str] = []
        if "paths" in raw_dotfile:
            # New format: paths is already a list
            paths_value = raw_dotfile["paths"]
            if isinstance(paths_value, list):
                paths = paths_value
            else:
                # Fallback: treat as single path
                paths = [str(paths_value)]
        elif "path" in raw_dotfile:
            # Legacy format: convert single path to list
            paths = [raw_dotfile["path"]]
        else:
            # No path provided
            paths = [""]

        return {
            "category": raw_dotfile.get("category", "Unknown"),
            "subcategory": raw_dotfile.get("subcategory", "Unknown"),
            "application": raw_dotfile.get("application", "Unknown"),
            "description": raw_dotfile.get("description", "None"),
            "paths": paths,
            "mirror_dir": raw_dotfile.get("mirror_dir", "~/DFBU_Mirror"),
            "archive_dir": raw_dotfile.get("archive_dir", "~/DFBU_Archives"),
            "enabled": enabled,
        }

    def _is_relative_to_home(self, path: Path) -> bool:
        """
        Check if path is relative to home directory.

        Args:
            path: Path to check

        Returns:
            True if relative to home, False otherwise
        """
        try:
            path.relative_to(Path.home())
            return True
        except ValueError:
            return False

    def _path_to_tilde_notation(self, path: Path) -> str:
        """
        Convert absolute path to tilde notation for home directory.

        Uses Path.relative_to() for proper path handling instead of string
        replacement to avoid edge cases where home path appears as substring.

        Args:
            path: Path to convert

        Returns:
            Path string with ~ notation if under home directory
        """
        try:
            # Check if path is relative to home directory
            rel_path = path.relative_to(Path.home())
            return f"~/{rel_path}"
        except ValueError:
            # Path is not under home directory, return as-is
            return str(path)
