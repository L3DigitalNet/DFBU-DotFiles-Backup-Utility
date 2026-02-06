"""Tests for YAML configuration loading and saving."""

from pathlib import Path
from typing import cast

import pytest
from core.common_types import DotFileDict, SessionDict, SettingsDict
from core.yaml_config import YAMLConfigLoader


class TestYAMLConfigLoader:
    """Tests for YAMLConfigLoader class."""

    @pytest.mark.unit
    def test_load_settings(self, tmp_path: Path) -> None:
        """Load settings from YAML file."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("""
paths:
  mirror_dir: ~/backups/mirror
  archive_dir: ~/backups/archives
  restore_backup_dir: ~/.local/share/dfbu/restore-backups

options:
  mirror: true
  archive: true
  hostname_subdir: true
  date_subdir: false
  archive_format: tar.gz
  archive_compression_level: 5
  rotate_archives: true
  max_archives: 5
  pre_restore_backup: true
  max_restore_backups: 5
  verify_after_backup: false
  hash_verification: false
""")
        loader = YAMLConfigLoader(tmp_path)
        settings = loader.load_settings()

        assert settings["paths"]["mirror_dir"] == "~/backups/mirror"
        assert settings["options"]["mirror"] is True
        assert settings["options"]["archive_compression_level"] == 5

    @pytest.mark.unit
    def test_load_dotfiles(self, tmp_path: Path) -> None:
        """Load dotfiles library from YAML file."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
Bash:
  description: Shell configuration
  path: ~/.bashrc

Konsole:
  description: Terminal emulator
  paths:
    - ~/.config/konsolerc
    - ~/.local/share/konsole/
  tags: kde, terminal
""")
        loader = YAMLConfigLoader(tmp_path)
        dotfiles = loader.load_dotfiles()

        assert "Bash" in dotfiles
        assert dotfiles["Bash"]["description"] == "Shell configuration"
        assert dotfiles["Bash"].get("path") == "~/.bashrc"
        assert "Konsole" in dotfiles
        assert dotfiles["Konsole"].get("tags") == "kde, terminal"

    @pytest.mark.unit
    def test_load_session(self, tmp_path: Path) -> None:
        """Load session exclusions from YAML file."""
        session_file = tmp_path / "session.yaml"
        session_file.write_text("""
excluded:
  - Wine
  - PlayOnLinux
""")
        loader = YAMLConfigLoader(tmp_path)
        session = loader.load_session()

        assert session["excluded"] == ["Wine", "PlayOnLinux"]

    @pytest.mark.unit
    def test_load_session_empty(self, tmp_path: Path) -> None:
        """Load empty session when file doesn't exist."""
        loader = YAMLConfigLoader(tmp_path)
        session = loader.load_session()

        assert session["excluded"] == []

    @pytest.mark.unit
    def test_save_settings(self, tmp_path: Path) -> None:
        """Save settings to YAML file."""
        loader = YAMLConfigLoader(tmp_path)
        # Cast needed: test uses partial OptionsDict (missing v1.0.0 size fields)
        settings = cast(
            SettingsDict,
            {
                "paths": {
                    "mirror_dir": "~/test/mirror",
                    "archive_dir": "~/test/archives",
                    "restore_backup_dir": "~/.local/share/dfbu/restore-backups",
                },
                "options": {
                    "mirror": True,
                    "archive": False,
                    "hostname_subdir": True,
                    "date_subdir": False,
                    "archive_format": "tar.gz",
                    "archive_compression_level": 5,
                    "rotate_archives": True,
                    "max_archives": 5,
                    "pre_restore_backup": True,
                    "max_restore_backups": 5,
                    "verify_after_backup": False,
                    "hash_verification": False,
                },
            },
        )
        loader.save_settings(settings)

        content = (tmp_path / "settings.yaml").read_text()
        assert "mirror_dir: ~/test/mirror" in content
        assert "archive: false" in content

    @pytest.mark.unit
    def test_save_session(self, tmp_path: Path) -> None:
        """Save session exclusions to YAML file."""
        loader = YAMLConfigLoader(tmp_path)
        session: SessionDict = {"excluded": ["Wine", "MAME"]}
        loader.save_session(session)

        content = (tmp_path / "session.yaml").read_text()
        assert "Wine" in content
        assert "MAME" in content

    @pytest.mark.unit
    def test_save_dotfiles(self, tmp_path: Path) -> None:
        """Save dotfiles library to YAML file."""
        loader = YAMLConfigLoader(tmp_path)
        dotfiles: dict[str, DotFileDict] = {
            "Bash": {
                "description": "Shell configuration",
                "path": "~/.bashrc",
            },
            "Konsole": {
                "description": "Terminal emulator",
                "paths": ["~/.config/konsolerc", "~/.local/share/konsole/"],
                "tags": "kde, terminal",
            },
        }
        loader.save_dotfiles(dotfiles)

        content = (tmp_path / "dotfiles.yaml").read_text()
        assert "Bash" in content
        assert "Shell configuration" in content
        assert "~/.bashrc" in content
        assert "Konsole" in content
        assert "Terminal emulator" in content

    @pytest.mark.unit
    def test_load_settings_file_not_found(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError when settings.yaml is missing."""
        loader = YAMLConfigLoader(tmp_path)

        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_settings()

        assert "Settings file not found" in str(exc_info.value)

    @pytest.mark.unit
    def test_load_settings_empty_file(self, tmp_path: Path) -> None:
        """Raise ValueError when settings.yaml is empty."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("")
        loader = YAMLConfigLoader(tmp_path)

        with pytest.raises(ValueError) as exc_info:
            loader.load_settings()

        assert "Settings file is empty" in str(exc_info.value)

    @pytest.mark.unit
    def test_load_settings_missing_paths_section(self, tmp_path: Path) -> None:
        """Raise ValueError when paths section is missing."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("""
options:
  mirror: true
""")
        loader = YAMLConfigLoader(tmp_path)

        with pytest.raises(ValueError) as exc_info:
            loader.load_settings()

        assert "Settings missing required 'paths' section" in str(exc_info.value)

    @pytest.mark.unit
    def test_load_settings_missing_options_section(self, tmp_path: Path) -> None:
        """Raise ValueError when options section is missing."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("""
paths:
  mirror_dir: ~/backups/mirror
  archive_dir: ~/backups/archives
  restore_backup_dir: ~/.local/share/dfbu/restore-backups
""")
        loader = YAMLConfigLoader(tmp_path)

        with pytest.raises(ValueError) as exc_info:
            loader.load_settings()

        assert "Settings missing required 'options' section" in str(exc_info.value)

    @pytest.mark.unit
    def test_load_dotfiles_file_not_found(self, tmp_path: Path) -> None:
        """Raise FileNotFoundError when dotfiles.yaml is missing."""
        loader = YAMLConfigLoader(tmp_path)

        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_dotfiles()

        assert "Dotfiles file not found" in str(exc_info.value)

    @pytest.mark.unit
    def test_load_dotfiles_empty_file(self, tmp_path: Path) -> None:
        """Return empty dict when dotfiles.yaml exists but is empty."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("")
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert dotfiles == {}

    @pytest.mark.unit
    def test_validate_dotfile_missing_description(self, tmp_path: Path) -> None:
        """Auto-fix missing description with app name as default."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
Bash:
  path: ~/.bashrc
""")
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert "Bash" in dotfiles
        assert dotfiles["Bash"]["description"] == "Bash configuration"
        assert dotfiles["Bash"].get("path") == "~/.bashrc"

    @pytest.mark.unit
    def test_validate_dotfile_missing_path_and_paths(self, tmp_path: Path) -> None:
        """Skip entry when dotfile is missing both path and paths."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
Bash:
  description: Shell configuration
Vim:
  description: Editor configuration
  path: ~/.vimrc
""")
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        # Bash should be skipped (no path/paths), Vim should remain
        assert "Bash" not in dotfiles
        assert "Vim" in dotfiles

    @pytest.mark.unit
    def test_load_session_empty_file(self, tmp_path: Path) -> None:
        """Return empty session when session.yaml exists but is empty."""
        session_file = tmp_path / "session.yaml"
        session_file.write_text("")
        loader = YAMLConfigLoader(tmp_path)

        session = loader.load_session()

        assert session["excluded"] == []

    @pytest.mark.unit
    def test_load_session_null_excluded(self, tmp_path: Path) -> None:
        """Return empty list when excluded is explicitly null."""
        session_file = tmp_path / "session.yaml"
        session_file.write_text("""
excluded: null
""")
        loader = YAMLConfigLoader(tmp_path)

        session = loader.load_session()

        assert session["excluded"] == []

    @pytest.mark.unit
    def test_load_settings_missing_required_path_field(self, tmp_path: Path) -> None:
        """Raise ValueError when required path field is missing."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("""
paths:
  archive_dir: ~/backups/archives
  restore_backup_dir: ~/.local/share/dfbu/restore-backups

options:
  mirror: true
  archive: true
  hostname_subdir: true
  date_subdir: false
  archive_format: tar.gz
  archive_compression_level: 5
  rotate_archives: true
  max_archives: 5
  pre_restore_backup: true
  max_restore_backups: 5
""")
        loader = YAMLConfigLoader(tmp_path)

        with pytest.raises(ValueError) as exc_info:
            loader.load_settings()

        assert "Settings paths missing required field: mirror_dir" in str(
            exc_info.value
        )

    @pytest.mark.unit
    def test_load_settings_missing_required_option_field(self, tmp_path: Path) -> None:
        """Raise ValueError when required option field is missing."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("""
paths:
  mirror_dir: ~/backups/mirror
  archive_dir: ~/backups/archives
  restore_backup_dir: ~/.local/share/dfbu/restore-backups

options:
  mirror: true
  archive: true
  hostname_subdir: true
  date_subdir: false
  archive_format: tar.gz
  rotate_archives: true
  max_archives: 5
  pre_restore_backup: true
  max_restore_backups: 5
""")
        loader = YAMLConfigLoader(tmp_path)

        with pytest.raises(ValueError) as exc_info:
            loader.load_settings()

        assert (
            "Settings options missing required field: archive_compression_level"
            in str(exc_info.value)
        )


class TestDuplicateKeyHandling:
    """Tests for duplicate key detection and merging in dotfiles.yaml."""

    @pytest.mark.unit
    def test_duplicate_keys_merged_automatically(self, tmp_path: Path) -> None:
        """Duplicate top-level keys are merged into a single entry."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text(
            "KDE Plasma:\n"
            "  description: KDE Plasma configuration\n"
            "  paths:\n"
            "    - ~/.config\n"
            "    - ~/.local/share/plasma\n"
            "Bash:\n"
            "  description: Shell configuration\n"
            "  path: ~/.bashrc\n"
            "KDE Plasma:\n"
            "  description: global configuration settings and theme preferences\n"
            "  path: ~/.config/kdeglobals\n"
        )
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert "KDE Plasma" in dotfiles
        assert "Bash" in dotfiles
        # Should have merged paths from both entries
        kde = dotfiles["KDE Plasma"]
        assert "paths" in kde
        paths = kde["paths"]
        assert "~/.config" in paths
        assert "~/.local/share/plasma" in paths
        assert "~/.config/kdeglobals" in paths

    @pytest.mark.unit
    def test_duplicate_keys_keep_longer_description(self, tmp_path: Path) -> None:
        """Merged duplicates keep the longest description."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text(
            "Vim:\n"
            "  description: Vim\n"
            "  path: ~/.vimrc\n"
            "Vim:\n"
            "  description: Vim text editor configuration and plugins\n"
            "  path: ~/.vim\n"
        )
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert (
            dotfiles["Vim"]["description"]
            == "Vim text editor configuration and plugins"
        )

    @pytest.mark.unit
    def test_duplicate_keys_deduplicate_paths(self, tmp_path: Path) -> None:
        """Merged duplicates don't include duplicate paths."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text(
            "Firefox:\n"
            "  description: Firefox browser\n"
            "  path: ~/.mozilla/firefox\n"
            "Firefox:\n"
            "  description: Firefox web browser profiles\n"
            "  path: ~/.mozilla/firefox\n"
        )
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert "Firefox" in dotfiles
        firefox = dotfiles["Firefox"]
        # Should have single path since both were identical
        assert firefox.get("path") == "~/.mozilla/firefox"
        assert "paths" not in firefox

    @pytest.mark.unit
    def test_duplicate_keys_merge_tags(self, tmp_path: Path) -> None:
        """Merged duplicates combine tags from all entries."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text(
            "Konsole:\n"
            "  description: Terminal emulator\n"
            "  path: ~/.config/konsolerc\n"
            "  tags: kde, terminal\n"
            "Konsole:\n"
            "  description: KDE terminal emulator profiles\n"
            "  path: ~/.local/share/konsole\n"
            "  tags: terminal, profiles\n"
        )
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        tags = dotfiles["Konsole"].get("tags", "")
        # All unique tags should be present
        assert "kde" in tags
        assert "terminal" in tags
        assert "profiles" in tags

    @pytest.mark.unit
    def test_duplicate_keys_file_auto_saved(self, tmp_path: Path) -> None:
        """After merging duplicates, the cleaned file is saved back."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text(
            "Vim:\n"
            "  description: Vim editor\n"
            "  path: ~/.vimrc\n"
            "Vim:\n"
            "  description: Vim plugins\n"
            "  path: ~/.vim\n"
        )
        loader = YAMLConfigLoader(tmp_path)

        loader.load_dotfiles()

        # File should now be de-duplicated and loadable without error
        loader2 = YAMLConfigLoader(tmp_path)
        dotfiles = loader2.load_dotfiles()
        assert "Vim" in dotfiles

    @pytest.mark.unit
    def test_no_duplicates_loads_normally(self, tmp_path: Path) -> None:
        """Files without duplicates load through the normal path."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
Bash:
  description: Shell configuration
  path: ~/.bashrc
Vim:
  description: Vim editor
  path: ~/.vimrc
""")
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert len(dotfiles) == 2
        assert "Bash" in dotfiles
        assert "Vim" in dotfiles


class TestDotfileCleanup:
    """Tests for dotfile entry validation and cleanup."""

    @pytest.mark.unit
    def test_empty_paths_list_removed(self, tmp_path: Path) -> None:
        """Entry with empty paths list and no path is skipped."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
BadEntry:
  description: Has empty paths
  paths: []
GoodEntry:
  description: Valid entry
  path: ~/.config/good
""")
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert "BadEntry" not in dotfiles
        assert "GoodEntry" in dotfiles

    @pytest.mark.unit
    def test_duplicate_paths_within_entry_deduplicated(self, tmp_path: Path) -> None:
        """Duplicate paths within a single entry are deduplicated."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
Konsole:
  description: Terminal emulator
  paths:
    - ~/.config/konsolerc
    - ~/.config/konsolerc
    - ~/.local/share/konsole
""")
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        paths = dotfiles["Konsole"].get("paths", [])
        assert len(paths) == 2
        assert "~/.config/konsolerc" in paths
        assert "~/.local/share/konsole" in paths

    @pytest.mark.unit
    def test_empty_path_string_skipped(self, tmp_path: Path) -> None:
        """Entry with empty path string and no paths is skipped."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
BadEntry:
  description: Empty path
  path: ""
GoodEntry:
  description: Valid entry
  path: ~/.config/good
""")
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert "BadEntry" not in dotfiles
        assert "GoodEntry" in dotfiles

    @pytest.mark.unit
    def test_paths_string_normalized_to_list(self, tmp_path: Path) -> None:
        """Single string in paths field is normalized to a list."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
Bash:
  description: Shell config
  paths: ~/.bashrc
""")
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert "Bash" in dotfiles
        assert dotfiles["Bash"].get("paths") == ["~/.bashrc"]

    @pytest.mark.unit
    def test_whitespace_in_paths_trimmed(self, tmp_path: Path) -> None:
        """Whitespace in path strings is trimmed."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
Vim:
  description: Vim editor
  path: "  ~/.vimrc  "
""")
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert dotfiles["Vim"].get("path") == "~/.vimrc"

    @pytest.mark.unit
    def test_non_dict_entry_skipped(self, tmp_path: Path) -> None:
        """Non-dict entries are skipped gracefully."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
BadEntry: just a string
GoodEntry:
  description: Valid
  path: ~/.config/good
""")
        loader = YAMLConfigLoader(tmp_path)

        dotfiles = loader.load_dotfiles()

        assert "BadEntry" not in dotfiles
        assert "GoodEntry" in dotfiles
