# DFBU - DotFiles Backup Utility

A simple GUI application to backup and restore your Linux configuration files.

**Version:** 1.2.0 | **Platform:** Linux | **License:** MIT

---

## Why DFBU?

Your dotfiles (`.bashrc`, `.config/`, `.local/share/`) contain years of customization - shell aliases, app settings, themes, and preferences. Losing them means hours of reconfiguration.

DFBU protects your configuration with:

- **Visual interface** - No command line needed for daily use
- **One-click backups** - Select files, click backup, done
- **Automatic organization** - Backups sorted by computer name and date
- **Safe restores** - Creates a safety backup before overwriting any files
- **Size warnings** - Alerts you before backing up unexpectedly large files
- **Flexible storage** - Choose mirror copies, compressed archives, or both

---

## Screenshots

Screenshots coming soon - main window, backup in progress, restore dialog

---

## Installation

### Quick Setup

```bash
# 1. Download DFBU
git clone https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility.git
cd DFBU-DotFiles-Backup-Utility

# 2. Run the setup script (installs Python 3.14 and dependencies)
./scripts/setup.sh

# 3. Launch DFBU
source .venv/bin/activate
python DFBU/dfbu_gui.py
```

### Requirements

- **Linux** - Tested on Ubuntu 22.04+, Fedora 38+, and other modern distributions
- **Python 3.14+** - The setup script installs this automatically via UV package manager

---

## Using DFBU

### First Launch

When you first open DFBU, you'll see the **Backup** tab with an empty file list. To add files to backup:

1. Click **Add Dotfile** in the toolbar
2. Enter the application name (e.g., "Bash")
3. Enter the path to backup (e.g., `~/.bashrc`)
4. Optionally add tags to organize your files
5. Click **Add**

DFBU comes with a library of common dotfiles you can browse and add.

### Backup Tab

The main tab shows all your configured dotfiles. Each entry displays:

- Application name and description
- File paths being backed up
- Tags for organization

To run a backup:

1. Ensure the files you want are checked (all are selected by default)
2. Choose your backup options (Mirror, Archive, or both)
3. Click **Start Backup**
4. Watch the progress bar and log for status

### Restore Tab

To restore files from a previous backup:

1. Switch to the **Restore** tab
2. Browse to your backup directory
3. Select the backup date to restore from
4. Choose which files to restore
5. Click **Restore**

DFBU automatically creates a safety backup of your current files before restoring, so you can always undo a restore.

### Settings Tab

Configure backup behavior:

- **Mirror Directory** - Where to store mirror backups
- **Archive Directory** - Where to store compressed archives
- **Hostname Subdirectory** - Organize backups by computer name
- **Date Subdirectory** - Create dated folders for each backup
- **Archive Compression** - Set compression level (0-9)
- **Archive Rotation** - Keep only the last N archives
- **Pre-Restore Backup** - Safety backup before restoring (recommended)
- **Size Warnings** - Alert thresholds for large files

---

## Backup Modes

DFBU offers two backup modes that can be used together or separately.

### Mirror Backup

Creates an exact copy of your files in a backup folder.

Advantages:

- Files are immediately accessible - just browse the folder
- Easy to see exactly what's backed up
- Fast for incremental backups (only changed files are copied)

Best for quick access to recent backups and browsing backup contents.

### Archive Backup

Compresses all files into a single `.tar.gz` archive.

Advantages:

- Saves disk space with compression
- Creates a single file that's easy to transfer
- Keeps multiple versions with date-stamped names

Best for long-term storage and transferring backups between machines.

---

## Backup Location Structure

DFBU organizes your backups like this:

```
~/backups/                          # Your backup directory
└── my-computer/                    # Organized by hostname
    └── 2026-02-01/                 # Organized by date
        ├── home/
        │   └── .bashrc             # Your backed up files
        │   └── .config/
        │       └── konsole/
        └── ...

~/archives/                         # Your archive directory
└── my-computer/
    ├── backup_2026-02-01_10-30.tar.gz
    ├── backup_2026-01-28_14-15.tar.gz
    └── ...
```

---

## Troubleshooting

### Common Issues

#### "Python 3.14+ required"

Run `./scripts/setup.sh` again - it will install Python 3.14 via UV.

#### "Permission denied" when backing up

DFBU can only backup files your user can read. System files in `/etc/` may need special handling.

#### Backup is unexpectedly large

Some dotfile directories (like `.cache/` or browser profiles) can be huge. Use the size warning feature to identify large files, and add patterns to `.dfbuignore` to exclude cache directories.

#### Restore button is grayed out

Select a valid backup directory first. Ensure the backup contains files for the current hostname.

### Getting Help

- Check the [full troubleshooting guide](docs/TROUBLESHOOTING.md)
- Report issues on [GitHub](https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility/issues)

---

## For Developers

DFBU is built with Python 3.14 and PySide6 following the MVVM architectural pattern.

For development setup, code standards, architecture documentation, and contribution guidelines, see:

- [CONTRIBUTING.md](CONTRIBUTING.md) - Development setup and guidelines
- [DFBU/docs/ARCHITECTURE.md](DFBU/docs/ARCHITECTURE.md) - Technical architecture
- [docs/INDEX.md](docs/INDEX.md) - Full documentation index

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Contact

**Chris Purcell**

- Email: <chris@l3digital.net>
- GitHub: [@L3DigitalNet](https://github.com/L3DigitalNet)

---

Last Updated: February 2026
