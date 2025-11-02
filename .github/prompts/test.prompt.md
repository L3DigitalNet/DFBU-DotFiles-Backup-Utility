---
mode: "agent"
description: "Perform comprehensive testing using Pytest, focusing on unit tests, coverage analysis, and type validation"
---

# Testing Management and Coverage

Handle comprehensive testing of project following repository guidelines and clean architecture principles using Pytest.

## Core Testing Requirements

### Test File Organization - MANDATORY
- **MUST** store ALL test files in each project's `/tests/` directory
- **NEVER** place test files in base project directory
- **INCLUDE** pytest tests, unit tests, example scripts, test configs in `/tests/`
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

### Version-Aware Testing Strategy

#### Pre-v1.0.0 Focus (Current Phase)
- **FOCUS** on core functionality testing and business logic validation
- **MINIMIZE** error handling and edge case testing (defer until v1.0.0)
- **PRIORITIZE** happy path testing and expected behavior patterns
- **TEST** clean architecture and confident design patterns
- **VALIDATE** proper initialization sequences and program flow

#### Test Architecture Alignment
- **REFLECT** confident design patterns in test structure
- **AVOID** excessive defensive testing for scenarios that shouldn't occur
- **FOCUS** on testing actual program behavior and constraints
- **VALIDATE** type hints and documented interfaces
- **TEST** clear, linear program flow expectations

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
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=html --cov-report=term-missing"
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

### Shared Testing Utilities
- **USE** `projects/common_lib/` for shared test utilities and fixtures
- **CREATE** reusable testing patterns and helpers
- **MAINTAIN** consistency across project test suites
- **ELIMINATE** duplicate testing code through shared utilities

### Python Standard Library Focus
- **PREFER** built-in testing capabilities and assert statements
- **USE** unittest.mock for mocking needs
- **LEVERAGE** built-in modules for test data generation
- **MINIMIZE** external testing dependencies beyond pytest

### Linux Environment Compliance
- **IMPORTANT** All tests designed for Linux environments only
- **TEST** Linux-specific paths, commands, and system calls
- **NOT COMPATIBLE** with Windows environments
- **VALIDATE** proper behavior on target Linux systems

## Testing Decision Framework

### When writing tests, prioritize:
1. **Core Business Logic**: Does this function perform critical business operations?
2. **Public Interfaces**: Is this function part of the public API?
3. **Integration Points**: Does this component interact with other modules?
4. **Type Safety**: Are the type annotations and behavior consistent?
5. **Happy Path Coverage**: Are the expected use cases thoroughly tested?
