"""
Example ViewModel Test Template

Description:
    Template demonstrating proper ViewModel testing following MVVM architecture
    and test.prompt.md guidelines. Shows how to test ViewModels with signals,
    mocking, and proper AAA (Arrange-Act-Assert) pattern.

    This is a REFERENCE FILE showing best practices. Copy and adapt patterns
    for actual ViewModel tests.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-02-2025
License: MIT

Testing Patterns Demonstrated:
    - ViewModel initialization with dependency injection
    - Signal emission testing with pytest-qt
    - Service mocking with pytest-mock
    - AAA pattern (Arrange-Act-Assert)
    - Proper test naming conventions
    - Using qtbot for Qt signal testing
    - Testing async operations and threads
    - Error handling in ViewModels

Requirements:
    - pytest>=7.0.0
    - pytest-qt>=4.0.0
    - pytest-mock>=3.0.0
    - conftest.py with qapp fixture
"""

# Template file - type checking relaxed for demonstration purposes

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, cast
from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QObject, Signal, Slot
from pytestqt.qtbot import QtBot


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


# =============================================================================
# Example ViewModel for Testing (normally imported from actual code)
# =============================================================================


class ExampleViewModel(QObject):
    """
    Example ViewModel demonstrating testable patterns.

    This would normally be imported from your actual code.
    Included here for demonstration purposes only.
    """

    # Signals for communicating with View layer
    data_loaded = Signal(list)
    error_occurred = Signal(str)
    progress_updated = Signal(int)

    def __init__(self, data_service: DataServiceProtocol) -> None:
        """
        Initialize ViewModel with injected dependencies.

        Args:
            data_service: Service for data operations (injected)
        """
        super().__init__()
        self._data_service = data_service
        self._data: list[str] = []

    @Slot()
    def load_data(self) -> None:
        """Load data from service and emit signal."""
        try:
            self._data = self._data_service.fetch()
            self.data_loaded.emit(self._data)
        except Exception as e:
            self.error_occurred.emit(str(e))

    @Slot(str)
    def add_item(self, item: str) -> None:
        """Add item and save via service."""
        if not item:
            self.error_occurred.emit("Item cannot be empty")
            return

        try:
            self._data.append(item)
            self._data_service.save(self._data)
            self.data_loaded.emit(self._data)
        except Exception as e:
            self.error_occurred.emit(str(e))


# =============================================================================
# Protocol Definitions (normally in separate module)
# =============================================================================


class DataServiceProtocol(Protocol):
    """Protocol defining data service interface."""

    def fetch(self) -> list[str]:
        """Fetch data from service."""
        ...

    def save(self, data: list[str]) -> bool:
        """Save data to service."""
        ...


# =============================================================================
# Test Class - Basic ViewModel Testing
# =============================================================================


class TestExampleViewModelBasics:
    """
    Test suite for basic ViewModel functionality.

    Demonstrates:
        - Fixture usage for test setup
        - Testing initialization
        - Testing with mock services
    """

    @pytest.fixture
    def mock_data_service(self, mocker: MockerFixture) -> MagicMock:
        """
        Create mock data service for testing.

        Args:
            mocker: pytest-mock fixture

        Returns:
            Mock service object
        """
        mock_service: MagicMock = mocker.Mock(spec=DataServiceProtocol)
        mock_service.fetch.return_value = ["item1", "item2"]
        mock_service.save.return_value = True
        return mock_service

    @pytest.fixture
    def viewmodel(self, mock_data_service: MagicMock, qapp: None) -> ExampleViewModel:
        """
        Create ViewModel instance for testing.

        Args:
            mock_data_service: Mocked data service
            qapp: QApplication fixture from conftest.py

        Returns:
            ViewModel instance for testing
        """
        return ExampleViewModel(mock_data_service)

    def test_viewmodel_initializes_with_empty_data(
        self, mock_data_service: MagicMock, qapp: None
    ) -> None:
        """Test that ViewModel initializes with empty data list."""
        # Arrange & Act
        vm = ExampleViewModel(mock_data_service)

        # Assert
        assert vm._data == []
        assert isinstance(vm._data_service, type(mock_data_service))


# =============================================================================
# Test Class - Signal Emission Testing
# =============================================================================


class TestExampleViewModelSignals:
    """
    Test suite for ViewModel signal emissions.

    Demonstrates:
        - Using qtbot to wait for signals
        - Testing signal arguments
        - Testing multiple signals
        - Testing signal ordering
    """

    @pytest.fixture
    def mock_data_service(self, mocker: MockerFixture) -> MagicMock:
        """Create mock data service."""
        mock_service: MagicMock = mocker.Mock(spec=DataServiceProtocol)
        mock_service.fetch.return_value = ["test1", "test2"]
        mock_service.save.return_value = True
        return mock_service

    @pytest.fixture
    def viewmodel(self, mock_data_service: MagicMock, qapp: None) -> ExampleViewModel:
        """Create ViewModel instance."""
        return ExampleViewModel(mock_data_service)

    def test_load_data_emits_signal_with_data(
        self,
        viewmodel: ExampleViewModel,
        mock_data_service: MagicMock,
        qtbot: QtBot,
    ) -> None:
        """Test that load_data emits data_loaded signal with correct data."""
        # Arrange
        expected_data = ["test1", "test2"]
        mock_data_service.fetch.return_value = expected_data

        # Act & Assert - Wait for signal emission
        with qtbot.waitSignal(viewmodel.data_loaded, timeout=1000) as blocker:
            viewmodel.load_data()

        # Assert - Check signal arguments
        assert blocker.args is not None
        assert blocker.args[0] == expected_data
        mock_data_service.fetch.assert_called_once()

    def test_load_data_emits_error_signal_on_failure(
        self,
        viewmodel: ExampleViewModel,
        mock_data_service: MagicMock,
        qtbot: QtBot,
    ) -> None:
        """Test that load_data emits error_occurred signal on exception."""
        # Arrange
        error_message = "Network error"
        mock_data_service.fetch.side_effect = Exception(error_message)

        # Act & Assert - Wait for error signal
        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            viewmodel.load_data()

        # Assert - Check error message
        assert blocker.args is not None
        assert error_message in blocker.args[0]

    def test_add_item_emits_data_loaded_signal(
        self,
        viewmodel: ExampleViewModel,
        mock_data_service: MagicMock,
        qtbot: QtBot,
    ) -> None:
        """Test that add_item emits data_loaded signal after saving."""
        # Arrange
        new_item = "test_item"

        # Act & Assert
        with qtbot.waitSignal(viewmodel.data_loaded, timeout=1000) as blocker:
            viewmodel.add_item(new_item)

        # Assert
        assert blocker.args is not None
        assert new_item in blocker.args[0]
        mock_data_service.save.assert_called_once()

    def test_add_empty_item_emits_error_signal(
        self, viewmodel: ExampleViewModel, qtbot: QtBot
    ) -> None:
        """Test that adding empty item emits error signal."""
        # Arrange
        empty_item = ""

        # Act & Assert
        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000) as blocker:
            viewmodel.add_item(empty_item)

        # Assert
        assert blocker.args is not None
        assert "empty" in blocker.args[0].lower()


# =============================================================================
# Test Class - Mock Verification
# =============================================================================


class TestExampleViewModelMockVerification:
    """
    Test suite demonstrating mock verification patterns.

    Demonstrates:
        - Verifying method calls
        - Checking call arguments
        - Verifying call count
        - Testing method call order
    """

    @pytest.fixture
    def mock_data_service(self, mocker: MockerFixture) -> MagicMock:
        """Create mock data service."""
        mock_service: MagicMock = mocker.Mock(spec=DataServiceProtocol)
        mock_service.fetch.return_value = ["item1"]
        mock_service.save.return_value = True
        return mock_service

    @pytest.fixture
    def viewmodel(self, mock_data_service: MagicMock, qapp: None) -> ExampleViewModel:
        """Create ViewModel instance."""
        return ExampleViewModel(mock_data_service)

    def test_load_data_calls_service_fetch(
        self,
        viewmodel: ExampleViewModel,
        mock_data_service: MagicMock,
        qtbot: QtBot,
    ) -> None:
        """Test that load_data calls service.fetch() exactly once."""
        # Arrange
        # (fixtures already arranged)

        # Act
        with qtbot.waitSignal(viewmodel.data_loaded, timeout=1000):
            viewmodel.load_data()

        # Assert - Verify service method was called
        mock_data_service.fetch.assert_called_once()

    def test_add_item_calls_service_save_with_correct_data(
        self,
        viewmodel: ExampleViewModel,
        mock_data_service: MagicMock,
        qtbot: QtBot,
    ) -> None:
        """Test that add_item calls service.save() with updated data."""
        # Arrange
        new_item = "new_test_item"

        # Act
        with qtbot.waitSignal(viewmodel.data_loaded, timeout=1000):
            viewmodel.add_item(new_item)

        # Assert - Verify save was called with correct data
        mock_data_service.save.assert_called_once()
        call_args = mock_data_service.save.call_args[0][0]
        assert new_item in call_args

    def test_service_not_called_on_empty_item(
        self,
        viewmodel: ExampleViewModel,
        mock_data_service: MagicMock,
        qtbot: QtBot,
    ) -> None:
        """Test that service.save() is NOT called when item is empty."""
        # Arrange
        empty_item = ""

        # Act
        with qtbot.waitSignal(viewmodel.error_occurred, timeout=1000):
            viewmodel.add_item(empty_item)

        # Assert - Verify save was never called
        mock_data_service.save.assert_not_called()


# =============================================================================
# Test Class - Integration Patterns
# =============================================================================


class TestExampleViewModelIntegration:
    """
    Test suite for integration scenarios.

    Demonstrates:
        - Testing multiple operations in sequence
        - Testing state management
        - Testing edge cases
        - Testing with realistic data
    """

    @pytest.fixture
    def mock_data_service(self, mocker: MockerFixture) -> MagicMock:
        """Create mock data service."""
        mock_service: MagicMock = mocker.Mock(spec=DataServiceProtocol)
        mock_service.fetch.return_value = []
        mock_service.save.return_value = True
        return mock_service

    @pytest.fixture
    def viewmodel(self, mock_data_service: MagicMock, qapp: None) -> ExampleViewModel:
        """Create ViewModel instance."""
        return ExampleViewModel(mock_data_service)

    def test_multiple_items_added_sequentially(
        self,
        viewmodel: ExampleViewModel,
        mock_data_service: MagicMock,
        qtbot: QtBot,
    ) -> None:
        """Test adding multiple items updates state correctly."""
        # Arrange
        items = ["item1", "item2", "item3"]

        # Act - Add items sequentially
        for item in items:
            with qtbot.waitSignal(viewmodel.data_loaded, timeout=1000):
                viewmodel.add_item(item)

        # Assert - Verify all items were added
        assert mock_data_service.save.call_count == len(items)
        # Last call should have all items
        final_call_args = mock_data_service.save.call_args[0][0]
        for item in items:
            assert item in final_call_args


# =============================================================================
# Notes on Testing Best Practices
# =============================================================================

"""
KEY TESTING PRINCIPLES from test.prompt.md:

1. AAA PATTERN (Arrange-Act-Assert):
   - Arrange: Set up test data and mocks
   - Act: Execute the code being tested
   - Assert: Verify the results

2. TEST NAMING:
   - Use descriptive names: test_<function>_should_<behavior>_when_<condition>
   - Example: test_load_data_emits_signal_when_service_succeeds

3. ISOLATION:
   - Mock all external dependencies (services, file I/O, network)
   - Each test should be independent
   - Use fixtures for common setup

4. SIGNAL TESTING:
   - Use qtbot.waitSignal() with timeout
   - Test both signal emission AND arguments
   - Test error signals separately from success signals

5. MOCK VERIFICATION:
   - Verify mocks were called: assert_called_once()
   - Check call arguments: call_args
   - Verify call count: call_count
   - Verify NOT called when appropriate: assert_not_called()

6. MVVM LAYER SEPARATION:
   - ViewModel tests should NOT instantiate Views
   - Mock Model/Service dependencies
   - Test signals, not UI state
   - Keep tests fast (< 1 second per test)

7. FIXTURES:
   - Use conftest.py for shared fixtures
   - Create test-specific fixtures in test class
   - Inject dependencies through fixtures
   - Use qapp fixture for Qt functionality

8. COVERAGE:
   - Target 80%+ for ViewModels
   - Focus on public methods
   - Test happy path first, then error cases
   - Test edge cases and boundary conditions

ANTI-PATTERNS TO AVOID:
❌ Testing View and ViewModel together
❌ Not using qtbot for signal testing
❌ Not mocking external dependencies
❌ Tests that depend on external resources
❌ Tests with hardcoded timeouts > 1000ms
❌ Not verifying mock calls
❌ Vague test names like test_function_works
❌ Multiple unrelated assertions in one test

REFER TO THIS FILE when writing new ViewModel tests!
"""
