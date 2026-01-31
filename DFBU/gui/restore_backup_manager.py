#!/usr/bin/env python3
"""
DFBU RestoreBackupManager - Pre-Restore Safety Component

Description:
    Manages automatic backups of files before restore operations, preventing
    data loss if a restore goes wrong. Creates timestamped backup directories
    with TOML manifests tracking what was backed up and why.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 2026-01-31
License: MIT

Features:
    - Automatic backup before restore operations
    - TOML manifest with backup metadata
    - Configurable retention policy (default: 5 backups)
    - Directory structure preservation
    - Cleanup of old backups

Requirements:
    - Linux environment
    - Python 3.14+ for Path.copy() with metadata preservation
    - tomli_w for TOML writing
    - No Qt dependencies (pure model layer)

Classes:
    - RestoreBackupManager: Manages pre-restore backup operations
"""

import logging
import shutil
from pathlib import Path
from typing import Final


# Setup logger for this module
logger = logging.getLogger(__name__)


# =============================================================================
# Constants
# =============================================================================

DEFAULT_BACKUP_DIR: Final[Path] = (
    Path.home() / ".local" / "share" / "dfbu" / "restore-backups"
)
DEFAULT_MAX_BACKUPS: Final[int] = 5


# =============================================================================
# RestoreBackupManager Class
# =============================================================================


class RestoreBackupManager:
    """
    Manages pre-restore backup operations for data safety.

    Creates timestamped backups of files before they are overwritten during
    restore operations. Maintains TOML manifests documenting what was backed
    up and enforces retention policies to limit disk usage.

    Attributes:
        backup_base_dir: Base directory for all restore backups
        max_backups: Maximum number of backups to retain

    Public methods:
        backup_before_restore: Create backup of files before restore
        get_backup_count: Get number of existing backups
        cleanup_old_backups: Remove backups exceeding retention limit
        list_backups: List all backups with timestamps
    """

    def __init__(
        self,
        backup_base_dir: Path | None = None,
        max_backups: int = DEFAULT_MAX_BACKUPS,
    ) -> None:
        """
        Initialize RestoreBackupManager.

        Args:
            backup_base_dir: Base directory for backups (default: ~/.local/share/dfbu/restore-backups)
            max_backups: Maximum backups to retain (default: 5)
        """
        self._backup_base_dir = backup_base_dir or DEFAULT_BACKUP_DIR
        self._max_backups = max_backups

    @property
    def backup_base_dir(self) -> Path:
        """Get base directory for restore backups."""
        return self._backup_base_dir

    @property
    def max_backups(self) -> int:
        """Get maximum number of restore backups to retain."""
        return self._max_backups

    @max_backups.setter
    def max_backups(self, value: int) -> None:
        """Set maximum number of restore backups to retain."""
        self._max_backups = value

    def get_backup_count(self) -> int:
        """
        Get number of existing restore backups.

        Returns:
            Number of backup directories in backup_base_dir
        """
        if not self._backup_base_dir.exists():
            return 0
        return len([d for d in self._backup_base_dir.iterdir() if d.is_dir()])

    def list_backups(self) -> list[tuple[Path, str]]:
        """
        List all restore backups with their timestamps.

        Returns:
            List of (backup_path, timestamp_str) tuples, newest first
        """
        if not self._backup_base_dir.exists():
            return []

        backup_dirs = [d for d in self._backup_base_dir.iterdir() if d.is_dir()]
        # Sort by directory name (timestamp format ensures correct ordering)
        backup_dirs.sort(key=lambda d: d.name, reverse=True)

        return [(d, d.name) for d in backup_dirs]

    def cleanup_old_backups(self) -> list[Path]:
        """
        Remove oldest backups exceeding max_backups limit.

        Returns:
            List of removed backup directory paths
        """
        if not self._backup_base_dir.exists():
            return []

        # Get all backup directories sorted oldest first
        backup_dirs = [d for d in self._backup_base_dir.iterdir() if d.is_dir()]
        backup_dirs.sort(key=lambda d: d.name)  # Oldest first

        removed: list[Path] = []
        while len(backup_dirs) > self._max_backups:
            oldest = backup_dirs.pop(0)
            try:
                shutil.rmtree(oldest)
                removed.append(oldest)
                logger.info(f"Removed old restore backup: {oldest}")
            except OSError as e:
                logger.error(f"Failed to remove backup {oldest}: {e}")

        return removed
