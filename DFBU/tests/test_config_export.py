"""
Tests for the Export and Import Config features.

Tests cover:
    - Export button exists in the backup tab UI
    - Import button exists in the backup tab UI
    - Successful export of all config files
    - Error reporting for missing source files
    - Successful import of config files
    - Import validation of YAML files
    - Import creates backups before overwriting
    - Import with no config files in source
    - Import with invalid YAML
"""

from pathlib import Path

import pytest
from PySide6.QtWidgets import QPushButton


# =========================================================================
# Export Tests
# =========================================================================


@pytest.mark.gui
def test_export_config_button_exists(qapp, qtbot):
    """Backup tab should have an 'Export Config' button."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    btn = window.findChild(QPushButton, "exportConfigButton")
    assert btn is not None


@pytest.mark.gui
def test_import_config_button_exists(qapp, qtbot):
    """Backup tab should have an 'Import Config' button."""
    from gui.model import DFBUModel
    from gui.view import MainWindow
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)
    window = MainWindow(vm, "0.0.0-test")

    btn = window.findChild(QPushButton, "importConfigButton")
    assert btn is not None


@pytest.mark.unit
def test_export_config_copies_files(tmp_path: Path) -> None:
    """Export should copy dotfiles.yaml and settings.yaml to the target directory."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)

    dest_dir = tmp_path / "export"
    dest_dir.mkdir()

    success, message = vm.command_export_config(dest_dir)

    assert success is True
    assert (dest_dir / "dotfiles.yaml").exists()
    assert (dest_dir / "settings.yaml").exists()


@pytest.mark.unit
def test_export_config_reports_missing_files(tmp_path: Path) -> None:
    """Export should report errors for missing source files."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    # Create a config dir with only one file
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "dotfiles.yaml").write_text(
        "Bash:\n  description: test\n  path: ~/.bashrc\n", encoding="utf-8"
    )
    # settings.yaml is missing
    (config_dir / "session.yaml").write_text("excluded: []\n", encoding="utf-8")

    model = DFBUModel(config_dir)
    vm = DFBUViewModel(model)

    dest_dir = tmp_path / "export"
    dest_dir.mkdir()

    success, message = vm.command_export_config(dest_dir)

    assert success is False
    assert "settings.yaml" in message


@pytest.mark.unit
def test_export_includes_session_and_dfbuignore(tmp_path: Path) -> None:
    """Export should include session.yaml and .dfbuignore when present."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)

    dest_dir = tmp_path / "export"
    dest_dir.mkdir()

    success, message = vm.command_export_config(dest_dir)

    assert success is True
    assert (dest_dir / "session.yaml").exists()
    assert (dest_dir / ".dfbuignore").exists()


@pytest.mark.unit
def test_export_to_nonexistent_dir(tmp_path: Path) -> None:
    """Export should fail with clear message for non-existent directory."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    config_path = Path(__file__).parent.parent / "data"
    model = DFBUModel(config_path)
    vm = DFBUViewModel(model)

    success, message = vm.command_export_config(tmp_path / "nonexistent")

    assert success is False
    assert "does not exist" in message


# =========================================================================
# Import Tests
# =========================================================================


@pytest.mark.unit
def test_import_config_copies_files(tmp_path: Path) -> None:
    """Import should copy config files to the config directory."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    # Create source directory with config files
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "dotfiles.yaml").write_text(
        "Vim:\n  description: Vim editor\n  path: ~/.vimrc\n", encoding="utf-8"
    )
    (source_dir / "settings.yaml").write_text(
        "paths:\n  mirror_dir: ~/backups\n  archive_dir: ~/archives\n"
        "  restore_backup_dir: ~/.local/share/dfbu/restore-backups\n"
        "options:\n  mirror: true\n  archive: true\n  hostname_subdir: true\n"
        "  date_subdir: false\n  archive_format: tar.gz\n"
        "  archive_compression_level: 5\n  rotate_archives: true\n"
        "  max_archives: 5\n  pre_restore_backup: true\n"
        "  max_restore_backups: 5\n",
        encoding="utf-8",
    )

    # Create target config directory with existing files
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "dotfiles.yaml").write_text(
        "OldApp:\n  description: Old\n  path: ~/.old\n", encoding="utf-8"
    )
    (config_dir / "settings.yaml").write_text(
        "paths:\n  mirror_dir: ~/old\n  archive_dir: ~/old\n"
        "  restore_backup_dir: ~/.local/share/dfbu/restore-backups\n"
        "options:\n  mirror: false\n  archive: false\n  hostname_subdir: false\n"
        "  date_subdir: false\n  archive_format: tar.gz\n"
        "  archive_compression_level: 5\n  rotate_archives: true\n"
        "  max_archives: 5\n  pre_restore_backup: true\n"
        "  max_restore_backups: 5\n",
        encoding="utf-8",
    )

    model = DFBUModel(config_dir)
    vm = DFBUViewModel(model)

    success, message = vm.command_import_config(source_dir)

    assert success is True
    assert "dotfiles.yaml" in message
    assert "settings.yaml" in message

    # Verify imported content
    content = (config_dir / "dotfiles.yaml").read_text()
    assert "Vim" in content


@pytest.mark.unit
def test_import_config_creates_backups(tmp_path: Path) -> None:
    """Import should create backups of existing config files."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    # Create source and config directories
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "dotfiles.yaml").write_text(
        "Vim:\n  description: New\n  path: ~/.vimrc\n", encoding="utf-8"
    )

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "dotfiles.yaml").write_text(
        "OldApp:\n  description: Old\n  path: ~/.old\n", encoding="utf-8"
    )
    (config_dir / "settings.yaml").write_text(
        "paths:\n  mirror_dir: ~/old\n  archive_dir: ~/old\n"
        "  restore_backup_dir: ~/.local/share/dfbu/restore-backups\n"
        "options:\n  mirror: false\n  archive: false\n  hostname_subdir: false\n"
        "  date_subdir: false\n  archive_format: tar.gz\n"
        "  archive_compression_level: 5\n  rotate_archives: true\n"
        "  max_archives: 5\n  pre_restore_backup: true\n"
        "  max_restore_backups: 5\n",
        encoding="utf-8",
    )

    model = DFBUModel(config_dir)
    vm = DFBUViewModel(model)

    vm.command_import_config(source_dir)

    # Check that backup was created for dotfiles.yaml
    backup_dir = config_dir / ".dotfiles.yaml.backups"
    assert backup_dir.exists()
    assert len(list(backup_dir.glob("*.yaml"))) >= 1


@pytest.mark.unit
def test_import_config_no_files_in_source(tmp_path: Path) -> None:
    """Import should fail when source directory has no config files."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    source_dir = tmp_path / "empty_source"
    source_dir.mkdir()

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "settings.yaml").write_text(
        "paths:\n  mirror_dir: ~/m\n  archive_dir: ~/a\n"
        "  restore_backup_dir: ~/r\n"
        "options:\n  mirror: true\n  archive: true\n  hostname_subdir: true\n"
        "  date_subdir: false\n  archive_format: tar.gz\n"
        "  archive_compression_level: 5\n  rotate_archives: true\n"
        "  max_archives: 5\n  pre_restore_backup: true\n"
        "  max_restore_backups: 5\n",
        encoding="utf-8",
    )
    (config_dir / "dotfiles.yaml").write_text(
        "Bash:\n  description: test\n  path: ~/.bashrc\n", encoding="utf-8"
    )

    model = DFBUModel(config_dir)
    vm = DFBUViewModel(model)

    success, message = vm.command_import_config(source_dir)

    assert success is False
    assert "No configuration files found" in message


@pytest.mark.unit
def test_import_config_invalid_yaml(tmp_path: Path) -> None:
    """Import should fail with validation error for invalid YAML files."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "dotfiles.yaml").write_text(
        "invalid: yaml: content:\n  - [broken", encoding="utf-8"
    )

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "settings.yaml").write_text(
        "paths:\n  mirror_dir: ~/m\n  archive_dir: ~/a\n"
        "  restore_backup_dir: ~/r\n"
        "options:\n  mirror: true\n  archive: true\n  hostname_subdir: true\n"
        "  date_subdir: false\n  archive_format: tar.gz\n"
        "  archive_compression_level: 5\n  rotate_archives: true\n"
        "  max_archives: 5\n  pre_restore_backup: true\n"
        "  max_restore_backups: 5\n",
        encoding="utf-8",
    )
    (config_dir / "dotfiles.yaml").write_text(
        "Bash:\n  description: test\n  path: ~/.bashrc\n", encoding="utf-8"
    )

    model = DFBUModel(config_dir)
    vm = DFBUViewModel(model)

    success, message = vm.command_import_config(source_dir)

    assert success is False
    assert "Validation errors" in message


@pytest.mark.unit
def test_import_from_nonexistent_dir(tmp_path: Path) -> None:
    """Import should fail with clear message for non-existent directory."""
    from gui.model import DFBUModel
    from gui.viewmodel import DFBUViewModel

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "settings.yaml").write_text(
        "paths:\n  mirror_dir: ~/m\n  archive_dir: ~/a\n"
        "  restore_backup_dir: ~/r\n"
        "options:\n  mirror: true\n  archive: true\n  hostname_subdir: true\n"
        "  date_subdir: false\n  archive_format: tar.gz\n"
        "  archive_compression_level: 5\n  rotate_archives: true\n"
        "  max_archives: 5\n  pre_restore_backup: true\n"
        "  max_restore_backups: 5\n",
        encoding="utf-8",
    )
    (config_dir / "dotfiles.yaml").write_text(
        "Bash:\n  description: test\n  path: ~/.bashrc\n", encoding="utf-8"
    )

    model = DFBUModel(config_dir)
    vm = DFBUViewModel(model)

    success, message = vm.command_import_config(tmp_path / "nonexistent")

    assert success is False
    assert "does not exist" in message
