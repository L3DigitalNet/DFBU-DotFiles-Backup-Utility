"""
Tests for the ErrorHandler component.

Covers:
    - PathResultDict creation
    - OperationResultDict creation
    - Exception handling and categorization
    - User-friendly message formatting
    - Result finalization
    - Log formatting
    - Retry eligibility determination
"""

import errno

import pytest

from gui.error_handler import (
    ERRNO_TO_ERROR_TYPE,
    ErrorHandler,
    NON_RETRYABLE_ERROR_TYPES,
    RETRYABLE_ERROR_TYPES,
    USER_MESSAGE_TEMPLATES,
)


class TestCreatePathResult:
    """Tests for create_path_result method."""

    @pytest.mark.unit
    def test_create_success_result(self) -> None:
        """Success result created with correct fields."""
        # Arrange
        handler = ErrorHandler()

        # Act
        result = handler.create_path_result(
            path="/home/user/.bashrc",
            dest_path="/backup/.bashrc",
            status="success",
        )

        # Assert
        assert result["path"] == "/home/user/.bashrc"
        assert result["dest_path"] == "/backup/.bashrc"
        assert result["status"] == "success"
        assert result["error_type"] is None
        assert result["error_message"] == ""
        assert result["can_retry"] is False

    @pytest.mark.unit
    def test_create_failed_result_with_all_fields(self) -> None:
        """Failed result includes all error information."""
        # Arrange
        handler = ErrorHandler()

        # Act
        result = handler.create_path_result(
            path="/home/user/.vimrc",
            dest_path="/backup/.vimrc",
            status="failed",
            error_type="permission",
            error_message="Permission denied",
            can_retry=True,
        )

        # Assert
        assert result["path"] == "/home/user/.vimrc"
        assert result["dest_path"] == "/backup/.vimrc"
        assert result["status"] == "failed"
        assert result["error_type"] == "permission"
        assert result["error_message"] == "Permission denied"
        assert result["can_retry"] is True

    @pytest.mark.unit
    def test_create_skipped_result(self) -> None:
        """Skipped result created correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        result = handler.create_path_result(
            path="/home/user/.config",
            dest_path=None,
            status="skipped",
            error_message="No changes detected",
        )

        # Assert
        assert result["status"] == "skipped"
        assert result["dest_path"] is None
        assert result["error_message"] == "No changes detected"

    @pytest.mark.unit
    def test_create_warning_result(self) -> None:
        """Warning result created correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        result = handler.create_path_result(
            path="/home/user/.profile",
            dest_path="/backup/.profile",
            status="warning",
            error_message="File is a symlink",
        )

        # Assert
        assert result["status"] == "warning"
        assert result["error_message"] == "File is a symlink"


class TestCreateOperationResult:
    """Tests for create_operation_result method."""

    @pytest.mark.unit
    def test_create_mirror_backup_result(self) -> None:
        """Mirror backup operation result initialized correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        result = handler.create_operation_result("mirror_backup")

        # Assert
        assert result["status"] == "pending"
        assert result["operation_type"] == "mirror_backup"
        assert result["total_items"] == 0
        assert result["completed"] == []
        assert result["failed"] == []
        assert result["skipped"] == []
        assert result["warnings"] == []
        assert result["can_retry"] == []

    @pytest.mark.unit
    def test_create_archive_backup_result(self) -> None:
        """Archive backup operation result initialized correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        result = handler.create_operation_result("archive_backup")

        # Assert
        assert result["operation_type"] == "archive_backup"
        assert result["status"] == "pending"

    @pytest.mark.unit
    def test_create_restore_result(self) -> None:
        """Restore operation result initialized correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        result = handler.create_operation_result("restore")

        # Assert
        assert result["operation_type"] == "restore"
        assert result["status"] == "pending"

    @pytest.mark.unit
    def test_timestamp_format_iso(self) -> None:
        """Timestamp is in ISO format with timezone."""
        # Arrange
        handler = ErrorHandler()

        # Act
        result = handler.create_operation_result("mirror_backup")

        # Assert
        timestamp = result["timestamp"]
        # ISO format: YYYY-MM-DDTHH:MM:SS.ssssss+00:00
        assert "T" in timestamp
        assert len(timestamp) > 19  # At least YYYY-MM-DDTHH:MM:SS


class TestHandleException:
    """Tests for handle_exception method."""

    @pytest.mark.unit
    def test_handle_permission_error(self) -> None:
        """PermissionError converted correctly."""
        # Arrange
        handler = ErrorHandler()
        exc = PermissionError("Permission denied")

        # Act
        result = handler.handle_exception(exc, "/home/user/.bashrc", "/backup/.bashrc")

        # Assert
        assert result["status"] == "failed"
        assert result["error_type"] == "permission"
        assert result["can_retry"] is True
        assert "permission denied" in result["error_message"].lower()

    @pytest.mark.unit
    def test_handle_file_not_found_error(self) -> None:
        """FileNotFoundError converted correctly."""
        # Arrange
        handler = ErrorHandler()
        exc = FileNotFoundError("No such file or directory")

        # Act
        result = handler.handle_exception(exc, "/home/user/missing.txt")

        # Assert
        assert result["error_type"] == "not_found"
        assert result["can_retry"] is False
        assert "no longer exists" in result["error_message"].lower()

    @pytest.mark.unit
    def test_handle_file_exists_error(self) -> None:
        """FileExistsError converted correctly."""
        # Arrange
        handler = ErrorHandler()
        exc = FileExistsError("File exists")

        # Act
        result = handler.handle_exception(exc, "/home/user/.bashrc")

        # Assert
        assert result["error_type"] == "already_exists"
        assert result["can_retry"] is False

    @pytest.mark.unit
    def test_handle_is_a_directory_error(self) -> None:
        """IsADirectoryError converted correctly."""
        # Arrange
        handler = ErrorHandler()
        exc = IsADirectoryError("Is a directory")

        # Act
        result = handler.handle_exception(exc, "/home/user/.config")

        # Assert
        assert result["error_type"] == "invalid_path"
        assert result["can_retry"] is False

    @pytest.mark.unit
    def test_handle_not_a_directory_error(self) -> None:
        """NotADirectoryError converted correctly."""
        # Arrange
        handler = ErrorHandler()
        exc = NotADirectoryError("Not a directory")

        # Act
        result = handler.handle_exception(exc, "/home/user/.bashrc/subdir")

        # Assert
        assert result["error_type"] == "invalid_path"
        assert result["can_retry"] is False

    @pytest.mark.unit
    def test_handle_oserror_disk_full(self) -> None:
        """OSError with ENOSPC converted to disk_full."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.ENOSPC, "No space left on device")

        # Act
        result = handler.handle_exception(exc, "/backup/.bashrc")

        # Assert
        assert result["error_type"] == "disk_full"
        assert result["can_retry"] is False
        assert "disk is full" in result["error_message"].lower()

    @pytest.mark.unit
    def test_handle_oserror_read_only(self) -> None:
        """OSError with EROFS converted to read_only."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EROFS, "Read-only file system")

        # Act
        result = handler.handle_exception(exc, "/backup/.bashrc")

        # Assert
        assert result["error_type"] == "read_only"
        assert result["can_retry"] is False

    @pytest.mark.unit
    def test_handle_oserror_busy(self) -> None:
        """OSError with EBUSY converted to busy."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EBUSY, "Device or resource busy")

        # Act
        result = handler.handle_exception(exc, "/home/user/.config/app.lock")

        # Assert
        assert result["error_type"] == "busy"
        assert result["can_retry"] is True

    @pytest.mark.unit
    def test_handle_oserror_temp_failure(self) -> None:
        """OSError with EAGAIN converted to temp_failure."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EAGAIN, "Resource temporarily unavailable")

        # Act
        result = handler.handle_exception(exc, "/home/user/.bashrc")

        # Assert
        assert result["error_type"] == "temp_failure"
        assert result["can_retry"] is True

    @pytest.mark.unit
    def test_handle_unknown_exception(self) -> None:
        """Generic exception converted to unknown."""
        # Arrange
        handler = ErrorHandler()
        exc = RuntimeError("Something unexpected")

        # Act
        result = handler.handle_exception(exc, "/home/user/.bashrc")

        # Assert
        assert result["error_type"] == "unknown"
        assert result["can_retry"] is False

    @pytest.mark.unit
    def test_handle_exception_preserves_paths(self) -> None:
        """Exception handling preserves source and destination paths."""
        # Arrange
        handler = ErrorHandler()
        exc = PermissionError("Permission denied")

        # Act
        result = handler.handle_exception(
            exc, "/home/user/.vimrc", "/backup/mirror/.vimrc"
        )

        # Assert
        assert result["path"] == "/home/user/.vimrc"
        assert result["dest_path"] == "/backup/mirror/.vimrc"

    @pytest.mark.unit
    def test_handle_exception_none_dest_path(self) -> None:
        """Exception handling works with None destination path."""
        # Arrange
        handler = ErrorHandler()
        exc = FileNotFoundError("Not found")

        # Act
        result = handler.handle_exception(exc, "/home/user/.bashrc", None)

        # Assert
        assert result["dest_path"] is None


class TestFormatUserMessage:
    """Tests for format_user_message method."""

    @pytest.mark.unit
    def test_format_permission_message(self) -> None:
        """Permission error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message(
            "permission", "/home/user/.bashrc", "Permission denied"
        )

        # Assert
        assert "/home/user/.bashrc" in message
        assert "permission denied" in message.lower()

    @pytest.mark.unit
    def test_format_not_found_message(self) -> None:
        """Not found error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("not_found", "/home/user/missing.txt")

        # Assert
        assert "/home/user/missing.txt" in message
        assert "no longer exists" in message.lower()

    @pytest.mark.unit
    def test_format_disk_full_message(self) -> None:
        """Disk full error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("disk_full", "/backup/.bashrc")

        # Assert
        assert "/backup/.bashrc" in message
        assert "disk is full" in message.lower()

    @pytest.mark.unit
    def test_format_read_only_message(self) -> None:
        """Read-only error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("read_only", "/backup/.bashrc")

        # Assert
        assert "/backup/.bashrc" in message
        assert "read-only" in message.lower()

    @pytest.mark.unit
    def test_format_locked_message(self) -> None:
        """Locked file error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("locked", "/home/user/app.lock")

        # Assert
        assert "/home/user/app.lock" in message
        assert "locked" in message.lower()

    @pytest.mark.unit
    def test_format_busy_message(self) -> None:
        """Busy resource error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("busy", "/home/user/.config/app.db")

        # Assert
        assert "/home/user/.config/app.db" in message
        assert "in use" in message.lower()

    @pytest.mark.unit
    def test_format_temp_failure_message(self) -> None:
        """Temporary failure error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("temp_failure", "/home/user/.bashrc")

        # Assert
        assert "/home/user/.bashrc" in message
        assert "retry" in message.lower()

    @pytest.mark.unit
    def test_format_already_exists_message(self) -> None:
        """Already exists error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("already_exists", "/backup/.bashrc")

        # Assert
        assert "/backup/.bashrc" in message
        assert "already exists" in message.lower()

    @pytest.mark.unit
    def test_format_invalid_path_message(self) -> None:
        """Invalid path error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("invalid_path", "/home/user/bad\x00path")

        # Assert
        assert "not a valid path" in message.lower()

    @pytest.mark.unit
    def test_format_symlink_loop_message(self) -> None:
        """Symlink loop error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("symlink_loop", "/home/user/link")

        # Assert
        assert "/home/user/link" in message
        assert "symbolic link loop" in message.lower()

    @pytest.mark.unit
    def test_format_io_error_message(self) -> None:
        """I/O error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("io_error", "/home/user/.bashrc")

        # Assert
        assert "/home/user/.bashrc" in message
        assert "i/o error" in message.lower()

    @pytest.mark.unit
    def test_format_too_many_files_message(self) -> None:
        """Too many files error message formatted correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("too_many_files", "/home/user/.config")

        # Assert
        assert "/home/user/.config" in message
        assert "too many files" in message.lower()

    @pytest.mark.unit
    def test_format_unknown_message_includes_original_error(self) -> None:
        """Unknown error type includes original error message."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message(
            "unknown", "/home/user/.bashrc", "Unexpected error occurred"
        )

        # Assert
        assert "/home/user/.bashrc" in message
        assert "Unexpected error occurred" in message

    @pytest.mark.unit
    def test_format_unrecognized_error_type_uses_unknown_template(self) -> None:
        """Unrecognized error type falls back to unknown template."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message(
            "nonexistent_type", "/home/user/.bashrc", "Some error"
        )

        # Assert
        assert "/home/user/.bashrc" in message
        assert "Some error" in message


class TestFinalizeResult:
    """Tests for finalize_result method."""

    @pytest.mark.unit
    def test_finalize_success_status(self) -> None:
        """All completed items results in success status."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["completed"].append(
            handler.create_path_result("/home/.bashrc", "/backup/.bashrc", "success")
        )
        result["completed"].append(
            handler.create_path_result("/home/.vimrc", "/backup/.vimrc", "success")
        )

        # Act
        finalized = handler.finalize_result(result)

        # Assert
        assert finalized["status"] == "success"
        assert finalized["total_items"] == 2

    @pytest.mark.unit
    def test_finalize_failed_status(self) -> None:
        """All failed items results in failed status."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["failed"].append(
            handler.create_path_result(
                "/home/.bashrc",
                "/backup/.bashrc",
                "failed",
                error_type="permission",
                can_retry=True,
            )
        )
        result["failed"].append(
            handler.create_path_result(
                "/home/.vimrc",
                "/backup/.vimrc",
                "failed",
                error_type="not_found",
                can_retry=False,
            )
        )

        # Act
        finalized = handler.finalize_result(result)

        # Assert
        assert finalized["status"] == "failed"
        assert finalized["total_items"] == 2

    @pytest.mark.unit
    def test_finalize_partial_status(self) -> None:
        """Mixed completed and failed results in partial status."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["completed"].append(
            handler.create_path_result("/home/.bashrc", "/backup/.bashrc", "success")
        )
        result["failed"].append(
            handler.create_path_result(
                "/home/.vimrc",
                "/backup/.vimrc",
                "failed",
                error_type="permission",
            )
        )

        # Act
        finalized = handler.finalize_result(result)

        # Assert
        assert finalized["status"] == "partial"
        assert finalized["total_items"] == 2

    @pytest.mark.unit
    def test_finalize_populates_can_retry_list(self) -> None:
        """Finalize populates can_retry list from failed items."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["failed"].append(
            handler.create_path_result(
                "/home/.bashrc",
                "/backup/.bashrc",
                "failed",
                error_type="permission",
                can_retry=True,
            )
        )
        result["failed"].append(
            handler.create_path_result(
                "/home/.vimrc",
                "/backup/.vimrc",
                "failed",
                error_type="not_found",
                can_retry=False,
            )
        )
        result["failed"].append(
            handler.create_path_result(
                "/home/.config/app",
                "/backup/.config/app",
                "failed",
                error_type="busy",
                can_retry=True,
            )
        )

        # Act
        finalized = handler.finalize_result(result)

        # Assert
        assert len(finalized["can_retry"]) == 2
        assert "/home/.bashrc" in finalized["can_retry"]
        assert "/home/.config/app" in finalized["can_retry"]
        assert "/home/.vimrc" not in finalized["can_retry"]

    @pytest.mark.unit
    def test_finalize_includes_skipped_in_total(self) -> None:
        """Total items includes skipped items."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["completed"].append(
            handler.create_path_result("/home/.bashrc", "/backup/.bashrc", "success")
        )
        result["skipped"].append(
            handler.create_path_result(
                "/home/.profile",
                None,
                "skipped",
                error_message="No changes",
            )
        )

        # Act
        finalized = handler.finalize_result(result)

        # Assert
        assert finalized["total_items"] == 2
        assert finalized["status"] == "success"  # Skipped don't cause failure

    @pytest.mark.unit
    def test_finalize_empty_result(self) -> None:
        """Empty result has zero total and success status."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")

        # Act
        finalized = handler.finalize_result(result)

        # Assert
        assert finalized["total_items"] == 0
        assert finalized["status"] == "success"  # No failures = success
        assert finalized["can_retry"] == []


class TestFormatSummaryForLog:
    """Tests for format_summary_for_log method."""

    @pytest.mark.unit
    def test_format_success_summary(self) -> None:
        """Success summary formatted correctly."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["completed"].append(
            handler.create_path_result("/home/.bashrc", "/backup/.bashrc", "success")
        )
        result = handler.finalize_result(result)

        # Act
        summary = handler.format_summary_for_log(result)

        # Assert
        assert "Mirror Backup" in summary
        assert "SUCCESS" in summary
        assert "Total items: 1" in summary
        assert "Completed: 1" in summary
        assert "Failed: 0" in summary

    @pytest.mark.unit
    def test_format_partial_summary(self) -> None:
        """Partial success summary formatted correctly."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("archive_backup")
        result["completed"].append(
            handler.create_path_result("/home/.bashrc", "/backup/.bashrc", "success")
        )
        result["failed"].append(
            handler.create_path_result(
                "/home/.vimrc",
                "/backup/.vimrc",
                "failed",
                error_type="permission",
                error_message="Permission denied",
            )
        )
        result = handler.finalize_result(result)

        # Act
        summary = handler.format_summary_for_log(result)

        # Assert
        assert "Archive Backup" in summary
        assert "PARTIAL" in summary
        assert "Total items: 2" in summary

    @pytest.mark.unit
    def test_format_failed_summary(self) -> None:
        """Failed summary formatted correctly."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("restore")
        result["failed"].append(
            handler.create_path_result(
                "/home/.bashrc",
                "/backup/.bashrc",
                "failed",
                error_type="not_found",
                error_message="File not found",
            )
        )
        result = handler.finalize_result(result)

        # Act
        summary = handler.format_summary_for_log(result)

        # Assert
        assert "Restore" in summary
        assert "FAILED" in summary

    @pytest.mark.unit
    def test_format_summary_includes_failed_items(self) -> None:
        """Summary includes failed items section."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["failed"].append(
            handler.create_path_result(
                "/home/.vimrc",
                "/backup/.vimrc",
                "failed",
                error_type="permission",
                error_message="Permission denied on ~/.vimrc",
                can_retry=True,
            )
        )
        result = handler.finalize_result(result)

        # Act
        summary = handler.format_summary_for_log(result)

        # Assert
        assert "Failed Items:" in summary
        assert "/home/.vimrc" in summary
        assert "Permission denied" in summary
        assert "[can retry]" in summary

    @pytest.mark.unit
    def test_format_summary_includes_skipped_items(self) -> None:
        """Summary includes skipped items section."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["completed"].append(
            handler.create_path_result("/home/.bashrc", "/backup/.bashrc", "success")
        )
        result["skipped"].append(
            handler.create_path_result(
                "/home/.profile",
                None,
                "skipped",
                error_message="No changes detected",
            )
        )
        result = handler.finalize_result(result)

        # Act
        summary = handler.format_summary_for_log(result)

        # Assert
        assert "Skipped Items:" in summary
        assert "/home/.profile" in summary
        assert "No changes detected" in summary

    @pytest.mark.unit
    def test_format_summary_includes_warnings(self) -> None:
        """Summary includes warnings section."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["completed"].append(
            handler.create_path_result("/home/.bashrc", "/backup/.bashrc", "success")
        )
        result["warnings"].append("Large file detected: ~/.config/app.db (500MB)")
        result["warnings"].append("Symlink not followed: ~/.bashrc.link")
        result = handler.finalize_result(result)

        # Act
        summary = handler.format_summary_for_log(result)

        # Assert
        assert "Warnings:" in summary
        assert "Large file detected" in summary
        assert "Symlink not followed" in summary

    @pytest.mark.unit
    def test_format_summary_includes_retry_suggestion(self) -> None:
        """Summary includes retry suggestion when retryable paths exist."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["failed"].append(
            handler.create_path_result(
                "/home/.bashrc",
                "/backup/.bashrc",
                "failed",
                error_type="permission",
                can_retry=True,
            )
        )
        result["failed"].append(
            handler.create_path_result(
                "/home/.vimrc",
                "/backup/.vimrc",
                "failed",
                error_type="busy",
                can_retry=True,
            )
        )
        result = handler.finalize_result(result)

        # Act
        summary = handler.format_summary_for_log(result)

        # Assert
        assert "2 items may succeed if retried" in summary

    @pytest.mark.unit
    def test_format_summary_skipped_default_message(self) -> None:
        """Skipped items without message show default reason."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["completed"].append(
            handler.create_path_result("/home/.bashrc", "/backup/.bashrc", "success")
        )
        result["skipped"].append(
            handler.create_path_result(
                "/home/.profile",
                None,
                "skipped",
                error_message="",  # Empty message
            )
        )
        result = handler.finalize_result(result)

        # Act
        summary = handler.format_summary_for_log(result)

        # Assert
        assert "No changes needed" in summary


class TestGetRetryablePaths:
    """Tests for get_retryable_paths method."""

    @pytest.mark.unit
    def test_returns_copy_of_can_retry_list(self) -> None:
        """Returns a copy, not the original list."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["failed"].append(
            handler.create_path_result(
                "/home/.bashrc",
                "/backup/.bashrc",
                "failed",
                error_type="permission",
                can_retry=True,
            )
        )
        result = handler.finalize_result(result)

        # Act
        paths = handler.get_retryable_paths(result)

        # Assert
        assert paths == result["can_retry"]
        assert paths is not result["can_retry"]  # Must be a copy

    @pytest.mark.unit
    def test_returns_empty_list_when_no_retryable(self) -> None:
        """Returns empty list when no retryable paths."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["failed"].append(
            handler.create_path_result(
                "/home/.bashrc",
                "/backup/.bashrc",
                "failed",
                error_type="not_found",
                can_retry=False,
            )
        )
        result = handler.finalize_result(result)

        # Act
        paths = handler.get_retryable_paths(result)

        # Assert
        assert paths == []

    @pytest.mark.unit
    def test_modifying_copy_does_not_affect_original(self) -> None:
        """Modifying returned list does not affect original."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["failed"].append(
            handler.create_path_result(
                "/home/.bashrc",
                "/backup/.bashrc",
                "failed",
                error_type="permission",
                can_retry=True,
            )
        )
        result = handler.finalize_result(result)

        # Act
        paths = handler.get_retryable_paths(result)
        paths.clear()

        # Assert
        assert len(result["can_retry"]) == 1


class TestCategorizeException:
    """Tests for _categorize_exception private method."""

    @pytest.mark.unit
    def test_permission_error_returns_permission(self) -> None:
        """PermissionError categorized as permission."""
        # Arrange
        handler = ErrorHandler()
        exc = PermissionError("Permission denied")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "permission"

    @pytest.mark.unit
    def test_file_not_found_error_returns_not_found(self) -> None:
        """FileNotFoundError categorized as not_found."""
        # Arrange
        handler = ErrorHandler()
        exc = FileNotFoundError("No such file or directory")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "not_found"

    @pytest.mark.unit
    def test_file_exists_error_returns_already_exists(self) -> None:
        """FileExistsError categorized as already_exists."""
        # Arrange
        handler = ErrorHandler()
        exc = FileExistsError("File exists")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "already_exists"

    @pytest.mark.unit
    def test_is_a_directory_error_returns_invalid_path(self) -> None:
        """IsADirectoryError categorized as invalid_path."""
        # Arrange
        handler = ErrorHandler()
        exc = IsADirectoryError("Is a directory")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "invalid_path"

    @pytest.mark.unit
    def test_not_a_directory_error_returns_invalid_path(self) -> None:
        """NotADirectoryError categorized as invalid_path."""
        # Arrange
        handler = ErrorHandler()
        exc = NotADirectoryError("Not a directory")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "invalid_path"

    @pytest.mark.unit
    def test_oserror_eacces_returns_permission(self) -> None:
        """OSError with EACCES categorized as permission."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EACCES, "Permission denied")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "permission"

    @pytest.mark.unit
    def test_oserror_eperm_returns_permission(self) -> None:
        """OSError with EPERM categorized as permission."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EPERM, "Operation not permitted")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "permission"

    @pytest.mark.unit
    def test_oserror_enoent_returns_not_found(self) -> None:
        """OSError with ENOENT categorized as not_found."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.ENOENT, "No such file or directory")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "not_found"

    @pytest.mark.unit
    def test_oserror_enospc_returns_disk_full(self) -> None:
        """OSError with ENOSPC categorized as disk_full."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.ENOSPC, "No space left on device")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "disk_full"

    @pytest.mark.unit
    def test_oserror_erofs_returns_read_only(self) -> None:
        """OSError with EROFS categorized as read_only."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EROFS, "Read-only file system")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "read_only"

    @pytest.mark.unit
    def test_oserror_ebusy_returns_busy(self) -> None:
        """OSError with EBUSY categorized as busy."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EBUSY, "Device or resource busy")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "busy"

    @pytest.mark.unit
    def test_oserror_etxtbsy_returns_busy(self) -> None:
        """OSError with ETXTBSY categorized as busy."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.ETXTBSY, "Text file busy")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "busy"

    @pytest.mark.unit
    def test_oserror_eagain_returns_temp_failure(self) -> None:
        """OSError with EAGAIN categorized as temp_failure."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EAGAIN, "Resource temporarily unavailable")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "temp_failure"

    @pytest.mark.unit
    def test_oserror_ewouldblock_returns_temp_failure(self) -> None:
        """OSError with EWOULDBLOCK categorized as temp_failure."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EWOULDBLOCK, "Operation would block")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "temp_failure"

    @pytest.mark.unit
    def test_oserror_eexist_returns_already_exists(self) -> None:
        """OSError with EEXIST categorized as already_exists."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EEXIST, "File exists")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "already_exists"

    @pytest.mark.unit
    def test_oserror_enotdir_returns_invalid_path(self) -> None:
        """OSError with ENOTDIR categorized as invalid_path."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.ENOTDIR, "Not a directory")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "invalid_path"

    @pytest.mark.unit
    def test_oserror_eisdir_returns_invalid_path(self) -> None:
        """OSError with EISDIR categorized as invalid_path."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EISDIR, "Is a directory")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "invalid_path"

    @pytest.mark.unit
    def test_oserror_enametoolong_returns_invalid_path(self) -> None:
        """OSError with ENAMETOOLONG categorized as invalid_path."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.ENAMETOOLONG, "File name too long")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "invalid_path"

    @pytest.mark.unit
    def test_oserror_eloop_returns_symlink_loop(self) -> None:
        """OSError with ELOOP categorized as symlink_loop."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.ELOOP, "Too many symbolic links")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "symlink_loop"

    @pytest.mark.unit
    def test_oserror_eio_returns_io_error(self) -> None:
        """OSError with EIO categorized as io_error."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EIO, "I/O error")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "io_error"

    @pytest.mark.unit
    def test_oserror_emfile_returns_too_many_files(self) -> None:
        """OSError with EMFILE categorized as too_many_files."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.EMFILE, "Too many open files")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "too_many_files"

    @pytest.mark.unit
    def test_oserror_enfile_returns_too_many_files(self) -> None:
        """OSError with ENFILE categorized as too_many_files."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError(errno.ENFILE, "Too many open files in system")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "too_many_files"

    @pytest.mark.unit
    def test_oserror_unknown_errno_returns_unknown(self) -> None:
        """OSError with unmapped errno categorized as unknown."""
        # Arrange
        handler = ErrorHandler()
        # Use an errno that's not in the mapping (e.g., EINTR)
        exc = OSError(errno.EINTR, "Interrupted system call")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "unknown"

    @pytest.mark.unit
    def test_oserror_no_errno_returns_unknown(self) -> None:
        """OSError without errno categorized as unknown."""
        # Arrange
        handler = ErrorHandler()
        exc = OSError("Generic OS error")
        exc.errno = None

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "unknown"

    @pytest.mark.unit
    def test_generic_exception_returns_unknown(self) -> None:
        """Generic exceptions categorized as unknown."""
        # Arrange
        handler = ErrorHandler()
        exc = RuntimeError("Something unexpected")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "unknown"

    @pytest.mark.unit
    def test_value_error_returns_unknown(self) -> None:
        """ValueError categorized as unknown."""
        # Arrange
        handler = ErrorHandler()
        exc = ValueError("Invalid value")

        # Act
        error_type = handler._categorize_exception(exc)

        # Assert
        assert error_type == "unknown"


class TestIsRetryable:
    """Tests for _is_retryable private method."""

    @pytest.mark.unit
    def test_permission_is_retryable(self) -> None:
        """Permission errors are retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("permission") is True

    @pytest.mark.unit
    def test_locked_is_retryable(self) -> None:
        """Locked errors are retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("locked") is True

    @pytest.mark.unit
    def test_busy_is_retryable(self) -> None:
        """Busy errors are retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("busy") is True

    @pytest.mark.unit
    def test_timeout_is_retryable(self) -> None:
        """Timeout errors are retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("timeout") is True

    @pytest.mark.unit
    def test_temp_failure_is_retryable(self) -> None:
        """Temporary failure errors are retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("temp_failure") is True

    @pytest.mark.unit
    def test_not_found_is_not_retryable(self) -> None:
        """Not found errors are not retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("not_found") is False

    @pytest.mark.unit
    def test_invalid_path_is_not_retryable(self) -> None:
        """Invalid path errors are not retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("invalid_path") is False

    @pytest.mark.unit
    def test_disk_full_is_not_retryable(self) -> None:
        """Disk full errors are not retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("disk_full") is False

    @pytest.mark.unit
    def test_read_only_is_not_retryable(self) -> None:
        """Read only errors are not retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("read_only") is False

    @pytest.mark.unit
    def test_unknown_is_not_retryable(self) -> None:
        """Unknown errors are not retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("unknown") is False

    @pytest.mark.unit
    def test_already_exists_is_not_retryable(self) -> None:
        """Already exists errors are not retryable."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        assert handler._is_retryable("already_exists") is False

    @pytest.mark.unit
    def test_all_retryable_types_match_constant(self) -> None:
        """All RETRYABLE_ERROR_TYPES return True."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        for error_type in RETRYABLE_ERROR_TYPES:
            assert handler._is_retryable(error_type) is True

    @pytest.mark.unit
    def test_all_non_retryable_types_match_constant(self) -> None:
        """All NON_RETRYABLE_ERROR_TYPES return False."""
        # Arrange
        handler = ErrorHandler()

        # Act/Assert
        for error_type in NON_RETRYABLE_ERROR_TYPES:
            assert handler._is_retryable(error_type) is False


class TestConstants:
    """Tests for module constants."""

    @pytest.mark.unit
    def test_retryable_error_types_is_frozenset(self) -> None:
        """RETRYABLE_ERROR_TYPES is a frozenset."""
        assert isinstance(RETRYABLE_ERROR_TYPES, frozenset)

    @pytest.mark.unit
    def test_non_retryable_error_types_is_frozenset(self) -> None:
        """NON_RETRYABLE_ERROR_TYPES is a frozenset."""
        assert isinstance(NON_RETRYABLE_ERROR_TYPES, frozenset)

    @pytest.mark.unit
    def test_errno_to_error_type_is_dict(self) -> None:
        """ERRNO_TO_ERROR_TYPE is a dict."""
        assert isinstance(ERRNO_TO_ERROR_TYPE, dict)

    @pytest.mark.unit
    def test_user_message_templates_has_all_error_types(self) -> None:
        """USER_MESSAGE_TEMPLATES covers all error types in ERRNO_TO_ERROR_TYPE."""
        # Get unique error types from ERRNO_TO_ERROR_TYPE
        error_types = set(ERRNO_TO_ERROR_TYPE.values())

        # Check each has a template
        for error_type in error_types:
            assert (
                error_type in USER_MESSAGE_TEMPLATES
                or error_type == "unknown"  # unknown always has a template
            ), f"Missing template for {error_type}"

    @pytest.mark.unit
    def test_user_message_templates_has_unknown(self) -> None:
        """USER_MESSAGE_TEMPLATES has an 'unknown' fallback."""
        assert "unknown" in USER_MESSAGE_TEMPLATES


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @pytest.mark.unit
    def test_empty_path_string(self) -> None:
        """Empty path string handled correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        result = handler.create_path_result(
            path="",
            dest_path="",
            status="failed",
            error_type="invalid_path",
        )

        # Assert
        assert result["path"] == ""
        assert result["dest_path"] == ""

    @pytest.mark.unit
    def test_unicode_path(self) -> None:
        """Unicode path handled correctly."""
        # Arrange
        handler = ErrorHandler()
        unicode_path = "/home/user/\u65e5\u672c\u8a9e/config.txt"

        # Act
        result = handler.create_path_result(
            path=unicode_path,
            dest_path="/backup/config.txt",
            status="success",
        )

        # Assert
        assert result["path"] == unicode_path

    @pytest.mark.unit
    def test_very_long_error_message(self) -> None:
        """Very long error message handled correctly."""
        # Arrange
        handler = ErrorHandler()
        long_message = "Error: " + "x" * 10000

        # Act
        result = handler.create_path_result(
            path="/home/user/.bashrc",
            dest_path="/backup/.bashrc",
            status="failed",
            error_type="unknown",
            error_message=long_message,
        )

        # Assert
        assert result["error_message"] == long_message

    @pytest.mark.unit
    def test_special_characters_in_path(self) -> None:
        """Paths with special characters handled correctly."""
        # Arrange
        handler = ErrorHandler()
        special_path = "/home/user/.config/app with spaces/file[1].conf"

        # Act
        result = handler.create_path_result(
            path=special_path,
            dest_path="/backup/file.conf",
            status="success",
        )

        # Assert
        assert result["path"] == special_path

    @pytest.mark.unit
    def test_format_user_message_with_braces_in_path(self) -> None:
        """Paths containing braces don't break message formatting."""
        # Arrange
        handler = ErrorHandler()
        path_with_braces = "/home/user/{backup}/config.txt"

        # Act
        message = handler.format_user_message("not_found", path_with_braces)

        # Assert
        assert path_with_braces in message

    @pytest.mark.unit
    def test_format_user_message_empty_original_error(self) -> None:
        """Empty original error string handled correctly."""
        # Arrange
        handler = ErrorHandler()

        # Act
        message = handler.format_user_message("unknown", "/home/user/.bashrc", "")

        # Assert
        assert "/home/user/.bashrc" in message

    @pytest.mark.unit
    def test_finalize_result_idempotent(self) -> None:
        """Calling finalize_result multiple times is idempotent."""
        # Arrange
        handler = ErrorHandler()
        result = handler.create_operation_result("mirror_backup")
        result["completed"].append(
            handler.create_path_result("/home/.bashrc", "/backup/.bashrc", "success")
        )

        # Act
        first_finalize = handler.finalize_result(result)
        second_finalize = handler.finalize_result(first_finalize)

        # Assert
        assert first_finalize["status"] == second_finalize["status"]
        assert first_finalize["total_items"] == second_finalize["total_items"]
