"""Theme loader utility for applying QSS stylesheets to the application."""

from pathlib import Path

from PySide6.QtWidgets import QApplication


def load_theme(app: QApplication, theme_name: str = "dfbu_light") -> bool:
    """Load and apply a QSS theme to the application.

    Args:
        app: The QApplication instance to apply the theme to.
        theme_name: Name of the theme file (without .qss extension).

    Returns:
        True if the theme was loaded successfully, False otherwise.
    """
    qss_path = Path(__file__).parent / "styles" / f"{theme_name}.qss"
    if not qss_path.exists():
        return False
    app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
    return True
