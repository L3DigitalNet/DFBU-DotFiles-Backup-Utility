"""
Test Multiple Paths Feature

Description:
    Comprehensive tests for multiple paths per dotfile feature including
    backward compatibility, category dropdowns, and UI integration.

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
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.model import DFBUModel


class TestModelBackwardCompatibility:
    """Test Model layer backward compatibility with legacy single path format."""

    def test_validate_dotfile_with_legacy_path(self, tmp_path):
        """Test _validate_dotfile converts legacy 'path' to 'paths' list."""
        # Create config file with legacy format
        config_path = tmp_path / "test_config.toml"
        config_content = """
[[dotfile]]
category = "Test"
subcategory = "Test"
application = "Test App"
description = "Test dotfile"
path = "~/.testrc"
enabled = true
"""
        config_path.write_text(config_content)

        # Load config
        model = DFBUModel(config_path)
        model.load_config()

        # Verify path was converted to paths list
        assert len(model.dotfiles) == 1
        dotfile = model.dotfiles[0]
        assert "paths" in dotfile
        assert isinstance(dotfile["paths"], list)
        assert len(dotfile["paths"]) == 1
        assert dotfile["paths"][0] == "~/.testrc"

    def test_validate_dotfile_with_new_paths(self, tmp_path):
        """Test _validate_dotfile handles new 'paths' format."""
        # Create config file with new format
        config_path = tmp_path / "test_config.toml"
        config_content = """
[[dotfile]]
category = "Test"
subcategory = "Test"
application = "Test App"
description = "Test dotfile"
paths = ["~/.testrc", "~/.test2rc", "~/.test3rc"]
enabled = true
"""
        config_path.write_text(config_content)

        # Load config
        model = DFBUModel(config_path)
        model.load_config()

        # Verify paths list is preserved
        assert len(model.dotfiles) == 1
        dotfile = model.dotfiles[0]
        assert "paths" in dotfile
        assert isinstance(dotfile["paths"], list)
        assert len(dotfile["paths"]) == 3
        assert dotfile["paths"] == ["~/.testrc", "~/.test2rc", "~/.test3rc"]

    def test_save_config_single_path_as_path(self, tmp_path):
        """Test save_config saves single path as 'path' for backward compatibility."""
        config_path = tmp_path / "test_config.toml"

        # Create model and add dotfile with single path
        model = DFBUModel(config_path)
        model.add_dotfile(
            "Test", "Test", "Test App", "Test dotfile", ["~/.testrc"], True
        )

        # Save config
        model.save_config()

        # Read raw config file
        content = config_path.read_text()

        # Verify saved as single "path" not "paths"
        assert 'path = "~/.testrc"' in content
        assert "paths = " not in content

    def test_save_config_multiple_paths_as_paths(self, tmp_path):
        """Test save_config saves multiple paths as 'paths' list."""
        config_path = tmp_path / "test_config.toml"

        # Create model and add dotfile with multiple paths
        model = DFBUModel(config_path)
        model.add_dotfile(
            "Test",
            "Test",
            "Test App",
            "Test dotfile",
            ["~/.testrc", "~/.test2rc"],
            True,
        )

        # Save config
        model.save_config()

        # Read raw config file
        content = config_path.read_text()

        # Verify saved as "paths" list
        assert "paths = " in content
        assert "~/.testrc" in content
        assert "~/.test2rc" in content


class TestModelValidationAndSizes:
    """Test Model validation and size calculation with multiple paths."""

    def test_validate_dotfile_paths_with_multiple_paths(self, tmp_path):
        """Test validate_dotfile_paths validates first path only."""
        config_path = tmp_path / "test_config.toml"

        # Create test files
        test_file1 = tmp_path / "testfile1.txt"
        test_file2 = tmp_path / "testfile2.txt"
        test_file1.write_text("Test content 1")
        test_file2.write_text("Test content 2")

        # Create model and add dotfile with multiple paths
        model = DFBUModel(config_path)
        model.add_dotfile(
            "Test",
            "Test",
            "Test App",
            "Test dotfile",
            [str(test_file1), str(test_file2)],
            True,
        )

        # Validate paths
        validation = model.validate_dotfile_paths()

        # Should validate first path only
        assert 0 in validation
        exists, is_dir, type_str = validation[0]
        assert exists is True
        assert is_dir is False
        assert type_str == "File"

    def test_get_dotfile_sizes_sums_all_paths(self, tmp_path):
        """Test get_dotfile_sizes sums sizes across all paths."""
        config_path = tmp_path / "test_config.toml"

        # Create test files with known sizes
        test_file1 = tmp_path / "testfile1.txt"
        test_file2 = tmp_path / "testfile2.txt"
        test_file1.write_text("A" * 100)  # 100 bytes
        test_file2.write_text("B" * 200)  # 200 bytes

        # Create model and add dotfile with multiple paths
        model = DFBUModel(config_path)
        model.add_dotfile(
            "Test",
            "Test",
            "Test App",
            "Test dotfile",
            [str(test_file1), str(test_file2)],
            True,
        )

        # Get sizes
        sizes = model.get_dotfile_sizes()

        # Should sum both files
        assert 0 in sizes
        assert sizes[0] == 300  # 100 + 200

    def test_get_dotfile_sizes_with_directory(self, tmp_path):
        """Test get_dotfile_sizes handles directories correctly."""
        config_path = tmp_path / "test_config.toml"

        # Create test directory with files
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()
        (test_dir / "file1.txt").write_text("A" * 50)
        (test_dir / "file2.txt").write_text("B" * 75)

        # Create model and add dotfile with directory path
        model = DFBUModel(config_path)
        model.add_dotfile(
            "Test", "Test", "Test App", "Test dotfile", [str(test_dir)], True
        )

        # Get sizes
        sizes = model.get_dotfile_sizes()

        # Should calculate directory size
        assert 0 in sizes
        assert sizes[0] == 125  # 50 + 75

    def test_get_dotfile_sizes_with_nonexistent_paths(self, tmp_path):
        """Test get_dotfile_sizes handles nonexistent paths gracefully."""
        config_path = tmp_path / "test_config.toml"

        # Create model with nonexistent paths
        model = DFBUModel(config_path)
        model.add_dotfile(
            "Test",
            "Test",
            "Test App",
            "Test dotfile",
            ["/nonexistent/path1.txt", "/nonexistent/path2.txt"],
            True,
        )

        # Get sizes
        sizes = model.get_dotfile_sizes()

        # Should return 0 for nonexistent paths
        assert 0 in sizes
        assert sizes[0] == 0


class TestModelAddUpdate:
    """Test Model add_dotfile and update_dotfile with multiple paths."""

    def test_add_dotfile_with_multiple_paths(self, tmp_path):
        """Test add_dotfile stores multiple paths correctly."""
        config_path = tmp_path / "test_config.toml"
        model = DFBUModel(config_path)

        # Add dotfile with multiple paths
        paths = ["~/.testrc", "~/.config/test.conf", "/etc/test.conf"]
        success = model.add_dotfile(
            "Test", "Test", "Test App", "Test dotfile", paths, True
        )

        assert success is True
        assert len(model.dotfiles) == 1
        assert model.dotfiles[0]["paths"] == paths

    def test_update_dotfile_with_multiple_paths(self, tmp_path):
        """Test update_dotfile updates paths list correctly."""
        config_path = tmp_path / "test_config.toml"
        model = DFBUModel(config_path)

        # Add initial dotfile
        model.add_dotfile(
            "Test", "Test", "Test App", "Test dotfile", ["~/.testrc"], True
        )

        # Update with multiple paths
        new_paths = ["~/.testrc", "~/.config/test.conf"]
        success = model.update_dotfile(
            0, "Test", "Test", "Test App Updated", "Updated desc", new_paths, True
        )

        assert success is True
        assert model.dotfiles[0]["paths"] == new_paths
        assert model.dotfiles[0]["application"] == "Test App Updated"


class TestModelRoundTrip:
    """Test complete save/load cycle with multiple paths."""

    def test_save_load_roundtrip_single_path(self, tmp_path):
        """Test save and reload config with single path."""
        config_path = tmp_path / "test_config.toml"

        # Create and save
        model1 = DFBUModel(config_path)
        model1.add_dotfile(
            "Category1", "Subcat1", "App1", "Description1", ["~/.testrc"], True
        )
        model1.save_config()

        # Reload in new model
        model2 = DFBUModel(config_path)
        model2.load_config()

        # Verify data
        assert len(model2.dotfiles) == 1
        assert model2.dotfiles[0]["paths"] == ["~/.testrc"]
        assert model2.dotfiles[0]["application"] == "App1"

    def test_save_load_roundtrip_multiple_paths(self, tmp_path):
        """Test save and reload config with multiple paths."""
        config_path = tmp_path / "test_config.toml"

        # Create and save
        model1 = DFBUModel(config_path)
        paths = ["~/.testrc", "~/.config/test.conf", "/etc/test.conf"]
        model1.add_dotfile("Category1", "Subcat1", "App1", "Description1", paths, True)
        model1.save_config()

        # Reload in new model
        model2 = DFBUModel(config_path)
        model2.load_config()

        # Verify data
        assert len(model2.dotfiles) == 1
        assert model2.dotfiles[0]["paths"] == paths
        assert model2.dotfiles[0]["application"] == "App1"

    def test_save_load_roundtrip_mixed(self, tmp_path):
        """Test save and reload config with mix of single and multiple paths."""
        config_path = tmp_path / "test_config.toml"

        # Create and save
        model1 = DFBUModel(config_path)
        model1.add_dotfile("Cat1", "Sub1", "App1", "Desc1", ["~/.single"], True)
        model1.add_dotfile(
            "Cat2", "Sub2", "App2", "Desc2", ["~/.multi1", "~/.multi2"], True
        )
        model1.save_config()

        # Reload in new model
        model2 = DFBUModel(config_path)
        model2.load_config()

        # Verify data
        assert len(model2.dotfiles) == 2
        assert model2.dotfiles[0]["paths"] == ["~/.single"]
        assert model2.dotfiles[1]["paths"] == ["~/.multi1", "~/.multi2"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
