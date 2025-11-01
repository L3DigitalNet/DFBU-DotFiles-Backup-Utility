#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DFBU Config Consolidator - Merge Duplicate Application Entries

Description:
    Analyzes TOML configuration files for duplicate application entries
    and consolidates them into single entries with multiple paths.
    Preserves all metadata (category, subcategory, description, size, etc.)
    and ensures backward compatibility.

Author: AI Assistant
Email: N/A
GitHub: https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility
Date Created: 10-31-2025
Date Changed: 10-31-2025
License: MIT

Features:
    - Detects duplicate application entries across config file
    - Consolidates paths into single entries using multiple paths feature
    - Preserves all metadata from original entries
    - Creates backup of original file before modification
    - Reports statistics on consolidation results
    - Standard library first approach (tomllib, tomli_w)

Requirements:
    - Linux environment
    - Python 3.14+ for latest language features
    - tomli_w for TOML writing

Known Issues:
    - None currently identified

Planned Features:
    - Interactive mode for reviewing changes before applying
    - Dry-run mode to preview consolidation without modifying file

Functions:
    - load_config(): Load TOML configuration file
    - find_duplicates(): Identify duplicate application entries
    - consolidate_entries(): Merge duplicate entries into single entries
    - save_config(): Write consolidated configuration to file
    - create_backup(): Create timestamped backup of original file
    - main(): Command-line entry point
"""

import sys
import tomllib
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


try:
    import tomli_w
except ImportError:
    print("Error: tomli_w package required for TOML writing")
    print("Install with: pip install tomli-w")
    sys.exit(1)


def load_config(config_path: Path) -> dict[str, Any]:
    """
    Load TOML configuration file.

    Args:
        config_path: Path to TOML configuration file

    Returns:
        Parsed configuration dictionary
    """
    with open(config_path, "rb") as f:
        return tomllib.load(f)


def find_duplicates(config: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """
    Identify duplicate application entries in configuration.

    Args:
        config: Parsed configuration dictionary

    Returns:
        Dictionary mapping application names to list of their entries
    """
    # Group dotfiles by application name
    app_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for dotfile in config.get("dotfile", []):
        app_name = dotfile.get("application", "")
        if app_name:
            app_groups[app_name].append(dotfile)

    # Filter to only duplicates (2+ entries)
    duplicates = {
        app: entries for app, entries in app_groups.items() if len(entries) > 1
    }

    return duplicates


def consolidate_entries(
    duplicates: dict[str, list[dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    """
    Merge duplicate entries into single entries with multiple paths.

    Args:
        duplicates: Dictionary of duplicate application entries

    Returns:
        Dictionary mapping application names to consolidated entries
    """
    consolidated: dict[str, dict[str, Any]] = {}

    for app_name, entries in duplicates.items():
        # Start with first entry as base
        merged = entries[0].copy()

        # Collect all paths from all entries
        all_paths: list[str] = []

        for entry in entries:
            # Handle both legacy "path" and new "paths" format
            if "paths" in entry:
                all_paths.extend(entry["paths"])
            elif "path" in entry:
                all_paths.append(entry["path"])

        # Remove duplicates while preserving order
        unique_paths = list(dict.fromkeys(all_paths))

        # Update merged entry with consolidated paths
        if "path" in merged:
            del merged["path"]
        merged["paths"] = unique_paths

        consolidated[app_name] = merged

    return consolidated


def create_backup(config_path: Path) -> Path:
    """
    Create timestamped backup of original configuration file.

    Args:
        config_path: Path to configuration file

    Returns:
        Path to backup file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = (
        config_path.parent
        / f"{config_path.stem}_backup_{timestamp}{config_path.suffix}"
    )

    # Copy original file to backup
    backup_path.write_bytes(config_path.read_bytes())

    return backup_path


def save_config(config_path: Path, config: dict[str, Any]) -> None:
    """
    Write consolidated configuration to file.

    Args:
        config_path: Path to configuration file
        config: Configuration dictionary to write
    """
    with open(config_path, "wb") as f:
        tomli_w.dump(config, f)


def main() -> int:
    """
    Main entry point for configuration consolidation.

    Returns:
        Exit code (0=success, 1=error)
    """
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python consolidate_config.py <config_file>")
        print("Example: python consolidate_config.py data/dfbu-config.toml")
        return 1

    config_path = Path(sys.argv[1])

    # Validate config file exists
    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        return 1

    print(f"Loading configuration from: {config_path}")

    # Load configuration
    config = load_config(config_path)
    original_count = len(config.get("dotfile", []))

    print(f"Found {original_count} total dotfile entries")

    # Find duplicates
    duplicates = find_duplicates(config)
    duplicate_count = sum(len(entries) for entries in duplicates.values())

    if not duplicates:
        print("No duplicate entries found - configuration already optimal")
        return 0

    print(f"\nFound {len(duplicates)} applications with duplicate entries:")
    for app_name, entries in sorted(duplicates.items()):
        print(f"  - {app_name}: {len(entries)} entries")

    # Create backup before modifying
    print("\nCreating backup...")
    backup_path = create_backup(config_path)
    print(f"Backup saved to: {backup_path}")

    # Consolidate duplicate entries
    print("\nConsolidating duplicate entries...")
    consolidated = consolidate_entries(duplicates)

    # Build new dotfile list with consolidated entries
    new_dotfiles: list[dict[str, Any]] = []
    processed_apps: set[str] = set()

    for dotfile in config.get("dotfile", []):
        app_name = dotfile.get("application", "")

        # Skip if already processed (duplicate)
        if app_name in processed_apps:
            continue

        # Use consolidated version if available, otherwise keep original
        if app_name in consolidated:
            new_dotfiles.append(consolidated[app_name])
            processed_apps.add(app_name)
        else:
            new_dotfiles.append(dotfile)

    # Update configuration with consolidated entries
    config["dotfile"] = new_dotfiles

    # Save consolidated configuration
    print(f"Writing consolidated configuration to: {config_path}")
    save_config(config_path, config)

    # Report results
    new_count = len(new_dotfiles)
    saved_entries = original_count - new_count

    print("\nConsolidation complete!")
    print(f"  Original entries: {original_count}")
    print(f"  Consolidated entries: {new_count}")
    print(f"  Entries saved: {saved_entries}")
    print(f"  Reduction: {saved_entries / original_count * 100:.1f}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
