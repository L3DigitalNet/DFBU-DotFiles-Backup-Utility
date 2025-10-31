#!/usr/bin/env python3
"""
Dotfiles Backup Utility (DFBU)

Description:
    A file backup and restoration utility. Originally meant for backing up
    dotfiles but is useful for any files.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-18-2025
Date Changed: 10-31-2025
License: MIT

Features:
    - Dual-mode operation with interactive backup and restore functionality
    - TOML configuration with Category/Subcategory/Application metadata structure
    - Flexible directory organization with hostname and date-based subdirectory options
    - Python 3.14 Path.copy() with metadata preservation and symlink support
    - Recursive file and directory processing with automatic parent directory creation
    - Permission checking and graceful handling of inaccessible files with skip messages
    - Mirror backup mode for uncompressed file copies maintaining directory structure
    - Compressed archive creation with TAR.GZ format and configurable compression levels
    - Archive rotation with configurable maximum archive limits per retention policy
    - Interactive CLI with color-coded ANSI output and confirmation prompts
    - Dry run mode for operation testing without actual file changes
    - Comprehensive file existence validation and type detection (file vs directory)
    - Separation of concerns with dedicated classes for CLI, backup operations, and utilities
    - Robust configuration validation with ConfigValidator class and TypedDict definitions
    - Centralized path assembly logic with PathAssembler utility for consistent path handling
    - Dedicated MirrorBackup and ArchiveBackup classes for operation encapsulation
    - CLIHandler class isolating UI concerns from business logic
    - FileSystemHelper utility class eliminating DRY violations for common operations
    - Full type hint coverage with typed dictionaries for configuration data structures
    - Standard library first approach with minimal external dependencies

Requirements:
    - Linux environment only
    - Python 3.14+ for latest Path.copy() functionality with metadata preservation
    - Properly configured TOML file located at ./data/dfbu-config.toml
    - Path configurable via global CONFIG_PATH variable
    - Standard library only: pathlib, tomllib, argparse, tarfile, socket, time, datetime, sys
    - AnsiColor and CLIMenu utility classes included inline (no external dependencies)

Known Issues:
    - Comprehensive error handling deferred until v1.0.0 per confident design pattern
    - No support for network paths or remote destinations
    - Restore functionality requires exact hostname match in backup directory structure
    - No verification of successful copies or restoration integrity checks
    - Limited symlink support (follow_symlinks=True only)

Planned Features:
    - Command-line argument support (--dry-run, --verbose, --force, --mode) planned for future versions
    - Enhanced restore capabilities with cross-hostname support and selective file restoration
    - Pre-restoration backup of existing files to prevent data loss
    - Incremental backup support with change detection and differential backups
    - Network path support for remote backup destinations
    - Backup verification and integrity checking with hash comparison
    - Enhanced error handling and reporting for production use (v1.0.0+)

Classes:
    - FileSystemHelper: Utility class for common filesystem operations
    - PathAssembler: Utility class for assembling backup destination paths
    - ConfigValidator: Validates TOML configuration structure and content
    - DotFile: Class containing dotfile information and metadata
    - MirrorBackup: Handles mirror backup operations (uncompressed file copies)
    - ArchiveBackup: Handles archive backup operations (compressed TAR.GZ archives)
    - Options: Contains options from configuration file
    - CLIHandler: Handles all CLI interactions separate from business logic

Functions:
    - wait_for_spacebar(): Waits for user to press spacebar to continue
    - load_config(): Load and validate TOML configuration file
    - sort_dotfiles(): Sort dotfiles by category, subcategory, application
    - create_src_file_list(): Create a list of source files from the given directory
    - create_dest_restore_paths(): Create destination restore paths for each source file
    - copy_files_restore(): Copy files from source to destination paths during restore
    - main(): Main entry point for DFBU application
"""

import argparse
import os
import sys
import tarfile
import termios
import time
import tomllib
import tty
from datetime import datetime
from pathlib import Path
from socket import gethostname
from typing import Any, Final, TypedDict


# Version information
__version__ = "0.3.1"


# =============================================================================
# Utility Classes (formerly from common_lib)
# =============================================================================


class AnsiColor:
    """
    Build ANSI escape sequences for terminal text formatting and styling.

    Attributes:
        fg_color: Foreground color name for text
        bg_color: Background color name for text
        reset: ANSI reset sequence to clear all formatting
        code: Complete ANSI color code for current configuration

    Public methods:
        bold: Returns ANSI code with bold styling
        dim: Returns ANSI code with dim styling
        underline: Returns ANSI code with underline styling
        blinking: Returns ANSI code with blinking styling
        hidden: Returns ANSI code with hidden text styling

    Private methods:
        _code: Assembles ANSI color code with optional styling
    """

    # Valid ANSI color names
    _valid_colors: Final[set[str]] = {
        "black",
        "red",
        "green",
        "yellow",
        "blue",
        "magenta",
        "cyan",
        "white",
        "default",
        "bright black",
        "bright red",
        "bright green",
        "bright yellow",
        "bright blue",
        "bright magenta",
        "bright cyan",
        "bright white",
    }

    # ANSI color codes mapping
    _fg_color_codes: Final[dict[str, str]] = {
        "black": "30",
        "red": "31",
        "green": "32",
        "yellow": "33",
        "blue": "34",
        "magenta": "35",
        "cyan": "36",
        "white": "37",
        "default": "39",
        "bright black": "90",
        "bright red": "91",
        "bright green": "92",
        "bright yellow": "93",
        "bright blue": "94",
        "bright magenta": "95",
        "bright cyan": "96",
        "bright white": "97",
    }

    _bg_color_codes: Final[dict[str, str]] = {
        "black": "40",
        "red": "41",
        "green": "42",
        "yellow": "43",
        "blue": "44",
        "magenta": "45",
        "cyan": "46",
        "white": "47",
        "default": "49",
        "bright black": "100",
        "bright red": "101",
        "bright green": "102",
        "bright yellow": "103",
        "bright blue": "104",
        "bright magenta": "105",
        "bright cyan": "106",
        "bright white": "107",
    }

    def __init__(
        self,
        fg_color: str = "default",
        bg_color: str = "default",
    ) -> None:
        """
        Initialize ANSI color formatter.

        Args:
            fg_color: Foreground color name
            bg_color: Background color name

        Returns:
            None
        """
        # Normalize input colors to lowercase and strip whitespace
        self.fg_color: str = fg_color.lower().strip()
        self.bg_color: str = bg_color.lower().strip()

        # Set ANSI reset sequence constant for clearing all formatting
        self.reset: Final[str] = "\u001b[0m"
        # NOTE: Validation deferred until v1.0.0 per confident design guidelines

        # Generate complete ANSI escape sequence for current color configuration
        self.code: str = self._code()

    def __str__(self) -> str:
        return self.code

    def _code(self, style_code: str = "") -> str:
        """
        Assemble ANSI color code with optional styling.

        Args:
            style_code: Optional ANSI style code

        Returns:
            Complete ANSI escape sequence
        """
        # Look up ANSI codes for foreground and background colors
        fg_code = self._fg_color_codes[self.fg_color]
        bg_code = self._bg_color_codes[self.bg_color]

        # Build complete ANSI escape sequence with optional style code
        if style_code:
            return f"\u001b[{fg_code};{bg_code};{style_code}m"
        return f"\u001b[{fg_code};{bg_code}m"

    @property
    def bold(self) -> str:
        """
        Get ANSI color code with bold styling.

        Args:
            None

        Returns:
            ANSI escape sequence with bold formatting
        """
        return self._code("1")

    @property
    def dim(self) -> str:
        """
        Get ANSI color code with dim styling.

        Args:
            None

        Returns:
            ANSI escape sequence with dim formatting
        """
        return self._code("2")

    @property
    def underline(self) -> str:
        """
        Get ANSI color code with underline styling.

        Args:
            None

        Returns:
            ANSI escape sequence with underline formatting
        """
        return self._code("4")

    @property
    def blinking(self) -> str:
        """
        Get ANSI color code with blinking styling.

        Args:
            None

        Returns:
            ANSI escape sequence with blinking formatting
        """
        return self._code("5")

    @property
    def hidden(self) -> str:
        """
        Get ANSI color code with hidden text styling.

        Args:
            None

        Returns:
            ANSI escape sequence with hidden text formatting
        """
        return self._code("8")


class CLIMenu:
    """
    Simple command-line interface menu utility class.

    Attributes:
        None

    Public methods:
        run: Display menu options and handle user input selection
        ynq: Display yes/no/quit prompt and handle user response

    Private methods:
        None
    """

    def run(
        self,
        menu_options: dict[str, Any],
    ) -> None:
        """
        Display menu options with numbered selection and handle user input.

        Args:
            menu_options: Dictionary mapping option names to functions

        Returns:
            None
        """
        # Display numbered menu options to user
        print("\nMenu Options:")
        for i, option in enumerate(menu_options.keys(), 1):
            print(f"{i}. {option}")

        # Get user selection and execute corresponding function
        while True:
            try:
                choice = input("\nSelect option (number): ").strip()
                option_num = int(choice)

                # Validate selection is within range
                if 1 <= option_num <= len(menu_options):
                    option_name = list(menu_options.keys())[option_num - 1]
                    selected_function = menu_options[option_name]
                    selected_function()
                    break
                print(f"Invalid selection. Please choose 1-{len(menu_options)}")

            except (ValueError, KeyboardInterrupt, EOFError):
                print("\nInvalid input or quit by user. Exiting...")
                sys.exit(0)

    def ynq(
        self,
        prompt: str,
    ) -> bool:
        """
        Display yes/no/quit prompt and handle user input.

        Args:
            prompt: Question to display to user

        Returns:
            True for 'yes', False for 'no'. Exits program on 'quit'
        """
        # Loop until valid response is entered
        while True:
            try:
                # Display prompt and get user input
                response = input(f"{prompt.strip()} (y/n/q) ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                # Handle Ctrl+C or EOF gracefully
                print("\nQuit by user. Exiting...")
                sys.exit(0)

            # Process user response and return appropriate boolean or exit
            if response in ("y", "yes"):
                return True
            if response in ("n", "no"):
                return False
            if response in ("q", "quit"):
                print("Quit by user. Exiting...")
                sys.exit(0)
            else:
                print("Invalid entry. Try again.")


# Color constants using AnsiColor class
RESET: Final = AnsiColor().reset
DEFAULT: Final = AnsiColor("default")
BLACK: Final = AnsiColor("black")
BLUE: Final = AnsiColor("blue")
B_BLUE: Final = AnsiColor("bright blue")
RED: Final = AnsiColor("red")
B_RED: Final = AnsiColor("bright red")
GREEN: Final = AnsiColor("green")
B_GREEN: Final = AnsiColor("bright green")
YELLOW: Final = AnsiColor("yellow")
B_YELLOW: Final = AnsiColor("bright yellow")
MAGENTA: Final = AnsiColor("magenta")
B_MAGENTA: Final = AnsiColor("bright magenta")
CYAN: Final = AnsiColor("cyan")
B_CYAN: Final = AnsiColor("bright cyan")
WHITE: Final = AnsiColor("white")
B_WHITE: Final = AnsiColor("bright white")


# Application constants
CONFIG_PATH: Path = Path(__file__).parent / "data" / "dfbu-config.toml"


# Type definitions for configuration data structures
class DotFileDict(TypedDict):
    """
    Type definition for dotfile configuration dictionary.

    Contains all metadata and path information for individual dotfile entries
    from TOML configuration file.
    """

    category: str
    subcategory: str
    application: str
    description: str
    path: str
    mirror_dir: str
    archive_dir: str


class OptionsDict(TypedDict):
    """
    Type definition for options configuration dictionary.

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


class FileSystemHelper:
    """
    Utility class for common filesystem operations to eliminate DRY violations.

    Provides centralized methods for permission checking, directory creation,
    path expansion, and dry-run messaging to reduce code duplication across
    backup and restore operations.

    Static methods:
        expand_path: Expand user home directory in path string
        check_readable: Check if path is readable with proper permissions
        create_directory: Create directory with parents and proper permissions
        format_dry_run_prefix: Format dry-run prefix for console messages
        format_action_verb: Format action verb based on dry-run mode and tense
    """

    @staticmethod
    def expand_path(path_str: str) -> Path:
        """
        Expand user home directory (~) in path string.

        Args:
            path_str: Path string potentially containing ~

        Returns:
            Expanded Path object
        """
        return Path(path_str).expanduser() if "~" in path_str else Path(path_str)

    @staticmethod
    def check_readable(path: Path) -> bool:
        """
        Check if path is readable with proper permissions.

        Args:
            path: Path to check

        Returns:
            True if readable, False otherwise
        """
        return os.access(path, os.R_OK)

    @staticmethod
    def create_directory(path: Path, dry_run: bool, mode: int = 0o755) -> None:
        """
        Create directory with proper permissions and parent directories.

        Args:
            path: Directory path to create
            dry_run: Whether to simulate operation
            mode: Directory permissions mode
        """
        # Display creation message based on dry-run mode
        if dry_run:
            print(f"  Would create directory: {path}")
        else:
            print(f"  Creating directory: {path}")
            path.mkdir(mode=mode, parents=True, exist_ok=True)

    @staticmethod
    def format_dry_run_prefix(dry_run: bool) -> str:
        """
        Format dry-run prefix for console messages.

        Args:
            dry_run: Whether in dry-run mode

        Returns:
            "[DRY RUN] " if dry_run else ""
        """
        return "[DRY RUN] " if dry_run else ""

    @staticmethod
    def format_action_verb(action: str, dry_run: bool, past_tense: bool = False) -> str:
        """
        Format action verb based on dry-run mode and tense.

        Args:
            action: Base action verb (e.g., "copy", "delete", "create")
            dry_run: Whether in dry-run mode
            past_tense: Whether to use past tense

        Returns:
            Formatted action string
        """
        if dry_run:
            return f"Would {action}"
        return action.capitalize() + ("d" if past_tense else "ing")


class PathAssembler:
    """
    Utility class for assembling backup destination paths.

    Provides centralized path construction logic for mirror and archive
    destinations with hostname and date-based subdirectory support. Handles
    both home directory and root directory path resolution.

    Static methods:
        assemble_dest_path: Assemble destination path based on source path and configuration options
    """

    @staticmethod
    def assemble_dest_path(
        base_path: Path,
        src_path: Path,
        hostname_subdir: bool,
        date_subdir: bool,
    ) -> Path:
        """
        Assemble destination path based on source path and options.

        Args:
            base_path: Base destination directory
            src_path: Source file/directory path
            hostname_subdir: Whether to include hostname subdirectory
            date_subdir: Whether to include date subdirectory

        Returns:
            Assembled destination path
        """
        # Determine prefix and relative path based on source location
        is_relative_to_home: bool = src_path.is_relative_to(Path.home())
        src_relative: Path = (
            src_path.relative_to(Path.home())
            if is_relative_to_home
            else src_path.relative_to(Path("/"))
        )
        prefix: str = "home" if is_relative_to_home else "root"

        # Build destination path components based on configuration options
        dest_parts: list[Path] = [base_path]
        if hostname_subdir:
            dest_parts.append(Path(gethostname()))
        if date_subdir:
            dest_parts.append(Path(time.strftime("%Y-%m-%d")))
        dest_parts.extend([Path(prefix), src_relative])

        # Combine all path components into final destination path
        final_path: Path = dest_parts[0]
        for part in dest_parts[1:]:
            final_path = final_path / part

        return final_path


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
        # Extract and validate compression level with range checking
        compression_level: int = raw_options.get("archive_compression_level", 9)
        if not isinstance(compression_level, int) or not (0 <= compression_level <= 9):
            compression_level = 9

        # Extract and validate max archives with minimum value checking
        max_archives: int = raw_options.get("max_archives", 5)
        if not isinstance(max_archives, int) or max_archives < 1:
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

        Args:
            raw_dotfile: Raw dotfile metadata from TOML config

        Returns:
            Validated dotfile metadata dictionary
        """
        # Build validated dictionary ensuring all required fields exist with defaults
        validated: DotFileDict = {
            "category": raw_dotfile.get("category", "Unknown"),
            "subcategory": raw_dotfile.get("subcategory", "Unknown"),
            "application": raw_dotfile.get("application", "Unknown"),
            "description": raw_dotfile.get("description", "None"),
            "path": raw_dotfile.get("path", ""),
            "mirror_dir": raw_dotfile.get("mirror_dir", "~/DFBU_Mirror"),
            "archive_dir": raw_dotfile.get("archive_dir", "~/DFBU_Archives"),
        }

        return validated


class DotFile:
    """
    Class containing dotfile information and metadata from TOML configuration.

    Represents a single file or directory entry to be backed up with all
    associated metadata, source path, and computed destination paths for
    both mirror and archive operations.

    Attributes:
        category: high-level grouping of dotfile
        subcategory: more specific grouping within category
        application: specific application name
        description: human-readable description of dotfile
        src_path: source path of dotfile (expanded from ~)
        name: filename or directory name
        exists: whether the source path exists on filesystem
        is_dir: whether the source path is a directory
        is_file: whether the source path is a file
        type: display string indicating File or Directory
        relative_to_home: whether path is relative to home directory
        dest_path_mirror: destination path for mirror backup
        dest_path_archive: destination path for archive backup
        relative_path: relative path from home or root

    Public methods:
        __str__: Formatted string representation with metadata and paths

    Private methods:
        _get_relative_path: Calculate relative path from home or root directory
    """

    def __init__(
        self,
        raw_dotfile: DotFileDict,
        options: Options,
    ) -> None:
        """
        Initialize dotfile metadata from configuration.

        Args:
            raw_dotfile: Validated dotfile metadata from configuration
            options: Options instance with configuration
        """
        # Expand path strings to Path objects for mirror and archive destinations
        mirror_base_dest_path: Path = FileSystemHelper.expand_path(
            raw_dotfile["mirror_dir"]
        )
        archive_base_dest_path: Path = FileSystemHelper.expand_path(
            raw_dotfile["archive_dir"]
        )

        # Extract metadata fields from configuration
        self.category: str = raw_dotfile["category"]
        self.subcategory: str = raw_dotfile["subcategory"]
        self.application: str = raw_dotfile["application"]
        self.description: str = raw_dotfile["description"]
        self.src_path: Path = FileSystemHelper.expand_path(raw_dotfile["path"])
        self.name: str = self.src_path.name

        # Check source path properties for backup operations
        self.exists: bool = self.src_path.exists()
        self.is_dir: bool = self.src_path.is_dir()
        self.is_file: bool = self.src_path.is_file()
        self.type: str = "Directory" if self.is_dir else "File"
        self.relative_to_home: bool = self.src_path.is_relative_to(Path.home())

        # Assemble destination paths using PathAssembler utility
        self.dest_path_mirror: Path = PathAssembler.assemble_dest_path(
            mirror_base_dest_path,
            self.src_path,
            options.hostname_subdir,
            options.date_subdir,
        )
        self.dest_path_archive: Path = PathAssembler.assemble_dest_path(
            archive_base_dest_path,
            self.src_path,
            options.hostname_subdir,
            options.date_subdir,
        )
        self.relative_path: Path = self._get_relative_path()

    def __str__(self) -> str:
        """
        String representation of dotfile.
        """
        return (
            f"[{self.type}] {BLUE.bold}{self.name}{RESET}: "
            f"{MAGENTA}{self.category}{RESET} {DEFAULT.bold}|{RESET} "
            f"{MAGENTA}{self.subcategory}{RESET} {DEFAULT.bold}|{RESET} "
            f"{MAGENTA}{self.application}{RESET}\n"
            f"  Description: {self.description}\n"
            f"  Source path: {DEFAULT.underline}{self.src_path}{RESET}\n"
            f"  Mirror destination: {DEFAULT.underline}{self.dest_path_mirror}{RESET}\n"
        )

    def _get_relative_path(self) -> Path:
        """
        Get the relative path for the dotfile.

        Returns:
            Relative path of the dotfile from home or root
        """
        # Calculate relative path based on home or root directory location
        if self.relative_to_home:
            relative_path: Path = Path("home") / self.src_path.relative_to(Path.home())
        else:
            relative_path: Path = Path("root") / self.src_path.relative_to(Path("/"))

        return relative_path


class MirrorBackup:
    """
    Handles mirror backup operations (uncompressed file copies).

    Provides methods to copy files and directories with Python 3.14 Path.copy()
    including metadata preservation and symlink following. Maintains original
    directory structure in destination.

    Static methods:
        execute: Execute mirror backup operation for all dotfiles

    Private methods:
        _process_file: Process individual file backup with metadata preservation
        _process_directory: Process directory backup recursively
    """

    @staticmethod
    def execute(dotfiles: list[DotFile], dry_run: bool) -> None:
        """
        Execute mirror backup operation.

        Args:
            dotfiles: List of DotFile objects to backup
            dry_run: Whether to simulate operations without actual file changes
        """
        print("Copying...\n")

        for dotfile in dotfiles:
            if not dotfile.exists:
                continue

            if dotfile.is_file:
                MirrorBackup._process_file(dotfile, dry_run)
            elif dotfile.is_dir:
                MirrorBackup._process_directory(dotfile, dry_run)

    @staticmethod
    def _process_file(dotfile: DotFile, dry_run: bool) -> None:
        """
        Process individual file backup.

        Args:
            dotfile: DotFile object containing file information
            dry_run: Whether to simulate operations
        """
        # Display processing message with dry-run prefix if applicable
        prefix: str = FileSystemHelper.format_dry_run_prefix(dry_run)
        print(f"{prefix}Processing file: {dotfile.src_path}")

        # Check file readability before attempting copy
        if not FileSystemHelper.check_readable(dotfile.src_path):
            action: str = FileSystemHelper.format_action_verb("skip", dry_run, True)
            print(f"  {action}: {dotfile.src_path} (permission denied)")
            return

        # Create parent directory structure if needed
        if not dotfile.dest_path_mirror.parent.exists():
            FileSystemHelper.create_directory(
                dotfile.dest_path_mirror.parent, dry_run, 0o755
            )

        # Copy file with metadata preservation using Python 3.14 Path.copy()
        action_verb: str = FileSystemHelper.format_action_verb("copy", dry_run, True)
        print(
            f"  {action_verb}: {dotfile.src_path}\n    to {dotfile.dest_path_mirror}\n"
        )

        if not dry_run:
            dotfile.src_path.copy(
                dotfile.dest_path_mirror,
                follow_symlinks=True,
                preserve_metadata=True,
            )

    @staticmethod
    def _process_directory(dotfile: DotFile, dry_run: bool) -> None:
        """
        Process directory backup recursively.

        Args:
            dotfile: DotFile object containing directory information
            dry_run: Whether to simulate operations
        """
        # Display processing message with dry-run prefix if applicable
        prefix: str = FileSystemHelper.format_dry_run_prefix(dry_run)
        print(f"{prefix}Processing directory: {dotfile.src_path}")

        # Check directory readability before processing contents
        if not FileSystemHelper.check_readable(dotfile.src_path):
            action: str = FileSystemHelper.format_action_verb("skip", dry_run, True)
            print(f"  {action}: {dotfile.src_path} (permission denied)")
            return

        # Gather all files in directory tree recursively
        files: list[Path] = [
            Path(file) for file in dotfile.src_path.rglob("*") if file.is_file()
        ]

        # Process each file in the directory
        for file in files:
            # Skip files without read permissions
            if not FileSystemHelper.check_readable(file):
                action: str = FileSystemHelper.format_action_verb("skip", dry_run, True)
                print(f"  {action}: {file} (permission denied)")
                continue

            # Calculate destination path maintaining directory structure
            file_base: Path = dotfile.dest_path_mirror
            file_relative: Path = file.relative_to(dotfile.src_path)
            file_dest_path: Path = file_base / file_relative

            # Create parent directory structure if needed
            if not file_dest_path.parent.exists():
                FileSystemHelper.create_directory(file_dest_path.parent, dry_run)

            # Copy file with metadata preservation using Python 3.14 Path.copy()
            action_verb: str = FileSystemHelper.format_action_verb(
                "copy", dry_run, False
            )
            print(f"  {action_verb}: {file}\n    to {file_dest_path}")

            if not dry_run:
                file.copy(
                    file_dest_path,
                    follow_symlinks=True,
                    preserve_metadata=True,
                )

            # Print completion message for last file in directory
            if file == files[-1]:
                action_verb = FileSystemHelper.format_action_verb("copy", dry_run, True)
                print(
                    f"  {action_verb} directory: {dotfile.src_path}\n    to {dotfile.dest_path_mirror}\n"
                )


class ArchiveBackup:
    """
    Handles archive backup operations (compressed TAR.GZ archives).

    Provides methods to create timestamped compressed archives and manage
    archive rotation based on retention policies. Supports configurable
    compression levels and maximum archive limits.

    Static methods:
        create: Create timestamped compressed TAR.GZ archive of dotfiles
        rotate: Rotate archives based on retention policy and delete oldest
    """

    @staticmethod
    def create(
        dotfiles: list[DotFile],
        archive_base_dest_path: Path,
        dry_run: bool,
    ) -> None:
        """
        Create compressed archive of dotfiles.

        Args:
            dotfiles: List of DotFile objects to archive
            archive_base_dest_path: Base destination path for archives
            dry_run: Whether to simulate operations
        """
        # Generate timestamped archive filename for uniqueness
        archive_name: str = (
            "dotfiles-" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".tar.gz"
        )
        archive_path: Path = archive_base_dest_path / archive_name

        # Create archive base directory if it doesn't exist
        if not archive_base_dest_path.exists():
            FileSystemHelper.create_directory(archive_base_dest_path, dry_run, 0o755)

        # Display archive creation message with dry-run prefix if applicable
        prefix: str = FileSystemHelper.format_dry_run_prefix(dry_run)
        print(f"{prefix}Creating archive {archive_name}...\n")

        # Create compressed TAR.GZ archive with all existing dotfiles
        if not dry_run:
            with tarfile.open(archive_path, "w:gz") as tar:
                for dotfile in dotfiles:
                    if dotfile.exists:
                        print(f"  Packaging: {dotfile.src_path}")
                        tar.add(dotfile.src_path)
        else:
            # Simulate archive creation in dry-run mode
            for dotfile in dotfiles:
                if dotfile.exists:
                    print(f"  Would package: {dotfile.src_path}\n")

        # Display completion message with full archive path
        completion_prefix: str = FileSystemHelper.format_dry_run_prefix(dry_run)
        completion_verb: str = "would be created" if dry_run else "created"
        print(f"\n{completion_prefix}Archive {completion_verb} at: {archive_path}\n")

    @staticmethod
    def rotate(
        archive_base_dest_path: Path,
        max_archives: int,
        dry_run: bool,
    ) -> None:
        """
        Rotate archives based on retention policy.

        Args:
            archive_base_dest_path: Base destination path for archives
            max_archives: Maximum number of archives to retain
            dry_run: Whether to simulate operations
        """
        print("Rotating archives...\n")

        # Get existing archives sorted by modification time (oldest first)
        archives: list[Path] = sorted(
            archive_base_dest_path.glob("dotfiles-*.tar.gz"),
            key=lambda x: x.stat().st_mtime,
        )

        # Calculate number of archives to delete based on retention limit
        num_archives: int = len(archives)
        num_to_delete: int = num_archives - max_archives

        # Delete oldest archives exceeding retention limit
        if num_to_delete > 0:
            for i in range(num_to_delete):
                archive_to_delete: Path = archives[i]
                prefix: str = FileSystemHelper.format_dry_run_prefix(dry_run)
                action: str = FileSystemHelper.format_action_verb(
                    "delete", dry_run, False
                )
                print(f"{prefix}{action} archive: {archive_to_delete}")

                if not dry_run:
                    archive_to_delete.unlink()
        else:
            print("No archives need to be deleted.\n")


class Options:
    """
    Contains backup operation options from TOML configuration file.

    Centralizes all backup behavior settings including mirror/archive modes,
    directory organization preferences, and archive retention policies.

    Attributes:
        mirror: whether to perform uncompressed mirror backup
        archive: whether to create compressed TAR.GZ archive
        hostname_subdir: whether to organize backups by hostname subdirectory
        date_subdir: whether to organize backups by date subdirectory
        archive_format: archive format string (currently only tar.gz supported)
        archive_compression_level: compression level for archives (0-9)
        rotate_archives: whether to enforce archive retention limits
        max_archives: maximum number of archives to retain before rotation

    Public methods:
        __str__: Formatted string representation of all options
    """

    def __init__(self, raw_options: OptionsDict) -> None:
        """
        Initialize options from validated options dictionary.

        Args:
            raw_options: Validated options from configuration file
        """
        # Directly assign validated options without get() or defaults
        self.mirror: bool = raw_options["mirror"]
        self.archive: bool = raw_options["archive"]
        self.hostname_subdir: bool = raw_options["hostname_subdir"]
        self.date_subdir: bool = raw_options["date_subdir"]
        self.archive_format: str = raw_options["archive_format"]
        self.archive_compression_level: int = raw_options["archive_compression_level"]
        self.rotate_archives: bool = raw_options["rotate_archives"]
        self.max_archives: int = raw_options["max_archives"]

    def __str__(self) -> str:
        """
        String representation of options.
        """
        return (
            f"The following options are set:\n"
            f"  Uncompressed mirror: {self.mirror}\n"
            f"  Create archive: {self.archive}\n"
            f"  Use hostname subdirectory: {self.hostname_subdir}\n"
            f"  Use date subdirectory: {self.date_subdir}\n"
            f"  Archive format: {self.archive_format if self.archive else 'N/A'}\n"
            f"  Archive compression level: {self.archive_compression_level if self.archive else 'N/A'}\n"
            f"  Rotate archives: {self.rotate_archives if self.archive else 'N/A'}\n"
            f"  Maximum number of archives to keep: {self.max_archives if self.archive else 'N/A'}\n"
        )


class CLIHandler:
    """
    Handles all CLI interactions separate from business logic.

    Provides methods for user prompts, confirmations, and output formatting
    to isolate UI concerns from backup/restore operations. Uses AnsiColor
    for colorized output and CLIMenu for interactive prompts.

    Static methods:
        parse_args: Parse command-line arguments for dry-run and force flags
        get_mode: Get backup or restore mode from interactive user menu
        get_restore_source: Get and validate restore source path from user input
        confirm_action: Get user confirmation using CLIMenu.ynq()
        display_backup_summary: Display formatted summary of proposed backup actions
        display_restore_summary: Display formatted summary of proposed restore actions
    """

    @staticmethod
    def parse_args() -> tuple[bool, bool]:
        """
        Parse command-line arguments.

        Returns:
            tuple[bool, bool]: (dry_run, force) flags
        """
        parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description="Dotfiles Backup Utility (DFBU)",
            epilog="Example usage: dfbu.py --dry-run",
        )

        parser.add_argument(
            "-d",
            "--dry-run",
            action="store_true",
            help="Perform a dry run without making any changes",
        )

        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Force the operation without confirmation",
        )

        args: argparse.Namespace = parser.parse_args()
        return args.dry_run, args.force

    @staticmethod
    def get_mode() -> str:
        """
        Get user input to choose backup or restore mode.

        Returns:
            str: The validated mode ("backup" or "restore")
        """
        print("Choose backup mode:")
        print("  1. backup files")
        print("  2. restore from backup")

        while True:
            choice: str = input("Choice (1/2/q): ").strip()
            if choice == "1":
                return "backup"
            if choice == "2":
                return "restore"
            if choice.lower() in ("q", "quit", "exit"):
                print("Exiting...")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 1, 2, or q.")

    @staticmethod
    def get_restore_source() -> Path:
        """
        Get user input for source path to restore from.

        Returns:
            Path: The validated source path
        """
        while True:
            print(
                "\nEnter the full path to the source directory, or 'q' to quit. (most likely hostname)"
            )
            raw_path: str = input("Path: ").strip()
            src_path: Path = Path(raw_path).expanduser()

            if raw_path.lower() in ("q", "quit", "exit"):
                print("Exiting...")
                sys.exit(0)
            elif src_path.exists() and src_path.is_dir():
                # Confirm with user
                while True:
                    confirm: str = (
                        (input(f"You entered: {src_path}. Is this correct? (y/n): "))
                        .strip()
                        .lower()
                    )

                    if confirm == "y":
                        return src_path
                    if confirm == "n":
                        break
            elif src_path.exists() and not src_path.is_dir():
                print(f"{DEFAULT.underline}{src_path}{RESET} is not a directory.")
            else:
                print(f"{DEFAULT.underline}{src_path}{RESET} does not exist.")

    @staticmethod
    def confirm_action(prompt: str) -> bool:
        """
        Get user confirmation for an action.

        Args:
            prompt: Confirmation prompt text

        Returns:
            bool: True if user confirms, False otherwise
        """
        menu: CLIMenu = CLIMenu()
        return menu.ynq(prompt)

    @staticmethod
    def display_backup_summary(
        dotfiles: list[DotFile],
        options: Options,
        dry_run: bool,
    ) -> None:
        """
        Display summary of backup actions to be taken.

        Args:
            dotfiles: List of DotFile objects to summarize
            options: Options instance with configuration
            dry_run: Whether this is a dry run
        """
        copy: int = 0
        mirror: int = 0
        archive: int = 0
        skip: int = 0

        # Print items that do not exist on the system and will be skipped
        print(
            f"\n{DEFAULT.bold}The following items do not exist and will be skipped{RESET}:\n"
        )
        for dotfile in dotfiles:
            if not dotfile.exists:
                skip += 1
                print(
                    f"  {YELLOW}{dotfile.name}{RESET} does not exist on this system. Skipping."
                )

        if skip == 0:
            print("  All items located on system\n")
        else:
            print("")

        # Print items that exist and will be processed
        print(f"{DEFAULT.bold}The following items will be processed:{RESET}\n")
        for dotfile in dotfiles:
            if dotfile.exists:
                copy += 1
                print(dotfile)
                if options.mirror:
                    mirror += 1
                if options.archive:
                    archive += 1

        print(
            f"{DEFAULT.bold}Proposed actions:{RESET}\n",
            f"  Dry run: {GREEN if dry_run else YELLOW}{dry_run}{RESET}\n",
            f"  Items to copy: {GREEN}{copy}{RESET}\n",
            f"    Items to mirror: {GREEN.dim}{mirror}{RESET}\n",
            f"    Items to archive: {GREEN.dim}{archive}{RESET}\n",
            f"  Items to skip: {YELLOW}{skip}{RESET}\n",
        )

    @staticmethod
    def display_restore_summary(
        src_files: list[Path],
        dest_files: list[Path],
    ) -> None:
        """
        Display summary of restore actions to be taken.

        Args:
            src_files: List of source file paths to summarize
            dest_files: List of destination file paths to summarize
        """
        print(f"\n{DEFAULT.bold}The following files will be restored:{RESET}\n")

        for src_file, dest_file in zip(src_files, dest_files, strict=False):
            if src_file.is_file():
                print(
                    f"  {BLUE.bold}{src_file.name}{RESET}: {DEFAULT}{src_file}{RESET}\n"
                    f"    -> {DEFAULT}{dest_file}{RESET}\n"
                )


def wait_for_spacebar() -> None:
    """
    Wait for user to press spacebar before continuing execution.

    Sets terminal to raw mode to capture single keypress, handles Ctrl+C
    interrupt, and restores terminal settings before returning.
    """
    print("Press SPACE to continue...")

    # Save terminal settings
    fd: int = sys.stdin.fileno()
    old_settings: list[Any] = termios.tcgetattr(fd)

    try:
        # Set terminal to raw mode
        tty.setraw(sys.stdin.fileno())

        while True:
            char = sys.stdin.read(1)
            if char == " ":  # Spacebar pressed
                break
            if char == "\x03":  # Ctrl+C
                raise KeyboardInterrupt

    finally:
        # Restore terminal settings even if interrupted
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    print()


def load_config() -> tuple[OptionsDict, list[DotFileDict]]:
    """
    Load and validate TOML configuration file using Python's tomllib.

    Reads configuration from CONFIG_PATH, validates structure with
    ConfigValidator, and returns typed dictionaries.

    Returns:
        tuple containing validated OptionsDict and list of DotFileDict objects
    """
    # Read TOML configuration file in binary mode
    with open(CONFIG_PATH, "rb") as toml_file:
        config_data: dict[str, Any] = tomllib.load(toml_file)

    # Validate configuration structure and return typed dictionaries
    return ConfigValidator.validate_config(config_data)


def sort_dotfiles(
    dotfiles: list[DotFile],
) -> list[DotFile]:
    """
    Sort dotfiles by category, subcategory, then application name.

    Performs multi-level sort for organized display and processing order.

    Args:
        dotfiles: unsorted list of DotFile objects

    Returns:
        sorted list of DotFile objects
    """
    dotfiles.sort(key=lambda dotfile: dotfile.application)
    dotfiles.sort(key=lambda dotfile: dotfile.subcategory)
    dotfiles.sort(key=lambda dotfile: dotfile.category)

    return dotfiles


def create_src_file_list(
    src_dir: Path,
) -> list[Path]:
    """
    Create list of all files in directory recursively for restore operations.

    Uses Path.rglob() to walk directory tree and collect only file paths,
    excluding directories.

    Args:
        src_dir: source directory path to scan

    Returns:
        list of all file Path objects found recursively
    """
    src_files: list[Path] = []

    for file in src_dir.rglob("*"):
        if file.is_file():
            src_files.append(file)

    return src_files


def create_dest_restore_paths(
    src_files: list[Path],
) -> list[Path]:
    """
    Create destination restore paths by reconstructing original paths from backup structure.

    Parses backup directory structure (hostname/home or hostname/root) and
    reconstructs original absolute paths for file restoration.

    Args:
        src_files: list of source file paths from backup directory

    Returns:
        list of destination file paths where files should be restored
    """
    full_paths: list[Path] = []
    hostname: str = gethostname()

    # Process each source file to reconstruct original destination path
    for src_path in src_files:
        # Extract path components after hostname directory in backup structure
        try:
            hostname_index: int = src_path.parts.index(hostname)
            r_host: Path = Path(*src_path.parts[hostname_index + 1 :])
        except ValueError:
            print(
                f"{RED}Error:{RESET} Could not find hostname directory '{hostname}' in path: "
                f"{DEFAULT.underline}{src_path}{RESET}"
            )
            continue

        # Reconstruct destination path based on home or root directory location
        if "home" in r_host.parts:
            # Extract path after home directory marker and build full home path
            home_index: int = r_host.parts.index("home")
            r_home: Path = Path(*r_host.parts[home_index + 1 :])
            full_path: Path = Path.home() / r_home
            full_paths.append(full_path)
        elif "root" in r_host.parts:
            # Extract path after root directory marker and build full absolute path
            root_index: int = r_host.parts.index("root")
            r_root: Path = Path(*r_host.parts[root_index + 1 :])
            full_path: Path = Path("/") / r_root
            full_paths.append(full_path)
        else:
            print(
                f"{RED}Error:{RESET} Could not determine if file is from home or root directory:\n"
                f"  {DEFAULT.underline}{src_path}{RESET}"
            )
            continue

    return full_paths


def copy_files_restore(
    src_files: list[Path],
    dest_paths: list[Path],
    dry_run: bool,
) -> None:
    """
    Copy files from backup to original locations during restore operations.

    Creates necessary parent directories and copies files with Python 3.14
    Path.copy() including metadata preservation and symlink following.

    Args:
        src_files: list of source file paths from backup to copy
        dest_paths: list of destination file paths where files should be restored
        dry_run: whether to simulate operations without actual file changes
    """
    # Display mode message with dry-run indicator if applicable
    if dry_run:
        print("DRY RUN mode enabled. No files will be copied.\n")

    # Create necessary parent directories for all destination paths
    for p in dest_paths:
        if not p.parent.exists():
            FileSystemHelper.create_directory(p.parent, dry_run)

    # Copy files with metadata preservation using Python 3.14 Path.copy()
    print(f"\n{DEFAULT.bold}Processing files:{RESET}\n")
    for src_file, dest_path in zip(src_files, dest_paths, strict=False):
        print(f"  copying {BLUE.bold}{src_file.name}{RESET} to: {dest_path}")

        if not dry_run:
            src_file.copy(
                dest_path,
                follow_symlinks=True,
                preserve_metadata=True,
            )


def main() -> None:
    """
    Main entry point for DFBU application with dual-mode workflow.

    Orchestrates complete backup or restore workflow including mode selection,
    configuration loading, user confirmation, and operation execution. Handles
    both mirror and archive backup modes as well as interactive restore.
    """
    print(f"{BLUE.bold}Dotfiles Backup Utility (DFBU){RESET} ver. {__version__}\n")

    # Parse command-line arguments for dry-run and force flags
    dry_run: bool
    force: bool
    dry_run, force = CLIHandler.parse_args()

    # Get user input to choose operation mode (backup or restore)
    mode: str = CLIHandler.get_mode()

    # Execute backup workflow
    if mode == "backup":
        # Load TOML configuration file with options and dotfile definitions
        raw_options: OptionsDict
        raw_dotfiles: list[DotFileDict]
        raw_options, raw_dotfiles = load_config()

        # Parse TOML configuration data into Options and DotFile objects
        options: Options = Options(raw_options)
        dotfiles: list[DotFile] = [DotFile(df, options) for df in raw_dotfiles]

        # Sort dotfiles by category, subcategory, and application
        dotfiles = sort_dotfiles(dotfiles)

        # Execute mirror backup operations if enabled
        if options.mirror:
            # Display summary of proposed backup actions
            CLIHandler.display_backup_summary(dotfiles, options, dry_run)

            # Prompt user for confirmation before proceeding
            if CLIHandler.confirm_action("Proceed with backup? (y/n): "):
                MirrorBackup.execute(dotfiles, dry_run)
            else:
                print("Backup operation cancelled by user.")

        # Execute archive creation if enabled
        if options.archive:
            # Determine archive base destination path from configuration with fallback
            if raw_dotfiles:
                archive_dir = raw_dotfiles[0].get("archive_dir", "~/DFBU_Archives")
            else:
                archive_dir = "~/DFBU_Archives"
            archive_base_dest_path: Path = Path(archive_dir).expanduser()

            # Add hostname subdirectory if configured
            if options.hostname_subdir:
                archive_base_dest_path = archive_base_dest_path / gethostname()

            # Create compressed archive and rotate old archives
            ArchiveBackup.create(dotfiles, archive_base_dest_path, dry_run)
            if options.rotate_archives:
                ArchiveBackup.rotate(
                    archive_base_dest_path, options.max_archives, dry_run
                )

    # Execute restore workflow
    elif mode == "restore":
        # Prompt user for source directory containing backup files
        src_dir: Path = CLIHandler.get_restore_source()

        # Build list of all files in source directory recursively
        src_files: list[Path] = create_src_file_list(src_dir)

        # Map source files to their original destination paths
        dest_paths: list[Path] = create_dest_restore_paths(src_files)

        # Display summary of proposed restore operations
        CLIHandler.display_restore_summary(src_files, dest_paths)

        # Prompt user for confirmation before proceeding
        if CLIHandler.confirm_action("Proceed with restore? (y/n): "):
            copy_files_restore(src_files, dest_paths, dry_run)
        else:
            print("Restore operation cancelled by user.")


if __name__ == "__main__":
    main()
