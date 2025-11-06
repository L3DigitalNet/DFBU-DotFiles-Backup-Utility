# QUICKSTART - UI Design with Qt Designer and UV

## Key Points

1. **UI is NEVER hardcoded in Python** - All UI is designed in Qt Designer
2. **UV is used for all virtual environment management** - Not standard venv
3. **MVVM architecture is strictly followed** - Models, Views, ViewModels are separate

## Initial Setup

```bash
# Run setup script (installs UV, creates .venv, installs dependencies)
./setup.sh

# Activate virtual environment
source .venv/bin/activate
```

## Working with UI

### Creating New UI

```bash
# Open Qt Designer
designer

# Or edit existing UI file
designer src/views/ui/main_window.ui
```

### Key Steps

1. Design UI in Qt Designer
2. Set **objectName** for all interactive widgets
3. Save as `.ui` file in `src/views/ui/`
4. Load `.ui` file in Python using `QUiLoader`
5. Access widgets with `findChild()`

### Example Python Code

```python
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import os

class MyView(QMainWindow):
    def _load_ui(self):
        ui_file_path = os.path.join(
            os.path.dirname(__file__), 'ui', 'my_view.ui'
        )
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setCentralWidget(self.ui)

        # Access widgets by objectName
        self.button = self.ui.findChild(QPushButton, "myButton")
```

## Package Management with UV

```bash
# Install new package
uv pip install package-name

# Update requirements.txt
uv pip freeze > requirements.txt

# Install from requirements.txt
uv pip install -r requirements.txt
```

## Running the Application

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Run the application
python src/main.py

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=src tests/
```

## Important Files

- **UI_DESIGN_GUIDE.md** - Comprehensive UI design guide
- **AGENTS.md** - Quick reference for development
- **.github/copilot-instructions.md** - Full instructions for GitHub Copilot
- **.agents/memory.instruction.md** - Coding preferences and patterns

## Critical Rules

### UI Design ✅ DO

- Design ALL UI in Qt Designer
- Save .ui files to `src/views/ui/`
- Set objectName for widgets you need to access
- Use layouts for responsive design

### UI Design ❌ DON'T

- Never write `QPushButton("Text")` or similar in Python
- Never create layouts in Python (`QVBoxLayout()`, etc.)
- Never hardcode widget positioning
- Never mix .ui files with hardcoded UI

### Virtual Environment ✅ DO

- Use `uv venv` to create environments
- Use `uv pip install` for packages
- Activate `.venv` directory (not `venv`)
- Use `uv pip freeze` for requirements

### Virtual Environment ❌ DON'T

- Don't use `python -m venv`
- Don't use `pip install` directly
- Don't use old `venv/` directory
- Don't manually edit requirements.txt

## Architecture Quick Reference

### Model Layer

- Pure Python (no Qt imports)
- Business logic only
- Data validation
- Domain entities

### ViewModel Layer

- Inherits from QObject
- Defines signals for state changes
- Presentation logic
- Mediates between Model and View

### View Layer

- Loads .ui files from Qt Designer
- Finds widgets by objectName
- Connects signals to ViewModel
- Minimal logic (UI state only)

## New Feature Workflow

1. **Create Model** - `src/models/feature.py`
2. **Create ViewModel** - `src/viewmodels/feature_viewmodel.py`
3. **Design UI** - Qt Designer → `src/views/ui/feature_view.ui`
4. **Create View** - `src/views/feature_view.py` (loads .ui file)
5. **Write Tests** - `tests/unit/test_feature_*.py`
6. **Connect Everything** - Wire up in `src/main.py`

## Getting Help

- Read **UI_DESIGN_GUIDE.md** for Qt Designer details
- Check **AGENTS.md** for code patterns
- Review existing code (main_window.py) as example
- Consult **.github/copilot-instructions.md** for comprehensive guide

## Common Issues

**"Cannot find widget"**
→ Set objectName in Qt Designer Property Editor

**"Cannot open UI file"**
→ Check file path, ensure .ui file exists in src/views/ui/

**"UV not found"**
→ Run setup.sh or install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`

**"Virtual environment not activated"**
→ Run: `source .venv/bin/activate`
