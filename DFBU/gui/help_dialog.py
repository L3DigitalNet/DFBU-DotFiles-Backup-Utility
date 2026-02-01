"""Help dialog for DFBU application.

This module provides the HelpDialog class which displays user documentation
in a tabbed interface with Quick Start and Configuration Reference sections.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


class HelpDialog(QDialog):
    """User guide dialog with Quick Start and Configuration Reference tabs.

    A modal dialog displaying application documentation in a tabbed format.
    Content is rendered as HTML in QTextBrowser widgets for rich formatting.
    """

    QUICK_START_HTML = """
    <h2>DFBU - DotFiles Backup Utility</h2>
    <p>DFBU backs up your Linux configuration files (dotfiles) to keep them
    safe and portable across machines.</p>

    <h3>Backing Up Files</h3>
    <ol>
        <li>On the <b>Backup</b> tab, check the files you want to include</li>
        <li>Choose <b>Mirror</b> (uncompressed) and/or <b>Archive</b> (compressed) options</li>
        <li>Click <b>Start Backup</b></li>
    </ol>
    <p>Your files are copied to the configured backup directories, organized
    by hostname.</p>

    <h3>Restoring Files</h3>
    <ol>
        <li>Go to the <b>Restore</b> tab</li>
        <li>Click <b>Browse...</b> and select your backup directory
            (the folder containing your hostname subdirectory)</li>
        <li>Click <b>Start Restore</b></li>
    </ol>
    <p><b>Warning:</b> Restore overwrites existing files at their original locations.
    Enable pre-restore backups in Configuration to keep safety copies.</p>

    <h3>Where Are My Backups?</h3>
    <p>View and change backup locations on the <b>Configuration</b> tab:</p>
    <ul>
        <li><b>Mirror Directory:</b> Uncompressed copies preserving folder structure</li>
        <li><b>Archive Directory:</b> Compressed .tar.gz archives</li>
    </ul>

    <h3>Keyboard Shortcuts</h3>
    <table border="0" cellpadding="4">
        <tr><td><code>Ctrl+B</code></td><td>Start Backup</td></tr>
        <tr><td><code>Ctrl+R</code></td><td>Start Restore</td></tr>
        <tr><td><code>Ctrl+V</code></td><td>Verify Backup</td></tr>
        <tr><td><code>F1</code></td><td>Open this User Guide</td></tr>
        <tr><td><code>Ctrl+Q</code></td><td>Exit</td></tr>
    </table>
    """

    CONFIG_REFERENCE_HTML = """
    <h2>Configuration Reference</h2>
    <p>All settings are saved to <code>settings.yaml</code> in the DFBU data directory.</p>

    <h3>Backup Paths</h3>
    <table border="0" cellpadding="4" width="100%">
        <tr>
            <td width="30%"><b>Mirror Directory</b></td>
            <td>Directory where uncompressed mirror backups are stored.
                Files are copied preserving their original folder structure
                relative to your home directory.</td>
        </tr>
        <tr>
            <td><b>Archive Directory</b></td>
            <td>Directory where compressed archive backups (.tar.gz) are stored.
                Archives contain all selected files in a single compressed file.</td>
        </tr>
    </table>

    <h3>Backup Modes</h3>
    <table border="0" cellpadding="4" width="100%">
        <tr>
            <td width="30%"><b>Mirror Backup</b></td>
            <td>Enable copying files to the mirror directory. Creates an
                uncompressed copy you can browse like regular folders.
                <br/><i>Default: Enabled</i></td>
        </tr>
        <tr>
            <td><b>Archive Backup</b></td>
            <td>Enable creating compressed archives. Creates a single .tar.gz
                file containing all selected files.
                <br/><i>Default: Enabled</i></td>
        </tr>
    </table>

    <h3>Directory Structure</h3>
    <table border="0" cellpadding="4" width="100%">
        <tr>
            <td width="30%"><b>Hostname Subdir</b></td>
            <td>Create a subdirectory named after this computer's hostname.
                Useful when backing up multiple machines to the same location.
                <br/><i>Default: Enabled</i></td>
        </tr>
        <tr>
            <td><b>Date Subdir</b></td>
            <td>Create a subdirectory with today's date (YYYY-MM-DD) for each
                backup. Creates separate snapshots instead of overwriting.
                <br/><i>Default: Disabled</i></td>
        </tr>
    </table>

    <h3>Archive Options</h3>
    <table border="0" cellpadding="4" width="100%">
        <tr>
            <td width="30%"><b>Compression Level</b></td>
            <td>Gzip compression level for archives. 0 = no compression (fastest),
                9 = maximum compression (smallest files, slowest).
                <br/><i>Default: 9</i></td>
        </tr>
        <tr>
            <td><b>Rotate Archives</b></td>
            <td>Automatically delete the oldest archives when the maximum
                number is reached. Prevents unlimited archive accumulation.
                <br/><i>Default: Enabled</i></td>
        </tr>
        <tr>
            <td><b>Max Archives</b></td>
            <td>Maximum number of archive files to keep when rotation is enabled.
                Oldest archives are deleted first.
                <br/><i>Default: 5</i></td>
        </tr>
    </table>

    <h3>Pre-Restore Safety</h3>
    <table border="0" cellpadding="4" width="100%">
        <tr>
            <td width="30%"><b>Enable Pre-Restore Backup</b></td>
            <td>Before restoring files, create a backup of any existing files
                that would be overwritten. Allows recovery if restore goes wrong.
                <br/><i>Default: Enabled</i></td>
        </tr>
        <tr>
            <td><b>Max Restore Backups</b></td>
            <td>Maximum number of pre-restore backup sets to keep.
                Oldest sets are deleted when limit is reached.
                <br/><i>Default: 5</i></td>
        </tr>
        <tr>
            <td><b>Restore Backup Dir</b></td>
            <td>Directory where pre-restore backups are stored.
                <br/><i>Default: ~/.local/share/dfbu/restore-backups</i></td>
        </tr>
    </table>
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the help dialog.

        Args:
            parent: Parent widget, typically the main window.
        """
        super().__init__(parent)
        self.setWindowTitle("DFBU User Guide")
        self.setMinimumSize(500, 400)
        self.resize(650, 550)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI with tabs and buttons."""
        layout = QVBoxLayout(self)

        # Create tab widget
        tab_widget = QTabWidget()

        # Quick Start tab
        quick_start_browser = QTextBrowser()
        quick_start_browser.setHtml(self.QUICK_START_HTML)
        quick_start_browser.setOpenExternalLinks(True)
        tab_widget.addTab(quick_start_browser, "Quick Start")

        # Configuration Reference tab
        config_browser = QTextBrowser()
        config_browser.setHtml(self.CONFIG_REFERENCE_HTML)
        config_browser.setOpenExternalLinks(True)
        tab_widget.addTab(config_browser, "Configuration Reference")

        layout.addWidget(tab_widget)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
