#!/usr/bin/env python3
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
Date Changed: 10-31-2025
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

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
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
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# Local import
from viewmodel import DFBUViewModel


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
        if self_value is None:
            self_value = 0
        if other_value is None:
            other_value = 0

        return self_value < other_value


class AddDotfileDialog(QDialog):
    """
    Dialog for adding or updating dotfile entry with support for multiple paths.

    Attributes:
        category_combo: Editable combo box for category (prepopulated)
        subcategory_combo: Editable combo box for subcategory (prepopulated)
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
        subcategories: list[str] | None = None,
    ) -> None:
        """
        Initialize the AddDotfileDialog.

        Args:
            parent: Parent widget
            dotfile_data: Optional existing dotfile data for update mode
            categories: List of existing categories for dropdown
            subcategories: List of existing subcategories for dropdown
        """
        super().__init__(parent)
        self.is_update_mode = dotfile_data is not None
        self.setWindowTitle(
            "Update Dotfile Entry" if self.is_update_mode else "Add Dotfile Entry"
        )
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

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

        # Subcategory combo box (editable)
        self.subcategory_combo = QComboBox()
        self.subcategory_combo.setEditable(True)
        self.subcategory_combo.setPlaceholderText("e.g., Web Browser, Shell")
        if subcategories:
            self.subcategory_combo.addItems(subcategories)
        form_layout.addRow("Subcategory:", self.subcategory_combo)

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
            self.subcategory_combo.setCurrentText(dotfile_data.get("subcategory", ""))
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
        # First try to select a file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            str(Path.home()),
            "All Files (*)",
        )

        if file_path:
            self.path_input_edit.setText(file_path)
        else:
            # If no file selected, try directory
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

    def get_paths(self) -> list[str]:
        """
        Get list of paths from the list widget.

        Returns:
            List of path strings
        """
        paths = []
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
    STATUS_MESSAGE_TIMEOUT_MS: Final[int] = 3000  # 3 seconds

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

        self.setup_ui()
        self._connect_viewmodel_signals()
        self._load_settings()

    def setup_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle(f"{self.PROJECT_NAME} v{self.version}")
        self.setMinimumSize(1000, 700)

        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Setup menu bar
        self.setup_menu_bar()

        # Create tab widget for different views
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Setup tabs
        self.setup_backup_tab()
        self.setup_restore_tab()
        self.setup_config_tab()

        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Load configuration to begin")

        # Setup progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

    def setup_menu_bar(self) -> None:
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        load_config_action = QAction("&Load Configuration...", self)
        load_config_action.setShortcut("Ctrl+O")
        load_config_action.triggered.connect(self._on_browse_config)
        file_menu.addAction(load_config_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Operations menu
        operations_menu = menubar.addMenu("&Operations")

        backup_action = QAction("Start &Backup", self)
        backup_action.setShortcut("Ctrl+B")
        backup_action.triggered.connect(self._on_start_backup)
        operations_menu.addAction(backup_action)

        restore_action = QAction("Start &Restore", self)
        restore_action.setShortcut("Ctrl+R")
        restore_action.triggered.connect(self._on_start_restore)
        operations_menu.addAction(restore_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def setup_backup_tab(self) -> None:
        """Create the backup operations tab."""
        backup_tab = QWidget()
        backup_layout = QVBoxLayout(backup_tab)

        # Configuration section
        config_group = self._create_config_section()
        backup_layout.addWidget(config_group)

        # Dotfile list section
        dotfile_group = self._create_dotfile_list_section()
        backup_layout.addWidget(dotfile_group)

        # Backup options section
        options_group = self._create_backup_options_section()
        backup_layout.addWidget(options_group)

        # Operation log section
        log_group = self._create_operation_log_section()
        backup_layout.addWidget(log_group)

        self.tab_widget.addTab(backup_tab, "Backup")

    def setup_restore_tab(self) -> None:
        """Create the restore operations tab."""
        restore_tab = QWidget()
        restore_layout = QVBoxLayout(restore_tab)

        # Source selection section
        source_group = self._create_restore_source_section()
        restore_layout.addWidget(source_group)

        # Restore information section
        info_group = self._create_restore_info_section()
        restore_layout.addWidget(info_group)

        # Operation log section
        log_group = self._create_operation_log_section_restore()
        restore_layout.addWidget(log_group)

        restore_layout.addStretch()

        self.tab_widget.addTab(restore_tab, "Restore")

    def setup_config_tab(self) -> None:
        """Create the configuration display tab."""
        config_tab = QWidget()
        config_layout = QVBoxLayout(config_tab)

        # Options display section
        options_group = self._create_options_display_section()
        config_layout.addWidget(options_group)

        config_layout.addStretch()

        self.tab_widget.addTab(config_tab, "Configuration")

    def _create_config_section(self) -> QGroupBox:
        """Create configuration file selection section."""
        group = QGroupBox("Configuration File")
        layout = QHBoxLayout()

        # Configuration path input
        self.config_path_edit = QLineEdit()
        self.config_path_edit.setPlaceholderText("Path to dfbu-config.toml")
        self.config_path_edit.setReadOnly(True)
        layout.addWidget(self.config_path_edit)

        # Browse button
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._on_browse_config)
        layout.addWidget(browse_btn)

        # Load button
        self.load_config_btn = QPushButton("Load Configuration")
        self.load_config_btn.clicked.connect(self._on_load_config)
        layout.addWidget(self.load_config_btn)

        group.setLayout(layout)
        return group

    def _create_dotfile_list_section(self) -> QGroupBox:
        """Create dotfile list display section."""
        group = QGroupBox("Configured Dotfiles")
        layout = QVBoxLayout()

        # Create table for dotfile display
        self.dotfile_table = QTableWidget()
        self.dotfile_table.setColumnCount(8)
        self.dotfile_table.setHorizontalHeaderLabels(
            [
                "Enabled",
                "Status",
                "Category",
                "Subcategory",
                "Application",
                "Type",
                "Size",
                "Path",
            ]
        )

        # Configure table properties
        self.dotfile_table.setAlternatingRowColors(True)
        self.dotfile_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.dotfile_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        # Set column resize modes
        header = self.dotfile_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.dotfile_table)

        # Total size label
        self.total_size_label = QLabel("Total Size (enabled): Calculating...")
        self.total_size_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.total_size_label)

        # Add/Remove buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.add_dotfile_btn = QPushButton("Add Dotfile")
        self.add_dotfile_btn.clicked.connect(self._on_add_dotfile)
        button_layout.addWidget(self.add_dotfile_btn)

        self.update_dotfile_btn = QPushButton("Update Selected")
        self.update_dotfile_btn.clicked.connect(self._on_update_dotfile)
        self.update_dotfile_btn.setEnabled(False)
        button_layout.addWidget(self.update_dotfile_btn)

        self.toggle_enabled_btn = QPushButton("Toggle Enabled/Disabled")
        self.toggle_enabled_btn.clicked.connect(self._on_toggle_dotfile_enabled)
        self.toggle_enabled_btn.setEnabled(False)
        button_layout.addWidget(self.toggle_enabled_btn)

        self.remove_dotfile_btn = QPushButton("Remove Selected")
        self.remove_dotfile_btn.clicked.connect(self._on_remove_dotfile)
        self.remove_dotfile_btn.setEnabled(False)
        button_layout.addWidget(self.remove_dotfile_btn)

        button_layout.addStretch()

        self.save_dotfiles_btn = QPushButton("Save Dotfile Config")
        self.save_dotfiles_btn.clicked.connect(self._on_save_dotfile_config)
        self.save_dotfiles_btn.setEnabled(False)
        button_layout.addWidget(self.save_dotfiles_btn)

        layout.addLayout(button_layout)

        # Connect table selection changed signal
        self.dotfile_table.itemSelectionChanged.connect(
            self._on_dotfile_selection_changed
        )

        group.setLayout(layout)
        return group

    def _create_backup_options_section(self) -> QGroupBox:
        """Create backup options and controls section."""
        group = QGroupBox("Backup Options")
        layout = QVBoxLayout()

        # Backup mode checkboxes
        mode_layout = QHBoxLayout()

        self.mirror_checkbox = QCheckBox("Mirror Backup (uncompressed)")
        self.mirror_checkbox.setChecked(True)
        self.mirror_checkbox.stateChanged.connect(self._on_mirror_checkbox_changed)
        mode_layout.addWidget(self.mirror_checkbox)

        self.archive_checkbox = QCheckBox("Archive Backup (compressed)")
        self.archive_checkbox.stateChanged.connect(self._on_archive_checkbox_changed)
        mode_layout.addWidget(self.archive_checkbox)

        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Backup button
        button_layout = QHBoxLayout()
        self.backup_btn = QPushButton("Start Backup")
        self.backup_btn.clicked.connect(self._on_start_backup)
        self.backup_btn.setEnabled(False)
        button_layout.addStretch()
        button_layout.addWidget(self.backup_btn)
        layout.addLayout(button_layout)

        group.setLayout(layout)
        return group

    def _create_operation_log_section(self) -> QGroupBox:
        """Create operation log display section."""
        group = QGroupBox("Operation Log")
        layout = QVBoxLayout()

        # Progress label
        self.progress_label = QLabel("Ready")
        layout.addWidget(self.progress_label)

        # Operation log text area
        self.operation_log = QTextEdit()
        self.operation_log.setReadOnly(True)
        self.operation_log.setMaximumHeight(200)
        layout.addWidget(self.operation_log)

        group.setLayout(layout)
        return group

    def _create_restore_source_section(self) -> QGroupBox:
        """Create restore source selection section."""
        group = QGroupBox("Restore Source")
        layout = QVBoxLayout()

        # Information label
        info_label = QLabel(
            "Select the backup directory containing the hostname folder.\n"
            "Example: ~/GitHub/dotfiles/ (containing hostname subdirectory)"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Source path input
        path_layout = QHBoxLayout()

        self.restore_source_edit = QLineEdit()
        self.restore_source_edit.setPlaceholderText(
            "Path to backup directory with hostname"
        )
        self.restore_source_edit.setReadOnly(True)
        path_layout.addWidget(self.restore_source_edit)

        # Browse button
        self.browse_restore_btn = QPushButton("Browse...")
        self.browse_restore_btn.clicked.connect(self._on_browse_restore_source)
        path_layout.addWidget(self.browse_restore_btn)

        layout.addLayout(path_layout)

        # Restore button
        button_layout = QHBoxLayout()
        self.restore_btn = QPushButton("Start Restore")
        self.restore_btn.clicked.connect(self._on_start_restore)
        self.restore_btn.setEnabled(False)
        button_layout.addStretch()
        button_layout.addWidget(self.restore_btn)
        layout.addLayout(button_layout)

        group.setLayout(layout)
        return group

    def _create_restore_info_section(self) -> QGroupBox:
        """Create restore information section."""
        group = QGroupBox("Restore Information")
        layout = QVBoxLayout()

        info_text = QLabel(
            "Restore will:\n"
            "• Discover all files in the selected backup directory\n"
            "• Reconstruct original file paths based on backup structure\n"
            "• Copy files back to their original locations\n"
            "• Create necessary parent directories\n"
            "• Preserve file metadata and permissions\n\n"
            "WARNING: This will overwrite existing files at destination paths."
        )
        info_text.setWordWrap(True)
        layout.addWidget(info_text)

        group.setLayout(layout)
        return group

    def _create_operation_log_section_restore(self) -> QGroupBox:
        """Create operation log display section for restore tab."""
        group = QGroupBox("Operation Log")
        layout = QVBoxLayout()

        # Progress label
        self.restore_progress_label = QLabel("Ready")
        layout.addWidget(self.restore_progress_label)

        # Operation log text area
        self.restore_operation_log = QTextEdit()
        self.restore_operation_log.setReadOnly(True)
        self.restore_operation_log.setMaximumHeight(200)
        layout.addWidget(self.restore_operation_log)

        group.setLayout(layout)
        return group

    def _create_options_display_section(self) -> QGroupBox:
        """Create editable options configuration section."""
        group = QGroupBox("Configuration Settings")
        main_layout = QVBoxLayout()

        # Create form layout for configuration options
        form_layout = QFormLayout()

        # Paths section
        paths_label = QLabel("Backup Paths")
        paths_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(paths_label)

        # Mirror directory path
        mirror_path_layout = QHBoxLayout()
        self.config_mirror_path_edit = QLineEdit()
        self.config_mirror_path_edit.setPlaceholderText("Mirror backup directory")
        self.config_mirror_path_edit.textChanged.connect(self._on_config_changed)
        mirror_path_layout.addWidget(self.config_mirror_path_edit)
        browse_mirror_btn = QPushButton("Browse...")
        browse_mirror_btn.clicked.connect(self._on_browse_mirror_dir)
        mirror_path_layout.addWidget(browse_mirror_btn)
        form_layout.addRow("Mirror Directory:", mirror_path_layout)

        # Archive directory path
        archive_path_layout = QHBoxLayout()
        self.config_archive_path_edit = QLineEdit()
        self.config_archive_path_edit.setPlaceholderText("Archive backup directory")
        self.config_archive_path_edit.textChanged.connect(self._on_config_changed)
        archive_path_layout.addWidget(self.config_archive_path_edit)
        browse_archive_btn = QPushButton("Browse...")
        browse_archive_btn.clicked.connect(self._on_browse_archive_dir)
        archive_path_layout.addWidget(browse_archive_btn)
        form_layout.addRow("Archive Directory:", archive_path_layout)

        # Backup modes section
        modes_label = QLabel("Backup Modes")
        modes_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(modes_label)

        # Mirror backup checkbox
        self.config_mirror_checkbox = QCheckBox("Enable mirror backup (uncompressed)")
        self.config_mirror_checkbox.stateChanged.connect(self._on_config_changed)
        form_layout.addRow("Mirror Backup:", self.config_mirror_checkbox)

        # Archive backup checkbox
        self.config_archive_checkbox = QCheckBox("Enable archive backup (compressed)")
        self.config_archive_checkbox.stateChanged.connect(self._on_config_changed)
        form_layout.addRow("Archive Backup:", self.config_archive_checkbox)

        # Directory structure section
        structure_label = QLabel("Directory Structure")
        structure_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(structure_label)

        # Hostname subdirectory checkbox
        self.config_hostname_checkbox = QCheckBox("Include hostname in backup path")
        self.config_hostname_checkbox.stateChanged.connect(self._on_config_changed)
        form_layout.addRow("Hostname Subdir:", self.config_hostname_checkbox)

        # Date subdirectory checkbox
        self.config_date_checkbox = QCheckBox("Include date in backup path")
        self.config_date_checkbox.stateChanged.connect(self._on_config_changed)
        form_layout.addRow("Date Subdir:", self.config_date_checkbox)

        # Archive options section
        archive_opts_label = QLabel("Archive Options")
        archive_opts_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        form_layout.addRow(archive_opts_label)

        # Compression level spinbox
        self.config_compression_spinbox = QSpinBox()
        self.config_compression_spinbox.setMinimum(0)
        self.config_compression_spinbox.setMaximum(9)
        self.config_compression_spinbox.setToolTip(
            "0 = no compression, 9 = maximum compression"
        )
        self.config_compression_spinbox.valueChanged.connect(self._on_config_changed)
        form_layout.addRow("Compression Level:", self.config_compression_spinbox)

        # Archive rotation checkbox
        self.config_rotate_checkbox = QCheckBox("Enable archive rotation")
        self.config_rotate_checkbox.stateChanged.connect(
            self._on_rotate_checkbox_changed
        )
        self.config_rotate_checkbox.stateChanged.connect(self._on_config_changed)
        form_layout.addRow("Rotate Archives:", self.config_rotate_checkbox)

        # Max archives spinbox
        self.config_max_archives_spinbox = QSpinBox()
        self.config_max_archives_spinbox.setMinimum(1)
        self.config_max_archives_spinbox.setMaximum(100)
        self.config_max_archives_spinbox.setToolTip(
            "Maximum number of archives to keep"
        )
        self.config_max_archives_spinbox.valueChanged.connect(self._on_config_changed)
        form_layout.addRow("Max Archives:", self.config_max_archives_spinbox)

        main_layout.addLayout(form_layout)

        # Save button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.save_config_btn = QPushButton("Save Configuration")
        self.save_config_btn.clicked.connect(self._on_save_config)
        self.save_config_btn.setEnabled(False)
        button_layout.addWidget(self.save_config_btn)
        main_layout.addLayout(button_layout)

        main_layout.addStretch()

        group.setLayout(main_layout)
        return group

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
            # Clear operation log
            self.operation_log.clear()
            self.progress_label.setText("Starting backup...")

            # Disable buttons during operation
            self.backup_btn.setEnabled(False)
            self.load_config_btn.setEnabled(False)

            # Show progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)

            # Start backup
            self.viewmodel.command_start_backup()

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
            self.restore_progress_label.setText("Starting restore...")

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

        # Update progress label
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:  # Backup tab
            self.progress_label.setText(f"Progress: {value}%")
        elif current_tab == 1:  # Restore tab
            self.restore_progress_label.setText(f"Progress: {value}%")

    def _on_item_processed(self, source: str, destination: str) -> None:
        """Handle item processed signal."""
        # Determine which log to update based on current tab
        current_tab = self.tab_widget.currentIndex()

        log_message = f"✓ {Path(source).name} → {destination}\n"

        if current_tab == 0:  # Backup tab
            self.operation_log.append(log_message)
        elif current_tab == 1:  # Restore tab
            self.restore_operation_log.append(log_message)

    def _on_item_skipped(self, path: str, reason: str) -> None:
        """Handle item skipped signal."""
        log_message = f"⊘ Skipped: {Path(path).name} - {reason}\n"
        self.operation_log.append(log_message)

    def _on_operation_finished(self, summary: str) -> None:
        """Handle operation finished signal."""
        # Hide progress bar
        self.progress_bar.setVisible(False)

        # Re-enable buttons
        self.backup_btn.setEnabled(True)
        self.load_config_btn.setEnabled(True)
        self.restore_btn.setEnabled(True)
        self.browse_restore_btn.setEnabled(True)

        # Update status
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:  # Backup tab
            self.progress_label.setText("Backup completed")
        elif current_tab == 1:  # Restore tab
            self.restore_progress_label.setText("Restore completed")

        # Show completion dialog
        QMessageBox.information(self, "Operation Complete", summary)

    def _on_error_occurred(self, context: str, error_message: str) -> None:
        """Handle error signal."""
        log_message = f"✗ Error in {context}: {error_message}\n"

        # Determine which log to update
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:  # Backup tab
            self.operation_log.append(log_message)
        elif current_tab == 1:  # Restore tab
            self.restore_operation_log.append(log_message)

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
        dotfiles: list,
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
            (exists, _is_dir, type_str),
            size,
        ) in enumerate(dotfile_data):
            # Enabled indicator
            enabled = dotfile.get("enabled", True)
            enabled_item = QTableWidgetItem("✓" if enabled else "✗")
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

            # Subcategory
            self.dotfile_table.setItem(
                row_idx, 3, QTableWidgetItem(dotfile["subcategory"])
            )

            # Application
            self.dotfile_table.setItem(
                row_idx, 4, QTableWidgetItem(dotfile["application"])
            )

            # Type
            self.dotfile_table.setItem(row_idx, 5, QTableWidgetItem(type_str))

            # Size - format to human readable with custom numeric sorting
            size_str = self.viewmodel.format_size(size)
            size_item = NumericTableWidgetItem(size_str)
            # Store raw size value for proper numeric sorting
            size_item.setData(Qt.ItemDataRole.UserRole, size)
            # Right-align the size for better readability
            size_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
            self.dotfile_table.setItem(row_idx, 6, size_item)

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
            self.dotfile_table.setItem(row_idx, 7, path_item)

            # Accumulate total size for enabled items
            if enabled and exists:
                total_enabled_size += size

        # Update total size label
        self.total_size_label.setText(
            f"Total Size (enabled): {self.viewmodel.format_size(total_enabled_size)}"
        )

        # Re-enable sorting after populating table
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
        """
        # Get the original index stored in the first column item
        item = self.dotfile_table.item(table_row, 0)
        if item:
            original_idx = item.data(Qt.ItemDataRole.UserRole)
            if original_idx is not None and isinstance(original_idx, int):
                return original_idx
        # Fallback to table row if no data stored (shouldn't happen)
        return table_row

    def _on_dotfile_selection_changed(self) -> None:
        """Handle dotfile table selection change."""
        # Enable update, toggle, and remove buttons if a row is selected
        has_selection = len(self.dotfile_table.selectedItems()) > 0
        self.update_dotfile_btn.setEnabled(has_selection)
        self.toggle_enabled_btn.setEnabled(has_selection)
        self.remove_dotfile_btn.setEnabled(has_selection)

    def _on_add_dotfile(self) -> None:
        """Handle add dotfile button click."""
        # Get unique categories and subcategories for dropdown
        categories = self.viewmodel.get_unique_categories()
        subcategories = self.viewmodel.get_unique_subcategories()

        # Create dialog for adding new dotfile
        dialog = AddDotfileDialog(
            self, categories=categories, subcategories=subcategories
        )

        if dialog.exec():
            # Get values from dialog
            category = dialog.category_combo.currentText()
            subcategory = dialog.subcategory_combo.currentText()
            application = dialog.application_edit.text()
            description = dialog.description_edit.text()
            paths = dialog.get_paths()
            enabled = dialog.enabled_checkbox.isChecked()

            # Validate inputs
            if not all([category, subcategory, application, description]) or not paths:
                QMessageBox.warning(
                    self,
                    "Missing Information",
                    "Please fill in all fields and add at least one path.",
                )
                return

            # Add dotfile via ViewModel
            success = self.viewmodel.command_add_dotfile(
                category, subcategory, application, description, paths, enabled
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

        # Get unique categories and subcategories for dropdown
        categories = self.viewmodel.get_unique_categories()
        subcategories = self.viewmodel.get_unique_subcategories()

        # Create dialog for updating dotfile with pre-populated data
        # Cast TypedDict to plain dict for dialog compatibility
        dialog = AddDotfileDialog(
            self,
            dotfile_data=dict(dotfile),
            categories=categories,
            subcategories=subcategories,
        )

        if dialog.exec():
            # Get updated values from dialog
            category = dialog.category_combo.currentText()
            subcategory = dialog.subcategory_combo.currentText()
            application = dialog.application_edit.text()
            description = dialog.description_edit.text()
            paths = dialog.get_paths()
            enabled = dialog.enabled_checkbox.isChecked()

            # Validate inputs
            if not all([category, subcategory, application, description]) or not paths:
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
                subcategory,
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
            self.STATUS_MESSAGE_TIMEOUT_MS,
        )

        # Perform lightweight table update without re-validation
        self._update_dotfile_table_fast()

    def _on_dotfiles_updated(self, dotfile_count: int) -> None:
        """Handle dotfiles updated signal."""
        # Update the dotfile table
        self._update_dotfile_table()

        # Update status bar
        self.status_bar.showMessage(f"Configuration updated: {dotfile_count} dotfiles")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event."""
        # Save window geometry and state
        self.viewmodel.save_settings(
            geometry=self.saveGeometry(), window_state=self.saveState()
        )
        event.accept()
