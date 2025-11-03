---
mode: "agent"
description: "Initialize a Python virtual environment for PySide6 MVVM project and install dependencies"
---

# Initialize Python Virtual Environment

Set up a Python virtual environment for the PySide6 MVVM desktop application template.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

## Steps to Follow

1. **Check Python Version**: Verify Python 3.10+ is installed
2. **Remove Old Environment**: Delete existing `venv/` or `.venv/` if present
3. **Create Virtual Environment**: Create new venv in project root
4. **Activate Virtual Environment**: Activate the environment
5. **Install Dependencies**: Install packages from `requirements.txt`
6. **Verification**: Verify installation success

## Commands

### Check Python Version
```bash
python --version  # Should be 3.10 or higher
```

### Remove Old Environment
```bash
rm -rf venv/
# or
rm -rf .venv/
```

### Create Virtual Environment
```bash
python -m venv venv
# or use .venv
python -m venv .venv
```

### Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
# or
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Verify Installation
```bash
# Check PySide6 installed
python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"

# Check pytest installed
pytest --version

# List all installed packages
pip list
```

## Expected Dependencies

From `requirements.txt`:
- **PySide6**: Qt for Python GUI framework
- **pytest**: Testing framework
- **pytest-qt**: Qt testing support for pytest
- **pytest-mock**: Mocking support for pytest
- **pytest-cov**: Coverage reporting

## Guidelines

- **MANDATORY**: Remove old virtual environment before creating new one
- **RECOMMENDED**: Use `venv` name for consistency (already in .gitignore)
- **OPTIONAL**: Use alternative tools (virtualenv, conda) if preferred
- **OPTIONAL**: Install development tools (mypy, black, ruff) if needed

## Troubleshooting

### Issue: Python version too old
```bash
# Install Python 3.10+ from your package manager
sudo apt install python3.10  # Ubuntu/Debian
```

### Issue: PySide6 installation fails
```bash
# Install required system packages
sudo apt install python3-dev qt6-base-dev  # Ubuntu/Debian
```

### Issue: Permission denied
```bash
# Don't use sudo with pip in venv
# Recreate venv without sudo
```

## Alternative: Using uv (Fast Python Package Installer)

If you have `uv` installed:

```bash
# Remove old environment
rm -rf .venv/

# Create venv with uv
uv venv

# Activate
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

## Next Steps

After successful setup:

1. Run tests to verify: `pytest tests/`
2. Run the application: `python src/main.py`
3. Start developing following MVVM architecture
4. See `QUICKSTART.md` for development guide
