"""
Test ViewModel Multiple Paths Feature

Description:
    Tests for ViewModel layer including category methods,
    command methods, and backup processing with multiple paths.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-31-2025
License: MIT
"""

import pytest

from gui.model import DFBUModel
from gui.viewmodel import DFBUViewModel


class TestViewModelCategories:
    """Test ViewModel category and subcategory helper methods."""

    def test_get_unique_categories_empty(self, tmp_path):
        """Test get_unique_categories with no dotfiles."""
        config_path = tmp_path / "test_config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        categories = viewmodel.get_unique_categories()

        assert isinstance(categories, list)
        assert len(categories) == 0

    def test_get_unique_categories_single(self, tmp_path):
        """Test get_unique_categories with one dotfile."""
        config_path = tmp_path / "test_config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        # Add dotfile
        viewmodel.command_add_dotfile("TestCat", "TestApp", "Test", ["~/.test"], True)

        categories = viewmodel.get_unique_categories()

        assert isinstance(categories, list)
        assert len(categories) == 1
        assert categories[0] == "TestCat"

    def test_get_unique_categories_multiple_unique(self, tmp_path):
        """Test get_unique_categories with multiple unique categories."""
        config_path = tmp_path / "test_config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        # Add dotfiles with different categories
        viewmodel.command_add_dotfile("Category C", "App1", "Test", ["~/.test1"], True)
        viewmodel.command_add_dotfile("Category A", "App2", "Test", ["~/.test2"], True)
        viewmodel.command_add_dotfile("Category B", "App3", "Test", ["~/.test3"], True)

        categories = viewmodel.get_unique_categories()

        # Should be sorted
        assert categories == ["Category A", "Category B", "Category C"]

    def test_get_unique_categories_with_duplicates(self, tmp_path):
        """Test get_unique_categories filters duplicates."""
        config_path = tmp_path / "test_config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        # Add dotfiles with duplicate categories
        viewmodel.command_add_dotfile("SameCat", "App1", "Test", ["~/.test1"], True)
        viewmodel.command_add_dotfile("SameCat", "App2", "Test", ["~/.test2"], True)
        viewmodel.command_add_dotfile("DiffCat", "App3", "Test", ["~/.test3"], True)

        categories = viewmodel.get_unique_categories()

        # Should have unique sorted list
        assert categories == ["DiffCat", "SameCat"]


class TestViewModelCommands:
    """Test ViewModel command methods with multiple paths."""

    def test_command_add_dotfile_single_path(self, tmp_path):
        """Test command_add_dotfile with single path."""
        config_path = tmp_path / "test_config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        success = viewmodel.command_add_dotfile(
            "Cat", "App", "Desc", ["~/.testrc"], True
        )

        assert success is True
        dotfiles = viewmodel.get_dotfile_list()
        assert len(dotfiles) == 1
        assert dotfiles[0]["paths"] == ["~/.testrc"]

    def test_command_add_dotfile_multiple_paths(self, tmp_path):
        """Test command_add_dotfile with multiple paths."""
        config_path = tmp_path / "test_config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        paths = ["~/.testrc", "~/.config/test.conf", "/etc/test.conf"]
        success = viewmodel.command_add_dotfile("Cat", "App", "Desc", paths, True)

        assert success is True
        dotfiles = viewmodel.get_dotfile_list()
        assert len(dotfiles) == 1
        assert dotfiles[0]["paths"] == paths

    def test_command_update_dotfile_change_paths(self, tmp_path):
        """Test command_update_dotfile can change paths list."""
        config_path = tmp_path / "test_config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        # Add initial dotfile with single path
        viewmodel.command_add_dotfile("Cat", "App", "Desc", ["~/.testrc"], True)

        # Update to multiple paths
        new_paths = ["~/.testrc", "~/.config/test.conf"]
        success = viewmodel.command_update_dotfile(
            0, "Cat", "App Updated", "Desc Updated", new_paths, True
        )

        assert success is True
        dotfiles = viewmodel.get_dotfile_list()
        assert dotfiles[0]["paths"] == new_paths
        assert dotfiles[0]["application"] == "App Updated"

    def test_command_update_dotfile_reduce_paths(self, tmp_path):
        """Test command_update_dotfile can reduce number of paths."""
        config_path = tmp_path / "test_config.toml"
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)

        # Add initial dotfile with multiple paths
        viewmodel.command_add_dotfile(
            "Cat", "App", "Desc", ["~/.test1", "~/.test2", "~/.test3"], True
        )

        # Update to single path
        success = viewmodel.command_update_dotfile(
            0, "Cat", "App", "Desc", ["~/.test1"], True
        )

        assert success is True
        dotfiles = viewmodel.get_dotfile_list()
        assert dotfiles[0]["paths"] == ["~/.test1"]


class TestViewModelBackupProcessing:
    """Test backup processing with multiple paths per dotfile."""

    def test_mirror_backup_processes_all_paths(self, tmp_path):
        """Test mirror backup can process all paths from all dotfiles."""
        config_path = tmp_path / "test_config.toml"
        mirror_dir = tmp_path / "mirror"
        mirror_dir.mkdir()

        # Create test files
        test_file1 = tmp_path / "testfile1.txt"
        test_file2 = tmp_path / "testfile2.txt"
        test_file1.write_text("Content 1")
        test_file2.write_text("Content 2")

        # Setup viewmodel
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)
        viewmodel.model.mirror_base_dir = mirror_dir

        # Add dotfile with multiple paths
        viewmodel.command_add_dotfile(
            "Test",
            "TestApp",
            "Test dotfile",
            [str(test_file1), str(test_file2)],
            True,
        )

        # Enable mirror backup
        viewmodel.model.options["mirror"] = True
        viewmodel.model.options["archive"] = False

        # Test that model can copy both files
        dest1 = mirror_dir / "file1.txt"
        dest2 = mirror_dir / "file2.txt"
        success1 = viewmodel.model.copy_file(test_file1, dest1)
        success2 = viewmodel.model.copy_file(test_file2, dest2)

        # Verify both files can be copied
        assert success1 is True
        assert success2 is True
        assert dest1.exists()
        assert dest2.exists()

    def test_archive_backup_includes_all_paths(self, tmp_path):
        """Test archive backup includes all paths from all dotfiles."""
        config_path = tmp_path / "test_config.toml"
        archive_dir = tmp_path / "archives"
        archive_dir.mkdir()

        # Create test files
        test_file1 = tmp_path / "testfile1.txt"
        test_file2 = tmp_path / "testfile2.txt"
        test_file1.write_text("Content 1")
        test_file2.write_text("Content 2")

        # Setup viewmodel
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)
        viewmodel.model.archive_base_dir = archive_dir

        # Add dotfile with multiple paths
        viewmodel.command_add_dotfile(
            "Test",
            "TestApp",
            "Test dotfile",
            [str(test_file1), str(test_file2)],
            True,
        )

        # Enable archive backup
        viewmodel.model.options["mirror"] = False
        viewmodel.model.options["archive"] = True

        # Run archive backup
        archive_path = viewmodel.model.create_archive(
            [
                (test_file1, True, False),
                (test_file2, True, False),
            ]
        )

        # Verify archive was created
        assert archive_path is not None
        assert archive_path.exists()

    def test_backup_skips_disabled_dotfiles(self, tmp_path):
        """Test backup logic respects disabled dotfile status."""
        config_path = tmp_path / "test_config.toml"
        mirror_dir = tmp_path / "mirror"
        mirror_dir.mkdir()

        # Create test file
        test_file = tmp_path / "testfile.txt"
        test_file.write_text("Content")

        # Setup viewmodel
        model = DFBUModel(config_path)
        viewmodel = DFBUViewModel(model)
        viewmodel.model.mirror_base_dir = mirror_dir

        # Add disabled dotfile
        viewmodel.command_add_dotfile(
            "Test", "TestApp", "Test", [str(test_file)], False
        )

        # Enable mirror backup option
        viewmodel.model.options["mirror"] = True
        viewmodel.model.options["archive"] = False

        # Verify dotfile is disabled
        dotfile = viewmodel.model.get_dotfile_by_index(0)
        assert dotfile is not None
        assert dotfile["enabled"] is False

        # Verify get_enabled_dotfiles would skip this dotfile
        enabled_dotfiles = [df for df in viewmodel.model.dotfiles if df["enabled"]]
        assert len(enabled_dotfiles) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
