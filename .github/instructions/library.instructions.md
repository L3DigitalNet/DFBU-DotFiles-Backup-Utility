---
description: "Custom instructions for Library development with Python"
applyTo: "**"
---

# Library Development Guidelines

*Note: All common requirements (file headers, testing, inline documentation) are defined in `copilot-instructions.md`. This file contains only Library-specific requirements.*

## Library Requirements
- **MUST** follow semantic versioning (SemVer) for releases
- **MUST** maintain backward compatibility within major versions
- **MUST** design APIs that are intuitive and hard to misuse
- **MUST** provide comprehensive documentation and usage examples
- **MUST** test public API interfaces thoroughly with contract testing
- **MUST** validate type safety and interface compliance across all public methods
- **MUST** ensure library behavior is consistent and predictable through comprehensive testing

## Library Header Requirements
- **MUST** include Library-specific Features section with:
  - Semantic versioning (SemVer) for releases
  - Backward compatibility within major versions
  - Intuitive API design that's hard to misuse
  - Comprehensive documentation and usage examples
  - Type-safe interfaces with full type hint coverage

## Library Code Generation Focus
- **Framework:** Standard library first, minimal external dependencies
- **Architecture:** Separate public API from internal implementation
- **Pattern:** Follow template below

## Library Development Patterns

```python
from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic, Any
import logging

T = TypeVar('T')

class ProcessorProtocol(Protocol[T]):
    """Protocol defining the interface for data processors."""

    def process(self, data: T) -> T:
        """Process the input data and return processed result."""
        ...

class BaseProcessor(ABC, Generic[T]):
    """Abstract base class for data processors."""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def process(self, data: T) -> T:
        """Process the input data. Must be implemented by subclasses."""
        pass

    def validate_input(self, data: T) -> None:
        """Validate input data. Override in subclasses if needed."""
        # NOTE: Defensive validation deferred until v1.0.0 per confident design
        pass
```
