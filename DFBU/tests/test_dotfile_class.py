"""
DFBU DotFile Class Tests

Description:
    Unit tests for DotFile class from dfbu.py, testing dotfile metadata
    management, path resolution, and property calculations.

Author: Test Suite
Date Created: 10-31-2025
License: MIT

Features:
    - DotFile initialization testing
    - Path property validation
    - Metadata handling
    - Relative path calculation
    - Type detection (file vs directory)

Requirements:
    - Linux environment
    - Python 3.14+
    - pytest framework
"""

import sys
from pathlib import Path


# Add DFBU directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dfbu import DotFile, Options


class TestDotFileInitialization:
    """Test DotFile class initialization and basic properties."""

    def test_dotfile_initialization_with_existing_file(self, tmp_path):
        """Test DotFile initializes correctly with an existing file."""
        # Arrange - create test file
        source_file = tmp_path / "test" / ".bashrc"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("# Bash configuration")

        raw_dotfile = {
            "category": "shell",
            "application": "bash",
            "description": "Bash configuration file",
            "paths": [str(source_file)],  # Updated to use paths list
            "mirror_dir": str(tmp_path / "mirror"),
            "enabled": True,
            "archive_dir": str(tmp_path / "archive"),
            "enabled": True,
        }

        options = Options(
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

        # Act - create DotFile instance
        dotfile = DotFile(raw_dotfile, options)

        # Assert - verify properties
        assert dotfile.category == "shell"
        assert dotfile.application == "bash"
        assert dotfile.description == "Bash configuration file"
        assert dotfile.name == ".bashrc"
        assert dotfile.exists is True
        assert dotfile.is_file is True
        assert dotfile.is_dir is False
        assert dotfile.type == "File"

    def test_dotfile_initialization_with_directory(self, tmp_path):
        """Test DotFile handles directory sources correctly."""
        # Arrange - create test directory
        source_dir = tmp_path / "test" / ".config"
        source_dir.mkdir(parents=True)

        raw_dotfile = {
            "category": "config",
            "application": "various",
            "description": "Configuration directory",
            "paths": [str(source_dir)],  # Updated to use paths list
            "mirror_dir": str(tmp_path / "mirror"),
            "enabled": True,
            "archive_dir": str(tmp_path / "archive"),
            "enabled": True,
        }

        options = Options(
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

        # Act - create DotFile instance
        dotfile = DotFile(raw_dotfile, options)

        # Assert - verify directory properties
        assert dotfile.name == ".config"
        assert dotfile.exists is True
        assert dotfile.is_file is False
        assert dotfile.is_dir is True
        assert dotfile.type == "Directory"

    def test_dotfile_with_nonexistent_source(self, tmp_path):
        """Test DotFile handles nonexistent sources."""
        # Arrange - path that doesn't exist
        source_file = tmp_path / "nonexistent" / ".vimrc"

        raw_dotfile = {
            "category": "editor",
            "application": "vim",
            "description": "Vim configuration",
            "paths": [str(source_file)],  # Updated to use paths list
            "mirror_dir": str(tmp_path / "mirror"),
            "enabled": True,
            "archive_dir": str(tmp_path / "archive"),
            "enabled": True,
        }

        options = Options(
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

        # Act - create DotFile instance
        dotfile = DotFile(raw_dotfile, options)

        # Assert - verify nonexistent properties
        assert dotfile.exists is False
        assert dotfile.is_file is False
        assert dotfile.is_dir is False

    def test_dotfile_path_expansion(self, tmp_path):
        """Test DotFile expands tilde in paths."""
        # Arrange - use tilde notation
        raw_dotfile = {
            "category": "shell",
            "application": "bash",
            "description": "Bash configuration",
            "paths": ["~/.bashrc"],  # Updated to use paths list
            "mirror_dir": str(tmp_path / "mirror"),
            "enabled": True,
            "archive_dir": str(tmp_path / "archive"),
            "enabled": True,
        }

        options = Options(
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

        # Act - create DotFile instance
        dotfile = DotFile(raw_dotfile, options)

        # Assert - verify path was expanded
        assert dotfile.src_path == Path.home() / ".bashrc"
        assert "~" not in str(dotfile.src_path)


class TestDotFileDestinationPaths:
    """Test DotFile destination path assembly."""

    def test_dotfile_destination_paths_no_subdirs(self, tmp_path):
        """Test destination paths without hostname or date subdirectories."""
        # Arrange
        source_file = tmp_path / "test" / ".bashrc"
        source_file.parent.mkdir(parents=True)
        source_file.touch()

        raw_dotfile = {
            "category": "shell",
            "application": "bash",
            "description": "Bash config",
            "paths": [str(source_file)],
            "mirror_dir": str(tmp_path / "mirror"),
            "enabled": True,
            "archive_dir": str(tmp_path / "archive"),
        }

        options = Options(
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

        # Act
        dotfile = DotFile(raw_dotfile, options)

        # Assert - verify destination paths
        assert dotfile.dest_path_mirror is not None
        assert dotfile.dest_path_archive is not None
        assert isinstance(dotfile.dest_path_mirror, Path)
        assert isinstance(dotfile.dest_path_archive, Path)

    def test_dotfile_destination_paths_with_hostname(self, tmp_path):
        """Test destination paths include hostname subdirectory."""
        # Arrange
        source_file = tmp_path / "test" / ".bashrc"
        source_file.parent.mkdir(parents=True)
        source_file.touch()

        raw_dotfile = {
            "category": "shell",
            "application": "bash",
            "description": "Bash config",
            "paths": [str(source_file)],
            "mirror_dir": str(tmp_path / "mirror"),
            "enabled": True,
            "archive_dir": str(tmp_path / "archive"),
        }

        options = Options(
            {
                "mirror": True,
                "archive": False,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 9,
                "rotate_archives": False,
                "max_archives": 5,
            }
        )

        # Act
        dotfile = DotFile(raw_dotfile, options)

        # Assert - hostname should be in path
        assert dotfile.dest_path_mirror is not None
        # Hostname is somewhere in the path structure
        assert len(str(dotfile.dest_path_mirror)) > len(str(tmp_path / "mirror"))


class TestDotFileRelativePaths:
    """Test DotFile relative path calculations."""

    def test_dotfile_relative_path_from_home(self, tmp_path):
        """Test relative path calculation for home directory files."""
        # Arrange - path in home directory
        raw_dotfile = {
            "category": "shell",
            "application": "bash",
            "description": "Bash config",
            "paths": [str(Path.home() / ".bashrc")],
            "mirror_dir": str(tmp_path / "mirror"),
            "enabled": True,
            "archive_dir": str(tmp_path / "archive"),
        }

        options = Options(
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

        # Act
        dotfile = DotFile(raw_dotfile, options)

        # Assert - relative path should start with "home"
        assert dotfile.relative_to_home is True
        assert dotfile.relative_path.parts[0] == "home"

    def test_dotfile_relative_path_from_root(self, tmp_path):
        """Test relative path calculation for root directory files."""
        # Arrange - path in root directory
        raw_dotfile = {
            "category": "system",
            "application": "system",
            "description": "System config",
            "paths": ["/etc/fstab"],
            "mirror_dir": str(tmp_path / "mirror"),
            "enabled": True,
            "archive_dir": str(tmp_path / "archive"),
        }

        options = Options(
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

        # Act
        dotfile = DotFile(raw_dotfile, options)

        # Assert - relative path should start with "root"
        assert dotfile.relative_to_home is False
        assert dotfile.relative_path.parts[0] == "root"


class TestDotFileStringRepresentation:
    """Test DotFile string representation."""

    def test_dotfile_str_contains_metadata(self, tmp_path):
        """Test __str__ includes all metadata fields."""
        # Arrange
        source_file = tmp_path / "test" / ".bashrc"
        source_file.parent.mkdir(parents=True)
        source_file.touch()

        raw_dotfile = {
            "category": "shell",
            "application": "bash",
            "description": "Bash configuration file",
            "paths": [str(source_file)],
            "mirror_dir": str(tmp_path / "mirror"),
            "enabled": True,
            "archive_dir": str(tmp_path / "archive"),
        }

        options = Options(
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

        # Act
        dotfile = DotFile(raw_dotfile, options)
        result = str(dotfile)

        # Assert - verify string contains key information
        assert ".bashrc" in result
        assert "shell" in result
        assert "bash" in result
        assert "Bash configuration file" in result
        assert "Source path" in result
        assert "Mirror destination" in result

    def test_dotfile_str_indicates_file_type(self, tmp_path):
        """Test __str__ indicates File vs Directory type."""
        # Arrange - test with directory
        source_dir = tmp_path / "test" / ".config"
        source_dir.mkdir(parents=True)

        raw_dotfile = {
            "category": "config",
            "application": "various",
            "description": "Config directory",
            "paths": [str(source_dir)],
            "mirror_dir": str(tmp_path / "mirror"),
            "enabled": True,
            "archive_dir": str(tmp_path / "archive"),
        }

        options = Options(
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

        # Act
        dotfile = DotFile(raw_dotfile, options)
        result = str(dotfile)

        # Assert - should indicate Directory type
        assert "[Directory]" in result or "Directory" in result
