---
description: "Analyze PySide6 MVVM code for bugs and potential issues"
mode: "agent"
---

# Analyze and Debug Code

Analyze the code in ${file} or project to identify bugs, issues, and potential improvements in the context of PySide6 MVVM architecture.

## General Guidelines

- **FOCUS**: Identify bugs, logical errors, performance issues, and MVVM violations
- **MANDATORY**: Code follows Python 3.10+ standards
- **MANDATORY**: Follow repository guidelines in ![copilot-instructions.md](../copilot-instructions.md)
- **MANDATORY**: Check MVVM layer separation
- **IMPORTANT**: This is not a comprehensive code review. Focus on actual bugs and issues.

## MVVM-Specific Debug Checks

### Model Layer Bugs
- ❌ Qt imports in model files
- ❌ UI logic in models
- ❌ Circular dependencies
- ❌ Missing validation
- ❌ Incorrect data types

### ViewModel Layer Bugs
- ❌ Missing QObject inheritance
- ❌ Undefined signals
- ❌ Business logic in viewmodels (should delegate to models/services)
- ❌ Direct widget manipulation
- ❌ Missing signal emissions
- ❌ Memory leaks (signals not disconnected)

### View Layer Bugs
- ❌ Business logic in views
- ❌ Data validation in views
- ❌ Missing signal/slot connections
- ❌ UI blocking operations
- ❌ Resource leaks (widgets not properly deleted)
- ❌ Missing parent-child relationships

## Common Issues to Check

### Threading Issues
- Long-running operations on UI thread
- Missing QThread usage
- Race conditions in signal/slot connections
- Improper thread cleanup

### Memory Issues
- Circular references
- Missing parent-child widget relationships
- Signals connected multiple times
- Resources not cleaned up

### Type Issues
- Missing type hints
- Incorrect type usage
- None handling issues
- Type mismatches in signal/slot connections

### Logic Issues
- Off-by-one errors
- Incorrect conditionals
- Missing edge case handling
- Incorrect algorithm implementation

### Performance Issues
- Inefficient algorithms
- Unnecessary computations
- Missing caching
- Excessive signal emissions

## Analysis Output

Provide a structured summary:

### Critical Bugs
List bugs that will cause crashes or data corruption

### MVVM Violations
List architectural violations

### Logic Errors
List logical mistakes in implementation

### Performance Issues
List code that could be optimized

### Recommendations
Prioritized suggestions for fixes
