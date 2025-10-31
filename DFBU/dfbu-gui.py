#!/usr/bin/env python3
"""
DFBU GUI - Dotfiles Backup Utility (Desktop Edition)

Description:
    Desktop application for comprehensive file backup and restoration with a
    graphical user interface. Built on MVVM architecture using PySide6,
    providing an intuitive way to manage configuration file backups.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-18-2025
Date Changed: 10-30-2025
License: MIT

Features:
    - Modern desktop GUI with tab-based interface
    - MVVM architectural pattern with clean separation of concerns
    - Threaded operations to prevent UI blocking
    - Window state persistence (size, position, preferences)
    - Responsive user feedback for long operations
    - Signal-based reactive data binding
    - TOML configuration with Category/Subcategory/Application metadata structure
    - Interactive dotfile management with add, update, and remove functionality
    - Flexible directory organization with hostname and date-based subdirectory options
    - Python 3.14 Path.copy() with metadata preservation and symlink support
    - Recursive file and directory processing with automatic parent directory creation
    - Permission checking and graceful handling of inaccessible files
    - Mirror backup mode for uncompressed file copies maintaining directory structure
    - Compressed archive creation with TAR.GZ format and configurable compression levels
    - Archive rotation with configurable maximum archive limits per retention policy
    - Interactive restore with visual feedback and progress tracking
    - Comprehensive file existence validation and type detection
    - Full type hint coverage with typed dictionaries for configuration data structures
    - Python standard library first approach with minimal dependencies

Requirements:
    - Linux environment only
    - Python 3.14+ for latest Path.copy() functionality with metadata preservation
    - PySide6 framework for modern desktop GUI
    - Custom libraries located at ../common_lib/
    - Properly configured TOML file located at ./data/dfbu-config.toml
    - Standard library: pathlib, tomllib, tarfile, socket, time, datetime, sys, os

Known Issues:
    - Comprehensive error handling deferred until v1.0.0 per confident design pattern
    - No support for network paths or remote destinations
    - Restore functionality requires exact hostname match in backup directory structure
    - No verification of successful copies or restoration integrity checks
    - Limited symlink support (follow_symlinks=True only)

Planned Features:
    - Differential backups with change detection based on modification time
    - Enhanced restore capabilities with cross-hostname support
    - Pre-restoration backup of existing files to prevent data loss
    - Incremental backup support with change detection and differential backups
    - Network path support for remote backup destinations
    - Backup verification and integrity checking with hash comparison
    - Scheduled backups with timer-based automation
    - Multiple configuration profile support
    - Drag-and-drop file addition to configuration
    - Dark mode theme support
    - Enhanced error handling and reporting for production use (v1.0.0+)

Classes:
    - Application: Main application controller implementing MVVM pattern

Functions:
    - main: Main entry point for the application
"""

import sys
from pathlib import Path
from typing import Final

# Add gui directory to Python path for module imports BEFORE importing local modules
sys.path.insert(0, str(Path(__file__).parent / "gui"))

# Import local modules after path is set
from gui.model import DFBUModel
from gui.view import MainWindow
from gui.viewmodel import DFBUViewModel

# Import PySide6 with proper error handling
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("PySide6 is required but not installed.")
    print("Install it with: pip install PySide6")
    sys.exit(1)

__version__: Final[str] = "0.5.2"
PROJECT_NAME: Final[str] = "DFBU GUI"
CONFIG_DIR: Final[Path] = Path.home() / ".config" / "dfbu_gui"
DEFAULT_CONFIG_PATH: Final[Path] = Path(__file__).parent / "data" / "dfbu-config.toml"


class Application:
    """
    Main application controller implementing MVVM pattern.

    Attributes:
        app: QApplication instance
        model: DFBUModel for business logic and state
        viewmodel: DFBUViewModel for presentation logic
        view: MainWindow for UI presentation

    Public methods:
        run: Start the application main loop
        cleanup: Perform cleanup when application exits

    Private methods:
        _initialize_config_directory: Create configuration directory if needed
    """

    def __init__(self) -> None:
        """Initialize the Application with MVVM architecture."""
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(PROJECT_NAME)
        self.app.setApplicationVersion(__version__)
        self.app.setOrganizationName("L3DigitalNet")

        self._initialize_config_directory()

        # Create MVVM components: Model -> ViewModel -> View
        self.model = DFBUModel(DEFAULT_CONFIG_PATH)
        self.viewmodel = DFBUViewModel(self.model)
        self.view = MainWindow(self.viewmodel, __version__)

        # Auto-load configuration if available from previous session
        self._auto_load_config()

    def _initialize_config_directory(self) -> None:
        """Create configuration directory if needed."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _auto_load_config(self) -> None:
        """Auto-load configuration from previous session if available."""
        # Load settings to get previous config path
        settings = self.viewmodel.load_settings()
        config_path = settings.get("config_path", "")

        # If valid config path exists, load it automatically
        if config_path and Path(config_path).exists():
            self.viewmodel.command_load_config()

    def run(self) -> int:
        """
        Start the application main loop.

        Returns:
            Application exit code
        """
        self.view.show()
        exit_code = self.app.exec()
        self.cleanup()
        return exit_code

    def cleanup(self) -> None:
        """Perform cleanup when application exits."""
        pass


def main() -> int:
    """
    Main entry point for the application.

    Returns:
        Application exit code
    """
    app = Application()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
