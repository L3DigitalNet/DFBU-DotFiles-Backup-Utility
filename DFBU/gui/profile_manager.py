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
from typing import Any

from ruamel.yaml import YAML

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

        # Initialize YAML handler
        self._yaml: YAML = YAML()
        self._yaml.preserve_quotes = True
        self._yaml.default_flow_style = False

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

    def load_profiles(self) -> tuple[bool, str]:
        """
        Load profiles from YAML configuration file.

        Returns:
            Tuple of (success, error_message)
        """
        profiles_file = self.config_path / "profiles.yaml"

        if not profiles_file.exists():
            # No profiles file is valid - just means no saved profiles
            return True, ""

        try:
            with profiles_file.open("r", encoding="utf-8") as f:
                data = self._yaml.load(f)

            if data is None:
                return True, ""

            # Extract active profile setting
            self._active_profile = data.pop("active_profile", None)

            # Remaining keys are profile names
            for name, profile_data in data.items():
                if isinstance(profile_data, dict):
                    self._profiles[name] = ProfileDict(
                        name=name,
                        description=profile_data.get("description", ""),
                        excluded=profile_data.get("excluded", []),
                        options_overrides=profile_data.get("options_overrides", {}),
                        created_at=profile_data.get("created_at", ""),
                        modified_at=profile_data.get("modified_at", ""),
                    )

            return True, ""

        except (OSError, IOError) as e:
            return False, f"Failed to load profiles: {e}"

    def save_profiles(self) -> tuple[bool, str]:
        """
        Save profiles to YAML configuration file.

        Returns:
            Tuple of (success, error_message)
        """
        profiles_file = self.config_path / "profiles.yaml"

        try:
            # Build data structure
            data: dict[str, Any] = {}

            for name, profile in self._profiles.items():
                data[name] = {
                    "description": profile["description"],
                    "excluded": profile["excluded"],
                    "options_overrides": profile["options_overrides"],
                    "created_at": profile["created_at"],
                    "modified_at": profile["modified_at"],
                }

            if self._active_profile:
                data["active_profile"] = self._active_profile

            with profiles_file.open("w", encoding="utf-8") as f:
                self._yaml.dump(data, f)

            return True, ""

        except (OSError, IOError) as e:
            return False, f"Failed to save profiles: {e}"
