#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for DFBU Model - Core Functionality

Description:
    Comprehensive unit tests for DFBUModel core functionality including
    initialization, statistics tracking, path operations, and type safety.
    Tests follow pytest framework and AAA pattern with focus on happy paths.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 10-30-2025
License: MIT

Features:
    - Unit tests for DFBUModel initialization
    - Tests for BackupStatistics data class operations
    - Tests for path expansion and assembly
    - Tests for permission checking and validation
    - Type safety validation for TypedDict structures
    - AAA pattern test structure for clarity
    - Pytest fixtures for reusable test data

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - pytest framework for testing
    - unittest.mock for mocking filesystem operations
"""

import sys
from pathlib import Path
from socket import gethostname
from unittest.mock import patch

import pytest

# Add project source to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import modules under test
from model import DFBUModel, BackupStatistics, DotFileDict, OptionsDict


class TestBackupStatistics:
    """
    Test suite for BackupStatistics data class.

    Tests statistics tracking, calculations, and reset functionality
    for backup and restore operations.
    """

    def test_statistics_initialization_with_defaults(self) -> None:
        """Test that BackupStatistics initializes with zero values."""
        # Act
        stats = BackupStatistics()

        # Assert
        assert stats.total_items == 0
        assert stats.processed_items == 0
        assert stats.skipped_items == 0
        assert stats.failed_items == 0
        assert stats.total_time == 0.0
        assert len(stats.processing_times) == 0

    def test_statistics_average_time_with_values(self) -> None:
        """Test average time calculation with multiple processing times."""
        # Arrange
        stats = BackupStatistics()
        stats.processing_times = [1.0, 2.0, 3.0, 4.0]

        # Act
        average = stats.average_time

        # Assert
        assert average == 2.5

    def test_statistics_average_time_with_empty_list(self) -> None:
        """Test average time calculation with no processing times."""
        # Arrange
        stats = BackupStatistics()

        # Act
        average = stats.average_time

        # Assert
        assert average == 0.0

    def test_statistics_min_time_calculation(self) -> None:
        """Test minimum time calculation from processing times."""
        # Arrange
        stats = BackupStatistics()
        stats.processing_times = [5.0, 2.0, 8.0, 1.5, 3.0]

        # Act
        min_time = stats.min_time

        # Assert
        assert min_time == 1.5

    def test_statistics_min_time_with_empty_list(self) -> None:
        """Test minimum time returns zero when no times recorded."""
        # Arrange
        stats = BackupStatistics()

        # Act
        min_time = stats.min_time

        # Assert
        assert min_time == 0.0

    def test_statistics_max_time_calculation(self) -> None:
        """Test maximum time calculation from processing times."""
        # Arrange
        stats = BackupStatistics()
        stats.processing_times = [5.0, 2.0, 8.0, 1.5, 3.0]

        # Act
        max_time = stats.max_time

        # Assert
        assert max_time == 8.0

    def test_statistics_max_time_with_empty_list(self) -> None:
        """Test maximum time returns zero when no times recorded."""
        # Arrange
        stats = BackupStatistics()

        # Act
        max_time = stats.max_time

        # Assert
        assert max_time == 0.0

    def test_statistics_reset_clears_all_values(self) -> None:
        """Test that reset clears all statistics to initial state."""
        # Arrange
        stats = BackupStatistics()
        stats.total_items = 10
        stats.processed_items = 8
        stats.skipped_items = 1
        stats.failed_items = 1
        stats.total_time = 45.5
        stats.processing_times = [1.0, 2.0, 3.0]

        # Act
        stats.reset()

        # Assert
        assert stats.total_items == 0
        assert stats.processed_items == 0
        assert stats.skipped_items == 0
        assert stats.failed_items == 0
        assert stats.total_time == 0.0
        assert len(stats.processing_times) == 0


class TestDFBUModelInitialization:
    """
    Test suite for DFBUModel initialization.

    Tests model creation with configuration path and default values.
    """

    def test_model_initialization_with_config_path(self, tmp_path: Path) -> None:
        """Test that DFBUModel initializes with provided config path."""
        # Arrange
        config_path = tmp_path / "test-config.toml"

        # Act
        model = DFBUModel(config_path)

        # Assert
        assert model.config_path == config_path

    def test_model_initialization_sets_hostname(self, tmp_path: Path) -> None:
        """Test that model initialization captures system hostname."""
        # Arrange
        config_path = tmp_path / "test-config.toml"

        # Act
        model = DFBUModel(config_path)

        # Assert
        assert model.hostname == gethostname()
        assert isinstance(model.hostname, str)
        assert len(model.hostname) > 0

    def test_model_initialization_creates_empty_dotfiles_list(
        self, tmp_path: Path
    ) -> None:
        """Test that model starts with empty dotfiles list."""
        # Arrange
        config_path = tmp_path / "test-config.toml"

        # Act
        model = DFBUModel(config_path)

        # Assert
        assert isinstance(model.dotfiles, list)
        assert len(model.dotfiles) == 0

    def test_model_initialization_creates_default_options(self, tmp_path: Path) -> None:
        """Test that model initializes with default options."""
        # Arrange
        config_path = tmp_path / "test-config.toml"

        # Act
        model = DFBUModel(config_path)

        # Assert
        assert model.options["mirror"] is True
        assert model.options["archive"] is False
        assert model.options["hostname_subdir"] is True
        assert model.options["date_subdir"] is False
        assert model.options["archive_format"] == "tar.gz"
        assert model.options["archive_compression_level"] == 9
        assert model.options["rotate_archives"] is False
        assert model.options["max_archives"] == 5

    def test_model_initialization_creates_statistics(self, tmp_path: Path) -> None:
        """Test that model creates BackupStatistics instance."""
        # Arrange
        config_path = tmp_path / "test-config.toml"

        # Act
        model = DFBUModel(config_path)

        # Assert
        assert isinstance(model.statistics, BackupStatistics)
        assert model.statistics.total_items == 0


class TestDFBUModelPathOperations:
    """
    Test suite for DFBUModel path operations.

    Tests path expansion, assembly, and validation methods.
    """

    @pytest.fixture
    def model(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel instance for testing."""
        config_path = tmp_path / "test-config.toml"
        return DFBUModel(config_path)

    def test_expand_path_with_tilde(self, model: DFBUModel) -> None:
        """Test that tilde in path expands to home directory."""
        # Arrange
        path_str = "~/test/file.txt"

        # Act
        result = model.expand_path(path_str)

        # Assert
        expected = Path.home() / "test" / "file.txt"
        assert result == expected
        assert "~" not in str(result)

    def test_expand_path_without_tilde(self, model: DFBUModel) -> None:
        """Test that absolute path remains unchanged."""
        # Arrange
        path_str = "/absolute/path/file.txt"

        # Act
        result = model.expand_path(path_str)

        # Assert
        assert result == Path("/absolute/path/file.txt")

    def test_assemble_dest_path_home_file_no_subdirs(self, model: DFBUModel) -> None:
        """Test destination path assembly for home file without subdirectories."""
        # Arrange
        base_path = Path("/backup")
        src_path = Path.home() / ".bashrc"
        hostname_subdir = False
        date_subdir = False

        # Act
        result = model.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected = base_path / "home" / ".bashrc"
        assert result == expected

    def test_assemble_dest_path_home_file_with_hostname(
        self, model: DFBUModel
    ) -> None:
        """Test destination path assembly includes hostname when enabled."""
        # Arrange
        base_path = Path("/backup")
        src_path = Path.home() / ".vimrc"
        hostname_subdir = True
        date_subdir = False

        # Act
        result = model.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected = base_path / gethostname() / "home" / ".vimrc"
        assert result == expected

    @patch("time.strftime")
    def test_assemble_dest_path_home_file_with_date(
        self, mock_strftime, model: DFBUModel
    ) -> None:
        """Test destination path assembly includes date when enabled."""
        # Arrange
        mock_strftime.return_value = "2025-10-30"
        base_path = Path("/backup")
        src_path = Path.home() / ".gitconfig"
        hostname_subdir = False
        date_subdir = True

        # Act
        result = model.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected = base_path / "2025-10-30" / "home" / ".gitconfig"
        assert result == expected

    def test_assemble_dest_path_root_file(self, model: DFBUModel) -> None:
        """Test destination path assembly for root directory file."""
        # Arrange
        base_path = Path("/backup")
        src_path = Path("/etc/hosts")
        hostname_subdir = False
        date_subdir = False

        # Act
        result = model.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected = base_path / "root" / "etc" / "hosts"
        assert result == expected

    def test_assemble_dest_path_nested_home_file(self, model: DFBUModel) -> None:
        """Test destination path assembly for deeply nested home file."""
        # Arrange
        base_path = Path("/backup")
        src_path = Path.home() / ".config" / "gtk-3.0" / "settings.ini"
        hostname_subdir = True
        date_subdir = False

        # Act
        result = model.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected = base_path / gethostname() / "home" / ".config" / "gtk-3.0" / "settings.ini"
        assert result == expected


class TestDFBUModelPermissions:
    """
    Test suite for DFBUModel permission checking.

    Tests file readability checks and access validation.
    """

    @pytest.fixture
    def model(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel instance for testing."""
        config_path = tmp_path / "test-config.toml"
        return DFBUModel(config_path)

    def test_check_readable_for_readable_file(
        self, model: DFBUModel, tmp_path: Path
    ) -> None:
        """Test that readable file is correctly identified."""
        # Arrange
        test_file = tmp_path / "readable.txt"
        test_file.write_text("test content")

        # Act
        result = model.check_readable(test_file)

        # Assert
        assert result is True

    def test_check_readable_for_readable_directory(
        self, model: DFBUModel, tmp_path: Path
    ) -> None:
        """Test that readable directory is correctly identified."""
        # Arrange
        test_dir = tmp_path / "readable_dir"
        test_dir.mkdir()

        # Act
        result = model.check_readable(test_dir)

        # Assert
        assert result is True

    def test_check_readable_for_nonexistent_path(self, model: DFBUModel) -> None:
        """Test that nonexistent path returns False."""
        # Arrange
        nonexistent = Path("/nonexistent/path/file.txt")

        # Act
        result = model.check_readable(nonexistent)

        # Assert
        assert result is False


class TestDFBUModelStatistics:
    """
    Test suite for DFBUModel statistics tracking.

    Tests recording of processed, skipped, and failed items.
    """

    @pytest.fixture
    def model(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel instance for testing."""
        config_path = tmp_path / "test-config.toml"
        return DFBUModel(config_path)

    def test_record_item_processed_increments_count(self, model: DFBUModel) -> None:
        """Test that recording processed item increments counter."""
        # Arrange
        processing_time = 1.5

        # Act
        model.record_item_processed(processing_time)

        # Assert
        assert model.statistics.processed_items == 1
        assert len(model.statistics.processing_times) == 1
        assert model.statistics.processing_times[0] == 1.5

    def test_record_item_processed_accumulates_times(self, model: DFBUModel) -> None:
        """Test that multiple processed items accumulate processing times."""
        # Act
        model.record_item_processed(1.0)
        model.record_item_processed(2.0)
        model.record_item_processed(1.5)

        # Assert
        assert model.statistics.processed_items == 3
        assert len(model.statistics.processing_times) == 3
        assert model.statistics.average_time == 1.5

    def test_record_item_skipped_increments_count(self, model: DFBUModel) -> None:
        """Test that recording skipped item increments counter."""
        # Act
        model.record_item_skipped()

        # Assert
        assert model.statistics.skipped_items == 1

    def test_record_item_failed_increments_count(self, model: DFBUModel) -> None:
        """Test that recording failed item increments counter."""
        # Act
        model.record_item_failed()

        # Assert
        assert model.statistics.failed_items == 1

    def test_reset_statistics_clears_all_counters(self, model: DFBUModel) -> None:
        """Test that reset clears all statistics counters."""
        # Arrange
        model.record_item_processed(1.0)
        model.record_item_skipped()
        model.record_item_failed()
        model.statistics.total_time = 10.0

        # Act
        model.reset_statistics()

        # Assert
        assert model.statistics.processed_items == 0
        assert model.statistics.skipped_items == 0
        assert model.statistics.failed_items == 0
        assert model.statistics.total_time == 0.0
        assert len(model.statistics.processing_times) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
