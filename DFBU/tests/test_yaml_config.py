"""Tests for YAML configuration loading and saving."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

import pytest

from yaml_config import YAMLConfigLoader


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
