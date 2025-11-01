"""
Test Configuration Validation Module

Description:
    Unit tests for ConfigValidator class validating TOML configuration
    structure, options validation, and dotfile entry validation.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-31-2025
License: MIT
"""

import sys
from pathlib import Path


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dfbu import ConfigValidator


class TestConfigValidator:
    """Test suite for ConfigValidator class."""

    def test_validate_options_with_defaults(self) -> None:
        """Test options validation with missing values uses defaults."""
        # Arrange
        raw_options = {}

        # Act
        result = ConfigValidator.validate_options(raw_options)

        # Assert
        assert result["mirror"] is True
        assert result["archive"] is False
        assert result["hostname_subdir"] is True
        assert result["date_subdir"] is False
        assert result["archive_format"] == "tar.gz"
        assert result["archive_compression_level"] == 9
        assert result["rotate_archives"] is False
        assert result["max_archives"] == 5

    def test_validate_options_with_valid_values(self) -> None:
        """Test options validation with all valid custom values."""
        # Arrange
        raw_options = {
            "mirror": False,
            "archive": True,
            "hostname_subdir": False,
            "date_subdir": True,
            "archive_format": "tar.gz",
            "archive_compression_level": 5,
            "rotate_archives": True,
            "max_archives": 10,
        }

        # Act
        result = ConfigValidator.validate_options(raw_options)

        # Assert
        assert result["mirror"] is False
        assert result["archive"] is True
        assert result["hostname_subdir"] is False
        assert result["date_subdir"] is True
        assert result["archive_format"] == "tar.gz"
        assert result["archive_compression_level"] == 5
        assert result["rotate_archives"] is True
        assert result["max_archives"] == 10

    def test_validate_options_compression_level_out_of_range(self) -> None:
        """Test compression level outside 0-9 range defaults to 9."""
        # Arrange - Test upper bound
        raw_options_high = {"archive_compression_level": 15}

        # Act
        result_high = ConfigValidator.validate_options(raw_options_high)

        # Assert
        assert result_high["archive_compression_level"] == 9

        # Arrange - Test lower bound
        raw_options_low = {"archive_compression_level": -5}

        # Act
        result_low = ConfigValidator.validate_options(raw_options_low)

        # Assert
        assert result_low["archive_compression_level"] == 9

    def test_validate_options_compression_level_invalid_type(self) -> None:
        """Test compression level with invalid type defaults to 9."""
        # Arrange
        raw_options = {"archive_compression_level": "invalid"}

        # Act
        result = ConfigValidator.validate_options(raw_options)

        # Assert
        assert result["archive_compression_level"] == 9

    def test_validate_options_max_archives_below_minimum(self) -> None:
        """Test max_archives below 1 defaults to 5."""
        # Arrange
        raw_options = {"max_archives": 0}

        # Act
        result = ConfigValidator.validate_options(raw_options)

        # Assert
        assert result["max_archives"] == 5

    def test_validate_options_max_archives_invalid_type(self) -> None:
        """Test max_archives with invalid type defaults to 5."""
        # Arrange
        raw_options = {"max_archives": "many"}

        # Act
        result = ConfigValidator.validate_options(raw_options)

        # Assert
        assert result["max_archives"] == 5

    def test_validate_dotfile_with_all_fields(self) -> None:
        """Test dotfile validation with all fields present."""
        # Arrange
        raw_dotfile = {
            "category": "Shell",
            "subcategory": "Bash",
            "application": "Bash",
            "description": "Bash configuration",
            "paths": ["~/.bashrc"],  # Updated to use paths list
            "mirror_dir": "~/backup/mirror",
            "archive_dir": "~/backup/archive",
        }

        # Act
        result = ConfigValidator.validate_dotfile(raw_dotfile)

        # Assert
        assert result["category"] == "Shell"
        assert result["subcategory"] == "Bash"
        assert result["application"] == "Bash"
        assert result["description"] == "Bash configuration"
        assert result["paths"] == ["~/.bashrc"]  # Updated to check paths list
        assert result["mirror_dir"] == "~/backup/mirror"
        assert result["archive_dir"] == "~/backup/archive"

    def test_validate_dotfile_with_missing_fields(self) -> None:
        """Test dotfile validation applies defaults for missing fields."""
        # Arrange
        raw_dotfile = {}

        # Act
        result = ConfigValidator.validate_dotfile(raw_dotfile)

        # Assert
        assert result["category"] == "Unknown"
        assert result["subcategory"] == "Unknown"
        assert result["application"] == "Unknown"
        assert result["description"] == "None"
        # Empty paths list when no path provided
        assert result["paths"] == [""]  # Updated to check paths list with empty string
        assert result["mirror_dir"] == "~/DFBU_Mirror"
        assert result["archive_dir"] == "~/DFBU_Archives"

    def test_validate_dotfile_partial_fields(self) -> None:
        """Test dotfile validation with subset of fields."""
        # Arrange
        raw_dotfile = {
            "category": "Shell",
            "paths": ["~/.bashrc"],  # Updated to use paths list
        }

        # Act
        result = ConfigValidator.validate_dotfile(raw_dotfile)

        # Assert - Specified fields preserved
        assert result["category"] == "Shell"
        assert result["paths"] == ["~/.bashrc"]  # Updated to check paths list
        # Missing fields use defaults
        assert result["subcategory"] == "Unknown"
        assert result["application"] == "Unknown"
        assert result["description"] == "None"

    def test_validate_config_complete_structure(self) -> None:
        """Test complete config validation with paths, options, and dotfiles."""
        # Arrange
        config_data = {
            "paths": {
                "mirror_dir": "~/test/mirror",
                "archive_dir": "~/test/archive",
            },
            "options": {
                "mirror": True,
                "archive": True,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_compression_level": 6,
                "max_archives": 3,
            },
            "dotfile": [
                {
                    "category": "Shell",
                    "subcategory": "Bash",
                    "application": "Bash",
                    "description": "Bash config",
                    "paths": ["~/.bashrc"],  # Updated to use paths list
                },
                {
                    "category": "Editor",
                    "subcategory": "Vim",
                    "application": "Vim",
                    "description": "Vim config",
                    "paths": ["~/.vimrc"],  # Updated to use paths list
                },
            ],
        }

        # Act
        options, dotfiles = ConfigValidator.validate_config(config_data)

        # Assert options
        assert options["mirror"] is True
        assert options["archive"] is True
        assert options["archive_compression_level"] == 6
        assert options["max_archives"] == 3

        # Assert dotfiles count
        assert len(dotfiles) == 2

        # Assert first dotfile merged with paths
        assert dotfiles[0]["category"] == "Shell"
        assert dotfiles[0]["paths"] == ["~/.bashrc"]  # Updated to check paths list
        assert dotfiles[0]["mirror_dir"] == "~/test/mirror"
        assert dotfiles[0]["archive_dir"] == "~/test/archive"

        # Assert second dotfile
        assert dotfiles[1]["category"] == "Editor"
        assert dotfiles[1]["paths"] == ["~/.vimrc"]  # Updated to check paths list

    def test_validate_config_missing_sections(self) -> None:
        """Test config validation handles missing sections gracefully."""
        # Arrange - Empty config
        config_data = {}

        # Act
        options, dotfiles = ConfigValidator.validate_config(config_data)

        # Assert - Should return defaults
        assert options["mirror"] is True
        assert options["archive"] is False
        assert len(dotfiles) == 0

    def test_validate_config_empty_dotfiles_list(self) -> None:
        """Test config validation with empty dotfiles list."""
        # Arrange
        config_data = {
            "paths": {"mirror_dir": "~/mirror", "archive_dir": "~/archive"},
            "options": {"mirror": False},
            "dotfile": [],
        }

        # Act
        options, dotfiles = ConfigValidator.validate_config(config_data)

        # Assert
        assert options["mirror"] is False
        assert len(dotfiles) == 0

    def test_validate_options_boolean_type_conversion(self) -> None:
        """Test options validation converts various types to boolean."""
        # Arrange - Test integer values
        raw_options = {
            "mirror": 1,
            "archive": 0,
            "hostname_subdir": 1,
        }

        # Act
        result = ConfigValidator.validate_options(raw_options)

        # Assert
        assert result["mirror"] is True
        assert result["archive"] is False
        assert result["hostname_subdir"] is True
