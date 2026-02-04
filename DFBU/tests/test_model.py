"""
Test Model Module

Description:
    Unit tests for DFBUModel business logic including configuration loading,
    dotfile management, file operations, and backup/restore functionality.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-31-2025
Date Changed: 10-31-2025
License: MIT
"""

from pathlib import Path

from gui.model import DFBUModel


class TestDFBUModelInitialization:
    """Test suite for DFBUModel initialization."""

    def test_model_initialization(self, tmp_path: Path) -> None:
        """Test model initializes with correct default values."""
        # Arrange
        config_path = tmp_path / "config.toml"

        # Act
        model = DFBUModel(config_path)

        # Assert
        assert model.config_path == config_path
        assert model.hostname != ""
        assert len(model.dotfiles) == 0
        assert model.statistics.total_items == 0

    def test_model_default_options(self, tmp_path: Path) -> None:
        """Test model has correct default options."""
        # Arrange & Act
        model = DFBUModel(tmp_path / "config.toml")

        # Assert
        assert model.options["mirror"] is True
        assert model.options["archive"] is False
        assert model.options["hostname_subdir"] is True
        assert model.options["date_subdir"] is False
        assert model.options["archive_compression_level"] == 9
        assert model.options["max_archives"] == 5


class TestDFBUModelConfigManagement:
    """Test suite for configuration loading and saving."""

    def test_load_config_file_not_found(self, tmp_path: Path) -> None:
        """Test loading nonexistent config file returns error."""
        # Arrange
        model = DFBUModel(tmp_path / "nonexistent.toml")

        # Act
        success, error_message = model.load_config()

        # Assert
        assert success is False
        assert "not found" in error_message.lower()

    def test_load_config_invalid_toml(self, tmp_path: Path) -> None:
        """Test loading invalid TOML format returns error."""
        # Arrange
        config_path = tmp_path / "invalid.toml"
        config_path.write_text("invalid toml ][[ content")
        model = DFBUModel(config_path)

        # Act
        success, error_message = model.load_config()

        # Assert
        assert success is False
        assert "toml" in error_message.lower()

    def test_load_config_valid_minimal(self, tmp_path: Path) -> None:
        """Test loading minimal valid config succeeds."""
        # Arrange - create YAML config directory structure
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # settings.yaml
        (config_dir / "settings.yaml").write_text("""
paths:
  mirror_dir: ~/test_mirror
  archive_dir: ~/test_archive
  restore_backup_dir: ~/.local/share/dfbu/restore-backups

options:
  mirror: true
  archive: false
  hostname_subdir: true
  date_subdir: false
  archive_format: tar.gz
  archive_compression_level: 9
  rotate_archives: true
  max_archives: 5
  pre_restore_backup: true
  max_restore_backups: 5
  verify_after_backup: false
  hash_verification: false
""")

        # dotfiles.yaml
        (config_dir / "dotfiles.yaml").write_text("""
TestApp:
  description: Test file
  path: ~/test.txt
  tags: Test
""")

        # session.yaml
        (config_dir / "session.yaml").write_text("""
excluded: []
""")

        model = DFBUModel(config_dir)

        # Act
        success, error_message = model.load_config()

        # Assert
        assert success is True
        assert error_message == ""
        assert len(model.dotfiles) == 1
        assert model.dotfiles[0]["application"] == "TestApp"

    def test_save_config_creates_file(self, tmp_path: Path) -> None:
        """Test saving config creates valid YAML files."""
        # Arrange - create config directory
        config_dir = tmp_path / "new_config"
        config_dir.mkdir()
        model = DFBUModel(config_dir)
        model.add_dotfile(
            category="Shell",
            application="Bash",
            description="Bash config",
            paths=["~/.bashrc"],
            enabled=True,
        )

        # Act
        success, error_message = model.save_config()

        # Assert
        assert success is True
        assert error_message == ""
        # Check dotfiles.yaml was created
        dotfiles_path = config_dir / "dotfiles.yaml"
        assert dotfiles_path.exists()
        content = dotfiles_path.read_text()
        assert "Bash" in content
        assert "Bash config" in content


class TestDFBUModelDotfileManagement:
    """Test suite for dotfile add/update/remove operations."""

    def test_add_dotfile(self, tmp_path: Path) -> None:
        """Test adding a new dotfile entry."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        success = model.add_dotfile(
            category="Editor",
            application="Vim",
            description="Vim configuration",
            paths=["~/.vimrc"],
            enabled=True,
        )

        # Assert
        assert success is True
        assert len(model.dotfiles) == 1
        assert model.dotfiles[0]["application"] == "Vim"
        assert model.dotfiles[0]["paths"] == ["~/.vimrc"]
        assert model.dotfiles[0]["enabled"] is True

    def test_add_multiple_dotfiles(self, tmp_path: Path) -> None:
        """Test adding multiple dotfile entries."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        model.add_dotfile("Cat1", "App1", "Desc1", ["~/file1"], True)
        model.add_dotfile("Cat2", "App2", "Desc2", ["~/file2"], False)
        model.add_dotfile("Cat3", "App3", "Desc3", ["~/file3"], True)

        # Assert
        assert len(model.dotfiles) == 3
        assert model.dotfiles[0]["application"] == "App1"
        assert model.dotfiles[1]["application"] == "App2"
        assert model.dotfiles[2]["application"] == "App3"

    def test_update_dotfile_valid_index(self, tmp_path: Path) -> None:
        """Test updating existing dotfile entry."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.add_dotfile("Old", "OldApp", "Old desc", ["~/old"], True)

        # Act
        success = model.update_dotfile(
            0,
            category="New",
            application="NewApp",
            description="New description",
            paths=["~/new"],
            enabled=False,
        )

        # Assert
        assert success is True
        assert model.dotfiles[0]["category"] == "New"
        assert model.dotfiles[0]["application"] == "NewApp"
        assert model.dotfiles[0]["paths"] == ["~/new"]
        assert model.dotfiles[0]["enabled"] is False

    def test_update_dotfile_invalid_index(self, tmp_path: Path) -> None:
        """Test updating with invalid index returns False."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.add_dotfile("Cat", "App", "Desc", ["~/file"], True)

        # Act
        success = model.update_dotfile(99, "New", "New", "New", ["~/new"], True)

        # Assert
        assert success is False
        # Original should be unchanged
        assert model.dotfiles[0]["application"] == "App"

    def test_remove_dotfile_valid_index(self, tmp_path: Path) -> None:
        """Test removing dotfile entry by valid index."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.add_dotfile("Cat1", "App1", "Desc1", ["~/file1"], True)
        model.add_dotfile("Cat2", "App2", "Desc2", ["~/file2"], True)
        model.add_dotfile("Cat3", "App3", "Desc3", ["~/file3"], True)

        # Act
        success = model.remove_dotfile(1)  # Remove middle item

        # Assert
        assert success is True
        assert len(model.dotfiles) == 2
        assert model.dotfiles[0]["application"] == "App1"
        assert model.dotfiles[1]["application"] == "App3"

    def test_remove_dotfile_invalid_index(self, tmp_path: Path) -> None:
        """Test removing with invalid index returns False."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.add_dotfile("Cat", "App", "Desc", ["~/file"], True)

        # Act
        success = model.remove_dotfile(99)

        # Assert
        assert success is False
        assert len(model.dotfiles) == 1

    def test_toggle_dotfile_enabled(self, tmp_path: Path) -> None:
        """Test toggling dotfile enabled status."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.add_dotfile("Cat", "App", "Desc", ["~/file"], True)

        # Act - Toggle from True to False
        result = model.toggle_dotfile_enabled(0)

        # Assert
        assert result is False
        assert model.dotfiles[0]["enabled"] is False

        # Act - Toggle from False to True
        result = model.toggle_dotfile_enabled(0)

        # Assert
        assert result is True
        assert model.dotfiles[0]["enabled"] is True

    def test_get_dotfile_by_index_valid(self, tmp_path: Path) -> None:
        """Test retrieving dotfile by valid index."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.add_dotfile("Cat", "TestApp", "Desc", ["~/file"], True)

        # Act
        dotfile = model.get_dotfile_by_index(0)

        # Assert
        assert dotfile is not None
        assert dotfile["application"] == "TestApp"

    def test_get_dotfile_by_index_invalid(self, tmp_path: Path) -> None:
        """Test retrieving dotfile by invalid index returns None."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        dotfile = model.get_dotfile_by_index(0)

        # Assert
        assert dotfile is None

    def test_get_dotfile_count(self, tmp_path: Path) -> None:
        """Test getting dotfile count."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act & Assert - Initially empty
        assert model.get_dotfile_count() == 0

        # Add dotfiles
        model.add_dotfile("Cat1", "App1", "Desc1", ["~/file1"], True)
        model.add_dotfile("Cat2", "App2", "Desc2", ["~/file2"], True)

        # Act & Assert - After adding
        assert model.get_dotfile_count() == 2


class TestDFBUModelPathOperations:
    """Test suite for path expansion and assembly."""

    def test_expand_path_with_tilde(self, tmp_path: Path) -> None:
        """Test path expansion with tilde."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        result = model.expand_path("~/test/file.txt")

        # Assert
        assert result == Path.home() / "test" / "file.txt"

    def test_expand_path_without_tilde(self, tmp_path: Path) -> None:
        """Test path expansion without tilde."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        result = model.expand_path("/absolute/path")

        # Assert
        assert result == Path("/absolute/path")

    def test_check_readable_existing_file(self, tmp_path: Path) -> None:
        """Test readability check for existing file."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        test_file = tmp_path / "readable.txt"
        test_file.write_text("content")

        # Act
        result = model.check_readable(test_file)

        # Assert
        assert result is True

    def test_check_readable_nonexistent(self, tmp_path: Path) -> None:
        """Test readability check for nonexistent path."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        test_file = tmp_path / "nonexistent.txt"

        # Act
        result = model.check_readable(test_file)

        # Assert
        assert result is False


class TestDFBUModelFileOperations:
    """Test suite for file copy and directory operations."""

    def test_copy_file_success(self, tmp_path: Path) -> None:
        """Test successful file copy operation."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        src = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        src.write_text("test content")

        # Act
        success = model.copy_file(src, dest, create_parent=False)

        # Assert
        assert success is True
        assert dest.exists()
        assert dest.read_text() == "test content"

    def test_copy_file_creates_parent_directory(self, tmp_path: Path) -> None:
        """Test file copy creates parent directories."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        src = tmp_path / "source.txt"
        dest = tmp_path / "nested" / "dir" / "dest.txt"
        src.write_text("test content")

        # Act
        success = model.copy_file(src, dest, create_parent=True)

        # Assert
        assert success is True
        assert dest.exists()
        assert dest.parent.exists()

    def test_copy_file_with_skip_identical(self, tmp_path: Path) -> None:
        """Test copy_file with skip_identical optimization."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        src = tmp_path / "source.txt"
        src.write_text("identical content")
        dest = tmp_path / "dest.txt"
        dest.write_text("identical content")

        # Make files identical with same mtime
        src.copy(dest, follow_symlinks=True, preserve_metadata=True)

        # Act - should skip copy since files are identical
        success = model.copy_file(src, dest, skip_identical=True)

        # Assert - operation succeeds but file wasn't actually copied
        assert success is True
        assert dest.exists()

    def test_create_directory_success(self, tmp_path: Path) -> None:
        """Test successful directory creation."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        new_dir = tmp_path / "new" / "nested" / "directory"

        # Act
        model.create_directory(new_dir)

        # Assert
        assert new_dir.exists()
        assert new_dir.is_dir()


class TestDFBUModelStatistics:
    """Test suite for operation statistics tracking."""

    def test_record_item_processed(self, tmp_path: Path) -> None:
        """Test recording processed items updates statistics."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        model.record_item_processed(0.5)
        model.record_item_processed(0.3)
        model.record_item_processed(0.7)

        # Assert
        assert model.statistics.processed_items == 3
        assert len(model.statistics.processing_times) == 3
        assert model.statistics.average_time > 0

    def test_record_item_skipped(self, tmp_path: Path) -> None:
        """Test recording skipped items updates statistics."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        model.record_item_skipped()
        model.record_item_skipped()

        # Assert
        assert model.statistics.skipped_items == 2

    def test_record_item_failed(self, tmp_path: Path) -> None:
        """Test recording failed items updates statistics."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        model.record_item_failed()
        model.record_item_failed()
        model.record_item_failed()

        # Assert
        assert model.statistics.failed_items == 3

    def test_reset_statistics(self, tmp_path: Path) -> None:
        """Test resetting statistics clears all counters."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.record_item_processed(0.5)
        model.record_item_skipped()
        model.record_item_failed()

        # Act
        model.reset_statistics()

        # Assert
        assert model.statistics.processed_items == 0
        assert model.statistics.skipped_items == 0
        assert model.statistics.failed_items == 0
        assert len(model.statistics.processing_times) == 0


class TestDFBUModelOptionManagement:
    """Test suite for option updates."""

    def test_update_option_valid_boolean(self, tmp_path: Path) -> None:
        """Test updating boolean option."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        success = model.update_option("mirror", False)

        # Assert
        assert success is True
        assert model.options["mirror"] is False

    def test_update_option_valid_integer(self, tmp_path: Path) -> None:
        """Test updating integer option."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        success = model.update_option("max_archives", 15)

        # Assert
        assert success is True
        assert model.options["max_archives"] == 15

    def test_update_option_invalid_key(self, tmp_path: Path) -> None:
        """Test updating invalid option key returns False."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        success = model.update_option("invalid_key", "value")

        # Assert
        assert success is False

    def test_update_path_mirror_dir(self, tmp_path: Path) -> None:
        """Test updating mirror directory path."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        success = model.update_path("mirror_dir", "~/new/mirror")

        # Assert
        assert success is True
        assert model.mirror_base_dir == Path.home() / "new" / "mirror"

    def test_update_path_archive_dir(self, tmp_path: Path) -> None:
        """Test updating archive directory path."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        success = model.update_path("archive_dir", "~/new/archive")

        # Assert
        assert success is True
        assert model.archive_base_dir == Path.home() / "new" / "archive"

    def test_update_path_invalid_type(self, tmp_path: Path) -> None:
        """Test updating invalid path type returns False."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")

        # Act
        success = model.update_path("invalid_type", "~/path")

        # Assert
        assert success is False


class TestModelRestoreBackupIntegration:
    """Test DFBUModel integration with RestoreBackupManager."""

    def test_model_has_restore_backup_manager(self) -> None:
        """Test DFBUModel creates RestoreBackupManager."""
        # Arrange & Act
        model = DFBUModel(Path("/tmp/test_config.toml"))

        # Assert
        assert hasattr(model, "_restore_backup_manager")
        assert model._restore_backup_manager is not None
