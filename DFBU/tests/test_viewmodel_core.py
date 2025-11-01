"""
Test ViewModel Core Functionality

Description:
    Comprehensive unit tests for DFBUViewModel including initialization,
    settings management, dotfile commands, and worker thread operations.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-31-2025
License: MIT
"""

import sys
from pathlib import Path

import pytest


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))

from model import DFBUModel
from viewmodel import BackupWorker, DFBUViewModel, RestoreWorker


class TestViewModelInitialization:
    """Test suite for ViewModel initialization and setup."""

    def test_viewmodel_init_with_model(self, tmp_path: Path) -> None:
        """Test ViewModel initializes correctly with model."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        # Act
        viewmodel = DFBUViewModel(model)

        # Assert
        assert viewmodel.model == model
        assert viewmodel.backup_worker is None
        assert viewmodel.restore_worker is None

    def test_viewmodel_signals_exist(self, tmp_path: Path) -> None:
        """Test ViewModel has required signal attributes."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        viewmodel = DFBUViewModel(model)

        # Act & Assert - signals should be defined
        assert hasattr(viewmodel, "config_loaded")
        assert hasattr(viewmodel, "dotfiles_updated")
        assert hasattr(viewmodel, "progress_updated")
        assert hasattr(viewmodel, "item_processed")
        assert hasattr(viewmodel, "operation_finished")


class TestViewModelSettings:
    """Test suite for ViewModel settings management."""

    def test_save_settings_stores_geometry(self, tmp_path: Path) -> None:
        """Test save_settings stores window geometry."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        viewmodel = DFBUViewModel(model)
        test_geometry = b"test_geometry_data"

        # Act
        viewmodel.save_settings(geometry=test_geometry)
        loaded = viewmodel.load_settings()

        # Assert
        assert loaded["geometry"] == test_geometry

    def test_save_settings_stores_window_state(self, tmp_path: Path) -> None:
        """Test save_settings stores window state."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        viewmodel = DFBUViewModel(model)
        test_state = b"window_state_data"

        # Act
        viewmodel.save_settings(window_state=test_state)
        loaded = viewmodel.load_settings()

        # Assert
        assert loaded["window_state"] == test_state

    def test_save_restore_settings_roundtrip(self, tmp_path: Path) -> None:
        """Test settings can be saved and restored."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        viewmodel = DFBUViewModel(model)
        test_geometry = b"geometry_12345"
        test_state = b"state_67890"

        # Act
        viewmodel.save_settings(geometry=test_geometry, window_state=test_state)
        loaded = viewmodel.load_settings()

        # Assert
        assert loaded["geometry"] == test_geometry
        assert loaded["window_state"] == test_state


class TestViewModelDotfileCommands:
    """Test suite for ViewModel dotfile management commands."""

    def test_command_add_dotfile_single_path(self, tmp_path: Path) -> None:
        """Test command_add_dotfile with single path."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        # Act
        viewmodel.command_add_dotfile(
            "TestCat", "TestSub", "TestApp", "Test description", ["~/test.txt"], True
        )

        # Assert
        assert model.get_dotfile_count() == 1
        dotfile = model.get_dotfile_by_index(0)
        assert dotfile is not None
        assert dotfile["category"] == "TestCat"
        assert dotfile["subcategory"] == "TestSub"
        assert dotfile["application"] == "TestApp"
        assert dotfile["description"] == "Test description"
        assert dotfile["paths"] == ["~/test.txt"]
        assert dotfile["enabled"] is True

    def test_command_add_dotfile_multiple_paths(self, tmp_path: Path) -> None:
        """Test command_add_dotfile with multiple paths."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)
        paths = ["~/file1.txt", "~/file2.txt", "~/file3.txt"]

        # Act
        viewmodel.command_add_dotfile(
            "Multi", "Test", "MultiApp", "Multiple paths", paths, True
        )

        # Assert
        assert model.get_dotfile_count() == 1
        dotfile = model.get_dotfile_by_index(0)
        assert dotfile is not None
        assert dotfile["paths"] == paths

    def test_command_update_dotfile_changes_fields(self, tmp_path: Path) -> None:
        """Test command_update_dotfile modifies existing dotfile."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        # Add initial dotfile
        viewmodel.command_add_dotfile(
            "Cat1", "Sub1", "App1", "Original", ["~/original.txt"], True
        )

        # Act - update the dotfile
        viewmodel.command_update_dotfile(
            0, "Cat2", "Sub2", "App2", "Updated", ["~/updated.txt"], False
        )

        # Assert
        dotfile = model.get_dotfile_by_index(0)
        assert dotfile is not None
        assert dotfile["category"] == "Cat2"
        assert dotfile["subcategory"] == "Sub2"
        assert dotfile["application"] == "App2"
        assert dotfile["description"] == "Updated"
        assert dotfile["paths"] == ["~/updated.txt"]
        assert dotfile["enabled"] is False

    def test_command_remove_dotfile_by_index(self, tmp_path: Path) -> None:
        """Test command_remove_dotfile removes correct entry."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        # Add multiple dotfiles
        viewmodel.command_add_dotfile("A", "A", "A", "First", ["~/a.txt"], True)
        viewmodel.command_add_dotfile("B", "B", "B", "Second", ["~/b.txt"], True)
        viewmodel.command_add_dotfile("C", "C", "C", "Third", ["~/c.txt"], True)

        # Act - remove middle entry
        viewmodel.command_remove_dotfile(1)

        # Assert
        assert model.get_dotfile_count() == 2
        first = model.get_dotfile_by_index(0)
        second = model.get_dotfile_by_index(1)
        assert first is not None
        assert second is not None
        assert first["category"] == "A"
        assert second["category"] == "C"

    def test_command_toggle_dotfile_enabled(self, tmp_path: Path) -> None:
        """Test command_toggle_dotfile_enabled changes status."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        viewmodel.command_add_dotfile(
            "Test", "Test", "Test", "Test", ["~/test.txt"], True
        )

        # Act - toggle enabled status
        viewmodel.command_toggle_dotfile_enabled(0)

        # Assert
        dotfile = model.get_dotfile_by_index(0)
        assert dotfile is not None
        assert dotfile["enabled"] is False

        # Act - toggle again
        viewmodel.command_toggle_dotfile_enabled(0)

        # Assert
        dotfile = model.get_dotfile_by_index(0)
        assert dotfile is not None
        assert dotfile["enabled"] is True


class TestViewModelConfigOperations:
    """Test suite for ViewModel configuration operations."""

    def test_command_load_config_success(self, tmp_path: Path) -> None:
        """Test command_load_config with valid config."""
        # Arrange
        config_path = tmp_path / "test.toml"
        config_path.write_text(
            """
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true
archive = false

[[dotfile]]
category = "Test"
subcategory = "Test"
application = "TestApp"
description = "Test dotfile"
path = "~/.testrc"
"""
        )

        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        # Act
        viewmodel.command_load_config()

        # Assert
        assert model.get_dotfile_count() == 1
        dotfile = model.get_dotfile_by_index(0)
        assert dotfile is not None
        assert dotfile["category"] == "Test"

    def test_command_save_config_creates_file(self, tmp_path: Path) -> None:
        """Test command_save_config creates config file."""
        # Arrange
        config_path = tmp_path / "new_config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        # Add a dotfile
        viewmodel.command_add_dotfile(
            "Save", "Test", "App", "Desc", ["~/save.txt"], True
        )

        # Act
        viewmodel.command_save_config()

        # Assert
        assert config_path.exists()


class TestViewModelPropertyAccess:
    """Test suite for ViewModel property accessors."""

    def test_get_dotfile_count(self, tmp_path: Path) -> None:
        """Test get_dotfile_count returns correct value."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        viewmodel = DFBUViewModel(model)

        # Act & Assert - initially empty
        assert viewmodel.get_dotfile_count() == 0

        # Add dotfiles
        viewmodel.command_add_dotfile("A", "A", "A", "A", ["~/a.txt"], True)
        viewmodel.command_add_dotfile("B", "B", "B", "B", ["~/b.txt"], True)

        # Assert - count updated
        assert viewmodel.get_dotfile_count() == 2

    def test_get_dotfile_list(self, tmp_path: Path) -> None:
        """Test get_dotfile_list returns all dotfiles."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        viewmodel = DFBUViewModel(model)
        viewmodel.command_add_dotfile("Test", "Sub", "App", "Desc", ["~/t.txt"], True)

        # Act
        dotfiles = viewmodel.get_dotfile_list()

        # Assert
        assert len(dotfiles) == 1
        assert dotfiles[0]["category"] == "Test"

    def test_get_dotfile_validation(self, tmp_path: Path) -> None:
        """Test get_dotfile_validation returns validation states."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        viewmodel = DFBUViewModel(model)
        viewmodel.command_add_dotfile("Test", "Sub", "App", "Desc", ["~/t.txt"], True)

        # Act
        validation = viewmodel.get_dotfile_validation()

        # Assert
        assert isinstance(validation, dict)
        assert 0 in validation


class TestBackupWorker:
    """Test suite for BackupWorker thread."""

    def test_backup_worker_initialization(self) -> None:
        """Test BackupWorker initializes correctly."""
        # Arrange & Act
        worker = BackupWorker()

        # Assert
        assert worker.model is None
        assert worker.mirror_mode is True
        assert worker.archive_mode is False

    def test_backup_worker_set_model(self, tmp_path: Path) -> None:
        """Test BackupWorker set_model method."""
        # Arrange
        worker = BackupWorker()
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        worker.set_model(model)

        # Assert
        assert worker.model == model

    def test_backup_worker_set_modes(self) -> None:
        """Test BackupWorker set_modes method."""
        # Arrange
        worker = BackupWorker()

        # Act
        worker.set_modes(mirror=False, archive=True)

        # Assert
        assert worker.mirror_mode is False
        assert worker.archive_mode is True


class TestRestoreWorker:
    """Test suite for RestoreWorker thread."""

    def test_restore_worker_initialization(self) -> None:
        """Test RestoreWorker initializes correctly."""
        # Arrange & Act
        worker = RestoreWorker()

        # Assert
        assert worker.model is None
        assert worker.source_directory is None

    def test_restore_worker_set_model(self, tmp_path: Path) -> None:
        """Test RestoreWorker set_model method."""
        # Arrange
        worker = RestoreWorker()
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        worker.set_model(model)

        # Assert
        assert worker.model == model

    def test_restore_worker_set_source_directory(self, tmp_path: Path) -> None:
        """Test RestoreWorker set_source_directory method."""
        # Arrange
        worker = RestoreWorker()
        source = tmp_path / "restore_source"
        source.mkdir()

        # Act
        worker.set_source_directory(source)

        # Assert
        assert worker.source_directory == source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
