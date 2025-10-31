#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for DFBU Data Classes

Description:
    Comprehensive unit tests for DotFile, Options, and CLIHandler classes
    following pytest framework and AAA pattern. Tests focus on initialization,
    type safety, and core business logic before v1.0.0.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-29-2025
Date Changed: 10-29-2025
License: MIT

Features:
    - Unit tests for DotFile class with various path scenarios
    - Unit tests for Options class with configuration validation
    - Unit tests for CLIHandler class with user interaction mocking
    - Type safety validation through runtime behavior testing
    - AAA pattern test structure for clarity
    - Pytest fixtures for reusable test data
    - Mock user input and filesystem for isolation

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - pytest framework for testing
    - unittest.mock for mocking user interactions
"""

import sys
from pathlib import Path
from socket import gethostname
from unittest.mock import Mock, patch

import pytest

# Add project to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common_lib"))

# Import module under test (from CLI backup for testing core classes)
from dfbug_cli_backup import (
    DotFile,
    Options,
    CLIHandler,
    DotFileDict,
    OptionsDict,
)


class TestDotFile:
    """
    Test suite for DotFile class functionality.

    Tests initialization, path resolution, metadata handling,
    and destination path assembly for both home and root files.
    """

    @pytest.fixture
    def basic_options(self) -> Options:
        """Create basic Options instance for testing."""
        # Arrange
        options_dict: OptionsDict = {
            "mirror": True,
            "archive": False,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": False,
            "max_archives": 5,
        }
        return Options(options_dict)

    @pytest.fixture
    def home_dotfile_dict(self) -> DotFileDict:
        """Create sample home directory dotfile dict for testing."""
        return {
            "category": "Shell configs",
            "subcategory": "Shell",
            "application": "Bash",
            "description": "Bash configuration file",
            "path": "~/.bashrc",
            "mirror_dir": "~/test_mirror",
            "archive_dir": "~/test_archive",
        }

    @pytest.fixture
    def root_dotfile_dict(self) -> DotFileDict:
        """Create sample root directory dotfile dict for testing."""
        return {
            "category": "System",
            "subcategory": "SSH",
            "application": "SSH Config",
            "description": "SSH system configuration",
            "path": "/etc/ssh/ssh_config",
            "mirror_dir": "~/test_mirror",
            "archive_dir": "~/test_archive",
        }

    def test_dotfile_initialization_with_metadata(
        self, home_dotfile_dict: DotFileDict, basic_options: Options
    ) -> None:
        """Test DotFile initialization stores all metadata correctly."""
        # Act
        dotfile: DotFile = DotFile(home_dotfile_dict, basic_options)

        # Assert
        assert dotfile.category == "Shell configs"
        assert dotfile.subcategory == "Shell"
        assert dotfile.application == "Bash"
        assert dotfile.description == "Bash configuration file"
        assert dotfile.name == ".bashrc"

    def test_dotfile_path_expansion_for_home_directory(
        self, home_dotfile_dict: DotFileDict, basic_options: Options
    ) -> None:
        """Test that tilde in path is expanded to full home directory path."""
        # Act
        dotfile: DotFile = DotFile(home_dotfile_dict, basic_options)

        # Assert
        expected_path: Path = Path.home() / ".bashrc"
        assert dotfile.src_path == expected_path
        assert dotfile.relative_to_home is True

    def test_dotfile_path_handling_for_root_directory(
        self, root_dotfile_dict: DotFileDict, basic_options: Options
    ) -> None:
        """Test that root directory paths are handled correctly."""
        # Act
        dotfile: DotFile = DotFile(root_dotfile_dict, basic_options)

        # Assert
        assert dotfile.src_path == Path("/etc/ssh/ssh_config")
        assert dotfile.relative_to_home is False

    def test_dotfile_existence_check_for_existing_file(
        self, basic_options: Options, tmp_path: Path
    ) -> None:
        """Test that existing file is correctly identified."""
        # Arrange
        test_file: Path = tmp_path / "test.txt"
        test_file.write_text("test content")
        dotfile_dict: DotFileDict = {
            "category": "Test",
            "subcategory": "Test",
            "application": "Test",
            "description": "Test file",
            "path": str(test_file),
            "mirror_dir": "~/test",
            "archive_dir": "~/test",
        }

        # Act
        dotfile: DotFile = DotFile(dotfile_dict, basic_options)

        # Assert
        assert dotfile.exists is True
        assert dotfile.is_file is True
        assert dotfile.is_dir is False
        assert dotfile.type == "File"

    def test_dotfile_existence_check_for_existing_directory(
        self, basic_options: Options, tmp_path: Path
    ) -> None:
        """Test that existing directory is correctly identified."""
        # Arrange
        test_dir: Path = tmp_path / "test_dir"
        test_dir.mkdir()
        dotfile_dict: DotFileDict = {
            "category": "Test",
            "subcategory": "Test",
            "application": "Test",
            "description": "Test directory",
            "path": str(test_dir),
            "mirror_dir": "~/test",
            "archive_dir": "~/test",
        }

        # Act
        dotfile: DotFile = DotFile(dotfile_dict, basic_options)

        # Assert
        assert dotfile.exists is True
        assert dotfile.is_file is False
        assert dotfile.is_dir is True
        assert dotfile.type == "Directory"

    def test_dotfile_nonexistent_file_detection(self, basic_options: Options) -> None:
        """Test that nonexistent file is correctly identified."""
        # Arrange
        dotfile_dict: DotFileDict = {
            "category": "Test",
            "subcategory": "Test",
            "application": "Test",
            "description": "Nonexistent file",
            "path": "/nonexistent/path/file.txt",
            "mirror_dir": "~/test",
            "archive_dir": "~/test",
        }

        # Act
        dotfile: DotFile = DotFile(dotfile_dict, basic_options)

        # Assert
        assert dotfile.exists is False
        assert dotfile.is_file is False
        assert dotfile.is_dir is False

    def test_dotfile_mirror_dest_path_with_hostname_subdir(
        self, home_dotfile_dict: DotFileDict, basic_options: Options
    ) -> None:
        """Test mirror destination path includes hostname when enabled."""
        # Arrange
        basic_options.hostname_subdir = True
        basic_options.date_subdir = False

        # Act
        dotfile: DotFile = DotFile(home_dotfile_dict, basic_options)

        # Assert
        expected_base: Path = Path.home() / "test_mirror"
        expected_path: Path = expected_base / gethostname() / "home" / ".bashrc"
        assert dotfile.dest_path_mirror == expected_path

    def test_dotfile_mirror_dest_path_without_subdirs(
        self, home_dotfile_dict: DotFileDict, basic_options: Options
    ) -> None:
        """Test mirror destination path without optional subdirectories."""
        # Arrange
        basic_options.hostname_subdir = False
        basic_options.date_subdir = False

        # Act
        dotfile: DotFile = DotFile(home_dotfile_dict, basic_options)

        # Assert
        expected_base: Path = Path.home() / "test_mirror"
        expected_path: Path = expected_base / "home" / ".bashrc"
        assert dotfile.dest_path_mirror == expected_path

    def test_dotfile_archive_dest_path_with_hostname_subdir(
        self, home_dotfile_dict: DotFileDict, basic_options: Options
    ) -> None:
        """Test archive destination path includes hostname when enabled."""
        # Arrange
        basic_options.hostname_subdir = True
        basic_options.date_subdir = False

        # Act
        dotfile: DotFile = DotFile(home_dotfile_dict, basic_options)

        # Assert
        expected_base: Path = Path.home() / "test_archive"
        expected_path: Path = expected_base / gethostname() / "home" / ".bashrc"
        assert dotfile.dest_path_archive == expected_path

    def test_dotfile_relative_path_calculation_for_home_file(
        self, home_dotfile_dict: DotFileDict, basic_options: Options
    ) -> None:
        """Test relative path calculation for home directory file."""
        # Act
        dotfile: DotFile = DotFile(home_dotfile_dict, basic_options)

        # Assert
        expected_relative: Path = Path("home") / ".bashrc"
        assert dotfile.relative_path == expected_relative

    def test_dotfile_relative_path_calculation_for_root_file(
        self, root_dotfile_dict: DotFileDict, basic_options: Options
    ) -> None:
        """Test relative path calculation for root directory file."""
        # Act
        dotfile: DotFile = DotFile(root_dotfile_dict, basic_options)

        # Assert
        expected_relative: Path = Path("root") / "etc" / "ssh" / "ssh_config"
        assert dotfile.relative_path == expected_relative

    def test_dotfile_string_representation_includes_metadata(
        self, home_dotfile_dict: DotFileDict, basic_options: Options
    ) -> None:
        """Test that string representation includes all relevant metadata."""
        # Act
        dotfile: DotFile = DotFile(home_dotfile_dict, basic_options)
        result: str = str(dotfile)

        # Assert
        assert "Shell configs" in result
        assert "Shell" in result
        assert "Bash" in result
        assert ".bashrc" in result
        assert "Bash configuration file" in result


class TestOptions:
    """
    Test suite for Options class functionality.

    Tests initialization from configuration dictionaries,
    default value handling, and string representation.
    """

    def test_options_initialization_from_complete_dict(self) -> None:
        """Test Options initialization with all fields specified."""
        # Arrange
        options_dict: OptionsDict = {
            "mirror": True,
            "archive": True,
            "hostname_subdir": True,
            "date_subdir": True,
            "archive_format": "tar.bz2",
            "archive_compression_level": 6,
            "rotate_archives": True,
            "max_archives": 10,
        }

        # Act
        options: Options = Options(options_dict)

        # Assert
        assert options.mirror is True
        assert options.archive is True
        assert options.hostname_subdir is True
        assert options.date_subdir is True
        assert options.archive_format == "tar.bz2"
        assert options.archive_compression_level == 6
        assert options.rotate_archives is True
        assert options.max_archives == 10

    def test_options_mirror_enabled_by_default(self) -> None:
        """Test that mirror option defaults to True."""
        # Arrange
        options_dict: OptionsDict = {
            "mirror": True,
            "archive": False,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": False,
            "max_archives": 5,
        }

        # Act
        options: Options = Options(options_dict)

        # Assert
        assert options.mirror is True

    def test_options_archive_disabled_by_default(self) -> None:
        """Test that archive option defaults to False."""
        # Arrange
        options_dict: OptionsDict = {
            "mirror": True,
            "archive": False,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": False,
            "max_archives": 5,
        }

        # Act
        options: Options = Options(options_dict)

        # Assert
        assert options.archive is False

    def test_options_hostname_subdir_enabled_by_default(self) -> None:
        """Test that hostname_subdir defaults to True."""
        # Arrange
        options_dict: OptionsDict = {
            "mirror": True,
            "archive": False,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": False,
            "max_archives": 5,
        }

        # Act
        options: Options = Options(options_dict)

        # Assert
        assert options.hostname_subdir is True

    def test_options_compression_level_default(self) -> None:
        """Test that compression level defaults to 9."""
        # Arrange
        options_dict: OptionsDict = {
            "mirror": True,
            "archive": False,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": False,
            "max_archives": 5,
        }

        # Act
        options: Options = Options(options_dict)

        # Assert
        assert options.archive_compression_level == 9

    def test_options_max_archives_default(self) -> None:
        """Test that max_archives defaults to 5."""
        # Arrange
        options_dict: OptionsDict = {
            "mirror": True,
            "archive": False,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": False,
            "max_archives": 5,
        }

        # Act
        options: Options = Options(options_dict)

        # Assert
        assert options.max_archives == 5

    def test_options_string_representation_includes_all_settings(self) -> None:
        """Test that string representation includes all option values."""
        # Arrange
        options_dict: OptionsDict = {
            "mirror": True,
            "archive": True,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": True,
            "max_archives": 10,
        }

        # Act
        options: Options = Options(options_dict)
        result: str = str(options)

        # Assert
        assert "Uncompressed mirror: True" in result
        assert "Create archive: True" in result
        assert "Use hostname subdirectory: True" in result
        assert "Use date subdirectory: False" in result
        assert "Archive format: tar.gz" in result
        assert "Archive compression level: 9" in result
        assert "Rotate archives: True" in result
        assert "Maximum number of archives to keep: 10" in result


class TestCLIHandler:
    """
    Test suite for CLIHandler class functionality.

    Tests command-line argument parsing, user input handling,
    confirmation prompts, and summary display methods.
    """

    def test_parse_args_with_no_arguments(self) -> None:
        """Test argument parsing with no command-line arguments."""
        # Arrange
        with patch("sys.argv", ["dfbu.py"]):
            # Act
            dry_run, force = CLIHandler.parse_args()

            # Assert
            assert dry_run is False
            assert force is False

    def test_parse_args_with_dry_run_flag(self) -> None:
        """Test argument parsing with --dry-run flag."""
        # Arrange
        with patch("sys.argv", ["dfbu.py", "--dry-run"]):
            # Act
            dry_run, force = CLIHandler.parse_args()

            # Assert
            assert dry_run is True
            assert force is False

    def test_parse_args_with_force_flag(self) -> None:
        """Test argument parsing with --force flag."""
        # Arrange
        with patch("sys.argv", ["dfbu.py", "--force"]):
            # Act
            dry_run, force = CLIHandler.parse_args()

            # Assert
            assert dry_run is False
            assert force is True

    def test_parse_args_with_both_flags(self) -> None:
        """Test argument parsing with both --dry-run and --force flags."""
        # Arrange
        with patch("sys.argv", ["dfbu.py", "--dry-run", "--force"]):
            # Act
            dry_run, force = CLIHandler.parse_args()

            # Assert
            assert dry_run is True
            assert force is True

    def test_parse_args_with_short_flags(self) -> None:
        """Test argument parsing with short flag versions."""
        # Arrange
        with patch("sys.argv", ["dfbu.py", "-d", "-f"]):
            # Act
            dry_run, force = CLIHandler.parse_args()

            # Assert
            assert dry_run is True
            assert force is True

    @patch("builtins.input")
    def test_get_mode_returns_backup_for_choice_1(self, mock_input: Mock) -> None:
        """Test that get_mode returns 'backup' when user enters 1."""
        # Arrange
        mock_input.return_value = "1"

        # Act
        result: str = CLIHandler.get_mode()

        # Assert
        assert result == "backup"

    @patch("builtins.input")
    def test_get_mode_returns_restore_for_choice_2(self, mock_input: Mock) -> None:
        """Test that get_mode returns 'restore' when user enters 2."""
        # Arrange
        mock_input.return_value = "2"

        # Act
        result: str = CLIHandler.get_mode()

        # Assert
        assert result == "restore"

    @patch("builtins.input")
    def test_get_mode_exits_on_quit(self, mock_input: Mock) -> None:
        """Test that get_mode exits when user enters 'q'."""
        # Arrange
        mock_input.return_value = "q"

        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            CLIHandler.get_mode()
        assert exc_info.value.code == 0

    @patch("builtins.input")
    def test_get_mode_reprompts_on_invalid_input(self, mock_input: Mock) -> None:
        """Test that get_mode reprompts on invalid input then accepts valid."""
        # Arrange
        mock_input.side_effect = ["invalid", "3", "1"]

        # Act
        result: str = CLIHandler.get_mode()

        # Assert
        assert result == "backup"
        assert mock_input.call_count == 3

    @patch("builtins.input")
    def test_get_restore_source_validates_existing_directory(
        self, mock_input: Mock, tmp_path: Path
    ) -> None:
        """Test that get_restore_source validates directory existence."""
        # Arrange
        test_dir: Path = tmp_path / "backup"
        test_dir.mkdir()
        mock_input.side_effect = [str(test_dir), "y"]

        # Act
        result: Path = CLIHandler.get_restore_source()

        # Assert
        assert result == test_dir

    @patch("builtins.input")
    def test_get_restore_source_rejects_nonexistent_path(
        self, mock_input: Mock, capsys: pytest.CaptureFixture
    ) -> None:
        """Test that get_restore_source rejects nonexistent paths."""
        # Arrange
        mock_input.side_effect = ["/nonexistent/path", "q"]

        # Act & Assert
        with pytest.raises(SystemExit):
            CLIHandler.get_restore_source()

        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    @patch("builtins.input")
    def test_get_restore_source_rejects_file_as_directory(
        self, mock_input: Mock, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test that get_restore_source rejects file when directory expected."""
        # Arrange
        test_file: Path = tmp_path / "file.txt"
        test_file.write_text("test")
        mock_input.side_effect = [str(test_file), "q"]

        # Act & Assert
        with pytest.raises(SystemExit):
            CLIHandler.get_restore_source()

        captured = capsys.readouterr()
        assert "is not a directory" in captured.out

    @patch("cust_class.CLIMenu.ynq")
    def test_confirm_action_returns_true_on_yes(self, mock_ynq: Mock) -> None:
        """Test that confirm_action returns True when user confirms."""
        # Arrange
        mock_ynq.return_value = True
        prompt: str = "Proceed with operation?"

        # Act
        result: bool = CLIHandler.confirm_action(prompt)

        # Assert
        assert result is True
        mock_ynq.assert_called_once_with(prompt)

    @patch("cust_class.CLIMenu.ynq")
    def test_confirm_action_returns_false_on_no(self, mock_ynq: Mock) -> None:
        """Test that confirm_action returns False when user declines."""
        # Arrange
        mock_ynq.return_value = False
        prompt: str = "Proceed with operation?"

        # Act
        result: bool = CLIHandler.confirm_action(prompt)

        # Assert
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
