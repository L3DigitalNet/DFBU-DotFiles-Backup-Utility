# DFBU AppImage Packaging Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Package DFBU as a portable, single-file AppImage that users can download and run on any modern Linux distribution without installing dependencies.

**Architecture:** Use PyInstaller to freeze the Python 3.14 runtime + PySide6 + all dependencies into a standalone directory, then wrap it with `appimagetool` into a `.AppImage` file. This approach is the most reliable for PySide6 apps because it bundles the exact runtime and shared libraries from the build environment, avoiding glibc compatibility issues that plague `python-appimage` with newer Python versions. Desktop integration files (.desktop, AppStream metadata, SVG icon) are created to meet FreeDesktop standards.

**Tech Stack:** PyInstaller, appimagetool, PySide6 6.6+, Python 3.14+

**Why PyInstaller + appimagetool over `python-appimage`?**
- `python-appimage` relies on manylinux Docker images — Python 3.14 support is limited/unavailable
- PySide6 wheels target `manylinux_2_34` which causes glibc compatibility issues on older distros
- PyInstaller bundles the exact Python + Qt runtime from the build system — no compatibility guessing
- This is the approach recommended by the PySide6 community for AppImage distribution

---

## Audit Summary (Current State)

| Item | Status | Notes |
|------|--------|-------|
| Source code & architecture | ✅ Ready | Clean MVVM, well-tested |
| pyproject.toml metadata | ⚠️ Incomplete | Missing entry points, version mismatch (0.9.2 vs 1.0.0) |
| .desktop file | ❌ Missing | Required for AppImage desktop integration |
| AppStream metadata | ❌ Missing | Required for app stores / AppImageHub |
| Application icon | ❌ Missing | No .svg or .png anywhere in project |
| Entry points | ❌ Missing | No `[project.gui-scripts]` or `__main__.py` |
| Build scripts | ❌ Missing | No PyInstaller spec or build automation |
| Build backend | ⚠️ Implicit | No explicit `[build-system]` in pyproject.toml |

---

## Task 1: Fix pyproject.toml Metadata

**Files:**
- Modify: `pyproject.toml`

**Step 1: Update version to match application code**

The application code in `DFBU/dfbu-gui.py:87` declares `__version__ = "1.0.0"` but `pyproject.toml:3` says `version = "0.9.2"`. These must match.

```toml
# In [project] section, change:
version = "1.0.0"
```

**Step 2: Add build system declaration**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Step 3: Add GUI entry point**

```toml
[project.gui-scripts]
dfbu = "DFBU.dfbu_gui:main"
```

Note: The module path uses underscores (`dfbu_gui`) because Python module names can't contain hyphens. The file is `dfbu-gui.py` but Python resolves it as `dfbu_gui`.

**Step 4: Add project classifiers and URLs**

```toml
[project]
# ... existing fields ...
keywords = ["dotfiles", "backup", "restore", "configuration", "linux", "desktop"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: X11 Applications :: Qt",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: Python :: 3.14",
    "Topic :: System :: Archiving :: Backup",
    "Topic :: Utilities",
]

[project.urls]
Homepage = "https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility"
Repository = "https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility"
Issues = "https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility/issues"
Changelog = "https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility/blob/main/DFBU/docs/CHANGELOG.md"
```

**Step 5: Verify the changes**

Run: `cd /home/chris/projects/dfbu && uv sync`
Expected: No errors, dependencies resolve correctly

**Step 6: Commit**

```bash
git add pyproject.toml
git commit -m "chore: update pyproject.toml metadata for distribution"
```

---

## Task 2: Rename Entry Point File (Hyphen → Underscore)

Python cannot import modules with hyphens in their names. The file `DFBU/dfbu-gui.py` must be renamed to `DFBU/dfbu_gui.py` so that `[project.gui-scripts]` entry points work and PyInstaller can resolve the module.

**Files:**
- Rename: `DFBU/dfbu-gui.py` → `DFBU/dfbu_gui.py`
- Modify: `DFBU/__init__.py` (if it imports dfbu-gui)
- Modify: `CLAUDE.md` (update references)

**Step 1: Rename the file**

```bash
cd /home/chris/projects/dfbu
git mv DFBU/dfbu-gui.py DFBU/dfbu_gui.py
```

**Step 2: Update any references in CLAUDE.md**

Search for `dfbu-gui.py` and replace with `dfbu_gui.py` in documentation files. Do NOT update references in pyproject.toml (already uses underscore from Task 1).

**Step 3: Verify the app still launches**

Run: `cd /home/chris/projects/dfbu && python DFBU/dfbu_gui.py`
Expected: Application window appears

**Step 4: Run tests to confirm nothing broke**

Run: `cd /home/chris/projects/dfbu && pytest DFBU/tests/ -x -q`
Expected: All tests pass

**Step 5: Commit**

```bash
git add -A
git commit -m "refactor: rename dfbu-gui.py to dfbu_gui.py for module import compatibility"
```

---

## Task 3: Create `__main__.py` Entry Point

This allows running the app with `python -m DFBU` which is required for clean PyInstaller integration.

**Files:**
- Create: `DFBU/__main__.py`

**Step 1: Create the file**

```python
"""Allow running DFBU as a module: python -m DFBU"""

import sys

from DFBU.dfbu_gui import main

sys.exit(main())
```

**Step 2: Verify it works**

Run: `cd /home/chris/projects/dfbu && python -m DFBU`
Expected: Application window appears

**Step 3: Commit**

```bash
git add DFBU/__main__.py
git commit -m "feat: add __main__.py for python -m DFBU support"
```

---

## Task 4: Create Application Icon

DFBU needs an SVG icon for desktop integration. The icon should represent "dotfiles backup" — a combination of a gear/config symbol with a backup/shield motif.

**Files:**
- Create: `DFBU/resources/icons/dfbu.svg` (scalable source)
- Create: `DFBU/resources/icons/dfbu-256.png` (rendered for AppImage)

**Step 1: Create the resources directory**

```bash
mkdir -p /home/chris/projects/dfbu/DFBU/resources/icons
```

**Step 2: Create the SVG icon**

Create `DFBU/resources/icons/dfbu.svg` — a clean, modern icon with:
- A document/file shape as the base
- A circular arrow or shield overlay suggesting backup/protection
- Use the color palette: primary blue (#2563EB), accent green (#10B981)
- 256x256 viewBox for scalable rendering
- Keep it simple — no gradients or complex paths that render poorly at small sizes

The SVG should be a professional-quality icon suitable for Linux desktop menus.

**Step 3: Generate PNG from SVG**

```bash
# If rsvg-convert is available:
rsvg-convert -w 256 -h 256 DFBU/resources/icons/dfbu.svg > DFBU/resources/icons/dfbu-256.png

# Alternative if rsvg-convert is not installed:
sudo apt install librsvg2-bin
rsvg-convert -w 256 -h 256 DFBU/resources/icons/dfbu.svg > DFBU/resources/icons/dfbu-256.png
```

**Step 4: Verify the icon renders correctly**

Open the SVG in a viewer or browser to confirm it looks correct.

**Step 5: Commit**

```bash
git add DFBU/resources/icons/
git commit -m "feat: add application icon (SVG + 256px PNG)"
```

---

## Task 5: Create `.desktop` File

The `.desktop` file is required by FreeDesktop standards and by AppImage for desktop integration (showing in application menus, having an icon, etc.).

**Files:**
- Create: `packaging/com.l3digital.dfbu.desktop`

**Step 1: Create the packaging directory**

```bash
mkdir -p /home/chris/projects/dfbu/packaging
```

**Step 2: Create the .desktop file**

Create `packaging/com.l3digital.dfbu.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=DFBU
GenericName=Dotfiles Backup Utility
Comment=Backup and restore your Linux configuration files
Exec=dfbu
Icon=com.l3digital.dfbu
Terminal=false
Categories=Utility;System;Archiving;
Keywords=dotfiles;backup;restore;configuration;
StartupNotify=true
StartupWMClass=dfbu
```

**Step 3: Validate the .desktop file**

```bash
# Install desktop-file-utils if not present
sudo apt install desktop-file-utils 2>/dev/null
desktop-file-validate packaging/com.l3digital.dfbu.desktop
```

Expected: No errors or warnings

**Step 4: Commit**

```bash
git add packaging/com.l3digital.dfbu.desktop
git commit -m "feat: add FreeDesktop .desktop file for desktop integration"
```

---

## Task 6: Create AppStream Metadata

AppStream metadata (`appdata.xml`) describes the application for software centers and AppImageHub. This is required for listing on AppImageHub and recommended for all Linux desktop apps.

**Files:**
- Create: `packaging/com.l3digital.dfbu.appdata.xml`

**Step 1: Create the AppStream metadata file**

Create `packaging/com.l3digital.dfbu.appdata.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>com.l3digital.dfbu</id>
  <metadata_license>MIT</metadata_license>
  <project_license>MIT</project_license>
  <name>DFBU</name>
  <summary>Dotfiles Backup Utility for Linux</summary>
  <description>
    <p>
      DFBU is a desktop application for comprehensive backup and restoration of
      Linux configuration files (dotfiles). Built with a modern MVVM architecture,
      it provides an intuitive graphical interface for managing your configuration
      file backups.
    </p>
    <p>Features include:</p>
    <ul>
      <li>Mirror and compressed archive backup modes with rotation</li>
      <li>Interactive dotfile management with tags and descriptions</li>
      <li>Backup verification with size and optional SHA-256 hash checking</li>
      <li>Pre-restore safety backups for safe restoration</li>
      <li>File size analysis with configurable thresholds</li>
      <li>Hostname and date-based backup organization</li>
    </ul>
  </description>
  <url type="homepage">https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility</url>
  <url type="bugtracker">https://github.com/L3DigitalNet/DFBU-DotFiles-Backup-Utility/issues</url>
  <developer_name>Chris Purcell</developer_name>
  <launchable type="desktop-id">com.l3digital.dfbu.desktop</launchable>
  <provides>
    <binary>dfbu</binary>
  </provides>
  <releases>
    <release version="1.0.0" date="2026-02-01">
      <description>
        <p>Production release with full error handling and file size management.</p>
      </description>
    </release>
  </releases>
  <content_rating type="oars-1.1" />
  <categories>
    <category>Utility</category>
    <category>System</category>
  </categories>
</component>
```

**Step 2: Validate the AppStream metadata**

```bash
# Install appstream-util if not present
sudo apt install appstream-util 2>/dev/null
appstream-util validate-relax packaging/com.l3digital.dfbu.appdata.xml
```

Expected: Validation passes (warnings about missing screenshots are OK)

**Step 3: Commit**

```bash
git add packaging/com.l3digital.dfbu.appdata.xml
git commit -m "feat: add AppStream metadata for software centers"
```

---

## Task 7: Create PyInstaller Spec File

The `.spec` file tells PyInstaller exactly how to bundle DFBU — which files to include, which data directories to preserve, and how to structure the output.

**Files:**
- Create: `packaging/dfbu.spec`

**Step 1: Write the spec file**

Create `packaging/dfbu.spec`:

```python
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
    (str(project_root / 'DFBU' / 'data' / 'settings.yaml'), 'DFBU/data'),
    (str(project_root / 'DFBU' / 'data' / 'dotfiles.yaml'), 'DFBU/data'),
    (str(project_root / 'DFBU' / 'data' / 'library.yaml'), 'DFBU/data'),
    (str(project_root / 'DFBU' / 'data' / 'session.yaml'), 'DFBU/data'),
    # Qt Designer UI files
    (str(project_root / 'DFBU' / 'gui' / 'designer' / 'main_window_complete.ui'), 'DFBU/gui/designer'),
    (str(project_root / 'DFBU' / 'gui' / 'designer' / 'add_dotfile_dialog.ui'), 'DFBU/gui/designer'),
    (str(project_root / 'DFBU' / 'gui' / 'designer' / 'recovery_dialog.ui'), 'DFBU/gui/designer'),
    (str(project_root / 'DFBU' / 'gui' / 'designer' / 'size_warning_dialog.ui'), 'DFBU/gui/designer'),
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
    pathex=[str(project_root)],
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
```

**Step 2: Install PyInstaller as a dev dependency**

```bash
cd /home/chris/projects/dfbu
uv add --group dev pyinstaller
```

**Step 3: Test the PyInstaller build (dry run)**

```bash
cd /home/chris/projects/dfbu
uv run pyinstaller packaging/dfbu.spec --noconfirm
```

Expected: Build completes. Output directory at `dist/dfbu/` contains the `dfbu` executable and supporting libraries.

**Step 4: Test the frozen executable launches**

```bash
./dist/dfbu/dfbu
```

Expected: Application window appears, loads default config, UI files render correctly.

**Step 5: Commit**

```bash
git add packaging/dfbu.spec pyproject.toml uv.lock
git commit -m "feat: add PyInstaller spec file for frozen builds"
```

---

## Task 8: Create AppImage Build Script

This script automates the full pipeline: PyInstaller freeze → AppDir assembly → AppImage creation.

**Files:**
- Create: `packaging/build-appimage.sh`

**Step 1: Create the build script**

Create `packaging/build-appimage.sh`:

```bash
#!/usr/bin/env bash
#
# Build DFBU AppImage
#
# Requirements:
#   - uv (Python package manager)
#   - PyInstaller (installed as dev dependency)
#   - appimagetool (downloaded automatically if not found)
#
# Usage: ./packaging/build-appimage.sh
# Output: dist/DFBU-x86_64.AppImage
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build/appimage"
APPDIR="$BUILD_DIR/DFBU.AppDir"
DIST_DIR="$PROJECT_ROOT/dist"
ARCH="$(uname -m)"

echo "=== DFBU AppImage Builder ==="
echo "Project root: $PROJECT_ROOT"
echo "Architecture: $ARCH"
echo ""

# --- Step 1: Clean previous builds ---
echo "[1/6] Cleaning previous builds..."
rm -rf "$BUILD_DIR" "$DIST_DIR/dfbu" "$DIST_DIR/DFBU-$ARCH.AppImage"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

# --- Step 2: Run PyInstaller ---
echo "[2/6] Running PyInstaller..."
cd "$PROJECT_ROOT"
uv run pyinstaller packaging/dfbu.spec --noconfirm --distpath "$DIST_DIR" --workpath "$BUILD_DIR/pyinstaller-work"
echo "  PyInstaller output: $DIST_DIR/dfbu/"

# --- Step 3: Assemble AppDir ---
echo "[3/6] Assembling AppDir..."
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$APPDIR/usr/share/metainfo"

# Copy frozen application into AppDir
cp -r "$DIST_DIR/dfbu/"* "$APPDIR/usr/bin/"

# Copy desktop integration files
cp "$SCRIPT_DIR/com.l3digital.dfbu.desktop" "$APPDIR/usr/share/applications/"
cp "$SCRIPT_DIR/com.l3digital.dfbu.desktop" "$APPDIR/com.l3digital.dfbu.desktop"
cp "$SCRIPT_DIR/com.l3digital.dfbu.appdata.xml" "$APPDIR/usr/share/metainfo/"

# Copy icons
cp "$PROJECT_ROOT/DFBU/resources/icons/dfbu.svg" "$APPDIR/usr/share/icons/hicolor/scalable/apps/com.l3digital.dfbu.svg"
cp "$PROJECT_ROOT/DFBU/resources/icons/dfbu-256.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/com.l3digital.dfbu.png"

# AppImage requires icon at root of AppDir
cp "$PROJECT_ROOT/DFBU/resources/icons/dfbu-256.png" "$APPDIR/com.l3digital.dfbu.png"

# --- Step 4: Create AppRun script ---
echo "[4/6] Creating AppRun script..."
cat > "$APPDIR/AppRun" << 'APPRUN_EOF'
#!/usr/bin/env bash
# AppRun - Entry point for DFBU AppImage
SELF_DIR="$(dirname "$(readlink -f "$0")")"
exec "$SELF_DIR/usr/bin/dfbu" "$@"
APPRUN_EOF
chmod +x "$APPDIR/AppRun"

# --- Step 5: Download appimagetool if needed ---
echo "[5/6] Checking for appimagetool..."
APPIMAGETOOL="$BUILD_DIR/appimagetool-$ARCH.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "  Downloading appimagetool..."
    wget -q -O "$APPIMAGETOOL" \
        "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-$ARCH.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

# --- Step 6: Build AppImage ---
echo "[6/6] Building AppImage..."
ARCH="$ARCH" "$APPIMAGETOOL" "$APPDIR" "$DIST_DIR/DFBU-$ARCH.AppImage"

echo ""
echo "=== Build Complete ==="
echo "AppImage: $DIST_DIR/DFBU-$ARCH.AppImage"
echo "Size: $(du -h "$DIST_DIR/DFBU-$ARCH.AppImage" | cut -f1)"
echo ""
echo "Test it with:"
echo "  chmod +x $DIST_DIR/DFBU-$ARCH.AppImage"
echo "  $DIST_DIR/DFBU-$ARCH.AppImage"
```

**Step 2: Make the script executable**

```bash
chmod +x packaging/build-appimage.sh
```

**Step 3: Commit**

```bash
git add packaging/build-appimage.sh
git commit -m "feat: add AppImage build script"
```

---

## Task 9: Update .gitignore for Build Artifacts

**Files:**
- Modify: `.gitignore`

**Step 1: Add build artifact patterns**

Append to `.gitignore`:

```gitignore
# PyInstaller
build/
dist/
*.spec.bak

# AppImage build artifacts
*.AppImage
appimagetool-*
```

**Step 2: Verify the patterns don't exclude source files**

```bash
cd /home/chris/projects/dfbu
git status
```

Expected: Only `.gitignore` shows as modified. No packaging/ source files are excluded.

**Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: add build artifact patterns to .gitignore"
```

---

## Task 10: Build and Test the AppImage

This is the integration test — build the full AppImage and verify it works.

**Step 1: Run the build script**

```bash
cd /home/chris/projects/dfbu
./packaging/build-appimage.sh
```

Expected: Script completes all 6 stages. AppImage created at `dist/DFBU-x86_64.AppImage`.

**Step 2: Test the AppImage launches**

```bash
chmod +x dist/DFBU-x86_64.AppImage
./dist/DFBU-x86_64.AppImage
```

Expected: Application window appears with all UI elements loading correctly.

**Step 3: Verify data files are accessible**

In the running app:
- Confirm the dotfile library loads (settings tab should show options)
- Confirm the main window UI renders (loaded from .ui file)
- Try adding a test dotfile entry to verify YAML config works

**Step 4: Test on a clean path (simulate portable execution)**

```bash
# Copy AppImage to /tmp and run from there to verify portability
cp dist/DFBU-x86_64.AppImage /tmp/
cd /tmp
./DFBU-x86_64.AppImage
```

Expected: App launches from /tmp with no dependency issues.

**Step 5: Check AppImage size**

```bash
du -h dist/DFBU-x86_64.AppImage
```

Expected: Somewhere between 80-200MB (PySide6 is large). If over 200MB, consider excluding more PySide6 modules in the spec file.

---

## Task 11: Document the Build Process

**Files:**
- Create: `packaging/README.md`

**Step 1: Create packaging documentation**

Create `packaging/README.md`:

```markdown
# DFBU Packaging

## AppImage

### Prerequisites

- Python 3.14+ with uv package manager
- Project dependencies installed: `uv sync --group dev`
- `wget` (for downloading appimagetool on first build)

### Building

```bash
./packaging/build-appimage.sh
```

Output: `dist/DFBU-x86_64.AppImage`

### Running

```bash
chmod +x dist/DFBU-x86_64.AppImage
./dist/DFBU-x86_64.AppImage
```

### File Structure

```
packaging/
├── README.md                          # This file
├── build-appimage.sh                  # Build automation script
├── dfbu.spec                          # PyInstaller configuration
├── com.l3digital.dfbu.desktop         # FreeDesktop desktop entry
└── com.l3digital.dfbu.appdata.xml     # AppStream metadata
```

### Troubleshooting

**AppImage won't launch:**
- Ensure FUSE is installed: `sudo apt install fuse libfuse2`
- Try extracting: `./DFBU-x86_64.AppImage --appimage-extract` then run `squashfs-root/AppRun`

**Missing Qt platform plugin:**
- The PyInstaller spec includes PySide6 platform plugins automatically
- If issues persist, set: `QT_DEBUG_PLUGINS=1 ./DFBU-x86_64.AppImage`

**UI files not loading:**
- Verify the spec file `datas` list includes all .ui files from `DFBU/gui/designer/`
- Check paths with: `./DFBU-x86_64.AppImage --appimage-extract && find squashfs-root -name "*.ui"`
```

**Step 2: Commit**

```bash
git add packaging/README.md
git commit -m "docs: add packaging build documentation"
```

---

## Summary of All Files Created/Modified

| Action | File | Purpose |
|--------|------|---------|
| Modify | `pyproject.toml` | Version fix, entry points, classifiers, build backend |
| Rename | `DFBU/dfbu-gui.py` → `DFBU/dfbu_gui.py` | Module import compatibility |
| Create | `DFBU/__main__.py` | `python -m DFBU` support |
| Create | `DFBU/resources/icons/dfbu.svg` | Scalable application icon |
| Create | `DFBU/resources/icons/dfbu-256.png` | Rendered icon for AppImage |
| Create | `packaging/com.l3digital.dfbu.desktop` | Desktop menu integration |
| Create | `packaging/com.l3digital.dfbu.appdata.xml` | AppStream/AppImageHub metadata |
| Create | `packaging/dfbu.spec` | PyInstaller build configuration |
| Create | `packaging/build-appimage.sh` | Full build automation script |
| Modify | `.gitignore` | Exclude build artifacts |
| Create | `packaging/README.md` | Build documentation |
| Modify | `CLAUDE.md` | Update file references |

## Dependencies Added

| Package | Group | Purpose |
|---------|-------|---------|
| `pyinstaller` | dev | Freeze Python app into standalone executable |
| `hatchling` | build-system | PEP 517 build backend |
