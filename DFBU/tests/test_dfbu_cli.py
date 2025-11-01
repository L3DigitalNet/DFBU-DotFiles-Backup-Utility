"""
DFBU CLI Integration Tests

Description:
    Integration tests for dfbu.py CLI application, testing backup/restore
    workflows, argument parsing, and integration between components.

Author: Test Suite
Date Created: 10-31-2025
License: MIT

Features:
    - Argument parsing validation
    - Backup workflow integration testing
    - Configuration loading and validation
    - Component integration testing
    - Happy path testing for core workflows

Requirements:
    - Linux environment
    - Python 3.14+
    - pytest framework
"""

import sys
from pathlib import Path
from unittest.mock import patch


# Add DFBU directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dfbu import (
    AnsiColor,
    CLIHandler,
    ConfigValidator,
    FileSystemHelper,
    Options,
    PathAssembler,
)


class TestCLIArgumentParsing:
    """Test command-line argument parsing and configuration."""

    def test_options_initialization_with_defaults(self):
        """Test Options class initializes with proper defaults."""
        # Arrange - create valid options dict
        raw_options = {
            "mirror": True,
            "archive": False,
            "hostname_subdir": True,
            "date_subdir": False,
            "archive_format": "tar.gz",
            "archive_compression_level": 9,
            "rotate_archives": False,
            "max_archives": 5,
        }

        # Act - create Options instance
        options = Options(raw_options)

        # Assert - verify default values
        assert options.mirror is True
        assert options.archive is False
        assert options.hostname_subdir is True
        assert options.date_subdir is False
        assert options.archive_format == "tar.gz"
        assert options.archive_compression_level == 9

    def test_options_with_custom_values(self):
        """Test Options accepts custom values."""
        # Arrange - create custom options dict
        raw_options = {
            "mirror": False,
            "archive": True,
            "hostname_subdir": False,
            "date_subdir": True,
            "archive_format": "tar.gz",
            "archive_compression_level": 6,
            "rotate_archives": True,
            "max_archives": 10,
        }

        # Act - create Options instance
        options = Options(raw_options)

        # Assert - verify custom values
        assert options.mirror is False
        assert options.archive is True
        assert options.hostname_subdir is False
        assert options.date_subdir is True
        assert options.archive_compression_level == 6
        assert options.max_archives == 10

    def test_options_archive_settings(self):
        """Test Options handles archive-specific settings."""
        # Arrange - create options with archive settings
        raw_options = {
            "mirror": True,
            "archive": True,
            "hostname_subdir": True,
            "date_subdir": True,
            "archive_format": "tar.gz",
            "archive_compression_level": 3,
            "rotate_archives": True,
            "max_archives": 7,
        }

        # Act - create Options instance
        options = Options(raw_options)

        # Assert - verify archive settings
        assert options.archive is True
        assert options.rotate_archives is True
        assert options.max_archives == 7

    def test_options_compression_levels(self):
        """Test Options handles different compression levels."""
        # Arrange - test various compression levels
        for level in [0, 3, 6, 9]:
            raw_options = {
                "mirror": True,
                "archive": True,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": level,
                "rotate_archives": False,
                "max_archives": 5,
            }

            # Act - create Options instance
            options = Options(raw_options)

            # Assert - verify compression level
            assert options.archive_compression_level == level


class TestBackupWorkflowIntegration:
    """Test complete backup workflow integration."""

    def test_config_validator_returns_correct_structure(self, tmp_path):
        """Test ConfigValidator returns tuple of options and dotfiles."""
        # Arrange - create valid config
        config_data = {
            "options": {
                "mirror": True,
                "archive": False,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 9,
                "rotate_archives": False,
                "max_archives": 5,
            },
            "paths": {
                "mirror_dir": str(tmp_path / "mirror"),
                "archive_dir": str(tmp_path / "archive"),
            },
            "dotfile": [
                {
                    "category": "shell",
                    "subcategory": "bash",
                    "application": "bash",
                    "description": "Bash config",
                    "paths": ["~/.bashrc"],
                }
            ],
        }

        # Act - validate config
        validated_options, validated_dotfiles = ConfigValidator.validate_config(
            config_data
        )

        # Assert - verify structure
        assert isinstance(validated_options, dict)
        assert isinstance(validated_dotfiles, list)
        assert validated_options["mirror"] is True
        assert len(validated_dotfiles) == 1
        assert validated_dotfiles[0]["description"] == "Bash config"

    def test_options_object_creation_from_validated_config(self, tmp_path):
        """Test Options object creation from validated config."""
        # Arrange - create and validate config
        config_data = {
            "options": {
                "mirror": False,
                "archive": True,
                "hostname_subdir": False,
                "date_subdir": True,
                "archive_format": "tar.gz",
                "archive_compression_level": 6,
                "rotate_archives": True,
                "max_archives": 10,
            },
        }

        # Act - validate and create Options object
        validated_options, _ = ConfigValidator.validate_config(config_data)
        options = Options(validated_options)

        # Assert - verify Options object
        assert options.mirror is False
        assert options.archive is True
        assert options.hostname_subdir is False
        assert options.date_subdir is True
        assert options.archive_compression_level == 6
        assert options.max_archives == 10

    def test_backup_workflow_with_validated_config(self, tmp_path):
        """Test complete workflow from config validation to Options creation."""
        # Arrange - create minimal valid config
        config_data = {
            "options": {
                "mirror": True,
                "archive": False,
            },
            "paths": {
                "mirror_dir": str(tmp_path / "backups"),
                "archive_dir": str(tmp_path / "archives"),
            },
            "dotfile": [],
        }

        # Act - validate config and create Options
        validated_options, validated_dotfiles = ConfigValidator.validate_config(
            config_data
        )
        options = Options(validated_options)

        # Assert - verify workflow completed
        assert options.mirror is True
        assert options.archive is False
        assert len(validated_dotfiles) == 0


class TestComponentIntegration:
    """Test integration between CLI components."""

    def test_config_validator_with_pathassembler(self, tmp_path):
        """Test ConfigValidator works with PathAssembler for path validation."""
        # Arrange - create valid config
        config_data = {
            "options": {
                "mirror": True,
                "archive": False,
                "hostname_subdir": True,
                "date_subdir": False,
            },
            "paths": {
                "mirror_dir": str(tmp_path / "backups"),
                "archive_dir": str(tmp_path / "archives"),
            },
            "dotfile": [
                {
                    "category": "shell",
                    "subcategory": "bash",
                    "application": "bash",
                    "description": "Bash configuration",
                    "paths": ["~/.bashrc"],
                }
            ],
        }

        # Act - validate config
        validated_options, validated_dotfiles = ConfigValidator.validate_config(
            config_data
        )

        # Assert - config should be valid
        assert isinstance(validated_options, dict)
        assert len(validated_dotfiles) == 1

        # Test PathAssembler can process the paths
        dotfile = validated_dotfiles[0]
        source_path = Path(dotfile["paths"][0]).expanduser()
        destination = PathAssembler.assemble_dest_path(
            Path(tmp_path / "backups"),
            source_path,
            validated_options["hostname_subdir"],
            validated_options["date_subdir"],
        )

        # Verify path assembly works
        assert destination is not None
        assert isinstance(destination, Path)

    def test_filesystem_helper_with_pathassembler(self, tmp_path):
        """Test FileSystemHelper works with PathAssembler for file operations."""
        # Arrange - create test files
        source = tmp_path / "source" / ".testrc"
        source.parent.mkdir(parents=True)
        source.write_text("test content")

        backup_dir = tmp_path / "backups"

        # Act - use PathAssembler to get destination
        destination = PathAssembler.assemble_dest_path(
            backup_dir,
            source,
            hostname_subdir=False,
            date_subdir=False,
        )

        # Use FileSystemHelper to expand path and check readability
        expanded_source = FileSystemHelper.expand_path(str(source))
        is_readable = FileSystemHelper.check_readable(source)

        # Create destination directory
        FileSystemHelper.create_directory(destination.parent, dry_run=False)

        # Copy file manually (FileSystemHelper doesn't have copy_file method)
        destination.write_text(source.read_text())

        # Assert - file operations completed
        assert expanded_source == source
        assert is_readable is True
        assert destination.exists()
        assert destination.read_text() == "test content"

    def test_cli_handler_parse_args_defaults(self):
        """Test CLIHandler parse_args returns defaults with no arguments."""
        # Arrange - mock sys.argv with no arguments
        with patch("sys.argv", ["dfbu.py"]):
            # Act - parse arguments
            dry_run, force = CLIHandler.parse_args()

            # Assert - should return False for both flags
            assert dry_run is False
            assert force is False

    def test_cli_handler_parse_args_dry_run(self):
        """Test CLIHandler parse_args handles --dry-run flag."""
        # Arrange - mock sys.argv with --dry-run
        with patch("sys.argv", ["dfbu.py", "--dry-run"]):
            # Act - parse arguments
            dry_run, force = CLIHandler.parse_args()

            # Assert - dry_run should be True
            assert dry_run is True
            assert force is False

    def test_cli_handler_parse_args_force(self):
        """Test CLIHandler parse_args handles --force flag."""
        # Arrange - mock sys.argv with --force
        with patch("sys.argv", ["dfbu.py", "--force"]):
            # Act - parse arguments
            dry_run, force = CLIHandler.parse_args()

            # Assert - force should be True
            assert dry_run is False
            assert force is True


class TestAnsiColorIntegration:
    """Test ANSI color formatting integration."""

    def test_ansicolor_instance_creation(self):
        """Test AnsiColor instances create proper color codes."""
        # Arrange & Act - create color instances
        green = AnsiColor("green")
        red = AnsiColor("red")
        blue = AnsiColor("blue")

        # Assert - instances should have ANSI codes
        assert "\033[" in green.code or "\u001b[" in green.code
        assert "\033[" in red.code or "\u001b[" in red.code
        assert "\033[" in blue.code or "\u001b[" in blue.code

    def test_ansicolor_bold_property(self):
        """Test AnsiColor bold property adds bold formatting."""
        # Arrange - create color instance
        color = AnsiColor("yellow")

        # Act - get bold version
        bold_code = color.bold

        # Assert - should contain ANSI codes
        assert "\033[" in bold_code or "\u001b[" in bold_code
        assert "1" in bold_code  # Bold style code

    def test_ansicolor_predefined_constants(self):
        """Test predefined color constants exist and work."""
        # Arrange & Act - use predefined constants from dfbu module
        # These are module-level constants like RED, GREEN, BLUE, etc.

        # Import and test a color constant
        from dfbu import BLUE, GREEN, RED

        # Assert - constants should be AnsiColor instances
        assert isinstance(RED, AnsiColor)
        assert isinstance(GREEN, AnsiColor)
        assert isinstance(BLUE, AnsiColor)
        assert "\033[" in str(RED) or "\u001b[" in str(RED)

    def test_ansicolor_with_background(self):
        """Test AnsiColor handles foreground and background colors."""
        # Arrange & Act - create color with background
        color = AnsiColor("white", "black")

        # Assert - should contain ANSI codes
        assert "\033[" in color.code or "\u001b[" in color.code


class TestWorkflowValidation:
    """Test complete workflow validation scenarios."""

    def test_complete_config_to_options_workflow(self, tmp_path):
        """Test complete workflow from config file to Options object."""
        # Arrange - create complete valid config
        config_data = {
            "options": {
                "mirror": True,
                "archive": True,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 9,
                "rotate_archives": True,
                "max_archives": 5,
            },
            "paths": {
                "mirror_dir": str(tmp_path / "backups"),
                "archive_dir": str(tmp_path / "archives"),
            },
            "dotfile": [
                {
                    "category": "shell",
                    "subcategory": "bash",
                    "application": "bash",
                    "description": "Test config",
                    "paths": [str(tmp_path / "source" / ".testrc")],
                }
            ],
        }

        # Act - validate config and create Options
        validated_options, validated_dotfiles = ConfigValidator.validate_config(
            config_data
        )
        options = Options(validated_options)

        # Assert - workflow completed successfully
        assert options.mirror is True
        assert options.archive is True
        assert options.hostname_subdir is True
        assert len(validated_dotfiles) == 1
        assert validated_dotfiles[0]["description"] == "Test config"

    def test_config_validation_workflow(self, tmp_path):
        """Test configuration validation workflow."""
        # Arrange - create valid config
        config_data = {
            "options": {
                "mirror": True,
                "archive": False,
                "hostname_subdir": True,
                "date_subdir": False,
            },
            "paths": {
                "mirror_dir": str(tmp_path / "backups"),
                "archive_dir": str(tmp_path / "archives"),
            },
            "dotfile": [
                {
                    "category": "shell",
                    "subcategory": "bash",
                    "application": "bash",
                    "description": "Bash config",
                    "paths": ["~/.bashrc"],
                }
            ],
        }

        # Act - validate through complete workflow
        validated_options, validated_dotfiles = ConfigValidator.validate_config(
            config_data
        )

        # Assert - all validations should pass
        assert isinstance(validated_options, dict)
        assert validated_options["mirror"] is True
        assert len(validated_dotfiles) == 1
        assert validated_dotfiles[0]["description"] == "Bash config"

    def test_path_assembly_integration_workflow(self, tmp_path):
        """Test path assembly workflow with config validation."""
        # Arrange - create source file and config
        source_file = tmp_path / "source" / ".testrc"
        source_file.parent.mkdir(parents=True)
        source_file.write_text("test content")

        config_data = {
            "options": {
                "mirror": True,
                "archive": False,
                "hostname_subdir": False,
                "date_subdir": False,
            },
            "paths": {
                "mirror_dir": str(tmp_path / "backups"),
                "archive_dir": str(tmp_path / "archives"),
            },
            "dotfile": [
                {
                    "category": "test",
                    "subcategory": "test",
                    "application": "test",
                    "description": "Test file",
                    "paths": [str(source_file)],
                }
            ],
        }

        # Act - validate config and assemble path
        validated_options, validated_dotfiles = ConfigValidator.validate_config(
            config_data
        )
        dotfile = validated_dotfiles[0]
        destination = PathAssembler.assemble_dest_path(
            Path(dotfile["mirror_dir"]),
            Path(dotfile["paths"][0]),
            validated_options["hostname_subdir"],
            validated_options["date_subdir"],
        )

        # Assert - workflow produced valid destination path
        assert isinstance(destination, Path)
        assert str(tmp_path / "backups") in str(destination)
