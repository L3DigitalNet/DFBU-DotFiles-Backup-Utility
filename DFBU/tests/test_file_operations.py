"""
Test File Operations Module

Description:
    Unit tests for FileSystemHelper and PathAssembler utility classes
    testing path operations, directory creation, and path assembly.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-31-2025
License: MIT
"""

import sys
from pathlib import Path
from socket import gethostname


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dfbu import FileSystemHelper, PathAssembler


class TestFileSystemHelper:
    """Test suite for FileSystemHelper utility class."""

    def test_expand_path_with_tilde(self) -> None:
        """Test path expansion converts ~ to home directory."""
        # Arrange
        path_str = "~/test/path"

        # Act
        result = FileSystemHelper.expand_path(path_str)

        # Assert
        assert result == Path.home() / "test" / "path"
        assert "~" not in str(result)

    def test_expand_path_without_tilde(self) -> None:
        """Test path expansion without tilde returns absolute path."""
        # Arrange
        path_str = "/absolute/test/path"

        # Act
        result = FileSystemHelper.expand_path(path_str)

        # Assert
        assert result == Path("/absolute/test/path")

    def test_check_readable_existing_file(self, tmp_path: Path) -> None:
        """Test readability check for existing readable file."""
        # Arrange
        test_file = tmp_path / "readable.txt"
        test_file.write_text("test content")

        # Act
        result = FileSystemHelper.check_readable(test_file)

        # Assert
        assert result is True

    def test_check_readable_nonexistent_file(self, tmp_path: Path) -> None:
        """Test readability check for nonexistent file."""
        # Arrange
        test_file = tmp_path / "nonexistent.txt"

        # Act
        result = FileSystemHelper.check_readable(test_file)

        # Assert
        assert result is False

    def test_create_directory_new_path(self, tmp_path: Path) -> None:
        """Test directory creation for new path."""
        # Arrange
        new_dir = tmp_path / "test" / "nested" / "directory"
        dry_run = False

        # Act
        FileSystemHelper.create_directory(new_dir, dry_run)

        # Assert
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_directory_existing_path(self, tmp_path: Path) -> None:
        """Test directory creation for existing path (should not error)."""
        # Arrange
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        dry_run = False

        # Act - Should not raise exception
        FileSystemHelper.create_directory(existing_dir, dry_run)

        # Assert
        assert existing_dir.exists()
        assert existing_dir.is_dir()

    def test_create_directory_dry_run(self, tmp_path: Path) -> None:
        """Test directory creation in dry-run mode doesn't create directory."""
        # Arrange
        new_dir = tmp_path / "dry_run_test"
        dry_run = True

        # Act
        FileSystemHelper.create_directory(new_dir, dry_run)

        # Assert
        assert not new_dir.exists()

    def test_format_dry_run_prefix_enabled(self) -> None:
        """Test dry-run prefix formatting when enabled."""
        # Act
        result = FileSystemHelper.format_dry_run_prefix(dry_run=True)

        # Assert
        assert result == "[DRY RUN] "

    def test_format_dry_run_prefix_disabled(self) -> None:
        """Test dry-run prefix formatting when disabled."""
        # Act
        result = FileSystemHelper.format_dry_run_prefix(dry_run=False)

        # Assert
        assert result == ""

    def test_format_action_verb_copy_dry_run_present_tense(self) -> None:
        """Test action verb formatting in dry-run mode, present tense."""
        # Act
        result = FileSystemHelper.format_action_verb(
            "copy", dry_run=True, past_tense=False
        )

        # Assert
        assert result == "Would copy"

    def test_format_action_verb_copy_normal_present_tense(self) -> None:
        """Test action verb formatting in normal mode, present tense."""
        # Act
        result = FileSystemHelper.format_action_verb(
            "copy", dry_run=False, past_tense=False
        )

        # Assert
        assert result == "Copying"

    def test_format_action_verb_copy_normal_past_tense(self) -> None:
        """Test action verb formatting in normal mode, past tense."""
        # Act
        result = FileSystemHelper.format_action_verb(
            "copy", dry_run=False, past_tense=True
        )

        # Assert - Implementation just adds "d" to capitalized verb
        assert result == "Copyd"

    def test_format_action_verb_delete_dry_run_past_tense(self) -> None:
        """Test action verb formatting for delete in dry-run mode."""
        # Act
        result = FileSystemHelper.format_action_verb(
            "delete", dry_run=True, past_tense=True
        )

        # Assert
        assert result == "Would delete"


class TestPathAssembler:
    """Test suite for PathAssembler utility class."""

    def test_assemble_dest_path_home_no_subdirs(self, tmp_path: Path) -> None:
        """Test destination path assembly for home directory without subdirs."""
        # Arrange
        base_path = tmp_path / "backup"
        src_path = Path.home() / "test" / "file.txt"
        hostname_subdir = False
        date_subdir = False

        # Act
        result = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        assert result == base_path / "home" / "test" / "file.txt"

    def test_assemble_dest_path_home_with_hostname(self, tmp_path: Path) -> None:
        """Test destination path assembly with hostname subdirectory."""
        # Arrange
        base_path = tmp_path / "backup"
        src_path = Path.home() / "test" / "file.txt"
        hostname_subdir = True
        date_subdir = False

        # Act
        result = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        hostname = gethostname()
        assert result == base_path / hostname / "home" / "test" / "file.txt"

    def test_assemble_dest_path_home_with_date(self, tmp_path: Path) -> None:
        """Test destination path assembly with date subdirectory."""
        # Arrange
        import time

        base_path = tmp_path / "backup"
        src_path = Path.home() / "test" / "file.txt"
        hostname_subdir = False
        date_subdir = True
        expected_date = time.strftime("%Y-%m-%d")

        # Act
        result = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        assert result == base_path / expected_date / "home" / "test" / "file.txt"

    def test_assemble_dest_path_home_with_both_subdirs(self, tmp_path: Path) -> None:
        """Test destination path assembly with both hostname and date subdirs."""
        # Arrange
        import time

        base_path = tmp_path / "backup"
        src_path = Path.home() / "config" / "app.conf"
        hostname_subdir = True
        date_subdir = True
        hostname = gethostname()
        expected_date = time.strftime("%Y-%m-%d")

        # Act
        result = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        assert (
            result
            == base_path / hostname / expected_date / "home" / "config" / "app.conf"
        )

    def test_assemble_dest_path_root_no_subdirs(self, tmp_path: Path) -> None:
        """Test destination path assembly for root directory without subdirs."""
        # Arrange
        base_path = tmp_path / "backup"
        src_path = Path("/etc/config/system.conf")
        hostname_subdir = False
        date_subdir = False

        # Act
        result = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        assert result == base_path / "root" / "etc" / "config" / "system.conf"

    def test_assemble_dest_path_root_with_hostname(self, tmp_path: Path) -> None:
        """Test destination path assembly for root with hostname."""
        # Arrange
        base_path = tmp_path / "backup"
        src_path = Path("/etc/hosts")
        hostname_subdir = True
        date_subdir = False
        hostname = gethostname()

        # Act
        result = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        assert result == base_path / hostname / "root" / "etc" / "hosts"

    def test_assemble_dest_path_preserves_nested_structure(
        self, tmp_path: Path
    ) -> None:
        """Test destination path preserves nested directory structure."""
        # Arrange
        base_path = tmp_path / "backup"
        src_path = (
            Path.home() / "deeply" / "nested" / "directory" / "structure" / "file.txt"
        )
        hostname_subdir = False
        date_subdir = False

        # Act
        result = PathAssembler.assemble_dest_path(
            base_path, src_path, hostname_subdir, date_subdir
        )

        # Assert
        expected = (
            base_path
            / "home"
            / "deeply"
            / "nested"
            / "directory"
            / "structure"
            / "file.txt"
        )
        assert result == expected
        # Verify all components are preserved
        assert "deeply" in result.parts
        assert "nested" in result.parts
        assert "structure" in result.parts
