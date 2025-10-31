#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DFBU GUI Package Tests

Description:
    Unit tests for gui package initialization, testing package metadata
    and imports.

Author: Test Suite
Date Created: 10-31-2025
License: MIT

Features:
    - Package metadata validation
    - Version string testing
    - Import testing

Requirements:
    - Linux environment
    - Python 3.14+
    - pytest framework
"""

import sys
from pathlib import Path

# Add DFBU directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import gui package
from gui import __version__, __author__, __email__, __all__


class TestGUIPackageMetadata:
    """Test GUI package metadata and initialization."""

    def test_package_has_version(self):
        """Test package defines version string."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_version_format(self):
        """Test version follows semantic versioning format."""
        # Should be in format X.Y.Z
        parts = __version__.split(".")
        assert len(parts) >= 2  # At least major.minor
        assert all(part.isdigit() for part in parts)

    def test_package_has_author(self):
        """Test package defines author information."""
        assert __author__ is not None
        assert isinstance(__author__, str)
        assert len(__author__) > 0

    def test_package_has_email(self):
        """Test package defines email information."""
        assert __email__ is not None
        assert isinstance(__email__, str)
        assert "@" in __email__

    def test_package_has_all_list(self):
        """Test package defines __all__ list."""
        assert __all__ is not None
        assert isinstance(__all__, list)

    def test_package_metadata_types(self):
        """Test all package metadata has correct types."""
        assert isinstance(__version__, str)
        assert isinstance(__author__, str)
        assert isinstance(__email__, str)
        assert isinstance(__all__, list)
