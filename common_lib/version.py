#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic Versioning Utility

Description:
    A simplified semantic versioning utility that manages MAJOR.MINOR.PATCH
    version format only. Provides version parsing, comparison, incrementing,
    and validation following semantic versioning standards. Designed for
    consistent version management across all repository projects with
    streamlined automation capabilities.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 10-20-2025
Date Changed: 10-29-2025
License: MIT

Features:
    - MAJOR.MINOR.PATCH semantic version parsing and validation
    - Automatic version incrementing with 0.0.1 increment support
    - Version comparison and sorting capabilities
    - String representation and parsing from various formats
    - Integration with project __version__ variables
    - Changelog-compatible version tracking
    - Python standard library first approach with minimal dependencies
    - Clean architecture with confident design patterns

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - No external dependencies - standard library only

Known Issues:
    - None currently identified

Planned Features:
    - Additional version comparison utilities as needed
    - Enhanced integration with project management tools
"""

from __future__ import annotations

import re
from typing import Final
from dataclasses import dataclass

# Version information
__version__: Final[str] = "0.1.0"


@dataclass(frozen=True)
class SemanticVersion:
    """
    Represents a semantic version following MAJOR.MINOR.PATCH format.

    Attributes:
        major: major version number (breaking changes)
        minor: minor version number (new features)
        patch: patch version number (bug fixes)

    Public methods:
        parse: create version from string
        increment_patch: increment patch version by 1
        increment_minor: increment minor version by 1, reset patch to 0
        increment_major: increment major version by 1, reset minor and patch to 0
        increment: increment version by 0.0.1 (patch)
        new_project_version: create initial version for new projects
    """

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        """
        Return string representation of version.

        Returns:
            version string in MAJOR.MINOR.PATCH format
        """
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, other: SemanticVersion) -> bool:
        """
        Compare if this version is less than another.

        Args:
            other: version to compare against

        Returns:
            true if this version is less than other
        """
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __le__(self, other: SemanticVersion) -> bool:
        """
        Compare if this version is less than or equal to another.

        Args:
            other: version to compare against

        Returns:
            true if this version is less than or equal to other
        """
        return (self.major, self.minor, self.patch) <= (
            other.major,
            other.minor,
            other.patch,
        )

    def __gt__(self, other: SemanticVersion) -> bool:
        """
        Compare if this version is greater than another.

        Args:
            other: version to compare against

        Returns:
            true if this version is greater than other
        """
        return (self.major, self.minor, self.patch) > (
            other.major,
            other.minor,
            other.patch,
        )

    def __ge__(self, other: SemanticVersion) -> bool:
        """
        Compare if this version is greater than or equal to another.

        Args:
            other: version to compare against

        Returns:
            true if this version is greater than or equal to other
        """
        return (self.major, self.minor, self.patch) >= (
            other.major,
            other.minor,
            other.patch,
        )

    @classmethod
    def parse(cls, version_string: str) -> SemanticVersion:
        """
        Parse a version string into a SemanticVersion object.

        Args:
            version_string: string representation of version

        Returns:
            SemanticVersion object

        Raises:
            ValueError: if version string is invalid
        """
        # Remove any leading 'v' if present
        version_string = version_string.lstrip("v")

        # Pattern for MAJOR.MINOR.PATCH
        pattern = r"^(\d+)\.(\d+)\.(\d+)$"
        match = re.match(pattern, version_string)

        if not match:
            raise ValueError(
                f"Invalid version format: {version_string}. Must be MAJOR.MINOR.PATCH"
            )

        major, minor, patch = map(int, match.groups())
        return cls(major=major, minor=minor, patch=patch)

    def increment_patch(self) -> SemanticVersion:
        """
        Increment the patch version by 1.

        Returns:
            new SemanticVersion with incremented patch
        """
        return SemanticVersion(major=self.major, minor=self.minor, patch=self.patch + 1)

    def increment_minor(self) -> SemanticVersion:
        """
        Increment the minor version by 1 and reset patch to 0.

        Returns:
            new SemanticVersion with incremented minor
        """
        return SemanticVersion(major=self.major, minor=self.minor + 1, patch=0)

    def increment_major(self) -> SemanticVersion:
        """
        Increment the major version by 1 and reset minor and patch to 0.

        Returns:
            new SemanticVersion with incremented major
        """
        return SemanticVersion(major=self.major + 1, minor=0, patch=0)

    def increment(self) -> SemanticVersion:
        """
        Increment version by 0.0.1 (patch increment).

        Returns:
            new SemanticVersion with incremented patch
        """
        return self.increment_patch()

    @classmethod
    def new_project_version(cls) -> SemanticVersion:
        """
        Create initial version for new projects.

        Returns:
            SemanticVersion set to 0.0.1
        """
        return cls(major=0, minor=0, patch=1)


def increment_version_string(version_string: str) -> str:
    """
    Increment a version string by 0.0.1.

    Args:
        version_string: current version as string

    Returns:
        incremented version string
    """
    version = SemanticVersion.parse(version_string)
    incremented = version.increment()
    return str(incremented)


def is_valid_version(version_string: str) -> bool:
    """
    Check if a version string is valid MAJOR.MINOR.PATCH format.

    Args:
        version_string: version string to validate

    Returns:
        true if version string is valid
    """
    try:
        SemanticVersion.parse(version_string)
        return True
    except ValueError:
        return False
