# Quick Start Guide

This guide will help you get started with the Template Desktop Application in under 5 minutes.

**Requirements:** Python 3.14 on Linux

## 1. Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd Template-Desktop-Application

# Run setup script (checks Python 3.14, creates venv, installs dependencies)
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

## 2. Run the Application (30 seconds)

```bash
python src/main.py
```

You should see a window with:

- "Load Data" button
- "Clear" button
- Item list
- Details view
- Status bar

Try clicking "Load Data" to see the example in action!

## 3. Run Tests (1 minute)

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Open coverage report
xdg-open htmlcov/index.html
```

## 4. Explore the Code (2 minutes)

### Look at the MVVM Structure

1. **Model** - Pure Python business logic:

   ```bash
   cat src/models/example_model.py
   ```

2. **ViewModel** - Presentation logic with Qt signals:

   ```bash
   cat src/viewmodels/main_viewmodel.py
   ```

3. **View** - PySide6 UI components:

   ```bash
   cat src/views/main_window.py
   ```

4. **Service** - External operations:

   ```bash
   cat src/services/example_service.py
   ```

### Check the Tests

```bash
# Model tests
cat tests/unit/test_example_model.py

# ViewModel tests
cat tests/unit/test_main_viewmodel.py

# Integration tests
cat tests/integration/test_application.py
```

## 5. Create Your First Feature

### Example: Add a "Count" feature

1. **Create the Model** (`src/models/counter.py`):

   ```python
   from dataclasses import dataclass

   @dataclass
   class Counter:
       value: int = 0

       def increment(self) -> int:
           self.value += 1
           return self.value
   ```

2. **Create the ViewModel** (`src/viewmodels/counter_viewmodel.py`):

   ```python
   from PySide6.QtCore import QObject, Signal, Slot
   from models.counter import Counter

   class CounterViewModel(QObject):
       count_changed = Signal(int)

       def __init__(self):
           super().__init__()
           self._counter = Counter()

       @Slot()
       def increment(self):
           new_value = self._counter.increment()
           self.count_changed.emit(new_value)
   ```

3. **Add to View** (modify `src/views/main_window.py`):

   ```python
   # In _setup_ui():
   self._count_button = QPushButton("Count")
   self._count_label = QLabel("Count: 0")

   # In _connect_signals():
   self._count_button.clicked.connect(counter_vm.increment)
   counter_vm.count_changed.connect(
       lambda v: self._count_label.setText(f"Count: {v}")
   )
   ```

4. **Write Tests** (`tests/unit/test_counter.py`):

   ```python
   from src.models.counter import Counter

   def test_counter_increments():
       counter = Counter()
       result = counter.increment()
       assert result == 1
       assert counter.value == 1
   ```

5. **Run Tests**:

   ```bash
   pytest tests/unit/test_counter.py -v
   ```

## Understanding the Architecture

### MVVM Flow

```text
User Action (View) → Signal → ViewModel Method → Service/Model → Signal → View Update
```

Example from the template:

1. User clicks "Load Data" button
2. View emits signal to ViewModel.load_data()
3. ViewModel calls Service.fetch_data()
4. Service returns Models
5. ViewModel processes Models
6. ViewModel emits data_loaded signal
7. View receives signal and updates UI

### Dependency Injection

See `src/main.py` for the DI pattern:

```python
# Create dependencies (bottom-up)
service = ExampleService()           # Infrastructure
viewmodel = MainViewModel(service)   # Presentation
view = MainWindow(viewmodel)         # UI
```

## Key Files to Review

### For Development

- `AGENTS.md` - Quick reference and patterns
- `.github/copilot-instructions.md` - Comprehensive guidelines
- `CONTRIBUTING.md` - Contribution guidelines

### For Configuration

- `pyproject.toml` - Python project configuration
- `requirements.txt` - Dependencies
- `.github/workflows/ci.yml` - CI/CD pipeline

## Next Steps

1. **Read the docs**:
   - `README.md` - Project overview
   - `AGENTS.md` - Development patterns
   - `.github/copilot-instructions.md` - Detailed guidelines

2. **Explore the code**:
   - Run the application and click around
   - Read the example implementations
   - Look at the tests to understand patterns

3. **Make it yours**:
   - Remove example files
   - Add your own features
   - Follow the MVVM pattern
   - Write tests for everything

4. **Get help**:
   - Check `AGENTS.md` for common patterns
   - Review tests for examples
   - Open an issue if stuck

## Common Commands

```bash
# Development
python src/main.py                    # Run application
pytest tests/ -v                      # Run tests
pytest --cov=src tests/               # Run with coverage

# Code Quality
black src/ tests/                     # Format code
isort src/ tests/                     # Sort imports
mypy src/                             # Type check
pylint src/                           # Lint code

# Git
git checkout -b feature/my-feature    # Create branch
git commit -m "feat: add feature"     # Commit
git push origin feature/my-feature    # Push
```

## Tips

1. **Always write tests first** - TDD helps design better APIs
2. **Keep MVVM layers separated** - No Qt in Models, no business logic in Views
3. **Use dependency injection** - Pass dependencies via constructors
4. **Use signals for communication** - Don't call methods across layers directly
5. **Type hint everything** - Makes code self-documenting
6. **Run tests frequently** - Catch issues early

## Troubleshooting

### "QApplication not created"

Add `qapp` fixture to your test:

```python
def test_something(qapp):
    # Your test
```

### "Import error"

Make sure virtual environment is activated:

```bash
source venv/bin/activate
```

### "Tests fail"

Run with verbose output:

```bash
pytest tests/ -v -s
```

## You're Ready

You now have:

- ✅ A working PySide6 application
- ✅ MVVM architecture in place
- ✅ Tests passing
- ✅ CI/CD configured
- ✅ Comprehensive documentation

Start building your application! 🚀
