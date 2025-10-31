#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common Library Package Initialization

Description:
    Package initialization file for the common library module.
    This file makes the common_lib directory a Python package and provides
    centralized imports for all utility classes and functions used across
    projects in the repository.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-19-2025
Date Changed: 10-19-2025
License: MIT

Features:
    - AnsiColor class for terminal text formatting and styling
    - CLIMenu class for simple interactive command-line menus
    - PerfMon class for performance monitoring with statistical analysis
    - SemanticVersion class for version management and comparison
    - Package-level exports for common utility classes and functions
    - Centralized import management for shared modules
    - Version information and metadata for the common library
    - Type hints and proper documentation following PEP standards
    - Integration with repository-wide coding standards
    - Minimal dependencies using Python standard library

Note:
    This package contains reusable components designed specifically for Linux
    environments. All modules follow the repository's coding standards with
    comprehensive docstrings, type hints, and proper error handling.
"""

# Package metadata
__version__ = "0.2.0"
__author__ = "Chris Purcell"
__email__ = "chris@l3digital.net"

# Import main classes and functions for easy access
from .cust_class import AnsiColor, CLIMenu, PerfMon
from .version import SemanticVersion, increment_version_string, is_valid_version

# Define what gets imported with "from common_lib import *"
__all__ = [
    "AnsiColor",
    "CLIMenu",
    "PerfMon",
    "SemanticVersion",
    "increment_version_string",
    "is_valid_version",
]
