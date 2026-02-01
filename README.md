# DFBU - DotFiles Backup Utility

**Version:** 0.6.0
**Author:** Chris Purcell
**Email:** <chris@l3digital.net>
**GitHub:** [L3DigitalNet/DFBU-DotFiles-Backup-Utility](https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility)
**License:** MIT
**Platform:** Linux Only

Modern Python 3.14+ desktop application for comprehensive Linux configuration file backup and restoration with a PySide6 GUI.

---

## Features

### Core Capabilities

- **Desktop GUI**: Modern PySide6 interface with MVVM architecture
- **TOML Configuration**: Structured config with Category/Subcategory/Application organization
- **Hostname-based Backups**: Automatic directory organization by hostname and date
- **Dual Backup Modes**:
  - Mirror backups with incremental file change detection
  - Compressed TAR.GZ archives with rotation and retention policies
- **Python 3.14 Path.copy()**: Enhanced file operations with metadata and symlink support
- **Interactive Restore**: Progress tracking and hostname-based restoration
- **MVVM Architecture**: Clean separation of concerns (GUI only)
- **Threaded Operations**: Non-blocking GUI with background workers
- **Window State Persistence**: Saves geometry and configuration paths

### Advanced Features

- **Pre-Restore Safety**: Automatic backup of files before restore operations
- **Enable/Disable Dotfiles**: Toggle individual files in configuration
- **Real-time Progress**: Visual progress bars and status updates
- **Configuration Backups**: Automatic config backup rotation before saves
- **Input Validation**: Comprehensive validation framework for all user inputs
- **Structured Logging**: Rotating logs with configurable levels and handlers
- **Type Safety**: Full type hint coverage with mypy compliance

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility.git
cd DFBU-DotFiles-Backup-Utility

# Run setup script (installs UV, creates venv, installs dependencies)
./setup.sh

# Activate virtual environment
source .venv/bin/activate
```

### Basic Usage

```bash
# Run the GUI application
python DFBU/dfbu-gui.py
```

### Configuration

Edit `DFBU/data/dfbu-config.toml`:

```toml
[options]
hostname = "myhost"
mirror_base_dir = "~/backups/mirror"
archive_base_dir = "~/backups/archives"
compression_level = 9
max_archives = 5

[[dotfiles]]
category = "Shell"
subcategory = "Bash"
application = "bashrc"
source_path = "~/.bashrc"
enabled = true
```

---

## Project Structure

```text
DFBU-DotFiles-Backup-Utility/
├── DFBU/                           # Main application directory
│   ├── dfbu-gui.py                 # GUI application entry point
│   ├── requirements.txt            # Python dependencies
│   ├── data/
│   │   └── dfbu-config.toml        # Default configuration file
│   ├── gui/                        # GUI components (MVVM)
│   │   ├── model.py                # Business logic and state (facade)
│   │   ├── viewmodel.py            # Presentation logic
│   │   ├── view.py                 # PySide6 UI components
│   │   ├── backup_orchestrator.py  # Backup/restore coordination
│   │   ├── config_manager.py       # Configuration management
│   │   ├── file_operations.py      # File system operations
│   │   ├── restore_backup_manager.py # Pre-restore safety backups
│   │   ├── statistics_tracker.py   # Operation metrics
│   │   ├── input_validation.py     # Input validation framework
│   │   ├── logging_config.py       # Logging configuration
│   │   └── designer/               # Qt Designer .ui files
│   ├── core/                       # Shared utilities
│   │   ├── common_types.py         # TypedDict definitions
│   │   └── validation.py           # Configuration validation
│   ├── tests/                      # Test suite (330+ tests)
│   │   ├── conftest.py             # Pytest fixtures
│   │   └── test_*.py               # Unit and integration tests
│   └── docs/                       # Project documentation
│       ├── CHANGELOG.md            # Version history
│       ├── ARCHITECTURE.md         # Architecture documentation
│       └── PROJECT-DOC.md          # Technical documentation
├── docs/                           # Additional documentation
│   ├── BRANCH_PROTECTION.md        # Branch protection docs
│   └── BRANCH_PROTECTION_QUICK.md  # Quick reference
├── .github/
│   ├── copilot-instructions.md     # GitHub Copilot guidelines
│   └── prompts/                    # Development prompts
├── .agents/                        # AI agent tools
│   ├── memory.instruction.md       # Coding preferences
│   └── branch_protection.py        # Branch protection checker
├── AGENTS.md                       # Quick agent reference
├── CLAUDE.md                       # Claude Code instructions
├── CONTRIBUTING.md                 # Contribution guidelines
├── scripts/                        # Setup scripts
│   └── setup.sh                    # Project setup script
├── pyproject.toml                  # Project configuration
└── README.md                       # This file
```

---

## Architecture

### MVVM Pattern (GUI)

The GUI follows the **Model-View-ViewModel** architectural pattern:

```
View (MainWindow)
    ↕ signals/slots
ViewModel (DFBUViewModel)
    ↕ method calls
Model (DFBUModel - Facade)
    ↕ coordinates
Components:
    ├── ConfigManager       # Config I/O and CRUD
    ├── FileOperations      # File system operations
    ├── BackupOrchestrator  # Backup/restore coordination
    └── StatisticsTracker   # Operation metrics
```

**Key Principles:**

- **Separation of Concerns**: Each layer has single, well-defined responsibilities
- **SOLID Principles**: Especially Single Responsibility and Dependency Inversion
- **Dependency Injection**: Components receive dependencies via constructors
- **Signal/Slot Communication**: Qt's event system for reactive updates
- **Threaded Operations**: Long-running tasks on background threads

### Model Components (v0.4.0+)

**DFBUModel (Facade - 583 lines)**

- Coordinates all model components via delegation
- Provides unified API to ViewModel
- Maintains backward compatibility

**ConfigManager (555 lines)**

- Configuration file I/O with rotating backups
- TOML parsing and serialization
- Dotfile CRUD operations
- Configuration validation integration

**FileOperations (620 lines)**

- Path expansion and validation
- File/directory copying with metadata preservation
- TAR.GZ archive creation and rotation
- Restore path reconstruction
- File comparison utilities

**BackupOrchestrator (420 lines)**

- Mirror backup coordination
- Archive backup coordination
- Restore operation coordination
- Progress tracking with callbacks
- Statistics integration

**StatisticsTracker (158 lines)**

- Operation metrics tracking
- Processing time calculation
- Success/skip/failure counters
- Statistics reset functionality

---

## Testing

### Test Suite Overview

- **Total Tests**: 330+
- **Overall Coverage**: 83%

### Running Tests

```bash
# All tests
pytest DFBU/tests/

# With coverage
pytest DFBU/tests/ --cov=DFBU --cov-report=html --cov-report=term-missing

# Specific categories
pytest DFBU/tests/ -m unit           # Unit tests only
pytest DFBU/tests/ -m integration    # Integration tests only
pytest DFBU/tests/ -m gui            # GUI tests only
pytest DFBU/tests/ -m "not slow"     # Skip slow tests

# Specific file
pytest DFBU/tests/test_model.py -v
```

### Test Organization

- **Unit Tests**: Fast, isolated component tests
- **Integration Tests**: Multi-component interaction tests
- **GUI Tests**: Qt-based signal/slot and worker tests
- **Fixtures**: Comprehensive fixture set in `conftest.py`

See [DFBU/tests/README.md](DFBU/tests/README.md) for detailed testing documentation.

---

## Dependencies

### Core Dependencies

- **Python 3.14+**: Required for `Path.copy()` with metadata preservation
- **PySide6**: Qt6 bindings for GUI (latest compatible version)
- **UV**: Fast Python package installer and virtual environment manager

### Standard Library Usage

- `pathlib`: Modern path handling
- `shutil`: File operations fallback
- `tarfile`: Archive creation
- `tomllib`: TOML parsing (Python 3.11+)
- `socket`: Hostname detection
- `datetime`: Timestamp generation

### Development Dependencies

- **pytest**: Test framework
- **pytest-qt**: Qt testing plugin
- **pytest-mock**: Mocking utilities
- **pytest-cov**: Coverage reporting
- **mypy**: Static type checking

---

## Configuration

### Options

```toml
[options]
hostname = "myhost"              # Auto-detected if empty
mirror_base_dir = "~/backups"    # Mirror backup destination
archive_base_dir = "~/archives"  # Archive backup destination
compression_level = 9            # 0-9 (0=no compression, 9=maximum)
max_archives = 5                 # Number of archives to retain
```

### Dotfiles

```toml
[[dotfiles]]
category = "Shell"               # Top-level category
subcategory = "Bash"             # Sub-category
application = "bashrc"           # Application name
source_path = "~/.bashrc"        # Source file path
enabled = true                   # Enable/disable in GUI
```

### Backup Structure

```
~/backups/
└── hostname/
    └── 2025-11-03/
        ├── home/
        │   └── .bashrc
        └── root/
            └── etc/
                └── config

~/archives/
└── hostname/
    ├── backup_2025-11-03_10-30-00.tar.gz
    ├── backup_2025-11-03_11-45-00.tar.gz
    └── ...
```

---

## Documentation

- **[CLAUDE.md](CLAUDE.md)**: Claude Code / AI agent instructions
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines
- **[DFBU/docs/CHANGELOG.md](DFBU/docs/CHANGELOG.md)**: Version history
- **[DFBU/docs/ARCHITECTURE.md](DFBU/docs/ARCHITECTURE.md)**: Architecture documentation
- **[DFBU/docs/PROJECT-DOC.md](DFBU/docs/PROJECT-DOC.md)**: Technical documentation
- **[docs/BRANCH_PROTECTION.md](docs/BRANCH_PROTECTION.md)**: Branch protection guide

---

## Known Issues

- No support for network paths or remote destinations
- Restore requires exact hostname match in backup directory structure
- No verification of successful copies or integrity checks
- Limited symlink support (follow_symlinks=True only)
- Comprehensive error handling deferred until v1.0.0

---

## Planned Features

- Differential backups with change detection (modification time)
- Enhanced restore with cross-hostname support
- Network path support for remote destinations
- Backup verification and integrity checking (hash comparison)
- Scheduled backups with timer automation
- Multiple configuration profiles
- Drag-and-drop file addition
- Dark mode theme
- Enhanced error handling for production (v1.0.0+)

---

## Development

### Branch Protection

**CRITICAL**: Always work on `testing` branch, never modify `main` directly.

```bash
# Check current branch before modifications
python .agents/branch_protection.py

# Switch to testing branch if needed
git checkout testing
```

See [docs/BRANCH_PROTECTION_QUICK.md](docs/BRANCH_PROTECTION_QUICK.md) for full details.

### Code Standards

- **Type Hints**: Mandatory on all functions, parameters, returns
- **Docstrings**: Required for all public APIs (Google or NumPy style)
- **MVVM Separation**: Strict layer boundaries (no Qt in Models)
- **SOLID Principles**: Single Responsibility, Dependency Inversion
- **Test Coverage**: Target 80%+ on critical paths
- **PEP 8**: Python style guidelines

### Setup for Development

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate
source .venv/bin/activate

# Install dependencies
uv pip install -r DFBU/requirements.txt

# Run type checking
mypy DFBU/

# Run tests with coverage
pytest DFBU/tests/ --cov=DFBU --cov-report=html
```

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Pull Request Process

1. Work on `testing` branch (never `main`)
2. Add/update tests for new functionality
3. Ensure 80%+ test coverage
4. Run `mypy` and fix all type errors
5. Update documentation
6. Follow commit message conventions
7. Submit PR to `testing` branch

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---

## Contact

**Chris Purcell**
Email: <chris@l3digital.net>
GitHub: [@L3DigitalNet](https://github.com/L3DigitalNet)

---

## Acknowledgments

- Python Software Foundation for Python 3.14
- Qt Project for Qt framework
- PySide6 maintainers for excellent Python bindings
- pytest community for robust testing tools

---

**Last Updated**: January 31, 2026
