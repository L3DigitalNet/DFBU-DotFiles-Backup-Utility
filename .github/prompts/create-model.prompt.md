---
mode: "agent"
description: "Create a new Model class following MVVM architecture and SOLID principles"
---

# Create New Model

Create a new Model class in the `DFBU/gui/` directory following MVVM architecture, SOLID principles, and repository guidelines.

## Overview

Models contain business logic and domain entities. They are pure Python with NO Qt dependencies.

## Guidelines

### Requirements
- **NO** Qt imports (no PySide6, no QObject)
- **PURE** Python business logic only
- **USE** `@dataclass` for simple data containers
- **INCLUDE** validation methods
- **PROVIDE** domain-specific functionality
- **TYPE HINTS** on all methods and attributes
- **DOCSTRINGS** on all public APIs

### Location
Place new model in: `DFBU/gui/[model_name].py`

### Naming Convention
- **File**: `snake_case.py` (e.g., `user_profile.py`)
- **Class**: `PascalCase` (e.g., `UserProfile`)

## Template Structure

### Simple Data Model
```python
"""Module for [description] model."""
from dataclasses import dataclass


@dataclass
class MyModel:
    """Represents [domain concept].

    Attributes:
        field1: Description of field1.
        field2: Description of field2.
    """
    field1: str
    field2: int
    field3: float | None = None

    def validate(self) -> bool:
        """Validate model data.

        Returns:
            True if all fields are valid, False otherwise.
        """
        return bool(self.field1) and self.field2 > 0
```

### Complex Business Logic Model
```python
"""Module for [description] model."""
from typing import Final


class MyBusinessModel:
    """Handles [business domain] operations.

    This class manages [description of responsibility].
    """

    MAX_VALUE: Final = 100

    def __init__(self, initial_value: int = 0):
        """Initialize model.

        Args:
            initial_value: Starting value for calculations.

        Raises:
            ValueError: If initial_value is negative.
        """
        if initial_value < 0:
            raise ValueError("Initial value must be non-negative")
        self._value = initial_value

    def calculate(self, input_data: list[float]) -> float:
        """Perform business calculation.

        Args:
            input_data: List of values to process.

        Returns:
            Calculated result based on business rules.

        Raises:
            ValueError: If input_data is empty.
        """
        if not input_data:
            raise ValueError("Input data cannot be empty")
        return sum(input_data) * self._value

    def validate_input(self, value: int) -> bool:
        """Validate input against business rules.

        Args:
            value: Value to validate.

        Returns:
            True if value is valid, False otherwise.
        """
        return 0 <= value <= self.MAX_VALUE
```

## Model Types

### Data Transfer Objects (DTOs)
Use `@dataclass` for simple data containers:
```python
@dataclass
class UserDTO:
    username: str
    email: str
    created_at: str
```

### Domain Entities
Use classes for entities with behavior:
```python
class Order:
    def __init__(self, order_id: str, items: list[Item]):
        self.order_id = order_id
        self.items = items

    def calculate_total(self) -> float:
        return sum(item.price * item.quantity for item in self.items)

    def is_valid(self) -> bool:
        return bool(self.items) and all(item.quantity > 0 for item in self.items)
```

### Value Objects
Immutable objects representing values:
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Price:
    amount: float
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Price cannot be negative")
```

## Testing

Create corresponding test file in `DFBU/tests/test_[model_name].py`:

```python
"""Tests for MyModel."""
import pytest
from gui.my_model import MyModel


class TestMyModel:
    """Test suite for MyModel."""

    @pytest.fixture
    def model(self):
        """Create a model instance for testing."""
        return MyModel(field1="test", field2=42)

    def test_validate_returns_true_for_valid_data(self, model):
        """Test that validate returns True for valid data."""
        # Arrange
        # (model fixture is already arranged)

        # Act
        result = model.validate()

        # Assert
        assert result is True

    def test_validate_returns_false_for_invalid_field2(self):
        """Test that validate returns False when field2 is invalid."""
        # Arrange
        model = MyModel(field1="test", field2=-1)

        # Act
        result = model.validate()

        # Assert
        assert result is False
```

## Integration with MVVM

### Model → ViewModel
ViewModels use Models for business logic:
```python
# In ViewModel
class MyViewModel(QObject):
    def __init__(self, model: MyModel):
        super().__init__()
        self._model = model

    def process_data(self):
        if self._model.validate():
            result = self._model.calculate()
            self.result_ready.emit(result)
```

## Checklist

- [ ] Created file in `DFBU/gui/`
- [ ] No Qt imports in model file
- [ ] Used appropriate structure (dataclass or class)
- [ ] Added type hints to all methods and attributes
- [ ] Included docstrings for public APIs
- [ ] Implemented validation if needed
- [ ] Created unit tests in `DFBU/tests/`
- [ ] All tests pass
- [ ] Model follows SRP (Single Responsibility Principle)
- [ ] Updated `DFBU/gui/__init__.py` if needed

## Common Patterns

### Validation Pattern
```python
def validate(self) -> tuple[bool, str]:
    """Validate and return result with error message."""
    if not self.field1:
        return False, "Field1 is required"
    if self.field2 < 0:
        return False, "Field2 must be non-negative"
    return True, ""
```

### Builder Pattern
```python
class ModelBuilder:
    def __init__(self):
        self._data = {}

    def with_field1(self, value: str) -> 'ModelBuilder':
        self._data['field1'] = value
        return self

    def build(self) -> MyModel:
        return MyModel(**self._data)
```

### Factory Pattern
```python
class ModelFactory:
    @staticmethod
    def create_from_dict(data: dict) -> MyModel:
        return MyModel(
            field1=data['field1'],
            field2=int(data['field2'])
        )
```
