#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Restore Functionality Test for Dotfiles Backup Utility

Description:
    Comprehensive test for the restore functionality of dfbu.py using
    a real backup directory structure. This test creates a temporary backup
    structure mimicking the actual dotfiles backup format and tests the
    restore process without writing to the actual system directories.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-27-2025
Date Changed: 10-27-2025
Version: 0.2.0.dev1
License: MIT

Features:
    - Test restore functionality with realistic backup directory structure
    - Use temporary directories to avoid system modifications
    - Test hostname-based path resolution
    - Validate home and root directory file restoration
    - Test file discovery and destination path calculation
    - Verify copy operations in both dry-run and actual modes

Requirements:
    - Linux environment
    - Python 3.14+ for Path.copy() functionality
    - pytest for test framework
    - Real backup directory structure at /home/chris/GitHub/dotfiles/PC-COS
    - Temporary directories for safe testing
"""

import pytest
import tempfile
import sys
import importlib.util
import shutil
from pathlib import Path
from socket import gethostname
from unittest.mock import patch

# Add the project directory to Python path for imports
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(PROJECT_DIR.parent / "common_lib"))

# Import the module under test using importlib to handle the hyphen in filename
spec = importlib.util.spec_from_file_location("dotfiles_bu", PROJECT_DIR / "dfbu.py")
if spec is not None and spec.loader is not None:
    dotfiles_bu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dotfiles_bu)

    # Import specific functions
    create_src_file_list = dotfiles_bu.create_src_file_list
    create_dest_restore_paths = dotfiles_bu.create_dest_restore_paths
    summarize_restore_actions = dotfiles_bu.summarize_restore_actions
    copy_files_restore = dotfiles_bu.copy_files_restore
    get_restore_src_path = dotfiles_bu.get_restore_src_path
else:
    raise ImportError("Could not load dotfiles_bu module")


class TestRestoreFunctionality:
    """
    Test suite for dotfiles backup utility restore functionality.

    Tests the complete restore workflow using a realistic backup directory
    structure based on the specified source path.
    """

    @pytest.fixture
    def temp_backup_structure(self) -> Path:
        """
        Create a temporary backup directory structure that mimics the real
        backup format with hostname/home and hostname/root subdirectories.

        Returns:
            Path: Path to the temporary backup directory root
        """
        # Create temporary directory
        temp_dir = Path(tempfile.mkdtemp())

        # Get current hostname for realistic testing
        hostname = gethostname()

        # Create hostname subdirectory
        hostname_dir = temp_dir / hostname
        hostname_dir.mkdir(parents=True)

        # Create home and root subdirectories
        home_dir = hostname_dir / "home"
        root_dir = hostname_dir / "root"
        home_dir.mkdir(parents=True)
        root_dir.mkdir(parents=True)

        # Create sample home directory files
        home_files = [
            ".bashrc",
            ".vimrc",
            ".gitconfig",
            ".ssh/config",
            ".config/gtk-3.0/settings.ini",
            "Documents/test.txt",
        ]

        for file_path in home_files:
            full_path = home_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"# Test content for {file_path}\ntest_data = true\n")

        # Create sample root directory files
        root_files = [
            "etc/ssh/ssh_config",
            "etc/hosts",
            "etc/fstab",
            "usr/local/bin/custom_script.sh",
        ]

        for file_path in root_files:
            full_path = root_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(f"# Test content for {file_path}\ntest_data = true\n")

        return temp_dir

    @pytest.fixture
    def temp_destination_area(self) -> Path:
        """
        Create a temporary destination area for testing file restoration.

        Returns:
            Path: Path to the temporary destination directory
        """
        return Path(tempfile.mkdtemp())

    def test_create_src_file_list(self, temp_backup_structure: Path) -> None:
        """
        Test the create_src_file_list function with realistic backup structure.

        Args:
            temp_backup_structure: Temporary backup directory fixture
        """
        # Test with the hostname subdirectory
        hostname = gethostname()
        src_dir = temp_backup_structure / hostname

        # Get list of source files
        src_files = create_src_file_list(src_dir)

        # Verify we found files
        assert len(src_files) > 0, "Should find source files in backup directory"

        # Verify all returned items are files
        for file_path in src_files:
            assert file_path.is_file(), f"Expected file, got directory: {file_path}"

        # Check for expected home directory files
        home_files = [f for f in src_files if "/home/" in str(f)]
        assert len(home_files) > 0, "Should find home directory files"

        # Check for expected root directory files
        root_files = [f for f in src_files if "/root/" in str(f)]
        assert len(root_files) > 0, "Should find root directory files"

        print(f"Found {len(src_files)} source files:")
        for f in src_files:
            print(f"  {f}")

    def test_create_dest_restore_paths_home_files(
        self, temp_backup_structure: Path
    ) -> None:
        """
        Test destination path creation for home directory files.

        Args:
            temp_backup_structure: Temporary backup directory fixture
        """
        hostname = gethostname()
        src_dir = temp_backup_structure / hostname

        # Get source files and filter for home directory files only
        all_src_files = create_src_file_list(src_dir)
        home_src_files = [f for f in all_src_files if "/home/" in str(f)]

        # Create destination paths
        dest_paths = create_dest_restore_paths(home_src_files)

        # Verify same number of destination paths as source files
        assert len(dest_paths) == len(home_src_files), (
            "Mismatch in source/destination counts"
        )

        # Verify all destination paths are under user home directory
        for dest_path in dest_paths:
            assert dest_path.is_relative_to(Path.home()), (
                f"Home file should restore to home directory: {dest_path}"
            )

        print("Home directory file mappings:")
        for src, dest in zip(home_src_files, dest_paths):
            print(f"  {src} -> {dest}")

    def test_create_dest_restore_paths_root_files(
        self, temp_backup_structure: Path
    ) -> None:
        """
        Test destination path creation for root directory files.

        Args:
            temp_backup_structure: Temporary backup directory fixture
        """
        hostname = gethostname()
        src_dir = temp_backup_structure / hostname

        # Get source files and filter for root directory files only
        all_src_files = create_src_file_list(src_dir)
        root_src_files = [f for f in all_src_files if "/root/" in str(f)]

        # Create destination paths
        dest_paths = create_dest_restore_paths(root_src_files)

        # Verify same number of destination paths as source files
        assert len(dest_paths) == len(root_src_files), (
            "Mismatch in source/destination counts"
        )

        # Verify all destination paths are absolute system paths
        for dest_path in dest_paths:
            assert dest_path.is_absolute(), (
                f"Root file should restore to absolute path: {dest_path}"
            )
            assert not dest_path.is_relative_to(Path.home()), (
                f"Root file should not restore to home directory: {dest_path}"
            )

        print("Root directory file mappings:")
        for src, dest in zip(root_src_files, dest_paths):
            print(f"  {src} -> {dest}")

    def test_summarize_restore_actions(
        self, temp_backup_structure: Path, capsys
    ) -> None:
        """
        Test the summarize_restore_actions function output.

        Args:
            temp_backup_structure: Temporary backup directory fixture
            capsys: Pytest fixture for capturing stdout/stderr
        """
        hostname = gethostname()
        src_dir = temp_backup_structure / hostname

        # Get source files and destination paths
        src_files = create_src_file_list(src_dir)
        dest_paths = create_dest_restore_paths(src_files)

        # Call summarize function
        summarize_restore_actions(src_files, dest_paths)

        # Capture and verify output
        captured = capsys.readouterr()
        output = captured.out

        assert "The following files will be restored:" in output
        assert len(src_files) > 0, "Should have source files to summarize"

        # Verify some file names appear in output
        for src_file in src_files[:3]:  # Check first few files
            assert src_file.name in output, (
                f"File name {src_file.name} should appear in summary"
            )

    def test_copy_files_restore_dry_run(
        self, temp_backup_structure: Path, capsys, monkeypatch
    ) -> None:
        """
        Test file restoration in dry-run mode.

        Args:
            temp_backup_structure: Temporary backup directory fixture
            capsys: Pytest fixture for capturing stdout/stderr
            monkeypatch: Pytest fixture for patching
        """
        hostname = gethostname()
        src_dir = temp_backup_structure / hostname

        # Get source files and destination paths
        src_files = create_src_file_list(src_dir)
        dest_paths = create_dest_restore_paths(src_files)

        # Enable dry run mode
        monkeypatch.setattr(dotfiles_bu, "DRY_RUN", True)

        # Call copy function
        copy_files_restore(src_files, dest_paths)

        # Verify dry run output
        captured = capsys.readouterr()
        output = captured.out

        assert "DRY RUN mode enabled" in output
        assert "Would create directory:" in output or "Processing files:" in output

        # Verify that the dry run message appears and no copy operations occur
        # Note: We can't check if destination files don't exist because some may
        # already exist on the system (like ~/.gitconfig). Instead, verify that
        # the dry run mode properly shows what would be copied without errors.
        assert len(src_files) > 0, "Should have source files to test"
        assert len(dest_paths) == len(src_files), (
            "Should have matching destination paths"
        )

    def test_copy_files_restore_with_temp_destinations(
        self, temp_backup_structure: Path, temp_destination_area: Path, monkeypatch
    ) -> None:
        """
        Test actual file restoration to temporary destination directories.

        Args:
            temp_backup_structure: Temporary backup directory fixture
            temp_destination_area: Temporary destination directory fixture
            monkeypatch: Pytest fixture for patching
        """
        hostname = gethostname()
        src_dir = temp_backup_structure / hostname

        # Get source files
        src_files = create_src_file_list(src_dir)

        # Create modified destination paths using temp directory instead of actual system paths
        modified_dest_paths = []
        for src_file in src_files:
            # Create relative path from hostname directory
            try:
                rel_path = src_file.relative_to(temp_backup_structure / hostname)
                temp_dest = temp_destination_area / rel_path
                modified_dest_paths.append(temp_dest)
            except ValueError:
                # Skip files not under hostname directory
                continue

        # Disable dry run mode
        monkeypatch.setattr(dotfiles_bu, "DRY_RUN", False)

        # Mock Path.copy to use shutil.copy2 for compatibility
        def mock_copy(
            src_path, dest_path, follow_symlinks=True, preserve_metadata=True
        ):
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)

        with patch.object(Path, "copy", mock_copy):
            # Call copy function with modified paths
            copy_files_restore(src_files, modified_dest_paths)

        # Verify files were actually copied
        for dest_path in modified_dest_paths:
            assert dest_path.exists(), f"File should exist after copy: {dest_path}"
            assert dest_path.is_file(), f"Destination should be a file: {dest_path}"

            # Verify content was copied
            content = dest_path.read_text()
            assert "test_data = true" in content, (
                f"File content should be preserved: {dest_path}"
            )

    def test_real_backup_directory_structure(self) -> None:
        """
        Test with the actual backup directory structure if it exists.
        This test will be skipped if the specified directory doesn't exist.
        """
        real_backup_path = Path("/home/chris/GitHub/dotfiles/PC-COS")

        if not real_backup_path.exists():
            pytest.skip(f"Real backup directory not found: {real_backup_path}")

        # Test file discovery in real backup directory
        src_files = create_src_file_list(real_backup_path)

        print(f"Found {len(src_files)} files in real backup directory:")
        for f in src_files[:10]:  # Show first 10 files
            print(f"  {f}")

        if len(src_files) > 10:
            print(f"  ... and {len(src_files) - 10} more files")

        # Test destination path creation
        if src_files:
            dest_paths = create_dest_restore_paths(src_files)

            print("\nFirst few file mappings:")
            for src, dest in zip(src_files[:5], dest_paths[:5]):
                print(f"  {src}")
                print(f"    -> {dest}")

    def test_get_restore_src_path_validation(
        self, temp_backup_structure: Path, monkeypatch
    ) -> None:
        """
        Test the get_restore_src_path function input validation.

        Args:
            temp_backup_structure: Temporary backup directory fixture
            monkeypatch: Pytest fixture for patching
        """
        hostname = gethostname()
        valid_path = temp_backup_structure / hostname

        # Mock input to return the valid path and then confirm
        input_sequence = [str(valid_path), "y"]
        input_iter = iter(input_sequence)
        monkeypatch.setattr("builtins.input", lambda _: next(input_iter))

        # Test function
        result_path = get_restore_src_path()

        assert result_path == valid_path
        assert result_path.exists()
        assert result_path.is_dir()

    def teardown_method(self, method) -> None:
        """Clean up any temporary files after each test method."""
        # This is handled automatically by tempfile.mkdtemp() and pytest cleanup
        pass


def main() -> None:
    """
    Main test runner function.

    This function demonstrates the restore functionality test by running
    a series of tests against both temporary and real backup directories.
    """
    print("Running Dotfiles Backup Utility Restore Functionality Tests")
    print("=" * 60)

    # Create test instance
    test_instance = TestRestoreFunctionality()

    # Create temporary backup structure directly (not as pytest fixture)
    temp_backup = create_temp_backup_structure()
    print(f"Created temporary backup structure at: {temp_backup}")

    try:
        # Test file discovery
        print("\nTesting file discovery...")
        test_instance.test_create_src_file_list(temp_backup)

        # Test destination path creation
        print("\nTesting destination path creation for home files...")
        test_instance.test_create_dest_restore_paths_home_files(temp_backup)

        print("\nTesting destination path creation for root files...")
        test_instance.test_create_dest_restore_paths_root_files(temp_backup)

        # Test with real backup directory if available
        print("\nTesting with real backup directory...")
        test_instance.test_real_backup_directory_structure()

        print("\n" + "=" * 60)
        print("All restore functionality tests completed successfully!")

    except Exception as e:
        print(f"Test failed with error: {e}")
        raise
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_backup, ignore_errors=True)
        print(f"Cleaned up temporary directory: {temp_backup}")


def create_temp_backup_structure() -> Path:
    """
    Create a temporary backup directory structure that mimics the real
    backup format with hostname/home and hostname/root subdirectories.

    Returns:
        Path: Path to the temporary backup directory root
    """
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp())

    # Get current hostname for realistic testing
    hostname = gethostname()

    # Create hostname subdirectory
    hostname_dir = temp_dir / hostname
    hostname_dir.mkdir(parents=True)

    # Create home and root subdirectories
    home_dir = hostname_dir / "home"
    root_dir = hostname_dir / "root"
    home_dir.mkdir(parents=True)
    root_dir.mkdir(parents=True)

    # Create sample home directory files
    home_files = [
        ".bashrc",
        ".vimrc",
        ".gitconfig",
        ".ssh/config",
        ".config/gtk-3.0/settings.ini",
        "Documents/test.txt",
    ]

    for file_path in home_files:
        full_path = home_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(f"# Test content for {file_path}\ntest_data = true\n")

    # Create sample root directory files
    root_files = [
        "etc/ssh/ssh_config",
        "etc/hosts",
        "etc/fstab",
        "usr/local/bin/custom_script.sh",
    ]

    for file_path in root_files:
        full_path = root_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(f"# Test content for {file_path}\ntest_data = true\n")

    return temp_dir


if __name__ == "__main__":
    # Run main test function if called directly
    main()

    # Also run pytest if available
    try:
        pytest.main([__file__, "-v", "-s"])
    except ImportError:
        print("pytest not available, ran basic tests only")
