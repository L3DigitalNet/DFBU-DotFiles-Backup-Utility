"""
Test CLI Integration

Description:
    Integration tests for CLI operations including backup workflow, restore
    operations, menu interactions, and end-to-end CLI functionality.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-31-2025
License: MIT
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dfbu import (
    ArchiveBackup,
    CLIHandler,
    ConfigValidator,
    DotFile,
    FileSystemHelper,
    MirrorBackup,
    Options,
    PathAssembler,
)


class TestCLIHandlerArgumentParsing:
    """Test suite for CLI argument parsing."""

    def test_parse_args_no_flags(self) -> None:
        """Test parse_args with no command-line flags."""
        # Arrange & Act
        with patch("sys.argv", ["dfbu.py"]):
            dry_run, force = CLIHandler.parse_args()

        # Assert
        assert dry_run is False
        assert force is False

    def test_parse_args_dry_run_flag(self) -> None:
        """Test parse_args with --dry-run flag."""
        # Arrange & Act
        with patch("sys.argv", ["dfbu.py", "--dry-run"]):
            dry_run, force = CLIHandler.parse_args()

        # Assert
        assert dry_run is True
        assert force is False

    def test_parse_args_force_flag(self) -> None:
        """Test parse_args with --force flag."""
        # Arrange & Act
        with patch("sys.argv", ["dfbu.py", "--force"]):
            dry_run, force = CLIHandler.parse_args()

        # Assert
        assert dry_run is False
        assert force is True

    def test_parse_args_both_flags(self) -> None:
        """Test parse_args with both flags."""
        # Arrange & Act
        with patch("sys.argv", ["dfbu.py", "--dry-run", "--force"]):
            dry_run, force = CLIHandler.parse_args()

        # Assert
        assert dry_run is True
        assert force is True

    def test_parse_args_short_flags(self) -> None:
        """Test parse_args with short flag syntax."""
        # Arrange & Act
        with patch("sys.argv", ["dfbu.py", "-d", "-f"]):
            dry_run, force = CLIHandler.parse_args()

        # Assert
        assert dry_run is True
        assert force is True


class TestMirrorBackupExecution:
    """Test suite for MirrorBackup static execution."""

    def test_mirror_backup_execute_with_existing_file(self, tmp_path: Path) -> None:
        """Test MirrorBackup.execute processes existing file."""
        # Arrange
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        mirror_dir = tmp_path / "mirror"
        options_dict = ConfigValidator.validate_options(
            {
                "mirror": True,
                "archive": False,
                "hostname_subdir": False,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 9,
                "rotate_archives": False,
                "max_archives": 5,
            }
        )
        options = Options(options_dict)

        dotfile_dict = ConfigValidator.validate_dotfile(
            {
                "category": "Test",
                "subcategory": "Test",
                "application": "Test",
                "description": "Test file",
                "path": str(test_file),
                "mirror_dir": str(mirror_dir),
                "archive_dir": str(tmp_path / "archive"),
            }
        )
        dotfile = DotFile(dotfile_dict, options)

        # Act
        MirrorBackup.execute([dotfile], dry_run=False)

        # Assert - destination should exist
        assert dotfile.dest_path_mirror.exists()

    def test_mirror_backup_execute_dry_run(self, tmp_path: Path) -> None:
        """Test MirrorBackup.execute in dry-run mode doesn't create files."""
        # Arrange
        test_file = tmp_path / "source.txt"
        test_file.write_text("Source content")

        mirror_dir = tmp_path / "mirror"
        options_dict = ConfigValidator.validate_options({})
        options = Options(options_dict)

        dotfile_dict = ConfigValidator.validate_dotfile(
            {
                "category": "Dry",
                "subcategory": "Run",
                "application": "Test",
                "description": "Dry run test",
                "path": str(test_file),
                "mirror_dir": str(mirror_dir),
                "archive_dir": str(tmp_path / "archive"),
            }
        )
        dotfile = DotFile(dotfile_dict, options)

        # Act
        MirrorBackup.execute([dotfile], dry_run=True)

        # Assert - destination should NOT exist (dry run)
        assert not dotfile.dest_path_mirror.exists()


class TestArchiveBackupExecution:
    """Test suite for ArchiveBackup static execution."""

    def test_archive_backup_create_creates_archive(self, tmp_path: Path) -> None:
        """Test ArchiveBackup.create creates archive file."""
        # Arrange
        test_file = tmp_path / "archive_test.txt"
        test_file.write_text("Archive content")

        archive_dir = tmp_path / "archives"
        archive_dir.mkdir()

        options_dict = ConfigValidator.validate_options(
            {
                "mirror": False,
                "archive": True,
                "hostname_subdir": False,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 9,
                "rotate_archives": False,
                "max_archives": 5,
            }
        )
        options = Options(options_dict)

        dotfile_dict = ConfigValidator.validate_dotfile(
            {
                "category": "Archive",
                "subcategory": "Test",
                "application": "Test",
                "description": "Archive test",
                "path": str(test_file),
                "mirror_dir": str(tmp_path / "mirror"),
                "archive_dir": str(archive_dir),
            }
        )
        dotfile = DotFile(dotfile_dict, options)

        # Act
        ArchiveBackup.create([dotfile], archive_dir, dry_run=False)

        # Assert - check archive was created
        archives = list(archive_dir.glob("dotfiles-*.tar.gz"))
        assert len(archives) == 1
        assert archives[0].exists()

    def test_archive_backup_create_dry_run(self, tmp_path: Path) -> None:
        """Test ArchiveBackup.create in dry-run mode doesn't create archive."""
        # Arrange
        test_file = tmp_path / "dry_archive.txt"
        test_file.write_text("Dry archive content")

        archive_dir = tmp_path / "archives"
        archive_dir.mkdir()

        options_dict = ConfigValidator.validate_options(
            {"mirror": False, "archive": True}
        )
        options = Options(options_dict)

        dotfile_dict = ConfigValidator.validate_dotfile(
            {
                "category": "Dry",
                "subcategory": "Archive",
                "application": "Test",
                "description": "Dry archive test",
                "path": str(test_file),
                "mirror_dir": str(tmp_path / "mirror"),
                "archive_dir": str(archive_dir),
            }
        )
        dotfile = DotFile(dotfile_dict, options)

        # Act
        ArchiveBackup.create([dotfile], archive_dir, dry_run=True)

        # Assert - no archives should be created
        archives = list(archive_dir.glob("dotfiles-*.tar.gz"))
        assert len(archives) == 0


class TestFileSystemHelperIntegration:
    """Test suite for FileSystemHelper utility methods."""

    def test_expand_path_integration(self, tmp_path: Path) -> None:
        """Test expand_path handles tilde expansion."""
        # Arrange
        path_with_tilde = "~/test_file.txt"

        # Act
        expanded = FileSystemHelper.expand_path(path_with_tilde)

        # Assert
        assert "~" not in str(expanded)
        assert expanded.is_absolute()

    def test_check_readable_with_existing_file(self, tmp_path: Path) -> None:
        """Test check_readable returns True for readable file."""
        # Arrange
        test_file = tmp_path / "readable.txt"
        test_file.write_text("Readable content")

        # Act
        result = FileSystemHelper.check_readable(test_file)

        # Assert
        assert result is True

    def test_create_directory_creates_parents(self, tmp_path: Path) -> None:
        """Test create_directory creates parent directories."""
        # Arrange
        nested_path = tmp_path / "level1" / "level2" / "level3"

        # Act
        FileSystemHelper.create_directory(nested_path, dry_run=False)

        # Assert
        assert nested_path.exists()
        assert nested_path.is_dir()

    def test_format_dry_run_prefix(self) -> None:
        """Test format_dry_run_prefix returns correct strings."""
        # Act
        with_dry_run = FileSystemHelper.format_dry_run_prefix(True)
        without_dry_run = FileSystemHelper.format_dry_run_prefix(False)

        # Assert
        assert "[DRY RUN]" in with_dry_run
        assert without_dry_run == ""


class TestPathAssemblerIntegration:
    """Test suite for PathAssembler utility."""

    def test_assemble_dest_path_home_file(self, tmp_path: Path) -> None:
        """Test assemble_dest_path for home directory file."""
        # Arrange
        home = Path.home()
        src_file = home / ".testrc"
        base_path = tmp_path / "backup"

        # Act
        dest = PathAssembler.assemble_dest_path(
            base_path, src_file, hostname_subdir=False, date_subdir=False
        )

        # Assert
        assert "home" in str(dest)
        assert ".testrc" in str(dest)

    def test_assemble_dest_path_with_hostname(self, tmp_path: Path) -> None:
        """Test assemble_dest_path includes hostname when enabled."""
        # Arrange
        from socket import gethostname

        src_file = Path.home() / "test.txt"
        base_path = tmp_path / "backup"

        # Act
        dest = PathAssembler.assemble_dest_path(
            base_path, src_file, hostname_subdir=True, date_subdir=False
        )

        # Assert
        assert gethostname() in str(dest)

    def test_assemble_dest_path_with_date(self, tmp_path: Path) -> None:
        """Test assemble_dest_path includes date when enabled."""
        # Arrange
        import time

        src_file = Path.home() / "dated.txt"
        base_path = tmp_path / "backup"
        current_date = time.strftime("%Y-%m-%d")

        # Act
        dest = PathAssembler.assemble_dest_path(
            base_path, src_file, hostname_subdir=False, date_subdir=True
        )

        # Assert
        assert current_date in str(dest)


class TestOptionsClass:
    """Test suite for Options class."""

    def test_options_initialization(self) -> None:
        """Test Options initializes with validated dict."""
        # Arrange
        options_dict = ConfigValidator.validate_options(
            {
                "mirror": True,
                "archive": False,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 6,
                "rotate_archives": True,
                "max_archives": 10,
            }
        )

        # Act
        options = Options(options_dict)

        # Assert
        assert options.mirror is True
        assert options.archive is False
        assert options.hostname_subdir is True
        assert options.date_subdir is False
        assert options.archive_format == "tar.gz"
        assert options.archive_compression_level == 6
        assert options.rotate_archives is True
        assert options.max_archives == 10

    def test_options_string_representation(self) -> None:
        """Test Options __str__ method returns formatted string."""
        # Arrange
        options_dict = ConfigValidator.validate_options({})
        options = Options(options_dict)

        # Act
        output = str(options)

        # Assert
        assert "Uncompressed mirror" in output
        assert "Create archive" in output
        assert "hostname subdirectory" in output


class TestDotFileClass:
    """Test suite for DotFile class integration."""

    def test_dotfile_initialization_with_options(self, tmp_path: Path) -> None:
        """Test DotFile initializes correctly with options."""
        # Arrange
        test_file = tmp_path / "dotfile_test.txt"
        test_file.write_text("Content")

        options_dict = ConfigValidator.validate_options({})
        options = Options(options_dict)

        dotfile_dict = ConfigValidator.validate_dotfile(
            {
                "category": "Test",
                "subcategory": "Sub",
                "application": "App",
                "description": "Description",
                "path": str(test_file),
                "mirror_dir": str(tmp_path / "mirror"),
                "archive_dir": str(tmp_path / "archive"),
            }
        )

        # Act
        dotfile = DotFile(dotfile_dict, options)

        # Assert
        assert dotfile.category == "Test"
        assert dotfile.subcategory == "Sub"
        assert dotfile.application == "App"
        assert dotfile.description == "Description"
        assert dotfile.exists is True
        assert dotfile.is_file is True

    def test_dotfile_string_representation(self, tmp_path: Path) -> None:
        """Test DotFile __str__ method returns formatted output."""
        # Arrange
        test_file = tmp_path / "repr_test.txt"
        test_file.write_text("Content")

        options_dict = ConfigValidator.validate_options({})
        options = Options(options_dict)

        dotfile_dict = ConfigValidator.validate_dotfile(
            {
                "category": "Repr",
                "subcategory": "Test",
                "application": "App",
                "description": "String representation test",
                "path": str(test_file),
                "mirror_dir": str(tmp_path / "mirror"),
                "archive_dir": str(tmp_path / "archive"),
            }
        )

        # Act
        dotfile = DotFile(dotfile_dict, options)
        output = str(dotfile)

        # Assert
        assert "Repr" in output
        assert "Test" in output
        assert "App" in output
        assert "repr_test.txt" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
