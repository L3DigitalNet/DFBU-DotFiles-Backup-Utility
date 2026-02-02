"""
Integration tests for Configuration tab options.

Tests that new verification and size management options
are properly loaded and saved through the UI model layer.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 02-01-2026
License: MIT
"""

from pathlib import Path

import pytest

from gui.model import DFBUModel


@pytest.fixture
def yaml_config_with_size_options(tmp_path: Path) -> Path:
    """
    Create a temporary directory with YAML configuration including size options.

    Args:
        tmp_path: pytest built-in temporary directory fixture

    Returns:
        Path: Directory containing YAML configuration files
    """
    # Create settings.yaml with all options including new v1.1.0 ones
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
  rotate_archives: true
  max_archives: 5
  pre_restore_backup: true
  max_restore_backups: 5
  verify_after_backup: false
  hash_verification: false
  size_check_enabled: true
  size_warning_threshold_mb: 10
  size_alert_threshold_mb: 100
  size_critical_threshold_mb: 1024
""")

    # Create dotfiles.yaml
    dotfiles_file = tmp_path / "dotfiles.yaml"
    dotfiles_file.write_text("""
TestApp:
  description: Test dotfile
  path: ~/test.txt
""")

    # Create session.yaml
    session_file = tmp_path / "session.yaml"
    session_file.write_text("""
excluded: []
""")

    return tmp_path


@pytest.mark.integration
class TestConfigTabVerificationOptions:
    """Test verification options in Configuration tab."""

    def test_verify_after_backup_option_loads(
        self, yaml_config_with_size_options: Path
    ) -> None:
        """Verify after backup option loads correctly from config."""
        # Arrange - pass directory path, not file path
        model = DFBUModel(yaml_config_with_size_options)

        # Act
        success, _ = model.load_config()

        # Assert
        assert success
        assert model.options.get("verify_after_backup") is False

    def test_verify_after_backup_option_saved(
        self, yaml_config_with_size_options: Path
    ) -> None:
        """Verify after backup option saves correctly."""
        # Arrange - pass directory path, not file path
        model = DFBUModel(yaml_config_with_size_options)
        model.load_config()
        model.options["verify_after_backup"] = False

        # Act
        model.options["verify_after_backup"] = True
        success, _ = model.save_config()

        # Assert
        assert success
        assert model.options["verify_after_backup"] is True

    def test_hash_verification_option_loads(
        self, yaml_config_with_size_options: Path
    ) -> None:
        """Hash verification option loads correctly from config."""
        # Arrange - pass directory path, not file path
        model = DFBUModel(yaml_config_with_size_options)

        # Act
        success, _ = model.load_config()

        # Assert
        assert success
        assert model.options.get("hash_verification") is False

    def test_hash_verification_option_saved(
        self, yaml_config_with_size_options: Path
    ) -> None:
        """Hash verification option saves correctly."""
        # Arrange - pass directory path, not file path
        model = DFBUModel(yaml_config_with_size_options)
        model.load_config()
        model.options["hash_verification"] = False

        # Act
        model.options["hash_verification"] = True
        success, _ = model.save_config()

        # Assert
        assert success
        assert model.options["hash_verification"] is True


@pytest.mark.integration
class TestConfigTabSizeOptions:
    """Test size management options in Configuration tab."""

    def test_size_check_enabled_option_loads(
        self, yaml_config_with_size_options: Path
    ) -> None:
        """Size check enabled option loads correctly from config."""
        # Arrange - pass directory path, not file path
        model = DFBUModel(yaml_config_with_size_options)

        # Act
        success, _ = model.load_config()

        # Assert
        assert success
        assert model.options.get("size_check_enabled") is True

    def test_size_check_enabled_option_saved(
        self, yaml_config_with_size_options: Path
    ) -> None:
        """Size check enabled option saves correctly."""
        # Arrange - pass directory path, not file path
        model = DFBUModel(yaml_config_with_size_options)
        model.load_config()

        # Act
        model.options["size_check_enabled"] = False
        success, _ = model.save_config()

        # Assert
        assert success
        assert model.options["size_check_enabled"] is False

    def test_size_warning_threshold_loads(
        self, yaml_config_with_size_options: Path
    ) -> None:
        """Size warning threshold loads correctly from config."""
        # Arrange - pass directory path, not file path
        model = DFBUModel(yaml_config_with_size_options)

        # Act
        success, _ = model.load_config()

        # Assert
        assert success
        assert model.options.get("size_warning_threshold_mb") == 10

    def test_size_thresholds_saved(
        self, yaml_config_with_size_options: Path
    ) -> None:
        """Size threshold options save correctly."""
        # Arrange - pass directory path, not file path
        model = DFBUModel(yaml_config_with_size_options)
        model.load_config()

        # Act
        model.options["size_warning_threshold_mb"] = 25
        model.options["size_alert_threshold_mb"] = 250
        model.options["size_critical_threshold_mb"] = 2048
        success, _ = model.save_config()

        # Assert
        assert success
        assert model.options["size_warning_threshold_mb"] == 25
        assert model.options["size_alert_threshold_mb"] == 250
        assert model.options["size_critical_threshold_mb"] == 2048

    def test_size_thresholds_persist_after_reload(
        self, yaml_config_with_size_options: Path
    ) -> None:
        """Size threshold options persist across save/load cycle."""
        # Arrange - pass directory path, not file path
        model = DFBUModel(yaml_config_with_size_options)
        model.load_config()

        # Act - modify and save
        model.options["size_warning_threshold_mb"] = 50
        model.options["size_alert_threshold_mb"] = 500
        model.options["size_critical_threshold_mb"] = 5000
        model.save_config()

        # Create new model and load
        model2 = DFBUModel(yaml_config_with_size_options)
        success, _ = model2.load_config()

        # Assert
        assert success
        assert model2.options["size_warning_threshold_mb"] == 50
        assert model2.options["size_alert_threshold_mb"] == 500
        assert model2.options["size_critical_threshold_mb"] == 5000
