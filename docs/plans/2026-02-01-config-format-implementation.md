# Config Format Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the single TOML configuration with split YAML files (settings.yaml, dotfiles.yaml, session.yaml) for cleaner manual editing and better separation of concerns.

**Architecture:** Split configuration into three YAML files: settings (paths/options), dotfiles (library of backup targets), and session (exclusions). Remove category/enabled fields from dotfile definitions. Selection becomes exclusion-based with all items included by default.

**Tech Stack:** Python 3.14, PySide6, ruamel.yaml (for comment preservation), pytest

---

## Prerequisites

**Add ruamel.yaml dependency:**
```bash
uv add ruamel.yaml
```

---

### Task 1: Update Type Definitions

**Files:**
- Modify: `DFBU/core/common_types.py:33-68`
- Test: `DFBU/tests/test_common_types.py` (create)

**Step 1: Write failing tests for new types**

Create `DFBU/tests/test_common_types.py`:

```python
"""Tests for common type definitions."""

import pytest
from DFBU.core.common_types import (
    DotFileDict,
    SettingsDict,
    PathsDict,
    OptionsDict,
)


class TestDotFileDict:
    """Tests for DotFileDict TypedDict."""

    @pytest.mark.unit
    def test_dotfile_dict_single_path(self) -> None:
        """DotFileDict accepts single path as string."""
        dotfile: DotFileDict = {
            "description": "Shell configuration",
            "path": "~/.bashrc",
        }
        assert dotfile["description"] == "Shell configuration"
        assert dotfile["path"] == "~/.bashrc"

    @pytest.mark.unit
    def test_dotfile_dict_multiple_paths(self) -> None:
        """DotFileDict accepts multiple paths as list."""
        dotfile: DotFileDict = {
            "description": "Terminal emulator",
            "paths": ["~/.config/konsolerc", "~/.local/share/konsole/"],
        }
        assert dotfile["description"] == "Terminal emulator"
        assert dotfile["paths"] == ["~/.config/konsolerc", "~/.local/share/konsole/"]

    @pytest.mark.unit
    def test_dotfile_dict_with_tags(self) -> None:
        """DotFileDict accepts optional tags string."""
        dotfile: DotFileDict = {
            "description": "Git configuration",
            "path": "~/.gitconfig",
            "tags": "dev, essential",
        }
        assert dotfile["tags"] == "dev, essential"


class TestSettingsDict:
    """Tests for SettingsDict TypedDict."""

    @pytest.mark.unit
    def test_settings_dict_structure(self) -> None:
        """SettingsDict contains paths and options."""
        settings: SettingsDict = {
            "paths": {
                "mirror_dir": "~/backups/mirror",
                "archive_dir": "~/backups/archives",
                "restore_backup_dir": "~/.local/share/dfbu/restore-backups",
            },
            "options": {
                "mirror": True,
                "archive": True,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 5,
                "rotate_archives": True,
                "max_archives": 5,
                "pre_restore_backup": True,
                "max_restore_backups": 5,
            },
        }
        assert settings["paths"]["mirror_dir"] == "~/backups/mirror"
        assert settings["options"]["mirror"] is True
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_common_types.py -v`
Expected: FAIL with import errors (SettingsDict, PathsDict not defined)

**Step 3: Update type definitions**

Modify `DFBU/core/common_types.py`:

```python
"""Common type definitions shared across DFBU modules.

This module defines TypedDict classes and type aliases used throughout the application.
These types ensure consistency between the model, viewmodel, and view layers.
"""

from typing import NotRequired, TypedDict


class PathsDict(TypedDict):
    """Backup destination paths configuration.

    Attributes:
        mirror_dir: Directory for mirror backups
        archive_dir: Directory for archive backups
        restore_backup_dir: Directory for pre-restore backups
    """

    mirror_dir: str
    archive_dir: str
    restore_backup_dir: str


class OptionsDict(TypedDict):
    """Backup behavior options.

    Attributes:
        mirror: Enable mirror backup
        archive: Enable archive creation
        hostname_subdir: Create hostname subdirectory
        date_subdir: Create date subdirectory
        archive_format: Archive format (e.g., "tar.gz")
        archive_compression_level: Compression level 0-9
        rotate_archives: Enable archive rotation
        max_archives: Maximum archives to keep
        pre_restore_backup: Enable pre-restore backup
        max_restore_backups: Maximum restore backups to keep
    """

    mirror: bool
    archive: bool
    hostname_subdir: bool
    date_subdir: bool
    archive_format: str
    archive_compression_level: int
    rotate_archives: bool
    max_archives: int
    pre_restore_backup: bool
    max_restore_backups: int


class SettingsDict(TypedDict):
    """Complete settings configuration.

    Attributes:
        paths: Backup destination paths
        options: Backup behavior options
    """

    paths: PathsDict
    options: OptionsDict


class DotFileDict(TypedDict, total=False):
    """Dotfile library entry.

    Application name is the key in the YAML file, not stored here.

    Attributes:
        description: Human-readable description (required)
        path: Single file/directory path (use path OR paths)
        paths: List of file/directory paths (use path OR paths)
        tags: Comma-separated tags for filtering (optional)
    """

    description: str  # Required but total=False allows partial construction
    path: NotRequired[str]
    paths: NotRequired[list[str]]
    tags: NotRequired[str]


class SessionDict(TypedDict):
    """Session state for exclusions.

    Attributes:
        excluded: List of application names to exclude from backup
    """

    excluded: list[str]


# Legacy type for migration - will be removed after migration complete
class LegacyDotFileDict(TypedDict):
    """Legacy dotfile entry from TOML format (for migration only)."""

    category: str
    application: str
    description: str
    paths: list[str]
    mirror_dir: str
    archive_dir: str
    enabled: bool
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_common_types.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add DFBU/core/common_types.py DFBU/tests/test_common_types.py
git commit -m "refactor: update TypedDicts for YAML config format"
```

---

### Task 2: Create YAML Configuration Loader

**Files:**
- Create: `DFBU/core/yaml_config.py`
- Test: `DFBU/tests/test_yaml_config.py`

**Step 1: Write failing tests for YAML loading**

Create `DFBU/tests/test_yaml_config.py`:

```python
"""Tests for YAML configuration loading and saving."""

from pathlib import Path

import pytest

from DFBU.core.yaml_config import YAMLConfigLoader


class TestYAMLConfigLoader:
    """Tests for YAMLConfigLoader class."""

    @pytest.mark.unit
    def test_load_settings(self, tmp_path: Path) -> None:
        """Load settings from YAML file."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text("""
paths:
  mirror_dir: ~/backups/mirror
  archive_dir: ~/backups/archives
  restore_backup_dir: ~/.local/share/dfbu/restore-backups

options:
  mirror: true
  archive: true
  hostname_subdir: true
  date_subdir: false
  archive_format: tar.gz
  archive_compression_level: 5
  rotate_archives: true
  max_archives: 5
  pre_restore_backup: true
  max_restore_backups: 5
""")
        loader = YAMLConfigLoader(tmp_path)
        settings = loader.load_settings()

        assert settings["paths"]["mirror_dir"] == "~/backups/mirror"
        assert settings["options"]["mirror"] is True
        assert settings["options"]["archive_compression_level"] == 5

    @pytest.mark.unit
    def test_load_dotfiles(self, tmp_path: Path) -> None:
        """Load dotfiles library from YAML file."""
        dotfiles_file = tmp_path / "dotfiles.yaml"
        dotfiles_file.write_text("""
Bash:
  description: Shell configuration
  path: ~/.bashrc

Konsole:
  description: Terminal emulator
  paths:
    - ~/.config/konsolerc
    - ~/.local/share/konsole/
  tags: kde, terminal
""")
        loader = YAMLConfigLoader(tmp_path)
        dotfiles = loader.load_dotfiles()

        assert "Bash" in dotfiles
        assert dotfiles["Bash"]["description"] == "Shell configuration"
        assert dotfiles["Bash"]["path"] == "~/.bashrc"
        assert "Konsole" in dotfiles
        assert dotfiles["Konsole"]["tags"] == "kde, terminal"

    @pytest.mark.unit
    def test_load_session(self, tmp_path: Path) -> None:
        """Load session exclusions from YAML file."""
        session_file = tmp_path / "session.yaml"
        session_file.write_text("""
excluded:
  - Wine
  - PlayOnLinux
""")
        loader = YAMLConfigLoader(tmp_path)
        session = loader.load_session()

        assert session["excluded"] == ["Wine", "PlayOnLinux"]

    @pytest.mark.unit
    def test_load_session_empty(self, tmp_path: Path) -> None:
        """Load empty session when file doesn't exist."""
        loader = YAMLConfigLoader(tmp_path)
        session = loader.load_session()

        assert session["excluded"] == []

    @pytest.mark.unit
    def test_save_settings(self, tmp_path: Path) -> None:
        """Save settings to YAML file."""
        loader = YAMLConfigLoader(tmp_path)
        settings = {
            "paths": {
                "mirror_dir": "~/test/mirror",
                "archive_dir": "~/test/archives",
                "restore_backup_dir": "~/.local/share/dfbu/restore-backups",
            },
            "options": {
                "mirror": True,
                "archive": False,
                "hostname_subdir": True,
                "date_subdir": False,
                "archive_format": "tar.gz",
                "archive_compression_level": 5,
                "rotate_archives": True,
                "max_archives": 5,
                "pre_restore_backup": True,
                "max_restore_backups": 5,
            },
        }
        loader.save_settings(settings)

        content = (tmp_path / "settings.yaml").read_text()
        assert "mirror_dir: ~/test/mirror" in content
        assert "archive: false" in content

    @pytest.mark.unit
    def test_save_session(self, tmp_path: Path) -> None:
        """Save session exclusions to YAML file."""
        loader = YAMLConfigLoader(tmp_path)
        session = {"excluded": ["Wine", "MAME"]}
        loader.save_session(session)

        content = (tmp_path / "session.yaml").read_text()
        assert "Wine" in content
        assert "MAME" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_yaml_config.py -v`
Expected: FAIL with import error (YAMLConfigLoader not defined)

**Step 3: Implement YAML loader**

Create `DFBU/core/yaml_config.py`:

```python
"""YAML configuration loading and saving for DFBU.

Handles the three configuration files:
- settings.yaml: Backup paths and options
- dotfiles.yaml: Dotfile library definitions
- session.yaml: User exclusions between sessions
"""

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from DFBU.core.common_types import DotFileDict, OptionsDict, PathsDict, SessionDict, SettingsDict


class YAMLConfigLoader:
    """Loads and saves YAML configuration files.

    Attributes:
        config_dir: Directory containing configuration files
    """

    def __init__(self, config_dir: Path | str) -> None:
        """Initialize loader with configuration directory.

        Args:
            config_dir: Path to directory containing YAML config files
        """
        self.config_dir = Path(config_dir)
        self._yaml = YAML()
        self._yaml.preserve_quotes = True
        self._yaml.default_flow_style = False

    @property
    def settings_path(self) -> Path:
        """Path to settings.yaml."""
        return self.config_dir / "settings.yaml"

    @property
    def dotfiles_path(self) -> Path:
        """Path to dotfiles.yaml."""
        return self.config_dir / "dotfiles.yaml"

    @property
    def session_path(self) -> Path:
        """Path to session.yaml."""
        return self.config_dir / "session.yaml"

    def load_settings(self) -> SettingsDict:
        """Load settings from settings.yaml.

        Returns:
            Settings dictionary with paths and options

        Raises:
            FileNotFoundError: If settings.yaml doesn't exist
            ValueError: If settings.yaml is malformed
        """
        if not self.settings_path.exists():
            raise FileNotFoundError(f"Settings file not found: {self.settings_path}")

        with open(self.settings_path, encoding="utf-8") as f:
            data = self._yaml.load(f)

        if data is None:
            raise ValueError("Settings file is empty")

        return self._validate_settings(data)

    def _validate_settings(self, data: dict[str, Any]) -> SettingsDict:
        """Validate and return settings dictionary.

        Args:
            data: Raw YAML data

        Returns:
            Validated SettingsDict

        Raises:
            ValueError: If required fields are missing
        """
        if "paths" not in data:
            raise ValueError("Missing 'paths' section in settings")
        if "options" not in data:
            raise ValueError("Missing 'options' section in settings")

        paths: PathsDict = {
            "mirror_dir": data["paths"].get("mirror_dir", ""),
            "archive_dir": data["paths"].get("archive_dir", ""),
            "restore_backup_dir": data["paths"].get(
                "restore_backup_dir", "~/.local/share/dfbu/restore-backups"
            ),
        }

        options: OptionsDict = {
            "mirror": data["options"].get("mirror", True),
            "archive": data["options"].get("archive", True),
            "hostname_subdir": data["options"].get("hostname_subdir", True),
            "date_subdir": data["options"].get("date_subdir", False),
            "archive_format": data["options"].get("archive_format", "tar.gz"),
            "archive_compression_level": data["options"].get("archive_compression_level", 5),
            "rotate_archives": data["options"].get("rotate_archives", True),
            "max_archives": data["options"].get("max_archives", 5),
            "pre_restore_backup": data["options"].get("pre_restore_backup", True),
            "max_restore_backups": data["options"].get("max_restore_backups", 5),
        }

        return {"paths": paths, "options": options}

    def load_dotfiles(self) -> dict[str, DotFileDict]:
        """Load dotfiles library from dotfiles.yaml.

        Returns:
            Dictionary mapping application names to dotfile definitions

        Raises:
            FileNotFoundError: If dotfiles.yaml doesn't exist
        """
        if not self.dotfiles_path.exists():
            raise FileNotFoundError(f"Dotfiles file not found: {self.dotfiles_path}")

        with open(self.dotfiles_path, encoding="utf-8") as f:
            data = self._yaml.load(f)

        if data is None:
            return {}

        return {name: self._validate_dotfile(name, entry) for name, entry in data.items()}

    def _validate_dotfile(self, name: str, entry: dict[str, Any]) -> DotFileDict:
        """Validate a single dotfile entry.

        Args:
            name: Application name (key)
            entry: Dotfile entry data

        Returns:
            Validated DotFileDict

        Raises:
            ValueError: If required fields are missing
        """
        if "description" not in entry:
            raise ValueError(f"Dotfile '{name}' missing required 'description' field")

        if "path" not in entry and "paths" not in entry:
            raise ValueError(f"Dotfile '{name}' must have either 'path' or 'paths' field")

        dotfile: DotFileDict = {"description": entry["description"]}

        if "path" in entry:
            dotfile["path"] = entry["path"]
        if "paths" in entry:
            dotfile["paths"] = list(entry["paths"])
        if "tags" in entry:
            dotfile["tags"] = entry["tags"]

        return dotfile

    def load_session(self) -> SessionDict:
        """Load session exclusions from session.yaml.

        Returns:
            Session dictionary with excluded list (empty if file doesn't exist)
        """
        if not self.session_path.exists():
            return {"excluded": []}

        with open(self.session_path, encoding="utf-8") as f:
            data = self._yaml.load(f)

        if data is None:
            return {"excluded": []}

        return {"excluded": list(data.get("excluded", []))}

    def save_settings(self, settings: SettingsDict) -> None:
        """Save settings to settings.yaml.

        Args:
            settings: Settings dictionary to save
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.settings_path, "w", encoding="utf-8") as f:
            self._yaml.dump(dict(settings), f)

    def save_dotfiles(self, dotfiles: dict[str, DotFileDict]) -> None:
        """Save dotfiles library to dotfiles.yaml.

        Args:
            dotfiles: Dictionary mapping names to dotfile definitions
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.dotfiles_path, "w", encoding="utf-8") as f:
            self._yaml.dump(dict(dotfiles), f)

    def save_session(self, session: SessionDict) -> None:
        """Save session exclusions to session.yaml.

        Args:
            session: Session dictionary with excluded list
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.session_path, "w", encoding="utf-8") as f:
            self._yaml.dump(dict(session), f)
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_yaml_config.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add DFBU/core/yaml_config.py DFBU/tests/test_yaml_config.py
git commit -m "feat: add YAML configuration loader"
```

---

### Task 3: Create Migration Script

**Files:**
- Create: `DFBU/core/migration.py`
- Test: `DFBU/tests/test_migration.py`

**Step 1: Write failing tests for migration**

Create `DFBU/tests/test_migration.py`:

```python
"""Tests for TOML to YAML migration."""

from pathlib import Path

import pytest

from DFBU.core.migration import ConfigMigrator


class TestConfigMigrator:
    """Tests for ConfigMigrator class."""

    @pytest.fixture
    def sample_toml(self, tmp_path: Path) -> Path:
        """Create sample TOML config for testing."""
        toml_file = tmp_path / "dfbu-config.toml"
        toml_file.write_text('''
title = "Dotfiles Backup Config"
description = "Configuration file for dotfiles backup."

[paths]
mirror_dir = "~/GitHub/dotfiles"
archive_dir = "~/pCloudDrive/Backups/Dotfiles"
restore_backup_dir = "~/.local/share/dfbu/restore-backups"

[options]
mirror = true
archive = true
hostname_subdir = true
date_subdir = false
archive_format = "tar.gz"
archive_compression_level = 5
rotate_archives = true
max_archives = 5
pre_restore_backup = true
max_restore_backups = 5

[[dotfile]]
category = "Shell configs"
application = "Bash"
description = "Bash shell configuration and startup script"
enabled = true
path = "~/.bashrc"

[[dotfile]]
category = "Shell configs"
application = "Zsh"
description = "Zsh shell configuration and startup script"
enabled = true
path = "~/.zshrc"

[[dotfile]]
category = "Terminal"
application = "Konsole"
description = "KDE Konsole terminal emulator configuration"
enabled = true
paths = [
    "~/.config/konsolerc",
    "~/.local/share/konsole/Bash.profile",
]

[[dotfile]]
category = "Applications"
application = "Firefox"
description = "Mozilla Firefox browser profiles"
enabled = true
path = "~/.mozilla/firefox/profiles.ini"

[[dotfile]]
category = "Applications"
application = "Firefox"
description = "Firefox preferences"
enabled = false
paths = ["~/.mozilla/firefox/*/prefs.js"]
''')
        return toml_file

    @pytest.mark.unit
    def test_migrate_creates_settings_yaml(self, sample_toml: Path, tmp_path: Path) -> None:
        """Migration creates settings.yaml with paths and options."""
        migrator = ConfigMigrator(sample_toml, tmp_path)
        migrator.migrate()

        settings_file = tmp_path / "settings.yaml"
        assert settings_file.exists()

        content = settings_file.read_text()
        assert "mirror_dir:" in content
        assert "~/GitHub/dotfiles" in content
        assert "archive_compression_level:" in content

    @pytest.mark.unit
    def test_migrate_creates_dotfiles_yaml(self, sample_toml: Path, tmp_path: Path) -> None:
        """Migration creates dotfiles.yaml with library entries."""
        migrator = ConfigMigrator(sample_toml, tmp_path)
        migrator.migrate()

        dotfiles_file = tmp_path / "dotfiles.yaml"
        assert dotfiles_file.exists()

        content = dotfiles_file.read_text()
        assert "Bash:" in content
        assert "description:" in content
        assert "~/.bashrc" in content

    @pytest.mark.unit
    def test_migrate_consolidates_duplicates(self, sample_toml: Path, tmp_path: Path) -> None:
        """Migration consolidates duplicate application entries."""
        migrator = ConfigMigrator(sample_toml, tmp_path)
        migrator.migrate()

        dotfiles_file = tmp_path / "dotfiles.yaml"
        content = dotfiles_file.read_text()

        # Firefox should appear once with merged paths
        assert content.count("Firefox:") == 1
        assert "profiles.ini" in content
        assert "prefs.js" in content

    @pytest.mark.unit
    def test_migrate_drops_category_and_enabled(self, sample_toml: Path, tmp_path: Path) -> None:
        """Migration drops category and enabled fields."""
        migrator = ConfigMigrator(sample_toml, tmp_path)
        migrator.migrate()

        dotfiles_file = tmp_path / "dotfiles.yaml"
        content = dotfiles_file.read_text()

        assert "category:" not in content
        assert "enabled:" not in content

    @pytest.mark.unit
    def test_migrate_creates_backup(self, sample_toml: Path, tmp_path: Path) -> None:
        """Migration creates backup of original TOML."""
        migrator = ConfigMigrator(sample_toml, tmp_path)
        migrator.migrate()

        backup_file = sample_toml.with_suffix(".toml.backup")
        assert backup_file.exists()

    @pytest.mark.unit
    def test_migrate_creates_empty_session(self, sample_toml: Path, tmp_path: Path) -> None:
        """Migration creates session.yaml with empty exclusions."""
        migrator = ConfigMigrator(sample_toml, tmp_path)
        migrator.migrate()

        session_file = tmp_path / "session.yaml"
        assert session_file.exists()

        content = session_file.read_text()
        assert "excluded:" in content
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_migration.py -v`
Expected: FAIL with import error (ConfigMigrator not defined)

**Step 3: Implement migration script**

Create `DFBU/core/migration.py`:

```python
"""Migration utility for converting TOML config to YAML format.

Converts the single dfbu-config.toml file into:
- settings.yaml: Backup paths and options
- dotfiles.yaml: Dotfile library
- session.yaml: Empty exclusions list
"""

import shutil
import tomllib
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from DFBU.core.common_types import DotFileDict, OptionsDict, PathsDict, SessionDict, SettingsDict


class ConfigMigrator:
    """Migrates TOML configuration to YAML format.

    Attributes:
        toml_path: Path to source TOML file
        output_dir: Directory for output YAML files
    """

    def __init__(self, toml_path: Path | str, output_dir: Path | str) -> None:
        """Initialize migrator with source and destination paths.

        Args:
            toml_path: Path to dfbu-config.toml
            output_dir: Directory for output YAML files
        """
        self.toml_path = Path(toml_path)
        self.output_dir = Path(output_dir)
        self._yaml = YAML()
        self._yaml.default_flow_style = False
        self._yaml.indent(mapping=2, sequence=4, offset=2)

    def migrate(self) -> None:
        """Perform the migration.

        Creates settings.yaml, dotfiles.yaml, and session.yaml in output_dir.
        Backs up the original TOML file.
        """
        toml_data = self._load_toml()

        settings = self._extract_settings(toml_data)
        dotfiles = self._extract_dotfiles(toml_data)
        session: SessionDict = {"excluded": []}

        self._save_yaml(settings, dotfiles, session)
        self._backup_toml()

    def _load_toml(self) -> dict[str, Any]:
        """Load and parse TOML file.

        Returns:
            Parsed TOML data as dictionary

        Raises:
            FileNotFoundError: If TOML file doesn't exist
        """
        if not self.toml_path.exists():
            raise FileNotFoundError(f"TOML file not found: {self.toml_path}")

        with open(self.toml_path, "rb") as f:
            return tomllib.load(f)

    def _extract_settings(self, data: dict[str, Any]) -> SettingsDict:
        """Extract settings from TOML data.

        Args:
            data: Parsed TOML data

        Returns:
            SettingsDict with paths and options
        """
        paths_data = data.get("paths", {})
        options_data = data.get("options", {})

        paths: PathsDict = {
            "mirror_dir": paths_data.get("mirror_dir", ""),
            "archive_dir": paths_data.get("archive_dir", ""),
            "restore_backup_dir": paths_data.get(
                "restore_backup_dir", "~/.local/share/dfbu/restore-backups"
            ),
        }

        options: OptionsDict = {
            "mirror": options_data.get("mirror", True),
            "archive": options_data.get("archive", True),
            "hostname_subdir": options_data.get("hostname_subdir", True),
            "date_subdir": options_data.get("date_subdir", False),
            "archive_format": options_data.get("archive_format", "tar.gz"),
            "archive_compression_level": options_data.get("archive_compression_level", 5),
            "rotate_archives": options_data.get("rotate_archives", True),
            "max_archives": options_data.get("max_archives", 5),
            "pre_restore_backup": options_data.get("pre_restore_backup", True),
            "max_restore_backups": options_data.get("max_restore_backups", 5),
        }

        return {"paths": paths, "options": options}

    def _extract_dotfiles(self, data: dict[str, Any]) -> dict[str, DotFileDict]:
        """Extract and consolidate dotfiles from TOML data.

        Merges duplicate application entries by combining their paths.

        Args:
            data: Parsed TOML data

        Returns:
            Dictionary mapping application names to DotFileDict
        """
        dotfiles: dict[str, DotFileDict] = {}
        raw_dotfiles = data.get("dotfile", [])

        for entry in raw_dotfiles:
            name = entry.get("application", "Unknown")
            description = self._clean_description(entry.get("description", ""), name)

            # Get paths from entry
            paths = self._get_paths_from_entry(entry)

            if name in dotfiles:
                # Merge with existing entry
                existing = dotfiles[name]
                existing_paths = self._get_paths_from_dotfile(existing)
                merged_paths = list(dict.fromkeys(existing_paths + paths))  # Dedupe, preserve order
                dotfiles[name] = {
                    "description": existing["description"],
                    "paths": merged_paths,
                }
                if "tags" in existing:
                    dotfiles[name]["tags"] = existing["tags"]
            else:
                # New entry
                dotfile: DotFileDict = {"description": description}
                if len(paths) == 1:
                    dotfile["path"] = paths[0]
                else:
                    dotfile["paths"] = paths
                dotfiles[name] = dotfile

        return dotfiles

    def _get_paths_from_entry(self, entry: dict[str, Any]) -> list[str]:
        """Extract paths from a TOML dotfile entry.

        Args:
            entry: TOML dotfile entry

        Returns:
            List of paths
        """
        if "paths" in entry:
            return list(entry["paths"])
        elif "path" in entry:
            return [entry["path"]]
        return []

    def _get_paths_from_dotfile(self, dotfile: DotFileDict) -> list[str]:
        """Extract paths from a DotFileDict.

        Args:
            dotfile: DotFileDict entry

        Returns:
            List of paths
        """
        if "paths" in dotfile:
            return list(dotfile["paths"])
        elif "path" in dotfile:
            return [dotfile["path"]]
        return []

    def _clean_description(self, description: str, app_name: str) -> str:
        """Clean up redundant description text.

        Removes patterns like "KDE X configuration" -> "X configuration"
        when the app name already indicates the application.

        Args:
            description: Original description
            app_name: Application name

        Returns:
            Cleaned description
        """
        # Remove common redundant prefixes
        prefixes_to_remove = [
            "KDE ",
            "GNOME ",
            "GNU ",
            "Mozilla ",
            "Google ",
            "Microsoft ",
        ]
        result = description
        for prefix in prefixes_to_remove:
            if result.startswith(prefix) and app_name in result:
                result = result[len(prefix):]

        # Remove app name from start if duplicated
        if result.lower().startswith(app_name.lower()):
            result = result[len(app_name):].lstrip(" -:")

        return result.strip() or description  # Fall back to original if empty

    def _save_yaml(
        self,
        settings: SettingsDict,
        dotfiles: dict[str, DotFileDict],
        session: SessionDict,
    ) -> None:
        """Save configuration to YAML files.

        Args:
            settings: Settings dictionary
            dotfiles: Dotfiles dictionary
            session: Session dictionary
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Save settings.yaml
        settings_path = self.output_dir / "settings.yaml"
        with open(settings_path, "w", encoding="utf-8") as f:
            self._yaml.dump(dict(settings), f)

        # Save dotfiles.yaml
        dotfiles_path = self.output_dir / "dotfiles.yaml"
        with open(dotfiles_path, "w", encoding="utf-8") as f:
            self._yaml.dump(dict(dotfiles), f)

        # Save session.yaml
        session_path = self.output_dir / "session.yaml"
        with open(session_path, "w", encoding="utf-8") as f:
            self._yaml.dump(dict(session), f)

    def _backup_toml(self) -> None:
        """Create backup of original TOML file."""
        backup_path = self.toml_path.with_suffix(".toml.backup")
        shutil.copy2(self.toml_path, backup_path)


def migrate_config(toml_path: Path | str, output_dir: Path | str | None = None) -> None:
    """Convenience function to migrate TOML config to YAML.

    Args:
        toml_path: Path to dfbu-config.toml
        output_dir: Directory for YAML files (defaults to same directory as TOML)
    """
    toml_path = Path(toml_path)
    if output_dir is None:
        output_dir = toml_path.parent

    migrator = ConfigMigrator(toml_path, output_dir)
    migrator.migrate()
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_migration.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add DFBU/core/migration.py DFBU/tests/test_migration.py
git commit -m "feat: add TOML to YAML migration script"
```

---

### Task 4: Update ConfigManager for YAML

**Files:**
- Modify: `DFBU/gui/config_manager.py`
- Test: `DFBU/tests/test_config_manager_yaml.py` (create)

**Step 1: Write failing tests for YAML-based ConfigManager**

Create `DFBU/tests/test_config_manager_yaml.py`:

```python
"""Tests for ConfigManager with YAML configuration."""

from pathlib import Path

import pytest

from DFBU.gui.config_manager import ConfigManager


@pytest.fixture
def yaml_config_dir(tmp_path: Path) -> Path:
    """Create YAML config files for testing."""
    # settings.yaml
    (tmp_path / "settings.yaml").write_text("""
paths:
  mirror_dir: ~/backups/mirror
  archive_dir: ~/backups/archives
  restore_backup_dir: ~/.local/share/dfbu/restore-backups

options:
  mirror: true
  archive: true
  hostname_subdir: true
  date_subdir: false
  archive_format: tar.gz
  archive_compression_level: 5
  rotate_archives: true
  max_archives: 5
  pre_restore_backup: true
  max_restore_backups: 5
""")

    # dotfiles.yaml
    (tmp_path / "dotfiles.yaml").write_text("""
Bash:
  description: Shell configuration
  path: ~/.bashrc

Konsole:
  description: Terminal emulator
  paths:
    - ~/.config/konsolerc
    - ~/.local/share/konsole/
  tags: kde, terminal
""")

    return tmp_path


class TestConfigManagerYAML:
    """Tests for ConfigManager with YAML files."""

    @pytest.mark.unit
    def test_load_config_from_yaml(self, yaml_config_dir: Path) -> None:
        """ConfigManager loads from YAML files."""
        manager = ConfigManager(yaml_config_dir)
        success, error = manager.load_config()

        assert success is True
        assert error == ""

    @pytest.mark.unit
    def test_get_dotfile_list(self, yaml_config_dir: Path) -> None:
        """Get list of dotfiles with application name included."""
        manager = ConfigManager(yaml_config_dir)
        manager.load_config()

        dotfiles = manager.get_dotfile_list()

        assert len(dotfiles) == 2
        # Application name should be included in the dict
        bash_entry = next(d for d in dotfiles if d["application"] == "Bash")
        assert bash_entry["description"] == "Shell configuration"

    @pytest.mark.unit
    def test_get_exclusions(self, yaml_config_dir: Path) -> None:
        """Get current exclusion list."""
        manager = ConfigManager(yaml_config_dir)
        manager.load_config()

        exclusions = manager.get_exclusions()
        assert exclusions == []

    @pytest.mark.unit
    def test_set_exclusions(self, yaml_config_dir: Path) -> None:
        """Set and persist exclusions."""
        manager = ConfigManager(yaml_config_dir)
        manager.load_config()

        manager.set_exclusions(["Bash"])

        # Reload and verify persistence
        manager2 = ConfigManager(yaml_config_dir)
        manager2.load_config()
        assert manager2.get_exclusions() == ["Bash"]

    @pytest.mark.unit
    def test_is_excluded(self, yaml_config_dir: Path) -> None:
        """Check if specific dotfile is excluded."""
        manager = ConfigManager(yaml_config_dir)
        manager.load_config()
        manager.set_exclusions(["Bash"])

        assert manager.is_excluded("Bash") is True
        assert manager.is_excluded("Konsole") is False

    @pytest.mark.unit
    def test_toggle_exclusion(self, yaml_config_dir: Path) -> None:
        """Toggle exclusion status."""
        manager = ConfigManager(yaml_config_dir)
        manager.load_config()

        # Exclude
        manager.toggle_exclusion("Bash")
        assert manager.is_excluded("Bash") is True

        # Include again
        manager.toggle_exclusion("Bash")
        assert manager.is_excluded("Bash") is False

    @pytest.mark.unit
    def test_get_included_dotfiles(self, yaml_config_dir: Path) -> None:
        """Get only non-excluded dotfiles."""
        manager = ConfigManager(yaml_config_dir)
        manager.load_config()
        manager.set_exclusions(["Bash"])

        included = manager.get_included_dotfiles()

        assert len(included) == 1
        assert included[0]["application"] == "Konsole"
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_config_manager_yaml.py -v`
Expected: FAIL (ConfigManager still expects TOML)

**Step 3: Update ConfigManager implementation**

This is a significant refactor. The key changes to `DFBU/gui/config_manager.py`:

1. Replace TOML loading with YAMLConfigLoader
2. Store dotfiles as dict (name -> definition) internally
3. Add exclusion management methods
4. Update save methods for YAML
5. Adapt existing methods to new data structure

See the full implementation in a separate detailed task breakdown below.

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_config_manager_yaml.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add DFBU/gui/config_manager.py DFBU/tests/test_config_manager_yaml.py
git commit -m "refactor: update ConfigManager for YAML format"
```

---

### Task 5: Update ViewModel for Exclusion-Based Selection

**Files:**
- Modify: `DFBU/gui/viewmodel.py`
- Test: `DFBU/tests/test_viewmodel_exclusions.py` (create)

**Step 1: Write failing tests for exclusion-based selection**

Create `DFBU/tests/test_viewmodel_exclusions.py`:

```python
"""Tests for ViewModel exclusion-based selection."""

import pytest
from PySide6.QtCore import QCoreApplication
from unittest.mock import Mock

from DFBU.gui.viewmodel import DFBUViewModel


@pytest.fixture
def mock_config_manager() -> Mock:
    """Create mock ConfigManager for ViewModel testing."""
    manager = Mock()
    manager.get_dotfile_list.return_value = [
        {"application": "Bash", "description": "Shell config", "paths": ["~/.bashrc"]},
        {"application": "Konsole", "description": "Terminal", "paths": ["~/.config/konsolerc"]},
    ]
    manager.get_exclusions.return_value = []
    manager.is_excluded.return_value = False
    manager.get_included_dotfiles.return_value = manager.get_dotfile_list.return_value
    return manager


class TestViewModelExclusions:
    """Tests for ViewModel exclusion handling."""

    @pytest.mark.gui
    def test_command_toggle_exclusion(self, qapp: QCoreApplication, mock_config_manager: Mock) -> None:
        """Toggle exclusion emits signal."""
        vm = DFBUViewModel(config_manager=mock_config_manager)

        vm.command_toggle_exclusion("Bash")

        mock_config_manager.toggle_exclusion.assert_called_once_with("Bash")

    @pytest.mark.gui
    def test_get_exclusions(self, qapp: QCoreApplication, mock_config_manager: Mock) -> None:
        """Get current exclusions from config manager."""
        mock_config_manager.get_exclusions.return_value = ["Bash"]
        vm = DFBUViewModel(config_manager=mock_config_manager)

        exclusions = vm.get_exclusions()

        assert exclusions == ["Bash"]

    @pytest.mark.gui
    def test_is_excluded(self, qapp: QCoreApplication, mock_config_manager: Mock) -> None:
        """Check if dotfile is excluded."""
        mock_config_manager.is_excluded.side_effect = lambda x: x == "Bash"
        vm = DFBUViewModel(config_manager=mock_config_manager)

        assert vm.is_excluded("Bash") is True
        assert vm.is_excluded("Konsole") is False
```

**Step 2: Run test to verify it fails**

Run: `pytest DFBU/tests/test_viewmodel_exclusions.py -v`
Expected: FAIL (methods don't exist)

**Step 3: Update ViewModel**

Add to `DFBU/gui/viewmodel.py`:

```python
def command_toggle_exclusion(self, application: str) -> None:
    """Toggle exclusion status for a dotfile.

    Args:
        application: Application name to toggle
    """
    self._config_manager.toggle_exclusion(application)
    self.exclusions_changed.emit()

def get_exclusions(self) -> list[str]:
    """Get current exclusion list.

    Returns:
        List of excluded application names
    """
    return self._config_manager.get_exclusions()

def is_excluded(self, application: str) -> bool:
    """Check if application is excluded.

    Args:
        application: Application name

    Returns:
        True if excluded
    """
    return self._config_manager.is_excluded(application)
```

Add signal:
```python
exclusions_changed = Signal()
```

**Step 4: Run test to verify it passes**

Run: `pytest DFBU/tests/test_viewmodel_exclusions.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add DFBU/gui/viewmodel.py DFBU/tests/test_viewmodel_exclusions.py
git commit -m "feat: add exclusion-based selection to ViewModel"
```

---

### Task 6: Update View for Exclusion UI

**Files:**
- Modify: `DFBU/gui/view.py`
- Modify: `DFBU/gui/designer/main_window.ui` (if needed)

**Step 1: Update dotfile table to show exclusion state**

Changes to `DFBU/gui/view.py`:

1. Replace "Enabled" column with "Included" (checked = included, unchecked = excluded)
2. Default all items to checked (included)
3. Connect checkbox toggle to `command_toggle_exclusion`
4. Remove category column, add tags display
5. Add text filter for application name search

**Step 2: Implement filtering by name, tags, path**

Add filter input field and logic:

```python
def _setup_filter_ui(self) -> None:
    """Set up filter controls for dotfile table."""
    self._filter_input = self.findChild(QLineEdit, "filterLineEdit")
    if self._filter_input:
        self._filter_input.textChanged.connect(self._apply_filter)
        self._filter_input.setPlaceholderText("Filter by name, tags, or path...")

def _apply_filter(self, text: str) -> None:
    """Filter dotfile table by search text.

    Args:
        text: Filter text to match against name, tags, path
    """
    text = text.lower()
    for row in range(self._dotfile_table.rowCount()):
        name_item = self._dotfile_table.item(row, 1)  # Application column
        tags_item = self._dotfile_table.item(row, 3)  # Tags column
        path_item = self._dotfile_table.item(row, 4)  # Path column

        name = name_item.text().lower() if name_item else ""
        tags = tags_item.text().lower() if tags_item else ""
        path = path_item.text().lower() if path_item else ""

        matches = text in name or text in tags or text in path
        self._dotfile_table.setRowHidden(row, not matches)
```

**Step 3: Test manually**

Run: `python DFBU/dfbu-gui.py`
Verify:
- All dotfiles show as included (checked) by default
- Unchecking excludes the item
- Filter works on name, tags, path
- Exclusions persist after restart

**Step 4: Commit**

```bash
git add DFBU/gui/view.py DFBU/gui/designer/main_window.ui
git commit -m "feat: update View for exclusion-based UI with filtering"
```

---

### Task 7: Run Migration on Real Config

**Files:**
- Use: `DFBU/data/dfbu-config.toml`

**Step 1: Backup current config**

```bash
cp DFBU/data/dfbu-config.toml DFBU/data/dfbu-config.toml.pre-migration
```

**Step 2: Run migration**

```bash
python -c "from DFBU.core.migration import migrate_config; migrate_config('DFBU/data/dfbu-config.toml')"
```

**Step 3: Verify output files**

Check that these exist and look correct:
- `DFBU/data/settings.yaml`
- `DFBU/data/dotfiles.yaml`
- `DFBU/data/session.yaml`
- `DFBU/data/dfbu-config.toml.backup`

**Step 4: Manual review and cleanup**

Review `dotfiles.yaml`:
- Check for duplicate consolidation
- Verify descriptions are cleaned up
- Add tags to key entries if desired

**Step 5: Commit migrated files**

```bash
git add DFBU/data/settings.yaml DFBU/data/dotfiles.yaml DFBU/data/session.yaml
git rm DFBU/data/dfbu-config.toml
git commit -m "chore: migrate config from TOML to YAML format"
```

---

### Task 8: Update Dependencies and Cleanup

**Files:**
- Modify: `pyproject.toml`
- Remove: Old TOML-specific imports

**Step 1: Add ruamel.yaml to dependencies**

```bash
uv add ruamel.yaml
```

**Step 2: Remove tomli-w dependency (if no longer needed)**

```bash
uv remove tomli-w
```

**Step 3: Update imports in config_manager.py**

Remove:
```python
import tomllib
import tomli_w
```

**Step 4: Run full test suite**

```bash
pytest DFBU/tests/ -v
```

**Step 5: Commit cleanup**

```bash
git add pyproject.toml uv.lock DFBU/gui/config_manager.py
git commit -m "chore: update dependencies for YAML config"
```

---

### Task 9: Final Integration Testing

**Step 1: Run application end-to-end**

```bash
python DFBU/dfbu-gui.py
```

Test scenarios:
1. Application loads without errors
2. All dotfiles display in table (included by default)
3. Exclude some items, restart, verify persistence
4. Filter by name works
5. Filter by tags works (for items with tags)
6. Filter by path works
7. Backup operation uses only included items
8. Settings changes save correctly

**Step 2: Run full test suite with coverage**

```bash
pytest DFBU/tests/ --cov=DFBU --cov-report=html
```

**Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete YAML config format migration"
```

---

## Summary

| Task | Description | Est. Steps |
|------|-------------|------------|
| 1 | Update type definitions | 5 |
| 2 | Create YAML loader | 5 |
| 3 | Create migration script | 5 |
| 4 | Update ConfigManager | 5 |
| 5 | Update ViewModel | 5 |
| 6 | Update View | 4 |
| 7 | Run migration | 5 |
| 8 | Update dependencies | 5 |
| 9 | Integration testing | 3 |

**Total: 9 tasks, ~42 steps**
