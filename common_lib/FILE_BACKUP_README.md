# File Backup Utility

Reusable utility module for creating and managing rotating file backups with automatic cleanup.

## Features

- **Timestamped Backups**: Creates backup copies with ISO 8601 compatible timestamps
- **Automatic Rotation**: Maintains maximum backup count by deleting oldest backups
- **Collision Handling**: Handles rapid successive backups within same timestamp
- **Configurable**: Custom backup directories, retention limits, and timestamp formats
- **Standard Library Only**: No external dependencies required

## Installation

This module is part of the common_lib shared utilities. No installation needed for projects in this repository.

```python
# Add to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "common_lib"))
from file_backup import create_rotating_backup
```

## Quick Start

```python
from pathlib import Path
from file_backup import create_rotating_backup

# Create backup with default settings (10 backups max)
config_file = Path("config.toml")
backup_path, success = create_rotating_backup(
    source_path=config_file,
    max_backups=10
)

if success:
    print(f"Backup created: {backup_path}")
```

## API Reference

### create_rotating_backup()

Create a timestamped backup of a file and rotate old backups.

```python
def create_rotating_backup(
    source_path: Path,
    backup_dir: Path | None = None,
    max_backups: int = 10,
    timestamp_format: str = "%Y%m%d_%H%M%S",
) -> tuple[Path | None, bool]:
```

**Parameters:**

- `source_path`: Path to file to backup (must exist)
- `backup_dir`: Directory for backup storage (default: `source_path.parent / '.{source_name}.backups'`)
- `max_backups`: Maximum number of backups to retain (default: 10)
- `timestamp_format`: strftime format for timestamp (default: ISO 8601 compatible)

**Returns:**

- Tuple of `(backup_path, success)`. `backup_path` is `None` if operation failed.

**Example:**

```python
# Custom backup directory and retention
backup_path, success = create_rotating_backup(
    source_path=Path("data/config.toml"),
    backup_dir=Path("backups"),
    max_backups=5,
    timestamp_format="%Y-%m-%d_%H%M"
)
```

### rotate_old_backups()

Delete oldest backups exceeding maximum retention limit.

```python
def rotate_old_backups(
    source_path: Path,
    backup_dir: Path,
    max_backups: int,
) -> list[Path]:
```

**Parameters:**

- `source_path`: Original file that was backed up
- `backup_dir`: Directory containing backup files
- `max_backups`: Maximum number of backups to retain

**Returns:**

- List of deleted backup file paths

**Example:**

```python
# Manually rotate backups to keep only 3
deleted = rotate_old_backups(
    source_path=Path("config.toml"),
    backup_dir=Path("backups"),
    max_backups=3
)
print(f"Deleted {len(deleted)} old backups")
```

### get_backup_files()

Find all backup files for a specific source file.

```python
def get_backup_files(
    source_path: Path,
    backup_dir: Path,
) -> list[Path]:
```

**Parameters:**

- `source_path`: Original file that was backed up
- `backup_dir`: Directory containing backup files

**Returns:**

- List of backup file paths sorted by age (oldest first)

**Example:**

```python
# List all backups
backups = get_backup_files(
    source_path=Path("config.toml"),
    backup_dir=Path("backups")
)
for backup in backups:
    print(f"Backup: {backup.name}")
```

## Backup Filename Format

Backups follow this naming convention:

```
{source_stem}.{timestamp}{source_suffix}
```

Examples:

- `config.20251030_091524.toml`
- `settings.20251030_143022.json`
- `data.20251030_160010.1.csv` (collision counter added)

## Backup Directory Structure

By default, backups are stored in a hidden directory next to the source file:

```
project/
├── config.toml                        # Original file
└── .config.toml.backups/              # Backup directory (hidden)
    ├── config.20251029_120000.toml    # Oldest backup
    ├── config.20251029_150000.toml
    ├── ...
    └── config.20251030_091524.toml    # Newest backup
```

Custom backup directories can be specified:

```
project/
├── config.toml                        # Original file
└── backups/                           # Custom backup directory
    ├── config.20251029_120000.toml
    └── ...
```

## Testing

Comprehensive pytest test suite with 18 tests:

```bash
cd projects/common_lib
python -m pytest tests/test_file_backup.py -v
```

Test coverage includes:

- Backup creation in default and custom directories
- Automatic directory creation
- Timestamp handling and collision resolution
- Rotation with various backup counts
- Edge cases and error handling
- Integration tests for full workflows

## Usage Examples

### Simple Backup on Save

```python
def save_config(config_path: Path, data: dict) -> bool:
    """Save config with automatic backup."""
    # Create backup before saving
    if config_path.exists():
        create_rotating_backup(config_path, max_backups=10)

    # Save new data
    with open(config_path, 'w') as f:
        json.dump(data, f)

    return True
```

### Custom Backup Location

```python
# Store backups in specific location
backup_dir = Path.home() / ".config" / "myapp" / "backups"
backup_path, success = create_rotating_backup(
    source_path=Path("~/.config/myapp/settings.json").expanduser(),
    backup_dir=backup_dir,
    max_backups=20
)
```

### Restore from Backup

```python
from file_backup import get_backup_files
import shutil

def restore_latest_backup(source_path: Path, backup_dir: Path) -> bool:
    """Restore most recent backup."""
    backups = get_backup_files(source_path, backup_dir)
    if not backups:
        return False

    # Get newest backup
    latest = backups[-1]

    # Restore
    shutil.copy2(latest, source_path)
    return True
```

## Requirements

- Linux environment
- Python 3.14+ (uses latest language features)
- Standard library only: `pathlib`, `datetime`, `shutil`

## License

MIT License - See repository LICENSE file
