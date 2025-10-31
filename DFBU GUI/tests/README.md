# DFBU GUI Test Suite

Comprehensive test suite for the DFBU GUI application following repository testing guidelines and clean architecture principles.

## Overview

This test suite provides thorough coverage of the DFBU GUI MVVM architecture with focus on:

- **Model Layer**: Business logic, configuration management, file operations
- **ViewModel Layer**: Presentation logic, commands, worker threads
- **Type Safety**: Runtime validation of type hints and TypedDict structures
- **Happy Path Testing**: Core functionality before v1.0.0 as per confident design pattern

## Test Structure

### Model Layer Tests

#### `test_model_core.py` (28 tests)

Core model functionality and foundational components:

- `BackupStatistics` data class operations
- Model initialization and default values
- Path expansion and assembly logic
- Permission checking and file access
- Statistics tracking and recording

#### `test_model_config.py` (25 tests)

Configuration management operations:

- TOML configuration loading and parsing
- Configuration validation with defaults
- Options validation and type safety
- Configuration saving with rotating backups
- Option and path updates

#### `test_model_dotfiles.py` (29 tests)

Dotfile management operations:

- Adding dotfiles with metadata
- Updating dotfile entries
- Removing dotfiles from configuration
- Toggling enabled/disabled status
- Path validation and existence checking
- Size calculation for files and directories
- Dotfile accessor methods

### Running Tests

#### Run All Tests

```bash
cd "projects/DFBU GUI"
python -m pytest tests/ -v
```

#### Run Specific Test File

```bash
python -m pytest tests/test_model_core.py -v
python -m pytest tests/test_model_config.py -v
python -m pytest tests/test_model_dotfiles.py -v
```

#### Run Tests with Coverage

```bash
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

#### Run Using Test Runner

```bash
python tests/run_tests.py
```

### Test Statistics

**Total Tests**: 82
**Current Status**: All passing ✓
**Coverage Focus**: Model layer business logic (80%+ target)

### Test Organization

Tests follow the AAA (Arrange-Act-Assert) pattern:

```python
def test_example_behavior(self) -> None:
    """Test that feature behaves correctly under specific condition."""
    # Arrange - Set up test data and conditions
    model = DFBUModel(config_path)

    # Act - Execute the behavior being tested
    result = model.some_operation()

    # Assert - Verify expected outcomes
    assert result == expected_value
```

### Test Fixtures

Reusable fixtures for common test scenarios:

- `tmp_path`: Pytest built-in for temporary directories
- `model`: Basic model instance with test configuration
- `model_with_config`: Model with loaded configuration
- `model_with_dotfiles`: Model with multiple dotfile entries
- `sample_config_dict`: Complete sample configuration data

### Testing Principles

Following repository testing guidelines:

1. **Standard Library First**: Minimal external dependencies beyond pytest
2. **Type Safety**: Validate TypedDict structures and type hints
3. **Happy Path Focus**: Core functionality testing before v1.0.0
4. **Confident Design**: Test expected program flow, not defensive scenarios
5. **Isolation**: Each test is independent and can run in any order
6. **Fast Execution**: All tests complete in under 1 second
7. **Clear Intent**: Descriptive test names explain expected behavior

### Future Test Files (Planned)

- `test_model_file_operations.py`: File copying and directory operations
- `test_viewmodel_commands.py`: ViewModel command patterns
- `test_viewmodel_workers.py`: Worker thread operations
- `test_mvvm_integration.py`: Integration between MVVM layers
- `test_type_safety.py`: Comprehensive type hint validation

## Requirements

- Linux environment
- Python 3.14+ for latest language features
- pytest framework for testing
- pytest-cov for coverage reporting (optional)
- PySide6 for Qt framework components

## Test Categories

### Unit Tests

Test individual functions and methods in isolation:

- Model methods: path operations, validation, statistics
- Configuration parsing and validation
- Dotfile management operations

### Integration Tests (Planned)

Test interactions between components:

- MVVM communication patterns
- Worker thread coordination
- Signal/slot connections

### Type Safety Tests (Planned)

Validate runtime behavior matches type annotations:

- TypedDict structure validation
- Function parameter type checking
- Return value type verification

## Contributing

When adding new tests:

1. Follow AAA pattern for test structure
2. Use descriptive test names explaining expected behavior
3. Include docstrings describing what is being tested
4. Keep tests focused on single behavior
5. Use fixtures for reusable test data
6. Ensure tests are fast and isolated
7. Focus on happy path and core functionality

## Notes

- Tests avoid testing GUI components directly (View layer) due to Qt complexity
- Focus on business logic and data flow rather than UI interactions
- Error handling tests deferred until v1.0.0 per confident design pattern
- Tests validate type safety through runtime behavior, not static analysis
