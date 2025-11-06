"""
DFBU View - UI Presentation Layer

Description:
    View layer for DFBU GUI implementing MVVM pattern. Focuses solely on
    UI presentation and user interaction, delegating all business logic to the
    ViewModel. Provides clean separation between presentation and logic.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 11-01-2025
License: MIT

Features:
    - MVVM View layer with pure UI presentation concerns
    - Signal-based data binding to ViewModel
    - Tab-based interface for Backup, Restore, and Configuration views
    - Real-time progress tracking and operation feedback
    - Dotfile list display with validation status indicators
    - Interactive dotfile management with add, update, and remove functionality
    - Window state persistence through ViewModel
    - Python standard library first approach with minimal dependencies
    - Clean architecture with confident design patterns

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - PySide6 framework for modern desktop GUI
    - viewmodel module for presentation logic

Classes:
    - AddDotfileDialog: Dialog for adding new dotfile entries
    - MainWindow: Main application window implementing the GUI interface

Functions:
    None
"""

from pathlib import Path
from typing import Any, Final

# Local imports
from core.common_types import DotFileDict
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QColor, QTextCursor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from gui.constants import MIN_DIALOG_HEIGHT, MIN_DIALOG_WIDTH, STATUS_MESSAGE_TIMEOUT_MS
from gui.input_validation import InputValidator
from gui.viewmodel import DFBUViewModel


# Constants for view configuration
SKIP_LOG_INTERVAL: Final[int] = 10  # Log every N skipped files to avoid log spam


class NumericTableWidgetItem(QTableWidgetItem):
    """
    Custom QTableWidgetItem for proper numeric sorting.

    Stores a numeric value in UserRole and uses it for comparisons,
    enabling correct sorting of formatted strings (like "1.5 KB").
    """

    def __lt__(self, other: QTableWidgetItem) -> bool:
        """
        Compare items by numeric value stored in UserRole.

        Args:
            other: Other table item to compare against

        Returns:
            True if this item's numeric value is less than other's
        """
        self_value = self.data(Qt.ItemDataRole.UserRole)
        other_value = other.data(Qt.ItemDataRole.UserRole)

        # Handle None values by treating them as 0
        self_numeric: int | float = (
            self_value if isinstance(self_value, (int, float)) else 0
        )
        other_numeric: int | float = (
            other_value if isinstance(other_value, (int, float)) else 0
        )

        return self_numeric < other_numeric


class AddDotfileDialog(QDialog):
    """
    Dialog for adding or updating dotfile entry with support for multiple paths.

    Attributes:
        category_combo: Editable combo box for category (prepopulated)
        application_edit: Line edit for application name
        description_edit: Line edit for description
        paths_list: List widget displaying all paths
        path_input_edit: Line edit for new path input
        enabled_checkbox: Checkbox for enabled status

    Public methods:
        exec: Show dialog and return result
        get_paths: Get list of paths from the list widget
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        dotfile_data: dict[str, Any] | None = None,
        categories: list[str] | None = None,
    ) -> None:
        """
        Initialize the AddDotfileDialog.

        Args:
            parent: Parent widget
            dotfile_data: Optional existing dotfile data for update mode
            categories: List of existing categories for dropdown
        """
        super().__init__(parent)
        self.is_update_mode = dotfile_data is not None
        self.setWindowTitle(
            "Update Dotfile Entry" if self.is_update_mode else "Add Dotfile Entry"
        )
        self.setMinimumWidth(MIN_DIALOG_WIDTH)
        self.setMinimumHeight(MIN_DIALOG_HEIGHT)

        # Create main layout
        main_layout = QVBoxLayout(self)

        # Add info label
        info_text = (
            "Update the dotfile entry:"
            if self.is_update_mode
            else "Add a new dotfile entry to the configuration:"
        )
        info_label = QLabel(info_text)
        main_layout.addWidget(info_label)

        # Create form layout for inputs
        form_layout = QFormLayout()

        # Category combo box (editable)
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.setPlaceholderText("e.g., Applications, Shell configs")
        if categories:
            self.category_combo.addItems(categories)
        form_layout.addRow("Category:", self.category_combo)

        # Application input
        self.application_edit = QLineEdit()
        self.application_edit.setPlaceholderText("e.g., Firefox, Bash")
        form_layout.addRow("Application:", self.application_edit)

        # Description input
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText(
            "Brief description of the configuration"
        )
        form_layout.addRow("Description:", self.description_edit)

        main_layout.addLayout(form_layout)

        # Paths section with QListWidget
        paths_label = QLabel("Paths (one or more):")
        main_layout.addWidget(paths_label)

        # List widget for paths
        self.paths_list = QListWidget()
        self.paths_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        main_layout.addWidget(self.paths_list)

        # Path input controls
        path_input_layout = QHBoxLayout()
        self.path_input_edit = QLineEdit()
        self.path_input_edit.setPlaceholderText("Enter or browse for path...")
        path_input_layout.addWidget(self.path_input_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse_path)
        path_input_layout.addWidget(browse_btn)

        add_path_btn = QPushButton("Add Path")
        add_path_btn.clicked.connect(self._on_add_path)
        path_input_layout.addWidget(add_path_btn)

        main_layout.addLayout(path_input_layout)

        # Remove path button
        remove_path_btn = QPushButton("Remove Selected Path(s)")
        remove_path_btn.clicked.connect(self._on_remove_paths)
        main_layout.addWidget(remove_path_btn)

        # Enabled checkbox
        self.enabled_checkbox = QCheckBox("Enable for backup")
        self.enabled_checkbox.setChecked(True)
        main_layout.addWidget(self.enabled_checkbox)

        # Pre-populate fields if in update mode
        if self.is_update_mode and dotfile_data:
            self.category_combo.setCurrentText(dotfile_data.get("category", ""))
            self.application_edit.setText(dotfile_data.get("application", ""))
            self.description_edit.setText(dotfile_data.get("description", ""))
            self.enabled_checkbox.setChecked(dotfile_data.get("enabled", True))

            # Handle both legacy "path" and new "paths" format
            if "paths" in dotfile_data:
                for path_str in dotfile_data["paths"]:
                    self.paths_list.addItem(path_str)
            elif "path" in dotfile_data:
                self.paths_list.addItem(dotfile_data["path"])

        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def _on_browse_path(self) -> None:
        """Handle browse button click to select file or directory."""
        # Create custom message box to ask user what type to select
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Select Type")
        msg_box.setText("What would you like to select?")
        msg_box.setIcon(QMessageBox.Icon.Question)

        # Add custom buttons with clear labels
        file_button = msg_box.addButton("File", QMessageBox.ButtonRole.YesRole)
        dir_button = msg_box.addButton("Directory", QMessageBox.ButtonRole.NoRole)
        _cancel_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

        msg_box.setDefaultButton(file_button)
        msg_box.exec()

        clicked_button = msg_box.clickedButton()

        if clicked_button == file_button:
            # Select a file
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select File",
                str(Path.home()),
                "All Files (*)",
            )

            if file_path:
                self.path_input_edit.setText(file_path)

        elif clicked_button == dir_button:
            # Select a directory
            dir_path = QFileDialog.getExistingDirectory(
                self, "Select Directory", str(Path.home())
            )

            if dir_path:
                self.path_input_edit.setText(dir_path)

    def _on_add_path(self) -> None:
        """Add path from input field to paths list."""
        path_text = self.path_input_edit.text().strip()

        if not path_text:
            return

        # Validate path before adding
        validation_result = InputValidator.validate_path(path_text, must_exist=False)
        if not validation_result.success:
            QMessageBox.warning(self, "Invalid Path", validation_result.error_message)
            return

        # Check for duplicates
        for i in range(self.paths_list.count()):
            if self.paths_list.item(i).text() == path_text:
                QMessageBox.warning(
                    self, "Duplicate Path", "This path is already in the list."
                )
                return

        # Add to list and clear input
        self.paths_list.addItem(path_text)
        self.path_input_edit.clear()

    def _on_remove_paths(self) -> None:
        """Remove selected paths from list."""
        selected_items = self.paths_list.selectedItems()

        for item in selected_items:
            self.paths_list.takeItem(self.paths_list.row(item))

    def accept(self) -> None:
        """
        Override accept to validate input before closing dialog.

        Validates all fields and shows error message if validation fails.
        """
        # Validate category
        category = self.category_combo.currentText().strip()
        validation_result = InputValidator.validate_string(
            category, field_name="Category", min_length=1, max_length=100
        )
        if not validation_result.success:
            QMessageBox.warning(
                self, "Validation Error", validation_result.error_message
            )
            self.category_combo.setFocus()
            return

        # Validate application
        application = self.application_edit.text().strip()
        validation_result = InputValidator.validate_string(
            application, field_name="Application", min_length=1, max_length=100
        )
        if not validation_result.success:
            QMessageBox.warning(
                self, "Validation Error", validation_result.error_message
            )
            self.application_edit.setFocus()
            return

        # Validate description
        description = self.description_edit.text().strip()
        validation_result = InputValidator.validate_string(
            description,
            field_name="Description",
            allow_empty=True,
            max_length=255,
        )
        if not validation_result.success:
            QMessageBox.warning(
                self, "Validation Error", validation_result.error_message
            )
            self.description_edit.setFocus()
            return

        # Validate paths
        paths = self.get_paths()
        if not paths:
            QMessageBox.warning(
                self,
                "Validation Error",
                "At least one path is required.",
            )
            self.path_input_edit.setFocus()
            return

        # Validate each path
        for path_str in paths:
            validation_result = InputValidator.validate_path(path_str, must_exist=False)
            if not validation_result.success:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    f"Invalid path '{path_str}': {validation_result.error_message}",
                )
                return

        # All validation passed, call parent accept
        super().accept()

    def get_paths(self) -> list[str]:
        """
        Get list of paths from the list widget.

        Returns:
            List of path strings
        """
        paths: list[str] = []
        for i in range(self.paths_list.count()):
            path_text = self.paths_list.item(i).text().strip()
            if path_text:
                paths.append(path_text)
        return paths


class MainWindow(QMainWindow):
    """
    Main application window implementing the GUI interface.

    Attributes:
        viewmodel: DFBUViewModel for presentation logic
        central_widget: Main central widget
        tab_widget: Tab widget for different views
        dotfile_table: Table widget for dotfile display
        add_dotfile_btn: Button to add new dotfile entry
        update_dotfile_btn: Button to update selected dotfile entry
        remove_dotfile_btn: Button to remove selected dotfile entry
        save_dotfiles_btn: Button to save dotfile configuration changes
        config_path_edit: Line edit for configuration file path
        load_config_btn: Button to load configuration
        backup_btn: Button to start backup
        mirror_checkbox: Checkbox for mirror backup mode
        archive_checkbox: Checkbox for archive backup mode
        force_full_backup_checkbox: Checkbox to force copying all files
        restore_source_edit: Line edit for restore source directory
        browse_restore_btn: Button to browse for restore source
        restore_btn: Button to start restore operation
        options_text: Text edit for options display
        config_mirror_checkbox: Checkbox for mirror backup mode
        config_archive_checkbox: Checkbox for archive backup mode
        config_hostname_checkbox: Checkbox for hostname subdirectory
        config_date_checkbox: Checkbox for date subdirectory
        config_compression_spinbox: SpinBox for compression level
        config_rotate_checkbox: Checkbox for archive rotation
        config_max_archives_spinbox: SpinBox for max archives
        config_mirror_path_edit: Line edit for mirror directory path
        config_archive_path_edit: Line edit for archive directory path
        save_config_btn: Button to save configuration changes
        progress_label: Label for progress text
        progress_bar: Progress bar widget
        operation_log: Text edit for operation log
        status_bar: Status bar widget

    Public methods:
        setup_ui: Initialize the user interface
        setup_menu_bar: Create the application menu bar
        setup_backup_tab: Create the backup operations tab
        setup_restore_tab: Create the restore operations tab
        setup_config_tab: Create the configuration display tab
        closeEvent: Handle application close event

    Private methods:
        _on_add_dotfile: Handle add dotfile button click
        _on_update_dotfile: Handle update dotfile button click
        _on_remove_dotfile: Handle remove dotfile button click
        _on_save_dotfile_config: Handle save dotfile configuration button click
        _on_dotfile_selection_changed: Handle dotfile table selection change
        Various other private methods for UI setup and event handling
    """

    PROJECT_NAME: Final[str] = "DFBU GUI"

    def __init__(self, viewmodel: DFBUViewModel, version: str) -> None:
        """
        Initialize the MainWindow.

        Args:
            viewmodel: DFBUViewModel instance
            version: Application version string
        """
        super().__init__()
        self.viewmodel: DFBUViewModel = viewmodel
        self.version: str = version

        # Track skipped items for periodic log updates
        self._skipped_count: int = 0
        self._last_logged_skip_count: int = 0

        self.setup_ui()
        self._connect_viewmodel_signals()
        self._load_settings()

    def setup_ui(self) -> None:
        """Initialize the user interface by loading from .ui file."""
        # Load UI file (contains QMainWindow definition)
        ui_file_path = Path(__file__).parent / "designer" / "main_window_complete.ui"
        loader = QUiLoader()
        loaded_window = loader.load(str(ui_file_path), None)

        # Type safety: QUiLoader returns QWidget, but we know it's QMainWindow from .ui file
        # We check dynamically and cast appropriately to satisfy type checker
        ui_widget: QWidget | None = None

        # Extract components from loaded QMainWindow to avoid nesting
        # Qt doesn't allow QMainWindow within QMainWindow, so we extract and reparent
        if hasattr(loaded_window, "centralWidget") and callable(
            getattr(loaded_window, "centralWidget", None)
        ):
            central = loaded_window.centralWidget()
            if isinstance(central, QWidget):
                ui_widget = central
                ui_widget.setParent(self)
                self.setCentralWidget(ui_widget)

            # Extract and set menubar if present
            if hasattr(loaded_window, "menuBar") and callable(
                getattr(loaded_window, "menuBar", None)
            ):
                menu = loaded_window.menuBar()
                if menu is not None:
                    # Set menubar without reparenting to avoid object lifecycle issues
                    self.setMenuBar(menu)

            # Extract and set statusbar if present
            if hasattr(loaded_window, "statusBar") and callable(
                getattr(loaded_window, "statusBar", None)
            ):
                status = loaded_window.statusBar()
                if status is not None:
                    status.setParent(self)
                    self.setStatusBar(status)
        # Fallback for non-QMainWindow UI files
        elif isinstance(loaded_window, QWidget):
            ui_widget = loaded_window
            ui_widget.setParent(self)
            self.setCentralWidget(ui_widget)

        # Ensure we have a valid ui_widget
        if ui_widget is None:
            raise RuntimeError("Failed to load UI from .ui file")

        # Set window title with version
        self.setWindowTitle(f"{self.PROJECT_NAME} v{self.version}")

        # Get references to all UI widgets and menu actions
        self._setup_widget_references(ui_widget, loaded_window)

        # Connect signals to handler methods
        self._connect_ui_signals()

        # Configure table widget properties
        self._configure_table_widget()

        # Set initial status message
        self.status_bar.showMessage("Ready - Load configuration to begin")

    def _setup_widget_references(
        self, ui_widget: QWidget, loaded_window: QWidget
    ) -> None:
        """
        Get references to UI elements from the loaded widget.

        Args:
            ui_widget: Central widget containing all UI elements
            loaded_window: Original loaded QMainWindow for finding menu actions
        """
        # Store reference to central widget
        self.central_widget: QWidget = ui_widget
        found_tab = ui_widget.findChild(QTabWidget, "tab_widget")
        if not isinstance(found_tab, QTabWidget):
            raise RuntimeError("Required widget 'tab_widget' not found in UI file")
        self.tab_widget: QTabWidget = found_tab

        # Backup tab widgets
        self.config_path_edit: QLineEdit = ui_widget.findChild(
            QLineEdit, "configGroupPathEdit"
        )  # type: ignore[assignment]
        self.load_config_btn: QPushButton = ui_widget.findChild(
            QPushButton, "configGroupLoadButton"
        )  # type: ignore[assignment]
        self.dotfile_table: QTableWidget = ui_widget.findChild(
            QTableWidget, "fileGroupFileTable"
        )  # type: ignore[assignment]
        self.total_size_label: QLabel = ui_widget.findChild(
            QLabel, "fileGroupTotalSizeLabel"
        )  # type: ignore[assignment]
        self.add_dotfile_btn: QPushButton = ui_widget.findChild(
            QPushButton, "fileGroupAddFileButton"
        )  # type: ignore[assignment]
        self.update_dotfile_btn: QPushButton = ui_widget.findChild(
            QPushButton, "fileGroupUpdateFileButton"
        )  # type: ignore[assignment]
        self.remove_dotfile_btn: QPushButton = ui_widget.findChild(
            QPushButton, "fileGroupRemoveFileButton"
        )  # type: ignore[assignment]
        self.toggle_enabled_btn: QPushButton = ui_widget.findChild(
            QPushButton, "fileGroupToggleEnabledButton"
        )  # type: ignore[assignment]
        self.save_dotfiles_btn: QPushButton = ui_widget.findChild(
            QPushButton, "fileGroupSaveFilesButton"
        )  # type: ignore[assignment]
        self.mirror_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "mirrorCheckbox"
        )  # type: ignore[assignment]
        self.archive_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "archiveCheckbox"
        )  # type: ignore[assignment]
        self.force_full_backup_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "forceBackupCheckbox"
        )  # type: ignore[assignment]
        self.backup_btn: QPushButton = ui_widget.findChild(
            QPushButton, "startBackupButton"
        )  # type: ignore[assignment]
        self.operation_log: QTextEdit = ui_widget.findChild(QTextEdit, "logBox")  # type: ignore[assignment]

        # Validate critical widgets were found
        if not self.operation_log:
            raise RuntimeError("logBox widget not found in UI file!")

        # Restore tab widgets
        self.restore_source_edit: QLineEdit = ui_widget.findChild(
            QLineEdit, "restoreSourceEdit"
        )  # type: ignore[assignment]
        self.browse_restore_btn: QPushButton = ui_widget.findChild(
            QPushButton, "restoreSourceBrowseButton"
        )  # type: ignore[assignment]
        self.restore_btn: QPushButton = ui_widget.findChild(
            QPushButton, "restoreSourceButton"
        )  # type: ignore[assignment]
        # Note: Restore operation log uses the same logBox widget in the Logs tab
        self.restore_operation_log: QTextEdit = self.operation_log

        # Configuration tab widgets
        self.config_mirror_path_edit: QLineEdit = ui_widget.findChild(
            QLineEdit, "config_mirror_path_edit"
        )  # type: ignore[assignment]
        self.config_archive_path_edit: QLineEdit = ui_widget.findChild(
            QLineEdit, "configArchivePathEdit"
        )  # type: ignore[assignment]
        self.config_mirror_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_mirror_checkbox"
        )  # type: ignore[assignment]
        self.config_archive_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_archive_checkbox"
        )  # type: ignore[assignment]
        self.config_hostname_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_hostname_checkbox"
        )  # type: ignore[assignment]
        self.config_date_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_date_checkbox"
        )  # type: ignore[assignment]
        self.config_compression_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_compression_spinbox"
        )  # type: ignore[assignment]
        self.config_rotate_checkbox: QCheckBox = ui_widget.findChild(
            QCheckBox, "config_rotate_checkbox"
        )  # type: ignore[assignment]
        self.config_max_archives_spinbox: QSpinBox = ui_widget.findChild(
            QSpinBox, "config_max_archives_spinbox"
        )  # type: ignore[assignment]
        self.save_config_btn: QPushButton = ui_widget.findChild(
            QPushButton, "saveConfigButton"
        )  # type: ignore[assignment]

        # Logs tab widgets
        self.save_log_btn: QPushButton = ui_widget.findChild(QPushButton, "pushButton")  # type: ignore[assignment]

        # Status bar and progress bar
        self.status_bar = self.statusBar()
        self.progress_bar: QProgressBar = self.status_bar.findChild(
            QProgressBar, "progress_bar"
        )  # type: ignore[assignment]

        # Menu actions from menubar (accessed from loaded_window before it goes out of scope)
        self.action_load_config: QAction = loaded_window.findChild(
            QAction, "actionLoadConfig"
        )  # type: ignore[assignment]
        self.action_exit: QAction = loaded_window.findChild(QAction, "actionExit")  # type: ignore[assignment]
        self.action_start_backup: QAction = loaded_window.findChild(
            QAction, "actionStartBackup"
        )  # type: ignore[assignment]
        self.action_start_restore: QAction = loaded_window.findChild(
            QAction, "actionStartRestore"
        )  # type: ignore[assignment]
        self.action_about: QAction = loaded_window.findChild(QAction, "actionAbout")  # type: ignore[assignment]

        # Fix Qt object ownership: Reparent actions to prevent deletion
        for action in [
            self.action_load_config,
            self.action_exit,
            self.action_start_backup,
            self.action_start_restore,
            self.action_about,
        ]:
            if action:
                action.setParent(self)

    def _connect_ui_signals(self) -> None:
        """Connect UI element signals to handler methods."""
        # Backup tab connections
        browse_config_btn: QPushButton = self.central_widget.findChild(
            QPushButton, "configGroupBrowseButton"
        )  # type: ignore[assignment]
        browse_config_btn.clicked.connect(self._on_browse_config)
        self.load_config_btn.clicked.connect(self._on_load_config)
        self.add_dotfile_btn.clicked.connect(self._on_add_dotfile)
        self.update_dotfile_btn.clicked.connect(self._on_update_dotfile)
        self.remove_dotfile_btn.clicked.connect(self._on_remove_dotfile)
        self.toggle_enabled_btn.clicked.connect(self._on_toggle_dotfile_enabled)
        self.save_dotfiles_btn.clicked.connect(self._on_save_dotfile_config)
        self.mirror_checkbox.stateChanged.connect(self._on_mirror_checkbox_changed)
        self.archive_checkbox.stateChanged.connect(self._on_archive_checkbox_changed)
        self.backup_btn.clicked.connect(self._on_start_backup)
        self.dotfile_table.itemSelectionChanged.connect(
            self._on_dotfile_selection_changed
        )

        # Restore tab connections
        self.browse_restore_btn.clicked.connect(self._on_browse_restore_source)
        self.restore_btn.clicked.connect(self._on_start_restore)

        # Configuration tab connections
        browse_mirror_btn: QPushButton = self.central_widget.findChild(
            QPushButton, "browse_mirror_btn"
        )  # type: ignore[assignment]
        browse_archive_btn: QPushButton = self.central_widget.findChild(
            QPushButton, "browseArchiveButton"
        )  # type: ignore[assignment]
        browse_mirror_btn.clicked.connect(self._on_browse_mirror_dir)
        browse_archive_btn.clicked.connect(self._on_browse_archive_dir)
        self.config_mirror_path_edit.textChanged.connect(self._on_config_changed)
        self.config_archive_path_edit.textChanged.connect(self._on_config_changed)
        self.config_mirror_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_archive_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_hostname_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_date_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_compression_spinbox.valueChanged.connect(self._on_config_changed)
        self.config_rotate_checkbox.stateChanged.connect(
            self._on_rotate_checkbox_changed
        )
        self.config_rotate_checkbox.stateChanged.connect(self._on_config_changed)
        self.config_max_archives_spinbox.valueChanged.connect(self._on_config_changed)
        self.save_config_btn.clicked.connect(self._on_save_config)

        # Logs tab connections
        self.save_log_btn.clicked.connect(self._on_save_log)

        # Menu action connections
        self.action_load_config.triggered.connect(self._on_browse_config)
        self.action_exit.triggered.connect(self.close)
        self.action_start_backup.triggered.connect(self._on_start_backup)
        self.action_start_restore.triggered.connect(self._on_start_restore)
        self.action_about.triggered.connect(self._show_about)

    def _configure_table_widget(self) -> None:
        """Configure the dotfile table widget properties."""
        # Set column resize modes
        header = self.dotfile_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

    def _connect_viewmodel_signals(self) -> None:
        """Connect ViewModel signals to View slots."""
        self.viewmodel.progress_updated.connect(self._on_progress_updated)
        self.viewmodel.item_processed.connect(self._on_item_processed)
        self.viewmodel.item_skipped.connect(self._on_item_skipped)
        self.viewmodel.operation_finished.connect(self._on_operation_finished)
        self.viewmodel.error_occurred.connect(self._on_error_occurred)
        self.viewmodel.config_loaded.connect(self._on_config_loaded)
        self.viewmodel.dotfiles_updated.connect(self._on_dotfiles_updated)

    def _load_settings(self) -> None:
        """Load persisted settings."""
        settings = self.viewmodel.load_settings()

        # Restore window geometry
        if settings.get("geometry"):
            self.restoreGeometry(settings["geometry"])
        if settings.get("window_state"):
            self.restoreState(settings["window_state"])

        # Display config path if loaded
        if settings.get("config_path"):
            self.config_path_edit.setText(settings["config_path"])

        # Display restore source if loaded
        if settings.get("restore_source"):
            self.restore_source_edit.setText(settings["restore_source"])
            self.restore_btn.setEnabled(True)

    def _on_browse_config(self) -> None:
        """Handle browse config button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Configuration File",
            str(Path.home()),
            "TOML Files (*.toml);;All Files (*)",
        )

        if file_path:
            self.config_path_edit.setText(file_path)
            self.viewmodel.model.config_path = Path(file_path)

    def _on_load_config(self) -> None:
        """Handle load configuration button click."""
        if not self.config_path_edit.text():
            QMessageBox.warning(
                self, "No Configuration", "Please select a configuration file first."
            )
            return

        success = self.viewmodel.command_load_config()

        if not success:
            QMessageBox.critical(
                self,
                "Configuration Error",
                "Failed to load configuration file. Please check the file path and format.",
            )

    def _on_start_backup(self) -> None:
        """Handle start backup button click."""
        if self.viewmodel.get_dotfile_count() == 0:
            QMessageBox.warning(
                self, "No Configuration", "Please load a configuration file first."
            )
            return

        # Confirm backup operation
        reply = QMessageBox.question(
            self,
            "Confirm Backup",
            "Start backup operation with current configuration?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Reset skip tracking for new operation
            self._skipped_count = 0
            self._last_logged_skip_count = 0

            # Clear operation log
            self.operation_log.clear()
            self.operation_log.append("=== Backup Operation Started ===\n")

            # Switch to Logs tab (index 3)
            self.tab_widget.setCurrentIndex(3)

            # Disable buttons during operation
            self.backup_btn.setEnabled(False)
            self.load_config_btn.setEnabled(False)

            # Show progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            # Get force full backup setting from checkbox
            force_full = self.force_full_backup_checkbox.isChecked()

            # Add info to log about backup mode
            if force_full:
                self.operation_log.append(
                    "INFO: Force Full Backup - All files will be copied\n"
                )
            else:
                self.operation_log.append(
                    "INFO: Smart Backup - Only changed files will be copied\n"
                )

            # Start backup with force full setting
            success = self.viewmodel.command_start_backup(force_full_backup=force_full)

            if not success:
                # Re-enable buttons if backup failed to start
                self.backup_btn.setEnabled(True)
                self.load_config_btn.setEnabled(True)
                self.progress_bar.setVisible(False)
                self.operation_log.append("✗ Failed to start backup operation\n")

    def _on_browse_restore_source(self) -> None:
        """Handle browse restore source button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Restore Source Directory", str(Path.home())
        )

        if directory:
            self.restore_source_edit.setText(directory)

            # Validate and set source
            if self.viewmodel.command_set_restore_source(Path(directory)):
                self.restore_btn.setEnabled(True)
            else:
                QMessageBox.warning(
                    self, "Invalid Directory", "Selected path is not a valid directory."
                )
                self.restore_btn.setEnabled(False)

    def _on_start_restore(self) -> None:
        """Handle start restore button click."""
        if not self.restore_source_edit.text():
            QMessageBox.warning(
                self, "No Source", "Please select a restore source directory first."
            )
            return

        # Confirm restore operation
        reply = QMessageBox.warning(
            self,
            "Confirm Restore",
            "This operation will restore files to their original locations.\n"
            "Existing files will be overwritten.\n\n"
            "Are you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Clear operation log
            self.restore_operation_log.clear()

            # Switch to Logs tab (index 3)
            self.tab_widget.setCurrentIndex(3)

            # Disable buttons during operation
            self.restore_btn.setEnabled(False)
            self.browse_restore_btn.setEnabled(False)

            # Show progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            # Start restore
            self.viewmodel.command_start_restore()

    def _on_progress_updated(self, value: int) -> None:
        """Handle progress updates."""
        self.progress_bar.setValue(value)

    def _on_item_processed(self, source: str, destination: str) -> None:
        """Handle item processed signal."""
        log_message = f"✓ {Path(source).name} → {Path(destination).name}\n"

        # Determine which log to update based on which worker is active
        # Check viewmodel to see which operation is running
        if self.viewmodel.backup_worker and self.viewmodel.backup_worker.isRunning():
            # Backup operation - write to backup log
            self.operation_log.moveCursor(QTextCursor.MoveOperation.End)
            self.operation_log.insertPlainText(log_message)
            self.operation_log.ensureCursorVisible()
        elif (
            self.viewmodel.restore_worker and self.viewmodel.restore_worker.isRunning()
        ):
            # Restore operation - write to restore log
            self.restore_operation_log.moveCursor(QTextCursor.MoveOperation.End)
            self.restore_operation_log.insertPlainText(log_message)
            self.restore_operation_log.ensureCursorVisible()

    def _on_item_skipped(self, path: str, reason: str) -> None:
        """
        Handle item skipped signal.

        Shows periodic summary of skipped files to avoid overwhelming the log
        with potentially hundreds of individual "unchanged" messages.
        """
        self._skipped_count += 1

        # Show progress at intervals to indicate activity without overwhelming the log
        if self._skipped_count % SKIP_LOG_INTERVAL == 0:
            new_skips = self._skipped_count - self._last_logged_skip_count
            self._last_logged_skip_count = self._skipped_count

            log_message = f"⊘ Skipped {new_skips} unchanged files (total: {self._skipped_count})...\n"

            # Update backup operation log (skips only happen during backup)
            self.operation_log.moveCursor(QTextCursor.MoveOperation.End)
            self.operation_log.insertPlainText(log_message)
            self.operation_log.ensureCursorVisible()

    def _on_operation_finished(self, summary: str) -> None:
        """Handle operation finished signal."""
        # Hide progress bar
        self.progress_bar.setVisible(False)

        # Re-enable buttons
        self.backup_btn.setEnabled(True)
        self.load_config_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.browse_restore_btn.setEnabled(True)

        # Determine which operation completed and update the appropriate log
        if (
            self.viewmodel.backup_worker
            and not self.viewmodel.backup_worker.isRunning()
        ):
            # Backup just completed
            # Log any remaining skipped files
            if self._skipped_count > self._last_logged_skip_count:
                remaining = self._skipped_count - self._last_logged_skip_count
                self.operation_log.append(
                    f"⊘ Skipped {remaining} unchanged files (total: {self._skipped_count})...\n"
                )
            self.operation_log.append("\n=== Backup Operation Completed ===\n")
            # Write summary statistics to log
            self.operation_log.append(f"\n{summary}\n")
            # Ensure log is scrolled to bottom
            self.operation_log.verticalScrollBar().setValue(
                self.operation_log.verticalScrollBar().maximum()
            )
        elif (
            self.viewmodel.restore_worker
            and not self.viewmodel.restore_worker.isRunning()
        ):
            # Restore just completed
            self.restore_operation_log.append("\n=== Restore Operation Completed ===\n")
            # Write summary statistics to log
            self.restore_operation_log.append(f"\n{summary}\n")
            self.restore_operation_log.verticalScrollBar().setValue(
                self.restore_operation_log.verticalScrollBar().maximum()
            )

    def _on_error_occurred(self, context: str, error_message: str) -> None:
        """Handle error signal."""
        log_message = f"✗ Error in {context}: {error_message}\n"

        # Determine which log to update based on which worker is active
        if self.viewmodel.backup_worker and self.viewmodel.backup_worker.isRunning():
            self.operation_log.append(log_message)
        elif (
            self.viewmodel.restore_worker and self.viewmodel.restore_worker.isRunning()
        ):
            self.restore_operation_log.append(log_message)
        else:
            # If neither is running, it's likely a startup error - log to backup log
            self.operation_log.append(log_message)

        # Hide and reset progress bar on error
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)

        # Re-enable buttons after error
        self.backup_btn.setEnabled(True)
        self.load_config_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.browse_restore_btn.setEnabled(True)

    def _on_config_loaded(self, dotfile_count: int) -> None:
        """Handle configuration loaded signal."""
        self.status_bar.showMessage(f"Configuration loaded: {dotfile_count} dotfiles")
        self.backup_btn.setEnabled(True)
        self.save_dotfiles_btn.setEnabled(True)

        # Update dotfile table
        self._update_dotfile_table()

        # Update options display
        self._update_options_display()

    def _update_dotfile_table(self) -> None:
        """Update the dotfile table with current configuration (with full validation)."""
        dotfiles = self.viewmodel.get_dotfile_list()
        validation = self.viewmodel.get_dotfile_validation()
        sizes = self.viewmodel.get_dotfile_sizes()
        self._populate_dotfile_table(dotfiles, validation, sizes)

    def _update_dotfile_table_fast(self) -> None:
        """
        Fast update of dotfile table without filesystem validation.

        Used for operations that only change metadata (like toggling enabled status)
        but don't affect file existence. Reuses cached validation and size data.
        """
        dotfiles = self.viewmodel.get_dotfile_list()

        # Reuse existing validation and size data from current table instead of re-validating
        # Build validation and size dicts from current table items
        validation: dict[int, tuple[bool, bool, str]] = {}
        sizes: dict[int, int] = {}

        # Build a mapping from original index to table row for lookup
        idx_to_row: dict[int, int] = {}
        for row in range(self.dotfile_table.rowCount()):
            original_idx = self._get_original_dotfile_index(row)
            idx_to_row[original_idx] = row

        # Extract cached data for each dotfile
        for i in range(len(dotfiles)):
            if i in idx_to_row:
                row = idx_to_row[i]
                # Get existing status from current table
                status_item = self.dotfile_table.item(row, 1)
                type_item = self.dotfile_table.item(row, 5)
                size_item = self.dotfile_table.item(row, 6)

                if status_item and type_item and size_item:
                    exists = status_item.text() == "✓"
                    type_str = type_item.text()
                    is_dir = type_str == "Directory"
                    validation[i] = (exists, is_dir, type_str)

                    # Store size data by parsing back from the stored UserRole data
                    # Since we have formatted text, we need to cache the raw bytes
                    # For now, get fresh sizes (it's still reasonably fast)
                    sizes = self.viewmodel.get_dotfile_sizes()
                else:
                    # Fallback for missing data
                    validation[i] = (False, False, "File")
                    sizes[i] = 0
            else:
                # New item not in table yet
                validation[i] = (False, False, "File")
                sizes[i] = 0

        self._populate_dotfile_table(dotfiles, validation, sizes)

    def _populate_dotfile_table(
        self,
        dotfiles: list[DotFileDict],
        validation: dict[int, tuple[bool, bool, str]],
        sizes: dict[int, int],
    ) -> None:
        """
        Populate the dotfile table with given data.

        Args:
            dotfiles: List of dotfile dictionaries
            validation: Validation results mapping index to (exists, is_dir, type_str)
            sizes: Size results mapping index to size in bytes
        """
        # Save current expansion state (indexed by dotfile_idx, so it's sort-safe)
        # We'll restore expanded state after populating the table

        # Disable sorting while populating table to prevent performance issues
        self.dotfile_table.setSortingEnabled(False)

        # Create list of (index, dotfile, validation, size) tuples
        dotfile_data = [
            (i, dotfile, validation[i], sizes[i]) for i, dotfile in enumerate(dotfiles)
        ]

        self.dotfile_table.setRowCount(len(dotfiles))

        # Track total size for enabled items
        total_enabled_size = 0

        for row_idx, (
            original_idx,
            dotfile,
            (exists, _is_dir, _type_str),
            size,
        ) in enumerate(dotfile_data):
            # Enabled indicator with directory expand icon
            enabled = dotfile.get("enabled", True)

            # Simple enabled indicator
            indicator = "✓" if enabled else "✗"

            enabled_item = QTableWidgetItem(indicator)
            enabled_item.setData(
                Qt.ItemDataRole.UserRole, original_idx
            )  # Store original index
            if enabled:
                enabled_item.setForeground(QColor(0, 150, 0))  # Green
            else:
                enabled_item.setForeground(QColor(128, 128, 128))  # Gray
            self.dotfile_table.setItem(row_idx, 0, enabled_item)

            # Status indicator (file exists)
            status_item = QTableWidgetItem("✓" if exists else "✗")
            if exists:
                status_item.setForeground(QColor(0, 150, 0))  # Green
            else:
                status_item.setForeground(QColor(200, 0, 0))  # Red
            self.dotfile_table.setItem(row_idx, 1, status_item)

            # Category
            self.dotfile_table.setItem(
                row_idx, 2, QTableWidgetItem(dotfile["category"])
            )

            # Application
            self.dotfile_table.setItem(
                row_idx, 3, QTableWidgetItem(dotfile["application"])
            )

            # Size - format to human readable with custom numeric sorting
            size_str = self.viewmodel.format_size(size)
            size_item = NumericTableWidgetItem(size_str)
            # Store raw size value for proper numeric sorting
            size_item.setData(Qt.ItemDataRole.UserRole, size)
            # Right-align the size for better readability
            size_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.dotfile_table.setItem(row_idx, 4, size_item)

            # Path - show first path with count indicator if multiple
            paths = dotfile["paths"]
            if len(paths) == 1:
                path_display = paths[0]
            else:
                path_display = f"{paths[0]} (+{len(paths) - 1} more)"

            path_item = QTableWidgetItem(path_display)
            # Tooltip shows description and all paths
            tooltip_text = f"{dotfile['description']}\n\nPaths:\n{'\n'.join(paths)}"
            path_item.setToolTip(tooltip_text)
            self.dotfile_table.setItem(row_idx, 5, path_item)

            # Accumulate total size for enabled items
            if enabled and exists:
                total_enabled_size += size

        # Update total size label
        self.total_size_label.setText(
            f"Total Size (enabled): {self.viewmodel.format_size(total_enabled_size)}"
        )

        # Re-enable sorting after everything is populated
        self.dotfile_table.setSortingEnabled(True)

    def _update_options_display(self) -> None:
        """Update the options display with current configuration."""
        options = self.viewmodel.get_options()

        # Update configuration tab widgets
        self.config_mirror_checkbox.setChecked(options["mirror"])
        self.config_archive_checkbox.setChecked(options["archive"])
        self.config_hostname_checkbox.setChecked(options["hostname_subdir"])
        self.config_date_checkbox.setChecked(options["date_subdir"])
        self.config_compression_spinbox.setValue(options["archive_compression_level"])
        self.config_rotate_checkbox.setChecked(options["rotate_archives"])
        self.config_max_archives_spinbox.setValue(options["max_archives"])

        # Update path displays
        mirror_path = str(self.viewmodel.model.mirror_base_dir)
        archive_path = str(self.viewmodel.model.archive_base_dir)
        self.config_mirror_path_edit.setText(mirror_path)
        self.config_archive_path_edit.setText(archive_path)

        # Enable max archives spinbox only if rotation is enabled
        self.config_max_archives_spinbox.setEnabled(options["rotate_archives"])

        # Enable save button since config is loaded
        self.save_config_btn.setEnabled(True)

        # Update backup tab checkboxes
        self.mirror_checkbox.setChecked(options["mirror"])
        self.archive_checkbox.setChecked(options["archive"])

    def _on_mirror_checkbox_changed(self, state: int) -> None:
        """Handle mirror checkbox state change."""
        self.viewmodel.set_mirror_mode(bool(state))

    def _on_archive_checkbox_changed(self, state: int) -> None:
        """Handle archive checkbox state change."""
        self.viewmodel.set_archive_mode(bool(state))

    def _show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            f"About {self.PROJECT_NAME}",
            f"{self.PROJECT_NAME} v{self.version}\n\n"
            "Dotfiles Backup and Restore Utility\n\n"
            "A desktop application for backing up and restoring\n"
            "configuration files with metadata preservation.\n\n"
            "Author: Chris Purcell\n"
            "Email: chris@l3digital.net\n"
            "GitHub: https://github.com/L3DigitalNet",
        )

    def _on_browse_mirror_dir(self) -> None:
        """Handle browse mirror directory button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Mirror Backup Directory", str(Path.home())
        )

        if directory:
            self.config_mirror_path_edit.setText(directory)

    def _on_browse_archive_dir(self) -> None:
        """Handle browse archive directory button click."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Archive Backup Directory", str(Path.home())
        )

        if directory:
            self.config_archive_path_edit.setText(directory)

    def _on_config_changed(self) -> None:
        """Handle configuration option changes to enable save button."""
        # Enable save button when any configuration option changes
        self.save_config_btn.setEnabled(True)

    def _on_rotate_checkbox_changed(self, state: int) -> None:
        """Handle rotate archives checkbox state change."""
        # Enable/disable max archives spinbox based on rotation checkbox
        self.config_max_archives_spinbox.setEnabled(bool(state))

    def _on_save_config(self) -> None:
        """Handle save configuration button click."""
        # Confirm save operation
        reply = QMessageBox.question(
            self,
            "Confirm Save",
            "Save configuration changes to file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Update model with all configuration values
            self.viewmodel.command_update_option(
                "mirror", self.config_mirror_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "archive", self.config_archive_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "hostname_subdir", self.config_hostname_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "date_subdir", self.config_date_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "archive_compression_level", self.config_compression_spinbox.value()
            )
            self.viewmodel.command_update_option(
                "rotate_archives", self.config_rotate_checkbox.isChecked()
            )
            self.viewmodel.command_update_option(
                "max_archives", self.config_max_archives_spinbox.value()
            )

            # Update paths
            self.viewmodel.command_update_path(
                "mirror_dir", self.config_mirror_path_edit.text()
            )
            self.viewmodel.command_update_path(
                "archive_dir", self.config_archive_path_edit.text()
            )

            # Save to file
            if self.viewmodel.command_save_config():
                QMessageBox.information(
                    self,
                    "Configuration Saved",
                    "Configuration has been saved successfully.",
                )

                # Update backup tab checkboxes to reflect changes
                self.mirror_checkbox.setChecked(self.config_mirror_checkbox.isChecked())
                self.archive_checkbox.setChecked(
                    self.config_archive_checkbox.isChecked()
                )
            else:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    "Failed to save configuration. Check file permissions.",
                )

    def _on_save_dotfile_config(self) -> None:
        """Handle save dotfile configuration button click from Backup tab."""
        # Confirm save operation
        reply = QMessageBox.question(
            self,
            "Confirm Save",
            "Save dotfile configuration changes (enable/disable settings) to file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Save to file
            if self.viewmodel.command_save_config():
                QMessageBox.information(
                    self,
                    "Configuration Saved",
                    "Dotfile configuration has been saved successfully.",
                )
            else:
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    "Failed to save configuration. Check file permissions.",
                )

    def _get_original_dotfile_index(self, table_row: int) -> int:
        """
        Get the original dotfile index from a table row.

        Args:
            table_row: Row index in the table (after sorting)

        Returns:
            Original index in the dotfiles list

        Raises:
            ValueError: If unable to determine original index (data corruption)
        """
        # Get the original index stored in the first column item
        item = self.dotfile_table.item(table_row, 0)
        if item:
            original_idx = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(original_idx, int):
                return original_idx

        # Data missing or corrupt - this indicates a programming error
        raise ValueError(
            f"Unable to determine original dotfile index for table row {table_row}. "
            "Table data may be corrupt."
        )

    def _on_dotfile_selection_changed(self) -> None:
        """Handle dotfile table selection change."""
        # Enable update, toggle, and remove buttons if a row is selected
        has_selection = len(self.dotfile_table.selectedItems()) > 0
        self.update_dotfile_btn.setEnabled(has_selection)
        self.toggle_enabled_btn.setEnabled(has_selection)
        self.remove_dotfile_btn.setEnabled(has_selection)

    def _on_add_dotfile(self) -> None:
        """Handle add dotfile button click."""
        # Get unique categories for dropdown
        categories = self.viewmodel.get_unique_categories()

        # Create dialog for adding new dotfile
        dialog = AddDotfileDialog(self, categories=categories)

        if dialog.exec():
            # Get values from dialog
            category = dialog.category_combo.currentText()
            application = dialog.application_edit.text()
            description = dialog.description_edit.text()
            paths = dialog.get_paths()
            enabled = dialog.enabled_checkbox.isChecked()

            # Validate inputs
            if not all([category, application, description]) or not paths:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please fill in all fields and add at least one path.",
                )
                return

            # Add dotfile via ViewModel
            success = self.viewmodel.command_add_dotfile(
                category, application, description, paths, enabled
            )

            if success:
                QMessageBox.information(
                    self, "Dotfile Added", "Dotfile entry has been added successfully."
                )
            else:
                QMessageBox.critical(self, "Add Failed", "Failed to add dotfile entry.")

    def _on_update_dotfile(self) -> None:
        """Handle update dotfile button click."""
        # Get selected row
        selected_rows = self.dotfile_table.selectionModel().selectedRows()

        if not selected_rows:
            return

        table_row = selected_rows[0].row()
        original_idx = self._get_original_dotfile_index(table_row)

        # Get existing dotfile data
        dotfile = self.viewmodel.get_dotfile_list()[original_idx]

        # Get unique categories for dropdown
        categories = self.viewmodel.get_unique_categories()

        # Create dialog for updating dotfile with pre-populated data
        # Cast TypedDict to plain dict for dialog compatibility
        dialog = AddDotfileDialog(
            self,
            dotfile_data=dict(dotfile),
            categories=categories,
        )

        if dialog.exec():
            # Get updated values from dialog
            category = dialog.category_combo.currentText()
            application = dialog.application_edit.text()
            description = dialog.description_edit.text()
            paths = dialog.get_paths()
            enabled = dialog.enabled_checkbox.isChecked()

            # Validate inputs
            if not all([category, application, description]) or not paths:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please fill in all fields and add at least one path.",
                )
                return

            # Update dotfile via ViewModel
            success = self.viewmodel.command_update_dotfile(
                original_idx,
                category,
                application,
                description,
                paths,
                enabled,
            )

            if success:
                QMessageBox.information(
                    self,
                    "Dotfile Updated",
                    "Dotfile entry has been updated successfully.",
                )
            else:
                QMessageBox.critical(
                    self, "Update Failed", "Failed to update dotfile entry."
                )

    def _on_remove_dotfile(self) -> None:
        """Handle remove dotfile button click."""
        # Get selected row
        selected_rows = self.dotfile_table.selectionModel().selectedRows()

        if not selected_rows:
            return

        table_row = selected_rows[0].row()
        original_idx = self._get_original_dotfile_index(table_row)

        # Confirm removal
        dotfile = self.viewmodel.get_dotfile_list()[original_idx]

        # Format paths display
        paths_display = "\n".join(dotfile["paths"])

        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Remove dotfile entry for {dotfile['application']}?\n\n"
            f"Paths:\n{paths_display}\n\n"
            "This will not delete the actual files, only the configuration entry.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove dotfile via ViewModel
            success = self.viewmodel.command_remove_dotfile(original_idx)

            if success:
                QMessageBox.information(
                    self,
                    "Dotfile Removed",
                    "Dotfile entry has been removed successfully.",
                )
            else:
                QMessageBox.critical(
                    self, "Remove Failed", "Failed to remove dotfile entry."
                )

    def _on_toggle_dotfile_enabled(self) -> None:
        """Handle toggle dotfile enabled button click."""
        # Get selected row
        selected_rows = self.dotfile_table.selectionModel().selectedRows()

        if not selected_rows:
            return

        table_row = selected_rows[0].row()
        original_idx = self._get_original_dotfile_index(table_row)

        # Get current dotfile
        dotfile = self.viewmodel.get_dotfile_list()[original_idx]

        # Toggle enabled status via ViewModel
        new_status = self.viewmodel.command_toggle_dotfile_enabled(original_idx)

        # Update status bar with brief feedback (non-blocking)
        status_text = "enabled" if new_status else "disabled"
        self.status_bar.showMessage(
            f"Dotfile '{dotfile['application']}' {status_text}",
            STATUS_MESSAGE_TIMEOUT_MS,
        )

        # Perform lightweight table update without re-validation
        self._update_dotfile_table_fast()

    def _on_dotfiles_updated(self, dotfile_count: int) -> None:
        """Handle dotfiles updated signal."""
        # Update the dotfile table
        self._update_dotfile_table()

        # Update status bar
        self.status_bar.showMessage(f"Configuration updated: {dotfile_count} dotfiles")

    def _on_save_log(self) -> None:
        """Handle save log button click."""
        # Get current log content
        log_content = self.operation_log.toPlainText()

        # Check if log is empty
        if not log_content.strip():
            QMessageBox.information(
                self,
                "Empty Log",
                "The log is currently empty. There is nothing to save.",
            )
            return

        # Open file save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log File",
            str(Path.home() / "dfbu_log.txt"),
            "Text Files (*.txt);;All Files (*)",
        )

        if file_path:
            try:
                # Write log content to file
                Path(file_path).write_text(log_content, encoding="utf-8")

                # Show success message in status bar (non-blocking)
                self.status_bar.showMessage(
                    f"Log saved to {Path(file_path).name}",
                    STATUS_MESSAGE_TIMEOUT_MS,
                )
            except (OSError, PermissionError) as e:
                # Show error dialog if save fails
                QMessageBox.critical(
                    self,
                    "Save Failed",
                    f"Failed to save log file:\n{e}",
                )

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event."""
        # Save window geometry and state
        self.viewmodel.save_settings(
            geometry=self.saveGeometry(), window_state=self.saveState()
        )
        event.accept()
