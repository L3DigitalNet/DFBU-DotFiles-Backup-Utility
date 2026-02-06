"""
Comprehensive tests for worker thread signals and lifecycle.

Tests BackupWorker and RestoreWorker signal emissions and cleanup.
"""

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from PySide6.QtCore import QThread

from gui.model import DFBUModel
from gui.viewmodel import DFBUViewModel


def create_yaml_config(
    config_dir: Path, dotfiles: list[dict[str, Any]] | None = None
) -> Path:
    """Create YAML config files for testing."""
    config_dir.mkdir(parents=True, exist_ok=True)

    # settings.yaml
    (config_dir / "settings.yaml").write_text("""
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
""")

    # dotfiles.yaml
    if dotfiles:
        content = ""
        for df in dotfiles:
            name = df.get("name", "TestApp")
            desc = df.get("description", "Test file")
            path = df.get("path", "~/.testfile")
            content += f"""
{name}:
  description: {desc}
  path: {path}
  tags: Test
"""
        (config_dir / "dotfiles.yaml").write_text(content)
    else:
        (config_dir / "dotfiles.yaml").write_text("""
TestApp:
  description: Test file
  path: ~/.testfile
  tags: Test
""")

    # session.yaml
    (config_dir / "session.yaml").write_text("excluded: []")

    return config_dir


class TestBackupWorkerSignals:
    """Test BackupWorker signal emissions."""

    @pytest.fixture
    def viewmodel(self, tmp_path):
        """Create viewmodel with test config."""
        config_dir = create_yaml_config(tmp_path / "config")
        model = DFBUModel(config_dir)
        return DFBUViewModel(model)

    @pytest.mark.skip(
        reason="Qt threading lifecycle issue causes fatal Python error - functionality tested in test_workers_comprehensive.py"
    )
    def test_backup_worker_emits_progress_signal(self, qtbot, viewmodel, tmp_path):
        """Test backup worker emits progress_updated signal."""
        # Arrange
        viewmodel.command_load_config()

        # Create test file
        test_file = tmp_path / ".testfile"
        test_file.write_text("test content")

        # Mock Path.home() and Path.expanduser()
        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch("pathlib.Path.expanduser", return_value=test_file),
        ):
            # Start backup
            viewmodel.command_start_backup()

            # Act & Assert - Wait for progress signal
            with qtbot.waitSignal(viewmodel.progress_updated, timeout=5000) as blocker:
                pass

            # Signal should have been emitted with progress value
            assert blocker.signal_triggered
            assert blocker.args[0] >= 0  # Progress value

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_backup_worker_emits_item_processed_signal(
        self, qtbot, viewmodel, tmp_path
    ):
        """Test backup worker emits item_processed signal through viewmodel."""
        # Arrange
        viewmodel.command_load_config()

        test_file = tmp_path / ".testfile"
        test_file.write_text("test content")

        # Use QTimer to wait for worker to complete
        processed_items = []

        def capture_processed(src, dest):
            processed_items.append((src, dest))

        viewmodel.item_processed.connect(capture_processed)

        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch("pathlib.Path.expanduser", return_value=test_file),
        ):
            viewmodel.command_start_backup()

            # Act & Assert - wait for operation to complete
            with qtbot.waitSignal(viewmodel.operation_finished, timeout=5000):
                pass

            # Check that item_processed was emitted at least once
            assert len(processed_items) > 0
            assert isinstance(processed_items[0][0], str)  # source_path
            assert isinstance(processed_items[0][1], str)  # dest_path

    @pytest.mark.skip(
        reason="Qt threading lifecycle issue causes fatal Python error - functionality tested in test_workers_comprehensive.py"
    )
    def test_backup_worker_emits_finished_signal(self, qtbot, viewmodel, tmp_path):
        """Test backup worker emits operation_finished signal through viewmodel."""
        # Arrange
        viewmodel.command_load_config()

        test_file = tmp_path / ".testfile"
        test_file.write_text("test content")

        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch("pathlib.Path.expanduser", return_value=test_file),
        ):
            viewmodel.command_start_backup()

            # Act & Assert - operation_finished signal has summary string argument
            with qtbot.waitSignal(
                viewmodel.operation_finished, timeout=5000
            ) as blocker:
                pass

            assert blocker.signal_triggered
            # Verify summary argument is a string
            assert isinstance(blocker.args[0], str)

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_backup_worker_emits_error_signal_on_failure(self, qtbot, viewmodel):
        """Test backup worker emits error_occurred signal on failure."""
        # Arrange
        viewmodel.command_load_config()

        # Mock backup operation to raise exception
        with patch.object(
            viewmodel.model, "perform_backup", side_effect=OSError("Test error")
        ):
            viewmodel.command_start_backup()

            # Act & Assert
            with qtbot.waitSignal(viewmodel.error_occurred, timeout=5000) as blocker:
                pass

            assert blocker.signal_triggered
            context, error_msg = blocker.args[0], blocker.args[1]
            assert isinstance(context, str)
            assert isinstance(error_msg, str)
            assert len(error_msg) > 0

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_backup_worker_emits_item_skipped_signal(self, qtbot, viewmodel, tmp_path):
        """Test backup worker emits item_skipped signal for disabled items."""
        # Arrange
        config = tmp_path / "config.toml"
        config.write_text("""
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true

[[dotfile]]
category = "Test"
application = "TestApp"
description = "Test file"
path = "~/.testfile"
enabled = false
""")

        model = DFBUModel(config)
        vm = DFBUViewModel(model)
        vm.command_load_config()

        # Act
        vm.command_start_backup()

        # Assert
        with qtbot.waitSignal(vm.item_skipped, timeout=5000) as blocker:
            pass

        assert blocker.signal_triggered
        # Args: (index, item_name, reason)
        assert isinstance(blocker.args[0], int)
        assert isinstance(blocker.args[1], str)
        assert isinstance(blocker.args[2], str)
        assert "disabled" in blocker.args[2].lower()


class TestRestoreWorkerSignals:
    """Test RestoreWorker signal emissions."""

    @pytest.fixture
    def viewmodel_with_backup(self, tmp_path):
        """Create viewmodel with existing backup."""
        config = tmp_path / "config.toml"
        config.write_text("""
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true

[[dotfile]]
category = "Test"
application = "TestApp"
description = "Test file"
path = "~/.testfile"
enabled = true
""")

        model = DFBUModel(config)
        vm = DFBUViewModel(model)
        vm.command_load_config()

        # Create mirror directory with test file
        mirror_dir = tmp_path / "test_mirror"
        mirror_dir.mkdir()
        (mirror_dir / ".testfile").write_text("backed up content")

        return vm

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_restore_worker_emits_progress_signal(
        self, qtbot, viewmodel_with_backup, tmp_path
    ):
        """Test restore worker emits progress_updated signal."""
        # Arrange
        vm = viewmodel_with_backup

        with patch("pathlib.Path.home", return_value=tmp_path):
            vm.command_start_restore()

            # Act & Assert
            with qtbot.waitSignal(vm.progress_updated, timeout=5000) as blocker:
                pass

            assert blocker.signal_triggered
            assert blocker.args[0] >= 0

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_restore_worker_emits_item_processed_signal(
        self, qtbot, viewmodel_with_backup, tmp_path
    ):
        """Test restore worker emits item_processed signal."""
        # Arrange
        vm = viewmodel_with_backup

        with patch("pathlib.Path.home", return_value=tmp_path):
            vm.command_start_restore()

            # Act & Assert
            with qtbot.waitSignal(vm.item_processed, timeout=5000) as blocker:
                pass

            assert blocker.signal_triggered
            assert isinstance(blocker.args[0], int)
            assert isinstance(blocker.args[1], str)
            assert isinstance(blocker.args[2], bool)

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_restore_worker_emits_finished_signal(
        self, qtbot, viewmodel_with_backup, tmp_path
    ):
        """Test restore worker emits operation_finished signal."""
        # Arrange
        vm = viewmodel_with_backup

        with patch("pathlib.Path.home", return_value=tmp_path):
            vm.command_start_restore()

            # Act & Assert
            with qtbot.waitSignal(vm.operation_finished, timeout=5000) as blocker:
                pass

            assert blocker.signal_triggered
            stats = blocker.args[0]
            assert isinstance(stats, dict)
            assert "total" in stats
            assert "successful" in stats

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_restore_worker_emits_error_signal_on_failure(
        self, qtbot, viewmodel_with_backup
    ):
        """Test restore worker emits error_occurred signal on failure."""
        # Arrange
        vm = viewmodel_with_backup

        with patch.object(
            vm.model, "perform_restore", side_effect=OSError("Test error")
        ):
            vm.command_start_restore()

            # Act & Assert
            with qtbot.waitSignal(vm.error_occurred, timeout=5000) as blocker:
                pass

            assert blocker.signal_triggered
            context, error_msg = blocker.args[0], blocker.args[1]
            assert isinstance(context, str)
            assert isinstance(error_msg, str)
            assert len(error_msg) > 0


class TestWorkerThreadLifecycle:
    """Test worker thread creation and cleanup."""

    @pytest.fixture
    def viewmodel(self, tmp_path):
        """Create viewmodel for testing."""
        config_dir = create_yaml_config(tmp_path / "config")
        model = DFBUModel(config_dir)
        return DFBUViewModel(model)

    @pytest.mark.skip(
        reason="Qt threading lifecycle issue causes fatal Python error - functionality tested in test_workers_comprehensive.py"
    )
    def test_backup_creates_worker_thread(self, qtbot, viewmodel, tmp_path):
        """Test backup operation creates worker and thread."""
        # Arrange
        viewmodel.command_load_config()

        test_file = tmp_path / ".testfile"
        test_file.write_text("test")

        # Act
        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch("pathlib.Path.expanduser", return_value=test_file),
        ):
            viewmodel.command_start_backup()

            # Assert - Worker and thread should be created
            assert viewmodel.backup_worker is not None
            assert viewmodel.backup_worker is not None
            assert isinstance(viewmodel.backup_worker, QThread)

            # Wait for completion
            with qtbot.waitSignal(viewmodel.operation_finished, timeout=5000):
                pass

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_restore_creates_worker_thread(self, qtbot, viewmodel, tmp_path):
        """Test restore operation creates worker and thread."""
        # Arrange
        viewmodel.command_load_config()

        mirror_dir = tmp_path / "test_mirror"
        mirror_dir.mkdir()
        (mirror_dir / ".testfile").write_text("backed up")

        # Act
        with patch("pathlib.Path.home", return_value=tmp_path):
            viewmodel.command_start_restore()

            # Assert
            assert viewmodel.restore_worker is not None
            assert viewmodel.restore_worker is not None
            assert isinstance(viewmodel.restore_worker, QThread)

            with qtbot.waitSignal(viewmodel.operation_finished, timeout=5000):
                pass

    @pytest.mark.skip(
        reason="Qt threading lifecycle issue causes fatal Python error - functionality tested in test_workers_comprehensive.py"
    )
    def test_worker_cleanup_after_backup(self, qtbot, viewmodel, tmp_path):
        """Test worker is properly cleaned up after backup."""
        # Arrange
        viewmodel.command_load_config()

        test_file = tmp_path / ".testfile"
        test_file.write_text("test")

        # Act
        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch("pathlib.Path.expanduser", return_value=test_file),
        ):
            viewmodel.command_start_backup()

            with qtbot.waitSignal(viewmodel.operation_finished, timeout=5000):
                pass

            # Assert - Worker should be scheduled for deletion
            # (Worker reference should be None after cleanup)
            assert viewmodel.backup_worker is None

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_worker_cleanup_after_restore(self, qtbot, viewmodel, tmp_path):
        """Test worker is properly cleaned up after restore."""
        # Arrange
        viewmodel.command_load_config()

        mirror_dir = tmp_path / "test_mirror"
        mirror_dir.mkdir()
        (mirror_dir / ".testfile").write_text("backed up")

        # Act
        with patch("pathlib.Path.home", return_value=tmp_path):
            viewmodel.command_start_restore()

            with qtbot.waitSignal(viewmodel.operation_finished, timeout=5000):
                pass

            # Assert
            assert viewmodel.restore_worker is None

    @pytest.mark.skip(
        reason="Qt threading lifecycle issue causes fatal Python error - functionality tested in test_workers_comprehensive.py"
    )
    def test_multiple_backup_operations_cleanup_properly(
        self, qtbot, viewmodel, tmp_path
    ):
        """Test multiple backup operations don't leak workers."""
        # Arrange
        viewmodel.command_load_config()

        test_file = tmp_path / ".testfile"
        test_file.write_text("test")

        # Act - Run backup twice
        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch("pathlib.Path.expanduser", return_value=test_file),
        ):
            # First backup
            viewmodel.command_start_backup()
            with qtbot.waitSignal(viewmodel.operation_finished, timeout=5000):
                pass

            first_worker = viewmodel.backup_worker

            # Second backup
            viewmodel.command_start_backup()
            with qtbot.waitSignal(viewmodel.operation_finished, timeout=5000):
                pass

            second_worker = viewmodel.backup_worker

            # Assert - Both should be None (cleaned up)
            assert first_worker is None
            assert second_worker is None


class TestWorkerSignalConnections:
    """Test worker signal/slot connections."""

    @pytest.fixture
    def viewmodel(self, tmp_path):
        """Create viewmodel for testing."""
        config_dir = create_yaml_config(tmp_path / "config")
        model = DFBUModel(config_dir)
        return DFBUViewModel(model)

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_backup_worker_signals_connected_to_viewmodel(
        self, qtbot, viewmodel, tmp_path
    ):
        """Test backup worker signals are properly connected to viewmodel."""
        # Arrange
        viewmodel.command_load_config()

        test_file = tmp_path / ".testfile"
        test_file.write_text("test")

        # Track signal emissions
        progress_received = []
        item_received = []

        def on_progress(value):
            progress_received.append(value)

        def on_item(idx, name, success):
            item_received.append((idx, name, success))

        viewmodel.progress_updated.connect(on_progress)
        viewmodel.item_processed.connect(on_item)

        # Act
        with (
            patch("pathlib.Path.home", return_value=tmp_path),
            patch("pathlib.Path.expanduser", return_value=test_file),
        ):
            viewmodel.command_start_backup()

            with qtbot.waitSignal(viewmodel.operation_finished, timeout=5000):
                pass

        # Assert
        assert len(progress_received) > 0
        assert len(item_received) > 0

    @pytest.mark.skip(
        reason="Integration test requires complex setup - worker functionality tested in test_workers_comprehensive.py"
    )
    def test_restore_worker_signals_connected_to_viewmodel(
        self, qtbot, viewmodel, tmp_path
    ):
        """Test restore worker signals are properly connected to viewmodel."""
        # Arrange
        viewmodel.command_load_config()

        mirror_dir = tmp_path / "test_mirror"
        mirror_dir.mkdir()
        (mirror_dir / ".testfile").write_text("backed up")

        progress_received = []
        item_received = []

        def on_progress(value):
            progress_received.append(value)

        def on_item(idx, name, success):
            item_received.append((idx, name, success))

        viewmodel.progress_updated.connect(on_progress)
        viewmodel.item_processed.connect(on_item)

        # Act
        with patch("pathlib.Path.home", return_value=tmp_path):
            viewmodel.command_start_restore()

            with qtbot.waitSignal(viewmodel.operation_finished, timeout=5000):
                pass

        # Assert
        assert len(progress_received) > 0
        assert len(item_received) > 0
