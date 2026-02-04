#!/usr/bin/env python3
"""
DFBU YAML Configuration Loader Module

Description:
    Handles loading and saving YAML configuration files for DFBU.
    Supports three separate configuration files: settings.yaml,
    dotfiles.yaml, and session.yaml.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 02-01-2026
Date Changed: 02-01-2026
License: MIT

Features:
    - Load and save settings configuration (paths and options)
    - Load and save dotfiles library (application configurations)
    - Load and save session state (exclusions)
    - Uses ruamel.yaml for round-trip safe YAML handling
    - Preserves comments in YAML files
    - Validation of configuration structure

Requirements:
    - Python 3.14+ for latest language features
    - ruamel.yaml for YAML handling
    - common_types module for TypedDict definitions

Classes:
    - YAMLConfigLoader: Load and save YAML configuration files
"""

from pathlib import Path
from typing import Any

from core.common_types import (
    DotFileDict,
    SessionDict,
    SettingsDict,
)
from ruamel.yaml import YAML


class YAMLConfigLoader:
    """
    Load and save YAML configuration files for DFBU.

    Handles three separate configuration files:
    - settings.yaml: Backup paths and options
    - dotfiles.yaml: Dotfile library definitions
    - session.yaml: Session-specific exclusions

    Uses ruamel.yaml for round-trip safe YAML handling that preserves
    comments and formatting when modifying files.

    Args:
        config_dir: Directory containing configuration files (Path or str)

    Properties:
        settings_path: Path to settings.yaml
        dotfiles_path: Path to dotfiles.yaml
        session_path: Path to session.yaml

    Methods:
        load_settings: Load settings from YAML file
        load_dotfiles: Load dotfiles library from YAML file
        load_session: Load session exclusions from YAML file
        save_settings: Save settings to YAML file
        save_dotfiles: Save dotfiles library to YAML file
        save_session: Save session exclusions to YAML file
    """

    def __init__(self, config_dir: Path | str) -> None:
        """
        Initialize YAMLConfigLoader with configuration directory.

        Args:
            config_dir: Directory containing configuration files
        """
        self._config_dir = Path(config_dir)
        self._yaml = YAML()
        self._yaml.preserve_quotes = True
        self._yaml.default_flow_style = False

    @property
    def settings_path(self) -> Path:
        """Path to settings.yaml configuration file."""
        return self._config_dir / "settings.yaml"

    @property
    def dotfiles_path(self) -> Path:
        """Path to dotfiles.yaml configuration file."""
        return self._config_dir / "dotfiles.yaml"

    @property
    def session_path(self) -> Path:
        """Path to session.yaml configuration file."""
        return self._config_dir / "session.yaml"

    def load_settings(self) -> SettingsDict:
        """
        Load settings from settings.yaml file.

        Returns:
            SettingsDict containing paths and options configuration

        Raises:
            FileNotFoundError: If settings.yaml does not exist
            ValueError: If settings file has invalid structure
        """
        if not self.settings_path.exists():
            raise FileNotFoundError(f"Settings file not found: {self.settings_path}")

        with self.settings_path.open("r", encoding="utf-8") as f:
            data = self._yaml.load(f)

        if data is None:
            raise ValueError("Settings file is empty")

        self._validate_settings(data)

        return data  # type: ignore[no-any-return]  # ruamel.yaml returns Any

    def load_dotfiles(self) -> dict[str, DotFileDict]:
        """
        Load dotfiles library from dotfiles.yaml file.

        Returns:
            Dictionary mapping application names to DotFileDict entries

        Raises:
            FileNotFoundError: If dotfiles.yaml does not exist
        """
        if not self.dotfiles_path.exists():
            raise FileNotFoundError(f"Dotfiles file not found: {self.dotfiles_path}")

        with self.dotfiles_path.open("r", encoding="utf-8") as f:
            data = self._yaml.load(f)

        if data is None:
            return {}

        # Validate each dotfile entry
        for app_name, dotfile_data in data.items():
            self._validate_dotfile(app_name, dotfile_data)

        return dict(data)

    def load_session(self) -> SessionDict:
        """
        Load session exclusions from session.yaml file.

        Returns empty session if file does not exist.

        Returns:
            SessionDict containing excluded application list
        """
        if not self.session_path.exists():
            return {"excluded": []}

        with self.session_path.open("r", encoding="utf-8") as f:
            data = self._yaml.load(f)

        if data is None:
            return {"excluded": []}

        excluded = data.get("excluded", [])
        if excluded is None:
            excluded = []

        return {"excluded": list(excluded)}

    def save_settings(self, settings: SettingsDict) -> None:
        """
        Save settings to settings.yaml file.

        Args:
            settings: SettingsDict containing paths and options configuration
        """
        self._config_dir.mkdir(parents=True, exist_ok=True)

        with self.settings_path.open("w", encoding="utf-8") as f:
            self._yaml.dump(dict(settings), f)

    def save_dotfiles(self, dotfiles: dict[str, DotFileDict]) -> None:
        """
        Save dotfiles library to dotfiles.yaml file.

        Args:
            dotfiles: Dictionary mapping application names to DotFileDict entries
        """
        self._config_dir.mkdir(parents=True, exist_ok=True)

        with self.dotfiles_path.open("w", encoding="utf-8") as f:
            self._yaml.dump(dict(dotfiles), f)

    def save_session(self, session: SessionDict) -> None:
        """
        Save session exclusions to session.yaml file.

        Args:
            session: SessionDict containing excluded application list
        """
        self._config_dir.mkdir(parents=True, exist_ok=True)

        with self.session_path.open("w", encoding="utf-8") as f:
            self._yaml.dump(dict(session), f)

    def _validate_settings(self, data: dict[str, Any]) -> None:
        """
        Validate settings configuration structure.

        Args:
            data: Raw settings data from YAML file

        Raises:
            ValueError: If required sections or fields are missing
        """
        if "paths" not in data:
            raise ValueError("Settings missing required 'paths' section")
        if "options" not in data:
            raise ValueError("Settings missing required 'options' section")

        paths = data["paths"]
        required_paths = ["mirror_dir", "archive_dir", "restore_backup_dir"]
        for field in required_paths:
            if field not in paths:
                raise ValueError(f"Settings paths missing required field: {field}")

        options = data["options"]
        required_options = [
            "mirror",
            "archive",
            "hostname_subdir",
            "date_subdir",
            "archive_format",
            "archive_compression_level",
            "rotate_archives",
            "max_archives",
            "pre_restore_backup",
            "max_restore_backups",
        ]
        for field in required_options:
            if field not in options:
                raise ValueError(f"Settings options missing required field: {field}")

    def _validate_dotfile(self, app_name: str, data: dict[str, Any]) -> None:
        """
        Validate individual dotfile entry.

        Args:
            app_name: Name of the application
            data: Raw dotfile data from YAML file

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if "description" not in data:
            raise ValueError(f"Dotfile '{app_name}' missing required 'description'")

        if "path" not in data and "paths" not in data:
            raise ValueError(f"Dotfile '{app_name}' must have either 'path' or 'paths'")
