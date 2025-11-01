---
description: "Comprehensive code review following repository guidelines"
mode: "agent"
---

# Comprehensive Code Review

Perform a complete code review of ${file} or project following repository guidelines.

## General Guidelines
- **MANDATORY**: Do not change any code logic or implementation, only suggest improvements
- **MANDATORY**: Follow all repository guidelines in [copilot-instructions.md](../copilot-instructions.md)

## CRITICAL: Linux Environment Only
- **IMPORTANT**: This repository is designed for **Linux environments ONLY**

## Core Standards
- **Python 3.14+ REQUIRED**: Minimum version with latest language features
- **Type hints MANDATORY**: ALL functions, methods, variables, constants, data structures, collections
- **Standard library FIRST**: Use Python stdlib before ANY external dependencies - justify external deps with comments
- **PEP 8 compliance**: Strict formatting and style requirements
- **File headers**: Full docstring format with shebang and complete metadata (UTF-8 encoding NOT required in Python 3)
- **Streamlined docstrings**: Brief descriptions, 80-char limit, leverage type hints
- **DRY principle**: Eliminate ALL duplication, centralize shared utilities within the project

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

## Domain Guidelines
Apply domain-specific patterns from [instructions/](../instructions/) if this is a CLI tool, desktop app, or library.

Provide a summary of changes made and recommendations for further improvement.
