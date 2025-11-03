---
mode: "agent"
description: "Arrange classes, functions, and methods in a logical order following MVVM architecture and repository guidelines"
---

# Arrange Code Structure for PySide6 MVVM Application

For the given ${file}, rearrange the classes, functions, and methods to follow a logical structure that supports MVVM architecture and SOLID principles.

Follow guidelines in ![repository instructions](../copilot-instructions.md) if not specified below.

## General Guidelines
- **MANDATORY**: Do not change any code logic or implementation
- **MANDATORY**: Only rearrange the order of classes, functions, and methods
- **MANDATORY**: Maintain existing dependencies and references
- **MANDATORY**: Preserve MVVM layer separation (Model/View/ViewModel)

## MVVM Layer-Specific Organization

### Model Layer (`src/models/`)
- Data classes and domain entities first
- Business logic methods grouped by functionality
- Validation methods after core logic
- Helper/utility methods last
- No Qt imports should be present

### ViewModel Layer (`src/viewmodels/`)
1. Signal definitions at the top
2. Constructor with dependency injection
3. Public slots for View interactions
4. Private helper methods
5. Property getters/setters if needed
- Inherits from QObject

### View Layer (`src/views/`)
1. Constructor accepting ViewModel
2. `_setup_ui()` method for widget creation
3. `_connect_signals()` method for signal/slot connections
4. Public methods for external interactions
5. Private event handlers (slots)
6. Private UI update methods

## Classes and Methods
- Classes should be at the top
- Class methods should be within their respective classes
- Public methods should come before private methods (underscore prefix)
- Static methods and class methods should be placed after instance methods
- Qt signal definitions should be at the top of the class body

## Functions
- Functions should follow classes
- Functions should be at the top level (not nested unless necessary)
- Public functions should come before private functions (underscore prefix)
- Group related functions together logically

## Logical Grouping
- Group related classes and functions together
- Follow logical flow: initialization, core functionality, helpers/utilities
- Maintain MVVM boundaries and dependencies
- Keep signal/slot connections organized
- Maintain readability and ease of navigation