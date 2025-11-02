---
description: "Comprehensive code review following repository guidelines"
mode: "agent"
---

# Comprehensive Code Review

Perform a complete code review of the project following repository guidelines.

## General Guidelines

- **MANDATORY**: Do not change any code logic or implementation, only suggest improvements
- **MANDATORY**: Follow all repository guidelines in ![copilot-instructions.md](../.github/copilot-instructions.md)
- **MANDATORY**: Code and design should reflect the project's overall design goals in ![DESIGN.md](../.github/DESIGN.md):

## CRITICAL: Linux Environment Only

- **IMPORTANT**: This repository is designed for **Linux environments ONLY**

## Core Standards

- **Python 3.14+ REQUIRED**: Minimum version with latest language features
- **Type hints MANDATORY**: ALL functions, methods, variables, constants, data structures, collections
- **PEP 8 compliance**: Strict formatting and style requirements
- **File headers**: Full docstring format with shebang, encoding, and complete metadata
- **Streamlined docstrings**: Brief descriptions, 80-char limit, leverage type hints

## Architecture

**Pattern:** Hybrid State Machine + Game Object + Component + MVC
- **NOT full ECS** - Use Game Object with Component composition (simpler for turn-based games)
- **pygame-ce** for rendering (game view) - Community Edition with Python 3.14+ support
- **PySide6** for UI (menus, dialogs, settings)
- **MVC separation** - Game logic independent of UI/rendering
- **Object pooling** for projectiles, effects, temporary entities

## Tooling

- **GUI Design:** Qt Designer for all UI layouts
- **Testing:** pytest framework for unit and integration tests

## Clean & Confident Design (Highest Priority)

- **PREFER confident, clean code** over defensive programming patterns
- **AVOID unnecessary null/None checks** when program flow guarantees valid values
- **PREFER explicit initialization** and clear program flow over defensive conditionals
- **Remove "just in case" code** that handles scenarios that shouldn't occur
- **Use architectural solutions** over scattered defensive checks
- **Precise types**: Use types that reflect actual program constraints, avoid defensive Optional
- **Linear flow**: Confident execution paths with proper initialization order

## Version-Aware Approach

- **BEFORE v1.0.0 (current)**: Focus on core functionality and clean architecture
- **DEFER comprehensive error handling** until v1.0.0 - use architectural solutions instead
- **NEVER** use bare `except:` statements in any version

## Summary of Changes and Recommendations

After completing the code review, please provide a summary of the changes made and any recommendations for further improvement.
