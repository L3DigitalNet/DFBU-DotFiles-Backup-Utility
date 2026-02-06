"""Tests for theme_loader module."""

from unittest.mock import MagicMock

import pytest

from gui.theme_loader import get_available_themes, get_current_theme, load_theme


class TestGetCurrentTheme:
    """Tests for get_current_theme()."""

    @pytest.mark.unit
    def test_default_theme_is_dfbu_light(self) -> None:
        """Default theme before any load should be dfbu_light."""
        assert get_current_theme() == "dfbu_light"


class TestLoadTheme:
    """Tests for load_theme()."""

    @pytest.mark.unit
    def test_load_existing_theme_returns_true(self) -> None:
        """Loading an existing QSS file should return True."""
        mock_app = MagicMock()
        result = load_theme(mock_app, "dfbu_light")
        assert result is True

    @pytest.mark.unit
    def test_load_nonexistent_theme_returns_false(self) -> None:
        """Loading a nonexistent theme should return False."""
        mock_app = MagicMock()
        result = load_theme(mock_app, "nonexistent_theme")
        assert result is False

    @pytest.mark.unit
    def test_load_theme_calls_set_stylesheet(self) -> None:
        """load_theme should call app.setStyleSheet with QSS content."""
        mock_app = MagicMock()
        load_theme(mock_app, "dfbu_light")
        mock_app.setStyleSheet.assert_called_once()
        qss_content = mock_app.setStyleSheet.call_args[0][0]
        assert "QMainWindow" in qss_content

    @pytest.mark.unit
    def test_load_updates_current_theme(self) -> None:
        """After loading, get_current_theme should reflect the new theme."""
        mock_app = MagicMock()
        load_theme(mock_app, "dfbu_light")
        assert get_current_theme() == "dfbu_light"


class TestGetAvailableThemes:
    """Tests for get_available_themes()."""

    @pytest.mark.unit
    def test_returns_list_containing_dfbu_light(self) -> None:
        """Available themes should include dfbu_light."""
        themes = get_available_themes()
        assert "dfbu_light" in themes

    @pytest.mark.unit
    def test_returns_list_of_strings(self) -> None:
        """Available themes should be a list of strings."""
        themes = get_available_themes()
        assert isinstance(themes, list)
        assert all(isinstance(t, str) for t in themes)

    @pytest.mark.unit
    def test_returns_list_containing_dfbu_dark(self) -> None:
        """Available themes should include dfbu_dark."""
        themes = get_available_themes()
        assert "dfbu_dark" in themes


class TestDarkThemeLoads:
    """Tests for dfbu_dark.qss loading."""

    @pytest.mark.unit
    def test_load_dark_theme_returns_true(self) -> None:
        """Loading dark theme should succeed."""
        mock_app = MagicMock()
        result = load_theme(mock_app, "dfbu_dark")
        assert result is True

    @pytest.mark.unit
    def test_dark_theme_has_dark_background(self) -> None:
        """Dark theme QSS should use dark background colors."""
        mock_app = MagicMock()
        load_theme(mock_app, "dfbu_dark")
        qss_content = mock_app.setStyleSheet.call_args[0][0]
        # Dark theme uses NEUTRAL_900 (#0F172A) as base background
        assert "#0F172A" in qss_content
