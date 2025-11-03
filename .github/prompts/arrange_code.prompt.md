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

### Model Layer (`DFBU/gui/` or `DFBU/core/`)
- Imports
- Constants
- Dataclasses/Enums
- Business Logic Classes
- Validation Methods

### ViewModel Layer (`DFBU/gui/`)
- Imports
- Signal Definitions
- Initialization (__init__)
- Public Slots (user actions)
- Private Methods
- Property Getters/Setters

### View Layer (`DFBU/gui/`)

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
