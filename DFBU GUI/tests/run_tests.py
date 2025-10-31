#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite Summary for DFBU GUI

Description:
    Entry point for running all DFBU GUI tests. Provides convenient test
    execution and summary reporting for the complete test suite.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-30-2025
Date Changed: 10-30-2025
License: MIT

Usage:
    Run all tests:
        python run_tests.py

    Run specific test file:
        pytest tests/test_model_core.py -v

    Run with coverage:
        pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

Features:
    - Comprehensive test coverage for DFBU GUI MVVM architecture
    - Model layer: Core functionality, configuration, dotfile management, file operations
    - ViewModel layer: Commands, worker threads, signal emissions
    - Integration testing between MVVM layers
    - Type safety validation for TypedDict structures

Test Files:
    - test_model_core.py: Core model functionality and statistics
    - test_model_config.py: Configuration loading, validation, and saving
    - test_model_dotfiles.py: Dotfile management operations (add/update/remove/toggle)
    - test_model_file_operations.py: File system operations and copying
    - test_viewmodel_commands.py: ViewModel command patterns
    - test_viewmodel_workers.py: Worker thread operations
    - test_mvvm_integration.py: MVVM layer integration
    - test_type_safety.py: Type hint validation

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - pytest framework for testing
    - pytest-cov for coverage reporting
"""

import sys
from pathlib import Path

import pytest


def main() -> int:
    """
    Run all tests with coverage reporting.

    Returns:
        Exit code from pytest
    """
    # Add project source to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src"))

    # Configure pytest arguments
    args = [
        str(project_root / "tests"),
        "-v",  # Verbose output
        "--tb=short",  # Shorter traceback format
        "-ra",  # Show summary of all test outcomes
        # Coverage options (uncomment when ready to measure coverage)
        # "--cov=src",
        # "--cov-report=html",
        # "--cov-report=term-missing",
    ]

    # Run tests
    return pytest.main(args)


if __name__ == "__main__":
    sys.exit(main())
