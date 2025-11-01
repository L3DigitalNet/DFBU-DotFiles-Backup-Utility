"""
Dotfiles Backup Source Package Initialization

Description:
    Package initialization file for the dotfiles backup source
    code. This file makes the src directory a Python package and provides
    centralized imports for dotfiles backup and management modules.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-19-2025
Date Changed: 10-31-2025
License: MIT

Features:
    - Package-level exports for dotfiles backup modules and utilities
    - Centralized import management for backup and restore functions
    - Integration with configuration file management workflows
    - Type hints and proper documentation following PEP standards
    - Support for automated dotfiles backup and synchronization
    - Minimal dependencies using Python standard library

Note:
    This package is specifically designed for Linux dotfiles management. All
    modules assume POSIX-compliant file systems and Linux-specific configuration
    file locations.
"""

# Package metadata
__version__ = "0.5.3"
__author__ = "Chris Purcell"
__email__ = "chris@l3digital.net"

# Package exports will be added here as modules are developed
__all__ = []
