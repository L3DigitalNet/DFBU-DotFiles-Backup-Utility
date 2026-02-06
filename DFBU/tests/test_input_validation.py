"""
Tests for Input Validation Module

Description:
    Comprehensive tests for input validation functionality including path
    validation, string validation, integer validation, and sanitization.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-03-2025
License: MIT
"""

import sys
from pathlib import Path

import pytest


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.input_validation import InputValidator, ValidationResult


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_validation_result_success(self) -> None:
        """Test creating successful validation result."""
        # Arrange & Act
        result = ValidationResult(
            success=True, error_message="", sanitized_value="test"
        )

        # Assert
        assert result.success is True
        assert result.error_message == ""
        assert result.sanitized_value == "test"

    def test_validation_result_failure(self) -> None:
        """Test creating failed validation result."""
        # Arrange & Act
        result = ValidationResult(success=False, error_message="Error occurred")

        # Assert
        assert result.success is False
        assert result.error_message == "Error occurred"
        assert result.sanitized_value is None


class TestPathValidation:
    """Test path validation functionality."""

    def test_validate_path_empty_string(self) -> None:
        """Test that empty path string fails validation."""
        # Arrange
        path_str = ""

        # Act
        result = InputValidator.validate_path(path_str)

        # Assert
        assert result.success is False
        assert "empty" in result.error_message.lower()

    def test_validate_path_whitespace_only(self) -> None:
        """Test that whitespace-only path fails validation."""
        # Arrange
        path_str = "   "

        # Act
        result = InputValidator.validate_path(path_str)

        # Assert
        assert result.success is False
        assert "empty" in result.error_message.lower()

    def test_validate_path_null_bytes(self) -> None:
        """Test that path with null bytes fails validation (security)."""
        # Arrange
        path_str = "/home/user\x00/file.txt"

        # Act
        result = InputValidator.validate_path(path_str)

        # Assert
        assert result.success is False
        assert "null bytes" in result.error_message.lower()

    def test_validate_path_too_long(self) -> None:
        """Test that excessively long path fails validation."""
        # Arrange
        path_str = "/" + "a" * 5000  # Exceeds MAX_PATH_LENGTH (4096)

        # Act
        result = InputValidator.validate_path(path_str)

        # Assert
        assert result.success is False
        assert "maximum length" in result.error_message.lower()

    def test_validate_path_valid_absolute(self) -> None:
        """Test that valid absolute path passes validation."""
        # Arrange
        path_str = "/home/user/test.txt"

        # Act
        result = InputValidator.validate_path(path_str)

        # Assert
        assert result.success is True
        assert result.error_message == ""
        assert result.sanitized_value is not None

    def test_validate_path_valid_with_tilde(self) -> None:
        """Test that path with tilde is expanded and validated."""
        # Arrange
        path_str = "~/test.txt"

        # Act
        result = InputValidator.validate_path(path_str)

        # Assert
        assert result.success is True
        assert result.sanitized_value is not None
        assert "~" not in result.sanitized_value  # Should be expanded

    def test_validate_path_must_exist_nonexistent(self, tmp_path: Path) -> None:
        """Test that nonexistent path fails when must_exist=True."""
        # Arrange
        path_str = str(tmp_path / "nonexistent.txt")

        # Act
        result = InputValidator.validate_path(path_str, must_exist=True)

        # Assert
        assert result.success is False
        assert "does not exist" in result.error_message.lower()

    def test_validate_path_must_exist_existing(self, tmp_path: Path) -> None:
        """Test that existing path passes when must_exist=True."""
        # Arrange
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        path_str = str(test_file)

        # Act
        result = InputValidator.validate_path(path_str, must_exist=True)

        # Assert
        assert result.success is True
        assert result.sanitized_value is not None


class TestStringValidation:
    """Test string validation functionality."""

    def test_validate_string_empty_not_allowed(self) -> None:
        """Test that empty string fails when not allowed."""
        # Arrange
        value = ""

        # Act
        result = InputValidator.validate_string(value, "TestField", allow_empty=False)

        # Assert
        assert result.success is False
        assert "empty" in result.error_message.lower()

    def test_validate_string_empty_allowed(self) -> None:
        """Test that empty string passes when allowed."""
        # Arrange
        value = ""

        # Act
        result = InputValidator.validate_string(value, "TestField", allow_empty=True)

        # Assert
        assert result.success is True
        assert result.sanitized_value == ""

    def test_validate_string_whitespace_only(self) -> None:
        """Test that whitespace-only string fails."""
        # Arrange
        value = "   "

        # Act
        result = InputValidator.validate_string(value, "TestField", allow_empty=False)

        # Assert
        assert result.success is False
        assert "empty" in result.error_message.lower()

    def test_validate_string_too_short(self) -> None:
        """Test that string below minimum length fails."""
        # Arrange
        value = "ab"

        # Act
        result = InputValidator.validate_string(value, "TestField", min_length=3)

        # Assert
        assert result.success is False
        assert "at least 3" in result.error_message.lower()

    def test_validate_string_too_long(self) -> None:
        """Test that string exceeding maximum length fails."""
        # Arrange
        value = "a" * 300

        # Act
        result = InputValidator.validate_string(value, "TestField", max_length=256)

        # Assert
        assert result.success is False
        assert "maximum length" in result.error_message.lower()

    def test_validate_string_control_characters(self) -> None:
        """Test that string with control characters fails (security)."""
        # Arrange
        value = "test\x01string"

        # Act
        result = InputValidator.validate_string(value, "TestField")

        # Assert
        assert result.success is False
        assert "control characters" in result.error_message.lower()

    def test_validate_string_valid(self) -> None:
        """Test that valid string passes validation."""
        # Arrange
        value = "Valid String"

        # Act
        result = InputValidator.validate_string(value, "TestField")

        # Assert
        assert result.success is True
        assert result.sanitized_value == "Valid String"

    def test_validate_string_trims_whitespace(self) -> None:
        """Test that validation trims leading/trailing whitespace."""
        # Arrange
        value = "  Valid String  "

        # Act
        result = InputValidator.validate_string(value, "TestField")

        # Assert
        assert result.success is True
        assert result.sanitized_value == "Valid String"


class TestIntegerValidation:
    """Test integer validation functionality."""

    def test_validate_integer_valid_int(self) -> None:
        """Test that valid integer passes validation."""
        # Arrange
        value = 42

        # Act
        result = InputValidator.validate_integer(value, "TestValue")

        # Assert
        assert result.success is True
        assert result.sanitized_value == "42"

    def test_validate_integer_valid_string(self) -> None:
        """Test that valid integer string is converted."""
        # Arrange
        value = "42"

        # Act
        result = InputValidator.validate_integer(value, "TestValue")

        # Assert
        assert result.success is True
        assert result.sanitized_value == "42"

    def test_validate_integer_invalid_string(self) -> None:
        """Test that non-numeric string fails validation."""
        # Arrange
        value = "not a number"

        # Act
        result = InputValidator.validate_integer(value, "TestValue")

        # Assert
        assert result.success is False
        assert "valid integer" in result.error_message.lower()

    def test_validate_integer_below_minimum(self) -> None:
        """Test that integer below minimum fails validation."""
        # Arrange
        value = 5

        # Act
        result = InputValidator.validate_integer(value, "TestValue", min_value=10)

        # Assert
        assert result.success is False
        assert "at least 10" in result.error_message.lower()

    def test_validate_integer_above_maximum(self) -> None:
        """Test that integer above maximum fails validation."""
        # Arrange
        value = 100

        # Act
        result = InputValidator.validate_integer(value, "TestValue", max_value=50)

        # Assert
        assert result.success is False
        assert "at most 50" in result.error_message.lower()

    def test_validate_integer_within_range(self) -> None:
        """Test that integer within range passes validation."""
        # Arrange
        value = 25

        # Act
        result = InputValidator.validate_integer(
            value, "TestValue", min_value=0, max_value=100
        )

        # Assert
        assert result.success is True
        assert result.sanitized_value == "25"


class TestBooleanValidation:
    """Test boolean validation functionality."""

    def test_validate_boolean_true(self) -> None:
        """Test that boolean True passes validation."""
        # Arrange
        value = True

        # Act
        result = InputValidator.validate_boolean(value, "TestValue")

        # Assert
        assert result.success is True
        assert result.sanitized_value == "true"

    def test_validate_boolean_false(self) -> None:
        """Test that boolean False passes validation."""
        # Arrange
        value = False

        # Act
        result = InputValidator.validate_boolean(value, "TestValue")

        # Assert
        assert result.success is True
        assert result.sanitized_value == "false"

    def test_validate_boolean_string_true_variants(self) -> None:
        """Test that various true string variants pass validation."""
        # Arrange
        true_variants = ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON"]

        # Act & Assert
        for variant in true_variants:
            result = InputValidator.validate_boolean(variant, "TestValue")
            assert result.success is True
            assert result.sanitized_value == "true"

    def test_validate_boolean_string_false_variants(self) -> None:
        """Test that various false string variants pass validation."""
        # Arrange
        false_variants = ["false", "False", "FALSE", "0", "no", "NO", "off", "OFF"]

        # Act & Assert
        for variant in false_variants:
            result = InputValidator.validate_boolean(variant, "TestValue")
            assert result.success is True
            assert result.sanitized_value == "false"

    def test_validate_boolean_invalid_string(self) -> None:
        """Test that invalid boolean string fails validation."""
        # Arrange
        value = "maybe"

        # Act
        result = InputValidator.validate_boolean(value, "TestValue")

        # Assert
        assert result.success is False
        assert "valid boolean" in result.error_message.lower()


class TestFilenameSanitization:
    """Test filename sanitization functionality."""

    def test_sanitize_filename_removes_illegal_characters(self) -> None:
        """Test that sanitize_filename removes illegal filesystem characters."""
        # Arrange
        filename = 'test<>:"/\\|?*\x00file.txt'

        # Act
        result = InputValidator.sanitize_filename(filename)

        # Assert
        # 10 illegal characters (<>:"/\|?*\x00) replaced with underscores
        assert result == "test__________file.txt"

    def test_sanitize_filename_removes_leading_dots(self) -> None:
        """Test that leading dots are removed."""
        # Arrange
        filename = "...test.txt"

        # Act
        result = InputValidator.sanitize_filename(filename)

        # Assert
        assert not result.startswith(".")

    def test_sanitize_filename_removes_trailing_dots(self) -> None:
        """Test that trailing dots are removed."""
        # Arrange
        filename = "test.txt..."

        # Act
        result = InputValidator.sanitize_filename(filename)

        # Assert
        assert not result.endswith(".")

    def test_sanitize_filename_handles_empty_result(self) -> None:
        """Test that empty result gets default name."""
        # Arrange
        filename = "..."

        # Act
        result = InputValidator.sanitize_filename(filename)

        # Assert
        assert result == "unnamed_file"

    def test_sanitize_filename_truncates_long_names(self) -> None:
        """Test that excessively long filenames are truncated."""
        # Arrange
        filename = "a" * 300 + ".txt"

        # Act
        result = InputValidator.sanitize_filename(filename)

        # Assert
        assert len(result) <= 255

    def test_sanitize_filename_preserves_valid_names(self) -> None:
        """Test that valid filenames are preserved."""
        # Arrange
        filename = "valid_filename-123.txt"

        # Act
        result = InputValidator.sanitize_filename(filename)

        # Assert
        assert result == filename


class TestArchiveValidation:
    """Test archive-specific validation methods."""

    def test_validate_archive_compression_level_valid(self) -> None:
        """Test that valid compression level (0-9) passes."""
        # Arrange & Act & Assert
        for level in range(10):
            result = InputValidator.validate_archive_compression_level(level)
            assert result.success is True
            assert result.sanitized_value == str(level)

    def test_validate_archive_compression_level_below_minimum(self) -> None:
        """Test that compression level below 0 fails."""
        # Arrange
        level = -1

        # Act
        result = InputValidator.validate_archive_compression_level(level)

        # Assert
        assert result.success is False
        assert "at least 0" in result.error_message.lower()

    def test_validate_archive_compression_level_above_maximum(self) -> None:
        """Test that compression level above 9 fails."""
        # Arrange
        level = 10

        # Act
        result = InputValidator.validate_archive_compression_level(level)

        # Assert
        assert result.success is False
        assert "at most 9" in result.error_message.lower()

    def test_validate_max_archives_valid(self) -> None:
        """Test that valid max archives count passes."""
        # Arrange
        count = 5

        # Act
        result = InputValidator.validate_max_archives(count)

        # Assert
        assert result.success is True
        assert result.sanitized_value == "5"

    def test_validate_max_archives_below_minimum(self) -> None:
        """Test that max archives below 1 fails."""
        # Arrange
        count = 0

        # Act
        result = InputValidator.validate_max_archives(count)

        # Assert
        assert result.success is False
        assert "at least 1" in result.error_message.lower()

    def test_validate_max_archives_above_maximum(self) -> None:
        """Test that max archives above 100 fails."""
        # Arrange
        count = 101

        # Act
        result = InputValidator.validate_max_archives(count)

        # Assert
        assert result.success is False
        assert "at most 100" in result.error_message.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
