"""
Test Model File Operations

Description:
    Additional unit tests for DFBUModel file operations including file
    identity checks, directory copying, and archive operations.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-31-2025
License: MIT
"""

import sys
import time
from pathlib import Path

import pytest


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))

from model import DFBUModel


class TestModelFileIdentity:
    """Test suite for file identity checking."""

    def test_files_are_identical_same_file(self, tmp_path: Path) -> None:
        """Test files_are_identical returns True for identical files."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        content = "Test content for identity check"
        file1.write_text(content)

        # Copy file1 to file2 to make them identical
        file1.copy(file2, follow_symlinks=True, preserve_metadata=True)

        # Act
        result = model.files_are_identical(file1, file2)

        # Assert
        assert result is True

    def test_files_are_identical_different_size(self, tmp_path: Path) -> None:
        """Test files_are_identical returns False for different sizes."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Short")
        file2.write_text("Much longer content")

        # Act
        result = model.files_are_identical(file1, file2)

        # Assert
        assert result is False

    def test_files_are_identical_destination_not_exists(self, tmp_path: Path) -> None:
        """Test files_are_identical returns False when dest doesn't exist."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Content")

        # Act
        result = model.files_are_identical(file1, file2)

        # Assert
        assert result is False

    def test_copy_file_skip_identical_optimization(self, tmp_path: Path) -> None:
        """Test copy_file skips copying when files are identical."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        src_file = tmp_path / "source.txt"
        dest_file = tmp_path / "dest.txt"
        content = "Test content"

        src_file.write_text(content)
        src_file.copy(dest_file, follow_symlinks=True, preserve_metadata=True)

        # Act
        success = model.copy_file(src_file, dest_file, skip_identical=True)

        # Assert
        assert success is True
        assert dest_file.read_text() == content


class TestModelDirectoryCopying:
    """Test suite for directory copying operations."""

    def test_copy_directory_with_multiple_files(self, tmp_path: Path) -> None:
        """Test copy_directory handles multiple files."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        src_dir = tmp_path / "source"
        src_dir.mkdir()

        (src_dir / "file1.txt").write_text("Content 1")
        (src_dir / "file2.txt").write_text("Content 2")
        (src_dir / "file3.txt").write_text("Content 3")

        dest_dir = tmp_path / "dest"

        # Act
        results = model.copy_directory(src_dir, dest_dir)

        # Assert
        assert len(results) == 3
        for _src_file, dest_file, success, skipped in results:
            assert success is True
            assert skipped is False
            assert dest_file is not None
            assert dest_file.exists()

    def test_copy_directory_with_nested_structure(self, tmp_path: Path) -> None:
        """Test copy_directory handles nested directory structure."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        src_dir = tmp_path / "source"

        # Create nested structure
        (src_dir / "subdir1").mkdir(parents=True)
        (src_dir / "subdir1" / "file1.txt").write_text("Nested 1")
        (src_dir / "subdir2").mkdir(parents=True)
        (src_dir / "subdir2" / "file2.txt").write_text("Nested 2")

        dest_dir = tmp_path / "dest"

        # Act
        results = model.copy_directory(src_dir, dest_dir)

        # Assert
        assert len(results) == 2
        assert (dest_dir / "subdir1" / "file1.txt").exists()
        assert (dest_dir / "subdir2" / "file2.txt").exists()

    def test_copy_directory_skip_identical_files(self, tmp_path: Path) -> None:
        """Test copy_directory skips identical files when optimization enabled."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        src_dir = tmp_path / "source"
        src_dir.mkdir()

        src_file = src_dir / "file.txt"
        src_file.write_text("Content")

        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        dest_file = dest_dir / "file.txt"

        # Copy once to create identical files
        model.copy_file(src_file, dest_file)

        # Act - copy again with skip_identical
        results = model.copy_directory(src_dir, dest_dir, skip_identical=True)

        # Assert
        assert len(results) == 1
        src, dest, success, skipped = results[0]
        assert success is True
        assert skipped is True


class TestModelPathSizeCalculation:
    """Test suite for path size calculation."""

    def test_calculate_path_size_single_file(self, tmp_path: Path) -> None:
        """Test calculate_path_size for single file."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        test_file = tmp_path / "test.txt"
        content = "Test content" * 100
        test_file.write_text(content)
        expected_size = test_file.stat().st_size

        # Act
        size = model.calculate_path_size(test_file)

        # Assert
        assert size == expected_size
        assert size > 0

    def test_calculate_path_size_directory(self, tmp_path: Path) -> None:
        """Test calculate_path_size for directory with multiple files."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()

        file1 = test_dir / "file1.txt"
        file2 = test_dir / "file2.txt"
        file1.write_text("Content 1" * 50)
        file2.write_text("Content 2" * 50)

        expected_size = file1.stat().st_size + file2.stat().st_size

        # Act
        size = model.calculate_path_size(test_dir)

        # Assert
        assert size == expected_size
        assert size > 0

    def test_calculate_path_size_nonexistent(self, tmp_path: Path) -> None:
        """Test calculate_path_size returns 0 for nonexistent path."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        nonexistent = tmp_path / "nonexistent.txt"

        # Act
        size = model.calculate_path_size(nonexistent)

        # Assert
        assert size == 0

    def test_get_dotfile_sizes_multiple_paths(self, tmp_path: Path) -> None:
        """Test get_dotfile_sizes sums sizes for multiple paths."""
        # Arrange
        config_path = tmp_path / "config.toml"
        model = DFBUModel(config_path)

        # Create test files
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("A" * 100)
        file2.write_text("B" * 200)

        # Add dotfile with multiple paths
        model.add_dotfile(
            "Test",
            "Test",
            "TestApp",
            "Test",
            [str(file1), str(file2)],
            True,
        )

        # Act
        sizes = model.get_dotfile_sizes()

        # Assert
        assert 0 in sizes
        expected_size = file1.stat().st_size + file2.stat().st_size
        assert sizes[0] == expected_size


class TestModelArchiveOperations:
    """Test suite for archive operations."""

    def test_create_archive_single_file(self, tmp_path: Path) -> None:
        """Test create_archive with single file."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.archive_base_dir = tmp_path / "archives"
        model.archive_base_dir.mkdir()

        test_file = tmp_path / "test.txt"
        test_file.write_text("Archive test content")

        dotfiles_to_archive = [(test_file, True, False)]

        # Act
        archive_path = model.create_archive(dotfiles_to_archive)

        # Assert
        assert archive_path is not None
        assert archive_path.exists()
        assert archive_path.suffix == ".gz"

    def test_create_archive_multiple_files(self, tmp_path: Path) -> None:
        """Test create_archive with multiple files."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.archive_base_dir = tmp_path / "archives"
        model.archive_base_dir.mkdir()

        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("Content 1")
        file2.write_text("Content 2")

        dotfiles_to_archive = [(file1, True, False), (file2, True, False)]

        # Act
        archive_path = model.create_archive(dotfiles_to_archive)

        # Assert
        assert archive_path is not None
        assert archive_path.exists()

    def test_rotate_archives_deletes_oldest(self, tmp_path: Path) -> None:
        """Test rotate_archives deletes oldest archives when exceeding max."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.archive_base_dir = tmp_path / "archives"
        model.archive_base_dir.mkdir()
        model.options["max_archives"] = 3
        model.options["hostname_subdir"] = False  # Disable hostname subdir for test

        # Create 5 archives with different times
        for i in range(5):
            archive = (
                model.archive_base_dir / f"dotfiles-2025-01-{i + 1:02d}_00-00-00.tar.gz"
            )
            archive.write_text(f"Archive {i}")
            time.sleep(0.01)  # Ensure different mtimes

        # Act
        deleted = model.rotate_archives()

        # Assert
        assert len(deleted) == 2
        remaining = list(model.archive_base_dir.glob("dotfiles-*.tar.gz"))
        assert len(remaining) == 3


class TestModelRestoreOperations:
    """Test suite for restore operations."""

    def test_discover_restore_files_finds_all_files(self, tmp_path: Path) -> None:
        """Test discover_restore_files finds all files in directory."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        src_dir = tmp_path / "backup"
        src_dir.mkdir()

        (src_dir / "file1.txt").write_text("1")
        (src_dir / "file2.txt").write_text("2")
        subdir = src_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("3")

        # Act
        files = model.discover_restore_files(src_dir)

        # Assert
        assert len(files) == 3
        assert all(f.is_file() for f in files)

    def test_reconstruct_restore_paths_home_directory(self, tmp_path: Path) -> None:
        """Test reconstruct_restore_paths for home directory files."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        hostname = model.hostname

        # Simulate backup structure: hostname/home/user/file.txt
        backup_path = tmp_path / hostname / "home" / "testuser" / "file.txt"
        backup_path.parent.mkdir(parents=True)
        backup_path.write_text("test")

        # Act
        results = model.reconstruct_restore_paths([backup_path])

        # Assert
        assert len(results) == 1
        src_path, dest_path = results[0]
        assert src_path == backup_path
        assert dest_path is not None
        assert "home" in str(dest_path) or dest_path.is_relative_to(Path.home())

    def test_reconstruct_restore_paths_root_directory(self, tmp_path: Path) -> None:
        """Test reconstruct_restore_paths for root directory files."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        hostname = model.hostname

        # Simulate backup structure: hostname/root/etc/config.txt
        backup_path = tmp_path / hostname / "root" / "etc" / "config.txt"
        backup_path.parent.mkdir(parents=True)
        backup_path.write_text("config")

        # Act
        results = model.reconstruct_restore_paths([backup_path])

        # Assert
        assert len(results) == 1
        src_path, dest_path = results[0]
        assert src_path == backup_path
        assert dest_path is not None


class TestModelConfidentCodePaths:
    """Test suite for confident code execution paths after simplification."""

    def test_copy_file_confident_execution(self, tmp_path: Path) -> None:
        """Test copy_file executes confidently with valid paths."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        src_file = tmp_path / "source.txt"
        src_file.write_text("Confident copy test")
        dest_file = tmp_path / "dest" / "target.txt"

        # Act - Should execute without defensive checks on valid paths
        success = model.copy_file(src_file, dest_file, create_parent=True)

        # Assert
        assert success is True
        assert dest_file.exists()
        assert dest_file.read_text() == "Confident copy test"

    def test_create_directory_confident_execution(self, tmp_path: Path) -> None:
        """Test create_directory executes confidently without return checks."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        new_dir = tmp_path / "confident" / "nested" / "path"

        # Act - Should execute without defensive return checking
        model.create_directory(new_dir)

        # Assert - Verify directory was created
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_archive_returns_path_on_success(self, tmp_path: Path) -> None:
        """Test create_archive returns Path object on success (not tuple)."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        model.archive_base_dir = tmp_path / "archives"
        model.archive_base_dir.mkdir()

        test_file = tmp_path / "test.txt"
        test_file.write_text("Archive content")

        dotfiles_to_archive = [(test_file, True, False)]

        # Act
        result = model.create_archive(dotfiles_to_archive)

        # Assert - Result should be Path object, not tuple
        assert isinstance(result, Path)
        assert result.exists()
        assert result.suffix == ".gz"

    def test_create_rotating_backup_returns_path_on_success(
        self, tmp_path: Path
    ) -> None:
        """Test create_rotating_backup returns Path object on success (not tuple)."""
        # Arrange
        source_file = tmp_path / "source.txt"
        source_file.write_text("Backup content")
        backup_dir = tmp_path / "backups"

        # Act
        from file_operations import create_rotating_backup

        result = create_rotating_backup(source_file, backup_dir, max_backups=5)

        # Assert - Result should be Path object or None, not tuple
        assert isinstance(result, Path) or result is None
        if result:
            assert result.exists()

    def test_discover_restore_files_confident_execution(self, tmp_path: Path) -> None:
        """Test discover_restore_files executes confidently without try-except."""
        # Arrange
        model = DFBUModel(tmp_path / "config.toml")
        restore_dir = tmp_path / "restore"
        restore_dir.mkdir()

        # Create test files
        (restore_dir / "file1.txt").write_text("1")
        (restore_dir / "file2.txt").write_text("2")
        subdir = restore_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("3")

        # Act - Should execute confidently
        files = model.discover_restore_files(restore_dir)

        # Assert
        assert len(files) == 3
        assert all(isinstance(f, Path) for f in files)
        assert all(f.is_file() for f in files)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
