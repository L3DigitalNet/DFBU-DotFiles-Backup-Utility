---
mode: "agent"
description: "Arrange classes, functions, and methods in a logical order following repository guidelines"
---

# Arrange classes, functions, and methods in a logical order

For the given ${file}, rearrange the classes, functions, and methods to follow a logical structure.

Follow guidelines in [repository instructions](../copilot-instructions.md) if not specified below.

## General Guidelines
- **MANDATORY**: Do not change any code logic or implementation
- **MANDATORY**: Only rearrange the order of classes, functions, and methods
- **MANDATORY**: Maintain existing dependencies and references

## Classes and Methods
- Classes should be at the top
- Class methods should be within their respective classes
- Public methods should come before private methods (underscore prefix)
- Static methods should be placed after instance methods

## Functions
- Functions should follow classes
- Functions should be at the top level (not nested unless necessary)
- Public functions should come before private functions (underscore prefix)
- Group related functions together logically

## Logical Grouping
- Group related classes and functions together
- Follow logical flow: initialization, core functionality, helpers/utilities
- Maintain readability and ease of navigation