"""
DFBU ViewModel - Presentation Logic Layer

Description:
    ViewModel layer for DFBU GUI implementing MVVM pattern. Mediates between
    Model and View, managing worker threads, signals/slots, and exposing properties
    and commands. Handles presentation logic while keeping View and Model separated.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 10-31-2025
License: MIT

Features:
    - MVVM ViewModel layer separating presentation logic from View and Model
    - Signal-based communication with View for reactive updates
    - Worker thread management for non-blocking backup/restore operations
    - Command pattern for user actions (backup, restore, config load, etc.)
    - Property exposure for data binding and state queries
    - Settings persistence and restoration for UI state
    - Interactive dotfile management with add, update, and remove commands
    - Python standard library first approach with minimal dependencies
    - Clean architecture with confident design patterns

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - PySide6 framework for Qt signals and threading
    - model module for business logic

Classes:
    - BackupWorker: Worker thread for backup operations
    - RestoreWorker: Worker thread for restore operations
    - DFBUViewModel: ViewModel mediating between Model and View

Functions:
    None
"""

import time
from pathlib import Path
from typing import Any, Final

# Local imports
from core.common_types import DotFileDict, OptionsDict
from PySide6.QtCore import QObject, QSettings, QThread, Signal

from gui.config_workers import ConfigLoadWorker, ConfigSaveWorker
from gui.input_validation import InputValidator
from gui.model import DFBUModel


class BackupWorker(QThread):
    """
    Worker thread for backup operations to prevent UI blocking.

    Attributes:
        progress_updated: Signal emitted when progress percentage changes
        item_processed: Signal emitted when an item completes processing
        item_skipped: Signal emitted when an item is skipped
        backup_finished: Signal emitted when backup completes
        error_occurred: Signal emitted when an error occurs
        model: Reference to DFBUModel for data access
        mirror_mode: Whether to perform mirror backup
        archive_mode: Whether to create archive
        force_full_backup: Whether to disable skip_identical optimization

    Public methods:
        run: Main thread execution method
        set_model: Set the model reference
        set_modes: Set backup operation modes
        set_force_full_backup: Set force full backup mode

    Private methods:
        _process_mirror_backup: Process mirror backup for all dotfiles
        _process_archive_backup: Create compressed archive
        _process_file: Process individual file backup
        _process_directory: Process directory backup recursively
    """

    # Signal definitions
    progress_updated = Signal(int)  # progress percentage
    item_processed = Signal(str, str)  # source_path, dest_path
    item_skipped = Signal(str, str)  # path, reason
    backup_finished = Signal()
    error_occurred = Signal(str, str)  # context, error_message

    def __init__(self) -> None:
        """Initialize the BackupWorker."""
        super().__init__()
        self.model: DFBUModel | None = None
        self.mirror_mode: bool = True
        self.archive_mode: bool = False
        self.force_full_backup: bool = False

    def set_model(self, model: DFBUModel) -> None:
        """
        Set the model reference.

        Args:
            model: DFBUModel instance
        """
        self.model = model

    def set_modes(self, mirror: bool, archive: bool) -> None:
        """
        Set backup operation modes.

        Args:
            mirror: Whether to perform mirror backup
            archive: Whether to create archive
        """
        self.mirror_mode = mirror
        self.archive_mode = archive

    def set_force_full_backup(self, force_full: bool) -> None:
        """
        Set force full backup mode.

        Args:
            force_full: If True, disable skip_identical optimization
        """
        self.force_full_backup = force_full

    def _process_file(
        self, src_path: Path, dest_path: Path, skip_identical: bool = False
    ) -> bool:
        """
        Process individual file backup with comprehensive error handling.

        Args:
            src_path: Source file path
            dest_path: Destination file path
            skip_identical: Whether to skip copying if files are identical

        Returns:
            True if successful, False otherwise
        """
        # Model must be set before running
        if not self.model:
            self.error_occurred.emit(
                str(src_path), "Internal error: Model not initialized"
            )
            return False

        start_time = time.perf_counter()

        try:
            # Check source file exists
            if not src_path.exists():
                self.item_skipped.emit(str(src_path), "File not found")
                self.model.record_item_skipped()
                return False

            # Check readability
            if not self.model.check_readable(src_path):
                self.item_skipped.emit(
                    str(src_path), "Permission denied (no read access)"
                )
                self.model.record_item_skipped()
                return False

            # Check if file is identical before copying (optimization for mirror mode)
            if skip_identical and self.model.files_are_identical(src_path, dest_path):
                self.item_skipped.emit(str(src_path), "File unchanged")
                self.model.record_item_skipped()
                return True

            # Copy file with skip_identical optimization
            success = self.model.copy_file(
                src_path, dest_path, create_parent=True, skip_identical=skip_identical
            )

            if success:
                elapsed = time.perf_counter() - start_time
                self.model.record_item_processed(elapsed)
                self.item_processed.emit(str(src_path), str(dest_path))
            else:
                self.model.record_item_failed()
                self.error_occurred.emit(
                    str(src_path), "Failed to copy file (unknown error)"
                )

            return success

        except PermissionError as e:
            self.item_skipped.emit(str(src_path), f"Permission denied: {e}")
            self.model.record_item_skipped()
            return False
        except FileNotFoundError as e:
            self.item_skipped.emit(str(src_path), f"File not found: {e}")
            self.model.record_item_skipped()
            return False
        except OSError as e:
            # Disk full, read-only filesystem, etc.
            self.error_occurred.emit(str(src_path), f"Filesystem error: {e}")
            self.model.record_item_failed()
            return False
        except Exception as e:
            # Catch-all for unexpected errors
            self.error_occurred.emit(
                str(src_path), f"Unexpected error: {type(e).__name__}: {e}"
            )
            self.model.record_item_failed()
            return False

    def _process_directory(
        self, src_path: Path, dest_path: Path, skip_identical: bool = False
    ) -> int:
        """
        Process directory backup recursively with comprehensive error handling.

        Args:
            src_path: Source directory path
            dest_path: Destination directory path
            skip_identical: Whether to skip copying if files are identical

        Returns:
            Number of successfully copied files
        """
        # Model must be set before running
        if not self.model:
            self.error_occurred.emit(
                str(src_path), "Internal error: Model not initialized"
            )
            return 0

        try:
            # Check directory exists
            if not src_path.exists():
                self.item_skipped.emit(str(src_path), "Directory not found")
                self.model.record_item_skipped()
                return 0

            # Check it's actually a directory
            if not src_path.is_dir():
                self.item_skipped.emit(str(src_path), "Not a directory")
                self.model.record_item_skipped()
                return 0

            # Check readability
            if not self.model.check_readable(src_path):
                self.item_skipped.emit(
                    str(src_path), "Permission denied (no read access)"
                )
                self.model.record_item_skipped()
                return 0

            # Copy directory with skip_identical optimization
            results = self.model.copy_directory(
                src_path, dest_path, skip_identical=skip_identical
            )

            # Process results
            success_count = 0
            skipped_count = 0
            for src_file, dest_file, success, skipped in results:
                if success:
                    if skipped:
                        skipped_count += 1
                        self.item_skipped.emit(str(src_file), "File unchanged")
                    else:
                        success_count += 1
                        self.item_processed.emit(str(src_file), str(dest_file))
                elif dest_file is None:
                    self.item_skipped.emit(
                        str(src_file), "Permission denied or read error"
                    )
                else:
                    self.error_occurred.emit(str(src_file), "Failed to copy file")

            return success_count

        except PermissionError as e:
            self.item_skipped.emit(str(src_path), f"Permission denied: {e}")
            self.model.record_item_skipped()
            return 0
        except FileNotFoundError as e:
            self.item_skipped.emit(str(src_path), f"Directory not found: {e}")
            self.model.record_item_skipped()
            return 0
        except OSError as e:
            # Disk full, read-only filesystem, etc.
            self.error_occurred.emit(str(src_path), f"Filesystem error: {e}")
            self.model.record_item_failed()
            return 0
        except Exception as e:
            # Catch-all for unexpected errors
            self.error_occurred.emit(
                str(src_path), f"Unexpected error: {type(e).__name__}: {e}"
            )
            self.model.record_item_failed()
            return 0

    def _process_mirror_backup(self) -> None:
        """Process mirror backup for all configured dotfiles."""
        # Model must be set before running (architectural guarantee)
        if not self.model:
            return

        # Validate which dotfiles exist on the filesystem before attempting backup
        # Returns dict mapping index -> (exists, is_dir, type_str) tuple
        validation_results = self.model.validate_dotfile_paths()

        # Count total items that actually exist (exist flag is first tuple element)
        # This gives us the denominator for progress calculation
        total_items = len([v for v in validation_results.values() if v[0]])

        # Nothing to back up - emit error and exit early
        if total_items == 0:
            self.error_occurred.emit("Mirror Backup", "No items found to backup")
            return

        # Track number of successfully processed items for progress updates
        processed_count = 0

        # Iterate through all configured dotfiles by index
        for i in range(self.model.get_dotfile_count()):
            dotfile = self.model.get_dotfile_by_index(i)
            if not dotfile:
                continue

            # Skip disabled dotfiles - user may have temporarily disabled certain entries
            if not dotfile.get("enabled", True):
                continue

            # Process each path in the dotfile's paths list
            # Note: GUI supports multiple paths per dotfile entry (unlike CLI)
            for path_str in dotfile["paths"]:
                # Skip empty path strings (validation should prevent this, but be safe)
                if not path_str:
                    continue

                # Expand tilde (~) and environment variables in path string
                src_path = self.model.expand_path(path_str)

                # Check if source path exists on filesystem
                # Non-existent paths are skipped silently (already reported in validation)
                if not src_path.exists():
                    continue

                # Determine if source is directory or file for proper handling
                is_dir = src_path.is_dir()

                # Assemble destination path using configured directory structure
                # Includes hostname and date subdirectories based on options
                dest_path = self.model.assemble_dest_path(
                    self.model.mirror_base_dir,
                    src_path,
                    self.model.options["hostname_subdir"],
                    self.model.options["date_subdir"],
                )

                # Process based on type with skip_identical optimization
                # skip_identical can be disabled by force_full_backup setting
                # When force_full_backup=True, all files are copied regardless of changes
                skip_identical = not self.force_full_backup

                if is_dir:
                    # Process directory recursively - returns count of successfully copied files
                    file_count = self._process_directory(
                        src_path, dest_path, skip_identical=skip_identical
                    )
                    # Only increment processed_count if at least one file was copied
                    if file_count > 0:
                        processed_count += 1
                elif self._process_file(
                    src_path, dest_path, skip_identical=skip_identical
                ):
                    # Process single file - increment on success
                    processed_count += 1

                # Update progress bar with percentage complete
                # Zero division protection (total_items guaranteed > 0 from earlier check)
                if total_items > 0:
                    progress = int((processed_count / total_items) * 100)
                    self.progress_updated.emit(progress)

    def _process_archive_backup(self) -> None:
        """Create compressed archive of configured dotfiles."""
        # Model must be set before running (architectural guarantee)
        if not self.model:
            return

        # Build list of items to include in archive
        # Tuple format: (path, exists, is_dir) for model.create_archive()
        items_to_archive: list[tuple[Path, bool, bool]] = []

        # Iterate through all configured dotfiles
        for i in range(self.model.get_dotfile_count()):
            dotfile = self.model.get_dotfile_by_index(i)
            if not dotfile:
                continue

            # Skip disabled dotfiles - respect user's enable/disable settings
            if not dotfile.get("enabled", True):
                continue

            # Process each path in the dotfile's paths list
            # Note: Archives can contain multiple paths per dotfile entry
            for path_str in dotfile["paths"]:
                # Skip empty path strings
                if not path_str:
                    continue

                # Expand tilde (~) and environment variables in path
                src_path = self.model.expand_path(path_str)

                # Only include paths that actually exist on the filesystem
                # Non-existent paths are silently skipped from archive
                if src_path.exists():
                    # Determine type for tarfile processing
                    is_dir = src_path.is_dir()
                    # Add to archive list with metadata (path, exists=True, is_dir)
                    items_to_archive.append((src_path, True, is_dir))

        # Nothing to archive - emit error and exit early
        if not items_to_archive:
            self.error_occurred.emit("Archive Backup", "No items found to archive")
            return

        # Create compressed TAR.GZ archive with timestamp
        # Returns Path to created archive or None on failure
        archive_path = self.model.create_archive(items_to_archive)

        if archive_path:
            # Archive created successfully - emit success signal
            self.item_processed.emit("Archive created", str(archive_path))

            # Rotate (delete) old archives if rotation is enabled
            # Maintains max_archives limit by deleting oldest archives first
            if self.model.options["rotate_archives"]:
                deleted = self.model.rotate_archives()
                # Emit signal for each deleted archive for UI feedback
                for deleted_path in deleted:
                    self.item_processed.emit("Archive deleted", str(deleted_path))
        else:
            # Archive creation failed - emit error signal
            self.error_occurred.emit("Archive Backup", "Failed to create archive")

    def run(self) -> None:
        """Main thread execution method for backup operations."""
        # Model must be set before running (architectural guarantee)
        if not self.model:
            return

        # Start timing for performance metrics
        start_time = time.perf_counter()

        # Reset statistics from any previous backup operation
        # Ensures clean slate for current backup run
        self.model.reset_statistics()

        # Process mirror backup if enabled in configuration
        # Mirror backup = uncompressed file copies maintaining directory structure
        if self.mirror_mode:
            self._process_mirror_backup()

        # Process archive backup if enabled in configuration
        # Archive backup = compressed TAR.GZ with timestamped filename
        if self.archive_mode:
            self._process_archive_backup()

        # Calculate and record total elapsed time for statistics
        end_time = time.perf_counter()
        self.model.statistics.total_time = end_time - start_time

        # Emit completion signal to notify ViewModel/View of finished operation
        # ViewModel will disconnect signals and display statistics summary
        self.backup_finished.emit()


class RestoreWorker(QThread):
    """
    Worker thread for restore operations to prevent UI blocking.

    Attributes:
        progress_updated: Signal emitted when progress percentage changes
        item_processed: Signal emitted when an item completes processing
        restore_finished: Signal emitted when restore completes
        error_occurred: Signal emitted when an error occurs
        model: Reference to DFBUModel for data access
        source_directory: Source directory containing backups

    Public methods:
        run: Main thread execution method
        set_model: Set the model reference
        set_source_directory: Set source directory for restore
    """

    # Signal definitions
    progress_updated = Signal(int)  # progress percentage
    item_processed = Signal(str, str)  # source_path, dest_path
    restore_finished = Signal()
    error_occurred = Signal(str, str)  # context, error_message

    def __init__(self) -> None:
        """Initialize the RestoreWorker."""
        super().__init__()
        self.model: DFBUModel | None = None
        self.source_directory: Path | None = None

    def set_model(self, model: DFBUModel) -> None:
        """
        Set the model reference.

        Args:
            model: DFBUModel instance
        """
        self.model = model

    def set_source_directory(self, directory: Path) -> None:
        """
        Set source directory for restore.

        Args:
            directory: Source directory containing backups
        """
        self.source_directory = directory

    def run(self) -> None:
        """Main thread execution method for restore operations."""
        # Model and source directory must be set before running (architectural guarantee)
        if not self.model or not self.source_directory:
            return

        # Start timing for performance metrics
        start_time = time.perf_counter()

        # Reset statistics from any previous restore operation
        self.model.reset_statistics()

        # Execute restore via BackupOrchestrator (includes pre-restore backup if enabled)
        # Callbacks emit signals for progress and item processing
        processed, total = self.model.execute_restore(
            src_dir=self.source_directory,
            progress_callback=lambda pct: self.progress_updated.emit(pct),
            item_processed_callback=lambda src, dest: self.item_processed.emit(src, dest),
        )

        # Handle error cases
        if total == 0:
            self.error_occurred.emit("Restore", "No files found in source directory")
            return
        if processed == 0 and total > 0:
            self.error_occurred.emit("Restore", "Restore operation failed")
            return

        # Calculate and record total elapsed time for statistics
        end_time = time.perf_counter()
        self.model.statistics.total_time = end_time - start_time

        # Emit completion signal to notify ViewModel/View of finished operation
        self.restore_finished.emit()


class DFBUViewModel(QObject):
    """
    ViewModel mediating between Model and View in MVVM pattern.

    Attributes:
        model: DFBUModel instance managing state
        backup_worker: Worker thread for backup operations
        restore_worker: Worker thread for restore operations
        config_load_worker: Worker thread for loading configuration
        config_save_worker: Worker thread for saving configuration
        settings: QSettings for persistence
        progress_updated: Signal for progress changes
        item_processed: Signal for individual item completion
        item_skipped: Signal for skipped items
        operation_finished: Signal for operation completion
        error_occurred: Signal for error notifications
        config_loaded: Signal when configuration loads
        dotfiles_updated: Signal when dotfile list changes

    Public methods:
        command_load_config: Load YAML configuration directory
        command_save_config: Save configuration changes to YAML files
        command_update_option: Update a configuration option
        command_update_path: Update mirror_dir or archive_dir path
        command_add_dotfile: Add a new dotfile entry to configuration
        command_update_dotfile: Update an existing dotfile entry in configuration
        command_remove_dotfile: Remove a dotfile entry from configuration
        command_start_backup: Start backup operation
        command_start_restore: Start restore operation
        command_set_restore_source: Set restore source directory
        get_dotfile_count: Get number of configured dotfiles
        get_dotfile_list: Get list of dotfile metadata
        get_dotfile_validation: Get validation status for all dotfiles
        get_statistics_summary: Get formatted statistics
        get_options: Get backup operation options
        load_settings: Load persisted settings
        save_settings: Save current settings

    Private methods:
        _on_worker_progress: Handle worker progress updates
        _on_item_processed: Handle worker item completion
        _on_item_skipped: Handle worker item skipped
        _on_backup_finished: Handle backup completion
        _on_restore_finished: Handle restore completion
        _on_worker_error: Handle worker errors
    """

    # Signal definitions
    progress_updated = Signal(int)
    item_processed = Signal(str, str)
    item_skipped = Signal(str, str)
    operation_finished = Signal(str)  # statistics summary
    error_occurred = Signal(str, str)
    config_loaded = Signal(int)  # dotfile count
    dotfiles_updated = Signal(int)
    exclusions_changed = Signal()  # emitted when exclusion list changes

    SETTINGS_ORG: Final[str] = "L3DigitalNet"
    SETTINGS_APP: Final[str] = "dfbu_gui_settings"

    def __init__(self, model: DFBUModel) -> None:
        """
        Initialize the DFBUViewModel.

        Args:
            model: DFBUModel instance
        """
        super().__init__()
        self.model: DFBUModel = model
        self.backup_worker: BackupWorker | None = None
        self.restore_worker: RestoreWorker | None = None
        self.config_load_worker: ConfigLoadWorker | None = None
        self.config_save_worker: ConfigSaveWorker | None = None
        self.settings: QSettings = QSettings(self.SETTINGS_ORG, self.SETTINGS_APP)
        self.restore_source_directory: Path | None = None

    def command_load_config(self) -> bool:
        """
        Command to load YAML configuration directory asynchronously.

        Uses ConfigLoadWorker to prevent UI blocking during file I/O.

        Returns:
            True if load operation started successfully
        """
        # Don't start new load if one is already in progress
        if self.config_load_worker is not None:
            return False

        # Create and configure worker
        self.config_load_worker = ConfigLoadWorker()
        self.config_load_worker.set_config_manager(self.model.get_config_manager())

        # Connect worker signals
        self.config_load_worker.progress_updated.connect(self._on_config_progress)
        self.config_load_worker.load_finished.connect(self._on_config_load_finished)
        self.config_load_worker.error_occurred.connect(self._on_worker_error)

        # Start worker thread
        self.config_load_worker.start()
        return True

    def command_save_config(self) -> bool:
        """
        Command to save configuration changes to YAML files asynchronously.

        Uses ConfigSaveWorker to prevent UI blocking during file I/O.

        Returns:
            True if save operation started successfully
        """
        # Don't start new save if one is already in progress
        if self.config_save_worker is not None:
            return False

        # Create and configure worker
        self.config_save_worker = ConfigSaveWorker()
        self.config_save_worker.set_config_manager(self.model.get_config_manager())

        # Connect worker signals
        self.config_save_worker.progress_updated.connect(self._on_config_progress)
        self.config_save_worker.save_finished.connect(self._on_config_save_finished)
        self.config_save_worker.error_occurred.connect(self._on_worker_error)

        # Start worker thread
        self.config_save_worker.start()
        return True

    def command_update_option(self, key: str, value: bool | int | str) -> bool:
        """
        Command to update a configuration option with type safety.

        Args:
            key: Option key to update
            value: New value for the option (bool, int, or str only)

        Returns:
            True if option updated successfully
        """
        # Map of valid keys to their expected types
        valid_options: dict[str, type] = {
            "mirror": bool,
            "archive": bool,
            "hostname_subdir": bool,
            "date_subdir": bool,
            "archive_format": str,
            "archive_compression_level": int,
            "rotate_archives": bool,
            "max_archives": int,
            "pre_restore_backup": bool,
            "max_restore_backups": int,
        }

        # Validate key exists
        if key not in valid_options:
            return False

        # Validate type matches expected type
        if not isinstance(value, valid_options[key]):
            return False

        # Type is already narrowed by function signature (bool | int | str)
        return self.model.update_option(key, value)

    def command_update_path(self, path_type: str, value: str) -> bool:
        """
        Command to update mirror_dir, archive_dir, or restore_backup_dir path.

        Args:
            path_type: One of "mirror_dir", "archive_dir", or "restore_backup_dir"
            value: New path value

        Returns:
            True if path updated successfully
        """
        return self.model.update_path(path_type, value)

    def command_start_backup(self, force_full_backup: bool = False) -> bool:
        """
        Command to start backup operation.

        Args:
            force_full_backup: If True, disable skip_identical optimization to copy all files

        Returns:
            True if backup started successfully
        """
        # Validate configuration loaded
        if self.model.get_dotfile_count() == 0:
            self.error_occurred.emit("Backup", "No configuration loaded")
            return False

        # Create and configure worker
        self.backup_worker = BackupWorker()
        self.backup_worker.set_model(self.model)
        self.backup_worker.set_modes(
            self.model.options["mirror"], self.model.options["archive"]
        )
        self.backup_worker.set_force_full_backup(force_full_backup)

        # Connect worker signals
        self.backup_worker.progress_updated.connect(self._on_worker_progress)
        self.backup_worker.item_processed.connect(self._on_item_processed)
        self.backup_worker.item_skipped.connect(self._on_item_skipped)
        self.backup_worker.backup_finished.connect(self._on_backup_finished)
        self.backup_worker.error_occurred.connect(self._on_worker_error)

        # Start worker thread
        self.backup_worker.start()
        return True

    def command_start_restore(self) -> bool:
        """
        Command to start restore operation.

        Returns:
            True if restore started successfully
        """
        # Validate source directory set
        if not self.restore_source_directory:
            self.error_occurred.emit("Restore", "No source directory set")
            return False

        # Create and configure worker
        self.restore_worker = RestoreWorker()
        self.restore_worker.set_model(self.model)
        self.restore_worker.set_source_directory(self.restore_source_directory)

        # Connect worker signals
        self.restore_worker.progress_updated.connect(self._on_worker_progress)
        self.restore_worker.item_processed.connect(self._on_item_processed)
        self.restore_worker.restore_finished.connect(self._on_restore_finished)
        self.restore_worker.error_occurred.connect(self._on_worker_error)

        # Start worker thread
        self.restore_worker.start()
        return True

    def command_set_restore_source(self, directory: Path) -> bool:
        """
        Command to set restore source directory.

        Args:
            directory: Source directory path

        Returns:
            True if valid directory
        """
        if directory.exists() and directory.is_dir():
            self.restore_source_directory = directory
            return True
        return False

    def command_add_dotfile(
        self,
        category: str,
        application: str,
        description: str,
        paths: list[str],
        enabled: bool = True,
    ) -> bool:
        """
        Command to add a new dotfile entry.

        Args:
            category: Category for the dotfile
            application: Application name
            description: Description of the dotfile
            paths: List of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was added successfully
        """
        success = self.model.add_dotfile(
            category, application, description, paths, enabled
        )

        if success:
            # Emit signal to update UI
            dotfile_count = self.model.get_dotfile_count()
            self.dotfiles_updated.emit(dotfile_count)

        return success

    def command_update_dotfile(
        self,
        index: int,
        category: str,
        application: str,
        description: str,
        paths: list[str],
        enabled: bool = True,
    ) -> bool:
        """
        Command to update an existing dotfile entry.

        Args:
            index: Index of dotfile to update
            category: Updated category
            application: Updated application name
            description: Updated description
            paths: List of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was updated successfully
        """
        success = self.model.update_dotfile(
            index, category, application, description, paths, enabled
        )

        if success:
            # Emit signal to update UI
            dotfile_count = self.model.get_dotfile_count()
            self.dotfiles_updated.emit(dotfile_count)

        return success

    def command_remove_dotfile(self, index: int) -> bool:
        """
        Command to remove a dotfile entry by index.

        Args:
            index: Index of dotfile to remove

        Returns:
            True if dotfile was removed successfully
        """
        success = self.model.remove_dotfile(index)

        if success:
            # Emit signal to update UI
            dotfile_count = self.model.get_dotfile_count()
            self.dotfiles_updated.emit(dotfile_count)

        return success

    def command_toggle_dotfile_enabled(self, index: int) -> bool:
        """
        Command to toggle the enabled status of a dotfile entry.

        Args:
            index: Index of dotfile to toggle

        Returns:
            New enabled status
        """
        # Note: Don't emit dotfiles_updated here - the list hasn't changed,
        # only the enabled status of one entry. The View will update locally.

        return self.model.toggle_dotfile_enabled(index)

    def command_toggle_exclusion(self, application: str) -> None:
        """Toggle exclusion status for a dotfile.

        Args:
            application: Application name to toggle
        """
        self.model.get_config_manager().toggle_exclusion(application)
        self.exclusions_changed.emit()

    def get_exclusions(self) -> list[str]:
        """Get current exclusion list.

        Returns:
            List of excluded application names
        """
        return self.model.get_config_manager().get_exclusions()

    def is_excluded(self, application: str) -> bool:
        """Check if application is excluded.

        Args:
            application: Application name

        Returns:
            True if excluded
        """
        return self.model.get_config_manager().is_excluded(application)

    def get_dotfile_count(self) -> int:
        """
        Get number of configured dotfiles.

        Returns:
            Dotfile count
        """
        return self.model.get_dotfile_count()

    def get_dotfile_list(self) -> list[DotFileDict]:
        """
        Get list of dotfile metadata.

        Returns:
            List of dotfile dictionaries
        """
        return self.model.dotfiles.copy()

    def get_dotfile_validation(self) -> dict[int, tuple[bool, bool, str]]:
        """
        Get validation status for all dotfiles.

        Returns:
            Dict mapping index to (exists, is_dir, type_str) tuple
        """
        return self.model.validate_dotfile_paths()

    def get_dotfile_sizes(self) -> dict[int, int]:
        """
        Get sizes for all dotfiles in bytes.

        Returns:
            Dict mapping index to size in bytes
        """
        return self.model.get_dotfile_sizes()

    def get_unique_categories(self) -> list[str]:
        """
        Get sorted list of unique categories from all dotfiles.

        Returns:
            Sorted list of unique category names
        """
        categories: set[str] = set()
        for dotfile in self.model.dotfiles:
            if dotfile.get("category"):
                categories.add(dotfile["category"])
        return sorted(categories)

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        Format size in bytes to human-readable string with appropriate units.

        Args:
            size_bytes: Size in bytes to format

        Returns:
            Formatted size string (e.g., "0 B", "1.5 KB", "2.3 MB", "5.7 GB")
        """
        if size_bytes == 0:
            return "0 B"

        # Define size units
        units = ["B", "KB", "MB", "GB", "TB"]
        unit_index = 0
        size = float(size_bytes)

        # Convert to appropriate unit
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1

        # Format with appropriate precision
        if unit_index == 0:  # Bytes
            return f"{int(size)} {units[unit_index]}"
        return f"{size:.1f} {units[unit_index]}"

    def get_statistics_summary(self) -> str:
        """
        Get formatted statistics summary.

        Returns:
            Formatted statistics string with enhanced clarity
        """
        stats = self.model.statistics

        # Build message using list and join for better performance
        message_parts = [
            "Backup Operation Completed!\n",
            "=" * 50,
        ]

        # Calculate total items
        total_items = stats.processed_items + stats.skipped_items + stats.failed_items

        # Summary line with totals
        message_parts.append(
            f"\n📊 Summary: {stats.processed_items} copied, "
            f"{stats.skipped_items} skipped, "
            f"{stats.failed_items} failed (Total: {total_items})"
        )

        # Detailed breakdown with clear explanations
        message_parts.append("\n📋 Details:")

        # Files copied
        if stats.processed_items > 0:
            message_parts.append(
                f"  ✓ Files copied: {stats.processed_items} "
                f"(new or modified files backed up)"
            )
        else:
            message_parts.append("  ✓ Files copied: 0 (all files already up to date)")

        # Files skipped
        if stats.skipped_items > 0:
            message_parts.append(
                f"  ⊘ Files skipped: {stats.skipped_items} "
                f"(unchanged since last backup)"
            )

        # Files failed
        if stats.failed_items > 0:
            message_parts.append(
                f"  ✗ Files failed: {stats.failed_items} (check log for details)"
            )

        # Timing information
        message_parts.append(f"\n⏱️  Total time: {stats.total_time:.2f} seconds")

        # Add detailed timing statistics if available
        if stats.processing_times and stats.processed_items > 0:
            message_parts.extend(
                [
                    "\n📈 Performance:",
                    f"  Average: {stats.average_time:.4f} seconds per file",
                    f"  Fastest: {stats.min_time:.4f} seconds",
                    f"  Slowest: {stats.max_time:.4f} seconds",
                ]
            )

        return "\n".join(message_parts)

    def get_options(self) -> OptionsDict:
        """
        Get backup operation options.

        Returns:
            Options dictionary with proper typing
        """
        # Return copy to prevent external modification (TypedDict is dict-like, not a class)
        return dict(self.model.options)  # type: ignore[return-value]

    def set_mirror_mode(self, enabled: bool) -> None:
        """
        Set mirror backup mode.

        Args:
            enabled: Whether mirror backup is enabled
        """
        self.model.options["mirror"] = enabled

    def set_archive_mode(self, enabled: bool) -> None:
        """
        Set archive backup mode.

        Args:
            enabled: Whether archive backup is enabled
        """
        self.model.options["archive"] = enabled

    def load_settings(self) -> dict[str, Any]:
        """
        Load persisted settings from QSettings with validation.

        Returns:
            Dictionary of loaded settings (safe/validated values only)
        """
        restore_source_str: str = str(self.settings.value("restoreSource", ""))

        settings_dict: dict[str, Any] = {
            "restore_source": restore_source_str,
            "geometry": self.settings.value("geometry"),
            "window_state": self.settings.value("windowState"),
        }

        # Validate and apply restore source if exists
        if restore_source_str:
            validation_result = InputValidator.validate_path(
                restore_source_str, must_exist=True
            )
            if validation_result.success:
                restore_path = Path(restore_source_str)
                if restore_path.exists():
                    self.restore_source_directory = restore_path
            # Silently ignore invalid paths

        return settings_dict

    def save_settings(self, geometry: Any = None, window_state: Any = None) -> None:
        """
        Save current settings to QSettings.

        Args:
            geometry: Window geometry to save
            window_state: Window state to save
        """
        if geometry:
            self.settings.setValue("geometry", geometry)
        if window_state:
            self.settings.setValue("windowState", window_state)

        if self.restore_source_directory:
            self.settings.setValue("restoreSource", str(self.restore_source_directory))

    def _on_worker_progress(self, value: int) -> None:
        """
        Handle worker progress updates.

        Args:
            value: Progress percentage
        """
        self.progress_updated.emit(value)

    def _on_item_processed(self, source: str, destination: str) -> None:
        """
        Handle worker item completion.

        Args:
            source: Source path
            destination: Destination path
        """
        self.item_processed.emit(source, destination)

    def _on_item_skipped(self, path: str, reason: str) -> None:
        """
        Handle worker item skipped.

        Args:
            path: Path that was skipped
            reason: Reason for skipping
        """
        self.item_skipped.emit(path, reason)

    def _on_backup_finished(self) -> None:
        """Handle backup completion and cleanup worker."""
        summary = self.get_statistics_summary()
        self.operation_finished.emit(summary)

        # Disconnect signals and cleanup worker to prevent memory leaks
        if self.backup_worker:
            self.backup_worker.progress_updated.disconnect(self._on_worker_progress)
            self.backup_worker.item_processed.disconnect(self._on_item_processed)
            self.backup_worker.item_skipped.disconnect(self._on_item_skipped)
            self.backup_worker.backup_finished.disconnect(self._on_backup_finished)
            self.backup_worker.error_occurred.disconnect(self._on_worker_error)
            # Properly cleanup Qt object to free resources
            self.backup_worker.deleteLater()
            self.backup_worker = None

    def _on_restore_finished(self) -> None:
        """Handle restore completion and cleanup worker."""
        summary = self.get_statistics_summary()
        self.operation_finished.emit(summary)

        # Disconnect signals and cleanup worker to prevent memory leaks
        if self.restore_worker:
            self.restore_worker.progress_updated.disconnect(self._on_worker_progress)
            self.restore_worker.item_processed.disconnect(self._on_item_processed)
            self.restore_worker.restore_finished.disconnect(self._on_restore_finished)
            self.restore_worker.error_occurred.disconnect(self._on_worker_error)
            # Properly cleanup Qt object to free resources
            self.restore_worker.deleteLater()
            self.restore_worker = None

    def _on_worker_error(self, context: str, error_message: str) -> None:
        """
        Handle worker errors.

        Args:
            context: Error context
            error_message: Error message
        """
        self.error_occurred.emit(context, error_message)

    def _on_config_progress(self, value: int) -> None:
        """
        Handle config worker progress updates.

        Args:
            value: Progress percentage
        """
        self.progress_updated.emit(value)

    def _on_config_load_finished(
        self, success: bool, error_message: str, dotfile_count: int
    ) -> None:
        """
        Handle config load completion and cleanup worker.

        Args:
            success: Whether load was successful
            error_message: Error message if failed
            dotfile_count: Number of dotfiles loaded
        """
        if success:
            self.config_loaded.emit(dotfile_count)
            self.dotfiles_updated.emit(dotfile_count)
        else:
            # Emit specific error message from model
            self.error_occurred.emit("Configuration", error_message)

        # Disconnect signals and cleanup worker
        if self.config_load_worker:
            self.config_load_worker.progress_updated.disconnect(
                self._on_config_progress
            )
            self.config_load_worker.load_finished.disconnect(
                self._on_config_load_finished
            )
            self.config_load_worker.error_occurred.disconnect(self._on_worker_error)
            self.config_load_worker.deleteLater()
            self.config_load_worker = None

    def _on_config_save_finished(self, success: bool, error_message: str) -> None:
        """
        Handle config save completion and cleanup worker.

        Args:
            success: Whether save was successful
            error_message: Error message if failed
        """
        if not success:
            self.error_occurred.emit("Configuration Save", error_message)

        # Disconnect signals and cleanup worker
        if self.config_save_worker:
            self.config_save_worker.progress_updated.disconnect(
                self._on_config_progress
            )
            self.config_save_worker.save_finished.disconnect(
                self._on_config_save_finished
            )
            self.config_save_worker.error_occurred.disconnect(self._on_worker_error)
            self.config_save_worker.deleteLater()
            self.config_save_worker = None
