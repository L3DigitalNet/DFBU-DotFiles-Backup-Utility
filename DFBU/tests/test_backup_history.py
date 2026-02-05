"""Tests for BackupHistoryManager service."""

from pathlib import Path

import pytest

from gui.backup_history import BackupHistoryManager


class TestBackupHistoryManagerInit:
    """Tests for BackupHistoryManager initialization."""

    @pytest.mark.unit
    def test_backup_history_manager_initialization(self, tmp_path: Path) -> None:
        """BackupHistoryManager should initialize with empty history."""
        manager = BackupHistoryManager(config_path=tmp_path)
        assert manager.get_entry_count() == 0


class TestBackupHistoryManagerRecording:
    """Tests for recording backup operations."""

    @pytest.mark.unit
    def test_backup_history_manager_record_backup(self, tmp_path: Path) -> None:
        """BackupHistoryManager should record backup entries."""
        manager = BackupHistoryManager(config_path=tmp_path)

        manager.record_backup(
            items_backed=10,
            size_bytes=1024,
            duration_seconds=2.5,
            success=True,
            backup_type="mirror",
            profile="Default",
        )

        assert manager.get_entry_count() == 1

    @pytest.mark.unit
    def test_backup_history_manager_record_multiple(self, tmp_path: Path) -> None:
        """BackupHistoryManager should record multiple entries."""
        manager = BackupHistoryManager(config_path=tmp_path)

        manager.record_backup(10, 1024, 2.0, True, "mirror", "Default")
        manager.record_backup(5, 512, 1.5, True, "archive", "Work")
        manager.record_backup(0, 0, 0.5, False, "mirror", "Default")

        assert manager.get_entry_count() == 3


class TestBackupHistoryManagerMetrics:
    """Tests for metrics calculation."""

    @pytest.mark.unit
    def test_backup_history_manager_calculates_metrics(self, tmp_path: Path) -> None:
        """BackupHistoryManager should calculate dashboard metrics."""
        manager = BackupHistoryManager(config_path=tmp_path)

        # Record some backups
        manager.record_backup(10, 1024, 2.0, True, "mirror", "Default")
        manager.record_backup(5, 512, 1.5, True, "archive", "Default")
        manager.record_backup(0, 0, 0.5, False, "mirror", "Default")

        metrics = manager.get_metrics()

        assert metrics["total_backups"] == 3
        assert metrics["successful_backups"] == 2
        assert metrics["failed_backups"] == 1
        assert metrics["success_rate"] == pytest.approx(0.667, rel=0.01)

    @pytest.mark.unit
    def test_backup_history_manager_metrics_empty(self, tmp_path: Path) -> None:
        """BackupHistoryManager should handle empty history."""
        manager = BackupHistoryManager(config_path=tmp_path)

        metrics = manager.get_metrics()

        assert metrics["total_backups"] == 0
        assert metrics["success_rate"] == 0.0
        assert metrics["last_backup_timestamp"] is None


class TestBackupHistoryManagerPersistence:
    """Tests for YAML persistence."""

    @pytest.mark.unit
    def test_backup_history_manager_persists_to_yaml(self, tmp_path: Path) -> None:
        """BackupHistoryManager should persist history to YAML."""
        manager = BackupHistoryManager(config_path=tmp_path)
        manager.record_backup(10, 1024, 2.0, True, "mirror", "Default")

        # Verify file was created
        history_file = tmp_path / "backup_history.yaml"
        assert history_file.exists()

    @pytest.mark.unit
    def test_backup_history_manager_loads_from_yaml(self, tmp_path: Path) -> None:
        """BackupHistoryManager should load existing history on init."""
        # First manager records history
        manager1 = BackupHistoryManager(config_path=tmp_path)
        manager1.record_backup(10, 1024, 2.0, True, "mirror", "Default")
        manager1.record_backup(5, 512, 1.5, True, "archive", "Work")

        # Second manager should load it
        manager2 = BackupHistoryManager(config_path=tmp_path)

        assert manager2.get_entry_count() == 2


class TestBackupHistoryManagerRecentHistory:
    """Tests for recent history retrieval."""

    @pytest.mark.unit
    def test_backup_history_manager_get_recent(self, tmp_path: Path) -> None:
        """BackupHistoryManager should return recent entries."""
        manager = BackupHistoryManager(config_path=tmp_path)

        for i in range(5):
            manager.record_backup(i, i * 100, 1.0, True, "mirror", "Default")

        recent = manager.get_recent_history(count=3)

        assert len(recent) == 3
        # Most recent first
        assert recent[0]["items_backed"] == 4
        assert recent[2]["items_backed"] == 2
