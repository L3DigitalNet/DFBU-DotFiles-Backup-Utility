"""
DFBU ConfigManager - Configuration Management Component

Description:
    Handles all configuration-related operations for DFBU GUI including loading,
    saving, validation, and manipulation of configuration data. Part of the
    refactored MVVM architecture following Single Responsibility Principle.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 02-01-2026
License: MIT

Features:
    - YAML configuration file loading and saving via YAMLConfigLoader
    - Automatic rotating backups on save (up to 10 backups)
    - Dotfile entry management (add/update/remove/toggle)
    - Exclusion management (session-based exclusions)
    - Options and path updates
    - Clean separation from file I/O and business logic

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - Standard library: pathlib, sys
    - External: ruamel.yaml (via YAMLConfigLoader)
    - Local: YAMLConfigLoader, common_types

Classes:
    - ConfigManager: Manages all configuration operations

Functions:
    create_rotating_backup: Create timestamped backup with rotation
"""

import shutil
import sys
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Local imports - import from parent DFBU directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import DotFileDict, LegacyDotFileDict, OptionsDict
from core.yaml_config import YAMLConfigLoader

from gui.input_validation import InputValidator
from gui.restore_backup_manager import DEFAULT_BACKUP_DIR


# =============================================================================
# Utility Functions (needed by ConfigManager)
# =============================================================================


def create_rotating_backup(
    source_path: Path,
    backup_dir: Path | None = None,
    max_backups: int = 10,
    timestamp_format: str = "%Y%m%d_%H%M%S",
) -> Path | None:
    """
    Create a timestamped backup of a file and rotate old backups.

    NOTE: This is a simplified inline version for config backups only.
    Full implementation exists in model.py for broader use.

    Args:
        source_path: Path to file to backup
        backup_dir: Directory for backup storage
        max_backups: Maximum number of backups to retain
        timestamp_format: strftime format for timestamp

    Returns:
        Path to created backup file, or None if operation failed
    """
    if not source_path.exists() or not source_path.is_file():
        return None

    if backup_dir is None:
        backup_dir = source_path.parent / f".{source_path.name}.backups"

    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
    except (OSError, PermissionError):
        return None

    timestamp = datetime.now(UTC).strftime(timestamp_format)
    backup_name = f"{source_path.stem}.{timestamp}{source_path.suffix}"
    backup_path = backup_dir / backup_name

    # Handle filename collisions
    counter = 1
    while backup_path.exists():
        backup_name = f"{source_path.stem}.{timestamp}_{counter}{source_path.suffix}"
        backup_path = backup_dir / backup_name
        counter += 1

    try:
        # Use shutil for reliable file copying
        shutil.copy2(source_path, backup_path)

        # Rotate old backups
        backup_files = sorted(
            backup_dir.glob(f"{source_path.stem}.*{source_path.suffix}"),
            key=lambda p: p.stat().st_mtime,
        )

        while len(backup_files) > max_backups:
            oldest = backup_files.pop(0)
            oldest.unlink()

        return backup_path

    except (OSError, PermissionError):
        return None


# =============================================================================
# ConfigManager Class
# =============================================================================


class ConfigManager:
    """
    Manages configuration file operations and dotfile entries.

    Handles loading, saving, validating, and manipulating YAML configuration
    data. Provides clean separation between configuration management and other
    concerns like file operations and backup orchestration.

    YAML Configuration Structure:
    - settings.yaml: Paths and options
    - dotfiles.yaml: Dotfile library (application name -> definition)
    - session.yaml: Session-specific exclusions

    Attributes:
        config_path: Path to configuration directory
        options: Current options configuration
        dotfiles: Dictionary of dotfiles (application name -> definition)
        exclusions: List of excluded application names
        mirror_base_dir: Base directory for mirror backups
        archive_base_dir: Base directory for archive backups

    Public methods:
        load_config: Load and validate YAML configuration
        save_config: Save configuration with automatic backups
        add_dotfile: Add new dotfile entry
        update_dotfile: Update existing dotfile entry
        remove_dotfile: Remove dotfile entry by index
        toggle_dotfile_enabled: Toggle enabled status
        update_option: Update single configuration option
        update_path: Update mirror_dir or archive_dir path
        get_dotfile_count: Get number of dotfiles
        get_dotfile_by_index: Get dotfile by index
        get_dotfile_list: Get all dotfiles as list with application name
        get_exclusions: Get list of excluded application names
        set_exclusions: Set and persist exclusions
        is_excluded: Check if specific dotfile is excluded
        toggle_exclusion: Toggle exclusion state for application
        get_included_dotfiles: Get only non-excluded dotfiles

    Private methods:
        _get_default_options: Get default options configuration
        _path_to_tilde_notation: Convert path to tilde notation
        _normalize_paths: Normalize dotfile paths to list format
    """

    def __init__(
        self, config_path: Path, expand_path_callback: Callable[[str], Path]
    ) -> None:
        """
        Initialize ConfigManager.

        Args:
            config_path: Path to configuration directory (for YAML files)
            expand_path_callback: Callback function to expand paths (from FileOperations)
        """
        self.config_path: Path = config_path
        self.expand_path: Callable[[str], Path] = expand_path_callback
        self.options: OptionsDict = self._get_default_options()
        # Store dotfiles as dict: application name -> definition
        self._dotfiles: dict[str, DotFileDict] = {}
        # Session-specific exclusions
        self._exclusions: list[str] = []

        # Base directories (set from settings after config load)
        self.mirror_base_dir: Path = Path.home() / "DFBU_Mirror"
        self.archive_base_dir: Path = Path.home() / "DFBU_Archives"
        # Pre-restore backup directory (v0.6.0)
        self.restore_backup_dir: Path = DEFAULT_BACKUP_DIR

        # YAML loader instance
        self._yaml_loader: YAMLConfigLoader | None = None

    def load_config(self) -> tuple[bool, str]:
        """
        Load and validate YAML configuration files.

        Loads settings, dotfiles, and session from separate YAML files.
        Automatically detects and corrects corrupted config entries where paths
        are not in tilde notation or have incorrect structure.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        try:
            # Initialize YAML loader
            self._yaml_loader = YAMLConfigLoader(self.config_path)

            # Load settings (paths and options)
            settings = self._yaml_loader.load_settings()
            self.options = settings["options"]
            paths = settings["paths"]

            # Set base directories from settings
            self.mirror_base_dir = self.expand_path(paths["mirror_dir"])
            self.archive_base_dir = self.expand_path(paths["archive_dir"])
            self.restore_backup_dir = self.expand_path(paths["restore_backup_dir"])

            # Load dotfiles library
            self._dotfiles = self._yaml_loader.load_dotfiles()

            # Load session exclusions
            session = self._yaml_loader.load_session()
            self._exclusions = session["excluded"]

            # Check for and fix any corrupted or non-portable path entries
            corruptions_fixed = self._validate_and_fix_paths()

            # If corruptions were found and fixed, auto-save the corrected config
            if corruptions_fixed > 0:
                save_success, save_error = self.save_config()
                if save_success:
                    return (
                        True,
                        f"Config loaded (auto-corrected {corruptions_fixed} path entries)",
                    )
                # If save fails, still return success for loading but mention the issue
                return (
                    True,
                    f"Config loaded (found {corruptions_fixed} issues but auto-save failed: {save_error})",
                )

            return True, ""

        except FileNotFoundError as e:
            return False, f"Configuration file not found: {e}"
        except ValueError as e:
            return False, f"Invalid configuration format: {e}"
        except KeyError as e:
            return False, f"Missing required configuration key: {e}"
        except Exception as e:
            return False, f"Unexpected error loading config: {e!s}"

    def _validate_and_fix_paths(self) -> int:
        """
        Validate and fix path entries in dotfiles configuration using parallel processing.

        Checks for and corrects:
        1. Absolute paths that should use tilde notation (~/...)
        2. Paths not using portable format

        Uses ThreadPoolExecutor for efficient parallel processing of multiple dotfiles.

        Returns:
            Number of path entries that were corrected
        """
        corrections_made = 0

        # Process dotfiles in parallel for better performance
        # Use ThreadPoolExecutor with max_workers=4 for optimal I/O-bound operations
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all dotfiles for processing
            future_to_app = {
                executor.submit(self._process_dotfile_paths, app_name, dotfile): app_name
                for app_name, dotfile in self._dotfiles.items()
            }

            # Collect results as they complete
            for future in as_completed(future_to_app):
                app_name = future_to_app[future]
                try:
                    corrected_paths, path_corrections = future.result()
                    if path_corrections > 0:
                        # Update dotfile with corrected paths
                        self._dotfiles[app_name]["paths"] = corrected_paths
                        corrections_made += path_corrections
                except Exception:
                    # Log error but continue processing other dotfiles
                    # Errors in individual dotfiles shouldn't stop the entire process
                    pass

        return corrections_made

    def _process_dotfile_paths(
        self, app_name: str, dotfile: DotFileDict
    ) -> tuple[list[str], int]:
        """
        Process a single dotfile's paths for validation and correction.

        This method is designed to be called in parallel from _validate_and_fix_paths.

        Args:
            app_name: Application name (for error reporting)
            dotfile: Dotfile dictionary to process

        Returns:
            Tuple of (corrected_paths_list, number_of_corrections)
        """
        paths_list = self._normalize_paths(dotfile)
        corrected_paths: list[str] = []
        corrections = 0

        for path_str in paths_list:
            # Skip empty paths
            if not path_str:
                corrected_paths.append(path_str)
                continue

            # Expand the path to check if it's under home directory
            expanded_path = self.expand_path(path_str)

            # Convert to portable tilde notation if under home directory
            portable_path = self._path_to_tilde_notation(expanded_path)

            # Check if conversion changed the path
            if portable_path != path_str:
                corrected_paths.append(portable_path)
                corrections += 1
            else:
                corrected_paths.append(path_str)

        return corrected_paths, corrections

    def _normalize_paths(self, dotfile: DotFileDict) -> list[str]:
        """
        Normalize dotfile paths to list format.

        Handles both 'path' (single string) and 'paths' (list) formats.

        Args:
            dotfile: Dotfile dictionary

        Returns:
            List of path strings
        """
        if "paths" in dotfile:
            return dotfile["paths"]
        if "path" in dotfile:
            return [dotfile["path"]]
        return []

    def save_config(self) -> tuple[bool, str]:
        """
        Save current configuration back to YAML files with automatic rotating backups.

        Creates a timestamped backup of the config files before saving, maintaining
        up to 10 backup copies with automatic rotation of oldest backups.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        try:
            if self._yaml_loader is None:
                self._yaml_loader = YAMLConfigLoader(self.config_path)

            # Create rotating backup before saving (if settings file exists)
            settings_path = self._yaml_loader.settings_path
            if settings_path.exists():
                backup_dir = settings_path.parent / f".{settings_path.name}.backups"
                _backup_path = create_rotating_backup(
                    source_path=settings_path,
                    backup_dir=backup_dir,
                    max_backups=10,
                    timestamp_format="%Y%m%d_%H%M%S",
                )
                # Continue with save even if backup fails

            # Build settings dictionary
            settings = {
                "paths": {
                    "mirror_dir": self._path_to_tilde_notation(self.mirror_base_dir),
                    "archive_dir": self._path_to_tilde_notation(self.archive_base_dir),
                    "restore_backup_dir": self._path_to_tilde_notation(
                        self.restore_backup_dir
                    ),
                },
                "options": dict(self.options),
            }

            # Save settings
            self._yaml_loader.save_settings(settings)

            # Save dotfiles (already in dict format)
            self._yaml_loader.save_dotfiles(self._dotfiles)

            # Save session (exclusions)
            self._yaml_loader.save_session({"excluded": self._exclusions})

            return True, ""

        except (OSError, PermissionError) as e:
            return False, f"Failed to write configuration file: {e!s}"
        except Exception as e:
            return False, f"Unexpected error saving config: {e!s}"

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
            category: Category for the dotfile (stored in tags)
            application: Application name (becomes the key)
            description: Description of the dotfile
            paths: List of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was added successfully
        """
        # Create new dotfile entry in YAML format
        new_dotfile: DotFileDict = {
            "description": description,
            "paths": paths,
            "tags": category,  # Use tags field for category
        }

        # Add to dotfiles dict using application name as key
        self._dotfiles[application] = new_dotfile

        # Handle enabled state via exclusions
        if not enabled:
            # Add to exclusions if disabled
            if application not in self._exclusions:
                self._exclusions.append(application)

        return True

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
            index: Index of dotfile to update (in the list order)
            category: Updated category (stored in tags)
            application: Updated application name
            description: Updated description
            paths: Updated list of file or directory paths
            enabled: Whether the dotfile is enabled for backup (default True)

        Returns:
            True if dotfile was updated successfully
        """
        # Get application name by index
        app_names = list(self._dotfiles.keys())
        if 0 <= index < len(app_names):
            old_app_name = app_names[index]

            # If application name changed, update exclusions list
            if old_app_name != application:
                # Remove old app name from exclusions if present
                if old_app_name in self._exclusions:
                    self._exclusions.remove(old_app_name)
                del self._dotfiles[old_app_name]

            # Create updated entry
            self._dotfiles[application] = {
                "description": description,
                "paths": paths,
                "tags": category,
            }

            # Handle enabled state via exclusions
            if enabled:
                # Remove from exclusions if present
                if application in self._exclusions:
                    self._exclusions.remove(application)
            else:
                # Add to exclusions if not present
                if application not in self._exclusions:
                    self._exclusions.append(application)

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
        app_names = list(self._dotfiles.keys())
        if 0 <= index < len(app_names):
            app_name = app_names[index]
            del self._dotfiles[app_name]
            return True
        return False

    def toggle_dotfile_enabled(self, index: int) -> bool:
        """
        Toggle the enabled status of a dotfile entry.

        In YAML format, enabled/disabled is handled via exclusions.
        This method toggles exclusion status.

        Args:
            index: Index of dotfile to toggle

        Returns:
            New enabled status if successful, False otherwise
        """
        app_names = list(self._dotfiles.keys())
        if 0 <= index < len(app_names):
            app_name = app_names[index]
            self.toggle_exclusion(app_name)
            return not self.is_excluded(app_name)
        return False

    def update_option(self, key: str, value: bool | int | str) -> bool:
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
            elif key == "pre_restore_backup":
                self.options["pre_restore_backup"] = bool(value)
            elif key == "max_restore_backups":
                self.options["max_restore_backups"] = int(value)
            return True
        return False

    def update_path(self, path_type: str, value: str) -> bool:
        """
        Update mirror_dir, archive_dir, or restore_backup_dir path with validation.

        Args:
            path_type: One of "mirror_dir", "archive_dir", or "restore_backup_dir"
            value: New path value

        Returns:
            True if path was updated successfully
        """
        # Validate path before applying
        validation_result = InputValidator.validate_path(value, must_exist=False)
        if not validation_result.success:
            return False

        expanded_path = self.expand_path(value)

        if path_type == "mirror_dir":
            self.mirror_base_dir = expanded_path
            return True
        if path_type == "archive_dir":
            self.archive_base_dir = expanded_path
            return True
        if path_type == "restore_backup_dir":
            self.restore_backup_dir = expanded_path
            return True

        return False

    def get_dotfile_count(self) -> int:
        """
        Get number of dotfile entries.

        Returns:
            Count of dotfiles
        """
        return len(self._dotfiles)

    def get_dotfile_by_index(self, index: int) -> LegacyDotFileDict | None:
        """
        Get dotfile entry by index.

        Args:
            index: Index of dotfile to retrieve

        Returns:
            Dotfile dictionary with application name or None if index invalid
        """
        app_names = list(self._dotfiles.keys())
        if 0 <= index < len(app_names):
            app_name = app_names[index]
            return self._to_legacy_format(app_name, self._dotfiles[app_name])
        return None

    def get_dotfile_list(self) -> list[LegacyDotFileDict]:
        """
        Get complete list of dotfile entries with application name included.

        Converts internal dict format to list format for backward compatibility
        with View layer. Each dict includes "application" key.

        Returns:
            List of all dotfiles with application names
        """
        result: list[LegacyDotFileDict] = []
        for app_name, dotfile in self._dotfiles.items():
            result.append(self._to_legacy_format(app_name, dotfile))
        return result

    def _to_legacy_format(self, app_name: str, dotfile: DotFileDict) -> LegacyDotFileDict:
        """
        Convert YAML dotfile format to legacy format for View compatibility.

        Args:
            app_name: Application name
            dotfile: YAML format dotfile dict

        Returns:
            Legacy format dotfile dict with all fields
        """
        paths = self._normalize_paths(dotfile)
        tags = dotfile.get("tags", "")
        # Use tags as category, or "General" if no tags
        category = tags.split(",")[0].strip() if tags else "General"

        return {
            "category": category,
            "application": app_name,
            "description": dotfile.get("description", ""),
            "paths": paths,
            "mirror_dir": self._path_to_tilde_notation(self.mirror_base_dir),
            "archive_dir": self._path_to_tilde_notation(self.archive_base_dir),
            "enabled": not self.is_excluded(app_name),
        }

    # =========================================================================
    # Exclusion Management Methods
    # =========================================================================

    def get_exclusions(self) -> list[str]:
        """
        Get list of excluded application names.

        Returns:
            List of excluded application names
        """
        return self._exclusions.copy()

    def set_exclusions(self, exclusions: list[str]) -> None:
        """
        Set and persist exclusions to session file.

        Args:
            exclusions: List of application names to exclude
        """
        self._exclusions = exclusions.copy()

        # Persist to session file
        if self._yaml_loader is None:
            self._yaml_loader = YAMLConfigLoader(self.config_path)
        self._yaml_loader.save_session({"excluded": self._exclusions})

    def is_excluded(self, application: str) -> bool:
        """
        Check if specific dotfile is excluded.

        Args:
            application: Application name to check

        Returns:
            True if application is excluded, False otherwise
        """
        return application in self._exclusions

    def toggle_exclusion(self, application: str) -> None:
        """
        Toggle exclusion state for application.

        If application is excluded, removes from exclusions.
        If not excluded, adds to exclusions.
        Changes are persisted to session file.

        Args:
            application: Application name to toggle
        """
        if application in self._exclusions:
            self._exclusions.remove(application)
        else:
            self._exclusions.append(application)

        # Persist to session file
        if self._yaml_loader is None:
            self._yaml_loader = YAMLConfigLoader(self.config_path)
        self._yaml_loader.save_session({"excluded": self._exclusions})

    def get_included_dotfiles(self) -> list[LegacyDotFileDict]:
        """
        Get only non-excluded dotfiles.

        Returns:
            List of dotfiles that are not in the exclusion list
        """
        result: list[LegacyDotFileDict] = []
        for app_name, dotfile in self._dotfiles.items():
            if not self.is_excluded(app_name):
                result.append(self._to_legacy_format(app_name, dotfile))
        return result

    # =========================================================================
    # Private Helper Methods
    # =========================================================================

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
            "pre_restore_backup": True,
            "max_restore_backups": 5,
        }

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

    # =========================================================================
    # Backward Compatibility Properties
    # =========================================================================

    @property
    def dotfiles(self) -> list[LegacyDotFileDict]:
        """
        Property for backward compatibility with code expecting list format.

        Returns:
            List of dotfiles in legacy format
        """
        return self.get_dotfile_list()
