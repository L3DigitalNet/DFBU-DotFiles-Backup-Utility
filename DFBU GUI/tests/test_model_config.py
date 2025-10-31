#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for DFBU Model - Configuration Management

Description:
    Comprehensive unit tests for DFBUModel configuration loading, validation,
    saving, and option management. Tests follow pytest framework and AAA pattern
    with focus on happy paths and type safety.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 10-30-2025
License: MIT

Features:
    - Unit tests for TOML configuration loading
    - Tests for configuration validation logic
    - Tests for configuration saving with rotating backups
    - Tests for option updates and path management
    - Type safety validation for configuration structures
    - AAA pattern test structure for clarity
    - Pytest fixtures for reusable test configurations

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - pytest framework for testing
    - unittest.mock for mocking filesystem operations
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import tomllib

# Add project source to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import modules under test
from model import DFBUModel, DotFileDict, OptionsDict


class TestConfigurationLoading:
    """
    Test suite for configuration file loading.

    Tests TOML loading, validation, and error handling for
    configuration files.
    """

    @pytest.fixture
    def sample_config_dict(self) -> dict:
        """Create sample configuration dictionary."""
        return {
            "title": "Test Config",
            "description": "Test configuration file",
            "paths": {
                "mirror_dir": "~/test_mirror",
                "archive_dir": "~/test_archive",
            },
            "options": {
                "mirror": True,
                "archive": False,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 9,
                "rotate_archives": False,
                "max_archives": 5,
            },
            "dotfile": [
                {
                    "category": "Shell configs",
                    "subcategory": "Shell",
                    "application": "Bash",
                    "description": "Bash configuration file",
                    "path": "~/.bashrc",
                    "enabled": True,
                },
                {
                    "category": "Editor",
                    "subcategory": "Vim",
                    "application": "Vim",
                    "description": "Vim configuration",
                    "path": "~/.vimrc",
                    "enabled": True,
                },
            ],
        }

    def test_load_config_with_valid_file(
        self, tmp_path: Path, sample_config_dict: dict
    ) -> None:
        """Test that valid configuration file loads successfully."""
        # Arrange
        config_path = tmp_path / "test-config.toml"
        import tomli_w
        with open(config_path, "wb") as f:
            tomli_w.dump(sample_config_dict, f)

        model = DFBUModel(config_path)

        # Act
        success, error_msg = model.load_config()

        # Assert
        assert success is True
        assert error_msg == ""
        assert len(model.dotfiles) == 2
        assert model.options["mirror"] is True

    def test_load_config_sets_dotfiles_list(
        self, tmp_path: Path, sample_config_dict: dict
    ) -> None:
        """Test that configuration loading populates dotfiles list."""
        # Arrange
        config_path = tmp_path / "test-config.toml"
        import tomli_w
        with open(config_path, "wb") as f:
            tomli_w.dump(sample_config_dict, f)

        model = DFBUModel(config_path)

        # Act
        model.load_config()

        # Assert
        assert len(model.dotfiles) == 2
        assert model.dotfiles[0]["category"] == "Shell configs"
        assert model.dotfiles[0]["application"] == "Bash"
        assert model.dotfiles[1]["category"] == "Editor"
        assert model.dotfiles[1]["application"] == "Vim"

    def test_load_config_sets_options(
        self, tmp_path: Path, sample_config_dict: dict
    ) -> None:
        """Test that configuration loading sets options correctly."""
        # Arrange
        config_path = tmp_path / "test-config.toml"
        import tomli_w
        with open(config_path, "wb") as f:
            tomli_w.dump(sample_config_dict, f)

        model = DFBUModel(config_path)

        # Act
        model.load_config()

        # Assert
        assert model.options["mirror"] is True
        assert model.options["archive"] is False
        assert model.options["hostname_subdir"] is True
        assert model.options["date_subdir"] is False
        assert model.options["archive_compression_level"] == 9

    def test_load_config_sets_base_directories(
        self, tmp_path: Path, sample_config_dict: dict
    ) -> None:
        """Test that configuration loading sets base directories from paths."""
        # Arrange
        config_path = tmp_path / "test-config.toml"
        import tomli_w
        with open(config_path, "wb") as f:
            tomli_w.dump(sample_config_dict, f)

        model = DFBUModel(config_path)

        # Act
        model.load_config()

        # Assert
        expected_mirror = Path.home() / "test_mirror"
        expected_archive = Path.home() / "test_archive"
        assert model.mirror_base_dir == expected_mirror
        assert model.archive_base_dir == expected_archive

    def test_load_config_merges_paths_with_dotfiles(
        self, tmp_path: Path, sample_config_dict: dict
    ) -> None:
        """Test that paths from config are merged with dotfile entries."""
        # Arrange
        config_path = tmp_path / "test-config.toml"
        import tomli_w
        with open(config_path, "wb") as f:
            tomli_w.dump(sample_config_dict, f)

        model = DFBUModel(config_path)

        # Act
        model.load_config()

        # Assert
        assert model.dotfiles[0]["mirror_dir"] == "~/test_mirror"
        assert model.dotfiles[0]["archive_dir"] == "~/test_archive"
        assert model.dotfiles[1]["mirror_dir"] == "~/test_mirror"
        assert model.dotfiles[1]["archive_dir"] == "~/test_archive"

    def test_load_config_returns_error_for_nonexistent_file(
        self, tmp_path: Path
    ) -> None:
        """Test that loading nonexistent config returns error."""
        # Arrange
        config_path = tmp_path / "nonexistent.toml"
        model = DFBUModel(config_path)

        # Act
        success, error_msg = model.load_config()

        # Assert
        assert success is False
        assert "not found" in error_msg


class TestConfigurationValidation:
    """
    Test suite for configuration validation logic.

    Tests validation of options, dotfiles, and handling of
    invalid or missing values.
    """

    @pytest.fixture
    def model(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel instance for testing."""
        config_path = tmp_path / "test-config.toml"
        return DFBUModel(config_path)

    def test_validate_options_with_defaults(self, model: DFBUModel) -> None:
        """Test options validation uses defaults for missing values."""
        # Arrange
        raw_options = {}

        # Act
        validated = model._validate_options(raw_options)

        # Assert
        assert validated["mirror"] is True
        assert validated["archive"] is False
        assert validated["hostname_subdir"] is True
        assert validated["date_subdir"] is False
        assert validated["archive_format"] == "tar.gz"
        assert validated["archive_compression_level"] == 9
        assert validated["rotate_archives"] is False
        assert validated["max_archives"] == 5

    def test_validate_options_with_custom_values(self, model: DFBUModel) -> None:
        """Test options validation preserves custom values."""
        # Arrange
        raw_options = {
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
        validated = model._validate_options(raw_options)

        # Assert
        assert validated["mirror"] is False
        assert validated["archive"] is True
        assert validated["hostname_subdir"] is False
        assert validated["date_subdir"] is True
        assert validated["archive_format"] == "tar.bz2"
        assert validated["archive_compression_level"] == 6
        assert validated["rotate_archives"] is True
        assert validated["max_archives"] == 10

    def test_validate_options_compression_level_bounds(
        self, model: DFBUModel
    ) -> None:
        """Test that invalid compression level defaults to 9."""
        # Arrange - too high
        raw_options_high = {"archive_compression_level": 15}

        # Act
        validated_high = model._validate_options(raw_options_high)

        # Assert
        assert validated_high["archive_compression_level"] == 9

        # Arrange - negative
        raw_options_neg = {"archive_compression_level": -1}

        # Act
        validated_neg = model._validate_options(raw_options_neg)

        # Assert
        assert validated_neg["archive_compression_level"] == 9

    def test_validate_options_max_archives_minimum(self, model: DFBUModel) -> None:
        """Test that max_archives less than 1 defaults to 5."""
        # Arrange
        raw_options = {"max_archives": 0}

        # Act
        validated = model._validate_options(raw_options)

        # Assert
        assert validated["max_archives"] == 5

    def test_validate_dotfile_with_all_fields(self, model: DFBUModel) -> None:
        """Test dotfile validation with complete metadata."""
        # Arrange
        raw_dotfile = {
            "category": "Shell configs",
            "subcategory": "Shell",
            "application": "Bash",
            "description": "Bash config",
            "path": "~/.bashrc",
            "mirror_dir": "~/mirror",
            "archive_dir": "~/archive",
            "enabled": True,
        }

        # Act
        validated = model._validate_dotfile(raw_dotfile)

        # Assert
        assert validated["category"] == "Shell configs"
        assert validated["subcategory"] == "Shell"
        assert validated["application"] == "Bash"
        assert validated["description"] == "Bash config"
        assert validated["path"] == "~/.bashrc"
        assert validated["mirror_dir"] == "~/mirror"
        assert validated["archive_dir"] == "~/archive"
        assert validated["enabled"] is True

    def test_validate_dotfile_with_missing_fields(self, model: DFBUModel) -> None:
        """Test dotfile validation fills in missing fields with defaults."""
        # Arrange
        raw_dotfile = {"path": "~/.vimrc"}

        # Act
        validated = model._validate_dotfile(raw_dotfile)

        # Assert
        assert validated["category"] == "Unknown"
        assert validated["subcategory"] == "Unknown"
        assert validated["application"] == "Unknown"
        assert validated["description"] == "None"
        assert validated["path"] == "~/.vimrc"
        assert validated["mirror_dir"] == "~/DFBU_Mirror"
        assert validated["archive_dir"] == "~/DFBU_Archives"
        assert validated["enabled"] is True

    def test_validate_dotfile_enabled_string_conversion(
        self, model: DFBUModel
    ) -> None:
        """Test that enabled field converts string values to boolean."""
        # Arrange - string "true"
        raw_dotfile_true = {"path": "~/.bashrc", "enabled": "true"}

        # Act
        validated_true = model._validate_dotfile(raw_dotfile_true)

        # Assert
        assert validated_true["enabled"] is True

        # Arrange - string "false"
        raw_dotfile_false = {"path": "~/.vimrc", "enabled": "false"}

        # Act
        validated_false = model._validate_dotfile(raw_dotfile_false)

        # Assert
        assert validated_false["enabled"] is False


class TestConfigurationSaving:
    """
    Test suite for configuration file saving.

    Tests saving configuration changes back to TOML file with
    proper formatting and rotating backups.
    """

    @pytest.fixture
    def model_with_config(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel with loaded configuration."""
        config_path = tmp_path / "test-config.toml"

        # Create initial config
        config_data = {
            "title": "Test Config",
            "description": "Test configuration",
            "paths": {
                "mirror_dir": "~/test_mirror",
                "archive_dir": "~/test_archive",
            },
            "options": {
                "mirror": True,
                "archive": False,
            },
            "dotfile": [
                {
                    "category": "Shell",
                    "subcategory": "Bash",
                    "application": "Bash",
                    "description": "Bash config",
                    "path": "~/.bashrc",
                    "enabled": True,
                }
            ],
        }

        import tomli_w
        with open(config_path, "wb") as f:
            tomli_w.dump(config_data, f)

        model = DFBUModel(config_path)
        model.load_config()
        return model

    def test_save_config_writes_toml_file(
        self, model_with_config: DFBUModel
    ) -> None:
        """Test that save_config writes valid TOML file."""
        # Act
        success, error_msg = model_with_config.save_config()

        # Assert
        assert success is True
        assert error_msg == ""
        assert model_with_config.config_path.exists()

    def test_save_config_preserves_dotfiles(
        self, model_with_config: DFBUModel
    ) -> None:
        """Test that saved configuration preserves dotfile entries."""
        # Act
        model_with_config.save_config()

        # Assert - reload and verify
        with open(model_with_config.config_path, "rb") as f:
            saved_config = tomllib.load(f)

        assert len(saved_config["dotfile"]) == 1
        assert saved_config["dotfile"][0]["application"] == "Bash"

    def test_save_config_preserves_options(
        self, model_with_config: DFBUModel
    ) -> None:
        """Test that saved configuration preserves options."""
        # Arrange - modify options
        model_with_config.options["archive"] = True
        model_with_config.options["rotate_archives"] = True

        # Act
        model_with_config.save_config()

        # Assert - reload and verify
        with open(model_with_config.config_path, "rb") as f:
            saved_config = tomllib.load(f)

        assert saved_config["options"]["archive"] is True
        assert saved_config["options"]["rotate_archives"] is True

    @patch("model.create_rotating_backup")
    def test_save_config_creates_rotating_backup(
        self, mock_backup, model_with_config: DFBUModel
    ) -> None:
        """Test that save_config creates rotating backup before saving."""
        # Arrange
        mock_backup.return_value = (Path("/backup/file"), True)

        # Act
        model_with_config.save_config()

        # Assert
        mock_backup.assert_called_once()


class TestOptionUpdates:
    """
    Test suite for option update operations.

    Tests updating individual configuration options and paths.
    """

    @pytest.fixture
    def model(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel instance for testing."""
        config_path = tmp_path / "test-config.toml"
        return DFBUModel(config_path)

    def test_update_option_mirror(self, model: DFBUModel) -> None:
        """Test updating mirror option."""
        # Act
        result = model.update_option("mirror", False)

        # Assert
        assert result is True
        assert model.options["mirror"] is False

    def test_update_option_archive(self, model: DFBUModel) -> None:
        """Test updating archive option."""
        # Act
        result = model.update_option("archive", True)

        # Assert
        assert result is True
        assert model.options["archive"] is True

    def test_update_option_compression_level(self, model: DFBUModel) -> None:
        """Test updating compression level option."""
        # Act
        result = model.update_option("archive_compression_level", 6)

        # Assert
        assert result is True
        assert model.options["archive_compression_level"] == 6

    def test_update_option_max_archives(self, model: DFBUModel) -> None:
        """Test updating max archives option."""
        # Act
        result = model.update_option("max_archives", 10)

        # Assert
        assert result is True
        assert model.options["max_archives"] == 10

    def test_update_option_invalid_key(self, model: DFBUModel) -> None:
        """Test that invalid option key returns False."""
        # Act
        result = model.update_option("invalid_key", "value")

        # Assert
        assert result is False

    def test_update_path_mirror_dir(self, model: DFBUModel) -> None:
        """Test updating mirror directory path."""
        # Act
        result = model.update_path("mirror_dir", "~/new_mirror")

        # Assert
        assert result is True
        assert model.mirror_base_dir == Path.home() / "new_mirror"

    def test_update_path_archive_dir(self, model: DFBUModel) -> None:
        """Test updating archive directory path."""
        # Act
        result = model.update_path("archive_dir", "~/new_archive")

        # Assert
        assert result is True
        assert model.archive_base_dir == Path.home() / "new_archive"

    def test_update_path_invalid_type(self, model: DFBUModel) -> None:
        """Test that invalid path type returns False."""
        # Act
        result = model.update_path("invalid_path", "~/path")

        # Assert
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
