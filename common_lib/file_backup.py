#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Backup Utility - Rotating Backup Management

Description:
    Utility module for creating and managing rotating file backups. Provides
    simple interface for creating timestamped backup copies of files with
    automatic rotation to maintain a maximum number of backups.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 10-30-2025
License: MIT

Features:
    - Timestamped backup file creation with ISO 8601 format
    - Automatic rotation to maintain maximum backup count
    - Age-based backup sorting for consistent rotation
    - Directory auto-creation for backup storage
    - Python standard library first approach with minimal dependencies
    - Clean architecture with confident design patterns

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - Standard library only: pathlib, datetime, shutil

Known Issues:
    - Error handling deferred until v1.0.0 per confident design pattern

Planned Features:
    - Compression support for backup files
    - Backup verification and integrity checking
    - Configurable backup naming patterns

Classes:
    None

Functions:
    - create_rotating_backup: Create timestamped backup with automatic rotation
    - rotate_old_backups: Delete oldest backups exceeding maximum count
    - get_backup_files: Find all backup files for a specific source file
"""

import shutil
from datetime import datetime
from pathlib import Path


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

    Example:
        >>> backup_path, success = create_rotating_backup(
        ...     Path("config.toml"),
        ...     backup_dir=Path("backups"),
        ...     max_backups=5
        ... )
        >>> if success:
        ...     print(f"Backup created: {backup_path}")
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

    Example:
        >>> deleted = rotate_old_backups(
        ...     Path("config.toml"),
        ...     Path("backups"),
        ...     max_backups=5
        ... )
        >>> print(f"Deleted {len(deleted)} old backups")
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

    Example:
        >>> backups = get_backup_files(Path("config.toml"), Path("backups"))
        >>> print(f"Found {len(backups)} backups")
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
