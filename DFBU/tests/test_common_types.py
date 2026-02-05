"""Tests for common type definitions."""

import pytest
from core.common_types import (
    DotFileDict,
    SettingsDict,
    PathsDict,
    OptionsDict,
    SessionDict,
    LegacyDotFileDict,
    ProfileDict,
    PreviewItemDict,
    BackupPreviewDict,
)


class TestDotFileDict:
    """Tests for DotFileDict TypedDict."""

    @pytest.mark.unit
    def test_dotfile_dict_single_path(self) -> None:
        """DotFileDict accepts single path as string."""
        dotfile: DotFileDict = {
            "description": "Shell configuration",
            "path": "~/.bashrc",
        }
        assert dotfile["description"] == "Shell configuration"
        assert dotfile["path"] == "~/.bashrc"

    @pytest.mark.unit
    def test_dotfile_dict_multiple_paths(self) -> None:
        """DotFileDict accepts multiple paths as list."""
        dotfile: DotFileDict = {
            "description": "Terminal emulator",
            "paths": ["~/.config/konsolerc", "~/.local/share/konsole/"],
        }
        assert dotfile["description"] == "Terminal emulator"
        assert dotfile["paths"] == ["~/.config/konsolerc", "~/.local/share/konsole/"]

    @pytest.mark.unit
    def test_dotfile_dict_with_tags(self) -> None:
        """DotFileDict accepts optional tags string."""
        dotfile: DotFileDict = {
            "description": "Git configuration",
            "path": "~/.gitconfig",
            "tags": "dev, essential",
        }
        assert dotfile["tags"] == "dev, essential"


class TestSettingsDict:
    """Tests for SettingsDict TypedDict."""

    @pytest.mark.unit
    def test_settings_dict_structure(self) -> None:
        """SettingsDict contains paths and options."""
        settings: SettingsDict = {
            "paths": {
                "mirror_dir": "~/backups/mirror",
                "archive_dir": "~/backups/archives",
                "restore_backup_dir": "~/.local/share/dfbu/restore-backups",
            },
            "options": {
                "mirror": True,
                "archive": True,
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
                "size_check_enabled": True,
                "size_warning_threshold_mb": 10,
                "size_alert_threshold_mb": 100,
                "size_critical_threshold_mb": 1024,
            },
        }
        assert settings["paths"]["mirror_dir"] == "~/backups/mirror"
        assert settings["options"]["mirror"] is True


class TestPathsDict:
    """Tests for PathsDict TypedDict."""

    @pytest.mark.unit
    def test_paths_dict_structure(self) -> None:
        """PathsDict contains all required directory paths."""
        paths: PathsDict = {
            "mirror_dir": "~/backups/mirror",
            "archive_dir": "~/backups/archives",
            "restore_backup_dir": "~/.local/share/dfbu/restore-backups",
        }
        assert paths["mirror_dir"] == "~/backups/mirror"
        assert paths["archive_dir"] == "~/backups/archives"
        assert paths["restore_backup_dir"] == "~/.local/share/dfbu/restore-backups"


class TestOptionsDict:
    """Tests for OptionsDict TypedDict."""

    @pytest.mark.unit
    def test_options_dict_structure(self) -> None:
        """OptionsDict contains all backup options."""
        options: OptionsDict = {
            "mirror": True,
            "archive": True,
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
            "size_check_enabled": True,
            "size_warning_threshold_mb": 10,
            "size_alert_threshold_mb": 100,
            "size_critical_threshold_mb": 1024,
        }
        assert options["mirror"] is True
        assert options["archive_format"] == "tar.gz"
        assert options["archive_compression_level"] == 5


class TestSessionDict:
    """Tests for SessionDict TypedDict."""

    @pytest.mark.unit
    def test_session_dict_structure(self) -> None:
        """SessionDict contains excluded applications list."""
        session: SessionDict = {
            "excluded": ["Bash", "Vim", "Git"],
        }
        assert session["excluded"] == ["Bash", "Vim", "Git"]

    @pytest.mark.unit
    def test_session_dict_empty_excluded(self) -> None:
        """SessionDict accepts empty excluded list."""
        session: SessionDict = {
            "excluded": [],
        }
        assert session["excluded"] == []


class TestLegacyDotFileDict:
    """Tests for LegacyDotFileDict TypedDict (TOML migration)."""

    @pytest.mark.unit
    def test_legacy_dotfile_dict_structure(self) -> None:
        """LegacyDotFileDict contains all TOML dotfile fields."""
        legacy: LegacyDotFileDict = {
            "category": "Shell",
            "application": "Bash",
            "description": "Bash shell configuration",
            "paths": ["~/.bashrc", "~/.bash_profile"],
            "mirror_dir": "~/backups/mirror",
            "archive_dir": "~/backups/archives",
            "enabled": True,
        }
        assert legacy["category"] == "Shell"
        assert legacy["application"] == "Bash"
        assert legacy["description"] == "Bash shell configuration"
        assert legacy["paths"] == ["~/.bashrc", "~/.bash_profile"]
        assert legacy["enabled"] is True


class TestProfileDict:
    """Tests for ProfileDict TypedDict (v1.1.0)."""

    @pytest.mark.unit
    def test_profile_dict_has_required_fields(self) -> None:
        """ProfileDict should have all required fields."""
        profile: ProfileDict = {
            "name": "Work Profile",
            "description": "Work-related dotfiles",
            "excluded": ["Steam", "Firefox"],
            "options_overrides": {"archive": True},
            "created_at": "2026-02-05T10:00:00Z",
            "modified_at": "2026-02-05T10:00:00Z",
        }
        assert profile["name"] == "Work Profile"
        assert profile["excluded"] == ["Steam", "Firefox"]


class TestPreviewItemDict:
    """Tests for PreviewItemDict TypedDict (v1.1.0)."""

    @pytest.mark.unit
    def test_preview_item_dict_structure(self) -> None:
        """PreviewItemDict should have all required fields."""
        item: PreviewItemDict = {
            "path": "/home/user/.bashrc",
            "dest_path": "/backups/mirror/.bashrc",
            "size_bytes": 1024,
            "status": "new",
            "application": "Bash",
        }
        assert item["status"] == "new"


class TestBackupPreviewDict:
    """Tests for BackupPreviewDict TypedDict (v1.1.0)."""

    @pytest.mark.unit
    def test_backup_preview_dict_structure(self) -> None:
        """BackupPreviewDict should have all required fields."""
        preview: BackupPreviewDict = {
            "items": [],
            "total_size_bytes": 0,
            "new_count": 0,
            "changed_count": 0,
            "unchanged_count": 0,
            "error_count": 0,
        }
        assert preview["total_size_bytes"] == 0


class TestBackupHistoryEntry:
    """Tests for BackupHistoryEntry TypedDict (v1.1.0)."""

    @pytest.mark.unit
    def test_backup_history_entry_structure(self) -> None:
        """BackupHistoryEntry should have all required fields."""
        from core.common_types import BackupHistoryEntry

        entry: BackupHistoryEntry = {
            "timestamp": "2026-02-05T10:00:00Z",
            "profile": "Default",
            "items_backed": 42,
            "size_bytes": 1048576,
            "duration_seconds": 5.5,
            "success": True,
            "backup_type": "mirror",
        }
        assert entry["success"] is True
        assert entry["backup_type"] == "mirror"


class TestDashboardMetrics:
    """Tests for DashboardMetrics TypedDict (v1.1.0)."""

    @pytest.mark.unit
    def test_dashboard_metrics_structure(self) -> None:
        """DashboardMetrics should have all required fields."""
        from core.common_types import DashboardMetrics

        metrics: DashboardMetrics = {
            "total_backups": 100,
            "successful_backups": 95,
            "failed_backups": 5,
            "success_rate": 0.95,
            "total_size_backed_bytes": 10737418240,
            "average_duration_seconds": 4.2,
            "last_backup_timestamp": "2026-02-05T10:00:00Z",
        }
        assert metrics["success_rate"] == 0.95
        assert metrics["total_backups"] == 100
