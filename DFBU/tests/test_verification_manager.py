"""
Tests for the VerificationManager component.

Covers:
    - Size verification
    - SHA-256 hash verification
    - Report generation
    - Error handling
    - Log formatting
"""

import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))
from verification_manager import VerificationManager


class TestVerificationManagerInit:
    """Tests for VerificationManager initialization."""

    @pytest.mark.unit
    def test_default_hash_verification_disabled(self) -> None:
        """Default initialization has hash verification disabled."""
        vm = VerificationManager()
        assert vm.hash_verification_enabled is False

    @pytest.mark.unit
    def test_hash_verification_enabled_init(self) -> None:
        """Can initialize with hash verification enabled."""
        vm = VerificationManager(hash_verification_enabled=True)
        assert vm.hash_verification_enabled is True

    @pytest.mark.unit
    def test_hash_verification_setter(self) -> None:
        """Hash verification can be toggled after initialization."""
        vm = VerificationManager()
        assert vm.hash_verification_enabled is False

        vm.hash_verification_enabled = True
        assert vm.hash_verification_enabled is True

        vm.hash_verification_enabled = False
        assert vm.hash_verification_enabled is False


class TestVerifyFile:
    """Tests for single file verification."""

    @pytest.mark.unit
    def test_verify_file_identical(self, tmp_path: Path) -> None:
        """Identical files pass verification."""
        vm = VerificationManager()

        # Create source and backup files with same content
        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        content = "test content\n"
        source.write_text(content)
        backup.write_text(content)

        size_match, hash_match, error = vm.verify_file(source, backup)

        assert size_match is True
        assert hash_match is None  # Hash verification disabled
        assert error == ""

    @pytest.mark.unit
    def test_verify_file_size_mismatch(self, tmp_path: Path) -> None:
        """Different sized files fail verification."""
        vm = VerificationManager()

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        source.write_text("longer content\n")
        backup.write_text("short\n")

        size_match, hash_match, error = vm.verify_file(source, backup)

        assert size_match is False
        assert hash_match is None
        assert error == ""

    @pytest.mark.unit
    def test_verify_file_backup_missing(self, tmp_path: Path) -> None:
        """Missing backup file returns error."""
        vm = VerificationManager()

        source = tmp_path / "source.txt"
        backup = tmp_path / "missing.txt"
        source.write_text("test\n")

        size_match, hash_match, error = vm.verify_file(source, backup)

        assert size_match is False
        assert hash_match is None
        assert "Backup file missing" in error

    @pytest.mark.unit
    def test_verify_file_source_missing(self, tmp_path: Path) -> None:
        """Missing source file returns error."""
        vm = VerificationManager()

        source = tmp_path / "missing.txt"
        backup = tmp_path / "backup.txt"
        backup.write_text("test\n")

        size_match, hash_match, error = vm.verify_file(source, backup)

        assert size_match is False
        assert hash_match is None
        assert "Source file no longer exists" in error

    @pytest.mark.unit
    def test_verify_file_with_hash_match(self, tmp_path: Path) -> None:
        """Hash verification passes for identical content."""
        vm = VerificationManager(hash_verification_enabled=True)

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        content = "test content for hash\n"
        source.write_text(content)
        backup.write_text(content)

        size_match, hash_match, error = vm.verify_file(source, backup)

        assert size_match is True
        assert hash_match is True
        assert error == ""

    @pytest.mark.unit
    def test_verify_file_hash_mismatch_same_size(self, tmp_path: Path) -> None:
        """Hash verification catches content differences with same size."""
        vm = VerificationManager(hash_verification_enabled=True)

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        # Same length but different content
        source.write_text("AAAA")
        backup.write_text("BBBB")

        size_match, hash_match, error = vm.verify_file(source, backup)

        assert size_match is True  # Same size
        assert hash_match is False  # Different content
        assert error == ""


class TestVerifyBackup:
    """Tests for full backup verification."""

    @pytest.mark.unit
    def test_verify_backup_all_pass(self, tmp_path: Path) -> None:
        """All files passing returns success report."""
        vm = VerificationManager()

        # Create matching source and backup files
        source_dir = tmp_path / "source"
        backup_dir = tmp_path / "backup"
        source_dir.mkdir()
        backup_dir.mkdir()

        file_pairs: list[tuple[Path, Path]] = []
        for i in range(3):
            src = source_dir / f"file{i}.txt"
            bkp = backup_dir / f"file{i}.txt"
            content = f"content {i}\n"
            src.write_text(content)
            bkp.write_text(content)
            file_pairs.append((src, bkp))

        report = vm.verify_backup(backup_dir, file_pairs, "mirror")

        assert report["total_files"] == 3
        assert report["verified_ok"] == 3
        assert report["verified_failed"] == 0
        assert report["backup_type"] == "mirror"
        assert report["hash_verified"] is False
        assert len(report["results"]) == 3
        assert all(r["status"] == "ok" for r in report["results"])

    @pytest.mark.unit
    def test_verify_backup_some_fail(self, tmp_path: Path) -> None:
        """Mixed results reported correctly."""
        vm = VerificationManager()

        source_dir = tmp_path / "source"
        backup_dir = tmp_path / "backup"
        source_dir.mkdir()
        backup_dir.mkdir()

        # File 1: Match
        src1 = source_dir / "good.txt"
        bkp1 = backup_dir / "good.txt"
        src1.write_text("good\n")
        bkp1.write_text("good\n")

        # File 2: Size mismatch
        src2 = source_dir / "bad.txt"
        bkp2 = backup_dir / "bad.txt"
        src2.write_text("longer content\n")
        bkp2.write_text("short\n")

        file_pairs = [(src1, bkp1), (src2, bkp2)]
        report = vm.verify_backup(backup_dir, file_pairs, "mirror")

        assert report["total_files"] == 2
        assert report["verified_ok"] == 1
        assert report["verified_failed"] == 1

    @pytest.mark.unit
    def test_verify_backup_missing_file(self, tmp_path: Path) -> None:
        """Missing backup file reported as failed."""
        vm = VerificationManager()

        source = tmp_path / "source.txt"
        backup = tmp_path / "missing.txt"
        source.write_text("test\n")

        report = vm.verify_backup(tmp_path, [(source, backup)], "mirror")

        assert report["total_files"] == 1
        assert report["verified_ok"] == 0
        assert report["verified_failed"] == 1
        assert report["results"][0]["status"] == "missing"

    @pytest.mark.unit
    def test_verify_backup_with_hash_enabled(self, tmp_path: Path) -> None:
        """Hash verification flag reflected in report."""
        vm = VerificationManager(hash_verification_enabled=True)

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        source.write_text("test\n")
        backup.write_text("test\n")

        report = vm.verify_backup(tmp_path, [(source, backup)], "mirror")

        assert report["hash_verified"] is True
        assert report["results"][0]["hash_match"] is True

    @pytest.mark.unit
    def test_verify_backup_empty_list(self, tmp_path: Path) -> None:
        """Empty file list produces valid report with zero counts."""
        vm = VerificationManager()

        report = vm.verify_backup(tmp_path, [], "mirror")

        assert report["total_files"] == 0
        assert report["verified_ok"] == 0
        assert report["verified_failed"] == 0
        assert report["results"] == []

    @pytest.mark.unit
    def test_verify_backup_timestamp_format(self, tmp_path: Path) -> None:
        """Timestamp is in expected ISO format."""
        vm = VerificationManager()

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        source.write_text("test\n")
        backup.write_text("test\n")

        report = vm.verify_backup(tmp_path, [(source, backup)], "mirror")

        # Should be in format YYYY-MM-DDTHH:MM:SS
        timestamp = report["timestamp"]
        assert len(timestamp) == 19
        assert timestamp[4] == "-"
        assert timestamp[7] == "-"
        assert timestamp[10] == "T"
        assert timestamp[13] == ":"
        assert timestamp[16] == ":"


class TestFormatReportForLog:
    """Tests for log output formatting."""

    @pytest.mark.unit
    def test_format_report_all_pass(self, tmp_path: Path) -> None:
        """Success report formatted correctly."""
        vm = VerificationManager()

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        source.write_text("test\n")
        backup.write_text("test\n")

        report = vm.verify_backup(tmp_path, [(source, backup)], "mirror")
        formatted = vm.format_report_for_log(report)

        assert "BACKUP VERIFICATION REPORT" in formatted
        assert "All 1 files verified successfully" in formatted
        assert "FAILED FILES:" not in formatted

    @pytest.mark.unit
    def test_format_report_with_failures(self, tmp_path: Path) -> None:
        """Failure report includes details."""
        vm = VerificationManager()

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        source.write_text("longer\n")
        backup.write_text("short\n")

        report = vm.verify_backup(tmp_path, [(source, backup)], "mirror")
        formatted = vm.format_report_for_log(report)

        assert "FAILED FILES:" in formatted
        assert "size_mismatch" in formatted
        assert "1 files FAILED verification" in formatted

    @pytest.mark.unit
    def test_format_report_missing_file(self, tmp_path: Path) -> None:
        """Missing file reported with status."""
        vm = VerificationManager()

        source = tmp_path / "source.txt"
        backup = tmp_path / "missing.txt"
        source.write_text("test\n")

        report = vm.verify_backup(tmp_path, [(source, backup)], "mirror")
        formatted = vm.format_report_for_log(report)

        assert "FAILED FILES:" in formatted
        assert "missing" in formatted

    @pytest.mark.unit
    def test_format_report_hash_enabled_shown(self, tmp_path: Path) -> None:
        """Hash check status displayed in report."""
        vm = VerificationManager(hash_verification_enabled=True)

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        source.write_text("test\n")
        backup.write_text("test\n")

        report = vm.verify_backup(tmp_path, [(source, backup)], "mirror")
        formatted = vm.format_report_for_log(report)

        assert "Hash Check:   Enabled" in formatted

    @pytest.mark.unit
    def test_format_report_hash_disabled_shown(self, tmp_path: Path) -> None:
        """Hash check disabled status displayed in report."""
        vm = VerificationManager(hash_verification_enabled=False)

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        source.write_text("test\n")
        backup.write_text("test\n")

        report = vm.verify_backup(tmp_path, [(source, backup)], "mirror")
        formatted = vm.format_report_for_log(report)

        assert "Hash Check:   Disabled" in formatted

    @pytest.mark.unit
    def test_format_report_backup_type_shown(self, tmp_path: Path) -> None:
        """Backup type displayed in report."""
        vm = VerificationManager()

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        source.write_text("test\n")
        backup.write_text("test\n")

        report = vm.verify_backup(tmp_path, [(source, backup)], "archive")
        formatted = vm.format_report_for_log(report)

        assert "Backup Type:  archive" in formatted


class TestCalculateHash:
    """Tests for hash calculation."""

    @pytest.mark.unit
    def test_calculate_hash_known_value(self, tmp_path: Path) -> None:
        """Hash calculation produces expected value."""
        vm = VerificationManager()

        test_file = tmp_path / "test.txt"
        content = "hello world\n"
        test_file.write_text(content)

        # Calculate expected hash
        expected_hash = hashlib.sha256(content.encode()).hexdigest()

        # Access private method for direct testing
        actual_hash = vm._calculate_hash(test_file)

        assert actual_hash == expected_hash

    @pytest.mark.unit
    def test_calculate_hash_empty_file(self, tmp_path: Path) -> None:
        """Empty file has consistent hash."""
        vm = VerificationManager()

        test_file = tmp_path / "empty.txt"
        test_file.write_text("")

        expected_hash = hashlib.sha256(b"").hexdigest()
        actual_hash = vm._calculate_hash(test_file)

        assert actual_hash == expected_hash

    @pytest.mark.unit
    def test_calculate_hash_binary_file(self, tmp_path: Path) -> None:
        """Binary file hashed correctly."""
        vm = VerificationManager()

        test_file = tmp_path / "binary.bin"
        binary_content = bytes(range(256))
        test_file.write_bytes(binary_content)

        expected_hash = hashlib.sha256(binary_content).hexdigest()
        actual_hash = vm._calculate_hash(test_file)

        assert actual_hash == expected_hash

    @pytest.mark.unit
    def test_calculate_hash_large_file(self, tmp_path: Path) -> None:
        """Large file hashed correctly (tests chunking)."""
        vm = VerificationManager()

        test_file = tmp_path / "large.bin"
        # Create file larger than chunk size (65536 bytes)
        large_content = b"x" * 100000
        test_file.write_bytes(large_content)

        expected_hash = hashlib.sha256(large_content).hexdigest()
        actual_hash = vm._calculate_hash(test_file)

        assert actual_hash == expected_hash


class TestVerificationResultDict:
    """Tests for VerificationResultDict structure."""

    @pytest.mark.unit
    def test_result_contains_all_fields(self, tmp_path: Path) -> None:
        """Result dict contains all required fields."""
        vm = VerificationManager()

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        source.write_text("test\n")
        backup.write_text("test\n")

        report = vm.verify_backup(tmp_path, [(source, backup)], "mirror")
        result = report["results"][0]

        assert "path" in result
        assert "backup_path" in result
        assert "status" in result
        assert "size_match" in result
        assert "hash_match" in result
        assert "expected_size" in result
        assert "actual_size" in result
        assert "error" in result

    @pytest.mark.unit
    def test_result_sizes_correct(self, tmp_path: Path) -> None:
        """Result includes correct file sizes."""
        vm = VerificationManager()

        source = tmp_path / "source.txt"
        backup = tmp_path / "backup.txt"
        content = "test content\n"
        source.write_text(content)
        backup.write_text(content)

        report = vm.verify_backup(tmp_path, [(source, backup)], "mirror")
        result = report["results"][0]

        expected_size = len(content.encode())
        assert result["expected_size"] == expected_size
        assert result["actual_size"] == expected_size


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.unit
    def test_verify_symlink_source(self, tmp_path: Path) -> None:
        """Verification handles symlink sources."""
        vm = VerificationManager()

        actual_file = tmp_path / "actual.txt"
        actual_file.write_text("test\n")

        source_link = tmp_path / "source_link.txt"
        source_link.symlink_to(actual_file)

        backup = tmp_path / "backup.txt"
        backup.write_text("test\n")

        size_match, hash_match, error = vm.verify_file(source_link, backup)

        assert size_match is True
        assert error == ""

    @pytest.mark.unit
    def test_verify_unicode_content(self, tmp_path: Path) -> None:
        """Unicode content verified correctly."""
        vm = VerificationManager(hash_verification_enabled=True)

        source = tmp_path / "unicode.txt"
        backup = tmp_path / "backup.txt"
        content = "Hello \u4e16\u754c \U0001f600\n"  # Hello World with emoji
        source.write_text(content)
        backup.write_text(content)

        size_match, hash_match, error = vm.verify_file(source, backup)

        assert size_match is True
        assert hash_match is True
        assert error == ""

    @pytest.mark.unit
    def test_verify_backup_path_in_report(self, tmp_path: Path) -> None:
        """Backup path correctly stored in report."""
        vm = VerificationManager()
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir()

        source = tmp_path / "source.txt"
        backup = backup_dir / "backup.txt"
        source.write_text("test\n")
        backup.write_text("test\n")

        report = vm.verify_backup(backup_dir, [(source, backup)], "mirror")

        assert report["backup_path"] == str(backup_dir)
