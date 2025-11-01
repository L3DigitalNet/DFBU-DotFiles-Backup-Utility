"""
DFBU FileOperations - File and Directory Operations Component

Description:
    Handles all file system operations for DFBU GUI including path manipulation,
    file copying, directory operations, archive creation, and restore path
    reconstruction. Part of the refactored MVVM architecture following Single
    Responsibility Principle.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 11-01-2025
License: MIT

Features:
    - Path expansion and validation
    - File identity comparison using metadata
    - File and directory copying with metadata preservation
    - Archive creation and rotation (TAR.GZ format)
    - Restore file discovery and path reconstruction
    - Size calculation for files and directories
    - Clean separation from configuration and business logic

Requirements:
    - Linux environment
    - Python 3.14+ for Path.copy() with metadata preservation
    - Standard library: pathlib, os, shutil, tarfile, time
    - No external dependencies

Classes:
    - FileOperations: Manages all file system operations

Functions:
    - create_rotating_backup: Create timestamped file backup with rotation
    - rotate_old_backups: Delete oldest backups exceeding limit
    - get_backup_files: Find all backup files for a source file
"""

import os
import shutil
import tarfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Final


# =============================================================================
# Constants
# =============================================================================

# File modification time comparison tolerance in seconds
# Accounts for filesystem timestamp precision differences across systems
# (e.g., ext4: 1ns, FAT32: 2s, NTFS: 100ns)
FILE_MTIME_TOLERANCE_SECONDS: Final[float] = 1.0


# =============================================================================
# Utility Functions for Backup Operations
# =============================================================================


def create_rotating_backup(
    source_path: Path,
    backup_dir: Path | None = None,
    max_backups: int = 10,
    timestamp_format: str = "%Y%m%d_%H%M%S",
) -> Path | None:
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
        Path to created backup file, or None if operation failed
    """
    # Source file must exist
    if not source_path.exists() or not source_path.is_file():
        return None

    # Determine backup directory location
    if backup_dir is None:
        backup_dir = source_path.parent / f".{source_path.name}.backups"

    # Create backup directory if needed
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError):
        return None

    # Generate timestamped backup filename with collision handling
    timestamp = datetime.now(UTC).strftime(timestamp_format)
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
        return None

    # Rotate old backups to maintain maximum count
    rotate_old_backups(source_path, backup_dir, max_backups)

    return backup_path


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


def get_backup_files(source_path: Path, backup_dir: Path) -> list[Path]:
    """
    Find all backup files for a source file sorted by age.

    Identifies backup files by matching pattern: {stem}.{timestamp}{suffix}
    Returns files sorted by modification time (oldest first).

    Args:
        source_path: Original file that was backed up
        backup_dir: Directory containing backup files

    Returns:
        List of backup file paths sorted by age (oldest first)
    """
    if not backup_dir.exists():
        return []

    # Build pattern to match backup files
    pattern = f"{source_path.stem}.*{source_path.suffix}"

    # Find all matching backup files with error handling
    backup_list: list[tuple[Path, float]] = []
    for backup_file in backup_dir.glob(pattern):
        try:
            mtime = backup_file.stat().st_mtime
            backup_list.append((backup_file, mtime))
        except OSError:
            # Skip files that can't be stat'd
            continue

    # Sort by modification time (oldest first)
    return [path for path, _mtime in sorted(backup_list, key=lambda x: x[1])]


# =============================================================================
# FileOperations Class
# =============================================================================


class FileOperations:
    """
    Manages all file system operations for DFBU.

    Handles path expansion, file copying, directory operations, archive creation,
    and restore path reconstruction. Provides clean separation between file I/O
    and business logic.

    Attributes:
        hostname: System hostname for path assembly and restore operations

    Public methods:
        expand_path: Expand user home directory in path string
        check_readable: Check if path has read permissions
        create_directory: Create directory with proper permissions
        files_are_identical: Compare files using metadata (size + mtime)
        copy_file: Copy single file with metadata preservation
        copy_directory: Copy directory recursively
        calculate_path_size: Calculate total size of file or directory
        assemble_dest_path: Build destination path from source and options
        create_archive: Create compressed TAR.GZ archive
        rotate_archives: Delete oldest archives exceeding limit
        discover_restore_files: Find all files in restore source
        reconstruct_restore_paths: Build original paths from backup structure
        is_relative_to_home: Check if path is under home directory

    Private methods:
        None
    """

    def __init__(self, hostname: str) -> None:
        """
        Initialize FileOperations.

        Args:
            hostname: System hostname for path operations
        """
        self.hostname: str = hostname

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

    def create_directory(self, path: Path, mode: int = 0o755) -> None:
        """
        Create directory with proper permissions.

        Args:
            path: Directory path to create
            mode: Directory permissions mode
        """
        path.mkdir(mode=mode, parents=True, exist_ok=True)

    def files_are_identical(self, src_path: Path, dest_path: Path) -> bool:
        """
        Compare two files to determine if they are identical.

        Uses efficient metadata comparison (size + mtime) instead of reading
        entire file contents. Includes tolerance for filesystem timestamp precision.

        Args:
            src_path: Source file path
            dest_path: Destination file path

        Returns:
            True if files are identical (same size and mtime), False otherwise
        """
        # Quick check: destination doesn't exist
        if not dest_path.exists():
            return False

        try:
            src_stat = src_path.stat()
            dest_stat = dest_path.stat()

            # Fast check: compare file sizes first (cheap operation)
            if src_stat.st_size != dest_stat.st_size:
                return False

            # Precise check: compare modification times with filesystem tolerance
            # Tolerance accounts for different filesystem timestamp precision (ext4, NTFS, etc.)
            time_diff = abs(src_stat.st_mtime - dest_stat.st_mtime)
            return time_diff <= FILE_MTIME_TOLERANCE_SECONDS

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
        Copy file with metadata preservation using Python 3.14 Path.copy().

        Args:
            src_path: Source file path (validated by caller)
            dest_path: Destination file path
            create_parent: Whether to create parent directories
            skip_identical: Whether to skip copying if files are identical (mirror optimization)

        Returns:
            True if copied successfully or skipped due to identical files, False otherwise
        """
        # Check if files are identical when optimization enabled
        if skip_identical and self.files_are_identical(src_path, dest_path):
            return True

        # Create parent directory if needed
        if create_parent and not dest_path.parent.exists():
            self.create_directory(dest_path.parent)

        # Use Path.copy() with metadata preservation (Python 3.14+ required)
        # Fall back to shutil.copy2 for older Python versions
        try:
            src_path.copy(dest_path, follow_symlinks=True, preserve_metadata=True)
        except AttributeError:
            # Fallback for Python < 3.14
            shutil.copy2(src_path, dest_path)
        return True

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

        # Process files iteratively to avoid loading all into memory
        try:
            # Use iterator for memory efficiency with large directories
            for file_path in src_path.rglob("*"):
                if not file_path.is_file():
                    continue

                # Skip files without read permissions
                if not self.check_readable(file_path):
                    results.append((file_path, None, False, False))
                    continue

                # Calculate destination path maintaining structure
                try:
                    file_relative = file_path.relative_to(src_path)
                    file_dest = dest_base / file_relative

                    # Check if file is identical and can be skipped
                    if skip_identical and self.files_are_identical(
                        file_path, file_dest
                    ):
                        results.append((file_path, file_dest, True, True))
                    else:
                        # Copy file
                        success = self.copy_file(
                            file_path,
                            file_dest,
                            create_parent=True,
                            skip_identical=False,
                        )
                        results.append((file_path, file_dest, success, False))

                except (ValueError, OSError):
                    results.append((file_path, None, False, False))

        except (OSError, PermissionError):
            return results

        return results

    def calculate_path_size(self, path: Path) -> int:
        """
        Calculate total size of a file or directory in bytes.

        Args:
            path: Path to file or directory

        Returns:
            Total size in bytes, 0 if path doesn't exist or permission denied
        """
        # Validate path exists and is readable
        if not path.exists() or not self.check_readable(path):
            return 0

        try:
            # Simple case: single file
            if path.is_file():
                return path.stat().st_size

            # Complex case: directory with recursive traversal
            if path.is_dir():
                total_size = 0
                # Sum all accessible file sizes in directory tree
                for item in path.rglob("*"):
                    if item.is_file():
                        try:
                            total_size += item.stat().st_size
                        except (OSError, PermissionError):
                            # Skip inaccessible files (e.g., permission denied)
                            continue
                return total_size

        except (OSError, PermissionError):
            # Error during directory traversal or stat operation
            pass

        # Default: not a file/directory or error occurred
        return 0

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
        # Determine if source path is under home directory or root filesystem
        # This affects how we reconstruct the path in backup structure
        is_relative_to_home = self.is_relative_to_home(src_path)
        src_relative = (
            src_path.relative_to(Path.home())
            if is_relative_to_home
            else src_path.relative_to(Path("/"))
        )
        # Use 'home' or 'root' prefix for clear backup organization
        prefix = "home" if is_relative_to_home else "root"

        # Build destination path with optional subdirectories
        # Structure: base_path / [hostname] / [date] / prefix / relative_path
        dest_parts: list[Path] = [base_path]
        if hostname_subdir:
            dest_parts.append(Path(self.hostname))
        if date_subdir:
            dest_parts.append(Path(time.strftime("%Y-%m-%d")))
        dest_parts.extend([Path(prefix), src_relative])

        # Combine all path components efficiently
        final_path = dest_parts[0]
        for part in dest_parts[1:]:
            final_path = final_path / part

        return final_path

    def create_archive(
        self,
        dotfiles_to_archive: list[tuple[Path, bool, bool]],
        archive_base_dir: Path,
        hostname_subdir: bool,
    ) -> Path | None:
        """
        Create compressed TAR.GZ archive of existing dotfiles.

        Args:
            dotfiles_to_archive: List of (path, exists, is_dir) tuples
            archive_base_dir: Base directory for archives
            hostname_subdir: Include hostname subdirectory in archive path

        Returns:
            Path to created archive file, or None if operation failed
        """
        # Determine archive path with hostname subdirectory if configured
        archive_base = archive_base_dir
        if hostname_subdir:
            archive_base = archive_base / self.hostname

        # Create archive directory
        self.create_directory(archive_base)

        # Generate timestamped archive filename
        archive_name = (
            f"dotfiles-{datetime.now(UTC).strftime('%Y-%m-%d_%H-%M-%S')}.tar.gz"
        )
        archive_path = archive_base / archive_name

        try:
            # Create compressed TAR.GZ archive
            with tarfile.open(archive_path, "w:gz") as tar:
                for path, exists, _is_dir in dotfiles_to_archive:
                    if exists:
                        tar.add(path)

            return archive_path

        except (OSError, tarfile.TarError):
            return None

    def rotate_archives(
        self, archive_base_dir: Path, hostname_subdir: bool, max_archives: int
    ) -> list[Path]:
        """
        Delete oldest archives exceeding maximum retention limit.

        Args:
            archive_base_dir: Base directory for archives
            hostname_subdir: Whether archives are in hostname subdirectory
            max_archives: Maximum number of archives to retain

        Returns:
            List of deleted archive paths
        """
        # Determine archive base directory
        archive_base = archive_base_dir
        if hostname_subdir:
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
                path for path, _mtime in sorted(archive_list, key=lambda x: x[1])
            ]
        except OSError:
            return deleted_archives

        # Calculate number to delete
        num_to_delete = len(archives) - max_archives

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
        return [f for f in src_dir.rglob("*") if f.is_file()]

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

    def is_relative_to_home(self, path: Path) -> bool:
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
