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
Date Changed: 02-01-2026
License: MIT

Features:
    - MVVM desktop GUI with tab-based interface and threaded operations
    - Window state persistence and responsive user feedback
    - YAML configuration with Application/Description/Paths/Tags structure
    - Interactive dotfile management (add, update, remove)
    - Flexible backup organization with hostname and date-based directories
    - Mirror and compressed archive backup modes with rotation
    - Interactive restore with progress tracking and pre-restore backups
    - Backup verification with size and optional SHA-256 hash checking
    - File size analysis with configurable thresholds and warnings
    - Structured error handling with recovery dialogs
    - Python 3.14 Path.copy() with metadata and symlink support
    - Standard library first approach with minimal dependencies

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - PySide6 for GUI components
    - Additional technical requirements and dependencies

Known Issues:
    - No support for network paths or remote destinations
    - Restore functionality requires exact hostname match in backup directory structure
    - Limited symlink support (follow_symlinks=True only)

Planned Features:
    - Differential backups with change detection based on modification time
    - Enhanced restore capabilities with cross-hostname support
    - Incremental backup support with change detection
    - Network path support for remote backup destinations
    - Scheduled backups with timer-based automation
    - Multiple configuration profile support
    - Drag-and-drop file addition to configuration
    - Dark mode theme support

Classes:
    - Application: Main application controller implementing MVVM pattern

Functions:
    - main: Main entry point for the application
"""

import shutil
import sys
from pathlib import Path
from typing import Final, cast


# Add DFBU directory to Python path for module imports BEFORE importing local modules
# This ensures 'gui' is findable as a package whether running directly or via python -m DFBU
# When frozen by PyInstaller, the import hook handles module resolution automatically
if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).parent))

# Import local modules after path is set
from gui.logging_config import get_logger, setup_default_logging
from gui.model import DFBUModel
from gui.theme_loader import load_theme
from gui.view import MainWindow
from gui.viewmodel import DFBUViewModel


# External dependency: PySide6 required for desktop GUI framework (Qt bindings for Python)
try:
    from PySide6.QtCore import QSettings
    from PySide6.QtGui import QIcon
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("PySide6 is required but not installed.")
    print("Install it with: pip install PySide6")
    sys.exit(1)

# Setup logging
setup_default_logging()
logger = get_logger(__name__)

# Application version
__version__: Final[str] = "1.2.1"
PROJECT_NAME: Final[str] = "DFBU GUI"
# User config directory - writable location for user settings
USER_CONFIG_DIR: Final[Path] = Path.home() / ".config" / "dfbu"

# Bundled config path - read-only defaults inside AppImage/PyInstaller bundle
# When frozen by PyInstaller, data files are bundled under sys._MEIPASS
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    _data_base = Path(cast(str, sys._MEIPASS))
else:
    _data_base = Path(__file__).parent
BUNDLED_CONFIG_PATH: Final[Path] = (_data_base / "data").resolve()

# Determine if running as frozen app (AppImage/PyInstaller)
IS_FROZEN: Final[bool] = getattr(sys, "frozen", False)

# Config path selection:
# - When frozen (AppImage): Use writable user directory (~/.config/dfbu/)
# - When running from source: Use local data directory (DFBU/data/)
DEFAULT_CONFIG_PATH: Final[Path] = USER_CONFIG_DIR if IS_FROZEN else BUNDLED_CONFIG_PATH


def _initialize_user_config() -> None:
    """
    Initialize user config directory with bundled defaults on first run.

    When running as AppImage/frozen app, the bundled config files are read-only.
    This function copies them to the user's writable config directory on first run.

    Files copied: settings.yaml, dotfiles.yaml, session.yaml, .dfbuignore
    """
    if not IS_FROZEN:
        # When running from source, use local data directory directly
        return

    # Create user config directory if it doesn't exist
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # List of config files to copy from bundle to user directory
    config_files = ["settings.yaml", "dotfiles.yaml", "session.yaml", ".dfbuignore"]

    for filename in config_files:
        user_file = USER_CONFIG_DIR / filename
        bundled_file = BUNDLED_CONFIG_PATH / filename

        # Only copy if user file doesn't exist (preserve user customizations)
        if not user_file.exists() and bundled_file.exists():
            try:
                shutil.copy2(bundled_file, user_file)
                logger.info(f"Copied default config: {filename} -> {user_file}")
            except (OSError, PermissionError) as e:
                logger.warning(f"Failed to copy default config {filename}: {e}")


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

        # Load user's preferred theme (read QSettings directly — ViewModel not yet created)
        settings = QSettings("L3DigitalNet", "dfbu_gui_settings")
        saved_theme = str(settings.value("appearance/theme", "dfbu_light"))
        if not load_theme(self.app, saved_theme):
            load_theme(self.app)  # Fallback to default light theme

        icon_path = Path(__file__).parent / "resources" / "icons" / "dfbu.svg"
        if icon_path.exists():
            self.app.setWindowIcon(QIcon(str(icon_path)))

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
        """Create configuration directory and copy defaults if needed."""
        # Initialize user config with bundled defaults (handles AppImage case)
        _initialize_user_config()

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
