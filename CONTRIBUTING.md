# Contributing to Template Desktop Application

Thank you for your interest in contributing to this template! This guide will help you get started.

## Development Setup

### Prerequisites

- Python 3.14
- Git
- Linux operating system
- Basic understanding of PySide6 and MVVM architecture

### Initial Setup

1. Fork and clone the repository:

   ```bash
   git clone <your-fork-url>
   cd Template-Desktop-Application
   ```

2. Run the setup script (checks Python 3.14, creates venv, installs dependencies):

   ```bash
   ./setup.sh
   ```

3. Activate the virtual environment:

   ```bash
   source venv/bin/activate
   ```

## Architecture Guidelines

This template follows strict architectural principles:

### MVVM Pattern

- **Models** (`src/models/`): Pure Python, no Qt dependencies
- **ViewModels** (`src/viewmodels/`): QObject-based, signals for state changes
- **Views** (`src/views/`): PySide6 widgets, minimal logic

### SOLID Principles

All code must adhere to SOLID principles:

- **S**ingle Responsibility
- **O**pen/Closed
- **L**iskov Substitution
- **I**nterface Segregation
- **D**ependency Inversion

See `.github/copilot-instructions.md` for detailed guidelines.

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Write Tests First (TDD)

```bash
# Create test file
touch tests/unit/test_your_feature.py

# Write tests
# Run tests (they should fail initially)
pytest tests/unit/test_your_feature.py
```

### 3. Implement Feature

Follow the MVVM structure:

```bash
# Create model
touch src/models/your_feature.py

# Create viewmodel
touch src/viewmodels/your_feature_viewmodel.py

# Create view
touch src/views/your_feature_view.py
```

### 4. Run Tests

```bash
# All tests
pytest tests/

# With coverage
pytest --cov=src --cov-report=html tests/

# Specific test file
pytest tests/unit/test_your_feature.py -v
```

### 5. Code Quality Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
pylint src/
```

### 6. Commit Changes

Follow conventional commit format:

```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug in component"
git commit -m "docs: update README"
git commit -m "test: add tests for feature"
```

### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Standards

### Type Hints

Always use type hints:

```python
def process_data(items: List[str], config: Optional[dict] = None) -> bool:
    """Process data with optional configuration."""
    return True
```

### Docstrings

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> dict:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Dictionary containing results.

    Raises:
        ValueError: If param2 is negative.
    """
```

### Testing

- Use Arrange-Act-Assert pattern
- One assertion per test (when possible)
- Descriptive test names: `test_should_X_when_Y`
- Mock external dependencies

Example:

```python
def test_viewmodel_emits_signal_when_data_loaded(qtbot, mocker):
    # Arrange
    mock_service = mocker.Mock()
    viewmodel = MyViewModel(mock_service)

    # Act
    with qtbot.waitSignal(viewmodel.data_loaded):
        viewmodel.load_data()

    # Assert
    mock_service.fetch_data.assert_called_once()
```

## What to Contribute

### Good Contributions

✅ Bug fixes with tests
✅ New features following MVVM/SOLID
✅ Documentation improvements
✅ Test coverage improvements
✅ Performance optimizations
✅ Example implementations

### Changes That Need Discussion

⚠️ Breaking API changes
⚠️ New dependencies
⚠️ Architecture changes
⚠️ Major refactoring

Please open an issue first to discuss these.

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Code follows MVVM architecture
- [ ] SOLID principles maintained
- [ ] All tests pass (`pytest tests/`)
- [ ] New features have tests
- [ ] Code is formatted (`black`, `isort`)
- [ ] Type hints added to all functions
- [ ] Docstrings added to public APIs
- [ ] No linting errors (`pylint src/`)
- [ ] Type checking passes (`mypy src/`)
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventional format

## Running the Full Check Suite

```bash
# Format code
black src/ tests/
isort src/ tests/

# Run tests with coverage
pytest --cov=src --cov-report=html tests/

# Type check
mypy src/

# Lint
pylint src/

# Run application
python src/main.py
```

## Directory Structure

```
Template-Desktop-Application/
├── src/
│   ├── models/         # Pure Python business logic
│   ├── viewmodels/     # Presentation logic with Qt signals
│   ├── views/          # PySide6 UI components
│   ├── services/       # External integrations
│   └── utils/          # Helper functions
├── tests/
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── .github/
│   ├── copilot-instructions.md  # AI assistant instructions
│   └── workflows/      # CI/CD pipelines
└── .agents/
    └── memory.instruction.md    # Coding standards
```

## Common Patterns

See `AGENTS.md` for:

- File templates
- Testing patterns
- Signal/slot patterns
- Dependency injection examples
- Troubleshooting guide

## Getting Help

- Check `AGENTS.md` for quick reference
- Review `.github/copilot-instructions.md` for detailed guidelines
- Review existing code for patterns
- Open an issue for questions
- Join discussions in pull requests

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

Feel free to open an issue for any questions or clarifications!
