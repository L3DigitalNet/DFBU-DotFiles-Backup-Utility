#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for DFBU Model - Dotfile Management

Description:
    Comprehensive unit tests for DFBUModel dotfile management operations
    including add, update, remove, toggle, and validation. Tests follow
    pytest framework and AAA pattern with focus on happy paths.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 10-30-2025
License: MIT

Features:
    - Unit tests for dotfile addition and removal
    - Tests for dotfile updates and toggling enabled status
    - Tests for dotfile validation and size calculation
    - Type safety validation for dotfile structures
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

import pytest

# Add project source to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import modules under test
from model import DFBUModel


class TestDotfileAddition:
    """
    Test suite for adding dotfile entries.

    Tests dotfile addition with various metadata configurations.
    """

    @pytest.fixture
    def model(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel instance for testing."""
        config_path = tmp_path / "test-config.toml"
        model = DFBUModel(config_path)
        model.mirror_base_dir = Path.home() / "test_mirror"
        model.archive_base_dir = Path.home() / "test_archive"
        return model

    def test_add_dotfile_increases_count(self, model: DFBUModel) -> None:
        """Test that adding dotfile increases dotfile count."""
        # Arrange
        initial_count = model.get_dotfile_count()

        # Act
        success = model.add_dotfile(
            "Shell configs",
            "Shell",
            "Bash",
            "Bash configuration",
            "~/.bashrc",
            True,
        )

        # Assert
        assert success is True
        assert model.get_dotfile_count() == initial_count + 1

    def test_add_dotfile_stores_metadata(self, model: DFBUModel) -> None:
        """Test that added dotfile stores all metadata correctly."""
        # Act
        model.add_dotfile(
            "Editor",
            "Vim",
            "Vim Editor",
            "Vim configuration file",
            "~/.vimrc",
            True,
        )

        # Assert
        dotfile = model.get_dotfile_by_index(0)
        assert dotfile is not None
        assert dotfile["category"] == "Editor"
        assert dotfile["subcategory"] == "Vim"
        assert dotfile["application"] == "Vim Editor"
        assert dotfile["description"] == "Vim configuration file"
        assert dotfile["path"] == "~/.vimrc"
        assert dotfile["enabled"] is True

    def test_add_dotfile_inherits_paths(self, model: DFBUModel) -> None:
        """Test that added dotfile inherits mirror and archive paths."""
        # Act
        model.add_dotfile(
            "Test",
            "Test",
            "Test App",
            "Test file",
            "~/test.txt",
            True,
        )

        # Assert
        dotfile = model.get_dotfile_by_index(0)
        assert dotfile is not None
        assert "test_mirror" in dotfile["mirror_dir"]
        assert "test_archive" in dotfile["archive_dir"]

    def test_add_multiple_dotfiles(self, model: DFBUModel) -> None:
        """Test adding multiple dotfile entries."""
        # Act
        model.add_dotfile("Cat1", "Sub1", "App1", "Desc1", "~/file1", True)
        model.add_dotfile("Cat2", "Sub2", "App2", "Desc2", "~/file2", True)
        model.add_dotfile("Cat3", "Sub3", "App3", "Desc3", "~/file3", True)

        # Assert
        assert model.get_dotfile_count() == 3

    def test_add_dotfile_with_disabled_status(self, model: DFBUModel) -> None:
        """Test adding dotfile with enabled=False."""
        # Act
        model.add_dotfile(
            "Test",
            "Test",
            "Test App",
            "Test file",
            "~/test.txt",
            False,
        )

        # Assert
        dotfile = model.get_dotfile_by_index(0)
        assert dotfile is not None
        assert dotfile["enabled"] is False


class TestDotfileUpdate:
    """
    Test suite for updating dotfile entries.

    Tests dotfile metadata updates and validation.
    """

    @pytest.fixture
    def model_with_dotfile(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel with an existing dotfile."""
        config_path = tmp_path / "test-config.toml"
        model = DFBUModel(config_path)
        model.mirror_base_dir = Path.home() / "test_mirror"
        model.archive_base_dir = Path.home() / "test_archive"

        # Add initial dotfile
        model.add_dotfile(
            "Original Category",
            "Original Sub",
            "Original App",
            "Original Desc",
            "~/original.txt",
            True,
        )
        return model

    def test_update_dotfile_changes_metadata(
        self, model_with_dotfile: DFBUModel
    ) -> None:
        """Test that update_dotfile changes all metadata fields."""
        # Act
        success = model_with_dotfile.update_dotfile(
            0,
            "New Category",
            "New Sub",
            "New App",
            "New Desc",
            "~/new.txt",
            False,
        )

        # Assert
        assert success is True
        dotfile = model_with_dotfile.get_dotfile_by_index(0)
        assert dotfile is not None
        assert dotfile["category"] == "New Category"
        assert dotfile["subcategory"] == "New Sub"
        assert dotfile["application"] == "New App"
        assert dotfile["description"] == "New Desc"
        assert dotfile["path"] == "~/new.txt"
        assert dotfile["enabled"] is False

    def test_update_dotfile_preserves_paths(
        self, model_with_dotfile: DFBUModel
    ) -> None:
        """Test that update_dotfile preserves mirror and archive paths."""
        # Arrange
        original_dotfile = model_with_dotfile.get_dotfile_by_index(0)
        original_mirror = original_dotfile["mirror_dir"]
        original_archive = original_dotfile["archive_dir"]

        # Act
        model_with_dotfile.update_dotfile(
            0,
            "Updated",
            "Updated",
            "Updated",
            "Updated",
            "~/updated.txt",
            True,
        )

        # Assert
        updated_dotfile = model_with_dotfile.get_dotfile_by_index(0)
        assert updated_dotfile["mirror_dir"] == original_mirror
        assert updated_dotfile["archive_dir"] == original_archive

    def test_update_dotfile_invalid_index(
        self, model_with_dotfile: DFBUModel
    ) -> None:
        """Test that updating invalid index returns False."""
        # Act
        success = model_with_dotfile.update_dotfile(
            999,  # Invalid index
            "Cat",
            "Sub",
            "App",
            "Desc",
            "~/file",
            True,
        )

        # Assert
        assert success is False

    def test_update_dotfile_count_unchanged(
        self, model_with_dotfile: DFBUModel
    ) -> None:
        """Test that update doesn't change dotfile count."""
        # Arrange
        initial_count = model_with_dotfile.get_dotfile_count()

        # Act
        model_with_dotfile.update_dotfile(
            0,
            "Updated",
            "Updated",
            "Updated",
            "Updated",
            "~/updated.txt",
            True,
        )

        # Assert
        assert model_with_dotfile.get_dotfile_count() == initial_count


class TestDotfileRemoval:
    """
    Test suite for removing dotfile entries.

    Tests dotfile removal and list management.
    """

    @pytest.fixture
    def model_with_dotfiles(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel with multiple dotfiles."""
        config_path = tmp_path / "test-config.toml"
        model = DFBUModel(config_path)
        model.mirror_base_dir = Path.home() / "test_mirror"
        model.archive_base_dir = Path.home() / "test_archive"

        # Add multiple dotfiles
        model.add_dotfile("Cat1", "Sub1", "App1", "Desc1", "~/file1", True)
        model.add_dotfile("Cat2", "Sub2", "App2", "Desc2", "~/file2", True)
        model.add_dotfile("Cat3", "Sub3", "App3", "Desc3", "~/file3", True)
        return model

    def test_remove_dotfile_decreases_count(
        self, model_with_dotfiles: DFBUModel
    ) -> None:
        """Test that removing dotfile decreases count."""
        # Arrange
        initial_count = model_with_dotfiles.get_dotfile_count()

        # Act
        success = model_with_dotfiles.remove_dotfile(1)

        # Assert
        assert success is True
        assert model_with_dotfiles.get_dotfile_count() == initial_count - 1

    def test_remove_dotfile_removes_correct_entry(
        self, model_with_dotfiles: DFBUModel
    ) -> None:
        """Test that removing dotfile removes correct entry."""
        # Act
        model_with_dotfiles.remove_dotfile(1)  # Remove "App2"

        # Assert
        assert model_with_dotfiles.get_dotfile_count() == 2
        # Verify remaining dotfiles
        dotfile0 = model_with_dotfiles.get_dotfile_by_index(0)
        dotfile1 = model_with_dotfiles.get_dotfile_by_index(1)
        assert dotfile0["application"] == "App1"
        assert dotfile1["application"] == "App3"

    def test_remove_dotfile_invalid_index(
        self, model_with_dotfiles: DFBUModel
    ) -> None:
        """Test that removing invalid index returns False."""
        # Act
        success = model_with_dotfiles.remove_dotfile(999)

        # Assert
        assert success is False

    def test_remove_first_dotfile(self, model_with_dotfiles: DFBUModel) -> None:
        """Test removing first dotfile in list."""
        # Act
        success = model_with_dotfiles.remove_dotfile(0)

        # Assert
        assert success is True
        assert model_with_dotfiles.get_dotfile_count() == 2
        first_dotfile = model_with_dotfiles.get_dotfile_by_index(0)
        assert first_dotfile["application"] == "App2"

    def test_remove_last_dotfile(self, model_with_dotfiles: DFBUModel) -> None:
        """Test removing last dotfile in list."""
        # Act
        success = model_with_dotfiles.remove_dotfile(2)

        # Assert
        assert success is True
        assert model_with_dotfiles.get_dotfile_count() == 2


class TestDotfileToggle:
    """
    Test suite for toggling dotfile enabled status.

    Tests enabled/disabled state toggling.
    """

    @pytest.fixture
    def model_with_dotfile(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel with a dotfile."""
        config_path = tmp_path / "test-config.toml"
        model = DFBUModel(config_path)
        model.add_dotfile("Cat", "Sub", "App", "Desc", "~/file", True)
        return model

    def test_toggle_enabled_to_disabled(self, model_with_dotfile: DFBUModel) -> None:
        """Test toggling enabled dotfile to disabled."""
        # Act
        new_status = model_with_dotfile.toggle_dotfile_enabled(0)

        # Assert
        assert new_status is False
        dotfile = model_with_dotfile.get_dotfile_by_index(0)
        assert dotfile["enabled"] is False

    def test_toggle_disabled_to_enabled(self, model_with_dotfile: DFBUModel) -> None:
        """Test toggling disabled dotfile to enabled."""
        # Arrange
        model_with_dotfile.toggle_dotfile_enabled(0)  # Make disabled

        # Act
        new_status = model_with_dotfile.toggle_dotfile_enabled(0)

        # Assert
        assert new_status is True
        dotfile = model_with_dotfile.get_dotfile_by_index(0)
        assert dotfile["enabled"] is True

    def test_toggle_multiple_times(self, model_with_dotfile: DFBUModel) -> None:
        """Test toggling dotfile multiple times."""
        # Act & Assert
        assert model_with_dotfile.toggle_dotfile_enabled(0) is False
        assert model_with_dotfile.toggle_dotfile_enabled(0) is True
        assert model_with_dotfile.toggle_dotfile_enabled(0) is False
        assert model_with_dotfile.toggle_dotfile_enabled(0) is True


class TestDotfileValidation:
    """
    Test suite for dotfile path validation.

    Tests existence checking and type detection for dotfiles.
    """

    @pytest.fixture
    def model_with_test_files(self, tmp_path: Path) -> tuple[DFBUModel, Path]:
        """Create a DFBUModel with test files."""
        config_path = tmp_path / "test-config.toml"
        model = DFBUModel(config_path)

        # Create test files
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # Add dotfiles for test file, test dir, and nonexistent
        model.add_dotfile("Test", "File", "TestFile", "Test file", str(test_file), True)
        model.add_dotfile("Test", "Dir", "TestDir", "Test dir", str(test_dir), True)
        model.add_dotfile("Test", "None", "Nonexist", "Nonexistent", "/nonexistent/path", True)

        return model, tmp_path

    def test_validate_dotfile_paths_existing_file(
        self, model_with_test_files: tuple[DFBUModel, Path]
    ) -> None:
        """Test validation detects existing file."""
        # Arrange
        model, _ = model_with_test_files

        # Act
        validation = model.validate_dotfile_paths()

        # Assert
        exists, is_dir, type_str = validation[0]
        assert exists is True
        assert is_dir is False
        assert type_str == "File"

    def test_validate_dotfile_paths_existing_directory(
        self, model_with_test_files: tuple[DFBUModel, Path]
    ) -> None:
        """Test validation detects existing directory."""
        # Arrange
        model, _ = model_with_test_files

        # Act
        validation = model.validate_dotfile_paths()

        # Assert
        exists, is_dir, type_str = validation[1]
        assert exists is True
        assert is_dir is True
        assert type_str == "Directory"

    def test_validate_dotfile_paths_nonexistent(
        self, model_with_test_files: tuple[DFBUModel, Path]
    ) -> None:
        """Test validation detects nonexistent path."""
        # Arrange
        model, _ = model_with_test_files

        # Act
        validation = model.validate_dotfile_paths()

        # Assert
        exists, is_dir, type_str = validation[2]
        assert exists is False
        assert is_dir is False


class TestDotfileSizeCalculation:
    """
    Test suite for dotfile size calculation.

    Tests size calculation for files and directories.
    """

    @pytest.fixture
    def model_with_sized_files(self, tmp_path: Path) -> tuple[DFBUModel, Path]:
        """Create a DFBUModel with files of known sizes."""
        config_path = tmp_path / "test-config.toml"
        model = DFBUModel(config_path)

        # Create test file with known size
        test_file = tmp_path / "test.txt"
        test_file.write_text("x" * 1000)  # 1000 bytes

        # Create test directory with multiple files
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("x" * 500)
        (test_dir / "file2.txt").write_text("x" * 300)

        # Add dotfiles
        model.add_dotfile("Test", "File", "TestFile", "Test file", str(test_file), True)
        model.add_dotfile("Test", "Dir", "TestDir", "Test dir", str(test_dir), True)
        model.add_dotfile("Test", "None", "Nonexist", "Nonexistent", "/nonexistent", True)

        return model, tmp_path

    def test_calculate_path_size_for_file(
        self, model_with_sized_files: tuple[DFBUModel, Path]
    ) -> None:
        """Test size calculation for single file."""
        # Arrange
        model, tmp_path = model_with_sized_files
        test_file = tmp_path / "test.txt"

        # Act
        size = model.calculate_path_size(test_file)

        # Assert
        assert size == 1000

    def test_calculate_path_size_for_directory(
        self, model_with_sized_files: tuple[DFBUModel, Path]
    ) -> None:
        """Test size calculation for directory."""
        # Arrange
        model, tmp_path = model_with_sized_files
        test_dir = tmp_path / "test_dir"

        # Act
        size = model.calculate_path_size(test_dir)

        # Assert
        assert size == 800  # 500 + 300

    def test_calculate_path_size_for_nonexistent(
        self, model_with_sized_files: tuple[DFBUModel, Path]
    ) -> None:
        """Test size calculation for nonexistent path returns zero."""
        # Arrange
        model, _ = model_with_sized_files

        # Act
        size = model.calculate_path_size(Path("/nonexistent"))

        # Assert
        assert size == 0

    def test_get_dotfile_sizes_returns_all_sizes(
        self, model_with_sized_files: tuple[DFBUModel, Path]
    ) -> None:
        """Test get_dotfile_sizes returns sizes for all dotfiles."""
        # Arrange
        model, _ = model_with_sized_files

        # Act
        sizes = model.get_dotfile_sizes()

        # Assert
        assert len(sizes) == 3
        assert sizes[0] == 1000  # file
        assert sizes[1] == 800   # directory
        assert sizes[2] == 0     # nonexistent


class TestDotfileAccessors:
    """
    Test suite for dotfile accessor methods.

    Tests getting dotfiles by index and retrieving dotfile count.
    """

    @pytest.fixture
    def model_with_dotfiles(self, tmp_path: Path) -> DFBUModel:
        """Create a DFBUModel with multiple dotfiles."""
        config_path = tmp_path / "test-config.toml"
        model = DFBUModel(config_path)
        model.add_dotfile("Cat1", "Sub1", "App1", "Desc1", "~/file1", True)
        model.add_dotfile("Cat2", "Sub2", "App2", "Desc2", "~/file2", True)
        model.add_dotfile("Cat3", "Sub3", "App3", "Desc3", "~/file3", True)
        return model

    def test_get_dotfile_by_index_valid_index(
        self, model_with_dotfiles: DFBUModel
    ) -> None:
        """Test getting dotfile by valid index."""
        # Act
        dotfile = model_with_dotfiles.get_dotfile_by_index(1)

        # Assert
        assert dotfile is not None
        assert dotfile["application"] == "App2"

    def test_get_dotfile_by_index_first(
        self, model_with_dotfiles: DFBUModel
    ) -> None:
        """Test getting first dotfile."""
        # Act
        dotfile = model_with_dotfiles.get_dotfile_by_index(0)

        # Assert
        assert dotfile is not None
        assert dotfile["application"] == "App1"

    def test_get_dotfile_by_index_last(
        self, model_with_dotfiles: DFBUModel
    ) -> None:
        """Test getting last dotfile."""
        # Act
        dotfile = model_with_dotfiles.get_dotfile_by_index(2)

        # Assert
        assert dotfile is not None
        assert dotfile["application"] == "App3"

    def test_get_dotfile_by_index_invalid_index(
        self, model_with_dotfiles: DFBUModel
    ) -> None:
        """Test getting dotfile with invalid index returns None."""
        # Act
        dotfile = model_with_dotfiles.get_dotfile_by_index(999)

        # Assert
        assert dotfile is None

    def test_get_dotfile_count(self, model_with_dotfiles: DFBUModel) -> None:
        """Test getting dotfile count."""
        # Act
        count = model_with_dotfiles.get_dotfile_count()

        # Assert
        assert count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
