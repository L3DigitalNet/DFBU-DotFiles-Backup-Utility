#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DFBU CLIMenu Class Tests

Description:
    Unit tests for CLIMenu class from dfbu.py, testing interactive menu
    functionality and yes/no/quit prompt handling.

Author: Test Suite
Date Created: 10-31-2025
License: MIT

Features:
    - Menu display and selection testing
    - Yes/No/Quit prompt handling
    - Input validation
    - Error handling for invalid input

Requirements:
    - Linux environment
    - Python 3.14+
    - pytest framework
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, call
import pytest

# Add DFBU directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dfbu import CLIMenu


class TestCLIMenuRun:
    """Test CLIMenu run method for numbered menu selection."""

    def test_menu_run_valid_selection(self):
        """Test menu executes correct function for valid selection."""
        # Arrange
        menu = CLIMenu()
        mock_func1 = Mock()
        mock_func2 = Mock()
        menu_options = {
            "Option 1": mock_func1,
            "Option 2": mock_func2,
        }

        # Act - simulate user selecting option 1
        with patch("builtins.input", return_value="1"):
            with patch("builtins.print"):
                menu.run(menu_options)

        # Assert - function 1 should be called
        mock_func1.assert_called_once()
        mock_func2.assert_not_called()

    def test_menu_run_second_option(self):
        """Test menu executes second option correctly."""
        # Arrange
        menu = CLIMenu()
        mock_func1 = Mock()
        mock_func2 = Mock()
        mock_func3 = Mock()
        menu_options = {
            "First": mock_func1,
            "Second": mock_func2,
            "Third": mock_func3,
        }

        # Act - simulate user selecting option 2
        with patch("builtins.input", return_value="2"):
            with patch("builtins.print"):
                menu.run(menu_options)

        # Assert - only function 2 should be called
        mock_func1.assert_not_called()
        mock_func2.assert_called_once()
        mock_func3.assert_not_called()

    def test_menu_run_invalid_then_valid(self):
        """Test menu handles invalid input then accepts valid selection."""
        # Arrange
        menu = CLIMenu()
        mock_func = Mock()
        menu_options = {"Valid Option": mock_func}

        # Act - simulate invalid then valid input
        with patch("builtins.input", side_effect=["0", "1"]):
            with patch("builtins.print") as mock_print:
                menu.run(menu_options)

        # Assert - function should be called after valid input
        mock_func.assert_called_once()
        # Check that error message was printed for invalid input
        assert any(
            "Invalid selection" in str(call) for call in mock_print.call_args_list
        )

    def test_menu_run_out_of_range_high(self):
        """Test menu rejects selection higher than available options."""
        # Arrange
        menu = CLIMenu()
        mock_func = Mock()
        menu_options = {
            "Option 1": mock_func,
            "Option 2": mock_func,
        }

        # Act - simulate out of range then valid input
        with patch("builtins.input", side_effect=["5", "1"]):
            with patch("builtins.print") as mock_print:
                menu.run(menu_options)

        # Assert - error message should be shown
        assert any(
            "Invalid selection" in str(call) for call in mock_print.call_args_list
        )
        mock_func.assert_called_once()

    def test_menu_run_keyboard_interrupt(self):
        """Test menu exits gracefully on KeyboardInterrupt."""
        # Arrange
        menu = CLIMenu()
        menu_options = {"Option": Mock()}

        # Act & Assert - should exit on KeyboardInterrupt
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with patch("builtins.print"):
                with pytest.raises(SystemExit) as exc_info:
                    menu.run(menu_options)
                assert exc_info.value.code == 0

    def test_menu_run_eof_error(self):
        """Test menu exits gracefully on EOF."""
        # Arrange
        menu = CLIMenu()
        menu_options = {"Option": Mock()}

        # Act & Assert - should exit on EOFError
        with patch("builtins.input", side_effect=EOFError):
            with patch("builtins.print"):
                with pytest.raises(SystemExit) as exc_info:
                    menu.run(menu_options)
                assert exc_info.value.code == 0

    def test_menu_run_non_numeric_input(self):
        """Test menu handles non-numeric input gracefully."""
        # Arrange
        menu = CLIMenu()
        menu_options = {"Option": Mock()}

        # Act & Assert - should exit on ValueError from non-numeric input
        with patch("builtins.input", side_effect=["abc", KeyboardInterrupt]):
            with patch("builtins.print"):
                with pytest.raises(SystemExit):
                    menu.run(menu_options)


class TestCLIMenuYNQ:
    """Test CLIMenu ynq method for yes/no/quit prompts."""

    def test_ynq_yes_response(self):
        """Test ynq returns True for 'yes' response."""
        # Arrange
        menu = CLIMenu()

        # Act - simulate 'y' input
        with patch("builtins.input", return_value="y"):
            result = menu.ynq("Continue?")

        # Assert
        assert result is True

    def test_ynq_yes_full_word(self):
        """Test ynq returns True for full 'yes' response."""
        # Arrange
        menu = CLIMenu()

        # Act - simulate 'yes' input
        with patch("builtins.input", return_value="yes"):
            result = menu.ynq("Continue?")

        # Assert
        assert result is True

    def test_ynq_no_response(self):
        """Test ynq returns False for 'no' response."""
        # Arrange
        menu = CLIMenu()

        # Act - simulate 'n' input
        with patch("builtins.input", return_value="n"):
            result = menu.ynq("Continue?")

        # Assert
        assert result is False

    def test_ynq_no_full_word(self):
        """Test ynq returns False for full 'no' response."""
        # Arrange
        menu = CLIMenu()

        # Act - simulate 'no' input
        with patch("builtins.input", return_value="no"):
            result = menu.ynq("Continue?")

        # Assert
        assert result is False

    def test_ynq_quit_response(self):
        """Test ynq exits on 'quit' response."""
        # Arrange
        menu = CLIMenu()

        # Act & Assert - should exit on 'q'
        with patch("builtins.input", return_value="q"):
            with patch("builtins.print"):
                with pytest.raises(SystemExit) as exc_info:
                    menu.ynq("Continue?")
                assert exc_info.value.code == 0

    def test_ynq_quit_full_word(self):
        """Test ynq exits on full 'quit' response."""
        # Arrange
        menu = CLIMenu()

        # Act & Assert - should exit on 'quit'
        with patch("builtins.input", return_value="quit"):
            with patch("builtins.print"):
                with pytest.raises(SystemExit) as exc_info:
                    menu.ynq("Continue?")
                assert exc_info.value.code == 0

    def test_ynq_case_insensitive(self):
        """Test ynq handles uppercase input."""
        # Arrange
        menu = CLIMenu()

        # Act - simulate 'Y' input
        with patch("builtins.input", return_value="Y"):
            result = menu.ynq("Continue?")

        # Assert - should still return True
        assert result is True

    def test_ynq_invalid_then_valid(self):
        """Test ynq handles invalid input then accepts valid response."""
        # Arrange
        menu = CLIMenu()

        # Act - simulate invalid then valid input
        with patch("builtins.input", side_effect=["invalid", "y"]):
            with patch("builtins.print") as mock_print:
                result = menu.ynq("Continue?")

        # Assert
        assert result is True
        # Check that error message was printed
        assert any("Invalid entry" in str(call) for call in mock_print.call_args_list)

    def test_ynq_whitespace_handling(self):
        """Test ynq strips whitespace from input."""
        # Arrange
        menu = CLIMenu()

        # Act - simulate input with whitespace
        with patch("builtins.input", return_value="  y  "):
            result = menu.ynq("Continue?")

        # Assert - should still work
        assert result is True

    def test_ynq_keyboard_interrupt(self):
        """Test ynq exits gracefully on KeyboardInterrupt."""
        # Arrange
        menu = CLIMenu()

        # Act & Assert - should exit on KeyboardInterrupt
        with patch("builtins.input", side_effect=KeyboardInterrupt):
            with patch("builtins.print"):
                with pytest.raises(SystemExit) as exc_info:
                    menu.ynq("Continue?")
                assert exc_info.value.code == 0

    def test_ynq_eof_error(self):
        """Test ynq exits gracefully on EOF."""
        # Arrange
        menu = CLIMenu()

        # Act & Assert - should exit on EOFError
        with patch("builtins.input", side_effect=EOFError):
            with patch("builtins.print"):
                with pytest.raises(SystemExit) as exc_info:
                    menu.ynq("Continue?")
                assert exc_info.value.code == 0

    def test_ynq_prompt_display(self):
        """Test ynq displays prompt correctly."""
        # Arrange
        menu = CLIMenu()
        prompt_text = "Do you want to continue?"

        # Act - capture input call
        with patch("builtins.input", return_value="y") as mock_input:
            menu.ynq(prompt_text)

        # Assert - prompt should be in the input call
        call_args = str(mock_input.call_args)
        assert "Do you want to continue?" in call_args
        assert "(y/n/q)" in call_args
