#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DFBU GUI - Main Application Entry Point

Description:
    Main entry point for DFBU GUI implementing MVVM architecture for desktop
    backup and restore operations with PySide6.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 10-30-2025
License: MIT

Features:
    - MVVM architectural pattern with clean separation of concerns
    - PySide6 desktop GUI with tab-based interface
    - Threaded operations to prevent UI blocking
    - Window state persistence through ViewModel
    - Signal-based reactive data binding
    - Configuration loading from TOML files
    - Mirror and archive backup operations
    - File restoration from backup directories
    - Python standard library first approach with minimal dependencies
    - Clean architecture with confident design patterns

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - PySide6 framework for modern desktop GUI
    - Custom libraries located at ../common_lib/
    - Standard library modules: pathlib, sys

Classes:
    - Application: Main application controller implementing MVVM pattern

Functions:
    - main: Main entry point for the application
"""

import sys
from pathlib import Path
from typing import Final

# Add src directory to Python path for module imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from model import DFBUModel
from viewmodel import DFBUViewModel
from view import MainWindow

try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    print("PySide6 is required but not installed.")
    print("Install it with: pip install PySide6")
    sys.exit(1)

__version__: Final[str] = "0.3.0"
PROJECT_NAME: Final[str] = "DFBU GUI"
CONFIG_DIR: Final[Path] = Path.home() / ".config" / "dfbu_gui"
DEFAULT_CONFIG_PATH: Final[Path] = (
    Path(__file__).parent / "data" / "dfbu-config.toml"
)


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

    def _initialize_config_directory(self) -> None:
        """Create configuration directory if needed."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)

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
