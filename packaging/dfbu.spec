# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for DFBU - Dotfiles Backup Utility.

This creates a --onedir distribution with all PySide6 dependencies,
data files (.yaml configs), and Qt Designer .ui files bundled.

Usage: pyinstaller packaging/dfbu.spec
Output: dist/dfbu/ (directory with executable + libraries)
"""

import sys
from pathlib import Path

block_cipher = None

# Project root is one level up from this spec file
project_root = Path(SPECPATH).parent

# Data files to bundle (source, destination_in_bundle)
datas = [
    # YAML configuration templates
    # Destination matches dfbu_gui.py: BUNDLED_CONFIG_PATH = _data_base / "data"
    (str(project_root / 'DFBU' / 'data' / 'settings.yaml'), 'data'),
    (str(project_root / 'DFBU' / 'data' / 'dotfiles.yaml'), 'data'),
    (str(project_root / 'DFBU' / 'data' / 'session.yaml'), 'data'),
    (str(project_root / 'DFBU' / 'data' / '.dfbuignore'), 'data'),
    # Qt Designer UI files
    # Destination matches view.py: Path(__file__).parent / "designer"
    (str(project_root / 'DFBU' / 'gui' / 'designer' / 'main_window_complete.ui'), 'gui/designer'),
    (str(project_root / 'DFBU' / 'gui' / 'designer' / 'add_dotfile_dialog.ui'), 'gui/designer'),
    (str(project_root / 'DFBU' / 'gui' / 'designer' / 'recovery_dialog.ui'), 'gui/designer'),
    (str(project_root / 'DFBU' / 'gui' / 'designer' / 'size_warning_dialog.ui'), 'gui/designer'),
    (str(project_root / 'DFBU' / 'gui' / 'designer' / 'profile_dialog.ui'), 'gui/designer'),
    # QSS theme stylesheets
    # Destination matches theme_loader.py: Path(__file__).parent / "styles"
    (str(project_root / 'DFBU' / 'gui' / 'styles' / 'dfbu_light.qss'), 'gui/styles'),
    (str(project_root / 'DFBU' / 'gui' / 'styles' / 'dfbu_dark.qss'), 'gui/styles'),
    # Help content HTML files
    # Destination matches help_dialog.py: Path(__file__).parent.parent / "resources" / "help"
    (str(project_root / 'DFBU' / 'resources' / 'help' / 'quick_start.html'), 'resources/help'),
    (str(project_root / 'DFBU' / 'resources' / 'help' / 'config_reference.html'), 'resources/help'),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    'PySide6.QtWidgets',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtUiTools',
    'ruamel.yaml',
    'tomli_w',
]

a = Analysis(
    [str(project_root / 'DFBU' / 'dfbu_gui.py')],
    pathex=[str(project_root), str(project_root / 'DFBU')],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary PySide6 modules to reduce size
        'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtQuick',
        'PySide6.QtQuick3D',
        'PySide6.QtQml',
        'PySide6.QtBluetooth',
        'PySide6.QtNfc',
        'PySide6.QtPositioning',
        'PySide6.QtSensors',
        'PySide6.QtSerialPort',
        'PySide6.QtWebSockets',
        'PySide6.QtTest',
        'PySide6.QtDesigner',
        # Exclude test/dev dependencies
        'pytest',
        'pytest_qt',
        'pytest_mock',
        'pytest_cov',
        'mypy',
        'coverage',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='dfbu',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application, no terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='dfbu',
)
