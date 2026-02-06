"""
Tests for the SizeAnalyzer component.

Covers:
    - Size threshold categorization
    - .dfbuignore pattern matching
    - Dotfile size analysis
    - Report generation
    - Error handling
    - Log formatting
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from core.common_types import DotFileDict

from gui.size_analyzer import (
    BYTES_PER_MB,
    DEFAULT_ALERT_THRESHOLD_MB,
    DEFAULT_CRITICAL_THRESHOLD_MB,
    DEFAULT_WARNING_THRESHOLD_MB,
    SizeAnalyzer,
)


@pytest.fixture
def mock_file_ops() -> MagicMock:
    """Create a mock FileOperationsProtocol."""
    mock = MagicMock()
    mock.expand_path.side_effect = lambda p: Path(p).expanduser()
    mock.calculate_path_size.return_value = 0
    return mock


@pytest.fixture
def size_analyzer(mock_file_ops: MagicMock) -> SizeAnalyzer:
    """Create a SizeAnalyzer instance with mock file operations."""
    return SizeAnalyzer(file_operations=mock_file_ops)


class TestSizeAnalyzerInit:
    """Tests for SizeAnalyzer initialization."""

    @pytest.mark.unit
    def test_default_thresholds(self, mock_file_ops: MagicMock) -> None:
        """Default initialization uses expected thresholds."""
        sa = SizeAnalyzer(file_operations=mock_file_ops)
        assert sa.warning_threshold_mb == DEFAULT_WARNING_THRESHOLD_MB
        assert sa.alert_threshold_mb == DEFAULT_ALERT_THRESHOLD_MB
        assert sa.critical_threshold_mb == DEFAULT_CRITICAL_THRESHOLD_MB

    @pytest.mark.unit
    def test_custom_thresholds(self, mock_file_ops: MagicMock) -> None:
        """Can initialize with custom thresholds."""
        sa = SizeAnalyzer(
            file_operations=mock_file_ops,
            warning_threshold_mb=5,
            alert_threshold_mb=50,
            critical_threshold_mb=500,
        )
        assert sa.warning_threshold_mb == 5
        assert sa.alert_threshold_mb == 50
        assert sa.critical_threshold_mb == 500

    @pytest.mark.unit
    def test_size_check_enabled_default(self, mock_file_ops: MagicMock) -> None:
        """Size checking is enabled by default."""
        sa = SizeAnalyzer(file_operations=mock_file_ops)
        assert sa.size_check_enabled is True

    @pytest.mark.unit
    def test_size_check_can_be_disabled(self, mock_file_ops: MagicMock) -> None:
        """Size checking can be disabled on init."""
        sa = SizeAnalyzer(file_operations=mock_file_ops, size_check_enabled=False)
        assert sa.size_check_enabled is False


class TestThresholdSetters:
    """Tests for threshold property setters."""

    @pytest.mark.unit
    def test_warning_threshold_setter(self, size_analyzer: SizeAnalyzer) -> None:
        """Warning threshold can be changed."""
        size_analyzer.warning_threshold_mb = 20
        assert size_analyzer.warning_threshold_mb == 20

    @pytest.mark.unit
    def test_warning_threshold_minimum(self, size_analyzer: SizeAnalyzer) -> None:
        """Warning threshold has minimum of 1."""
        size_analyzer.warning_threshold_mb = 0
        assert size_analyzer.warning_threshold_mb == 1

        size_analyzer.warning_threshold_mb = -5
        assert size_analyzer.warning_threshold_mb == 1

    @pytest.mark.unit
    def test_alert_threshold_setter(self, size_analyzer: SizeAnalyzer) -> None:
        """Alert threshold can be changed."""
        size_analyzer.alert_threshold_mb = 200
        assert size_analyzer.alert_threshold_mb == 200

    @pytest.mark.unit
    def test_critical_threshold_setter(self, size_analyzer: SizeAnalyzer) -> None:
        """Critical threshold can be changed."""
        size_analyzer.critical_threshold_mb = 2048
        assert size_analyzer.critical_threshold_mb == 2048


class TestCategorizeSizes:
    """Tests for size categorization by threshold."""

    @pytest.mark.unit
    def test_info_level(self, size_analyzer: SizeAnalyzer) -> None:
        """Sizes below warning threshold are 'info'."""
        # 5 MB < 10 MB warning threshold
        size_bytes = 5 * BYTES_PER_MB
        assert size_analyzer.categorize_size(size_bytes) == "info"

    @pytest.mark.unit
    def test_warning_level(self, size_analyzer: SizeAnalyzer) -> None:
        """Sizes at or above warning but below alert are 'warning'."""
        # 10 MB = warning threshold
        size_bytes = 10 * BYTES_PER_MB
        assert size_analyzer.categorize_size(size_bytes) == "warning"

        # 50 MB = between warning and alert
        size_bytes = 50 * BYTES_PER_MB
        assert size_analyzer.categorize_size(size_bytes) == "warning"

    @pytest.mark.unit
    def test_alert_level(self, size_analyzer: SizeAnalyzer) -> None:
        """Sizes at or above alert but below critical are 'alert'."""
        # 100 MB = alert threshold
        size_bytes = 100 * BYTES_PER_MB
        assert size_analyzer.categorize_size(size_bytes) == "alert"

        # 500 MB = between alert and critical
        size_bytes = 500 * BYTES_PER_MB
        assert size_analyzer.categorize_size(size_bytes) == "alert"

    @pytest.mark.unit
    def test_critical_level(self, size_analyzer: SizeAnalyzer) -> None:
        """Sizes at or above critical threshold are 'critical'."""
        # 1024 MB = critical threshold
        size_bytes = 1024 * BYTES_PER_MB
        assert size_analyzer.categorize_size(size_bytes) == "critical"

        # 2048 MB = above critical
        size_bytes = 2048 * BYTES_PER_MB
        assert size_analyzer.categorize_size(size_bytes) == "critical"


class TestIgnorePatterns:
    """Tests for .dfbuignore pattern loading and matching."""

    @pytest.mark.unit
    def test_load_patterns_from_file(
        self, size_analyzer: SizeAnalyzer, tmp_path: Path
    ) -> None:
        """Patterns are loaded from ignore file."""
        ignore_file = tmp_path / ".dfbuignore"
        ignore_file.write_text("**/cache/\n*.log\n# comment\n\n**/temp/\n")

        patterns = size_analyzer.load_ignore_patterns(ignore_file)

        assert len(patterns) == 3
        assert "**/cache/" in patterns
        assert "*.log" in patterns
        assert "**/temp/" in patterns
        assert "# comment" not in patterns

    @pytest.mark.unit
    def test_load_patterns_missing_file(self, size_analyzer: SizeAnalyzer) -> None:
        """Missing ignore file returns empty list."""
        patterns = size_analyzer.load_ignore_patterns(Path("/nonexistent/.dfbuignore"))
        assert patterns == []

    @pytest.mark.unit
    def test_matches_simple_pattern(self, size_analyzer: SizeAnalyzer) -> None:
        """Simple filename pattern matching works."""
        patterns = ["*.log"]
        assert size_analyzer.matches_ignore_pattern(Path("/var/log/test.log"), patterns)
        assert not size_analyzer.matches_ignore_pattern(
            Path("/var/log/test.txt"), patterns
        )

    @pytest.mark.unit
    def test_matches_directory_pattern(self, size_analyzer: SizeAnalyzer) -> None:
        """Directory pattern matching works."""
        # Pattern for .cache directory (note the dot)
        patterns = ["**/.cache/"]

        # Should match paths containing '.cache' directory
        assert size_analyzer.matches_ignore_pattern(
            Path("/home/user/.cache/thumbnails"), patterns
        )

        # Pattern for cache2 directory
        patterns2 = ["**/cache2/"]
        assert size_analyzer.matches_ignore_pattern(
            Path("/home/user/.mozilla/firefox/profile/cache2/entries"), patterns2
        )

    @pytest.mark.unit
    def test_empty_patterns_no_match(self, size_analyzer: SizeAnalyzer) -> None:
        """Empty pattern list matches nothing."""
        assert not size_analyzer.matches_ignore_pattern(Path("/any/path"), [])


class TestAnalyzeDotfiles:
    """Tests for dotfile size analysis."""

    @pytest.mark.unit
    def test_analyze_empty_dotfiles(self, size_analyzer: SizeAnalyzer) -> None:
        """Empty dotfile list returns empty report."""
        report = size_analyzer.analyze_dotfiles([])

        assert report["total_files"] == 0
        assert report["total_size_bytes"] == 0
        assert report["large_items"] == []
        assert not report["has_warning"]
        assert not report["has_alert"]
        assert not report["has_critical"]

    @pytest.mark.unit
    def test_analyze_single_small_file(
        self, size_analyzer: SizeAnalyzer, mock_file_ops: MagicMock, tmp_path: Path
    ) -> None:
        """Small file analysis doesn't trigger warnings."""
        # Setup mock to return small size (1 MB)
        test_path = tmp_path / ".bashrc"
        test_path.touch()
        mock_file_ops.expand_path.return_value = test_path
        mock_file_ops.calculate_path_size.return_value = 1 * BYTES_PER_MB

        dotfiles: list[DotFileDict] = [
            {"description": "Bash", "paths": [str(test_path)]}
        ]
        report = size_analyzer.analyze_dotfiles(dotfiles)

        assert report["total_files"] == 1
        assert report["total_size_bytes"] == 1 * BYTES_PER_MB
        assert len(report["large_items"]) == 0
        assert not report["has_warning"]

    @pytest.mark.unit
    def test_analyze_large_file_triggers_warning(
        self, size_analyzer: SizeAnalyzer, mock_file_ops: MagicMock, tmp_path: Path
    ) -> None:
        """Large file triggers warning in report."""
        # Setup mock to return large size (50 MB = warning level)
        test_path = tmp_path / ".config/bigapp"
        test_path.mkdir(parents=True)
        mock_file_ops.expand_path.return_value = test_path
        mock_file_ops.calculate_path_size.return_value = 50 * BYTES_PER_MB

        dotfiles: list[DotFileDict] = [
            {"description": "BigApp", "paths": [str(test_path)]}
        ]
        report = size_analyzer.analyze_dotfiles(dotfiles)

        assert report["has_warning"] is True
        assert len(report["large_items"]) == 1
        assert report["large_items"][0]["level"] == "warning"
        assert report["large_items"][0]["application"] == "BigApp"

    @pytest.mark.unit
    def test_analyze_critical_file(
        self, size_analyzer: SizeAnalyzer, mock_file_ops: MagicMock, tmp_path: Path
    ) -> None:
        """Critical size file is flagged correctly."""
        # Setup mock to return critical size (2 GB)
        test_path = tmp_path / ".mozilla"
        test_path.mkdir(parents=True)
        mock_file_ops.expand_path.return_value = test_path
        mock_file_ops.calculate_path_size.return_value = 2048 * BYTES_PER_MB

        dotfiles: list[DotFileDict] = [
            {"description": "Firefox", "paths": [str(test_path)]}
        ]
        report = size_analyzer.analyze_dotfiles(dotfiles)

        assert report["has_critical"] is True
        assert report["large_items"][0]["level"] == "critical"

    @pytest.mark.unit
    def test_progress_callback_called(
        self, size_analyzer: SizeAnalyzer, mock_file_ops: MagicMock, tmp_path: Path
    ) -> None:
        """Progress callback is invoked during analysis."""
        test_path = tmp_path / ".bashrc"
        test_path.touch()
        mock_file_ops.expand_path.return_value = test_path
        mock_file_ops.calculate_path_size.return_value = 1000

        progress_values: list[int] = []
        callback = lambda p: progress_values.append(p)

        dotfiles: list[DotFileDict] = [
            {"description": "Bash", "paths": [str(test_path)]}
        ]
        size_analyzer.analyze_dotfiles(dotfiles, progress_callback=callback)

        assert len(progress_values) > 0
        assert 100 in progress_values  # Should reach 100%

    @pytest.mark.unit
    def test_items_sorted_by_size(
        self, size_analyzer: SizeAnalyzer, mock_file_ops: MagicMock, tmp_path: Path
    ) -> None:
        """Large items are sorted by size (largest first)."""
        path1 = tmp_path / ".small"
        path2 = tmp_path / ".large"
        path1.touch()
        path2.touch()

        # Mock different sizes for each path
        def mock_size(path: Path) -> int:
            if "large" in str(path):
                return int(200 * BYTES_PER_MB)  # Alert level
            return int(50 * BYTES_PER_MB)  # Warning level

        mock_file_ops.expand_path.side_effect = lambda p: Path(p)
        mock_file_ops.calculate_path_size.side_effect = mock_size

        dotfiles: list[DotFileDict] = [
            {"description": "Small", "paths": [str(path1)]},
            {"description": "Large", "paths": [str(path2)]},
        ]
        report = size_analyzer.analyze_dotfiles(dotfiles)

        assert len(report["large_items"]) == 2
        # Largest should be first
        assert report["large_items"][0]["application"] == "Large"
        assert report["large_items"][1]["application"] == "Small"


class TestFormatReport:
    """Tests for report log formatting."""

    @pytest.mark.unit
    def test_format_empty_report(self, size_analyzer: SizeAnalyzer) -> None:
        """Empty report formats correctly."""
        report = size_analyzer.analyze_dotfiles([])
        formatted = size_analyzer.format_report_for_log(report)

        assert "BACKUP SIZE ANALYSIS REPORT" in formatted
        assert "Total Files:  0" in formatted
        assert "Total Size:   0.0 MB" in formatted

    @pytest.mark.unit
    def test_format_report_with_large_items(
        self, size_analyzer: SizeAnalyzer, mock_file_ops: MagicMock, tmp_path: Path
    ) -> None:
        """Report with large items formats correctly."""
        test_path = tmp_path / ".bigdir"
        test_path.mkdir()
        mock_file_ops.expand_path.return_value = test_path
        mock_file_ops.calculate_path_size.return_value = 150 * BYTES_PER_MB

        dotfiles: list[DotFileDict] = [
            {"description": "BigDir", "paths": [str(test_path)]}
        ]
        report = size_analyzer.analyze_dotfiles(dotfiles)
        formatted = size_analyzer.format_report_for_log(report)

        assert "LARGE ITEMS" in formatted
        assert "ALERT" in formatted
        assert "BigDir" in formatted

    @pytest.mark.unit
    def test_format_report_includes_patterns(self, size_analyzer: SizeAnalyzer) -> None:
        """Report includes excluded patterns when present."""
        report = size_analyzer.analyze_dotfiles(
            [], ignore_patterns=["**/cache/", "*.log"]
        )
        formatted = size_analyzer.format_report_for_log(report)

        assert "EXCLUDED PATTERNS" in formatted
        assert "**/cache/" in formatted
        assert "*.log" in formatted


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    @pytest.mark.unit
    def test_nonexistent_path_skipped(
        self, size_analyzer: SizeAnalyzer, mock_file_ops: MagicMock
    ) -> None:
        """Non-existent paths are skipped gracefully."""
        mock_file_ops.expand_path.return_value = Path("/nonexistent/path")
        mock_file_ops.calculate_path_size.return_value = 0

        dotfiles: list[DotFileDict] = [
            {"description": "Missing", "paths": ["/nonexistent/path"]}
        ]
        report = size_analyzer.analyze_dotfiles(dotfiles)

        # Should not crash, just skip
        assert report["total_files"] == 0

    @pytest.mark.unit
    def test_handles_single_path_field(
        self, size_analyzer: SizeAnalyzer, mock_file_ops: MagicMock, tmp_path: Path
    ) -> None:
        """Dotfile with 'path' field (singular) is handled."""
        test_path = tmp_path / ".bashrc"
        test_path.touch()
        mock_file_ops.expand_path.return_value = test_path
        mock_file_ops.calculate_path_size.return_value = 1000

        # Use 'path' instead of 'paths'
        dotfiles: list[DotFileDict] = [{"description": "Bash", "path": str(test_path)}]
        report = size_analyzer.analyze_dotfiles(dotfiles)

        assert report["total_files"] == 1
