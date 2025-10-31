---
description: "Analyze code for bugs and potential issues"
mode: "agent"
---

# Analyze and Debug Code

Analyze the code in ${file} or project to identify bugs, issues, and potential improvements.

## General Guidelines

- **IMPORTANT**: This is not a comprehensive code review or unit testing. Focus on identifying bugs, logical errors, performance issues, and potential improvements.
- **MANDATORY**: Code utilizes Python 3.14+ features and standard library where applicable (such as `Path.copy()`). #fetch <https://docs.python.org/3.14/index.html> for latest stdlib documentation.
- **MANDATORY**: Follow repository guidelines in [copilot-instructions.md](../copilot-instructions.md)
- **MANDATORY**: All code is designed for Linux environments only. Do not suggest Windows-specific solutions.
- **IMPORTANT**: Error handling is deferred until v1.0.0. Focus on clean architecture and core functionality first. Do not add error handling unless absolutely necessary to fix a bug.
