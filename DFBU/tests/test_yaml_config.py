"""Tests for YAML configuration loading and saving."""

from pathlib import Path

import pytest

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
        assert dotfiles["Bash"]["path"] == "~/.bashrc"
        assert "Konsole" in dotfiles
        assert dotfiles["Konsole"]["tags"] == "kde, terminal"

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
        settings = {
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
        }
        loader.save_settings(settings)

        content = (tmp_path / "settings.yaml").read_text()
        assert "mirror_dir: ~/test/mirror" in content
        assert "archive: false" in content

    @pytest.mark.unit
    def test_save_session(self, tmp_path: Path) -> None:
        """Save session exclusions to YAML file."""
        loader = YAMLConfigLoader(tmp_path)
        session = {"excluded": ["Wine", "MAME"]}
        loader.save_session(session)

        content = (tmp_path / "session.yaml").read_text()
        assert "Wine" in content
        assert "MAME" in content

    @pytest.mark.unit
    def test_save_dotfiles(self, tmp_path: Path) -> None:
        """Save dotfiles library to YAML file."""
        loader = YAMLConfigLoader(tmp_path)
        dotfiles = {
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
    def test_validate_dotfile_missing_description(self, tmp_path: Path) -> None:
        """Raise ValueError when dotfile is missing description."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
Bash:
  path: ~/.bashrc
""")
        loader = YAMLConfigLoader(tmp_path)

        with pytest.raises(ValueError) as exc_info:
            loader.load_dotfiles()

        assert "missing required 'description'" in str(exc_info.value)

    @pytest.mark.unit
    def test_validate_dotfile_missing_path_and_paths(self, tmp_path: Path) -> None:
        """Raise ValueError when dotfile is missing both path and paths."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
Bash:
  description: Shell configuration
""")
        loader = YAMLConfigLoader(tmp_path)

        with pytest.raises(ValueError) as exc_info:
            loader.load_dotfiles()

        assert "must have either 'path' or 'paths'" in str(exc_info.value)
