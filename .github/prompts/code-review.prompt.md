---
description: "Comprehensive code review following MVVM architecture and SOLID principles"
mode: "agent"
---

# Comprehensive Code Review for PySide6 MVVM Application

Perform a complete code review of the project following MVVM architecture, SOLID principles, and repository guidelines.

## General Guidelines

- **MANDATORY**: Do not change any code logic or implementation, only suggest improvements
- **MANDATORY**: Follow all repository guidelines in ![copilot-instructions.md](../copilot-instructions.md)
- **MANDATORY**: Follow quick reference in ![AGENTS.md](../../AGENTS.md)

## Core Standards

- **Python 3.10+ REQUIRED**: Minimum version for PySide6 compatibility
- **Type hints MANDATORY**: ALL functions, methods, parameters, return values
- **PEP 8 compliance**: Strict formatting and style requirements
- **Docstrings REQUIRED**: Google or NumPy style for all public APIs
- **Modern Python**: Use `str | None` not `Optional[str]`, `list[str]` not `List[str]`

## MVVM Architecture Review (CRITICAL)

### Model Layer (`src/models/`)
- **VERIFY**: No Qt imports (no PySide6, no QObject)
- **VERIFY**: Pure Python business logic only
- **VERIFY**: No UI concerns or dependencies
- **VERIFY**: Uses `@dataclass` for simple data containers
- **VERIFY**: Domain-specific validation and exceptions
- **CHECK**: Proper separation of concerns
- **CHECK**: DRY principle applied

### ViewModel Layer (`src/viewmodels/`)
- **VERIFY**: Inherits from `QObject` for signals/slots
- **VERIFY**: Defines signals for state changes
- **VERIFY**: Accepts dependencies through constructor (dependency injection)
- **VERIFY**: No direct widget manipulation
- **VERIFY**: No business logic (delegates to Model/Service)
- **CHECK**: Testable without UI instantiation
- **CHECK**: Proper signal naming and usage

### View Layer (`src/views/`)
- **VERIFY**: Inherits from appropriate Qt widget class
- **VERIFY**: Accepts ViewModel in constructor
- **VERIFY**: Connects signals/slots in `__init__` or `setup_connections()`
- **VERIFY**: Minimal logic (only UI state management)
- **VERIFY**: No business logic or data validation
- **CHECK**: Proper widget initialization
- **CHECK**: Signal/slot connections are clear

## SOLID Principles Review

### Single Responsibility Principle (SRP)
- **CHECK**: Each class has one clear purpose
- **CHECK**: Separation of concerns maintained
- **CHECK**: UI event handling separated from business logic

### Open/Closed Principle (OCP)
- **CHECK**: Use of abstract base classes for extensibility
- **CHECK**: Composition over inheritance
- **CHECK**: Dependency injection used

### Liskov Substitution Principle (LSP)
- **CHECK**: Derived classes are substitutable for base classes
- **CHECK**: Consistent contracts in inheritance

### Interface Segregation Principle (ISP)
- **CHECK**: Focused interfaces/protocols
- **CHECK**: No unused methods in interfaces
- **CHECK**: Python `Protocol` used for type hints

### Dependency Inversion Principle (DIP)
- **CHECK**: Dependencies on abstractions, not concrete implementations
- **CHECK**: Dependencies injected through constructors
- **CHECK**: Use of protocols or ABCs for dependencies

## Testing Review

- **CHECK**: Unit tests exist for Models and ViewModels
- **CHECK**: Tests follow AAA pattern (Arrange, Act, Assert)
- **CHECK**: Tests use pytest fixtures appropriately
- **CHECK**: QApplication fixture used in conftest.py
- **CHECK**: Mocking used for external dependencies
- **CHECK**: Tests are isolated and deterministic
- **CHECK**: Coverage of critical paths

## Code Quality Checks

- **CHECK**: No circular dependencies
- **CHECK**: Proper error handling and logging
- **CHECK**: No blocking operations on UI thread
- **CHECK**: Thread safety for multi-threaded operations
- **CHECK**: Proper resource cleanup (`deleteLater()` for widgets)
- **CHECK**: No memory leaks (parent-child relationships)
- **CHECK**: Consistent naming conventions

## Documentation Review

- **CHECK**: All public APIs have docstrings
- **CHECK**: Type hints present and accurate
- **CHECK**: Complex logic has inline comments
- **CHECK**: README and AGENTS.md are up to date
- **CHECK**: Examples follow established patterns

## Summary Format

After completing the code review, provide a structured summary:

### Strengths
- List architectural and implementation strengths

### Issues Found
- **CRITICAL**: MVVM violations, missing tests, security issues
- **MAJOR**: SOLID violations, missing type hints, performance issues
- **MINOR**: Style inconsistencies, missing docs, minor improvements

### Recommendations
- Prioritized list of improvements
- Links to relevant documentation or patterns
- Suggested refactoring approaches
