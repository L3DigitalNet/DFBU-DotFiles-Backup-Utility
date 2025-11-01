"""
Test Model Additional Coverage

Description:
    Additional comprehensive unit tests for DFBUModel to achieve full coverage
    including edge cases, error paths, and utility functions.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
License: MIT
"""

import sys
import tarfile
from pathlib import Path


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))

from file_operations import (
    create_rotating_backup,
    get_backup_files,
    rotate_old_backups,
)
from model import DFBUModel


class TestModelBackupUtilities:
    """Test suite for backup utility functions."""

    def test_create_rotating_backup_success(self, tmp_path: Path) -> None:
        """Test create_rotating_backup creates timestamped backup."""
        # Arrange
        source_file = tmp_path / "source.txt"
        source_file.write_text("test content")
        backup_dir = tmp_path / "backups"

        # Act
        backup_path = create_rotating_backup(source_file, backup_dir, max_backups=5)

        # Assert
        assert backup_path is not None
        assert backup_path.exists()
        assert backup_path.parent == backup_dir

    def test_create_rotating_backup_default_directory(self, tmp_path: Path) -> None:
        """Test create_rotating_backup uses default backup directory."""
        # Arrange
        source_file = tmp_path / "source.txt"
        source_file.write_text("test content")

        # Act - no backup_dir specified
        backup_path = create_rotating_backup(
            source_file, backup_dir=None, max_backups=5
        )

        # Assert
        assert backup_path is not None
        assert backup_path.parent.name == ".source.txt.backups"

    def test_create_rotating_backup_handles_collision(self, tmp_path: Path) -> None:
        """Test create_rotating_backup handles filename collisions."""
        # Arrange
        source_file = tmp_path / "source.txt"
        source_file.write_text("test content")
        backup_dir = tmp_path / "backups"

        # Act - create multiple backups rapidly
        backup1 = create_rotating_backup(source_file, backup_dir)
        backup2 = create_rotating_backup(source_file, backup_dir)

        # Assert
        assert backup1 is not None
        assert backup2 is not None
        assert backup1 != backup2

    def test_create_rotating_backup_rotates_old_backups(self, tmp_path: Path) -> None:
        """Test create_rotating_backup deletes oldest backups."""
        # Arrange
        source_file = tmp_path / "source.txt"
        source_file.write_text("test content")
        backup_dir = tmp_path / "backups"
        max_backups = 3

        # Act - create more than max_backups
        for i in range(5):
            source_file.write_text(f"content {i}")
            create_rotating_backup(source_file, backup_dir, max_backups)

        # Assert - should have exactly max_backups
        backup_files = list(backup_dir.glob("source.*.txt"))
        assert len(backup_files) == max_backups

    def test_create_rotating_backup_returns_none_for_nonexistent(
        self, tmp_path: Path
    ) -> None:
        """Test create_rotating_backup returns None for nonexistent file."""
        # Arrange
        nonexistent = tmp_path / "nonexistent.txt"

        # Act
        result = create_rotating_backup(nonexistent)

        # Assert
        assert result is None

    def test_get_backup_files_finds_all_backups(self, tmp_path: Path) -> None:
        """Test get_backup_files finds all backup files."""
        # Arrange
        source_file = tmp_path / "source.txt"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create test backup files
        (backup_dir / "source.20250101_120000.txt").write_text("backup1")
        (backup_dir / "source.20250102_120000.txt").write_text("backup2")
        (backup_dir / "source.20250103_120000.txt").write_text("backup3")

        # Act
        backup_files = get_backup_files(source_file, backup_dir)

        # Assert
        assert len(backup_files) == 3

    def test_get_backup_files_returns_empty_for_nonexistent_dir(
        self, tmp_path: Path
    ) -> None:
        """Test get_backup_files returns empty list for nonexistent directory."""
        # Arrange
        source_file = tmp_path / "source.txt"
        nonexistent_dir = tmp_path / "nonexistent"

        # Act
        backup_files = get_backup_files(source_file, nonexistent_dir)

        # Assert
        assert len(backup_files) == 0

    def test_get_backup_files_sorts_by_age(self, tmp_path: Path) -> None:
        """Test get_backup_files returns files sorted oldest first."""
        # Arrange
        source_file = tmp_path / "source.txt"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create backup files with different timestamps
        import time

        file1 = backup_dir / "source.20250101_120000.txt"
        file1.write_text("backup1")
        time.sleep(0.01)

        file2 = backup_dir / "source.20250102_120000.txt"
        file2.write_text("backup2")
        time.sleep(0.01)

        file3 = backup_dir / "source.20250103_120000.txt"
        file3.write_text("backup3")

        # Act
        backup_files = get_backup_files(source_file, backup_dir)

        # Assert - should be sorted by modification time
        assert len(backup_files) == 3
        assert backup_files[0].name == "source.20250101_120000.txt"

    def test_rotate_old_backups_deletes_oldest(self, tmp_path: Path) -> None:
        """Test rotate_old_backups deletes oldest backups."""
        # Arrange
        source_file = tmp_path / "source.txt"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        # Create backup files
        import time

        file1 = backup_dir / "source.20250101_120000.txt"
        file1.write_text("backup1")
        time.sleep(0.01)

        file2 = backup_dir / "source.20250102_120000.txt"
        file2.write_text("backup2")
        time.sleep(0.01)

        file3 = backup_dir / "source.20250103_120000.txt"
        file3.write_text("backup3")

        # Act
        deleted = rotate_old_backups(source_file, backup_dir, max_backups=2)

        # Assert
        assert len(deleted) == 1
        assert not file1.exists()
        assert file2.exists()
        assert file3.exists()

    def test_rotate_old_backups_returns_empty_when_under_limit(
        self, tmp_path: Path
    ) -> None:
        """Test rotate_old_backups returns empty when under limit."""
        # Arrange
        source_file = tmp_path / "source.txt"
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        (backup_dir / "source.20250101_120000.txt").write_text("backup1")

        # Act
        deleted = rotate_old_backups(source_file, backup_dir, max_backups=5)

        # Assert
        assert len(deleted) == 0


class TestModelArchiveOperations:
    """Test suite for archive creation and rotation."""

    def test_create_archive_with_hostname_subdir(self, tmp_path: Path) -> None:
        """Test create_archive respects hostname_subdir option."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)
        model.archive_base_dir = tmp_path / "archives"
        model.options["hostname_subdir"] = True

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Act
        archive_path = model.create_archive([(test_file, True, False)])

        # Assert
        assert archive_path is not None
        assert model.hostname in str(archive_path.parent)

    def test_create_archive_without_hostname_subdir(self, tmp_path: Path) -> None:
        """Test create_archive without hostname subdirectory."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)
        model.archive_base_dir = tmp_path / "archives"
        model.options["hostname_subdir"] = False

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        # Act
        archive_path = model.create_archive([(test_file, True, False)])

        # Assert
        assert archive_path is not None
        assert archive_path.parent == model.archive_base_dir

    def test_create_archive_skips_nonexistent_paths(self, tmp_path: Path) -> None:
        """Test create_archive skips paths that don't exist."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)
        model.archive_base_dir = tmp_path / "archives"

        nonexistent = tmp_path / "nonexistent.txt"

        # Act
        archive_path = model.create_archive([(nonexistent, False, False)])

        # Assert
        assert archive_path is not None
        assert archive_path.exists()

    def test_create_archive_includes_directories(self, tmp_path: Path) -> None:
        """Test create_archive includes directory contents."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)
        model.archive_base_dir = tmp_path / "archives"

        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")

        # Act
        archive_path = model.create_archive([(test_dir, True, True)])

        # Assert
        assert archive_path is not None
        assert archive_path.exists()

        # Verify archive contents
        with tarfile.open(archive_path, "r:gz") as tar:
            members = tar.getmembers()
            assert len(members) > 0

    def test_rotate_archives_deletes_oldest(self, tmp_path: Path) -> None:
        """Test rotate_archives deletes oldest archives."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)
        model.archive_base_dir = tmp_path / "archives"
        model.archive_base_dir.mkdir()
        model.options["max_archives"] = 2
        model.options["hostname_subdir"] = False

        # Create old archives
        import time

        archive1 = model.archive_base_dir / "dotfiles-2025-01-01_00-00-00.tar.gz"
        archive1.write_text("archive1")
        time.sleep(0.01)

        archive2 = model.archive_base_dir / "dotfiles-2025-01-02_00-00-00.tar.gz"
        archive2.write_text("archive2")
        time.sleep(0.01)

        archive3 = model.archive_base_dir / "dotfiles-2025-01-03_00-00-00.tar.gz"
        archive3.write_text("archive3")

        # Act
        deleted = model.rotate_archives()

        # Assert
        assert len(deleted) == 1
        assert not archive1.exists()
        assert archive2.exists()
        assert archive3.exists()


class TestModelRestoreOperations:
    """Test suite for restore file discovery and path reconstruction."""

    def test_discover_restore_files_with_hostname(self, tmp_path: Path) -> None:
        """Test discover_restore_files finds files in hostname subdirectory."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        # Create backup structure with hostname
        backup_dir = tmp_path / "backup" / model.hostname / "home"
        backup_dir.mkdir(parents=True)
        (backup_dir / ".testrc").write_text("content")

        # Act
        files = model.discover_restore_files(tmp_path / "backup")

        # Assert
        assert len(files) > 0

    def test_discover_restore_files_without_hostname(self, tmp_path: Path) -> None:
        """Test discover_restore_files finds files without hostname subdirectory."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        # Create backup structure without hostname
        backup_dir = tmp_path / "backup" / "home"
        backup_dir.mkdir(parents=True)
        (backup_dir / ".testrc").write_text("content")

        # Act
        files = model.discover_restore_files(tmp_path / "backup")

        # Assert
        assert len(files) > 0

    def test_discover_restore_files_empty_directory(self, tmp_path: Path) -> None:
        """Test discover_restore_files returns empty list for empty directory."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        # Act
        files = model.discover_restore_files(empty_dir)

        # Assert
        assert len(files) == 0

    def test_reconstruct_restore_paths_home_files(self, tmp_path: Path) -> None:
        """Test reconstruct_restore_paths handles home directory files."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        backup_dir = tmp_path / "backup"
        home_backup = backup_dir / model.hostname / "home" / ".testrc"
        home_backup.parent.mkdir(parents=True)
        home_backup.write_text("content")

        # Act
        paths = model.reconstruct_restore_paths([home_backup])

        # Assert
        assert len(paths) > 0

    def test_reconstruct_restore_paths_root_files(self, tmp_path: Path) -> None:
        """Test reconstruct_restore_paths handles root directory files."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        backup_dir = tmp_path / "backup"
        root_backup = backup_dir / model.hostname / "root" / "etc" / "config"
        root_backup.parent.mkdir(parents=True)
        root_backup.write_text("content")

        # Act
        paths = model.reconstruct_restore_paths([root_backup])

        # Assert
        assert len(paths) > 0


class TestModelValidation:
    """Test suite for dotfile path validation."""

    def test_validate_dotfile_paths_all_valid(self, tmp_path: Path) -> None:
        """Test validate_dotfile_paths with all valid paths."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        test_file = tmp_path / "test.txt"
        test_file.write_text("content")

        model.add_dotfile("Test", "Test", "Test", "Test", [str(test_file)], True)

        # Act
        results = model.validate_dotfile_paths()

        # Assert
        assert len(results) == 1
        assert results[0][0] is True  # exists
        assert results[0][1] is False  # is_dir (file, not directory)

    def test_validate_dotfile_paths_nonexistent(self, tmp_path: Path) -> None:
        """Test validate_dotfile_paths with nonexistent paths."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        model.add_dotfile("Test", "Test", "Test", "Test", ["/nonexistent/path"], True)

        # Act
        results = model.validate_dotfile_paths()

        # Assert
        assert len(results) == 1
        assert results[0][0] is False  # doesn't exist

    def test_validate_dotfile_paths_multiple_dotfiles(self, tmp_path: Path) -> None:
        """Test validate_dotfile_paths with multiple dotfiles."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        test_file1 = tmp_path / "test1.txt"
        test_file1.write_text("content1")

        test_file2 = tmp_path / "test2.txt"
        test_file2.write_text("content2")

        model.add_dotfile("Test1", "Test", "Test", "Test", [str(test_file1)], True)

        model.add_dotfile("Test2", "Test", "Test", "Test", [str(test_file2)], True)

        # Act
        results = model.validate_dotfile_paths()

        # Assert
        assert len(results) == 2


class TestModelDotfileSizes:
    """Test suite for dotfile size calculation."""

    def test_get_dotfile_sizes_single_file(self, tmp_path: Path) -> None:
        """Test get_dotfile_sizes for single file."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        model.add_dotfile("Test", "Test", "Test", "Test", [str(test_file)], True)

        # Act
        sizes = model.get_dotfile_sizes()

        # Assert
        assert len(sizes) == 1
        assert sizes[0] > 0

    def test_get_dotfile_sizes_directory(self, tmp_path: Path) -> None:
        """Test get_dotfile_sizes for directory."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content1")
        (test_dir / "file2.txt").write_text("content2")

        model.add_dotfile("Test", "Test", "Test", "Test", [str(test_dir)], True)

        # Act
        sizes = model.get_dotfile_sizes()

        # Assert
        assert len(sizes) == 1
        assert sizes[0] > 0

    def test_get_dotfile_sizes_nonexistent(self, tmp_path: Path) -> None:
        """Test get_dotfile_sizes for nonexistent path."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        model.add_dotfile("Test", "Test", "Test", "Test", ["/nonexistent/path"], True)

        # Act
        sizes = model.get_dotfile_sizes()

        # Assert
        assert len(sizes) == 1
        assert sizes[0] == 0
