"""
DFBU Model - Facade for Application Components

Description:
    Facade pattern implementation providing unified interface to DFBU components.
    Coordinates ConfigManager, FileOperations, BackupOrchestrator, and
    StatisticsTracker. Maintains backward compatibility with existing ViewModel.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 11-01-2025
License: MIT

Features:
    - Facade pattern for clean component composition
    - Maintains public API for backward compatibility
    - Delegates operations to focused components
    - Single entry point for ViewModel layer
    - Significantly reduced code (~300 lines vs ~1179 lines)

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - Component modules: config_manager, file_operations, backup_orchestrator, statistics_tracker

Classes:
    - DFBUModel: Facade coordinating all components

Functions:
    None
"""

import sys
from pathlib import Path
from socket import gethostname


# Local imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import DotFileDict, OptionsDict

from gui.backup_orchestrator import BackupOrchestrator
from gui.config_manager import ConfigManager
from gui.file_operations import FileOperations
from gui.statistics_tracker import BackupStatistics, StatisticsTracker


# =============================================================================
# DFBUModel Facade
# =============================================================================


class DFBUModel:
    """
    Facade coordinating DFBU application components.

    Provides unified interface to ConfigManager, FileOperations, BackupOrchestrator,
    and StatisticsTracker. Maintains backward compatibility with existing ViewModel
    by exposing the same public API.

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
        toggle_dotfile_enabled: Toggle enabled status of dotfile
        get_dotfile_by_index: Get dotfile metadata by index
        get_dotfile_count: Get number of configured dotfiles
        get_dotfile_sizes: Calculate sizes for all dotfiles
        validate_dotfile_paths: Check which dotfiles exist on system
        expand_path: Expand user home directory in path
        check_readable: Check if path has read permissions
        create_directory: Create directory with permissions
        files_are_identical: Compare files using metadata
        copy_file: Copy file with metadata preservation
        copy_directory: Copy directory recursively
        calculate_path_size: Calculate total size of file or directory
        assemble_dest_path: Build destination path for backup
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
        None (delegation only)
    """

    def __init__(self, config_path: Path) -> None:
        """
        Initialize DFBUModel facade with all components.

        Args:
            config_path: Path to TOML configuration file
        """
        self.hostname: str = gethostname()

        # Initialize FileOperations (needed by ConfigManager)
        self._file_ops = FileOperations(self.hostname)

        # Initialize ConfigManager
        self._config_manager = ConfigManager(
            config_path, expand_path_callback=self._file_ops.expand_path
        )

        # Initialize StatisticsTracker
        self._stats_tracker = StatisticsTracker()

        # Initialize BackupOrchestrator
        self._backup_orchestrator = BackupOrchestrator(
            file_ops=self._file_ops,
            stats_tracker=self._stats_tracker,
            mirror_base_dir=self._config_manager.mirror_base_dir,
            archive_base_dir=self._config_manager.archive_base_dir,
        )

    # =========================================================================
    # Property Accessors for Backward Compatibility
    # =========================================================================

    @property
    def config_path(self) -> Path:
        """Get current configuration file path."""
        return self._config_manager.config_path

    @config_path.setter
    def config_path(self, path: Path) -> None:
        """Set configuration file path."""
        self._config_manager.config_path = path

    @property
    def options(self) -> OptionsDict:
        """Get current options configuration."""
        return self._config_manager.options

    @property
    def dotfiles(self) -> list[DotFileDict]:
        """Get current dotfiles list."""
        return self._config_manager.dotfiles

    @property
    def statistics(self) -> BackupStatistics:
        """Get current operation statistics."""
        return self._stats_tracker.statistics

    @property
    def mirror_base_dir(self) -> Path:
        """Get mirror backup base directory."""
        return self._config_manager.mirror_base_dir

    @mirror_base_dir.setter
    def mirror_base_dir(self, path: Path) -> None:
        """Set mirror backup base directory."""
        self._config_manager.mirror_base_dir = path
        self._backup_orchestrator.mirror_base_dir = path

    @property
    def archive_base_dir(self) -> Path:
        """Get archive backup base directory."""
        return self._config_manager.archive_base_dir

    @archive_base_dir.setter
    def archive_base_dir(self, path: Path) -> None:
        """Set archive backup base directory."""
        self._config_manager.archive_base_dir = path
        self._backup_orchestrator.archive_base_dir = path

    def get_config_manager(self) -> ConfigManager:
        """
        Get the ConfigManager instance for worker threads.

        Returns:
            ConfigManager instance
        """
        return self._config_manager

    # =========================================================================
    # Configuration Management (Delegate to ConfigManager)
    # =========================================================================

    def load_config(self) -> tuple[bool, str]:
        """
        Load and validate TOML configuration file.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        success, error = self._config_manager.load_config()

        # Update BackupOrchestrator with new base directories
        if success:
            self._backup_orchestrator.mirror_base_dir = (
                self._config_manager.mirror_base_dir
            )
            self._backup_orchestrator.archive_base_dir = (
                self._config_manager.archive_base_dir
            )

        return success, error

    def save_config(self) -> tuple[bool, str]:
        """
        Save current configuration back to TOML file with automatic rotating backups.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        return self._config_manager.save_config()

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
        return self._config_manager.add_dotfile(
            category, application, description, paths, enabled
        )

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
        return self._config_manager.update_dotfile(
            index, category, application, description, paths, enabled
        )

    def remove_dotfile(self, index: int) -> bool:
        """
        Remove a dotfile entry from the configuration by index.

        Args:
            index: Index of dotfile to remove

        Returns:
            True if dotfile was removed successfully
        """
        return self._config_manager.remove_dotfile(index)

    def toggle_dotfile_enabled(self, index: int) -> bool:
        """
        Toggle the enabled status of a dotfile entry.

        Args:
            index: Index of dotfile to toggle

        Returns:
            New enabled status if successful, current status otherwise
        """
        return self._config_manager.toggle_dotfile_enabled(index)

    def update_option(self, key: str, value: bool | int | str) -> bool:
        """
        Update a single configuration option.

        Args:
            key: Option key to update
            value: New value for the option

        Returns:
            True if option was updated successfully
        """
        return self._config_manager.update_option(key, value)

    def update_path(self, path_type: str, value: str) -> bool:
        """
        Update mirror_dir or archive_dir path.

        Args:
            path_type: Either "mirror_dir" or "archive_dir"
            value: New path value

        Returns:
            True if path was updated successfully
        """
        success = self._config_manager.update_path(path_type, value)

        # Update BackupOrchestrator with new base directories
        if success:
            self._backup_orchestrator.mirror_base_dir = (
                self._config_manager.mirror_base_dir
            )
            self._backup_orchestrator.archive_base_dir = (
                self._config_manager.archive_base_dir
            )

        return success

    def get_dotfile_by_index(self, index: int) -> DotFileDict | None:
        """
        Get dotfile metadata by index.

        Args:
            index: Index in dotfiles list

        Returns:
            Dotfile dictionary or None if invalid index
        """
        return self._config_manager.get_dotfile_by_index(index)

    def get_dotfile_count(self) -> int:
        """
        Get number of configured dotfiles.

        Returns:
            Number of dotfiles in configuration
        """
        return self._config_manager.get_dotfile_count()

    # =========================================================================
    # File Operations (Delegate to FileOperations)
    # =========================================================================

    def expand_path(self, path_str: str) -> Path:
        """
        Expand user home directory in path string.

        Args:
            path_str: Path string potentially containing ~

        Returns:
            Expanded Path object
        """
        return self._file_ops.expand_path(path_str)

    def check_readable(self, path: Path) -> bool:
        """
        Check if path has read permissions.

        Args:
            path: Path to check

        Returns:
            True if readable, False otherwise
        """
        return self._file_ops.check_readable(path)

    def create_directory(self, path: Path, mode: int = 0o755) -> None:
        """
        Create directory with proper permissions.

        Args:
            path: Directory path to create
            mode: Directory permissions mode
        """
        self._file_ops.create_directory(path, mode)

    def files_are_identical(self, src_path: Path, dest_path: Path) -> bool:
        """
        Compare two files to determine if they are identical.

        Args:
            src_path: Source file path
            dest_path: Destination file path

        Returns:
            True if files are identical (same size and mtime), False otherwise
        """
        return self._file_ops.files_are_identical(src_path, dest_path)

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
        return self._file_ops.copy_file(
            src_path, dest_path, create_parent, skip_identical
        )

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
        return self._file_ops.copy_directory(src_path, dest_base, skip_identical)

    def calculate_path_size(self, path: Path) -> int:
        """
        Calculate total size of a file or directory in bytes.

        Args:
            path: Path to file or directory

        Returns:
            Total size in bytes, 0 if path doesn't exist or permission denied
        """
        return self._file_ops.calculate_path_size(path)

    def get_dotfile_sizes(self) -> dict[int, int]:
        """
        Calculate sizes for all configured dotfiles.

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
        return self._file_ops.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

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
        return self._file_ops.create_archive(
            dotfiles_to_archive, self.archive_base_dir, self.options["hostname_subdir"]
        )

    def rotate_archives(self) -> list[Path]:
        """
        Delete oldest archives exceeding maximum retention limit.

        Returns:
            List of deleted archive paths
        """
        return self._file_ops.rotate_archives(
            self.archive_base_dir,
            self.options["hostname_subdir"],
            self.options["max_archives"],
        )

    def discover_restore_files(self, src_dir: Path) -> list[Path]:
        """
        Find all files in restore source directory recursively.

        Args:
            src_dir: Source directory containing backup files

        Returns:
            List of all file paths found
        """
        return self._file_ops.discover_restore_files(src_dir)

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
        return self._file_ops.reconstruct_restore_paths(src_files)

    # =========================================================================
    # Backup/Restore Operations (Delegate to BackupOrchestrator)
    # =========================================================================

    def validate_dotfile_paths(self) -> dict[int, tuple[bool, bool, str]]:
        """
        Validate all dotfile paths exist and determine their types.

        Returns:
            Dict mapping dotfile index to (exists, is_dir, type_str) tuple
        """
        return self._backup_orchestrator.validate_dotfile_paths(self.dotfiles)

    # =========================================================================
    # Statistics Tracking (Delegate to StatisticsTracker)
    # =========================================================================

    def record_item_processed(self, processing_time: float) -> None:
        """
        Record successfully processed item.

        Args:
            processing_time: Time taken to process item
        """
        self._stats_tracker.record_item_processed(processing_time)

    def record_item_skipped(self) -> None:
        """Record skipped item (not exist or no permission)."""
        self._stats_tracker.record_item_skipped()

    def record_item_failed(self) -> None:
        """Record failed item."""
        self._stats_tracker.record_item_failed()

    def reset_statistics(self) -> None:
        """Reset operation statistics for new run."""
        self._stats_tracker.reset_statistics()
