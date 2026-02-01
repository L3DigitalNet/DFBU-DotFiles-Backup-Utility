"""Tests for ConfigManager YAML configuration loading and exclusion management."""

from pathlib import Path

import pytest

from gui.config_manager import ConfigManager


@pytest.fixture
def yaml_config_dir(tmp_path: Path) -> Path:
    """
    Create test YAML configuration files for ConfigManager testing.

    Creates a complete set of YAML config files:
    - settings.yaml: Paths and options
    - dotfiles.yaml: Dotfile library entries
    - session.yaml: Exclusions (initially empty)

    Args:
        tmp_path: pytest built-in temporary directory fixture

    Returns:
        Path: Directory containing test YAML configuration files
    """
    # Create settings.yaml
    settings_file = tmp_path / "settings.yaml"
    settings_file.write_text("""
paths:
  mirror_dir: ~/test_mirror
  archive_dir: ~/test_archive
  restore_backup_dir: ~/.local/share/dfbu/restore-backups

options:
  mirror: true
  archive: false
  hostname_subdir: true
  date_subdir: false
  archive_format: tar.gz
  archive_compression_level: 9
  rotate_archives: false
  max_archives: 5
  pre_restore_backup: true
  max_restore_backups: 5
""")

    # Create dotfiles.yaml
    dotfiles_file = tmp_path / "dotfiles.yaml"
    dotfiles_file.write_text("""
Bash:
  description: Bash shell configuration
  path: ~/.bashrc
  tags: shell

Vim:
  description: Vim editor configuration
  paths:
    - ~/.vimrc
    - ~/.vim/
  tags: editor

Konsole:
  description: KDE terminal emulator
  paths:
    - ~/.config/konsolerc
    - ~/.local/share/konsole/
  tags: kde, terminal
""")

    # Create session.yaml (empty initially)
    session_file = tmp_path / "session.yaml"
    session_file.write_text("""
excluded: []
""")

    return tmp_path


@pytest.fixture
def yaml_config_dir_with_exclusions(yaml_config_dir: Path) -> Path:
    """
    Create test YAML configuration files with pre-existing exclusions.

    Args:
        yaml_config_dir: Base fixture with test YAML files

    Returns:
        Path: Directory containing test YAML configuration files
    """
    session_file = yaml_config_dir / "session.yaml"
    session_file.write_text("""
excluded:
  - Vim
  - Konsole
""")
    return yaml_config_dir


def expand_path(path_str: str) -> Path:
    """Test expand_path callback that expands ~ to home directory."""
    return Path(path_str).expanduser()


class TestConfigManagerYAMLLoading:
    """Tests for ConfigManager loading from YAML files."""

    @pytest.mark.unit
    def test_load_config_from_yaml(self, yaml_config_dir: Path) -> None:
        """ConfigManager loads settings and dotfiles from YAML files."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)

        # Act
        success, error = config_manager.load_config()

        # Assert
        assert success is True
        # Error is empty or contains auto-correction message (both are valid)
        assert error == "" or "auto-corrected" in error
        assert config_manager.options["mirror"] is True
        assert config_manager.options["archive"] is False
        assert config_manager.options["hostname_subdir"] is True
        assert config_manager.get_dotfile_count() == 3

    @pytest.mark.unit
    def test_load_config_sets_paths(self, yaml_config_dir: Path) -> None:
        """ConfigManager sets mirror and archive paths from YAML settings."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)

        # Act
        success, error = config_manager.load_config()

        # Assert
        assert success is True
        assert "test_mirror" in str(config_manager.mirror_base_dir)
        assert "test_archive" in str(config_manager.archive_base_dir)


class TestConfigManagerDotfileList:
    """Tests for get_dotfile_list method with application name."""

    @pytest.mark.unit
    def test_get_dotfile_list(self, yaml_config_dir: Path) -> None:
        """Get list of dotfiles with application name included."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()

        # Act
        dotfiles = config_manager.get_dotfile_list()

        # Assert
        assert len(dotfiles) == 3

        # Verify each dotfile has application name
        app_names = [df["application"] for df in dotfiles]
        assert "Bash" in app_names
        assert "Vim" in app_names
        assert "Konsole" in app_names

        # Verify other fields are present
        for df in dotfiles:
            assert "description" in df
            assert "paths" in df

    @pytest.mark.unit
    def test_get_dotfile_list_includes_description(
        self, yaml_config_dir: Path
    ) -> None:
        """Dotfile list includes correct descriptions."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()

        # Act
        dotfiles = config_manager.get_dotfile_list()

        # Assert
        bash_df = next(df for df in dotfiles if df["application"] == "Bash")
        assert bash_df["description"] == "Bash shell configuration"


class TestConfigManagerExclusions:
    """Tests for exclusion management methods."""

    @pytest.mark.unit
    def test_get_exclusions_empty(self, yaml_config_dir: Path) -> None:
        """Get empty exclusion list when session has no exclusions."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()

        # Act
        exclusions = config_manager.get_exclusions()

        # Assert
        assert exclusions == []

    @pytest.mark.unit
    def test_get_exclusions_with_items(
        self, yaml_config_dir_with_exclusions: Path
    ) -> None:
        """Get current exclusion list with existing exclusions."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir_with_exclusions, expand_path)
        config_manager.load_config()

        # Act
        exclusions = config_manager.get_exclusions()

        # Assert
        assert "Vim" in exclusions
        assert "Konsole" in exclusions
        assert len(exclusions) == 2

    @pytest.mark.unit
    def test_set_exclusions(self, yaml_config_dir: Path) -> None:
        """Set and persist exclusions to session file."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()

        # Act
        config_manager.set_exclusions(["Bash", "Vim"])

        # Assert
        exclusions = config_manager.get_exclusions()
        assert "Bash" in exclusions
        assert "Vim" in exclusions
        assert len(exclusions) == 2

        # Verify persisted to file
        session_content = (yaml_config_dir / "session.yaml").read_text()
        assert "Bash" in session_content
        assert "Vim" in session_content

    @pytest.mark.unit
    def test_set_exclusions_replaces_previous(self, yaml_config_dir: Path) -> None:
        """Setting exclusions replaces any previous exclusions."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()
        config_manager.set_exclusions(["Bash"])

        # Act
        config_manager.set_exclusions(["Vim"])

        # Assert
        exclusions = config_manager.get_exclusions()
        assert exclusions == ["Vim"]

    @pytest.mark.unit
    def test_is_excluded_true(
        self, yaml_config_dir_with_exclusions: Path
    ) -> None:
        """Check if specific dotfile is excluded returns True."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir_with_exclusions, expand_path)
        config_manager.load_config()

        # Act & Assert
        assert config_manager.is_excluded("Vim") is True
        assert config_manager.is_excluded("Konsole") is True

    @pytest.mark.unit
    def test_is_excluded_false(
        self, yaml_config_dir_with_exclusions: Path
    ) -> None:
        """Check if specific dotfile is not excluded returns False."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir_with_exclusions, expand_path)
        config_manager.load_config()

        # Act & Assert
        assert config_manager.is_excluded("Bash") is False

    @pytest.mark.unit
    def test_toggle_exclusion_add(self, yaml_config_dir: Path) -> None:
        """Toggle exclusion adds item when not excluded."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()

        # Act
        config_manager.toggle_exclusion("Bash")

        # Assert
        assert config_manager.is_excluded("Bash") is True

    @pytest.mark.unit
    def test_toggle_exclusion_remove(
        self, yaml_config_dir_with_exclusions: Path
    ) -> None:
        """Toggle exclusion removes item when already excluded."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir_with_exclusions, expand_path)
        config_manager.load_config()

        # Act
        config_manager.toggle_exclusion("Vim")

        # Assert
        assert config_manager.is_excluded("Vim") is False

    @pytest.mark.unit
    def test_toggle_exclusion_persists(self, yaml_config_dir: Path) -> None:
        """Toggle exclusion persists change to session file."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()

        # Act
        config_manager.toggle_exclusion("Bash")

        # Assert - verify persisted
        session_content = (yaml_config_dir / "session.yaml").read_text()
        assert "Bash" in session_content


class TestConfigManagerIncludedDotfiles:
    """Tests for get_included_dotfiles method."""

    @pytest.mark.unit
    def test_get_included_dotfiles_all(self, yaml_config_dir: Path) -> None:
        """Get all dotfiles when none are excluded."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()

        # Act
        included = config_manager.get_included_dotfiles()

        # Assert
        assert len(included) == 3
        app_names = [df["application"] for df in included]
        assert "Bash" in app_names
        assert "Vim" in app_names
        assert "Konsole" in app_names

    @pytest.mark.unit
    def test_get_included_dotfiles_with_exclusions(
        self, yaml_config_dir_with_exclusions: Path
    ) -> None:
        """Get only non-excluded dotfiles."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir_with_exclusions, expand_path)
        config_manager.load_config()

        # Act
        included = config_manager.get_included_dotfiles()

        # Assert
        assert len(included) == 1
        assert included[0]["application"] == "Bash"

    @pytest.mark.unit
    def test_get_included_dotfiles_after_toggle(
        self, yaml_config_dir: Path
    ) -> None:
        """Get included dotfiles updates after toggle."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()

        # Act
        config_manager.toggle_exclusion("Bash")
        config_manager.toggle_exclusion("Vim")
        included = config_manager.get_included_dotfiles()

        # Assert
        assert len(included) == 1
        assert included[0]["application"] == "Konsole"


class TestConfigManagerSaveConfig:
    """Tests for save_config with YAML format."""

    @pytest.mark.unit
    def test_save_config_updates_settings(self, yaml_config_dir: Path) -> None:
        """Save config persists option changes to settings.yaml."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()

        # Act
        config_manager.options["archive"] = True
        success, error = config_manager.save_config()

        # Assert
        assert success is True
        settings_content = (yaml_config_dir / "settings.yaml").read_text()
        assert "archive: true" in settings_content

    @pytest.mark.unit
    def test_save_config_preserves_dotfiles(self, yaml_config_dir: Path) -> None:
        """Save config does not corrupt dotfiles.yaml."""
        # Arrange
        config_manager = ConfigManager(yaml_config_dir, expand_path)
        config_manager.load_config()
        initial_count = config_manager.get_dotfile_count()

        # Act
        config_manager.options["archive"] = True
        config_manager.save_config()

        # Reload and verify
        config_manager2 = ConfigManager(yaml_config_dir, expand_path)
        config_manager2.load_config()

        # Assert
        assert config_manager2.get_dotfile_count() == initial_count
