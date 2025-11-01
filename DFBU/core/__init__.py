"""
Core Utilities for DFBU

Description:
    Shared core utilities used by both CLI and GUI applications.
    Contains type definitions and validation logic.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-01-2025
Date Changed: 11-01-2025
License: MIT

Modules:
    - common_types: Shared TypedDict definitions
    - validation: Configuration validation logic
"""

from core.common_types import DotFileDict, OptionsDict
from core.validation import ConfigValidator


__all__ = ["ConfigValidator", "DotFileDict", "OptionsDict"]
