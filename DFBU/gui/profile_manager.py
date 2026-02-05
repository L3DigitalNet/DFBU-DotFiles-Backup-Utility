"""
DFBU ProfileManager - Backup Profile Management Component

Description:
    Handles named backup profiles allowing users to save and switch
    between different dotfile selection and option configurations.

Author: Chris Purcell
Date Created: 2026-02-05
License: MIT
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.common_types import ProfileDict


class ProfileManager:
    """
    Manages backup profiles for different configurations.

    Profiles allow users to save named presets of excluded dotfiles
    and option overrides for quick switching between backup configurations.

    Attributes:
        config_path: Path to configuration directory
        _profiles: Dictionary of profile name -> ProfileDict
        _active_profile: Name of currently active profile (None = default)
    """

    def __init__(self, config_path: Path) -> None:
        """
        Initialize ProfileManager.

        Args:
            config_path: Path to configuration directory for profiles.yaml
        """
        self.config_path: Path = config_path
        self._profiles: dict[str, ProfileDict] = {}
        self._active_profile: str | None = None

    def get_profile_count(self) -> int:
        """
        Get number of saved profiles.

        Returns:
            Number of profiles in storage
        """
        return len(self._profiles)

    def get_active_profile_name(self) -> str | None:
        """
        Get name of currently active profile.

        Returns:
            Active profile name, or None if using default settings
        """
        return self._active_profile
