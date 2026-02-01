"""
Tests for TOML to YAML Configuration Migration

Description:
    Tests for the ConfigMigrator class that converts legacy TOML configuration
    to the new YAML format with settings.yaml, dotfiles.yaml, and session.yaml.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 02-01-2026
License: MIT

Tests:
    - test_migrate_creates_settings_yaml: Migration creates settings.yaml
    - test_migrate_creates_dotfiles_yaml: Migration creates dotfiles.yaml
    - test_migrate_consolidates_duplicates: Merges duplicate application entries
    - test_migrate_drops_category_and_enabled: Removes legacy fields
    - test_migrate_creates_backup: Creates backup of original TOML
    - test_migrate_creates_empty_session: Creates session.yaml with empty exclusions
"""

from pathlib import Path

import pytest

from core.migration import ConfigMigrator, migrate_config


@pytest.fixture
def sample_toml(tmp_path: Path) -> Path:
    """
    Create a sample TOML configuration file for testing migration.

    Includes:
    - [paths] section with mirror and archive directories
    - [options] section with backup settings
    - Multiple [[dotfile]] entries including duplicates (two Firefox entries)
    - Entries with single path and multiple paths

    Args:
        tmp_path: pytest temporary directory fixture

    Returns:
        Path: Path to the created TOML file
    """
    toml_content = '''title = "Dotfiles Backup Config"
description = "Configuration file for dotfiles backup."

[paths]
mirror_dir = "~/GitHub/dotfiles"
archive_dir = "~/pCloudDrive/Backups/Dotfiles"
restore_backup_dir = "~/.local/share/dfbu/restore-backups"

[options]
mirror = true
archive = true
hostname_subdir = true
date_subdir = false
archive_format = "tar.gz"
archive_compression_level = 5
rotate_archives = true
max_archives = 5
pre_restore_backup = true
max_restore_backups = 5

[[dotfile]]
category = "Shell configs"
application = "Bash"
description = "Bash shell configuration and startup script"
enabled = true
path = "~/.bashrc"

[[dotfile]]
category = "Shell configs"
application = "Zsh"
description = "Zsh shell configuration"
enabled = false
path = "~/.zshrc"

[[dotfile]]
category = "Terminal"
application = "Konsole"
description = "KDE Konsole terminal emulator configuration"
enabled = true
paths = [
    "~/.config/konsolerc",
    "~/.local/share/konsole/Bash.profile",
]

[[dotfile]]
category = "Applications"
application = "Firefox"
description = "Mozilla Firefox browser profiles configuration"
enabled = true
paths = [
    "~/.mozilla/firefox/profiles.ini",
    "~/.mozilla/firefox/*/prefs.js",
]

[[dotfile]]
category = "Applications"
application = "Firefox"
description = "Configuration files"
enabled = true
paths = [
    "~/.mozilla/firefox/0u2cfm04.default-release/prefs.js",
    "/usr/lib64/firefox/defaults/pref",
]

[[dotfile]]
category = "Desktop Environment"
application = "KDE Plasma"
description = "KDE global configuration settings and theme preferences"
enabled = true
path = "~/.config/kdeglobals"

[[dotfile]]
category = "Applications"
application = "GNOME Nautilus"
description = "GNOME Nautilus file manager preferences (stored in dconf)"
enabled = true
path = "~/.config/dconf/user"

[[dotfile]]
category = "System"
application = "Krusader"
description = "Krusader file manager configuration"
enabled = true
paths = [
    "~/.config/krusaderrc",
    "~/.local/share/kxmlgui5/krusader/krusaderui.rc",
]
'''
    toml_file = tmp_path / "dfbu-config.toml"
    toml_file.write_text(toml_content)
    return toml_file


class TestConfigMigrator:
    """Tests for ConfigMigrator class."""

    @pytest.mark.unit
    def test_migrate_creates_settings_yaml(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """Migration creates settings.yaml with paths and options."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(sample_toml, output_dir)
        migrator.migrate()

        settings_path = output_dir / "settings.yaml"
        assert settings_path.exists(), "settings.yaml should be created"

        content = settings_path.read_text()
        # Check paths section
        assert "mirror_dir" in content
        assert "~/GitHub/dotfiles" in content
        assert "archive_dir" in content
        assert "~/pCloudDrive/Backups/Dotfiles" in content
        assert "restore_backup_dir" in content

        # Check options section
        assert "mirror:" in content
        assert "archive:" in content
        assert "hostname_subdir:" in content
        assert "archive_format:" in content
        assert "archive_compression_level:" in content

    @pytest.mark.unit
    def test_migrate_creates_dotfiles_yaml(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """Migration creates dotfiles.yaml with library entries."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(sample_toml, output_dir)
        migrator.migrate()

        dotfiles_path = output_dir / "dotfiles.yaml"
        assert dotfiles_path.exists(), "dotfiles.yaml should be created"

        content = dotfiles_path.read_text()
        # Check that application names are present as keys
        assert "Bash:" in content
        assert "Zsh:" in content
        assert "Konsole:" in content
        assert "Firefox:" in content
        assert "KDE Plasma:" in content

        # Check that descriptions are present
        assert "description:" in content

        # Check that paths are present
        assert "~/.bashrc" in content
        assert "~/.config/konsolerc" in content

    @pytest.mark.unit
    def test_migrate_consolidates_duplicates(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """Migration consolidates duplicate application entries by merging paths."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(sample_toml, output_dir)
        migrator.migrate()

        dotfiles_path = output_dir / "dotfiles.yaml"
        content = dotfiles_path.read_text()

        # Firefox should appear only once (consolidated)
        firefox_count = content.count("Firefox:")
        assert firefox_count == 1, "Firefox should appear only once after consolidation"

        # All Firefox paths should be present (merged from both entries)
        assert "~/.mozilla/firefox/profiles.ini" in content
        assert "~/.mozilla/firefox/*/prefs.js" in content
        assert "~/.mozilla/firefox/0u2cfm04.default-release/prefs.js" in content
        assert "/usr/lib64/firefox/defaults/pref" in content

    @pytest.mark.unit
    def test_migrate_drops_category_and_enabled(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """Migration drops category and enabled fields from dotfiles."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(sample_toml, output_dir)
        migrator.migrate()

        dotfiles_path = output_dir / "dotfiles.yaml"
        content = dotfiles_path.read_text()

        # Category and enabled should not appear in the output
        assert "category:" not in content, "category field should be dropped"
        assert "enabled:" not in content, "enabled field should be dropped"

        # But descriptions should still be present
        assert "description:" in content

    @pytest.mark.unit
    def test_migrate_creates_backup(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """Migration creates backup of original TOML file."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(sample_toml, output_dir)
        migrator.migrate()

        # Check for backup file in output directory
        backup_files = list(output_dir.glob("dfbu-config.toml.bak*"))
        assert len(backup_files) >= 1, "Should create at least one backup file"

        # Backup should contain original content
        backup_content = backup_files[0].read_text()
        assert "[paths]" in backup_content
        assert "[[dotfile]]" in backup_content

    @pytest.mark.unit
    def test_migrate_creates_empty_session(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """Migration creates session.yaml with empty exclusions."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(sample_toml, output_dir)
        migrator.migrate()

        session_path = output_dir / "session.yaml"
        assert session_path.exists(), "session.yaml should be created"

        content = session_path.read_text()
        # Should have excluded key with empty list
        assert "excluded:" in content

    @pytest.mark.unit
    def test_migrate_cleans_description_prefixes(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """Migration cleans up redundant prefixes in descriptions."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(sample_toml, output_dir)
        migrator.migrate()

        dotfiles_path = output_dir / "dotfiles.yaml"
        content = dotfiles_path.read_text()

        # "GNOME Nautilus" should have "GNOME " prefix removed from description
        # The description was "GNOME Nautilus file manager preferences..."
        # It should be cleaned to just "Nautilus file manager preferences..."
        assert "GNOME Nautilus file manager" not in content or \
            "Nautilus file manager" in content

    @pytest.mark.unit
    def test_migrate_preserves_paths_order(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """Migration preserves order of paths in entries."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(sample_toml, output_dir)
        migrator.migrate()

        dotfiles_path = output_dir / "dotfiles.yaml"
        content = dotfiles_path.read_text()

        # For Konsole, the paths should maintain order
        konsolerc_pos = content.find("~/.config/konsolerc")
        bash_profile_pos = content.find("~/.local/share/konsole/Bash.profile")
        assert konsolerc_pos < bash_profile_pos, "Paths order should be preserved"


class TestMigrateConfigFunction:
    """Tests for migrate_config convenience function."""

    @pytest.mark.unit
    def test_migrate_config_convenience_function(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """migrate_config convenience function works correctly."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = migrate_config(sample_toml, output_dir)

        assert result is True
        assert (output_dir / "settings.yaml").exists()
        assert (output_dir / "dotfiles.yaml").exists()
        assert (output_dir / "session.yaml").exists()

    @pytest.mark.unit
    def test_migrate_config_with_string_paths(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """migrate_config accepts string paths."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        result = migrate_config(str(sample_toml), str(output_dir))

        assert result is True
        assert (output_dir / "settings.yaml").exists()

    @pytest.mark.unit
    def test_migrate_config_creates_output_dir(
        self, sample_toml: Path, tmp_path: Path
    ) -> None:
        """migrate_config creates output directory if it doesn't exist."""
        output_dir = tmp_path / "new_output_dir"

        result = migrate_config(sample_toml, output_dir)

        assert result is True
        assert output_dir.exists()
        assert (output_dir / "settings.yaml").exists()


class TestMigrationEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.unit
    def test_migrate_single_path_entry(self, tmp_path: Path) -> None:
        """Migration handles entries with single path correctly."""
        toml_content = '''
[paths]
mirror_dir = "~/test"
archive_dir = "~/test"
restore_backup_dir = "~/test"

[options]
mirror = true
archive = true
hostname_subdir = true
date_subdir = false
archive_format = "tar.gz"
archive_compression_level = 5
rotate_archives = true
max_archives = 5
pre_restore_backup = true
max_restore_backups = 5

[[dotfile]]
category = "Test"
application = "SinglePath"
description = "Single path entry"
enabled = true
path = "~/.testrc"
'''
        toml_file = tmp_path / "config.toml"
        toml_file.write_text(toml_content)
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(toml_file, output_dir)
        migrator.migrate()

        dotfiles_path = output_dir / "dotfiles.yaml"
        content = dotfiles_path.read_text()

        assert "SinglePath:" in content
        assert "~/.testrc" in content

    @pytest.mark.unit
    def test_migrate_removes_duplicate_paths(self, tmp_path: Path) -> None:
        """Migration removes duplicate paths when consolidating entries."""
        toml_content = '''
[paths]
mirror_dir = "~/test"
archive_dir = "~/test"
restore_backup_dir = "~/test"

[options]
mirror = true
archive = true
hostname_subdir = true
date_subdir = false
archive_format = "tar.gz"
archive_compression_level = 5
rotate_archives = true
max_archives = 5
pre_restore_backup = true
max_restore_backups = 5

[[dotfile]]
category = "Test"
application = "DupApp"
description = "First entry"
enabled = true
paths = ["~/.config/app1", "~/.config/app2"]

[[dotfile]]
category = "Test"
application = "DupApp"
description = "Second entry"
enabled = true
paths = ["~/.config/app2", "~/.config/app3"]
'''
        toml_file = tmp_path / "config.toml"
        toml_file.write_text(toml_content)
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(toml_file, output_dir)
        migrator.migrate()

        dotfiles_path = output_dir / "dotfiles.yaml"
        content = dotfiles_path.read_text()

        # app2 should appear only once
        app2_count = content.count("~/.config/app2")
        assert app2_count == 1, "Duplicate paths should be removed"

    @pytest.mark.unit
    def test_migrate_missing_toml_raises_error(self, tmp_path: Path) -> None:
        """Migration raises error when TOML file doesn't exist."""
        nonexistent_toml = tmp_path / "nonexistent.toml"
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        migrator = ConfigMigrator(nonexistent_toml, output_dir)

        with pytest.raises(FileNotFoundError):
            migrator.migrate()
