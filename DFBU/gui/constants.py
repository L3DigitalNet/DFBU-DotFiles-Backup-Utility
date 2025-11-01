"""
GUI Configuration Constants for DFBU

Description:
    Centralized configuration constants for GUI elements including UI dimensions,
    timeouts, and other configurable values. Extracted from hardcoded values in
    view.py to improve maintainability and configurability.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 11-01-2025
License: MIT

Features:
    - Centralized UI configuration constants
    - Timeout and duration settings
    - Dialog dimension specifications
    - Standard library only (no external dependencies)

Requirements:
    - Python 3.14+ for latest typing features
"""

from typing import Final


# =============================================================================
# Status Bar Configuration
# =============================================================================

# Duration (in milliseconds) to display status bar messages before auto-clear
STATUS_MESSAGE_TIMEOUT_MS: Final[int] = 3000  # 3 seconds


# =============================================================================
# Dialog Dimensions
# =============================================================================

# Minimum width for add/update dotfile dialog (pixels)
MIN_DIALOG_WIDTH: Final[int] = 600

# Minimum height for add/update dotfile dialog (pixels)
MIN_DIALOG_HEIGHT: Final[int] = 400


# =============================================================================
# Window Configuration
# =============================================================================

# Default minimum main window width (pixels)
MIN_MAIN_WINDOW_WIDTH: Final[int] = 1024

# Default minimum main window height (pixels)
MIN_MAIN_WINDOW_HEIGHT: Final[int] = 768
