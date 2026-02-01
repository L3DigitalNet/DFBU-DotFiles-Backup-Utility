# Config Format Redesign

## Overview

Redesign the DFBU configuration format to be more compact, easier to edit manually, and better organized. Replace the single TOML file with two YAML files plus a session file.

## Problem Statement

The current `dfbu-config.toml` is clunky for manual editing:
- ~1940 lines for ~160 dotfile entries
- Each entry requires 5-6 lines (category, application, description, path, enabled)
- Redundant fields (category duplicates information, descriptions repeat app names)
- `enabled = true` on nearly every entry serves no purpose
- Duplicate entries exist (Firefox ×3, Steam ×2)
- Settings mixed with dotfile definitions

## Solution

### File Structure

```
DFBU/data/
├── settings.yaml     # Backup paths and options
├── dotfiles.yaml     # Dotfile library
└── session.yaml      # Excluded items (persisted between sessions)
```

### settings.yaml

User preferences for backup behavior:

```yaml
paths:
  mirror_dir: ~/GitHub/dotfiles
  archive_dir: ~/pCloudDrive/Backups/Dotfiles
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
```

### dotfiles.yaml

Dotfile library - application name as key:

```yaml
Bash:
  description: Shell configuration and startup script
  path: ~/.bashrc

Konsole:
  description: KDE terminal emulator
  paths:
    - ~/.config/konsolerc
    - ~/.local/share/konsole/Bash.profile
    - ~/.local/share/konsole/Fish.profile
  tags: kde, terminal

Git:
  description: Global version control configuration
  path: ~/.gitconfig
  tags: dev, essential
```

**Field definitions:**
- **Key**: Application/package name (required)
- **description**: Short explanation of what's being backed up (required)
- **path**: Single file/directory path (use this OR paths)
- **paths**: List of paths (use this OR path)
- **tags**: Comma-separated labels for filtering (optional)

### session.yaml

Tracks user exclusions between sessions:

```yaml
excluded:
  - Wine
  - PlayOnLinux
  - MAME
```

All entries in `dotfiles.yaml` are included by default. Only exclusions are tracked.

## Removed Fields

| Field | Reason |
|-------|--------|
| `category` | Redundant; tags provide flexible filtering |
| `enabled` | Handled by UI at runtime; exclusions in session.yaml |
| `title` | No functional purpose |
| `description` (file-level) | No functional purpose |

## UI Behavior Changes

### Selection Model
- **Default state**: All dotfiles included
- **User action**: Exclude items they don't want (uncheck)
- **Persistence**: Exclusions saved to session.yaml

### Filtering
- Text search by application name
- Tag filter for tagged entries
- Path pattern filter (e.g., `~/.config/*`)

Description field is display-only, not searchable.

## Migration

### Strategy
1. One-time migration script converts TOML → YAML
2. Consolidate duplicate entries (merge paths under single key)
3. Strip redundant description text
4. Drop removed fields
5. Keep original as `dfbu-config.toml.backup`

### Duplicate Consolidation Example

Before (3 entries):
```toml
[[dotfile]]
application = "Firefox"
path = "~/.mozilla/firefox/profiles.ini"

[[dotfile]]
application = "Firefox"
paths = ["~/.mozilla/firefox/*/prefs.js"]

[[dotfile]]
application = "Firefox"
path = "~/.mozilla/firefox/0u2cfm04.default-release/prefs.js"
```

After (1 entry):
```yaml
Firefox:
  description: Browser profiles and preferences
  paths:
    - ~/.mozilla/firefox/profiles.ini
    - ~/.mozilla/firefox/*/prefs.js
    - ~/.mozilla/firefox/0u2cfm04.default-release/prefs.js
  tags: browser
```

## Code Impact

| Component | Change |
|-----------|--------|
| `ConfigManager` | Parse YAML instead of TOML; load from two files |
| `DFBUModel` | Adapt to new data structures |
| `ViewModel` | Exclusion-based selection logic; default all checked |
| `View` | Filter/group by tags instead of category |
| New: `migration.py` | One-time TOML → YAML converter |

## New Dependency

Add `PyYAML` or `ruamel.yaml` (preferred for comment preservation during round-trip editing).

## File Size Reduction

Estimated reduction from ~1940 lines to ~600-700 lines in dotfiles.yaml:
- Remove 5 lines per entry (category, enabled, application key, brackets)
- Consolidate duplicates
- Shorter descriptions
