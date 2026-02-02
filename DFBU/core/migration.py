#!/usr/bin/env python3
"""
DFBU TOML to YAML Configuration Migration Module

Description:
    Migrates legacy TOML configuration format to the new YAML format.
    Converts a single dfbu-config.toml into three separate YAML files:
    - settings.yaml: Backup paths and options
    - dotfiles.yaml: Application dotfile library
    - session.yaml: Session-specific exclusions

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 02-01-2026
Date Changed: 02-01-2026
License: MIT

Features:
    - Load and parse legacy TOML configuration
    - Extract and save settings (paths + options) to settings.yaml
    - Extract and save dotfiles library to dotfiles.yaml
    - Create empty session.yaml with exclusions list
    - Consolidate duplicate application entries by merging paths
    - Clean up redundant description prefixes (KDE, GNOME, etc.)
    - Create backup of original TOML file before migration

Requirements:
    - Python 3.14+ for latest language features
    - tomllib for TOML parsing (stdlib in 3.11+)
    - ruamel.yaml for YAML output with preserved formatting

Classes:
    - ConfigMigrator: Main migration class

Functions:
    - migrate_config: Convenience function for migration
"""

import shutil
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML


class ConfigMigrator:
    """
    Migrate legacy TOML configuration to YAML format.

    Converts dfbu-config.toml into settings.yaml, dotfiles.yaml, and
    session.yaml. Handles duplicate application entries by merging their
    paths and cleans up redundant description prefixes.

    Args:
        toml_path: Path to the source TOML configuration file
        output_dir: Directory where YAML files will be created

    Methods:
        migrate: Perform the complete migration process

    Example:
        migrator = ConfigMigrator(Path("config.toml"), Path("output/"))
        migrator.migrate()
    """

    # Prefixes to clean from descriptions when they match the application name
    _DESCRIPTION_PREFIXES = [
        "KDE ",
        "GNOME ",
        "Xfce ",
        "GNU ",
        "Mozilla ",
        "Google ",
        "Microsoft ",
    ]

    def __init__(self, toml_path: Path | str, output_dir: Path | str) -> None:
        """
        Initialize ConfigMigrator with source and destination paths.

        Args:
            toml_path: Path to source TOML configuration file
            output_dir: Directory for output YAML files
        """
        self._toml_path = Path(toml_path)
        self._output_dir = Path(output_dir)
        self._yaml = YAML()
        self._yaml.preserve_quotes = True
        self._yaml.default_flow_style = False
        self._yaml.indent(mapping=2, sequence=4, offset=2)

    def migrate(self) -> None:
        """
        Perform complete TOML to YAML migration.

        Creates backup of original TOML, then generates:
        - settings.yaml with paths and options
        - dotfiles.yaml with application library
        - session.yaml with empty exclusions

        Raises:
            FileNotFoundError: If TOML file does not exist
        """
        # Load the source TOML
        toml_data = self._load_toml()

        # Create output directory if needed
        self._output_dir.mkdir(parents=True, exist_ok=True)

        # Backup original TOML
        self._backup_toml()

        # Extract and save settings
        settings = self._extract_settings(toml_data)
        self._save_yaml(settings, self._output_dir / "settings.yaml")

        # Extract and save dotfiles
        dotfiles = self._extract_dotfiles(toml_data)
        self._save_yaml(dotfiles, self._output_dir / "dotfiles.yaml")

        # Create empty session
        session: dict[str, list[str]] = {"excluded": []}
        self._save_yaml(session, self._output_dir / "session.yaml")

    def _load_toml(self) -> dict[str, Any]:
        """
        Load and parse TOML configuration file.

        Returns:
            Parsed TOML data as dictionary

        Raises:
            FileNotFoundError: If TOML file does not exist
        """
        if not self._toml_path.exists():
            raise FileNotFoundError(f"TOML file not found: {self._toml_path}")

        with self._toml_path.open("rb") as f:
            return tomllib.load(f)

    def _extract_settings(self, toml_data: dict[str, Any]) -> dict[str, Any]:
        """
        Extract paths and options sections from TOML data.

        Args:
            toml_data: Parsed TOML configuration data

        Returns:
            Dictionary containing paths and options for settings.yaml
        """
        settings: dict[str, Any] = {}

        if "paths" in toml_data:
            settings["paths"] = dict(toml_data["paths"])

        if "options" in toml_data:
            settings["options"] = dict(toml_data["options"])

        return settings

    def _extract_dotfiles(self, toml_data: dict[str, Any]) -> dict[str, Any]:
        """
        Extract and consolidate dotfile entries from TOML data.

        Processes [[dotfile]] entries, consolidating duplicates by merging
        their paths and cleaning up descriptions.

        Args:
            toml_data: Parsed TOML configuration data

        Returns:
            Dictionary mapping application names to dotfile configs
        """
        dotfiles: dict[str, dict[str, Any]] = {}
        entries = toml_data.get("dotfile", [])

        for entry in entries:
            app_name = entry.get("application", "Unknown")
            paths = self._get_paths_from_entry(entry)
            description = self._clean_description(
                entry.get("description", ""), app_name
            )

            if app_name in dotfiles:
                # Consolidate duplicate entry - merge paths
                existing_paths = self._get_paths_from_dotfile(dotfiles[app_name])
                # Add new paths, avoiding duplicates
                for path in paths:
                    if path not in existing_paths:
                        existing_paths.append(path)
                # Update the entry with merged paths
                if len(existing_paths) == 1:
                    dotfiles[app_name]["path"] = existing_paths[0]
                    if "paths" in dotfiles[app_name]:
                        del dotfiles[app_name]["paths"]
                else:
                    dotfiles[app_name]["paths"] = existing_paths
                    if "path" in dotfiles[app_name]:
                        del dotfiles[app_name]["path"]
            else:
                # New entry
                dotfile_entry: dict[str, Any] = {"description": description}

                if len(paths) == 1:
                    dotfile_entry["path"] = paths[0]
                else:
                    dotfile_entry["paths"] = paths

                dotfiles[app_name] = dotfile_entry

        return dotfiles

    def _get_paths_from_entry(self, entry: dict[str, Any]) -> list[str]:
        """
        Extract paths from a TOML dotfile entry.

        Handles both single path and multiple paths configurations.

        Args:
            entry: Single [[dotfile]] entry from TOML

        Returns:
            List of path strings
        """
        if "paths" in entry:
            return [str(p).strip() for p in entry["paths"]]
        elif "path" in entry:
            return [str(entry["path"]).strip()]
        return []

    def _get_paths_from_dotfile(self, dotfile: dict[str, Any]) -> list[str]:
        """
        Extract paths from a processed dotfile dictionary.

        Args:
            dotfile: Dotfile entry dictionary

        Returns:
            List of path strings
        """
        if "paths" in dotfile:
            return list(dotfile["paths"])
        elif "path" in dotfile:
            return [dotfile["path"]]
        return []

    def _clean_description(self, description: str, app_name: str) -> str:
        """
        Clean redundant prefixes from description text.

        Removes common prefixes like "KDE ", "GNOME ", etc. when they
        match or are redundant with the application name.

        Args:
            description: Original description text
            app_name: Application name for context

        Returns:
            Cleaned description string
        """
        cleaned = description

        for prefix in self._DESCRIPTION_PREFIXES:
            # Check if description starts with the prefix
            if cleaned.startswith(prefix):
                # Check if the app name also starts with the prefix (redundant)
                if app_name.startswith(prefix.strip()):
                    # Remove the prefix from description
                    cleaned = cleaned[len(prefix):]
                    break
                # Also remove if the next word matches app name (e.g., "KDE Konsole")
                remaining = cleaned[len(prefix):]
                first_word = remaining.split()[0] if remaining.split() else ""
                if first_word and app_name.startswith(first_word):
                    cleaned = remaining
                    break

        return cleaned

    def _save_yaml(self, data: dict[str, Any], output_path: Path) -> None:
        """
        Save data to YAML file with proper formatting.

        Args:
            data: Data to save
            output_path: Destination file path
        """
        with output_path.open("w", encoding="utf-8") as f:
            self._yaml.dump(data, f)

    def _backup_toml(self) -> None:
        """
        Create backup of original TOML file in output directory.

        Backup filename includes timestamp for uniqueness.
        """
        if not self._toml_path.exists():
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{self._toml_path.name}.bak.{timestamp}"
        backup_path = self._output_dir / backup_name

        shutil.copy2(self._toml_path, backup_path)


def migrate_config(toml_path: Path | str, output_dir: Path | str) -> bool:
    """
    Convenience function to migrate TOML configuration to YAML.

    Creates output directory if it doesn't exist, performs migration,
    and returns success status.

    Args:
        toml_path: Path to source TOML configuration file
        output_dir: Directory for output YAML files

    Returns:
        True if migration completed successfully

    Example:
        success = migrate_config("config.toml", "output/")
        if success:
            print("Migration complete!")
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    migrator = ConfigMigrator(toml_path, output_path)
    migrator.migrate()

    return True
