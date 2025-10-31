---
description: "Custom instructions for Desktop Application development with Python"
applyTo: "**"
---

# Desktop Application Development Guidelines

*Note: All common requirements (file headers, testing, inline documentation) are defined in `copilot-instructions.md`. This file contains only Desktop-specific requirements.*

## Desktop Requirements
- **MUST** implement MVVM (Model–View–ViewModel) for Qt/PySide:
- **MUST** handle threading for non-blocking UI
- **MUST** provide user feedback for long operations
- **MUST** save/restore window state and preferences
- **MUST** separate business logic from GUI for testing
- **MUST** test business logic independently of GUI components
- **MUST** validate UI behavior through integration testing where appropriate

## Desktop Header Requirements
- **MUST** include Desktop-specific Features section with:
  - MVVM (Model–View–ViewModel) architectural pattern for clean separation of concerns
  - Threaded operations to prevent UI blocking
  - Window state persistence (size, position, preferences)
  - Responsive user feedback for long operations

## Desktop Code Generation Focus
- **Framework:** PySide6 first, justify alternatives
- **Architecture:** Separate business logic from UI, use MVVM
- **Pattern:** Follow template below

## Desktop Application Template

```python
class Application:
    """Main application controller."""

    def __init__(self):
        self.model = DataModel()
        self.view = MainWindow(self)
        self.setup_event_handlers()

    def setup_event_handlers(self):
        """Connect UI events to business logic."""
        self.view.on_save = self.handle_save
        self.view.on_load = self.handle_load

    def run(self):
        """Start the application main loop."""
        # NOTE: Error handling deferred until v1.0.0 per main guidelines
        self.view.mainloop()
        self.cleanup()
```
