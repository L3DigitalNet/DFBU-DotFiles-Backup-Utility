"""
DFBU Protocol Definitions - Interface Abstractions for Dependency Inversion

Description:
    Protocol definitions for DFBU GUI application following the Dependency
    Inversion Principle (DIP). Defines interfaces that allow components to
    depend on abstractions rather than concrete implementations, improving
    testability and maintainability.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-05-2025
License: MIT

Features:
    - Protocol definitions for service layer interfaces
    - Enables dependency injection with type safety
    - Facilitates mocking in tests without complex class hierarchies
    - Follows Interface Segregation Principle (ISP)
    - Pure Python typing without runtime overhead

Requirements:
    - Python 3.14+ for Protocol support
    - typing module from standard library

Classes:
    - FileOperationsProtocol: Interface for file system operations
    - ConfigManagerProtocol: Interface for configuration management
    - StatisticsTrackerProtocol: Interface for statistics tracking
    - BackupOrchestratorProtocol: Interface for backup orchestration

Functions:
    None
"""

import sys
from pathlib import Path
from typing import Protocol


sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import DotFileDict, OptionsDict

from gui.statistics_tracker import BackupStatistics


# =============================================================================
# File Operations Protocol
# =============================================================================


class FileOperationsProtocol(Protocol):
    """
    Protocol defining interface for file system operations.

    Implementations must provide file/directory operations including
    path expansion, permission checking, copying, and size calculation.
    """

    def expand_path(self, path_str: str) -> Path:
        """
        Expand user home directory in path string.

        Args:
            path_str: Path string potentially containing ~

        Returns:
            Expanded Path object
        """
        ...

    def check_readable(self, path: Path) -> bool:
        """
        Check if path has read permissions.

        Args:
            path: Path to check

        Returns:
            True if readable, False otherwise
        """
        ...

    def create_directory(self, path: Path, mode: int = 0o755) -> None:
        """
        Create directory with proper permissions.

        Args:
            path: Directory path to create
            mode: Directory permissions mode
        """
        ...

    def files_are_identical(self, src_path: Path, dest_path: Path) -> bool:
        """
        Compare two files to determine if they are identical.

        Args:
            src_path: Source file path
            dest_path: Destination file path

        Returns:
            True if files are identical (same size and mtime), False otherwise
        """
        ...

    def copy_file(
        self,
        src_path: Path,
        dest_path: Path,
        create_parent: bool = True,
        skip_identical: bool = False,
    ) -> bool:
        """
        Copy file with metadata preservation.

        Args:
            src_path: Source file path
            dest_path: Destination file path
            create_parent: Whether to create parent directories
            skip_identical: Whether to skip copying if files are identical

        Returns:
            True if copied successfully or skipped due to identical files
        """
        ...

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
        """
        ...

    def calculate_path_size(self, path: Path) -> int:
        """
        Calculate total size of a file or directory in bytes.

        Args:
            path: Path to file or directory

        Returns:
            Total size in bytes, 0 if path doesn't exist or permission denied
        """
        ...

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
        ...

    def create_archive(
        self, dotfiles_to_archive: list[tuple[Path, bool, bool]]
    ) -> Path | None:
        """
        Create compressed TAR.GZ archive of existing dotfiles.

        Args:
            dotfiles_to_archive: List of (path, exists, is_dir) tuples

        Returns:
            Path to created archive file, or None if operation failed
        """
        ...

    def rotate_archives(self) -> list[Path]:
        """
        Delete oldest archives exceeding maximum retention limit.

        Returns:
            List of deleted archive paths
        """
        ...

    def discover_restore_files(self, src_dir: Path) -> list[Path]:
        """
        Find all files in restore source directory recursively.

        Args:
            src_dir: Source directory containing backup files

        Returns:
            List of all file paths found
        """
        ...

    def reconstruct_restore_paths(
        self, src_files: list[Path]
    ) -> list[tuple[Path, Path | None]]:
        """
        Build original destination paths from backup structure.

        Args:
            src_files: List of source files from backup

        Returns:
            List of (src_path, dest_path) tuples
        """
        ...


# =============================================================================
# Configuration Manager Protocol
# =============================================================================


class ConfigManagerProtocol(Protocol):
    """
    Protocol defining interface for configuration management.

    Implementations must provide configuration loading, saving, validation,
    and manipulation operations.
    """

    @property
    def config_path(self) -> Path:
        """Get current configuration file path."""
        ...

    @config_path.setter
    def config_path(self, path: Path) -> None:
        """Set configuration file path."""
        ...

    @property
    def options(self) -> OptionsDict:
        """Get current options configuration."""
        ...

    @property
    def dotfiles(self) -> list[DotFileDict]:
        """Get current dotfiles list."""
        ...

    @property
    def mirror_base_dir(self) -> Path:
        """Get mirror backup base directory."""
        ...

    @mirror_base_dir.setter
    def mirror_base_dir(self, path: Path) -> None:
        """Set mirror backup base directory."""
        ...

    @property
    def archive_base_dir(self) -> Path:
        """Get archive backup base directory."""
        ...

    @archive_base_dir.setter
    def archive_base_dir(self, path: Path) -> None:
        """Set archive backup base directory."""
        ...

    def load_config(self) -> tuple[bool, str]:
        """
        Load and validate TOML configuration file.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        ...

    def save_config(self) -> tuple[bool, str]:
        """
        Save current configuration back to TOML file with automatic rotating backups.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        ...

    def add_dotfile(
        self,
        category: str,
        application: str,
        description: str,
        paths: list[str],
        enabled: bool = True,
    ) -> bool:
        """
        Add a new dotfile entry to the configuration.

        Args:
            category: Category for the dotfile
            application: Application name
            description: Description of the dotfile
            paths: List of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was added successfully
        """
        ...

    def update_dotfile(
        self,
        index: int,
        category: str,
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
            application: Updated application name
            description: Updated description
            paths: Updated list of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was updated successfully
        """
        ...

    def remove_dotfile(self, index: int) -> bool:
        """
        Remove a dotfile entry from the configuration by index.

        Args:
            index: Index of dotfile to remove

        Returns:
            True if dotfile was removed successfully
        """
        ...

    def toggle_dotfile_enabled(self, index: int) -> bool:
        """
        Toggle the enabled status of a dotfile entry.

        Args:
            index: Index of dotfile to toggle

        Returns:
            New enabled status if successful, current status otherwise
        """
        ...

    def update_option(self, key: str, value: bool | int | str) -> bool:
        """
        Update a single configuration option.

        Args:
            key: Option key to update
            value: New value for the option

        Returns:
            True if option was updated successfully
        """
        ...

    def update_path(self, path_type: str, value: str) -> bool:
        """
        Update mirror_dir or archive_dir path.

        Args:
            path_type: Either "mirror_dir" or "archive_dir"
            value: New path value

        Returns:
            True if path was updated successfully
        """
        ...

    def get_dotfile_by_index(self, index: int) -> DotFileDict | None:
        """
        Get dotfile metadata by index.

        Args:
            index: Index in dotfiles list

        Returns:
            Dotfile dictionary or None if invalid index
        """
        ...

    def get_dotfile_count(self) -> int:
        """
        Get number of configured dotfiles.

        Returns:
            Number of dotfiles in configuration
        """
        ...


# =============================================================================
# Statistics Tracker Protocol
# =============================================================================


class StatisticsTrackerProtocol(Protocol):
    """
    Protocol defining interface for backup/restore statistics tracking.

    Implementations must provide statistics recording and retrieval.
    """

    @property
    def statistics(self) -> BackupStatistics:
        """Get current operation statistics."""
        ...

    def record_item_processed(self, processing_time: float) -> None:
        """
        Record successfully processed item.

        Args:
            processing_time: Time taken to process item
        """
        ...

    def record_item_skipped(self) -> None:
        """Record skipped item (not exist or no permission)."""
        ...

    def record_item_failed(self) -> None:
        """Record failed item."""
        ...

    def reset_statistics(self) -> None:
        """Reset operation statistics for new run."""
        ...


# =============================================================================
# Backup Orchestrator Protocol
# =============================================================================


class BackupOrchestratorProtocol(Protocol):
    """
    Protocol defining interface for backup orchestration.

    Implementations must coordinate backup operations across components.
    """

    @property
    def mirror_base_dir(self) -> Path:
        """Get mirror backup base directory."""
        ...

    @mirror_base_dir.setter
    def mirror_base_dir(self, path: Path) -> None:
        """Set mirror backup base directory."""
        ...

    @property
    def archive_base_dir(self) -> Path:
        """Get archive backup base directory."""
        ...

    @archive_base_dir.setter
    def archive_base_dir(self, path: Path) -> None:
        """Set archive backup base directory."""
        ...

    def validate_dotfile_paths(
        self, dotfiles: list[DotFileDict]
    ) -> dict[int, tuple[bool, bool, str]]:
        """
        Validate all dotfile paths exist and determine their types.

        Args:
            dotfiles: List of dotfile dictionaries to validate

        Returns:
            Dict mapping dotfile index to (exists, is_dir, type_str) tuple
        """
        ...
