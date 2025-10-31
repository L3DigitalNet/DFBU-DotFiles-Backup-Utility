#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for DFBU Backup Operations

Description:
    Comprehensive integration tests for MirrorBackup and ArchiveBackup classes
    following pytest framework and AAA pattern. Tests focus on backup workflow
    integration with mocked filesystem operations before v1.0.0.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-29-2025
Date Changed: 10-29-2025
License: MIT

Features:
    - Integration tests for MirrorBackup file and directory operations
    - Integration tests for ArchiveBackup creation and rotation
    - Mock filesystem operations for safe testing
    - AAA pattern test structure for clarity
    - Pytest fixtures for test data setup
    - Dry-run and active mode testing
    - Archive rotation logic validation

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - pytest framework for testing
    - unittest.mock for filesystem mocking
    - tarfile module for archive operations
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

# Add project to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common_lib"))

# Import module under test
from dfbu import (
    MirrorBackup,
    ArchiveBackup,
    DotFile,
    Options,
    DotFileDict,
    OptionsDict,
)


class TestMirrorBackup:
    """
    Test suite for MirrorBackup class functionality.

    Tests mirror backup operations including file copying,
    directory recursion, and permission handling.
    """

    @pytest.fixture
    def basic_options(self) -> Options:
        """Create basic Options instance for testing."""
        options_dict: OptionsDict = {
            "mirror": True,
            "archive": False,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": False,
            "max_archives": 5,
        }
        return Options(options_dict)

    @pytest.fixture
    def test_file_dotfile(self, tmp_path: Path, basic_options: Options) -> DotFile:
        """Create DotFile instance for existing test file."""
        # Create test file
        test_file: Path = tmp_path / "test.txt"
        test_file.write_text("test content")

        dotfile_dict: DotFileDict = {
            "category": "Test",
            "subcategory": "Test",
            "application": "Test",
            "description": "Test file",
            "path": str(test_file),
            "mirror_dir": str(tmp_path / "mirror"),
            "archive_dir": str(tmp_path / "archive"),
        }
        return DotFile(dotfile_dict, basic_options)

    @pytest.fixture
    def test_dir_dotfile(self, tmp_path: Path, basic_options: Options) -> DotFile:
        """Create DotFile instance for existing test directory."""
        # Create test directory with files
        test_dir: Path = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("content 1")
        (test_dir / "file2.txt").write_text("content 2")
        (test_dir / "subdir").mkdir()
        (test_dir / "subdir" / "file3.txt").write_text("content 3")

        dotfile_dict: DotFileDict = {
            "category": "Test",
            "subcategory": "Test",
            "application": "Test",
            "description": "Test directory",
            "path": str(test_dir),
            "mirror_dir": str(tmp_path / "mirror"),
            "archive_dir": str(tmp_path / "archive"),
        }
        return DotFile(dotfile_dict, basic_options)

    def test_execute_with_empty_list(self, capsys: pytest.CaptureFixture) -> None:
        """Test MirrorBackup.execute with empty dotfiles list."""
        # Arrange
        dotfiles: list[DotFile] = []
        dry_run: bool = False

        # Act
        MirrorBackup.execute(dotfiles, dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "Copying..." in captured.out

    def test_execute_skips_nonexistent_files(
        self, basic_options: Options, capsys: pytest.CaptureFixture
    ) -> None:
        """Test that nonexistent files are skipped during execution."""
        # Arrange
        dotfile_dict: DotFileDict = {
            "category": "Test",
            "subcategory": "Test",
            "application": "Test",
            "description": "Nonexistent",
            "path": "/nonexistent/file.txt",
            "mirror_dir": "~/test",
            "archive_dir": "~/test",
        }
        dotfile: DotFile = DotFile(dotfile_dict, basic_options)
        dry_run: bool = False

        # Act
        MirrorBackup.execute([dotfile], dry_run)

        # Assert
        captured = capsys.readouterr()
        # Should not try to process nonexistent file
        assert "Processing" not in captured.out or "nonexistent" not in captured.out

    @patch("dfbu.FileSystemHelper.check_readable")
    @patch.object(Path, "copy")
    def test_process_file_in_active_mode(
        self,
        mock_copy: Mock,
        mock_readable: Mock,
        test_file_dotfile: DotFile,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test file processing in active (non-dry-run) mode."""
        # Arrange
        mock_readable.return_value = True
        dry_run: bool = False

        # Act
        MirrorBackup.execute([test_file_dotfile], dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "Processing file:" in captured.out
        mock_copy.assert_called_once()

    @patch("dfbu.FileSystemHelper.check_readable")
    def test_process_file_in_dry_run_mode(
        self,
        mock_readable: Mock,
        test_file_dotfile: DotFile,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test file processing in dry-run mode."""
        # Arrange
        mock_readable.return_value = True
        dry_run: bool = True

        # Act
        MirrorBackup.execute([test_file_dotfile], dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "[DRY RUN]" in captured.out
        assert "Would copy:" in captured.out

    @patch("dfbu.FileSystemHelper.check_readable")
    def test_process_file_skips_unreadable(
        self,
        mock_readable: Mock,
        test_file_dotfile: DotFile,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test that unreadable files are skipped."""
        # Arrange
        mock_readable.return_value = False
        dry_run: bool = False

        # Act
        MirrorBackup.execute([test_file_dotfile], dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "permission denied" in captured.out or "Skipped" in captured.out

    @patch("dfbu.FileSystemHelper.check_readable")
    @patch.object(Path, "copy")
    def test_process_directory_copies_all_files(
        self,
        mock_copy: Mock,
        mock_readable: Mock,
        test_dir_dotfile: DotFile,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test that directory processing copies all contained files."""
        # Arrange
        mock_readable.return_value = True
        dry_run: bool = False

        # Act
        MirrorBackup.execute([test_dir_dotfile], dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "Processing directory:" in captured.out
        # Should have copied 3 files (file1.txt, file2.txt, subdir/file3.txt)
        assert mock_copy.call_count == 3

    @patch("dfbu.FileSystemHelper.check_readable")
    def test_process_directory_in_dry_run_mode(
        self,
        mock_readable: Mock,
        test_dir_dotfile: DotFile,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test directory processing in dry-run mode."""
        # Arrange
        mock_readable.return_value = True
        dry_run: bool = True

        # Act
        MirrorBackup.execute([test_dir_dotfile], dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "[DRY RUN]" in captured.out
        assert "Processing directory:" in captured.out

    @patch("dfbu.FileSystemHelper.check_readable")
    @patch("dfbu.FileSystemHelper.create_directory")
    @patch.object(Path, "copy")
    def test_creates_parent_directories_for_files(
        self,
        mock_copy: Mock,
        mock_create_dir: Mock,
        mock_readable: Mock,
        test_file_dotfile: DotFile,
    ) -> None:
        """Test that parent directories are created before copying files."""
        # Arrange
        mock_readable.return_value = True
        dry_run: bool = False

        # Act
        MirrorBackup.execute([test_file_dotfile], dry_run)

        # Assert
        mock_create_dir.assert_called()


class TestArchiveBackup:
    """
    Test suite for ArchiveBackup class functionality.

    Tests archive creation, rotation, and compression operations.
    """

    @pytest.fixture
    def basic_options(self) -> Options:
        """Create basic Options instance for testing."""
        options_dict: OptionsDict = {
            "mirror": True,
            "archive": True,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": True,
            "max_archives": 3,
        }
        return Options(options_dict)

    @pytest.fixture
    def test_dotfiles(self, tmp_path: Path, basic_options: Options) -> list[DotFile]:
        """Create list of test DotFile instances."""
        # Create test files
        file1: Path = tmp_path / "file1.txt"
        file1.write_text("content 1")
        file2: Path = tmp_path / "file2.txt"
        file2.write_text("content 2")

        dotfile_dicts: list[DotFileDict] = [
            {
                "category": "Test",
                "subcategory": "Test",
                "application": "Test1",
                "description": "Test file 1",
                "path": str(file1),
                "mirror_dir": str(tmp_path / "mirror"),
                "archive_dir": str(tmp_path / "archive"),
            },
            {
                "category": "Test",
                "subcategory": "Test",
                "application": "Test2",
                "description": "Test file 2",
                "path": str(file2),
                "mirror_dir": str(tmp_path / "mirror"),
                "archive_dir": str(tmp_path / "archive"),
            },
        ]
        return [DotFile(d, basic_options) for d in dotfile_dicts]

    @patch("tarfile.open")
    def test_create_archive_in_active_mode(
        self,
        mock_tarfile: Mock,
        test_dotfiles: list[DotFile],
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test archive creation in active (non-dry-run) mode."""
        # Arrange
        mock_tar = MagicMock()
        mock_tarfile.return_value.__enter__.return_value = mock_tar
        archive_path: Path = tmp_path / "archive"
        dry_run: bool = False

        # Act
        ArchiveBackup.create(test_dotfiles, archive_path, dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "Creating archive" in captured.out
        assert "Packaging:" in captured.out
        mock_tarfile.assert_called_once()
        # Should have added 2 files to archive
        assert mock_tar.add.call_count == 2

    def test_create_archive_in_dry_run_mode(
        self,
        test_dotfiles: list[DotFile],
        tmp_path: Path,
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test archive creation in dry-run mode."""
        # Arrange
        archive_path: Path = tmp_path / "archive"
        dry_run: bool = True

        # Act
        ArchiveBackup.create(test_dotfiles, archive_path, dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "[DRY RUN]" in captured.out
        assert "Would package:" in captured.out
        assert "would be created" in captured.out

    def test_create_archive_skips_nonexistent_files(
        self, basic_options: Options, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test that nonexistent files are skipped in archive creation."""
        # Arrange
        dotfile_dict: DotFileDict = {
            "category": "Test",
            "subcategory": "Test",
            "application": "Test",
            "description": "Nonexistent",
            "path": "/nonexistent/file.txt",
            "mirror_dir": str(tmp_path / "mirror"),
            "archive_dir": str(tmp_path / "archive"),
        }
        dotfile: DotFile = DotFile(dotfile_dict, basic_options)
        archive_path: Path = tmp_path / "archive"
        dry_run: bool = True

        # Act
        ArchiveBackup.create([dotfile], archive_path, dry_run)

        # Assert
        captured = capsys.readouterr()
        # Should not package nonexistent file
        assert "nonexistent" not in captured.out.lower()

    def test_rotate_deletes_excess_archives(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test that archive rotation deletes oldest archives."""
        # Arrange
        archive_dir: Path = tmp_path / "archive"
        archive_dir.mkdir()

        # Create 5 test archives with different timestamps
        for i in range(5):
            archive_file: Path = (
                archive_dir / f"dotfiles-2025-10-{20 + i:02d}_12-00-00.tar.gz"
            )
            archive_file.write_text(f"archive {i}")

        max_archives: int = 3
        dry_run: bool = False

        # Act
        ArchiveBackup.rotate(archive_dir, max_archives, dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "Rotating archives" in captured.out
        # Should have deleted 2 oldest archives (5 - 3 = 2)
        remaining_archives = list(archive_dir.glob("dotfiles-*.tar.gz"))
        assert len(remaining_archives) == max_archives

    def test_rotate_in_dry_run_mode(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test archive rotation in dry-run mode."""
        # Arrange
        archive_dir: Path = tmp_path / "archive"
        archive_dir.mkdir()

        # Create 5 test archives
        for i in range(5):
            archive_file: Path = (
                archive_dir / f"dotfiles-2025-10-{20 + i:02d}_12-00-00.tar.gz"
            )
            archive_file.write_text(f"archive {i}")

        max_archives: int = 2
        dry_run: bool = True

        # Act
        ArchiveBackup.rotate(archive_dir, max_archives, dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "[DRY RUN]" in captured.out
        assert "Would delete" in captured.out
        # Files should still exist in dry-run mode
        remaining_archives = list(archive_dir.glob("dotfiles-*.tar.gz"))
        assert len(remaining_archives) == 5

    def test_rotate_with_no_excess_archives(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test archive rotation when no deletion is needed."""
        # Arrange
        archive_dir: Path = tmp_path / "archive"
        archive_dir.mkdir()

        # Create 2 test archives
        for i in range(2):
            archive_file: Path = (
                archive_dir / f"dotfiles-2025-10-{20 + i:02d}_12-00-00.tar.gz"
            )
            archive_file.write_text(f"archive {i}")

        max_archives: int = 5
        dry_run: bool = False

        # Act
        ArchiveBackup.rotate(archive_dir, max_archives, dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "No archives need to be deleted" in captured.out
        remaining_archives = list(archive_dir.glob("dotfiles-*.tar.gz"))
        assert len(remaining_archives) == 2

    def test_rotate_deletes_oldest_first(self, tmp_path: Path) -> None:
        """Test that rotation deletes oldest archives first based on mtime."""
        # Arrange
        archive_dir: Path = tmp_path / "archive"
        archive_dir.mkdir()

        # Create archives and track oldest
        oldest_archive: Path = archive_dir / "dotfiles-2025-10-20_12-00-00.tar.gz"
        oldest_archive.write_text("oldest")

        for i in range(1, 4):
            archive_file: Path = (
                archive_dir / f"dotfiles-2025-10-{20 + i:02d}_12-00-00.tar.gz"
            )
            archive_file.write_text(f"archive {i}")

        max_archives: int = 3
        dry_run: bool = False

        # Act
        ArchiveBackup.rotate(archive_dir, max_archives, dry_run)

        # Assert
        assert not oldest_archive.exists()
        remaining_archives = list(archive_dir.glob("dotfiles-*.tar.gz"))
        assert len(remaining_archives) == max_archives


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
