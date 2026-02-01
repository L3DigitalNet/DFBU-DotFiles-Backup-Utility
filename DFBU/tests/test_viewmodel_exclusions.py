"""
Tests for ViewModel Exclusion-Based Selection
==============================================

Description:
    Unit tests for the ViewModel's exclusion management methods that delegate
    to ConfigManager. Tests verify proper signal emission and correct delegation.

Author: Chris Purcell
Date Created: 2026-02-01
License: MIT

Test Coverage:
    - command_toggle_exclusion: Toggle exclusion and emit signal
    - get_exclusions: Get current exclusion list from ConfigManager
    - is_excluded: Check if specific dotfile is excluded
"""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock

import pytest
from PySide6.QtWidgets import QApplication


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config_manager(mocker: Any) -> Mock:
    """
    Create mock ConfigManager with exclusion methods.

    Args:
        mocker: pytest-mock fixture

    Returns:
        Mock: Configured mock ConfigManager
    """
    mock_cm = mocker.Mock()
    mock_cm.toggle_exclusion = mocker.Mock()
    mock_cm.get_exclusions = mocker.Mock(return_value=["Bash", "Vim"])
    mock_cm.is_excluded = mocker.Mock(return_value=True)
    return mock_cm


@pytest.fixture
def mock_model(mocker: Any, mock_config_manager: Mock) -> Mock:
    """
    Create mock DFBUModel that returns the mock ConfigManager.

    Args:
        mocker: pytest-mock fixture
        mock_config_manager: Mock ConfigManager fixture

    Returns:
        Mock: Configured mock DFBUModel
    """
    mock_m = mocker.Mock()
    mock_m.get_config_manager.return_value = mock_config_manager
    return mock_m


@pytest.fixture
def viewmodel(qapp: QApplication, mock_model: Mock) -> Any:
    """
    Create ViewModel instance with mocked model.

    Args:
        qapp: Qt application fixture
        mock_model: Mock DFBUModel fixture

    Returns:
        DFBUViewModel: ViewModel instance for testing
    """
    from gui.viewmodel import DFBUViewModel

    return DFBUViewModel(mock_model)


# =============================================================================
# Tests for command_toggle_exclusion
# =============================================================================


@pytest.mark.unit
class TestCommandToggleExclusion:
    """Tests for command_toggle_exclusion method."""

    def test_toggle_exclusion_calls_config_manager(
        self, viewmodel: Any, mock_config_manager: Mock
    ) -> None:
        """Toggle exclusion should delegate to ConfigManager."""
        # Act
        viewmodel.command_toggle_exclusion("Bash")

        # Assert
        mock_config_manager.toggle_exclusion.assert_called_once_with("Bash")

    def test_toggle_exclusion_emits_signal(
        self, viewmodel: Any, qtbot: Any
    ) -> None:
        """Toggle exclusion should emit exclusions_changed signal."""
        # Arrange
        with qtbot.waitSignal(viewmodel.exclusions_changed, timeout=1000):
            # Act
            viewmodel.command_toggle_exclusion("Vim")

    def test_toggle_exclusion_with_different_applications(
        self, viewmodel: Any, mock_config_manager: Mock
    ) -> None:
        """Toggle exclusion should work with various application names."""
        # Act
        viewmodel.command_toggle_exclusion("Konsole")
        viewmodel.command_toggle_exclusion("Alacritty")

        # Assert
        assert mock_config_manager.toggle_exclusion.call_count == 2
        mock_config_manager.toggle_exclusion.assert_any_call("Konsole")
        mock_config_manager.toggle_exclusion.assert_any_call("Alacritty")


# =============================================================================
# Tests for get_exclusions
# =============================================================================


@pytest.mark.unit
class TestGetExclusions:
    """Tests for get_exclusions method."""

    def test_get_exclusions_returns_list(self, viewmodel: Any) -> None:
        """get_exclusions should return list from ConfigManager."""
        # Act
        result = viewmodel.get_exclusions()

        # Assert
        assert result == ["Bash", "Vim"]

    def test_get_exclusions_delegates_to_config_manager(
        self, viewmodel: Any, mock_config_manager: Mock
    ) -> None:
        """get_exclusions should call ConfigManager's get_exclusions."""
        # Act
        viewmodel.get_exclusions()

        # Assert
        mock_config_manager.get_exclusions.assert_called_once()

    def test_get_exclusions_returns_empty_list_when_none(
        self, viewmodel: Any, mock_config_manager: Mock
    ) -> None:
        """get_exclusions should return empty list when no exclusions."""
        # Arrange
        mock_config_manager.get_exclusions.return_value = []

        # Act
        result = viewmodel.get_exclusions()

        # Assert
        assert result == []


# =============================================================================
# Tests for is_excluded
# =============================================================================


@pytest.mark.unit
class TestIsExcluded:
    """Tests for is_excluded method."""

    def test_is_excluded_returns_true_when_excluded(
        self, viewmodel: Any, mock_config_manager: Mock
    ) -> None:
        """is_excluded should return True for excluded application."""
        # Arrange
        mock_config_manager.is_excluded.return_value = True

        # Act
        result = viewmodel.is_excluded("Bash")

        # Assert
        assert result is True
        mock_config_manager.is_excluded.assert_called_once_with("Bash")

    def test_is_excluded_returns_false_when_not_excluded(
        self, viewmodel: Any, mock_config_manager: Mock
    ) -> None:
        """is_excluded should return False for non-excluded application."""
        # Arrange
        mock_config_manager.is_excluded.return_value = False

        # Act
        result = viewmodel.is_excluded("Konsole")

        # Assert
        assert result is False
        mock_config_manager.is_excluded.assert_called_once_with("Konsole")

    def test_is_excluded_delegates_to_config_manager(
        self, viewmodel: Any, mock_config_manager: Mock
    ) -> None:
        """is_excluded should delegate to ConfigManager's is_excluded."""
        # Act
        viewmodel.is_excluded("Alacritty")

        # Assert
        mock_config_manager.is_excluded.assert_called_once_with("Alacritty")
