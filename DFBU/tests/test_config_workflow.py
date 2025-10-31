#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for DFBU Configuration and Workflow

Description:
    Comprehensive integration tests for configuration loading, sorting,
    and main workflow orchestration following pytest framework and AAA pattern.
    Tests focus on TOML parsing and workflow integration before v1.0.0.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-29-2025
Date Changed: 10-29-2025
License: MIT

Features:
    - Integration tests for TOML configuration loading
    - Integration tests for dotfiles sorting algorithm
    - Integration tests for workflow orchestration
    - Mock TOML file operations for testing
    - AAA pattern test structure for clarity
    - Pytest fixtures for configuration data

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - pytest framework for testing
    - tomllib for TOML parsing
    - unittest.mock for file operation mocking
"""

import sys
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch, mock_open

import pytest

# Add project to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common_lib"))

# Import module under test
from dfbu import (
    load_config,
    sort_dotfiles,
    DotFile,
    Options,
    DotFileDict,
    OptionsDict,
)


class TestLoadConfig:
    """
    Test suite for load_config function.

    Tests TOML configuration file loading, parsing,
    and validation with various configuration scenarios.
    """

    @pytest.fixture
    def complete_config(self) -> dict[str, Any]:
        """Create complete configuration dictionary for testing."""
        return {
            "paths": {
                "mirror_dir": "~/test_mirror",
                "archive_dir": "~/test_archive",
            },
            "options": {
                "mirror": True,
                "archive": True,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 9,
                "rotate_archives": True,
                "max_archives": 5,
            },
            "dotfile": [
                {
                    "category": "Shell configs",
                    "subcategory": "Shell",
                    "application": "Bash",
                    "description": "Bash configuration",
                    "path": "~/.bashrc",
                },
                {
                    "category": "Editor",
                    "subcategory": "Text Editor",
                    "application": "Vim",
                    "description": "Vim configuration",
                    "path": "~/.vimrc",
                },
            ],
        }

    @patch("builtins.open", new_callable=mock_open)
    @patch("tomllib.load")
    def test_load_config_returns_options_and_dotfiles(
        self, mock_toml_load: Mock, mock_file: Mock, complete_config: dict[str, Any]
    ) -> None:
        """Test that load_config returns validated options and dotfiles."""
        # Arrange
        mock_toml_load.return_value = complete_config

        # Act
        options, dotfiles = load_config()

        # Assert
        assert isinstance(options, dict)
        assert isinstance(dotfiles, list)
        assert len(dotfiles) == 2

    @patch("builtins.open", new_callable=mock_open)
    @patch("tomllib.load")
    def test_load_config_merges_paths_with_dotfiles(
        self, mock_toml_load: Mock, mock_file: Mock, complete_config: dict[str, Any]
    ) -> None:
        """Test that global paths are merged into individual dotfiles."""
        # Arrange
        mock_toml_load.return_value = complete_config

        # Act
        options, dotfiles = load_config()

        # Assert
        # Each dotfile should have mirror_dir and archive_dir from paths section
        assert all("mirror_dir" in df for df in dotfiles)
        assert all("archive_dir" in df for df in dotfiles)
        assert dotfiles[0]["mirror_dir"] == "~/test_mirror"
        assert dotfiles[0]["archive_dir"] == "~/test_archive"

    @patch("builtins.open", new_callable=mock_open)
    @patch("tomllib.load")
    def test_load_config_validates_options(
        self, mock_toml_load: Mock, mock_file: Mock, complete_config: dict[str, Any]
    ) -> None:
        """Test that options are validated with correct types."""
        # Arrange
        mock_toml_load.return_value = complete_config

        # Act
        options, dotfiles = load_config()

        # Assert
        assert options["mirror"] is True
        assert options["archive"] is True
        assert options["hostname_subdir"] is True
        assert options["archive_compression_level"] == 9
        assert options["max_archives"] == 5

    @patch("builtins.open", new_callable=mock_open)
    @patch("tomllib.load")
    def test_load_config_validates_dotfiles(
        self, mock_toml_load: Mock, mock_file: Mock, complete_config: dict[str, Any]
    ) -> None:
        """Test that dotfile entries are validated correctly."""
        # Arrange
        mock_toml_load.return_value = complete_config

        # Act
        options, dotfiles = load_config()

        # Assert
        assert dotfiles[0]["category"] == "Shell configs"
        assert dotfiles[0]["application"] == "Bash"
        assert dotfiles[0]["path"] == "~/.bashrc"
        assert dotfiles[1]["category"] == "Editor"
        assert dotfiles[1]["application"] == "Vim"

    @patch("builtins.open", new_callable=mock_open)
    @patch("tomllib.load")
    def test_load_config_with_minimal_configuration(
        self, mock_toml_load: Mock, mock_file: Mock
    ) -> None:
        """Test loading with minimal configuration using defaults."""
        # Arrange
        minimal_config: dict[str, Any] = {
            "dotfile": [
                {
                    "path": "~/.bashrc",
                }
            ]
        }
        mock_toml_load.return_value = minimal_config

        # Act
        options, dotfiles = load_config()

        # Assert
        # Options should use defaults
        assert options["mirror"] is True
        assert options["archive"] is False
        # Dotfile should have defaults for missing fields
        assert dotfiles[0]["category"] == "Unknown"
        assert dotfiles[0]["mirror_dir"] == "~/DFBU_Mirror"

    @patch("builtins.open", new_callable=mock_open)
    @patch("tomllib.load")
    def test_load_config_opens_correct_file_path(
        self, mock_toml_load: Mock, mock_file: Mock, complete_config: dict[str, Any]
    ) -> None:
        """Test that correct configuration file path is opened."""
        # Arrange
        mock_toml_load.return_value = complete_config

        # Act
        load_config()

        # Assert
        # Verify file was opened in binary mode
        mock_file.assert_called_once()
        call_args = mock_file.call_args
        # Should open CONFIG_PATH in binary read mode
        assert "rb" in str(call_args) or call_args[0][1] == "rb"


class TestSortDotfiles:
    """
    Test suite for sort_dotfiles function.

    Tests multi-level sorting by category, subcategory,
    and application name.
    """

    @pytest.fixture
    def basic_options(self) -> Options:
        """Create basic Options instance for testing."""
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

    def test_sort_by_category_ascending(self, basic_options: Options) -> None:
        """Test that dotfiles are sorted by category in ascending order."""
        # Arrange
        dotfile_dicts: list[DotFileDict] = [
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
            {
                "category": "M Category",
                "subcategory": "Sub",
                "application": "App",
                "description": "Test",
                "path": "/tmp/file3",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
        ]
        dotfiles: list[DotFile] = [DotFile(d, basic_options) for d in dotfile_dicts]

        # Act
        result: list[DotFile] = sort_dotfiles(dotfiles)

        # Assert
        assert result[0].category == "A Category"
        assert result[1].category == "M Category"
        assert result[2].category == "Z Category"

    def test_sort_by_subcategory_when_category_same(
        self, basic_options: Options
    ) -> None:
        """Test that dotfiles with same category are sorted by subcategory."""
        # Arrange
        dotfile_dicts: list[DotFileDict] = [
            {
                "category": "Same",
                "subcategory": "Z Sub",
                "application": "App",
                "description": "Test",
                "path": "/tmp/file1",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
            {
                "category": "Same",
                "subcategory": "A Sub",
                "application": "App",
                "description": "Test",
                "path": "/tmp/file2",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
        ]
        dotfiles: list[DotFile] = [DotFile(d, basic_options) for d in dotfile_dicts]

        # Act
        result: list[DotFile] = sort_dotfiles(dotfiles)

        # Assert
        assert result[0].subcategory == "A Sub"
        assert result[1].subcategory == "Z Sub"

    def test_sort_by_application_when_category_and_subcategory_same(
        self, basic_options: Options
    ) -> None:
        """Test that dotfiles are sorted by application when category/subcategory match."""
        # Arrange
        dotfile_dicts: list[DotFileDict] = [
            {
                "category": "Same",
                "subcategory": "Same",
                "application": "Z App",
                "description": "Test",
                "path": "/tmp/file1",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
            {
                "category": "Same",
                "subcategory": "Same",
                "application": "A App",
                "description": "Test",
                "path": "/tmp/file2",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
            {
                "category": "Same",
                "subcategory": "Same",
                "application": "M App",
                "description": "Test",
                "path": "/tmp/file3",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
        ]
        dotfiles: list[DotFile] = [DotFile(d, basic_options) for d in dotfile_dicts]

        # Act
        result: list[DotFile] = sort_dotfiles(dotfiles)

        # Assert
        assert result[0].application == "A App"
        assert result[1].application == "M App"
        assert result[2].application == "Z App"

    def test_sort_maintains_order_stability(self, basic_options: Options) -> None:
        """Test that sort maintains stable ordering for equal elements."""
        # Arrange
        dotfile_dicts: list[DotFileDict] = [
            {
                "category": "Same",
                "subcategory": "Same",
                "application": "Same",
                "description": "First",
                "path": "/tmp/file1",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
            {
                "category": "Same",
                "subcategory": "Same",
                "application": "Same",
                "description": "Second",
                "path": "/tmp/file2",
                "mirror_dir": "~/test",
                "archive_dir": "~/test",
            },
        ]
        dotfiles: list[DotFile] = [DotFile(d, basic_options) for d in dotfile_dicts]

        # Act
        result: list[DotFile] = sort_dotfiles(dotfiles)

        # Assert
        # Order should be maintained for equal elements
        assert result[0].description == "First"
        assert result[1].description == "Second"

    def test_sort_handles_empty_list(self) -> None:
        """Test that sorting empty list returns empty list."""
        # Arrange
        dotfiles: list[DotFile] = []

        # Act
        result: list[DotFile] = sort_dotfiles(dotfiles)

        # Assert
        assert len(result) == 0

    def test_sort_handles_single_item(self, basic_options: Options) -> None:
        """Test that sorting single item list returns same list."""
        # Arrange
        dotfile_dict: DotFileDict = {
            "category": "Test",
            "subcategory": "Test",
            "application": "Test",
            "description": "Test",
            "path": "/tmp/file",
            "mirror_dir": "~/test",
            "archive_dir": "~/test",
        }
        dotfiles: list[DotFile] = [DotFile(dotfile_dict, basic_options)]

        # Act
        result: list[DotFile] = sort_dotfiles(dotfiles)

        # Assert
        assert len(result) == 1
        assert result[0].category == "Test"


class TestWorkflowIntegration:
    """
    Test suite for complete workflow integration.

    Tests the integration of configuration loading, validation,
    DotFile creation, and sorting in a complete workflow.
    """

    @pytest.fixture
    def realistic_config(self) -> dict[str, Any]:
        """Create realistic configuration for workflow testing."""
        return {
            "paths": {
                "mirror_dir": "~/GitHub/dotfiles",
                "archive_dir": "~/Backups/dotfiles",
            },
            "options": {
                "mirror": True,
                "archive": False,
                "hostname_subdir": True,
                "date_subdir": False,
            },
            "dotfile": [
                {
                    "category": "Editor",
                    "subcategory": "Text Editor",
                    "application": "Vim",
                    "description": "Vim configuration",
                    "path": "~/.vimrc",
                },
                {
                    "category": "Shell configs",
                    "subcategory": "Shell",
                    "application": "Bash",
                    "description": "Bash configuration",
                    "path": "~/.bashrc",
                },
                {
                    "category": "Shell configs",
                    "subcategory": "Shell",
                    "application": "Fish",
                    "description": "Fish configuration",
                    "path": "~/.config/fish/config.fish",
                },
            ],
        }

    @patch("builtins.open", new_callable=mock_open)
    @patch("tomllib.load")
    def test_complete_workflow_from_load_to_sort(
        self, mock_toml_load: Mock, mock_file: Mock, realistic_config: dict[str, Any]
    ) -> None:
        """Test complete workflow from config loading through sorting."""
        # Arrange
        mock_toml_load.return_value = realistic_config

        # Act - Load configuration
        raw_options, raw_dotfiles = load_config()

        # Act - Create Options and DotFile objects
        options: Options = Options(raw_options)
        dotfiles: list[DotFile] = [DotFile(df, options) for df in raw_dotfiles]

        # Act - Sort dotfiles
        sorted_dotfiles: list[DotFile] = sort_dotfiles(dotfiles)

        # Assert - Options properly created
        assert options.mirror is True
        assert options.hostname_subdir is True

        # Assert - DotFiles properly created
        assert len(dotfiles) == 3
        assert all(isinstance(df, DotFile) for df in dotfiles)

        # Assert - Proper sorting (Shell configs before Editor)
        assert sorted_dotfiles[0].category == "Editor"
        assert sorted_dotfiles[1].category == "Shell configs"
        assert sorted_dotfiles[2].category == "Shell configs"
        # Within Shell configs, Bash before Fish
        shell_configs = [df for df in sorted_dotfiles if df.category == "Shell configs"]
        assert shell_configs[0].application == "Bash"
        assert shell_configs[1].application == "Fish"

    @patch("builtins.open", new_callable=mock_open)
    @patch("tomllib.load")
    def test_workflow_with_type_safety(
        self, mock_toml_load: Mock, mock_file: Mock, realistic_config: dict[str, Any]
    ) -> None:
        """Test that workflow maintains type safety through all stages."""
        # Arrange
        mock_toml_load.return_value = realistic_config

        # Act
        raw_options, raw_dotfiles = load_config()
        options: Options = Options(raw_options)
        dotfiles: list[DotFile] = [DotFile(df, options) for df in raw_dotfiles]
        sorted_dotfiles: list[DotFile] = sort_dotfiles(dotfiles)

        # Assert - Type consistency throughout workflow
        assert isinstance(raw_options, dict)
        assert isinstance(raw_dotfiles, list)
        assert isinstance(options, Options)
        assert all(isinstance(df, DotFile) for df in dotfiles)
        assert all(isinstance(df, DotFile) for df in sorted_dotfiles)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
