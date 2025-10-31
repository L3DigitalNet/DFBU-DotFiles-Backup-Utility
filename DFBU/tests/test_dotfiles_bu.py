#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Dotfiles Backup Utility

Description:
    Comprehensive test suite for dfbu.py providing unit tests for all
    major components including DotFile class, Options class, configuration
    loading, sorting, and file operations. Uses pytest framework with mock
    objects to test file system operations without affecting the actual system.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-27-2025
Date Changed: 10-27-2025
Version: 0.2.0.dev1
License: MIT

Features:
    - Comprehensive DotFile class testing with various path scenarios
    - Options class validation with different configuration combinations
    - Configuration loading and parsing tests with mock TOML files
    - Sorting algorithm validation for dotfiles organization
    - File operation tests using temporary directories and mock objects
    - Integration tests for main workflow components
    - Error handling validation (when implemented in v1.0.0)

Note:
    Tests are designed for Linux environments and use pytest fixtures for
    consistent test setup and teardown. All file operations are mocked or
    use temporary directories to avoid affecting the actual file system.
"""

import pytest
import tempfile
import sys
import importlib.util
import re
from pathlib import Path
from socket import gethostname
from unittest.mock import Mock, patch, mock_open
from typing import Dict

# Add the project directory to Python path for imports
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(PROJECT_DIR.parent / "common_lib"))

# Import the module under test using importlib to handle the hyphen in filename
spec = importlib.util.spec_from_file_location("dotfiles_bu", PROJECT_DIR / "dfbu.py")
if spec is not None and spec.loader is not None:
    dotfiles_bu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dotfiles_bu)

    # Import specific classes and functions
    DotFile = dotfiles_bu.DotFile
    Options = dotfiles_bu.Options
    load_config = dotfiles_bu.load_config
    sort_dotfiles = dotfiles_bu.sort_dotfiles
    summarize_backup_actions = dotfiles_bu.summarize_backup_actions
    copy_files_backup = dotfiles_bu.copy_files_backup
else:
    raise ImportError("Could not load dotfiles_bu module")


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


class TestDotFile:
    """Test suite for DotFile class functionality."""

    @pytest.fixture
    def mock_options(self) -> Options:
        """Create mock Options object for testing."""
        return Options(
            {
                "mirror": True,
                "archive": False,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 9,
                "rotate_archives": False,
                "max_archives": 5,
            }
        )

    @pytest.fixture
    def sample_dotfile_dict(self) -> Dict[str, str]:
        """Create sample dotfile dictionary for testing."""
        return {
            "category": "Shell configs",
            "subcategory": "Shell",
            "application": "Bash",
            "description": "Bash shell configuration",
            "path": "~/.bashrc",
            "mirror_dir": "~/test_mirror",
            "archive_dir": "~/test_archive",
        }

    @pytest.fixture
    def system_dotfile_dict(self) -> Dict[str, str]:
        """Create sample system dotfile dictionary for testing."""
        return {
            "category": "System",
            "subcategory": "SSH",
            "application": "SSH Config",
            "description": "SSH client configuration",
            "path": "/etc/ssh/ssh_config",
            "mirror_dir": "~/test_mirror",
            "archive_dir": "~/test_archive",
        }

    def test_dotfile_initialization_home_path(
        self, sample_dotfile_dict: Dict[str, str], mock_options: Options
    ) -> None:
        """Test DotFile initialization with home directory path."""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            sample_dotfile_dict["path"] = str(temp_path)

            dotfile = DotFile(sample_dotfile_dict, mock_options)

            assert dotfile.category == "Shell configs"
            assert dotfile.subcategory == "Shell"
            assert dotfile.application == "Bash"
            assert dotfile.description == "Bash shell configuration"
            assert dotfile.src_path == temp_path
            assert dotfile.name == temp_path.name
            assert dotfile.exists is True
            assert dotfile.is_file is True
            assert dotfile.is_dir is False
            assert dotfile.type == "File"

            # Clean up
            temp_path.unlink()

    def test_dotfile_initialization_missing_file(
        self, sample_dotfile_dict: Dict[str, str], mock_options: Options
    ) -> None:
        """Test DotFile initialization with non-existent file."""
        sample_dotfile_dict["path"] = "/non/existent/file"

        dotfile = DotFile(sample_dotfile_dict, mock_options)

        assert dotfile.exists is False
        assert dotfile.is_file is False
        assert dotfile.is_dir is False
        assert dotfile.type == "File"

    def test_dotfile_initialization_directory(
        self, sample_dotfile_dict: Dict[str, str], mock_options: Options
    ) -> None:
        """Test DotFile initialization with directory path."""
        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            sample_dotfile_dict["path"] = temp_dir

            dotfile = DotFile(sample_dotfile_dict, mock_options)

            assert dotfile.exists is True
            assert dotfile.is_file is False
            assert dotfile.is_dir is True
            assert dotfile.type == "Directory"

    def test_validate_dotfile_missing_fields(self, mock_options: Options) -> None:
        """Test dotfile validation with missing fields."""
        incomplete_dict = {"category": "Test", "path": "~/.testfile"}

        dotfile = DotFile(incomplete_dict, mock_options)

        assert dotfile.subcategory == ""
        assert dotfile.application == ""
        assert dotfile.description == "None"

    def test_convert_path_with_tilde(
        self, sample_dotfile_dict: Dict[str, str], mock_options: Options
    ) -> None:
        """Test path conversion with tilde expansion."""
        sample_dotfile_dict["path"] = "~/.testfile"

        dotfile = DotFile(sample_dotfile_dict, mock_options)

        expected_path = Path.home() / ".testfile"
        assert dotfile.src_path == expected_path

    def test_convert_path_absolute(
        self, sample_dotfile_dict: Dict[str, str], mock_options: Options
    ) -> None:
        """Test path conversion with absolute path."""
        sample_dotfile_dict["path"] = "/absolute/path/file"

        dotfile = DotFile(sample_dotfile_dict, mock_options)

        assert dotfile.src_path == Path("/absolute/path/file")

    def test_mirror_dest_path_hostname_subdir(
        self, sample_dotfile_dict: Dict[str, str], mock_options: Options
    ) -> None:
        """Test mirror destination path with hostname subdirectory."""
        sample_dotfile_dict["path"] = "~/.testfile"
        mock_options.hostname_subdir = True
        mock_options.date_subdir = False

        dotfile = DotFile(sample_dotfile_dict, mock_options)

        expected_base = Path("~/test_mirror").expanduser()
        expected_path = expected_base / gethostname() / "home" / ".testfile"
        assert dotfile.dest_path_mirror == expected_path

    def test_mirror_dest_path_system_file(
        self, system_dotfile_dict: Dict[str, str], mock_options: Options
    ) -> None:
        """Test mirror destination path for system files."""
        system_dotfile_dict["path"] = "/etc/ssh/ssh_config"
        mock_options.hostname_subdir = True
        mock_options.date_subdir = False

        dotfile = DotFile(system_dotfile_dict, mock_options)

        expected_base = Path("~/test_mirror").expanduser()
        expected_path = (
            expected_base / gethostname() / "root" / "etc" / "ssh" / "ssh_config"
        )
        assert dotfile.dest_path_mirror == expected_path

    @patch("time.strftime")
    def test_mirror_dest_path_date_subdir(
        self,
        mock_strftime: Mock,
        sample_dotfile_dict: Dict[str, str],
        mock_options: Options,
    ) -> None:
        """Test mirror destination path with date subdirectory."""
        mock_strftime.return_value = "2025-10-27"
        sample_dotfile_dict["path"] = "~/.testfile"
        mock_options.hostname_subdir = False
        mock_options.date_subdir = True

        dotfile = DotFile(sample_dotfile_dict, mock_options)

        expected_base = Path("~/test_mirror").expanduser()
        expected_path = expected_base / "2025-10-27" / "home" / ".testfile"
        assert dotfile.dest_path_mirror == expected_path

    def test_dotfile_string_representation(
        self, sample_dotfile_dict: Dict[str, str], mock_options: Options
    ) -> None:
        """Test DotFile string representation."""
        sample_dotfile_dict["path"] = "/tmp/testfile"

        dotfile = DotFile(sample_dotfile_dict, mock_options)

        str_repr = str(dotfile)
        assert "testfile" in str_repr
        assert "Shell configs" in str_repr
        assert "Shell" in str_repr
        assert "Bash" in str_repr
        assert "Bash shell configuration" in str_repr


class TestOptions:
    """Test suite for Options class functionality."""

    def test_options_default_values(self) -> None:
        """Test Options initialization with default values."""
        options = Options({})

        assert options.mirror is True
        assert options.archive is False
        assert options.hostname_subdir is True
        assert options.date_subdir is False
        assert options.archive_format == "tar.gz"
        assert options.archive_compression_level == 9
        assert options.rotate_archives is False
        assert options.max_archives == 5

    def test_options_custom_values(self) -> None:
        """Test Options initialization with custom values."""
        custom_options = {
            "mirror": False,
            "archive": True,
            "hostname_subdir": False,
            "date_subdir": True,
            "archive_format": "zip",
            "archive_compression_level": 6,
            "rotate_archives": True,
            "max_archives": 10,
        }

        options = Options(custom_options)

        assert options.mirror is False
        assert options.archive is True
        assert options.hostname_subdir is False
        assert options.date_subdir is True
        assert options.archive_format == "zip"
        assert options.archive_compression_level == 6
        assert options.rotate_archives is True
        assert options.max_archives == 10

    def test_options_string_representation(self) -> None:
        """Test Options string representation."""
        options = Options({"archive": True})

        str_repr = str(options)
        assert "Uncompressed mirror: True" in str_repr
        assert "Create archive: True" in str_repr
        assert "Use hostname subdirectory: True" in str_repr


class TestConfigLoading:
    """Test suite for configuration loading functionality."""

    @patch("builtins.open", new_callable=mock_open)
    @patch("tomllib.load")
    def test_load_config_success(
        self, mock_toml_load: Mock, mock_file_open: Mock
    ) -> None:
        """Test successful configuration loading."""
        mock_config_data = {
            "paths": {"mirror_dir": "~/test_mirror", "archive_dir": "~/test_archive"},
            "options": {"mirror": True, "archive": False},
            "dotfile": [
                {
                    "category": "Test",
                    "subcategory": "Test",
                    "application": "Test App",
                    "description": "Test description",
                    "path": "~/.testfile",
                }
            ],
        }

        mock_toml_load.return_value = mock_config_data

        raw_options, raw_dotfiles = load_config()

        assert raw_options == {"mirror": True, "archive": False}
        assert len(raw_dotfiles) == 1
        assert raw_dotfiles[0]["category"] == "Test"
        assert raw_dotfiles[0]["mirror_dir"] == "~/test_mirror"
        assert raw_dotfiles[0]["archive_dir"] == "~/test_archive"


class TestSortingFunctionality:
    """Test suite for dotfiles sorting functionality."""

    @pytest.fixture
    def mock_options(self) -> Options:
        """Create mock Options object for testing."""
        return Options({})

    def test_sort_dotfiles_by_category(self, mock_options: Options) -> None:
        """Test dotfiles sorting by category."""
        dotfiles_data = [
            {
                "category": "Z Category",
                "subcategory": "Sub",
                "application": "App",
                "description": "Test",
                "path": "/tmp/file1",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
            {
                "category": "A Category",
                "subcategory": "Sub",
                "application": "App",
                "description": "Test",
                "path": "/tmp/file2",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
        ]

        dotfiles = [DotFile(df, mock_options) for df in dotfiles_data]
        sorted_dotfiles = sort_dotfiles(dotfiles)

        assert sorted_dotfiles[0].category == "A Category"
        assert sorted_dotfiles[1].category == "Z Category"

    def test_sort_dotfiles_by_subcategory(self, mock_options: Options) -> None:
        """Test dotfiles sorting by subcategory."""
        dotfiles_data = [
            {
                "category": "Same Category",
                "subcategory": "Z Sub",
                "application": "App",
                "description": "Test",
                "path": "/tmp/file1",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
            {
                "category": "Same Category",
                "subcategory": "A Sub",
                "application": "App",
                "description": "Test",
                "path": "/tmp/file2",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
        ]

        dotfiles = [DotFile(df, mock_options) for df in dotfiles_data]
        sorted_dotfiles = sort_dotfiles(dotfiles)

        assert sorted_dotfiles[0].subcategory == "A Sub"
        assert sorted_dotfiles[1].subcategory == "Z Sub"

    def test_sort_dotfiles_by_application(self, mock_options: Options) -> None:
        """Test dotfiles sorting by application."""
        dotfiles_data = [
            {
                "category": "Same Category",
                "subcategory": "Same Sub",
                "application": "Z App",
                "description": "Test",
                "path": "/tmp/file1",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
            {
                "category": "Same Category",
                "subcategory": "Same Sub",
                "application": "A App",
                "description": "Test",
                "path": "/tmp/file2",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
        ]

        dotfiles = [DotFile(df, mock_options) for df in dotfiles_data]
        sorted_dotfiles = sort_dotfiles(dotfiles)

        assert sorted_dotfiles[0].application == "A App"
        assert sorted_dotfiles[1].application == "Z App"


class TestSummarizeBackupActions:
    """Test suite for summarize_backup_actions functionality."""

    @pytest.fixture
    def mock_options(self) -> Options:
        """Create mock Options object for testing."""
        return Options({"mirror": True, "archive": False})

    def test_summarize_actions_with_existing_files(
        self, mock_options: Options, capsys
    ) -> None:
        """Test summarize_actions with existing files."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)

            dotfile_data = {
                "category": "Test",
                "subcategory": "Test",
                "application": "Test App",
                "description": "Test description",
                "path": str(temp_path),
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            }

            dotfile = DotFile(dotfile_data, mock_options)
            dotfiles = [dotfile]

            summarize_backup_actions(dotfiles, mock_options)

            captured = capsys.readouterr()
            # Remove ANSI color codes for easier testing
            clean_output = strip_ansi_codes(captured.out)
            assert "All items located on system" in clean_output
            assert "Items to copy: 1" in clean_output
            assert "Items to mirror: 1" in clean_output

            # Clean up
            temp_path.unlink()

    def test_summarize_actions_with_missing_files(
        self, mock_options: Options, capsys
    ) -> None:
        """Test summarize_actions with missing files."""
        dotfile_data = {
            "category": "Test",
            "subcategory": "Test",
            "application": "Test App",
            "description": "Test description",
            "path": "/non/existent/file",
            "mirror_dir": "~/test",
            "archive_dir": "~/test",
        }

        dotfile = DotFile(dotfile_data, mock_options)
        dotfiles = [dotfile]

        summarize_backup_actions(dotfiles, mock_options)

        captured = capsys.readouterr()
        # Remove ANSI color codes for easier testing
        clean_output = strip_ansi_codes(captured.out)
        assert "does not exist on this system" in clean_output
        assert "Items to skip: 1" in clean_output


class TestCopyFilesBackup:
    """Test suite for copy_files_backup functionality."""

    @pytest.fixture
    def mock_options(self) -> Options:
        """Create mock Options object for testing."""
        return Options({"mirror": True, "archive": False})

    def test_copy_files_dry_run(
        self, mock_options: Options, capsys, monkeypatch
    ) -> None:
        """Test copy_files in dry run mode."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = Path(temp_file.name)

            dotfile_data = {
                "category": "Test",
                "subcategory": "Test",
                "application": "Test App",
                "description": "Test description",
                "path": str(temp_path),
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            }

            dotfile = DotFile(dotfile_data, mock_options)
            dotfiles = [dotfile]

            # Patch the DRY_RUN constant to True
            monkeypatch.setattr(dotfiles_bu, "DRY_RUN", True)

            copy_files_backup(dotfiles, mock_options)

            captured = capsys.readouterr()
            # Remove ANSI color codes for easier testing
            clean_output = strip_ansi_codes(captured.out)
            assert "[DRY RUN]" in clean_output
            assert "Would copy:" in clean_output

            # Clean up
            temp_path.unlink()

    def test_copy_files_actual_copy(self, mock_options: Options, monkeypatch) -> None:
        """Test copy_files with actual file copying."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create source file
            source_file = Path(temp_dir) / "source.txt"
            source_file.write_text("test content")

            # Create destination directory
            dest_dir = Path(temp_dir) / "dest"
            dest_dir.mkdir()

            dotfile_data = {
                "category": "Test",
                "subcategory": "Test",
                "application": "Test App",
                "description": "Test description",
                "path": str(source_file),
                "mirror_dir": str(dest_dir),
                "archive_dir": str(dest_dir),
            }

            dotfile = DotFile(dotfile_data, mock_options)
            dotfiles = [dotfile]

            # Patch the DRY_RUN constant to False and mock Path.copy
            monkeypatch.setattr(dotfiles_bu, "DRY_RUN", False)

            # Mock the Path.copy method since Python 3.14 isn't available
            with patch.object(Path, "copy") as mock_copy:
                copy_files_backup(dotfiles, mock_options)

                # Verify copy was called
                mock_copy.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
