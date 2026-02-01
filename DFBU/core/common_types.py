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
    verify_after_backup: bool
    hash_verification: bool


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


class VerificationResultDict(TypedDict):
    """
    Type definition for individual file verification result.

    Contains verification status and details for a single file.

    Fields:
        path: Original source path that was backed up
        backup_path: Path in the backup directory
        status: Verification status ("ok", "size_mismatch", "hash_mismatch", "missing", "error")
        size_match: Whether file sizes match
        hash_match: Whether SHA-256 hashes match (None if not checked)
        expected_size: Expected file size in bytes
        actual_size: Actual file size in bytes (None if file missing)
        error: Error message if status is "error"
    """

    path: str
    backup_path: str
    status: str
    size_match: bool
    hash_match: bool | None
    expected_size: int
    actual_size: int | None
    error: str


class VerificationReportDict(TypedDict):
    """
    Type definition for backup verification report.

    Contains overall verification summary and individual file results.

    Fields:
        timestamp: ISO format timestamp of verification
        backup_type: Type of backup verified ("mirror" or "archive")
        backup_path: Path to the backup that was verified
        total_files: Total number of files checked
        verified_ok: Number of files that passed verification
        verified_failed: Number of files that failed verification
        hash_verified: Whether SHA-256 hash verification was performed
        results: List of individual file verification results
    """

    timestamp: str
    backup_type: str
    backup_path: str
    total_files: int
    verified_ok: int
    verified_failed: int
    hash_verified: bool
    results: list[VerificationResultDict]


# =============================================================================
# Error Handling Types (v0.9.0)
# =============================================================================


class PathResultDict(TypedDict):
    """
    Type definition for individual path operation result.

    Contains the result of an operation on a single file or directory path.

    Fields:
        path: The file or directory path that was processed
        dest_path: Destination path (for copy operations, None if not applicable)
        status: Result status ("success", "failed", "skipped", "warning")
        error_type: Error category if failed (None if success)
        error_message: Human-readable error message (empty if success)
        can_retry: Whether this operation might succeed on retry
    """

    path: str
    dest_path: str | None
    status: str  # "success", "failed", "skipped", "warning"
    error_type: str | None  # "permission", "not_found", "disk_full", "locked", etc.
    error_message: str
    can_retry: bool


class OperationResultDict(TypedDict):
    """
    Type definition for structured operation result.

    Contains comprehensive result information for backup/restore operations,
    replacing simple success/fail returns with detailed tracking.

    Fields:
        status: Overall operation status ("success", "partial", "failed")
        operation_type: Type of operation ("mirror_backup", "archive_backup", "restore")
        total_items: Total number of items attempted
        completed: List of successfully processed paths
        failed: List of paths that failed with error details
        skipped: List of paths that were skipped with reasons
        warnings: List of non-fatal warning messages
        can_retry: List of paths that might succeed on retry
        timestamp: ISO format timestamp of operation
    """

    status: str  # "success", "partial", "failed"
    operation_type: str  # "mirror_backup", "archive_backup", "restore"
    total_items: int
    completed: list[PathResultDict]
    failed: list[PathResultDict]
    skipped: list[PathResultDict]
    warnings: list[str]
    can_retry: list[str]  # List of path strings that can be retried
    timestamp: str
