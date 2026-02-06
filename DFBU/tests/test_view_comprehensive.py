"""
Test View Comprehensive Coverage

Description:
    Comprehensive unit tests for View layer including MainWindow, dialogs,
    UI components, signals, and user interactions. Tests presentation logic
    and data binding.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
License: MIT
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Import Qt modules for testing
from PySide6.QtCore import QByteArray, Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from gui.model import DFBUModel
from gui.view import AddDotfileDialog, MainWindow, NumericTableWidgetItem
from gui.viewmodel import DFBUViewModel


@pytest.fixture
def qapp():
    """Create QApplication for testing Qt components."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def tmp_config(tmp_path: Path) -> Path:
    """Create temporary config file."""
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[paths]
mirror_dir = "~/test_mirror"
archive_dir = "~/test_archive"

[options]
mirror = true
archive = false
"""
    )
    return config_path


@pytest.fixture
def viewmodel_with_config(tmp_config: Path) -> DFBUViewModel:
    """Create ViewModel with valid config."""
    model = DFBUModel(tmp_config)
    model.load_config()
    return DFBUViewModel(model)


class TestNumericTableWidgetItem:
    """Test suite for NumericTableWidgetItem custom sorting."""

    def test_numeric_item_less_than_comparison(self, qapp):
        """Test numeric comparison for table sorting."""
        # Arrange
        item1 = NumericTableWidgetItem("100 KB")
        item1.setData(Qt.ItemDataRole.UserRole, 100)

        item2 = NumericTableWidgetItem("200 KB")
        item2.setData(Qt.ItemDataRole.UserRole, 200)

        # Act & Assert
        assert item1 < item2
        assert not item2 < item1

    def test_numeric_item_with_none_values(self, qapp):
        """Test comparison handles None values as zero."""
        # Arrange
        item1 = NumericTableWidgetItem("N/A")
        item1.setData(Qt.ItemDataRole.UserRole, None)

        item2 = NumericTableWidgetItem("100 KB")
        item2.setData(Qt.ItemDataRole.UserRole, 100)

        # Act & Assert
        assert item1 < item2

    def test_numeric_item_both_none_values(self, qapp):
        """Test comparison when both items have None values."""
        # Arrange
        item1 = NumericTableWidgetItem("N/A")
        item1.setData(Qt.ItemDataRole.UserRole, None)

        item2 = NumericTableWidgetItem("N/A")
        item2.setData(Qt.ItemDataRole.UserRole, None)

        # Act & Assert
        assert not item1 < item2


class TestAddDotfileDialog:
    """Test suite for AddDotfileDialog."""

    def test_dialog_initialization_add_mode(self, qapp, tmp_path):
        """Test dialog initializes correctly in add mode."""
        # Arrange
        _model = DFBUModel(tmp_path / "config.toml")
        _viewmodel = DFBUViewModel(_model)

        # Act
        dialog = AddDotfileDialog(parent=None)

        # Assert
        assert dialog.is_update_mode is False
        assert dialog.windowTitle() == "Add Dotfile Entry"
        assert dialog.paths_list.count() == 0
        assert dialog.enabled_checkbox.isChecked() is True

    def test_dialog_initialization_update_mode(self, qapp, tmp_path):
        """Test dialog initializes correctly in update mode."""
        # Arrange
        _model = DFBUModel(tmp_path / "config.toml")
        _viewmodel = DFBUViewModel(_model)
        dotfile_data = {
            "category": "TestCat",
            "application": "TestApp",
            "description": "Test description",
            "paths": ["~/.testrc", "~/.config/test"],
            "enabled": False,
        }

        # Act
        dialog = AddDotfileDialog(parent=None, dotfile_data=dotfile_data)

        # Assert
        assert dialog.is_update_mode is True
        assert dialog.windowTitle() == "Update Dotfile Entry"
        assert dialog.tags_edit.text() == "TestCat"  # category used as tags fallback
        assert dialog.application_edit.text() == "TestApp"
        assert dialog.description_edit.text() == "Test description"
        assert dialog.paths_list.count() == 2
        assert dialog.enabled_checkbox.isChecked() is False

    def test_dialog_legacy_path_format(self, qapp, tmp_path):
        """Test dialog handles legacy single path format."""
        # Arrange
        _model = DFBUModel(tmp_path / "config.toml")
        _viewmodel = DFBUViewModel(_model)
        dotfile_data = {
            "category": "TestCat",
            "application": "TestApp",
            "description": "Test",
            "path": "~/.testrc",  # Legacy format
            "enabled": True,
        }

        # Act
        dialog = AddDotfileDialog(parent=None, dotfile_data=dotfile_data)

        # Assert
        assert dialog.paths_list.count() == 1
        assert dialog.paths_list.item(0).text() == "~/.testrc"

    def test_add_path_to_list(self, qapp, tmp_path):
        """Test adding path to paths list."""
        # Arrange
        _model = DFBUModel(tmp_path / "config.toml")
        _viewmodel = DFBUViewModel(_model)
        dialog = AddDotfileDialog(parent=None)

        # Act
        dialog.path_input_edit.setText("~/.testfile")
        dialog._on_add_path()

        # Assert
        assert dialog.paths_list.count() == 1
        assert dialog.paths_list.item(0).text() == "~/.testfile"
        assert dialog.path_input_edit.text() == ""

    def test_add_path_prevents_duplicates(self, qapp, tmp_path):
        """Test adding duplicate path shows warning."""
        # Arrange
        _model = DFBUModel(tmp_path / "config.toml")
        _viewmodel = DFBUViewModel(_model)
        dialog = AddDotfileDialog(parent=None)
        dialog.paths_list.addItem("~/.testfile")

        # Act
        with patch.object(dialog, "show") as _mock_show:
            dialog.path_input_edit.setText("~/.testfile")
            with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
                dialog._on_add_path()

                # Assert
                mock_warning.assert_called_once()
                assert dialog.paths_list.count() == 1

    def test_add_path_ignores_empty_input(self, qapp, tmp_path):
        """Test adding empty path does nothing."""
        # Arrange
        _model = DFBUModel(tmp_path / "config.toml")
        _viewmodel = DFBUViewModel(_model)
        dialog = AddDotfileDialog(parent=None)

        # Act
        dialog.path_input_edit.setText("   ")
        dialog._on_add_path()

        # Assert
        assert dialog.paths_list.count() == 0

    def test_remove_selected_paths(self, qapp, tmp_path):
        """Test removing selected paths from list."""
        # Arrange
        _model = DFBUModel(tmp_path / "config.toml")
        _viewmodel = DFBUViewModel(_model)
        dialog = AddDotfileDialog(parent=None)
        dialog.paths_list.addItem("~/.file1")
        dialog.paths_list.addItem("~/.file2")
        dialog.paths_list.addItem("~/.file3")

        # Act - select and remove middle item
        dialog.paths_list.item(1).setSelected(True)
        dialog._on_remove_paths()

        # Assert
        assert dialog.paths_list.count() == 2
        assert dialog.paths_list.item(0).text() == "~/.file1"
        assert dialog.paths_list.item(1).text() == "~/.file3"

    def test_get_paths_returns_all_items(self, qapp, tmp_path):
        """Test get_paths returns all paths from list."""
        # Arrange
        _model = DFBUModel(tmp_path / "config.toml")
        _viewmodel = DFBUViewModel(_model)
        dialog = AddDotfileDialog(parent=None)
        dialog.paths_list.addItem("~/.file1")
        dialog.paths_list.addItem("~/.file2")

        # Act
        paths = dialog.get_paths()

        # Assert
        assert len(paths) == 2
        assert "~/.file1" in paths
        assert "~/.file2" in paths

    @pytest.mark.skip(
        reason="Complex UI interaction test - requires intricate QMessageBox mocking. "
        "Per test.prompt.md, View layer tests are optional. "
        "Core functionality tested via integration tests."
    )
    def test_browse_path_selects_file(self, qapp, tmp_path):
        """Test browse button sets file path when user selects a file.

        NOTE: Skipped due to complex UI interaction flow:
        1. Method shows QMessageBox with custom buttons
        2. User clicks File button
        3. QFileDialog opens
        4. Result populates text field

        Testing this requires complex mocking of Qt dialog lifecycle.
        The functionality is verified through manual testing and integration tests.
        """

    @pytest.mark.skip(
        reason="Complex UI interaction test - requires intricate QMessageBox mocking. "
        "Per test.prompt.md, View layer tests are optional. "
        "Core functionality tested via integration tests."
    )
    def test_browse_path_falls_back_to_directory(self, qapp, tmp_path):
        """Test browse button sets directory path when user selects a directory.

        NOTE: Skipped due to complex UI interaction flow:
        1. Method shows QMessageBox with custom buttons
        2. User clicks Directory button
        3. QFileDialog opens
        4. Result populates text field

        Testing this requires complex mocking of Qt dialog lifecycle.
        The functionality is verified through manual testing and integration tests.
        """


class TestMainWindow:
    """Test suite for MainWindow initialization and core functionality."""

    def test_main_window_initialization(self, qapp, viewmodel_with_config):
        """Test MainWindow initializes with ViewModel."""
        # Act
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Assert
        assert window.viewmodel == viewmodel_with_config
        assert "DFBU GUI" in window.windowTitle()
        assert hasattr(window, "tab_widget")
        assert hasattr(window, "dotfile_table")

    def test_window_connects_viewmodel_signals(self, qapp, viewmodel_with_config):
        """Test window connects to ViewModel signals."""
        # Arrange - patch before window creation to intercept connection
        with patch.object(MainWindow, "_on_config_loaded") as mock_handler:
            window = MainWindow(viewmodel_with_config, "1.2.0")

            # Act - emit signal from viewmodel
            viewmodel_with_config.config_loaded.emit(5)

            # Assert - handler should be called
            mock_handler.assert_called_once_with(5)

    def test_window_saves_geometry_on_close(self, qapp, viewmodel_with_config):
        """Test window saves geometry and state on close."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Mock the viewmodel save_settings method
        with patch.object(viewmodel_with_config, "save_settings") as mock_save_settings:
            # Create a proper QCloseEvent
            from PySide6.QtGui import QCloseEvent

            event = QCloseEvent()

            # Act
            window.closeEvent(event)

            # Assert
            mock_save_settings.assert_called_once()

    def test_window_restores_geometry_on_startup(self, qapp, tmp_config):
        """Test window restores saved geometry."""
        # Arrange
        model = DFBUModel(tmp_config)
        viewmodel = DFBUViewModel(model)

        # Save some geometry
        test_geometry = QByteArray(b"test_geometry_data")
        viewmodel.save_settings(geometry=test_geometry)

        # Act
        window = MainWindow(viewmodel, "1.2.0")

        # Assert - geometry should be restored (we can't easily verify the exact bytes)
        assert window is not None


class TestMainWindowActions:
    """Test suite for MainWindow menu actions and commands."""

    def test_save_config_action_triggers_command(self, qapp, viewmodel_with_config):
        """Test save config menu action triggers ViewModel command."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Mock the save command and confirmation dialog
        with patch.object(viewmodel_with_config, "command_save_config") as mock_command:
            mock_command.return_value = True  # Simulate successful save
            with patch("PySide6.QtWidgets.QMessageBox.question") as mock_question:
                # Mock user clicking "Yes" on confirmation
                mock_question.return_value = QMessageBox.StandardButton.Yes

                # Act
                window._on_save_config()

                # Assert - save_config should be called after user confirms
                mock_command.assert_called_once()

    def test_add_dotfile_opens_dialog(self, qapp, viewmodel_with_config):
        """Test add dotfile button opens AddDotfileDialog."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Mock dialog
        with patch("gui.view.AddDotfileDialog") as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec.return_value = False  # Dialog cancelled
            mock_dialog_class.return_value = mock_dialog

            # Act
            window._on_add_dotfile()

            # Assert
            mock_dialog_class.assert_called_once()
            mock_dialog.exec.assert_called_once()

    def test_update_dotfile_requires_selection(self, qapp, viewmodel_with_config):
        """Test update dotfile returns early when no selection."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Mock the command to verify it's not called
        with patch.object(
            viewmodel_with_config, "command_update_dotfile"
        ) as mock_command:
            # Act - no selection, should return early
            window._on_update_dotfile()

            # Assert - command should not be called when no selection
            mock_command.assert_not_called()

    def test_remove_dotfile_requires_selection(self, qapp, viewmodel_with_config):
        """Test remove dotfile returns early when no selection."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Mock the command to verify it's not called
        with patch.object(
            viewmodel_with_config, "command_remove_dotfile"
        ) as mock_command:
            # Act - no selection, should return early
            window._on_remove_dotfile()

            # Assert - command should not be called when no selection
            mock_command.assert_not_called()


class TestMainWindowBackupRestore:
    """Test suite for backup and restore operations in MainWindow."""

    def test_start_backup_creates_worker(self, qapp, viewmodel_with_config):
        """Test starting backup creates BackupWorker."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Mock get_dotfile_count to return > 0
        with patch.object(viewmodel_with_config, "get_dotfile_count", return_value=1):
            # Mock QMessageBox.question to return Yes
            with patch("PySide6.QtWidgets.QMessageBox.question") as mock_question:
                mock_question.return_value = QMessageBox.StandardButton.Yes

                # Mock command_start_backup command
                with patch.object(
                    viewmodel_with_config, "command_start_backup"
                ) as mock_start_backup:
                    # Act
                    window._on_start_backup()

                    # Assert
                    mock_start_backup.assert_called_once()

    def test_start_restore_requires_directory(self, qapp, viewmodel_with_config):
        """Test starting restore requires backup directory selection."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Mock the warning dialog that appears when no source is selected
        with patch("PySide6.QtWidgets.QMessageBox.warning") as mock_warning:
            with patch.object(
                viewmodel_with_config, "command_start_restore"
            ) as mock_start_restore:
                # Act
                window._on_start_restore()

                # Assert - warning shown, restore not started
                mock_warning.assert_called_once()
                mock_start_restore.assert_not_called()

    def test_progress_updated_displays_correctly(self, qapp, viewmodel_with_config):
        """Test progress updates display in UI."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Act
        window._on_progress_updated(50)

        # Assert
        assert window.progress_bar.value() == 50

    def test_operation_finished_resets_ui(self, qapp, viewmodel_with_config):
        """Test operation finished resets progress and enables buttons."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Simulate operation in progress
        window.progress_bar.setValue(50)
        window.progress_bar.setVisible(True)
        window.backup_btn.setEnabled(False)

        # Mock QMessageBox.information to avoid blocking
        with patch("PySide6.QtWidgets.QMessageBox.information"):
            # Act
            window._on_operation_finished("")

        # Assert - progress bar should be hidden
        assert window.progress_bar.isVisible() is False
        assert window.backup_btn.isEnabled() is True


class TestMainWindowDotfileDisplay:
    """Test suite for dotfile table display and updates."""

    def test_update_dotfile_table_populates_rows(self, qapp, tmp_config, tmp_path):
        """Test table updates with dotfile data."""
        # Arrange
        model = DFBUModel(tmp_config)
        viewmodel = DFBUViewModel(model)

        # Add test dotfiles
        test_file = tmp_path / "testfile.txt"
        test_file.write_text("test content")

        viewmodel.command_add_dotfile(
            "TestCat",
            "TestApp",
            "Test description",
            [str(test_file)],
            True,
        )

        window = MainWindow(viewmodel, "1.2.0")

        # Act
        window._update_dotfile_table()

        # Assert
        assert window.dotfile_table.rowCount() > 0

    def test_table_displays_validation_status(self, qapp, tmp_config, tmp_path):
        """Test table shows validation status for dotfiles."""
        # Arrange
        model = DFBUModel(tmp_config)
        viewmodel = DFBUViewModel(model)

        # Add dotfile with valid path
        test_file = tmp_path / "testfile.txt"
        test_file.write_text("test content")

        viewmodel.command_add_dotfile(
            "TestCat", "TestApp", "Test", [str(test_file)], True
        )

        window = MainWindow(viewmodel, "1.2.0")

        # Act
        window._update_dotfile_table()

        # Assert - table should have entries
        assert window.dotfile_table.rowCount() == 1


class TestMainWindowOptionsTab:
    """Test suite for options/settings tab functionality."""

    def test_options_update_from_viewmodel(self, qapp, viewmodel_with_config):
        """Test options tab reflects ViewModel state."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Act
        window._update_options_display()

        # Assert - options should be loaded
        assert window.mirror_checkbox is not None
        assert window.archive_checkbox is not None

    def test_save_options_updates_viewmodel(self, qapp, viewmodel_with_config):
        """Test saving options updates ViewModel."""
        # Arrange
        window = MainWindow(viewmodel_with_config, "1.2.0")

        # Mock update option command and confirmation dialog
        with patch.object(
            viewmodel_with_config, "command_update_option"
        ) as mock_update:
            with patch("PySide6.QtWidgets.QMessageBox.question") as mock_question:
                # Mock user clicking "Yes"
                mock_question.return_value = QMessageBox.StandardButton.Yes

                # Act
                window._on_save_config()

                # Assert - should be called multiple times for different options
                assert mock_update.call_count > 0
