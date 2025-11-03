"""
Tests for Logging Configuration Module

Description:
    Tests for logging setup, configuration, and log rotation functionality.

Author: Chris Purcell
Email: chris@l3digital.net
GitHub: https://github.com/L3DigitalNet
Date Created: 11-03-2025
License: MIT
"""

import logging
import sys
from pathlib import Path

import pytest


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gui.logging_config import get_logger, setup_default_logging, setup_logging


class TestLoggingSetup:
    """Test logging setup functionality."""

    def test_setup_logging_creates_logger(self) -> None:
        """Test that setup_logging configures root logger."""
        # Arrange
        logging.root.handlers.clear()  # Clean slate

        # Act
        setup_logging(level=logging.INFO, console_output=True, file_output=False)

        # Assert
        assert logging.root.level == logging.INFO
        assert len(logging.root.handlers) > 0

    def test_setup_logging_console_only(self) -> None:
        """Test setup with console output only."""
        # Arrange
        logging.root.handlers.clear()

        # Act
        setup_logging(level=logging.DEBUG, console_output=True, file_output=False)

        # Assert
        assert len(logging.root.handlers) == 1
        assert isinstance(logging.root.handlers[0], logging.StreamHandler)

    def test_setup_logging_with_file_output(self, tmp_path: Path) -> None:
        """Test setup with file output."""
        # Arrange
        logging.root.handlers.clear()
        # Monkey patch LOG_DIR for testing
        import gui.logging_config as log_config

        original_log_dir = log_config.LOG_DIR
        original_log_file = log_config.LOG_FILE
        log_config.LOG_DIR = tmp_path
        log_config.LOG_FILE = tmp_path / "test.log"

        try:
            # Act
            setup_logging(level=logging.INFO, console_output=False, file_output=True)

            # Assert
            assert len(logging.root.handlers) > 0
            assert (tmp_path / "test.log").exists()
        finally:
            # Restore
            log_config.LOG_DIR = original_log_dir
            log_config.LOG_FILE = original_log_file
            logging.root.handlers.clear()

    def test_setup_logging_clears_existing_handlers(self) -> None:
        """Test that setup_logging removes existing handlers."""
        # Arrange
        logging.root.handlers.clear()
        old_handler = logging.StreamHandler()
        logging.root.addHandler(old_handler)

        # Act
        setup_logging(level=logging.INFO, console_output=True, file_output=False)

        # Assert
        # Should have cleared old handler and added new one
        assert old_handler not in logging.root.handlers

    def test_setup_logging_with_different_levels(self) -> None:
        """Test setup with different logging levels."""
        # Arrange & Act & Assert
        for level in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]:
            logging.root.handlers.clear()
            setup_logging(level=level, console_output=True, file_output=False)
            assert logging.root.level == level

    def test_setup_default_logging(self) -> None:
        """Test default logging setup."""
        # Arrange
        logging.root.handlers.clear()

        # Act
        setup_default_logging()

        # Assert
        assert logging.root.level == logging.INFO
        assert len(logging.root.handlers) > 0


class TestGetLogger:
    """Test get_logger functionality."""

    def test_get_logger_returns_logger(self) -> None:
        """Test that get_logger returns a logger instance."""
        # Act
        logger = get_logger("test_module")

        # Assert
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_different_names(self) -> None:
        """Test that get_logger returns different loggers for different names."""
        # Act
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        # Assert
        assert logger1 is not logger2
        assert logger1.name == "module1"
        assert logger2.name == "module2"

    def test_get_logger_same_name_returns_same_logger(self) -> None:
        """Test that get_logger returns same logger for same name."""
        # Act
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")

        # Assert
        assert logger1 is logger2


class TestLoggingFunctionality:
    """Test actual logging functionality."""

    def test_logger_can_log_messages(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that logger can log messages."""
        # Arrange
        logger = get_logger("test")

        # Act
        with caplog.at_level(logging.INFO, logger="test"):
            logger.info("Test message")

        # Assert
        assert "Test message" in caplog.text

    def test_logger_respects_log_level(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that logger respects configured log level."""
        # Arrange
        logger = get_logger("test")

        # Act
        with caplog.at_level(logging.WARNING, logger="test"):
            logger.debug("Debug message")  # Should not appear
            logger.warning("Warning message")  # Should appear

        # Assert
        assert "Debug message" not in caplog.text
        assert "Warning message" in caplog.text

    def test_logger_formats_messages_correctly(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that logger formats messages with proper structure."""
        # Arrange
        logger = get_logger("test_module")

        # Act
        with caplog.at_level(logging.INFO, logger="test_module"):
            logger.info("Test message")

        # Assert
        # Check that log contains module name
        assert "test_module" in caplog.text or "test" in caplog.text

    def test_logger_handles_exception_info(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that logger can log exception information."""
        # Arrange
        logger = get_logger("test")

        # Act
        with caplog.at_level(logging.ERROR, logger="test"):
            try:
                raise ValueError("Test exception")
            except ValueError:
                logger.error("Error occurred", exc_info=True)

        # Assert
        assert "Error occurred" in caplog.text
        # Exception info should be in the log
        assert "ValueError" in caplog.text or "Traceback" in caplog.text


class TestLogRotation:
    """Test log rotation functionality (file handler specific)."""

    def test_rotating_file_handler_created(self, tmp_path: Path) -> None:
        """Test that rotating file handler is created when file_output=True."""
        # Arrange
        logging.root.handlers.clear()
        import gui.logging_config as log_config

        original_log_dir = log_config.LOG_DIR
        original_log_file = log_config.LOG_FILE
        log_config.LOG_DIR = tmp_path
        log_config.LOG_FILE = tmp_path / "test.log"

        try:
            # Act
            setup_logging(level=logging.INFO, console_output=False, file_output=True)

            # Assert
            handlers = logging.root.handlers
            assert len(handlers) > 0
            # Check for rotating file handler
            from logging.handlers import RotatingFileHandler

            rotating_handlers = [
                h for h in handlers if isinstance(h, RotatingFileHandler)
            ]
            assert len(rotating_handlers) > 0
        finally:
            # Restore
            log_config.LOG_DIR = original_log_dir
            log_config.LOG_FILE = original_log_file
            logging.root.handlers.clear()

    def test_log_file_is_created(self, tmp_path: Path) -> None:
        """Test that log file is created in specified directory."""
        # Arrange
        logging.root.handlers.clear()
        import gui.logging_config as log_config

        original_log_dir = log_config.LOG_DIR
        original_log_file = log_config.LOG_FILE
        log_config.LOG_DIR = tmp_path
        log_config.LOG_FILE = tmp_path / "test.log"

        try:
            # Act
            setup_logging(level=logging.INFO, console_output=False, file_output=True)
            logger = get_logger("test")
            logger.info("Test message")

            # Flush handlers to ensure write
            for handler in logging.root.handlers:
                handler.flush()

            # Assert
            assert (tmp_path / "test.log").exists()
            log_content = (tmp_path / "test.log").read_text()
            assert "Test message" in log_content
        finally:
            # Cleanup
            for handler in logging.root.handlers:
                handler.close()
            logging.root.handlers.clear()
            log_config.LOG_DIR = original_log_dir
            log_config.LOG_FILE = original_log_file


class TestLoggingErrorHandling:
    """Test error handling in logging setup."""

    def test_setup_continues_without_file_on_permission_error(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that setup continues if file creation fails."""
        # Arrange
        logging.root.handlers.clear()
        import gui.logging_config as log_config

        # Create a directory we can't write to (simulate permission error)
        read_only_dir = tmp_path / "readonly"
        read_only_dir.mkdir()
        read_only_dir.chmod(0o444)  # Read-only

        original_log_dir = log_config.LOG_DIR
        original_log_file = log_config.LOG_FILE
        log_config.LOG_DIR = read_only_dir
        log_config.LOG_FILE = read_only_dir / "test.log"

        try:
            # Act - should not raise exception
            setup_logging(level=logging.INFO, console_output=True, file_output=True)

            # Assert - should have console handler even if file failed
            assert len(logging.root.handlers) > 0
            stream_handlers = [
                h for h in logging.root.handlers if isinstance(h, logging.StreamHandler)
            ]
            assert len(stream_handlers) > 0
        finally:
            # Cleanup
            logging.root.handlers.clear()
            read_only_dir.chmod(0o755)  # Restore permissions for cleanup
            log_config.LOG_DIR = original_log_dir
            log_config.LOG_FILE = original_log_file


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
