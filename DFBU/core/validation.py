#!/usr/bin/env python3
"""
DFBU Configuration Validation Module

Description:
    Shared validation logic for TOML configuration files used by both CLI
    and GUI applications. Provides robust validation with type checking,
    default values, and format conversion for backward compatibility.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 11-01-2025
License: MIT

Features:
    - TypedDict-based validation for type safety
    - Backward compatibility for legacy path format (path → paths)
    - Range validation for numeric values
    - Default values for missing configuration
    - Used by GUI (gui/model.py) and core modules

Requirements:
    - Python 3.14+ for latest language features
    - common_types module for TypedDict definitions

Classes:
    - ConfigValidator: Static methods for validating TOML configuration

Functions:
    - validate_config(): Validate complete configuration structure
    - validate_options(): Validate options with type checking and defaults
    - validate_dotfile(): Validate individual dotfile entry
"""

from typing import Any

from core.common_types import DotFileDict, OptionsDict


class ConfigValidator:
    """
    Validates TOML configuration structure and content.

    Provides robust validation of configuration before use to ensure all
    required fields are present with proper types and valid values. Returns
    TypedDict instances for type safety.

    Static methods:
        validate_config: Validate complete configuration structure and return typed dicts
        validate_options: Validate options dictionary with type checking and defaults
        validate_dotfile: Validate individual dotfile entry with required field checking
    """

    @staticmethod
    def validate_config(
        config_data: dict[str, Any],
    ) -> tuple[OptionsDict, list[DotFileDict]]:
        """
        Validate complete configuration structure.

        Args:
            config_data: Raw configuration data from TOML file

        Returns:
            Tuple of validated options dict and list of dotfile dicts
        """
        # Extract configuration sections with defaults for missing sections
        raw_paths: dict[str, str] = config_data.get("paths", {})
        raw_options: dict[str, Any] = config_data.get("options", {})
        raw_dotfiles: list[dict[str, str]] = config_data.get("dotfile", [])

        # Validate options configuration
        validated_options: OptionsDict = ConfigValidator.validate_options(raw_options)

        # Validate and merge each dotfile entry with path configuration
        validated_dotfiles: list[DotFileDict] = []
        for dotfile in raw_dotfiles:
            merged_dotfile: dict[str, str] = {**raw_paths, **dotfile}
            validated_dotfiles.append(ConfigValidator.validate_dotfile(merged_dotfile))

        return validated_options, validated_dotfiles

    @staticmethod
    def validate_options(raw_options: dict[str, Any]) -> OptionsDict:
        """
        Validate options dictionary with type checking and defaults.

        Args:
            raw_options: Raw options from configuration

        Returns:
            Validated options dictionary with proper types
        """
        # Extract compression level with range validation and type checking
        compression_level: int = 9  # Default value
        try:
            raw_compression = raw_options.get("archive_compression_level", 9)
            compression_level = int(raw_compression)
            # Validate range [0, 9] - if outside range, use default
            if not 0 <= compression_level <= 9:
                compression_level = 9
        except (TypeError, ValueError):
            compression_level = 9

        # Extract max archives with minimum value validation and type checking
        max_archives: int = 5  # Default value
        try:
            raw_max_archives = raw_options.get("max_archives", 5)
            max_archives = int(raw_max_archives)
            # Validate minimum value - if below 1, use default
            if max_archives < 1:
                max_archives = 5
        except (TypeError, ValueError):
            max_archives = 5

        # Build validated options dictionary with proper types
        validated: OptionsDict = {
            "mirror": bool(raw_options.get("mirror", True)),
            "archive": bool(raw_options.get("archive", False)),
            "hostname_subdir": bool(raw_options.get("hostname_subdir", True)),
            "date_subdir": bool(raw_options.get("date_subdir", False)),
            "archive_format": str(raw_options.get("archive_format", "tar.gz")),
            "archive_compression_level": compression_level,
            "rotate_archives": bool(raw_options.get("rotate_archives", False)),
            "max_archives": max_archives,
        }

        return validated

    @staticmethod
    def validate_dotfile(raw_dotfile: dict[str, str]) -> DotFileDict:
        """
        Validate individual dotfile entry with required field checking.

        Supports both legacy single 'path' (str) and new 'paths' (list[str]) format.
        Automatically converts single path to list for internal consistency.

        Args:
            raw_dotfile: Raw dotfile metadata from TOML config

        Returns:
            Validated dotfile metadata dictionary
        """
        # Handle both legacy 'path' (str) and new 'paths' (list[str]) format
        paths: list[str] = []
        if "paths" in raw_dotfile:
            # New format: paths is already a list
            paths_value: Any = raw_dotfile.get("paths", [])
            if isinstance(paths_value, list):
                paths = [str(p) for p in paths_value]
            else:
                paths = [str(paths_value)]
        elif "path" in raw_dotfile:
            # Legacy format: convert single path to list
            # Handle case where 'path' might accidentally be a list (corrupted TOML)
            path_value = raw_dotfile.get("path", "")
            if isinstance(path_value, list):
                # 'path' was saved as list by mistake - convert to list of strings
                paths = [str(p) for p in path_value]
            elif isinstance(path_value, str):
                # Normal case: 'path' is a string
                path_str = path_value.strip()
                paths = [path_str] if path_str else [""]
            else:
                # Unknown type - convert to string
                paths = [str(path_value)]
        else:
            # No path provided
            paths = [""]

        # Build validated dictionary ensuring all required fields exist with defaults
        validated: DotFileDict = {
            "category": raw_dotfile.get("category", "Unknown"),
            "subcategory": raw_dotfile.get("subcategory", "Unknown"),
            "application": raw_dotfile.get("application", "Unknown"),
            "description": raw_dotfile.get("description", "None"),
            "paths": paths,
            "mirror_dir": raw_dotfile.get("mirror_dir", "~/DFBU_Mirror"),
            "archive_dir": raw_dotfile.get("archive_dir", "~/DFBU_Archives"),
            "enabled": True,  # Default to enabled for CLI compatibility
        }

        return validated
