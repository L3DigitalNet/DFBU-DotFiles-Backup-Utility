---
mode: "agent"
description: "Perform comprehensive testing for PySide6 MVVM applications using Pytest and pytest-qt"
---

# Testing Management for PySide6 MVVM Applications

Handle comprehensive testing of PySide6 MVVM desktop applications following architectural principles using Pytest and pytest-qt.

## Core Testing Requirements

### Test File Organization - MANDATORY
- **MUST** store ALL test files in each project's `DFBU/tests/` directory
- **NEVER** place test files in base project directory
- **INCLUDE** pytest tests, unit tests, example scripts, test configs in `DFBU/tests/`
- **MIRROR** source code structure in test directory organization
- **MAINTAIN** clear separation between different test types

### PyTest Standards - REQUIRED
- **MUST** write unit tests for ALL business logic
- **MUST** follow AAA pattern: Arrange, Act, Assert
- **TARGET** 80%+ test coverage for critical paths
- **MUST** use descriptive test names that explain expected behavior
- **MUST** keep tests fast, isolated, and deterministic
- **MUST** ensure tests are discoverable by pytest

## Test Generation Principles

### Unit Test Structure
```python
def test_function_name_should_behavior_when_condition():
    """Test that function_name produces expected behavior under specific condition."""
    # Arrange
    input_data = create_test_data()
    expected_result = define_expected_outcome()

    # Act
    actual_result = function_to_test(input_data)

    # Assert
    assert actual_result == expected_result
```

### Test Categories and Focus
- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test interactions between modules and components
- **Functional Tests**: Test complete workflows and user scenarios
- **Performance Tests**: Test timing and resource usage for critical operations

## MVVM Testing Strategy

### Model Layer Testing
- **TEST** business logic in isolation (no Qt dependencies)
- **VALIDATE** data validation and transformation
- **CHECK** domain entity behavior
- **NO** UI dependencies or Qt imports
- **USE** standard pytest fixtures

### ViewModel Layer Testing
- **TEST** signal emissions using `pytest-qt`
- **MOCK** Model and Service dependencies
- **VALIDATE** state management
- **CHECK** proper signal/slot behavior
- **USE** `qtbot` fixture for Qt testing
- **VERIFY** no direct widget manipulation

### View Layer Testing (Optional)
- **FOCUS** on ViewModel and Model testing
- **VIEW** tests are optional for template
- **IF TESTED**: Use `qtbot` and QApplication
- **VALIDATE** signal connections if needed
- **KEEP** tests simple and focused

### Integration Testing
- **TEST** interactions between layers
- **VALIDATE** dependency injection works
- **CHECK** signal flow across boundaries
- **TEST** complete user workflows

## Type Safety and Validation Testing

### Type Hint Verification
- **VERIFY** runtime behavior matches type annotations
- **TEST** that functions accept and return expected types
- **VALIDATE** collection types and their contents
- **CHECK** protocol implementations and interface compliance
- **ENSURE** generic types work correctly with various type parameters

### Contract Testing
- **TEST** public interfaces behave as documented
- **VERIFY** function preconditions and postconditions
- **VALIDATE** class invariants and state consistency
- **CHECK** module boundaries and interaction points

## Coverage Analysis and Reporting

### Coverage Targets and Priorities
- **TARGET** 80%+ coverage for critical business logic paths
- **PRIORITIZE** core functionality over defensive error handling
- **FOCUS** on testing actual program behavior patterns
- **MEASURE** coverage of happy path scenarios and expected workflows
- **IDENTIFY** gaps in business logic testing

### Coverage Tools and Configuration
```python
# pytest configuration in pyproject.toml
[tool.pytest.ini_options]
testpaths = ["DFBU/tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=DFBU",
    "--cov-report=term-missing",
    "--cov-report=html",
]
```

## Testing Best Practices

### Test Data and Fixtures
- **CREATE** reusable test data and setup functions
- **USE** pytest fixtures for common test resources
- **MAINTAIN** clear test data organization
- **AVOID** hardcoded test values that obscure test intent
- **SEPARATE** test data from test logic

### Mocking and Isolation
- **USE** proper mocking of external dependencies
- **ISOLATE** units under test from complex dependencies
- **MOCK** file system operations, network calls, and external services
- **MAINTAIN** clear boundaries between real and mocked components
- **VALIDATE** mock usage doesn't obscure actual behavior

### Test Performance and Reliability
- **ENSURE** tests run quickly (target < 1 second per test)
- **MAKE** tests deterministic and repeatable
- **AVOID** tests that depend on external resources or timing
- **ELIMINATE** flaky tests that pass/fail inconsistently
- **OPTIMIZE** test execution time without sacrificing coverage

## Repository Integration

### QApplication Fixture
Ensure `DFBU/tests/conftest.py` has:
```python
import pytest
from PySide6.QtWidgets import QApplication

@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
```

### Python Standard Library and Mocking
- **USE** unittest.mock or pytest-mock for mocking
- **MOCK** Service dependencies in ViewModel tests
- **ISOLATE** units under test
- **VERIFY** mock interactions with `assert_called_once()` etc.

### Example Tests

#### Model Test
```python
def test_model_validation():
    """Test that model validates data correctly."""
    # Arrange
    model = ExampleModel(value="test")

    # Act
    is_valid = model.validate()

    # Assert
    assert is_valid is True
```

#### ViewModel Test with Signals
```python
def test_viewmodel_emits_signal(qtbot, mocker):
    """Test that viewmodel emits signal when data changes."""
    # Arrange
    mock_service = mocker.Mock()
    mock_service.fetch.return_value = ["item1"]
    vm = ExampleViewModel(mock_service)

    # Act & Assert
    with qtbot.waitSignal(vm.data_changed, timeout=1000) as blocker:
        vm.load_data()

    assert blocker.args[0] == ["item1"]
    mock_service.fetch.assert_called_once()
```

## Testing Decision Framework

### When writing tests, prioritize:
1. **Core Business Logic**: Does this function perform critical business operations?
2. **Public Interfaces**: Is this function part of the public API?
3. **Integration Points**: Does this component interact with other modules?
4. **Type Safety**: Are the type annotations and behavior consistent?
5. **Happy Path Coverage**: Are the expected use cases thoroughly tested?
