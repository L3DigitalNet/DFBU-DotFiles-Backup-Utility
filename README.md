# DFBU-DotFiles-Backup-Utility

DFBU is a backup utility originally intended for dotfiles management but was expanded to centralize my other backup needs into a single utility. Includes a limited CLI utility and and GUI application with extended functionality.

## Setup

After cloning, run the setup script to configure Git hooks:

```bash
./setup-git-hooks.sh
```

See [Git Hooks Setup](.github/GIT_HOOKS_SETUP.md) for details.

## Architecture: Independent CLI and GUI Tools

DFBU provides two completely independent tools that can be used separately or together:

### CLI Tool (`dfbu.py`)

- **Standalone**: Self-contained with no external dependencies beyond Python standard library
- **Lightweight**: Command-line interface for backup and restore operations
- **Dependencies**: Python 3.14+ standard library only
- **Can be deleted**: Remove `dfbu.py` without affecting GUI functionality

### GUI Tool (`dfbu-gui.py` + `gui/` directory)

- **Standalone**: Self-contained within the `gui/` directory
- **Feature-rich**: Desktop application with MVVM architecture using PySide6
- **Dependencies**: Python 3.14+, PySide6, tomli-w (see `requirements.txt`)
- **Can be deleted**: Remove `dfbu-gui.py` and `gui/` directory without affecting CLI functionality

### Why This Design?

This independent architecture allows users to:

- **Use only what they need**: Install just the CLI for lightweight systems, or just the GUI for desktop environments
- **Reduce dependencies**: CLI users don't need PySide6 and GUI dependencies
- **Maintain flexibility**: Each tool can evolve independently without breaking the other
- **Simplify deployment**: Distribute CLI or GUI separately for different use cases

### File Structure

```text
DFBU/
├── dfbu.py              # CLI tool (independent)
├── dfbu-gui.py          # GUI tool entry point
├── gui/                 # GUI tool modules
│   ├── __init__.py
│   ├── model.py         # Business logic layer
│   ├── view.py          # UI presentation layer
│   └── viewmodel.py     # Presentation logic layer
├── data/                # Shared configuration files
│   └── dfbu-config.toml
├── requirements.txt     # GUI dependencies only
└── docs/                # Documentation
```
