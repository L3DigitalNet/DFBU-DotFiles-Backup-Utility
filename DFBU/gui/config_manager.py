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
Date Changed: 11-01-2025
License: MIT

Features:
    - TOML configuration file loading and saving
    - Automatic rotating backups on save (up to 10 backups)
    - Configuration validation using shared ConfigValidator
    - Dotfile entry management (add/update/remove/toggle)
    - Options and path updates
    - GUI-specific enabled field handling
    - Clean separation from file I/O and business logic

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - Standard library: tomllib, pathlib, sys
    - External: tomli_w for TOML writing
    - Local: validation.ConfigValidator, common_types

Classes:
    - ConfigManager: Manages all configuration operations

Functions:
    None
"""

import shutil
import sys
import tomllib
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# External dependency for TOML writing
import tomli_w


# Local imports - import from parent DFBU directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.common_types import DotFileDict, OptionsDict
from core.validation import ConfigValidator

from gui.input_validation import InputValidator


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

    Handles loading, saving, validating, and manipulating TOML configuration
    data. Provides clean separation between configuration management and other
    concerns like file operations and backup orchestration.

    Attributes:
        config_path: Path to TOML configuration file
        options: Current options configuration
        dotfiles: List of dotfile entries
        mirror_base_dir: Base directory for mirror backups
        archive_base_dir: Base directory for archive backups

    Public methods:
        load_config: Load and validate TOML configuration
        save_config: Save configuration with automatic backups
        add_dotfile: Add new dotfile entry
        update_dotfile: Update existing dotfile entry
        remove_dotfile: Remove dotfile entry by index
        toggle_dotfile_enabled: Toggle enabled status
        update_option: Update single configuration option
        update_path: Update mirror_dir or archive_dir path
        get_dotfile_count: Get number of dotfiles
        get_dotfile_by_index: Get dotfile by index
        get_dotfile_list: Get all dotfiles

    Private methods:
        _validate_config: Validate config with GUI-specific enabled handling
        _get_default_options: Get default options configuration
        _path_to_tilde_notation: Convert path to tilde notation
    """

    def __init__(
        self, config_path: Path, expand_path_callback: Callable[[str], Path]
    ) -> None:
        """
        Initialize ConfigManager.

        Args:
            config_path: Path to TOML configuration file
            expand_path_callback: Callback function to expand paths (from FileOperations)
        """
        self.config_path: Path = config_path
        self.expand_path: Callable[[str], Path] = expand_path_callback
        self.options: OptionsDict = self._get_default_options()
        self.dotfiles: list[DotFileDict] = []

        # Base directories (set from first dotfile after config load)
        self.mirror_base_dir: Path = Path.home() / "DFBU_Mirror"
        self.archive_base_dir: Path = Path.home() / "DFBU_Archives"

    def load_config(self) -> tuple[bool, str]:
        """
        Load and validate TOML configuration file.

        Automatically detects and corrects corrupted config entries where paths
        are not in tilde notation or have incorrect structure.

        Returns:
            Tuple of (success, error_message). error_message is empty on success.
        """
        try:
            # Read TOML configuration file
            with self.config_path.open("rb") as toml_file:
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

        except FileNotFoundError:
            return False, f"Configuration file not found: {self.config_path}"
        except tomllib.TOMLDecodeError as e:
            return False, f"Invalid TOML format: {e!s}"
        except KeyError as e:
            return False, f"Missing required configuration key: {e!s}"
        except Exception as e:
            return False, f"Unexpected error loading config: {e!s}"

    def _validate_and_fix_paths(self) -> int:
        """
        Validate and fix path entries in dotfiles configuration.

        Checks for and corrects:
        1. Absolute paths that should use tilde notation (~/...)
        2. Paths not using portable format

        Returns:
            Number of path entries that were corrected
        """
        corrections_made = 0

        for dotfile in self.dotfiles:
            paths_list = dotfile.get("paths", [])
            corrected_paths: list[str] = []
            paths_changed = False

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
                    paths_changed = True
                    corrections_made += 1
                else:
                    corrected_paths.append(path_str)

            # Update the dotfile's paths if any changes were made
            if paths_changed:
                dotfile["paths"] = corrected_paths

        return corrections_made

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
                _backup_path = create_rotating_backup(
                    source_path=self.config_path,
                    backup_dir=backup_dir,
                    max_backups=10,
                    timestamp_format="%Y%m%d_%H%M%S",
                )
                # Continue with save even if backup fails

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
                    "application": dotfile["application"],
                    "description": dotfile["description"],
                    "enabled": dotfile["enabled"],
                }

                # Convert paths to tilde notation for portability
                # Save as single 'path' for backward compatibility if only one path
                # Otherwise save as 'paths' list
                paths_list = dotfile["paths"]
                portable_paths = [
                    self._path_to_tilde_notation(self.expand_path(path))
                    for path in paths_list
                ]

                if len(portable_paths) == 1:
                    dotfile_entry["path"] = portable_paths[0]
                else:
                    dotfile_entry["paths"] = portable_paths

                config_data["dotfile"].append(dotfile_entry)

            # Write TOML file using tomli_w
            with self.config_path.open("wb") as toml_file:
                tomli_w.dump(config_data, toml_file)

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
            category: Category for the dotfile
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
        if 0 <= index < len(self.dotfiles):
            # Update the dotfile entry while preserving mirror_dir and archive_dir
            self.dotfiles[index]["category"] = category
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
            current_enabled: bool = bool(self.dotfiles[index]["enabled"])
            self.dotfiles[index]["enabled"] = not current_enabled
            return bool(self.dotfiles[index]["enabled"])
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
            return True
        return False

    def update_path(self, path_type: str, value: str) -> bool:
        """
        Update mirror_dir or archive_dir path with validation.

        Args:
            path_type: Either "mirror_dir" or "archive_dir"
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

        return False

    def get_dotfile_count(self) -> int:
        """
        Get number of dotfile entries.

        Returns:
            Count of dotfiles
        """
        return len(self.dotfiles)

    def get_dotfile_by_index(self, index: int) -> DotFileDict | None:
        """
        Get dotfile entry by index.

        Args:
            index: Index of dotfile to retrieve

        Returns:
            Dotfile dictionary or None if index invalid
        """
        if 0 <= index < len(self.dotfiles):
            return self.dotfiles[index]
        return None

    def get_dotfile_list(self) -> list[DotFileDict]:
        """
        Get complete list of dotfile entries.

        Returns:
            List of all dotfiles
        """
        return self.dotfiles.copy()

    def _validate_config(
        self, config_data: dict[str, Any]
    ) -> tuple[OptionsDict, list[DotFileDict]]:
        """
        Validate complete configuration structure using shared ConfigValidator.

        NOTE: GUI requires enabled field handling, so we delegate to shared
        validator then process enabled field conversion for each dotfile.

        Args:
            config_data: Raw configuration from TOML

        Returns:
            Tuple of validated options and dotfiles list
        """
        # Use shared validator for consistency
        options, dotfiles = ConfigValidator.validate_config(config_data)

        # GUI-specific: Convert enabled field strings to bool for each dotfile
        # NOTE: CLI doesn't use enabled field, so this is GUI-only behavior
        gui_dotfiles: list[DotFileDict] = []
        raw_dotfiles = config_data.get("dotfile", [])
        for validated_dotfile, raw_dotfile in zip(dotfiles, raw_dotfiles, strict=True):
            # Convert enabled field to bool with proper type handling
            enabled_value = raw_dotfile.get("enabled", "true")
            if isinstance(enabled_value, bool):
                enabled = enabled_value
            else:
                # Handle string representations from TOML
                enabled = str(enabled_value).lower() in ("true", "1", "yes")

            # Create new dict with GUI-specific enabled handling
            gui_dotfile: DotFileDict = {**validated_dotfile, "enabled": enabled}
            gui_dotfiles.append(gui_dotfile)

        return options, gui_dotfiles

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
