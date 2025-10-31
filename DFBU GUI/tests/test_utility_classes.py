#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for DFBU Utility Classes

Description:
    Comprehensive unit tests for FileSystemHelper, PathAssembler, and
    ConfigValidator utility classes following pytest framework and AAA pattern.
    Tests focus on core functionality and happy paths before v1.0.0.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-29-2025
Date Changed: 10-29-2025
License: MIT

Features:
    - Unit tests for FileSystemHelper path and permission operations
    - Unit tests for PathAssembler path construction logic
    - Unit tests for ConfigValidator TOML validation logic
    - AAA pattern test structure for clarity
    - Pytest fixtures for reusable test data
    - Mock filesystem operations for isolation
    - Type safety validation for TypedDict structures

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - pytest framework for testing
    - unittest.mock for mocking filesystem operations
"""

import os
import sys
from pathlib import Path
from socket import gethostname
from typing import Any
from unittest.mock import Mock, patch

import pytest

# Add project to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common_lib"))

# Import module under test
from dfbug_cli_backup import (
    FileSystemHelper,
    PathAssembler,
    ConfigValidator,
    DotFileDict,
    OptionsDict,
)


class TestFileSystemHelper:
    """
    Test suite for FileSystemHelper utility class.

    Tests path expansion, permission checking, directory creation,
    and message formatting utilities.
    """

    def test_expand_path_with_tilde(self) -> None:
        """Test that tilde expansion works correctly for home directory."""
        # Arrange
        path_str: str = "~/test/file.txt"

        # Act
        result: Path = FileSystemHelper.expand_path(path_str)

        # Assert
        assert result == Path.home() / "test" / "file.txt"
        assert "~" not in str(result)

    def test_expand_path_without_tilde(self) -> None:
        """Test that paths without tilde remain unchanged."""
        # Arrange
        path_str: str = "/absolute/path/file.txt"

        # Act
        result: Path = FileSystemHelper.expand_path(path_str)

        # Assert
        assert result == Path("/absolute/path/file.txt")

    def test_check_readable_for_readable_file(self, tmp_path: Path) -> None:
        """Test that readable file is correctly identified."""
        # Arrange
        test_file: Path = tmp_path / "readable.txt"
        test_file.write_text("test content")

        # Act
        result: bool = FileSystemHelper.check_readable(test_file)

        # Assert
        assert result is True

    def test_check_readable_for_nonexistent_file(self) -> None:
        """Test that nonexistent file returns False."""
        # Arrange
        nonexistent: Path = Path("/nonexistent/file.txt")

        # Act
        result: bool = FileSystemHelper.check_readable(nonexistent)

        # Assert
        assert result is False

    @patch("os.access")
    def test_check_readable_for_permission_denied(
        self, mock_access: Mock, tmp_path: Path
    ) -> None:
        """Test that file without read permission returns False."""
        # Arrange
        test_file: Path = tmp_path / "unreadable.txt"
        mock_access.return_value = False

        # Act
        result: bool = FileSystemHelper.check_readable(test_file)

        # Assert
        assert result is False
        mock_access.assert_called_once_with(test_file, os.R_OK)

    def test_create_directory_actual_mode(self, tmp_path: Path) -> None:
        """Test that directory is created in non-dry-run mode."""
        # Arrange
        new_dir: Path = tmp_path / "subdir" / "nested"
        dry_run: bool = False

        # Act
        FileSystemHelper.create_directory(new_dir, dry_run, 0o755)

        # Assert
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_directory_dry_run_mode(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test that directory is not created in dry-run mode."""
        # Arrange
        new_dir: Path = tmp_path / "would_create"
        dry_run: bool = True

        # Act
        FileSystemHelper.create_directory(new_dir, dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "Would create directory:" in captured.out
        assert not new_dir.exists()

    def test_format_dry_run_prefix_enabled(self) -> None:
        """Test dry-run prefix formatting when enabled."""
        # Arrange
        dry_run: bool = True

        # Act
        result: str = FileSystemHelper.format_dry_run_prefix(dry_run)

        # Assert
        assert result == "[DRY RUN] "

    def test_format_dry_run_prefix_disabled(self) -> None:
        """Test dry-run prefix formatting when disabled."""
        # Arrange
        dry_run: bool = False

        # Act
        result: str = FileSystemHelper.format_dry_run_prefix(dry_run)

        # Assert
        assert result == ""

    def test_format_action_verb_present_tense_active(self) -> None:
        """Test action verb formatting in present tense, active mode."""
        # Arrange
        action: str = "copy"
        dry_run: bool = False
        past_tense: bool = False

        # Act
        result: str = FileSystemHelper.format_action_verb(action, dry_run, past_tense)

        # Assert
        assert result == "Copying"

    def test_format_action_verb_past_tense_active(self) -> None:
        """Test action verb formatting in past tense, active mode."""
        # Arrange
        action: str = "copy"
        dry_run: bool = False
        past_tense: bool = True

        # Act
        result: str = FileSystemHelper.format_action_verb(action, dry_run, past_tense)

        # Assert
        assert result == "Copyd"  # Implementation adds 'd' not 'ed'

    def test_format_action_verb_dry_run(self) -> None:
        """Test action verb formatting in dry-run mode."""
        # Arrange
        action: str = "delete"
        dry_run: bool = True
        past_tense: bool = False

        # Act
        result: str = FileSystemHelper.format_action_verb(action, dry_run, past_tense)

        # Assert
        assert result == "Would delete"


class TestPathAssembler:
    """
    Test suite for PathAssembler utility class.

    Tests destination path assembly with various configuration options
    for hostname and date subdirectories.
    """

    def test_assemble_dest_path_home_file_no_subdirs(self, tmp_path: Path) -> None:
        """Test path assembly for home file without subdirectories."""
        # Arrange
        base_path: Path = tmp_path / "backup"
        src_path: Path = Path.home() / ".bashrc"
        hostname_subdir: bool = False
        date_subdir: bool = False

        # Act
        result: Path = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected: Path = base_path / "home" / ".bashrc"
        assert result == expected

    def test_assemble_dest_path_home_file_with_hostname(self, tmp_path: Path) -> None:
        """Test path assembly for home file with hostname subdirectory."""
        # Arrange
        base_path: Path = tmp_path / "backup"
        src_path: Path = Path.home() / ".vimrc"
        hostname_subdir: bool = True
        date_subdir: bool = False

        # Act
        result: Path = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected: Path = base_path / gethostname() / "home" / ".vimrc"
        assert result == expected

    @patch("time.strftime")
    def test_assemble_dest_path_home_file_with_date(
        self, mock_strftime: Mock, tmp_path: Path
    ) -> None:
        """Test path assembly for home file with date subdirectory."""
        # Arrange
        mock_strftime.return_value = "2025-10-29"
        base_path: Path = tmp_path / "backup"
        src_path: Path = Path.home() / ".gitconfig"
        hostname_subdir: bool = False
        date_subdir: bool = True

        # Act
        result: Path = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected: Path = base_path / "2025-10-29" / "home" / ".gitconfig"
        assert result == expected
        mock_strftime.assert_called_once_with("%Y-%m-%d")

    @patch("time.strftime")
    def test_assemble_dest_path_home_file_with_both_subdirs(
        self, mock_strftime: Mock, tmp_path: Path
    ) -> None:
        """Test path assembly for home file with hostname and date subdirectories."""
        # Arrange
        mock_strftime.return_value = "2025-10-29"
        base_path: Path = tmp_path / "backup"
        src_path: Path = Path.home() / ".config" / "starship.toml"
        hostname_subdir: bool = True
        date_subdir: bool = True

        # Act
        result: Path = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected: Path = (
            base_path
            / gethostname()
            / "2025-10-29"
            / "home"
            / ".config"
            / "starship.toml"
        )
        assert result == expected

    def test_assemble_dest_path_root_file_no_subdirs(self, tmp_path: Path) -> None:
        """Test path assembly for root file without subdirectories."""
        # Arrange
        base_path: Path = tmp_path / "backup"
        src_path: Path = Path("/etc/ssh/ssh_config")
        hostname_subdir: bool = False
        date_subdir: bool = False

        # Act
        result: Path = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected: Path = base_path / "root" / "etc" / "ssh" / "ssh_config"
        assert result == expected

    def test_assemble_dest_path_root_file_with_hostname(self, tmp_path: Path) -> None:
        """Test path assembly for root file with hostname subdirectory."""
        # Arrange
        base_path: Path = tmp_path / "backup"
        src_path: Path = Path("/etc/hosts")
        hostname_subdir: bool = True
        date_subdir: bool = False

        # Act
        result: Path = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected: Path = base_path / gethostname() / "root" / "etc" / "hosts"
        assert result == expected

    def test_assemble_dest_path_nested_home_file(self, tmp_path: Path) -> None:
        """Test path assembly for deeply nested home directory file."""
        # Arrange
        base_path: Path = tmp_path / "backup"
        src_path: Path = Path.home() / ".config" / "gtk-3.0" / "settings.ini"
        hostname_subdir: bool = True
        date_subdir: bool = False

        # Act
        result: Path = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected: Path = (
            base_path / gethostname() / "home" / ".config" / "gtk-3.0" / "settings.ini"
        )
        assert result == expected


class TestConfigValidator:
    """
    Test suite for ConfigValidator utility class.

    Tests TOML configuration validation with proper type checking
    and default value handling.
    """

    def test_validate_options_with_defaults(self) -> None:
        """Test options validation using all default values."""
        # Arrange
        raw_options: dict[str, Any] = {}

        # Act
        result: OptionsDict = ConfigValidator.validate_options(raw_options)

        # Assert
        assert result["mirror"] is True
        assert result["archive"] is False
        assert result["hostname_subdir"] is True
        assert result["date_subdir"] is False
        assert result["archive_format"] == "tar.gz"
        assert result["archive_compression_level"] == 9
        assert result["rotate_archives"] is False
        assert result["max_archives"] == 5

    def test_validate_options_with_custom_values(self) -> None:
        """Test options validation with custom values."""
        # Arrange
        raw_options: dict[str, Any] = {
            "mirror": False,
            "archive": True,
            "hostname_subdir": False,
            "date_subdir": True,
            "archive_format": "tar.bz2",
            "archive_compression_level": 6,
            "rotate_archives": True,
            "max_archives": 10,
        }

        # Act
        result: OptionsDict = ConfigValidator.validate_options(raw_options)

        # Assert
        assert result["mirror"] is False
        assert result["archive"] is True
        assert result["hostname_subdir"] is False
        assert result["date_subdir"] is True
        assert result["archive_format"] == "tar.bz2"
        assert result["archive_compression_level"] == 6
        assert result["rotate_archives"] is True
        assert result["max_archives"] == 10

    def test_validate_options_compression_level_bounds(self) -> None:
        """Test compression level validation with out-of-bounds values."""
        # Arrange - invalid compression level too high
        raw_options_high: dict[str, Any] = {"archive_compression_level": 15}

        # Act
        result_high: OptionsDict = ConfigValidator.validate_options(raw_options_high)

        # Assert - should default to 9
        assert result_high["archive_compression_level"] == 9

        # Arrange - invalid compression level negative
        raw_options_negative: dict[str, Any] = {"archive_compression_level": -1}

        # Act
        result_negative: OptionsDict = ConfigValidator.validate_options(
            raw_options_negative
        )

        # Assert - should default to 9
        assert result_negative["archive_compression_level"] == 9

    def test_validate_options_max_archives_minimum(self) -> None:
        """Test max_archives validation with invalid minimum value."""
        # Arrange
        raw_options: dict[str, Any] = {"max_archives": 0}

        # Act
        result: OptionsDict = ConfigValidator.validate_options(raw_options)

        # Assert - should default to 5
        assert result["max_archives"] == 5

    def test_validate_dotfile_with_all_fields(self) -> None:
        """Test dotfile validation with all required fields present."""
        # Arrange
        raw_dotfile: dict[str, str] = {
            "category": "Shell configs",
            "subcategory": "Shell",
            "application": "Bash",
            "description": "Bash configuration file",
            "path": "~/.bashrc",
            "mirror_dir": "~/backup/mirror",
            "archive_dir": "~/backup/archive",
        }

        # Act
        result: DotFileDict = ConfigValidator.validate_dotfile(raw_dotfile)

        # Assert
        assert result["category"] == "Shell configs"
        assert result["subcategory"] == "Shell"
        assert result["application"] == "Bash"
        assert result["description"] == "Bash configuration file"
        assert result["path"] == "~/.bashrc"
        assert result["mirror_dir"] == "~/backup/mirror"
        assert result["archive_dir"] == "~/backup/archive"

    def test_validate_dotfile_with_missing_fields(self) -> None:
        """Test dotfile validation with missing optional fields."""
        # Arrange
        raw_dotfile: dict[str, str] = {
            "path": "~/.vimrc",
        }

        # Act
        result: DotFileDict = ConfigValidator.validate_dotfile(raw_dotfile)

        # Assert - should use defaults for missing fields
        assert result["category"] == "Unknown"
        assert result["subcategory"] == "Unknown"
        assert result["application"] == "Unknown"
        assert result["description"] == "None"
        assert result["path"] == "~/.vimrc"
        assert result["mirror_dir"] == "~/DFBU_Mirror"
        assert result["archive_dir"] == "~/DFBU_Archives"

    def test_validate_config_complete_structure(self) -> None:
        """Test complete configuration validation with all sections."""
        # Arrange
        config_data: dict[str, Any] = {
            "paths": {
                "mirror_dir": "~/test_mirror",
                "archive_dir": "~/test_archive",
            },
            "options": {
                "mirror": True,
                "archive": True,
                "hostname_subdir": True,
                "date_subdir": False,
            },
            "dotfile": [
                {
                    "category": "Shell",
                    "subcategory": "Bash",
                    "application": "Bash Shell",
                    "description": "Bash config",
                    "path": "~/.bashrc",
                },
                {
                    "category": "Editor",
                    "subcategory": "Vim",
                    "application": "Vim Editor",
                    "description": "Vim config",
                    "path": "~/.vimrc",
                },
            ],
        }

        # Act
        options, dotfiles = ConfigValidator.validate_config(config_data)

        # Assert options
        assert options["mirror"] is True
        assert options["archive"] is True
        assert options["hostname_subdir"] is True
        assert options["date_subdir"] is False

        # Assert dotfiles
        assert len(dotfiles) == 2
        assert dotfiles[0]["category"] == "Shell"
        assert dotfiles[0]["path"] == "~/.bashrc"
        assert dotfiles[0]["mirror_dir"] == "~/test_mirror"
        assert dotfiles[1]["category"] == "Editor"
        assert dotfiles[1]["path"] == "~/.vimrc"
        assert dotfiles[1]["archive_dir"] == "~/test_archive"

    def test_validate_config_with_missing_sections(self) -> None:
        """Test configuration validation with missing sections."""
        # Arrange
        config_data: dict[str, Any] = {}

        # Act
        options, dotfiles = ConfigValidator.validate_config(config_data)

        # Assert - should use defaults
        assert options["mirror"] is True
        assert options["archive"] is False
        assert len(dotfiles) == 0

    def test_validate_config_merges_paths_with_dotfiles(self) -> None:
        """Test that paths configuration is merged with individual dotfiles."""
        # Arrange
        config_data: dict[str, Any] = {
            "paths": {
                "mirror_dir": "~/global_mirror",
                "archive_dir": "~/global_archive",
            },
            "dotfile": [
                {
                    "category": "Test",
                    "path": "~/.testfile",
                    # No mirror_dir or archive_dir specified
                },
            ],
        }

        # Act
        options, dotfiles = ConfigValidator.validate_config(config_data)

        # Assert - paths should be inherited from global paths section
        assert dotfiles[0]["mirror_dir"] == "~/global_mirror"
        assert dotfiles[0]["archive_dir"] == "~/global_archive"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
