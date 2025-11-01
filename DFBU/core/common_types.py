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
Date Changed: 11-01-2025
License: MIT

Features:
    - Centralized TypedDict definitions for dotfile configuration
    - Shared type definitions for backup options
    - Type safety across CLI and GUI modules
    - Standard library only (no external dependencies)

Requirements:
    - Python 3.14+ for latest typing features

Classes:
    - DotFileDict: TypedDict for dotfile configuration
    - OptionsDict: TypedDict for backup options configuration
"""

from typing import TypedDict


class DotFileDict(TypedDict):
    """
    Type definition for dotfile configuration dictionary.

    Contains all metadata and path information for individual dotfile entries
    from TOML configuration file. Supports multiple paths per dotfile entry.
    """

    category: str
    subcategory: str
    application: str
    description: str
    paths: list[str]
    mirror_dir: str
    archive_dir: str
    enabled: bool


class OptionsDict(TypedDict):
    """
    Type definition for backup options configuration dictionary.

    Contains all backup operation settings and preferences from TOML
    configuration file.
    """

    mirror: bool
    archive: bool
    hostname_subdir: bool
    date_subdir: bool
    archive_format: str
    archive_compression_level: int
    rotate_archives: bool
    max_archives: int
