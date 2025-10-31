#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test incremental mirror backup functionality.

Tests the file comparison and skip_identical optimization for mirror backups.
"""

import os
import time
from pathlib import Path
import pytest
from src.model import DFBUModel


def test_files_are_identical_nonexistent_dest(tmp_path):
    """Test files_are_identical returns False when destination doesn't exist."""
    # Arrange: Create source file only
    src_file = tmp_path / "source.txt"
    src_file.write_text("test content")
    dest_file = tmp_path / "dest.txt"

    config_path = tmp_path / "config.toml"
    model = DFBUModel(config_path)

    # Act & Assert
    assert not model.files_are_identical(src_file, dest_file)


def test_files_are_identical_different_size(tmp_path):
    """Test files_are_identical returns False when sizes differ."""
    # Arrange: Create files with different sizes
    src_file = tmp_path / "source.txt"
    src_file.write_text("short")
    dest_file = tmp_path / "dest.txt"
    dest_file.write_text("much longer content")

    config_path = tmp_path / "config.toml"
    model = DFBUModel(config_path)

    # Act & Assert
    assert not model.files_are_identical(src_file, dest_file)


def test_files_are_identical_different_mtime(tmp_path):
    """Test files_are_identical returns False when modification times differ significantly."""
    # Arrange: Create files with same size but different mtimes
    src_file = tmp_path / "source.txt"
    dest_file = tmp_path / "dest.txt"

    content = "same content"
    src_file.write_text(content)
    dest_file.write_text(content)

    # Modify mtime of dest to be significantly older
    dest_stat = dest_file.stat()
    old_mtime = dest_stat.st_mtime - 10.0  # 10 seconds older
    os.utime(dest_file, (old_mtime, old_mtime))

    config_path = tmp_path / "config.toml"
    model = DFBUModel(config_path)

    # Act & Assert
    assert not model.files_are_identical(src_file, dest_file)


def test_files_are_identical_same_files(tmp_path):
    """Test files_are_identical returns True when files are the same."""
    # Arrange: Create identical files
    src_file = tmp_path / "source.txt"
    dest_file = tmp_path / "dest.txt"

    content = "identical content"
    src_file.write_text(content)

    # Copy with metadata preservation
    import shutil
    shutil.copy2(src_file, dest_file)

    config_path = tmp_path / "config.toml"
    model = DFBUModel(config_path)

    # Act & Assert
    assert model.files_are_identical(src_file, dest_file)


def test_copy_file_skip_identical_true(tmp_path):
    """Test copy_file with skip_identical=True skips identical files."""
    # Arrange: Create identical files
    src_file = tmp_path / "source.txt"
    dest_file = tmp_path / "dest.txt"

    content = "test content"
    src_file.write_text(content)

    import shutil
    shutil.copy2(src_file, dest_file)

    # Modify source slightly but keep same size and mtime
    original_mtime = dest_file.stat().st_mtime

    config_path = tmp_path / "config.toml"
    model = DFBUModel(config_path)

    # Act: Copy with skip_identical=True
    result = model.copy_file(src_file, dest_file, skip_identical=True)

    # Assert: Operation succeeds and file is unchanged
    assert result is True
    assert dest_file.stat().st_mtime == original_mtime


def test_copy_file_skip_identical_false_overwrites(tmp_path):
    """Test copy_file with skip_identical=False always copies."""
    # Arrange: Create different files
    src_file = tmp_path / "source.txt"
    dest_file = tmp_path / "dest.txt"

    src_file.write_text("new content")
    dest_file.write_text("old content")

    config_path = tmp_path / "config.toml"
    model = DFBUModel(config_path)

    # Act: Copy with skip_identical=False
    result = model.copy_file(src_file, dest_file, skip_identical=False)

    # Assert: File is overwritten
    assert result is True
    assert dest_file.read_text() == "new content"


def test_copy_directory_skip_identical(tmp_path):
    """Test copy_directory with skip_identical skips unchanged files."""
    # Arrange: Create source directory with files
    src_dir = tmp_path / "source"
    src_dir.mkdir()

    (src_dir / "file1.txt").write_text("content 1")
    (src_dir / "file2.txt").write_text("content 2")

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    # Copy once to establish identical files
    import shutil
    shutil.copy2(src_dir / "file1.txt", dest_dir / "file1.txt")
    shutil.copy2(src_dir / "file2.txt", dest_dir / "file2.txt")

    config_path = tmp_path / "config.toml"
    model = DFBUModel(config_path)

    # Act: Copy directory with skip_identical=True
    results = model.copy_directory(src_dir, dest_dir, skip_identical=True)

    # Assert: Both files are skipped (success=True, skipped=True)
    assert len(results) == 2
    for src_file, dest_file, success, skipped in results:
        assert success is True
        assert skipped is True


def test_copy_directory_with_changes(tmp_path):
    """Test copy_directory copies only changed files."""
    # Arrange: Create source directory with files
    src_dir = tmp_path / "source"
    src_dir.mkdir()

    (src_dir / "unchanged.txt").write_text("same")

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir()

    # Copy unchanged file with metadata
    import shutil
    shutil.copy2(src_dir / "unchanged.txt", dest_dir / "unchanged.txt")

    # Create changed file with different size (will fail identical check)
    (src_dir / "changed.txt").write_text("new version")
    (dest_dir / "changed.txt").write_text("old")  # Different size

    # Wait to ensure different mtime for changed file
    time.sleep(0.01)

    config_path = tmp_path / "config.toml"
    model = DFBUModel(config_path)

    # Act: Copy directory with skip_identical=True
    results = model.copy_directory(src_dir, dest_dir, skip_identical=True)

    # Assert: One file skipped, one file copied
    assert len(results) == 2

    skipped_files = [r for r in results if r[3]]  # r[3] is skipped flag
    copied_files = [r for r in results if not r[3]]

    assert len(skipped_files) == 1
    assert len(copied_files) == 1
    assert skipped_files[0][0].name == "unchanged.txt"
    assert copied_files[0][0].name == "changed.txt"

    # Verify content was actually updated
    assert (dest_dir / "changed.txt").read_text() == "new version"
