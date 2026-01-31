#!/usr/bin/env python3
"""
Tests for RestoreBackupManager - Pre-Restore Safety Component

Description:
    Test suite for RestoreBackupManager validating pre-restore backups,
    manifest creation, and retention policy.

Author: Chris Purcell
"""

import sys
from pathlib import Path
from typing import Protocol, runtime_checkable

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))

from protocols import RestoreBackupManagerProtocol


class TestRestoreBackupManagerProtocol:
    """Test RestoreBackupManagerProtocol interface definition."""

    def test_protocol_exists(self) -> None:
        """Test that RestoreBackupManagerProtocol is defined."""
        # Assert
        assert hasattr(RestoreBackupManagerProtocol, "backup_before_restore")
        assert hasattr(RestoreBackupManagerProtocol, "get_backup_count")
        assert hasattr(RestoreBackupManagerProtocol, "cleanup_old_backups")
