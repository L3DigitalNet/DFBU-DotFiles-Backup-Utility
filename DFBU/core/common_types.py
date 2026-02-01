"""
Shared Type Definitions for DFBU

Description:
    Common TypedDict definitions used across CLI and GUI modules.
    Centralizes type definitions to eliminate duplication and ensure
    consistency across the application.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 02-01-2026
License: MIT

Features:
    - Centralized TypedDict definitions for dotfile configuration
    - Shared type definitions for backup options and settings
    - Type safety across CLI and GUI modules
    - Support for YAML configuration format migration
    - Standard library only (no external dependencies)

Requirements:
    - Python 3.14+ for latest typing features

Classes:
    - PathsDict: TypedDict for backup directory paths
    - OptionsDict: TypedDict for backup options configuration
    - SettingsDict: TypedDict combining paths and options
    - DotFileDict: TypedDict for dotfile configuration (YAML format)
    - SessionDict: TypedDict for session-specific exclusions
    - LegacyDotFileDict: TypedDict for TOML migration support
"""

from typing import TypedDict


class PathsDict(TypedDict):
    """
    Type definition for backup directory paths configuration.

    Contains all directory paths used for backup operations.
    """

    mirror_dir: str
    archive_dir: str
    restore_backup_dir: str


class OptionsDict(TypedDict):
    """
    Type definition for backup options configuration dictionary.

    Contains all backup operation settings and preferences.
    """

    mirror: bool
    archive: bool
    hostname_subdir: bool
    date_subdir: bool
    archive_format: str
    archive_compression_level: int
    rotate_archives: bool
    max_archives: int
    pre_restore_backup: bool
    max_restore_backups: int


class SettingsDict(TypedDict):
    """
    Type definition for combined settings configuration.

    Contains both paths and options in a single structure,
    matching the top-level settings section in YAML config.
    """

    paths: PathsDict
    options: OptionsDict


class DotFileDict(TypedDict, total=False):
    """
    Type definition for dotfile configuration dictionary (YAML format).

    Contains metadata and path information for individual dotfile entries.
    Supports both single path (path) and multiple paths (paths) per entry.
    All fields are optional (total=False) except description.

    Fields:
        description: Human-readable description of the dotfile (required)
        path: Single path string (optional, mutually exclusive with paths)
        paths: List of path strings (optional, mutually exclusive with path)
        tags: Comma-separated tags for categorization (optional)
    """

    description: str
    path: str
    paths: list[str]
    tags: str


class SessionDict(TypedDict):
    """
    Type definition for session-specific exclusions.

    Contains the list of applications excluded from the current session.
    """

    excluded: list[str]


class LegacyDotFileDict(TypedDict):
    """
    Type definition for legacy TOML dotfile configuration.

    Used for migration from TOML to YAML format. Contains all fields
    from the original TOML [[dotfile]] entries.

    Fields:
        category: Category grouping (e.g., "Shell", "Editor")
        application: Application name (e.g., "Bash", "Vim")
        description: Human-readable description
        paths: List of file/directory paths
        mirror_dir: Override mirror directory (optional in TOML)
        archive_dir: Override archive directory (optional in TOML)
        enabled: Whether dotfile is enabled for backup
    """

    category: str
    application: str
    description: str
    paths: list[str]
    mirror_dir: str
    archive_dir: str
    enabled: bool
