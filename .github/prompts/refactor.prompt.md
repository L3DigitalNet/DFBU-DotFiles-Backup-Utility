---
description: "Code Refactoring following MVVM architecture and SOLID principles"
mode: "agent"
---

# Code Refactoring for PySide6 MVVM Applications

Perform comprehensive refactoring of ${file} or project following MVVM architecture, SOLID principles, and repository guidelines.

Follow [repository guidelines](../copilot-instructions.md) and [AGENTS.md](../../AGENTS.md).

## Core Refactoring Principles

### MVVM Separation - CRITICAL
- **MUST** maintain strict layer boundaries (Model/View/ViewModel)
- **NEVER** add Qt imports to Model layer
- **ALWAYS** use signals for cross-layer communication
- **MUST** inject dependencies through constructors
- **VERIFY** no business logic in Views
- **ENSURE** ViewModels don't manipulate widgets directly

### DRY (Don't Repeat Yourself) - HIGH PRIORITY
- **ELIMINATE** code duplication through abstraction
- **MAINTAIN** single source of truth for business logic
- **CENTRALIZE** constants in `DFBU/gui/constants.py`
- **EXTRACT** common patterns into base classes
- **CONSOLIDATE** similar logic into unified implementations

### Python Standard Library First
- **PREFER** Python standard library over external dependencies
- **USE** built-in modules: `pathlib`, `dataclasses`, `typing`, `collections`
- **ONLY** add dependencies when necessary (PySide6, pytest, etc.)
- **JUSTIFY** external dependencies with comments

### Clean Code and Type Safety
- **USE** type hints for ALL functions, methods, parameters
- **PREFER** `str | None` over `Optional[str]`
- **USE** `list[str]` over `List[str]`
- **APPLY** `@dataclass` for simple data containers
- **USE** `Protocol` for interface definitions
- **ENSURE** clear, readable code structure

## Type Hints and Documentation

### Type Hint Requirements
- **MUST** include type hints for ALL functions, methods, variables, constants, and data structures
- **MUST** use modern union syntax: `str | None` not `Optional[str]`
- **MUST** use collection types: `list[str]`, `dict[str, int]`, `set[int]`
- **MUST** use `Final` for constants, `ClassVar` for class variables, `TypedDict` for structured dicts
## SOLID Principles Application

### Single Responsibility Principle
- **ONE** purpose per class/function
- **SEPARATE** UI, business logic, and data access
- **EXTRACT** mixed responsibilities into focused classes

### Open/Closed Principle
- **EXTEND** behavior through composition
- **USE** abstract base classes for extensibility
- **AVOID** modifying existing, working code

### Liskov Substitution Principle
- **ENSURE** derived classes are substitutable
- **MAINTAIN** consistent contracts
- **PRESERVE** base class behavior expectations

### Interface Segregation Principle
- **CREATE** focused interfaces with `Protocol`
- **AVOID** fat interfaces with unused methods
- **SPLIT** large interfaces into cohesive units

### Dependency Inversion Principle
- **DEPEND** on abstractions (protocols, ABCs)
- **INJECT** dependencies through constructors
- **AVOID** creating dependencies inside classes

## Refactoring Patterns for MVVM

### Extract to ViewModel
Move presentation logic from View to ViewModel:
```python
# Before: Logic in View
class MyView(QWidget):
    def on_button_click(self):
        data = self.fetch_data()  # Wrong!
        self.process(data)        # Wrong!

# After: Logic in ViewModel
class MyViewModel(QObject):
    data_ready = Signal(list)

    def load_data(self):
        data = self._service.fetch()
        self.data_ready.emit(data)

class MyView(QWidget):
    def __init__(self, vm: MyViewModel):
        vm.data_ready.connect(self._update_ui)
        self._button.clicked.connect(vm.load_data)
```

### Extract to Model
Move business logic from ViewModel to Model:
```python
# Before: Business logic in ViewModel
class MyViewModel(QObject):
    def calculate_total(self, items):
        return sum(item.price * item.quantity for item in items)

# After: Business logic in Model
class OrderCalculator:
    @staticmethod
    def calculate_total(items: list[Item]) -> float:
        return sum(item.price * item.quantity for item in items)

class MyViewModel(QObject):
    def update_total(self):
        total = OrderCalculator.calculate_total(self._items)
        self.total_changed.emit(total)
```

### Extract to Service
Move external interactions to Service layer:
```python
# Service for file I/O, API calls, database
class DataService:
    def fetch_data(self) -> list[dict]:
        # File I/O or API call
        pass

# ViewModel uses Service
class MyViewModel(QObject):
    def __init__(self, service: DataService):
        self._service = service
```

## Code Quality Standards

### Naming Conventions
- **Classes**: PascalCase (e.g., `MainViewModel`)
- **Functions/Methods**: snake_case (e.g., `load_data`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_ITEMS`)
- **Private**: Leading underscore (e.g., `_internal_method`)
- **Signals**: Descriptive past tense (e.g., `data_changed`)

### Code Organization
- **IMPORTS**: Standard library, third-party, local (separated)
- **ORDER**: Classes first, then functions
- **GROUPING**: Related methods together
- **SPACING**: Two blank lines between top-level definitions

## Refactoring Checklist

- [ ] MVVM layers properly separated
- [ ] Dependencies injected, not created
- [ ] Type hints on all functions/methods
- [ ] Docstrings on public APIs
- [ ] No code duplication
- [ ] SOLID principles followed
- [ ] Tests updated and passing
- [ ] No Qt imports in Models
- [ ] Signals used for cross-layer communication
4. **Confident Design**: Can defensive patterns be replaced with architectural solutions?
5. **Reusability**: Can this be generalized for use by other projects?
