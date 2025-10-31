#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for DFBU Restore Operations

Description:
    Comprehensive integration tests for restore workflow functions following
    pytest framework and AAA pattern. Tests focus on path resolution, file
    discovery, and restoration operations before v1.0.0.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-29-2025
Date Changed: 10-29-2025
License: MIT

Features:
    - Integration tests for restore source file discovery
    - Integration tests for destination path reconstruction
    - Integration tests for file copying during restore
    - Mock filesystem operations for safe testing
    - AAA pattern test structure for clarity
    - Pytest fixtures for backup directory structures
    - Hostname-based path resolution testing

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - pytest framework for testing
    - unittest.mock for filesystem mocking
"""

import sys
from pathlib import Path
from socket import gethostname
from unittest.mock import Mock, patch

import pytest

# Add project to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "common_lib"))

# Import module under test
from dfbug_cli_backup import (
    create_src_file_list,
    create_dest_restore_paths,
    copy_files_restore,
)


class TestCreateSrcFileList:
    """
    Test suite for create_src_file_list function.

    Tests recursive file discovery in backup directory structures.
    """

    @pytest.fixture
    def backup_structure(self, tmp_path: Path) -> Path:
        """Create realistic backup directory structure for testing."""
        # Create hostname subdirectory
        hostname_dir: Path = tmp_path / gethostname()
        hostname_dir.mkdir()

        # Create home directory structure
        home_dir: Path = hostname_dir / "home"
        home_dir.mkdir()
        (home_dir / ".bashrc").write_text("bash config")
        (home_dir / ".vimrc").write_text("vim config")
        (home_dir / ".config").mkdir()
        (home_dir / ".config" / "starship.toml").write_text("starship config")

        # Create root directory structure
        root_dir: Path = hostname_dir / "root"
        root_dir.mkdir()
        (root_dir / "etc").mkdir()
        (root_dir / "etc" / "hosts").write_text("127.0.0.1 localhost")
        (root_dir / "etc" / "ssh").mkdir()
        (root_dir / "etc" / "ssh" / "ssh_config").write_text("ssh config")

        return hostname_dir

    def test_discovers_all_files_in_backup(self, backup_structure: Path) -> None:
        """Test that all files in backup directory are discovered."""
        # Act
        result: list[Path] = create_src_file_list(backup_structure)

        # Assert
        assert len(result) == 5  # .bashrc, .vimrc, starship.toml, hosts, ssh_config
        assert all(f.is_file() for f in result)

    def test_excludes_directories_from_results(self, backup_structure: Path) -> None:
        """Test that directories are excluded from file list."""
        # Act
        result: list[Path] = create_src_file_list(backup_structure)

        # Assert
        assert all(not f.is_dir() for f in result)

    def test_discovers_nested_files(self, backup_structure: Path) -> None:
        """Test that deeply nested files are discovered."""
        # Act
        result: list[Path] = create_src_file_list(backup_structure)
        result_strs: list[str] = [str(f) for f in result]

        # Assert
        # Check for nested config file
        assert any(".config/starship.toml" in s for s in result_strs)
        # Check for nested ssh config
        assert any("etc/ssh/ssh_config" in s for s in result_strs)

    def test_handles_empty_directory(self, tmp_path: Path) -> None:
        """Test that empty directory returns empty list."""
        # Arrange
        empty_dir: Path = tmp_path / "empty"
        empty_dir.mkdir()

        # Act
        result: list[Path] = create_src_file_list(empty_dir)

        # Assert
        assert len(result) == 0


class TestCreateDestRestorePaths:
    """
    Test suite for create_dest_restore_paths function.

    Tests reconstruction of original file paths from backup structure.
    """

    @pytest.fixture
    def home_backup_files(self, tmp_path: Path) -> list[Path]:
        """Create list of backup file paths for home directory."""
        hostname: str = gethostname()
        base: Path = tmp_path / hostname / "home"
        base.mkdir(parents=True)

        files: list[Path] = [
            base / ".bashrc",
            base / ".vimrc",
            base / ".config" / "starship.toml",
        ]

        for f in files:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("test")

        return files

    @pytest.fixture
    def root_backup_files(self, tmp_path: Path) -> list[Path]:
        """Create list of backup file paths for root directory."""
        hostname: str = gethostname()
        base: Path = tmp_path / hostname / "root"
        base.mkdir(parents=True)

        files: list[Path] = [
            base / "etc" / "hosts",
            base / "etc" / "ssh" / "ssh_config",
        ]

        for f in files:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("test")

        return files

    def test_reconstructs_home_directory_paths(
        self, home_backup_files: list[Path]
    ) -> None:
        """Test that home directory paths are correctly reconstructed."""
        # Act
        result: list[Path] = create_dest_restore_paths(home_backup_files)

        # Assert
        assert len(result) == 3
        # All should be under user home directory
        assert all(p.is_relative_to(Path.home()) for p in result)
        # Check specific reconstructed paths
        assert any(p.name == ".bashrc" for p in result)
        assert any(p.name == ".vimrc" for p in result)
        assert any(p.name == "starship.toml" for p in result)

    def test_reconstructs_root_directory_paths(
        self, root_backup_files: list[Path]
    ) -> None:
        """Test that root directory paths are correctly reconstructed."""
        # Act
        result: list[Path] = create_dest_restore_paths(root_backup_files)

        # Assert
        assert len(result) == 2
        # All should be absolute paths
        assert all(p.is_absolute() for p in result)
        # Should not be under home directory
        assert all(not p.is_relative_to(Path.home()) for p in result)
        # Check specific reconstructed paths
        assert any(p == Path("/etc/hosts") for p in result)
        assert any(p == Path("/etc/ssh/ssh_config") for p in result)

    def test_preserves_nested_structure(self, home_backup_files: list[Path]) -> None:
        """Test that nested directory structure is preserved in destination."""
        # Act
        result: list[Path] = create_dest_restore_paths(home_backup_files)

        # Assert
        # Find the starship.toml path
        starship_paths = [p for p in result if p.name == "starship.toml"]
        assert len(starship_paths) == 1
        # Should maintain .config subdirectory
        assert starship_paths[0].parent.name == "starship" or ".config" in str(
            starship_paths[0].parent
        )

    def test_returns_same_count_as_input(
        self, home_backup_files: list[Path], root_backup_files: list[Path]
    ) -> None:
        """Test that output has same number of paths as input."""
        # Act
        home_result: list[Path] = create_dest_restore_paths(home_backup_files)
        root_result: list[Path] = create_dest_restore_paths(root_backup_files)

        # Assert
        assert len(home_result) == len(home_backup_files)
        assert len(root_result) == len(root_backup_files)

    def test_handles_empty_list(self) -> None:
        """Test that empty input list returns empty output list."""
        # Arrange
        empty_list: list[Path] = []

        # Act
        result: list[Path] = create_dest_restore_paths(empty_list)

        # Assert
        assert len(result) == 0


class TestCopyFilesRestore:
    """
    Test suite for copy_files_restore function.

    Tests file copying during restore operations with both
    dry-run and active modes.
    """

    @pytest.fixture
    def source_and_dest_files(self, tmp_path: Path) -> tuple[list[Path], list[Path]]:
        """Create matching source and destination file lists."""
        # Create source files
        src_dir: Path = tmp_path / "source"
        src_dir.mkdir()
        src_files: list[Path] = [
            src_dir / "file1.txt",
            src_dir / "file2.txt",
            src_dir / "subdir" / "file3.txt",
        ]

        for f in src_files:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(f"content of {f.name}")

        # Create destination paths
        dest_dir: Path = tmp_path / "dest"
        dest_files: list[Path] = [
            dest_dir / "file1.txt",
            dest_dir / "file2.txt",
            dest_dir / "subdir" / "file3.txt",
        ]

        return src_files, dest_files

    def test_copy_files_in_dry_run_mode(
        self,
        source_and_dest_files: tuple[list[Path], list[Path]],
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test file copying in dry-run mode."""
        # Arrange
        src_files, dest_files = source_and_dest_files
        dry_run: bool = True

        # Act
        copy_files_restore(src_files, dest_files, dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "DRY RUN mode enabled" in captured.out
        # Files should not be created
        assert not any(d.exists() for d in dest_files)

    @patch.object(Path, "copy")
    def test_copy_files_in_active_mode(
        self,
        mock_copy: Mock,
        source_and_dest_files: tuple[list[Path], list[Path]],
    ) -> None:
        """Test file copying in active (non-dry-run) mode."""
        # Arrange
        src_files, dest_files = source_and_dest_files
        dry_run: bool = False

        # Act
        copy_files_restore(src_files, dest_files, dry_run)

        # Assert
        # Should have called copy for each file
        assert mock_copy.call_count == len(src_files)

    @patch("dfbu.FileSystemHelper.create_directory")
    def test_creates_parent_directories(
        self,
        mock_create_dir: Mock,
        source_and_dest_files: tuple[list[Path], list[Path]],
    ) -> None:
        """Test that parent directories are created before copying."""
        # Arrange
        src_files, dest_files = source_and_dest_files
        dry_run: bool = False

        # Act
        with patch.object(Path, "copy"):
            copy_files_restore(src_files, dest_files, dry_run)

        # Assert
        # Should have created directories for all destination parent paths
        assert mock_create_dir.call_count >= 1

    def test_displays_progress_during_copy(
        self,
        source_and_dest_files: tuple[list[Path], list[Path]],
        capsys: pytest.CaptureFixture,
    ) -> None:
        """Test that progress messages are displayed during copying."""
        # Arrange
        src_files, dest_files = source_and_dest_files
        dry_run: bool = False

        # Act
        with patch.object(Path, "copy"):
            copy_files_restore(src_files, dest_files, dry_run)

        # Assert
        captured = capsys.readouterr()
        assert "Processing files:" in captured.out
        # Should show individual file names
        assert "file1.txt" in captured.out or "copying" in captured.out

    def test_handles_empty_file_lists(self) -> None:
        """Test that empty file lists are handled gracefully."""
        # Arrange
        src_files: list[Path] = []
        dest_files: list[Path] = []
        dry_run: bool = False

        # Act & Assert - should not raise exception
        copy_files_restore(src_files, dest_files, dry_run)

    def test_processes_all_files_in_list(
        self, source_and_dest_files: tuple[list[Path], list[Path]]
    ) -> None:
        """Test that all files in the list are processed."""
        # Arrange
        src_files, dest_files = source_and_dest_files
        dry_run: bool = False

        # Act
        with patch.object(Path, "copy") as mock_copy:
            copy_files_restore(src_files, dest_files, dry_run)

        # Assert
        # Verify each source file was copied to corresponding destination
        assert mock_copy.call_count == len(src_files)


class TestRestoreWorkflowIntegration:
    """
    Test suite for complete restore workflow integration.

    Tests the full restore workflow from file discovery through
    destination path calculation to actual file copying.
    """

    @pytest.fixture
    def complete_backup_structure(self, tmp_path: Path) -> Path:
        """Create complete backup structure mimicking real backup."""
        hostname: str = gethostname()
        hostname_dir: Path = tmp_path / hostname
        hostname_dir.mkdir()

        # Create home files
        home_dir: Path = hostname_dir / "home"
        home_dir.mkdir()
        (home_dir / ".bashrc").write_text("bash config")
        (home_dir / ".config").mkdir()
        (home_dir / ".config" / "starship.toml").write_text("starship")

        # Create root files
        root_dir: Path = hostname_dir / "root"
        root_dir.mkdir()
        (root_dir / "etc").mkdir()
        (root_dir / "etc" / "hosts").write_text("hosts file")

        return hostname_dir

    def test_complete_restore_workflow(self, complete_backup_structure: Path) -> None:
        """Test complete workflow from discovery to path reconstruction."""
        # Act - Step 1: Discover files
        src_files: list[Path] = create_src_file_list(complete_backup_structure)

        # Assert - Files discovered
        assert len(src_files) > 0

        # Act - Step 2: Create destination paths
        dest_paths: list[Path] = create_dest_restore_paths(src_files)

        # Assert - Paths created
        assert len(dest_paths) == len(src_files)
        # Home files should go to home directory
        home_files = [p for p in dest_paths if p.is_relative_to(Path.home())]
        assert len(home_files) >= 2  # .bashrc and starship.toml
        # Root files should go to root
        root_files = [
            p
            for p in dest_paths
            if not p.is_relative_to(Path.home()) and p.is_absolute()
        ]
        assert len(root_files) >= 1  # etc/hosts

    def test_workflow_preserves_file_count(
        self, complete_backup_structure: Path
    ) -> None:
        """Test that file count is preserved through workflow steps."""
        # Act
        src_files: list[Path] = create_src_file_list(complete_backup_structure)
        dest_paths: list[Path] = create_dest_restore_paths(src_files)

        # Assert
        assert len(src_files) == len(dest_paths)

    def test_workflow_with_dry_run_copy(
        self, complete_backup_structure: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test complete workflow with dry-run file copy."""
        # Act
        src_files: list[Path] = create_src_file_list(complete_backup_structure)
        dest_paths: list[Path] = create_dest_restore_paths(src_files)
        copy_files_restore(src_files, dest_paths, dry_run=True)

        # Assert
        captured = capsys.readouterr()
        assert "DRY RUN" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
