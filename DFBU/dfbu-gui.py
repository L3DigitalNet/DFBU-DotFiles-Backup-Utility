#!/usr/bin/env python3
r"""
DFBU GUI - Dotfiles Backup Utility (Desktop Edition)

Description:
    Desktop application for comprehensive file backup and restoration with a
    graphical user interface. Built on MVVM architecture using PySide6,
    providing an intuitive way to manage configuration file backups.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-18-2025
Date Changed: 11-03-2025
License: MIT

Features:
    - MVVM desktop GUI with tab-based interface and threaded operations
    - Window state persistence and responsive user feedback
    - TOML configuration with Category/Subcategory/Application structure
    - Interactive dotfile management (add, update, remove)
    - Flexible backup organization with hostname and date-based directories
    - Mirror and compressed archive backup modes with rotation
    - Interactive restore with progress tracking
    - Python 3.14 Path.copy() with metadata and symlink support
    - Standard library first approach with minimal dependencies

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - PySide6 for GUI components
    - Additional technical requirements and dependencies

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
from gui.logging_config import get_logger, setup_default_logging
from gui.model import DFBUModel
from gui.view import MainWindow
from gui.viewmodel import DFBUViewModel


# External dependency: PySide6 required for desktop GUI framework (Qt bindings for Python)
try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("PySide6 is required but not installed.")
    print("Install it with: pip install PySide6")
    sys.exit(1)

# Setup logging
setup_default_logging()
logger = get_logger(__name__)

# Application version
__version__: Final[str] = "0.6.0"
PROJECT_NAME: Final[str] = "DFBU GUI"
CONFIG_DIR: Final[Path] = Path.home() / ".config" / "dfbu_gui"
# Use relative path for portability - resolve to absolute at runtime
DEFAULT_CONFIG_PATH: Final[Path] = (
    Path(__file__).parent / "data" / "dfbu-config.toml"
).resolve()


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
        logger.info(f"Initializing {PROJECT_NAME} v{__version__}")

        self.app = QApplication(sys.argv)
        self.app.setApplicationName(PROJECT_NAME)
        self.app.setApplicationVersion(__version__)
        self.app.setOrganizationName("L3DigitalNet")

        self._initialize_config_directory()

        try:
            # Create MVVM components: Model -> ViewModel -> View
            logger.debug("Creating Model with config path: %s", DEFAULT_CONFIG_PATH)
            self.model = DFBUModel(DEFAULT_CONFIG_PATH)

            logger.debug("Creating ViewModel")
            self.viewmodel = DFBUViewModel(self.model)

            logger.debug("Creating Main Window")
            self.view = MainWindow(self.viewmodel, __version__)

            # Load configuration from default path if available
            self._load_config_if_available()

            logger.info("Application initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize application: %s", e, exc_info=True)
            raise

    def _initialize_config_directory(self) -> None:
        """Create configuration directory if needed."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config_if_available(self) -> None:
        """Load configuration from default path on startup."""
        if DEFAULT_CONFIG_PATH.exists():
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
